"""Analyze the sealed Qwen projector-tomography Boolean cubes."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rsi_topology.godel_capture import canonical_json_bytes, sha256_file
from rsi_topology.projector_tomography import (
    design_matrix,
    exact_boolean_coefficients,
    interaction_order_energy,
    relative_sse_reduction,
)


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _records(result_dir: Path) -> list[dict]:
    rows = []
    for path in sorted((result_dir / "work_units").glob("*.json")):
        rows.extend(_load(path)["records"])
    return rows


def _cross_validated(rows: list[dict], arm: str) -> tuple[list[dict], float]:
    arm_rows = [row for row in rows if row["arm"] == arm]
    prompts: dict[str, list[dict]] = defaultdict(list)
    for row in arm_rows:
        prompts[row["prompt_id"]].append(row)
    groups = sorted({items[0]["subcondition_id"] for items in prompts.values()})
    fold_results = []
    total_y, total_low, total_high = [], [], []
    for heldout in groups:
        train_x, train_y, test_x, test_y = [], [], [], []
        for items in prompts.values():
            ordered = sorted(items, key=lambda item: item["mask"])
            baseline = ordered[0]["mean_log_probability"]
            target_x = train_x if ordered[0]["subcondition_id"] != heldout else test_x
            target_y = train_y if ordered[0]["subcondition_id"] != heldout else test_y
            for item in ordered[1:]:
                target_x.append(item["bits"])
                target_y.append(item["mean_log_probability"] - baseline)
        train_x, train_y = np.asarray(train_x), np.asarray(train_y)
        test_x, test_y = np.asarray(test_x), np.asarray(test_y)
        x1_train, x2_train = design_matrix(train_x, 1), design_matrix(train_x, 2)
        beta1 = np.linalg.lstsq(x1_train, train_y, rcond=None)[0]
        beta2 = np.linalg.lstsq(x2_train, train_y, rcond=None)[0]
        pred1 = design_matrix(test_x, 1) @ beta1
        pred2 = design_matrix(test_x, 2) @ beta2
        sse1 = float(np.sum((test_y - pred1) ** 2))
        sse2 = float(np.sum((test_y - pred2) ** 2))
        fold_results.append({"subcondition_id": heldout, "sse_degree1": sse1, "sse_degree2": sse2, "row_count": len(test_y)})
        total_y.extend(test_y)
        total_low.extend(pred1)
        total_high.extend(pred2)
    return fold_results, relative_sse_reduction(np.asarray(total_y), np.asarray(total_low), np.asarray(total_high))


def _bootstrap_fold_reduction(folds: list[dict], *, seed: int, replicates: int) -> list[float]:
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(replicates):
        sampled = rng.integers(0, len(folds), size=len(folds))
        low = sum(folds[i]["sse_degree1"] for i in sampled)
        high = sum(folds[i]["sse_degree2"] for i in sampled)
        values.append(0.0 if low <= 1e-18 else (low - high) / low)
    return values


def analyze(protocol_path: Path, registration_path: Path, result_dir: Path, output: Path) -> dict:
    protocol, registration = _load(protocol_path), _load(registration_path)
    if sha256_file(protocol_path) != registration["protocol"]["sha256"]:
        raise ValueError("protocol hash mismatch")
    summary = _load(result_dir / "summary.json")
    if summary["status"] != "completed" or summary["work_units_completed"] != 32:
        raise ValueError("model run is incomplete")
    rows = _records(result_dir)
    if len(rows) != registration["prompt_count"] * 32:
        raise ValueError("incomplete cube records")
    by_arm_prompt: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        by_arm_prompt[(row["arm"], row["prompt_id"])].append(row)
    prompt_spectra, interaction_fraction = [], {"selected": {}, "matched_random": {}}
    for (arm, prompt_id), items in sorted(by_arm_prompt.items()):
        ordered = sorted(items, key=lambda item: item["mask"])
        bits = np.asarray([item["bits"] for item in ordered])
        outcomes = np.asarray([item["mean_log_probability"] for item in ordered])
        coeff = exact_boolean_coefficients(bits, outcomes)
        energy = interaction_order_energy(coeff)
        total = sum(energy.values())
        fraction = 0.0 if total <= 1e-24 else sum(value for order, value in energy.items() if order >= 2) / total
        interaction_fraction[arm][prompt_id] = fraction
        prompt_spectra.append({"arm": arm, "prompt_id": prompt_id, "subcondition_id": ordered[0]["subcondition_id"], "order_energy": {str(k): v for k, v in energy.items()}, "interaction_fraction_degree_ge_2": fraction})

    analysis = protocol["analysis"]
    folds_selected, point_selected = _cross_validated(rows, "selected")
    folds_random, point_random = _cross_validated(rows, "matched_random")
    bootstrap_selected = _bootstrap_fold_reduction(folds_selected, seed=int(analysis["bootstrap_seed"]), replicates=int(analysis["bootstrap_replicates"]))
    selected_ci = np.quantile(bootstrap_selected, [0.025, 0.975]).tolist()

    prompt_metadata = {row["prompt_id"]: row for row in _load(Path(registration["sealed_evaluation_prompts"]["path"]))["rows"]}
    groups = sorted({row["subcondition_id"] for row in prompt_metadata.values()})
    group_differences = []
    for group in groups:
        ids = [pid for pid, row in prompt_metadata.items() if row["subcondition_id"] == group]
        group_differences.append(float(np.mean([interaction_fraction["selected"][pid] - interaction_fraction["matched_random"][pid] for pid in ids])))
    rng = np.random.default_rng(int(analysis["bootstrap_seed"]) + 1)
    difference_bootstrap = [float(np.mean(np.asarray(group_differences)[rng.integers(0, len(groups), len(groups))])) for _ in range(int(analysis["bootstrap_replicates"]))]
    interaction_difference = float(np.mean(group_differences))
    interaction_difference_ci = np.quantile(difference_bootstrap, [0.025, 0.975]).tolist()

    baseline = {(row["prompt_id"]): row["mean_log_probability"] for row in rows if row["arm"] == "selected" and row["mask"] == 0}
    replay = {row["prompt_id"]: row["mean_log_probability"] for row in _load(result_dir / "baseline_replay.json")["records"]}
    replay_error = max(abs(baseline[key] - replay[key]) for key in baseline)
    full_deltas = [abs(row["mean_log_probability"] - baseline[row["prompt_id"]]) for row in rows if row["arm"] == "selected" and row["mask"] == 15]
    liveness = float(np.median(full_deltas))
    gates_spec = analysis["gates"]
    gates = {
        "N0_baseline_replay": {"passed": replay_error <= gates_spec["N0_baseline_replay_max_abs_logprob_error"], "value": replay_error},
        "L0_intervention_liveness": {"passed": liveness >= gates_spec["L0_selected_full_subset_median_abs_delta_min"], "value": liveness},
        "I1_stable_degree2_increment": {"passed": point_selected >= gates_spec["I1_degree2_relative_sse_reduction_point_min"] and selected_ci[0] > gates_spec["I1_degree2_relative_sse_reduction_lower95_min"], "value": point_selected, "ci95": selected_ci},
        "S0_selected_specificity": {"passed": interaction_difference_ci[0] > gates_spec["S0_selected_minus_random_interaction_fraction_lower95_min"], "value": interaction_difference, "ci95": interaction_difference_ci},
    }
    if not gates["N0_baseline_replay"]["passed"]:
        verdict = "invalid_numerical_replay"
    elif not gates["L0_intervention_liveness"]["passed"]:
        verdict = "instrument_not_live"
    elif gates["I1_stable_degree2_increment"]["passed"] and gates["S0_selected_specificity"]["passed"]:
        verdict = "selected_projector_interactions_established"
    elif gates["I1_stable_degree2_increment"]["passed"]:
        verdict = "nonadditivity_established_specificity_not_established"
    else:
        verdict = "stable_nonadditivity_not_established"
    result = {
        "schema_version": "qwen08_projector_tomography_analysis_v0_1",
        "verdict": verdict,
        "claim_boundary": protocol["claim_boundary"],
        "protocol_sha256": sha256_file(protocol_path),
        "registration_sha256": sha256_file(registration_path),
        "run_summary_sha256": sha256_file(result_dir / "summary.json"),
        "record_count": len(rows),
        "prompt_count": registration["prompt_count"],
        "gates": gates,
        "selected_degree2_relative_sse_reduction": point_selected,
        "matched_random_degree2_relative_sse_reduction": point_random,
        "selected_minus_random_interaction_fraction": interaction_difference,
        "folds": {"selected": folds_selected, "matched_random": folds_random},
        "prompt_spectra": prompt_spectra,
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "analysis_result.json").write_bytes(canonical_json_bytes(result))
    report = f"""# Qwen-0.8B projector interaction tomography\n\n**Verdict:** `{verdict}`\n\nThe intervention was numerically live with a median absolute four-projector effect of {liveness:.6g} mean log-probability units. Adding stable pairwise terms changed held-out prediction SSE by {point_selected:.3%} for the selected projectors (cluster bootstrap 95% interval [{selected_ci[0]:.3%}, {selected_ci[1]:.3%}]) and {point_random:.3%} for matched-random projectors. The selected-minus-random interaction-fraction difference was {interaction_difference:.6g} (95% interval [{interaction_difference_ci[0]:.6g}, {interaction_difference_ci[1]:.6g}]).\n\n## Gate record\n\n```json\n{json.dumps(gates, indent=2, sort_keys=True)}\n```\n\n## Claim boundary\n\n{protocol['claim_boundary']}\n"""
    (output / "REPORT.md").write_text(report, encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=ROOT / "protocols" / "qwen08_projector_tomography_v0_1.json")
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.protocol.resolve(), args.registration.resolve(), args.result_dir.resolve(), args.output_dir.resolve())
    print(json.dumps({"verdict": result["verdict"], "gates": result["gates"]}, indent=2))


if __name__ == "__main__":
    main()
