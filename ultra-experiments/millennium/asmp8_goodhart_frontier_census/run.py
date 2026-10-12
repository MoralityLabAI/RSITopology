"""Registered finite Goodhart-frontier census for ASMP-8."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import platform
import subprocess
import time
import tracemalloc
from io import StringIO
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
SEALED_NAMES = (
    "protocol_v0_1.json",
    "run.py",
    "verify_result.py",
    "test_goodhart_frontier.py",
    "README.md",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to overwrite non-identical artifact: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def git(*args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True, capture_output=True, text=text
    )


def bind_committed_inputs(paths: Sequence[Path]) -> dict[str, Any]:
    commit = git("rev-parse", "HEAD").stdout.strip()
    tracked_diff = git("diff", "--binary", "HEAD", "--", text=False).stdout
    if tracked_diff:
        raise ValueError("tracked diff is nonempty at registered run start")
    bindings: dict[str, Any] = {}
    for path in paths:
        relative = path.resolve().relative_to(REPO_ROOT).as_posix()
        if git("status", "--porcelain", "--", relative).stdout.strip():
            raise ValueError(f"sealed input is dirty or untracked: {relative}")
        committed = git("show", f"HEAD:{relative}", text=False).stdout
        working = path.read_bytes()
        if committed != working:
            raise ValueError(f"sealed input differs from HEAD: {relative}")
        bindings[relative] = {
            "sha256": hashlib.sha256(working).hexdigest(),
            "git_blob": git("rev-parse", f"HEAD:{relative}").stdout.strip(),
        }
    return {
        "commit": commit,
        "tracked_diff_sha256": hashlib.sha256(tracked_diff).hexdigest(),
        "sealed_inputs": bindings,
    }


def normalize_centered(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    centered = values - float(np.dot(weights, values))
    rms = math.sqrt(float(np.dot(weights, centered * centered)))
    if rms == 0:
        raise ValueError("cannot normalize a constant vector")
    return centered / rms


def kl_divergence(policy: np.ndarray, reference: np.ndarray) -> float:
    positive = policy > 0
    return float(np.sum(policy[positive] * np.log(policy[positive] / reference[positive])))


def bisection_for_kl(
    make_policy,
    target: float,
    reference: np.ndarray,
    *,
    lower: float,
    upper: float,
    iterations: int = 100,
) -> np.ndarray:
    if target == 0:
        return reference.copy()
    while kl_divergence(make_policy(upper), reference) < target:
        upper *= 2.0
        if upper > 1e9:
            raise RuntimeError("failed to bracket KL target")
    for _ in range(iterations):
        middle = (lower + upper) / 2.0
        if kl_divergence(make_policy(middle), reference) < target:
            lower = middle
        else:
            upper = middle
    return make_policy((lower + upper) / 2.0)


def gibbs_policy(proxy: np.ndarray, reference: np.ndarray, target_kl: float) -> np.ndarray:
    def make(beta: float) -> np.ndarray:
        logits = beta * proxy
        logits -= float(np.max(logits))
        weights = reference * np.exp(logits)
        return weights / float(np.sum(weights))

    return bisection_for_kl(make, target_kl, reference, lower=0.0, upper=1.0)


def spike_policy(proxy: np.ndarray, reference: np.ndarray, target_kl: float) -> np.ndarray:
    top = int(np.argmax(proxy))

    def make(alpha: float) -> np.ndarray:
        policy = (1.0 - alpha) * reference.copy()
        policy[top] += alpha
        return policy

    return bisection_for_kl(make, target_kl, reference, lower=0.0, upper=1.0 - 1e-14)


def best_of_n_policy(proxy: np.ndarray, n_draws: int) -> np.ndarray:
    """Distribution of the largest-proxy item among iid uniform draws."""
    order = np.argsort(proxy)
    count = len(proxy)
    policy = np.zeros(count, dtype=float)
    for rank, index in enumerate(order, start=1):
        policy[index] = (rank / count) ** n_draws - ((rank - 1) / count) ** n_draws
    return policy


def enumerate_true_rewards(protocol: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    config = protocol["finite_census"]
    levels = tuple(float(value) for value in config["true_reward_alphabet"])
    count = int(config["outcome_count"])
    reference = np.full(count, 1.0 / count)
    raw_rows = []
    normalized_rows = []
    for values in itertools.product(levels, repeat=count):
        row = np.asarray(values, dtype=float)
        if np.all(row == row[0]):
            continue
        raw_rows.append(row)
        normalized_rows.append(normalize_centered(row, reference))
    return np.asarray(raw_rows, dtype=float), np.asarray(normalized_rows, dtype=float)


def classify_curve(curve: np.ndarray, protocol: dict[str, Any]) -> str:
    settings = protocol["phase_labels"]
    tolerance = float(settings["positive_tolerance"])
    peak_minimum = float(settings["interior_peak_minimum"])
    drop = float(settings["peak_to_final_drop"])
    negative_final = float(settings["negative_final_threshold"])
    peak_index = int(np.argmax(curve))
    if 0 < peak_index < len(curve) - 1 and curve[peak_index] >= peak_minimum and curve[peak_index] - curve[-1] >= drop:
        return "peak_then_degrade"
    if float(np.min(curve)) >= -tolerance:
        return "nonnegative"
    if float(curve[-1]) <= negative_final:
        return "negative_tail"
    return "mixed"


def supnorm_positive_control(protocol: dict[str, Any]) -> dict[str, Any]:
    config = protocol["controls"]
    epsilon = float(config["supnorm_epsilon"])
    levels = tuple(float(value) for value in config["supnorm_true_alphabet"])
    count = int(config["supnorm_outcome_count"])
    maximum_regret = -math.inf
    cases = 0
    witness: dict[str, Any] | None = None
    for true_values in itertools.product(levels, repeat=count):
        true_reward = np.asarray(true_values, dtype=float)
        for signs in itertools.product((-1.0, 1.0), repeat=count):
            proxy = true_reward + epsilon * np.asarray(signs)
            chosen = int(np.argmax(proxy))
            regret = float(np.max(true_reward) - true_reward[chosen])
            cases += 1
            if regret > maximum_regret:
                maximum_regret = regret
                witness = {
                    "true_reward": true_reward.tolist(),
                    "proxy": proxy.tolist(),
                    "chosen_index": chosen,
                    "regret": regret,
                }
    bound = 2.0 * epsilon
    return {
        "cases": cases,
        "epsilon": epsilon,
        "maximum_regret": maximum_regret,
        "bound": bound,
        "margin": bound - maximum_regret,
        "witness": witness,
        "pass": maximum_regret <= bound + 1e-12,
    }


def rare_l2_negative_control(protocol: dict[str, Any]) -> dict[str, Any]:
    rare_probability = float(protocol["controls"]["rare_state_probability"])
    reference = np.asarray([1.0 - rare_probability, rare_probability])
    true_reward = np.asarray([0.0, -1.0])
    proxy = np.asarray([0.0, 1.0])
    error = proxy - true_reward
    l2_error = math.sqrt(float(np.dot(reference, error * error)))
    chosen = int(np.argmax(proxy))
    regret = float(np.max(true_reward) - true_reward[chosen])
    return {
        "reference": reference.tolist(),
        "true_reward": true_reward.tolist(),
        "proxy": proxy.tolist(),
        "reference_l2_error": l2_error,
        "optimized_true_regret": regret,
        "pass": l2_error <= float(protocol["controls"]["rare_l2_ceiling"])
        and regret >= float(protocol["controls"]["rare_regret_floor"]),
    }


def alignment_bins(
    alignments: np.ndarray,
    phases: dict[str, list[str]],
    protocol: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    width = float(protocol["alignment"]["bin_width"])
    minimum = int(protocol["alignment"]["minimum_vectors_for_diversity_gate"])
    indices = np.floor((alignments + 1.0 + 1e-12) / width).astype(int)
    records: list[dict[str, Any]] = []
    witnesses = []
    for optimizer, labels in phases.items():
        label_array = np.asarray(labels, dtype=object)
        for index in sorted(set(indices.tolist())):
            mask = indices == index
            if int(np.sum(mask)) == 0:
                continue
            unique, counts = np.unique(label_array[mask], return_counts=True)
            record = {
                "optimizer": optimizer,
                "bin_lower": -1.0 + width * index,
                "bin_upper": -1.0 + width * (index + 1),
                "count": int(np.sum(mask)),
                "phase_counts": {str(label): int(count) for label, count in zip(unique, counts)},
            }
            records.append(record)
            if record["count"] >= minimum and len(record["phase_counts"]) > 1:
                witnesses.append(record)
    return {
        "pass": bool(witnesses),
        "witness": witnesses[0] if witnesses else None,
        "qualifying_bin_count": len(witnesses),
    }, records


def csv_bytes(records: Iterable[dict[str, Any]], fieldnames: Sequence[str]) -> bytes:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for record in records:
        writer.writerow(record)
    return buffer.getvalue().encode("utf-8")


def analyze(protocol: dict[str, Any]) -> dict[str, Any]:
    raw_rewards, rewards = enumerate_true_rewards(protocol)
    count = int(protocol["finite_census"]["outcome_count"])
    reference = np.full(count, 1.0 / count)
    proxy = normalize_centered(
        np.asarray(protocol["finite_census"]["proxy_rank_values"], dtype=float), reference
    )
    fractions = np.asarray(protocol["pressure"]["fractions_of_log_outcome_count"], dtype=float)
    targets = fractions * math.log(count)
    policies: dict[str, list[np.ndarray]] = {"gibbs": [], "top_spike_mixture": []}
    calibration = []
    for target in targets:
        for name, builder in (("gibbs", gibbs_policy), ("top_spike_mixture", spike_policy)):
            policy = builder(proxy, reference, float(target))
            policies[name].append(policy)
            realized = kl_divergence(policy, reference)
            calibration.append(
                {
                    "optimizer": name,
                    "target_kl": float(target),
                    "realized_kl": realized,
                    "absolute_error": abs(realized - float(target)),
                    "sum_error": abs(float(np.sum(policy)) - 1.0),
                    "minimum_probability": float(np.min(policy)),
                    "finite": bool(np.all(np.isfinite(policy))),
                }
            )

    gains: dict[str, np.ndarray] = {}
    phases: dict[str, list[str]] = {}
    for name, path in policies.items():
        path_matrix = np.asarray(path)
        path_gains = rewards @ (path_matrix - reference).T
        gains[name] = path_gains
        phases[name] = [classify_curve(row, protocol) for row in path_gains]

    alignments = rewards @ (reference * proxy)
    sign_floor = 0.05
    difference_floor = 0.20
    sign_witnesses = []
    for pressure_index, target in enumerate(targets):
        gibbs_gain = gains["gibbs"][:, pressure_index]
        spike_gain = gains["top_spike_mixture"][:, pressure_index]
        opposite = ((gibbs_gain > sign_floor) & (spike_gain < -sign_floor)) | (
            (spike_gain > sign_floor) & (gibbs_gain < -sign_floor)
        )
        different = np.abs(gibbs_gain - spike_gain) >= difference_floor
        for row_index in np.where(opposite & different)[0]:
            sign_witnesses.append(
                {
                    "row_index": int(row_index),
                    "raw_true_reward": raw_rewards[row_index].tolist(),
                    "normalized_true_reward": rewards[row_index].tolist(),
                    "alignment_cosine": float(alignments[row_index]),
                    "pressure_fraction_log_n": float(fractions[pressure_index]),
                    "target_kl_nats": float(target),
                    "gibbs_gain": float(gibbs_gain[row_index]),
                    "top_spike_gain": float(spike_gain[row_index]),
                    "gain_difference": float(abs(gibbs_gain[row_index] - spike_gain[row_index])),
                }
            )
    sign_witnesses.sort(key=lambda item: item["gain_difference"], reverse=True)

    alignment_gate, alignment_records = alignment_bins(alignments, phases, protocol)
    phase_records = []
    for optimizer, labels in phases.items():
        unique, counts_by_phase = np.unique(np.asarray(labels, dtype=object), return_counts=True)
        for label, phase_count in zip(unique, counts_by_phase):
            phase_records.append(
                {"optimizer": optimizer, "phase": str(label), "count": int(phase_count)}
            )

    best_of_n = []
    for n_draws in protocol["optimizer_paths"]["best_of_n_descriptive"]:
        policy = best_of_n_policy(proxy, int(n_draws))
        best_of_n.append(
            {
                "n_draws": int(n_draws),
                "kl_nats": kl_divergence(policy, reference),
                "policy": policy.tolist(),
            }
        )

    supnorm = supnorm_positive_control(protocol)
    rare = rare_l2_negative_control(protocol)
    tolerance = float(protocol["pressure"]["match_tolerance"])
    g1 = all(
        row["finite"]
        and row["minimum_probability"] >= 0.0
        and row["absolute_error"] <= tolerance
        and row["sum_error"] <= 1e-12
        for row in calibration
    )
    expected_count = len(protocol["finite_census"]["true_reward_alphabet"]) ** count - len(
        protocol["finite_census"]["true_reward_alphabet"]
    )
    gates = {
        "G1_numerical_calibration": {"pass": g1, "maximum_kl_error": max(row["absolute_error"] for row in calibration)},
        "G2_supnorm_positive_control": {"pass": bool(supnorm["pass"]), "maximum_regret": supnorm["maximum_regret"], "bound": supnorm["bound"]},
        "G3_reference_l2_negative_control": {"pass": bool(rare["pass"]), "reference_l2_error": rare["reference_l2_error"], "optimized_true_regret": rare["optimized_true_regret"]},
        "G4_optimizer_independence_falsification": {"pass": bool(sign_witnesses), "witness_count": len(sign_witnesses), "strongest_witness": sign_witnesses[0] if sign_witnesses else None},
        "G5_alignment_descriptor_stress": alignment_gate,
        "G6_complete_census": {"pass": len(rewards) == expected_count, "observed": len(rewards), "expected": expected_count, "pressure_cells_per_optimizer": len(targets)},
    }
    invalid = not all(gates[name]["pass"] for name in (
        "G1_numerical_calibration",
        "G2_supnorm_positive_control",
        "G3_reference_l2_negative_control",
        "G6_complete_census",
    ))
    if invalid:
        verdict = "invalid"
    elif gates["G4_optimizer_independence_falsification"]["pass"]:
        verdict = "scalar_kl_pressure_rejected_on_registered_class"
    else:
        verdict = "scalar_kl_pressure_not_rejected_on_registered_class"
    return {
        "verdict": verdict,
        "gates": gates,
        "census": {
            "reward_vector_count": len(rewards),
            "outcome_count": count,
            "pressure_targets_nats": targets.tolist(),
            "calibration": calibration,
            "phase_counts": phase_records,
            "alignment_bin_records": alignment_records,
            "optimizer_sign_disagreement_count": len(sign_witnesses),
        },
        "controls": {"supnorm": supnorm, "rare_reference_l2": rare},
        "descriptive": {"best_of_n": best_of_n},
        "witnesses": sign_witnesses[:25],
        "claim_boundary": protocol["claim_boundary"],
        "tables": {"phase_counts": phase_records, "alignment_bins": alignment_records},
    }


def render_report(result: dict[str, Any], protocol: dict[str, Any]) -> str:
    gates = result["gates"]
    witness = gates["G4_optimizer_independence_falsification"]["strongest_witness"]
    lines = [
        "# ASMP-8 finite Goodhart-frontier census — Result",
        "",
        f"**Verdict:** `{result['verdict']}`",
        "",
        "This is an exhaustive result for the registered six-outcome labelled reward class and two",
        "optimizer paths. It is not a universal Goodhart theorem.",
        "",
        "## Gates",
        "",
    ]
    for name, record in gates.items():
        lines.append(f"- **{name}:** {'PASS' if record['pass'] else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Primary estimand",
            "",
            f"The exhaustive census contained {result['census']['reward_vector_count']:,} normalized labelled true-reward vectors.",
            f"It found {result['census']['optimizer_sign_disagreement_count']:,} matched-KL cells with registered sign disagreement.",
        ]
    )
    if witness:
        lines.extend(
            [
                "",
                "The strongest witness used the same proxy, reference policy, and KL pressure for both optimizers:",
                "",
                f"- KL pressure: {witness['target_kl_nats']:.9f} nats",
                f"- Gibbs true-reward gain: {witness['gibbs_gain']:.9f}",
                f"- top-spike true-reward gain: {witness['top_spike_gain']:.9f}",
                f"- absolute difference: {witness['gain_difference']:.9f}",
                f"- raw true-reward vector: `{witness['raw_true_reward']}`",
            ]
        )
    supnorm = result["controls"]["supnorm"]
    rare = result["controls"]["rare_reference_l2"]
    lines.extend(
        [
            "",
            "## Controls",
            "",
            f"The pointwise-error census attained maximum regret {supnorm['maximum_regret']:.6f} against the registered 2ε bound {supnorm['bound']:.6f}.",
            f"The rare-state control had reference L2 error {rare['reference_l2_error']:.9f} while optimized true regret was {rare['optimized_true_regret']:.6f}.",
            "",
            "## Interpretation",
            "",
            "A scalar KL distance from the reference policy is not, by itself, an optimizer-independent state variable for true-reward change on this class. It remains a useful coordinate when paired with the reachable-set or optimizer-path geometry. Uniform pointwise proxy error supplies a positive bound; average reference-distribution error does not.",
            "",
            "## Prohibited extrapolations",
            "",
        ]
    )
    lines.extend(f"- {claim}" for claim in protocol["claim_boundary"]["not_claimed"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=HERE / "protocol_v0_1.json")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    output_dir = args.output_dir.resolve()

    tracemalloc.start()
    start = time.perf_counter()
    binding = bind_committed_inputs([HERE / name for name in SEALED_NAMES])
    result = analyze(protocol)
    elapsed = time.perf_counter() - start
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    result["gates"] = {"G0_registration_binding": {"pass": True, **binding}, **result["gates"]}
    result["resources"] = {
        "wall_seconds": elapsed,
        "python_peak_bytes": peak_bytes,
        "wall_ceiling": protocol["resource_ceiling"]["wall_seconds"],
        "memory_ceiling": protocol["resource_ceiling"]["python_peak_bytes"],
    }
    if elapsed > float(protocol["resource_ceiling"]["wall_seconds"]) or peak_bytes > int(protocol["resource_ceiling"]["python_peak_bytes"]):
        result["verdict"] = "invalid_resource_cap"

    result_path = output_dir / "result_v0_1.json"
    phase_path = output_dir / "phase_counts_v0_1.csv"
    bins_path = output_dir / "alignment_bins_v0_1.csv"
    witnesses_path = output_dir / "witnesses_v0_1.json"
    report_path = output_dir / "RESULT_v0_1.md"
    write_once(result_path, canonical_json(result).encode("utf-8"))
    write_once(
        phase_path,
        csv_bytes(result["tables"]["phase_counts"], ("optimizer", "phase", "count")),
    )
    alignment_rows = []
    for row in result["tables"]["alignment_bins"]:
        alignment_rows.append({**row, "phase_counts": json.dumps(row["phase_counts"], sort_keys=True)})
    write_once(
        bins_path,
        csv_bytes(alignment_rows, ("optimizer", "bin_lower", "bin_upper", "count", "phase_counts")),
    )
    write_once(witnesses_path, canonical_json(result["witnesses"]).encode("utf-8"))
    write_once(report_path, render_report(result, protocol).encode("utf-8"))
    receipt = {
        "schema_version": "asmp8_goodhart_frontier_census_receipt_v0_1",
        "protocol_id": protocol["protocol_id"],
        "verdict": result["verdict"],
        "binding": binding,
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform()},
        "resources": result["resources"],
        "outputs": {
            path.name: {"sha256": sha256_file(path), "bytes": path.stat().st_size}
            for path in (result_path, phase_path, bins_path, witnesses_path, report_path)
        },
    }
    write_once(output_dir / "receipt_v0_1.json", canonical_json(receipt).encode("utf-8"))
    print(canonical_json({"verdict": result["verdict"], "gates": result["gates"], "resources": result["resources"]}))
    return 0 if not result["verdict"].startswith("invalid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
