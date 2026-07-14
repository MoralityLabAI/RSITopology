"""Run the frozen gauge-invariant Qwen soft-atlas measurement gate."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.recursive_gate import (
    PromptFamilySufficiency,
    effective_dimension,
    evaluate_prompt_family_sufficiency,
    fixed_sequence,
    measurement_edges,
    measurement_noise_scale,
    prompt_cluster_simultaneous_band,
    psd_square_root,
    quadrant_cells,
    regularization_grid,
    resolve_gate_record,
    response_gram,
    soft_profile,
    structured_soft_null,
)


SIGNATURE_RE = re.compile(r"signature__m(\d+)__p(\d+)__r(\d+)__t(\d+)")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_json_bytes(value))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _load_signatures(
    path: Path,
    *,
    modules: list[str],
    prompts: list[str],
    replicas: list[str],
    checkpoints: list[int],
) -> tuple[dict[tuple[str, str, int], np.ndarray], dict[str, Any]]:
    signatures: dict[tuple[int, int, int, int], np.ndarray] = {}
    with np.load(path, allow_pickle=False) as archive:
        manifest = json.loads(archive["manifest_json_utf8"].tobytes().decode("utf-8"))
        for key in archive.files:
            match = SIGNATURE_RE.fullmatch(key)
            if match:
                indices = tuple(map(int, match.groups()))
                signatures[indices] = np.asarray(archive[key], dtype=np.float64)
    expected = {
        (module_index, prompt_index, replica_index, checkpoint)
        for module_index in range(len(modules))
        for prompt_index in range(len(prompts))
        for replica_index in range(len(replicas))
        for checkpoint in checkpoints
    }
    if set(signatures) != expected:
        missing = sorted(expected - set(signatures))[:5]
        extra = sorted(set(signatures) - expected)[:5]
        raise ValueError(f"signature universe mismatch; missing={missing}, extra={extra}")
    grams: dict[tuple[str, str, int], np.ndarray] = {}
    for prompt_index, prompt in enumerate(prompts):
        for replica_index, replica in enumerate(replicas):
            for checkpoint in checkpoints:
                matrices = [
                    signatures[(module_index, prompt_index, replica_index, checkpoint)]
                    for module_index in range(len(modules))
                ]
                grams[(prompt, replica, checkpoint)] = response_gram(matrices)
    return grams, manifest


def _gate_decision(
    *,
    dimension_range: float,
    common_intersection_margin: float,
    null_advantage: float,
    minimum_informative_fraction: float,
    minimum_median_anisotropy: float,
    margins: dict[str, float],
) -> str:
    pass_conditions = [
        dimension_range < margins["maximum_effective_dimension_range"],
        common_intersection_margin > 0.0,
        null_advantage > margins["minimum_soft_similarity_advantage_over_null"],
        minimum_informative_fraction > margins["minimum_informative_fraction"],
        minimum_median_anisotropy > margins["minimum_spectral_anisotropy"],
    ]
    if all(pass_conditions):
        return "pass"
    fail_conditions = [
        dimension_range > margins["maximum_effective_dimension_range"],
        common_intersection_margin < 0.0,
        null_advantage < 0.0,
        minimum_informative_fraction < margins["minimum_informative_fraction"],
        minimum_median_anisotropy < margins["minimum_spectral_anisotropy"],
    ]
    return "fail" if any(fail_conditions) else "inconclusive"


def _report(result: dict[str, Any]) -> str:
    measurement = result["measurement_component"]
    prompt = result["prompt_component"]
    lines = [
        "# Qwen soft-atlas measurement gate v1",
        "",
        "## Result",
        "",
        f"Measurement component: **{measurement['gate_record']['gate_decision']}**.",
        f"Prompt-scale component: **{prompt['status']}**.",
        f"Overall G1 decision: **{result['overall_G1']['gate_decision']}**.",
        f"Prompt-corpus decision: **{result['prompt_corpus_decision']}**.",
        "",
        "The measurement instrument uses only target-blind Qwen functional signatures. "
        "It works in the shared 12-dimensional probe-response space and does not identify "
        "coordinated weight-space edit coordinates.",
        "",
        "## Frozen measurements",
        "",
        f"- lambda_measurement: `{measurement['lambda_measurement']:.12g}`",
        f"- registered edges: `{measurement['measurement_edge_count']}`",
        f"- effective-dimension range in central window: `{measurement['central']['effective_dimension_range']:.6f}`",
        f"- simultaneous-band common-intersection margin: `{measurement['central']['common_intersection_margin']:.6f}`",
        f"- minimum observed-minus-null similarity margin: `{measurement['central']['minimum_null_advantage']:.6f}`",
        f"- minimum informative fraction: `{measurement['central']['minimum_informative_fraction']:.6f}`",
        f"- minimum median spectral anisotropy: `{measurement['central']['minimum_median_anisotropy']:.6f}`",
        f"- audit-null false-support rate: `{measurement['null']['audit_false_support_rate']:.6f}`",
        "",
        "## Decision interpretation",
        "",
        result["decision_interpretation"],
        "",
        "The prior hard-projector `noise_floor_only` result is unchanged. A measurement "
        "pass would justify building a new prompt-family corpus, not opening recursive "
        "testing. A fail stops that investment under the frozen sequence.",
        "",
        "## Claim boundary",
        "",
        result["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


def run(
    *,
    protocol_path: Path,
    primitives_path: Path,
    summary_path: Path,
    prompt_manifest_path: Path,
    out_dir: Path,
) -> dict[str, Any]:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if protocol.get("status") != "frozen_prereveal_measurement_gate":
        raise ValueError("measurement protocol is not frozen")
    expected_hashes = protocol["source_sha256"]
    actual_hashes = {
        "primitives": sha256_file(primitives_path),
        "summary": sha256_file(summary_path),
        "prompt_manifest": sha256_file(prompt_manifest_path),
    }
    if actual_hashes != expected_hashes:
        raise ValueError("source hashes do not match frozen protocol")
    implementation = {
        "runner": sha256_file(Path(__file__).resolve()),
        "recursive_gate": sha256_file(
            Path(__file__).resolve().parents[1] / "rsi_topology" / "recursive_gate.py"
        ),
    }
    if implementation != protocol["implementation_sha256"]:
        raise ValueError("implementation hashes do not match frozen protocol")
    if out_dir.exists():
        raise FileExistsError(f"refusing to overwrite {out_dir}")
    out_dir.mkdir(parents=True)

    design = protocol["design"]
    modules = list(design["module_paths"])
    prompts = list(design["prompt_groups"])
    replicas = list(design["replicas"])
    checkpoints = [int(value) for value in design["checkpoints"]]
    grams, primitive_manifest = _load_signatures(
        primitives_path,
        modules=modules,
        prompts=prompts,
        replicas=replicas,
        checkpoints=checkpoints,
    )
    if len(grams) != int(protocol["universe"]["required_cells"]):
        raise ValueError("canonical Gram universe is incomplete")
    canonical = {cell: psd_square_root(gram) for cell, gram in grams.items()}
    edges = measurement_edges(prompts, replicas, checkpoints)
    if len(edges) != int(protocol["universe"]["required_measurement_edges"]):
        raise ValueError("measurement edge universe is incomplete")
    lambda_measurement, edge_values = measurement_noise_scale(
        canonical, edges, quantile=float(protocol["noise"]["quantile"])
    )
    exponents = [int(value) for value in protocol["regularization"]["exponents_j"]]
    lambdas = regularization_grid(lambda_measurement, exponents)
    quadrants = quadrant_cells(
        prompt_halves=design["prompt_group_halves"],
        replica_halves=design["replica_halves"],
        checkpoints=checkpoints,
    )
    profile_rows, projectors = soft_profile(grams, lambdas, quadrants)

    null_config = protocol["null"]
    threshold_null = structured_soft_null(
        projectors,
        quadrants,
        draws=int(null_config["draws"]),
        seed=int(null_config["threshold_seed"]),
        block_sizes=tuple(int(value) for value in null_config["block_sizes"]),
    )
    audit_null = structured_soft_null(
        projectors,
        quadrants,
        draws=int(null_config["draws"]),
        seed=int(null_config["audit_seed"]),
        block_sizes=tuple(int(value) for value in null_config["block_sizes"]),
    )
    central_exponents = set(int(value) for value in protocol["regularization"]["central_j"])
    central_indices = [index for index, exponent in enumerate(exponents) if exponent in central_exponents]
    central_lambdas = [float(lambdas[index]) for index in central_indices]
    threshold_matrix = np.column_stack([threshold_null[lam] for lam in central_lambdas])
    audit_matrix = np.column_stack([audit_null[lam] for lam in central_lambdas])
    threshold_max = np.max(threshold_matrix, axis=1)
    audit_max = np.max(audit_matrix, axis=1)
    alpha = float(null_config["familywise_alpha"])
    threshold = float(np.quantile(threshold_max, 1.0 - alpha))
    audit_false_support = float(np.mean(audit_max > threshold))
    tolerance = float(null_config["maximum_audit_false_support_rate"])
    null_valid = bool(audit_false_support <= tolerance)

    dimension_values = {
        float(lam): {
            cell: effective_dimension(projector)
            for cell, projector in projectors[float(lam)].items()
        }
        for lam in lambdas
    }
    bootstrap_config = protocol["bootstrap"]
    band = prompt_cluster_simultaneous_band(
        dimension_values,
        draws=int(bootstrap_config["draws"]),
        seed=int(bootstrap_config["seed"]),
        alpha=float(bootstrap_config["alpha"]),
    )
    central_rows = [profile_rows[index] for index in central_indices]
    central_points = [float(band["point"][index]) for index in central_indices]
    central_lowers = [float(band["simultaneous_lower"][index]) for index in central_indices]
    central_uppers = [float(band["simultaneous_upper"][index]) for index in central_indices]
    dimension_range = float(max(central_points) - min(central_points))
    intersection_margin = float(min(central_uppers) - max(central_lowers))
    null_advantages = [float(row["minimum_soft_similarity"] - threshold) for row in central_rows]
    minimum_null_advantage = float(min(null_advantages))
    minimum_informative_fraction = float(
        min(row["informative_fraction_anisotropy_ge_0_10"] for row in central_rows)
    )
    minimum_median_anisotropy = float(
        min(row["median_spectral_anisotropy"] for row in central_rows)
    )
    margins = {key: float(value) for key, value in protocol["margins"].items()}
    evidential = _gate_decision(
        dimension_range=dimension_range,
        common_intersection_margin=intersection_margin,
        null_advantage=minimum_null_advantage,
        minimum_informative_fraction=minimum_informative_fraction,
        minimum_median_anisotropy=minimum_median_anisotropy,
        margins=margins,
    )
    measurement_record = resolve_gate_record(
        gate_id="G1_measurement_component",
        execution_status="evaluated",
        instrument_status="valid" if null_valid else "invalid_gate_inputs",
        evidential_decision=evidential if null_valid else None,
        stop_reason=None if null_valid else "audit_null_failed_registered_false_support_tolerance",
    )

    family_protocol = json.loads(
        (protocol_path.parent / "proposal_recursive_prompt_families_v1.json").read_text(
            encoding="utf-8"
        )
    )
    if sha256_file(protocol_path.parent / "proposal_recursive_prompt_families_v1.json") != protocol[
        "prompt_family_artifact_sha256"
    ]:
        raise ValueError("prompt-family artifact hash does not match measurement protocol")
    sufficiency_fields = PromptFamilySufficiency.__dataclass_fields__
    criteria = PromptFamilySufficiency(
        **{
            key: int(value)
            for key, value in family_protocol["sufficiency"].items()
            if key in sufficiency_fields
        }
    )
    prompt_sufficiency = evaluate_prompt_family_sufficiency(
        family_protocol["behavior_family_assignments"],
        prompt_universe=prompts,
        independent_replicas_per_prompt={prompt: len(replicas) for prompt in prompts},
        criteria=criteria,
    )
    if measurement_record["instrument_status"] != "valid":
        overall_instrument_status = measurement_record["instrument_status"]
    elif not prompt_sufficiency["available"]:
        overall_instrument_status = "unavailable_insufficient_prompt_families"
    else:
        overall_instrument_status = "valid"
    overall_record = resolve_gate_record(
        gate_id="G1_atlas",
        execution_status="evaluated",
        instrument_status=overall_instrument_status,
        evidential_decision=(
            measurement_record["gate_decision"]
            if overall_instrument_status == "valid"
            else None
        ),
        stop_reason=(
            None
            if overall_instrument_status == "valid"
            else (
                "prompt_scale_unavailable"
                if overall_instrument_status == "unavailable_insufficient_prompt_families"
                else "measurement_component_instrument_invalid"
            )
        ),
    )
    downstream = fixed_sequence(
        [
            {
                "gate_id": "G1_atlas",
                "execution_status": "evaluated",
                "instrument_status": overall_record["instrument_status"],
                "evidential_decision": (
                    overall_record["gate_decision"]
                    if overall_record["gate_decision"] in {"pass", "fail", "inconclusive"}
                    else None
                ),
                "stop_reason": overall_record["stop_reason"],
            },
            {"gate_id": "G2_causal_edit_family", "execution_status": "not_reached"},
            {"gate_id": "G3_recursive_proposal", "execution_status": "not_reached"},
            {"gate_id": "G4_adversarial_order_safety", "execution_status": "not_reached"},
        ]
    )
    measurement_decision = measurement_record["gate_decision"]
    prompt_corpus_decision = {
        "pass": "warranted_next_investment",
        "fail": "do_not_invest_stop_branch",
        "inconclusive": "defer_until_fresh_disjoint_measurement_extension",
        "not_evaluated": "defer_instrument_invalid",
    }[measurement_decision]
    interpretation = {
        "pass": "The soft probe-response atlas clears the frozen measurement-scale criteria. Build and preregister the behavior-family prompt corpus; do not open recursive testing yet.",
        "fail": "The soft probe-response atlas fails at measurement scale. Stop before funding the prompt-corpus branch under this protocol.",
        "inconclusive": "The valid measurement instrument does not clear pass or failure margins. Only a versioned fresh-disjoint-holdout extension may continue it.",
        "not_evaluated": "The measurement instrument is invalid, so the result contains no evidence for or against the atlas hypothesis.",
    }[measurement_decision]

    result = {
        "schema_version": "qwen_soft_atlas_measurement_result_v1",
        "status": "complete",
        "target_blind": True,
        "outcomes_used": False,
        "source_sha256": actual_hashes,
        "implementation_sha256": implementation,
        "protocol_sha256": sha256_file(protocol_path),
        "primitive_protocol_sha256": primitive_manifest.get("protocol_sha256"),
        "measurement_component": {
            "gate_record": measurement_record,
            "lambda_measurement": lambda_measurement,
            "measurement_edge_count": len(edges),
            "central": {
                "j": sorted(central_exponents),
                "lambdas": central_lambdas,
                "effective_dimension_range": dimension_range,
                "common_intersection_margin": intersection_margin,
                "minimum_null_advantage": minimum_null_advantage,
                "minimum_informative_fraction": minimum_informative_fraction,
                "minimum_median_anisotropy": minimum_median_anisotropy,
            },
            "null": {
                "threshold": threshold,
                "audit_false_support_rate": audit_false_support,
                "maximum_audit_false_support_rate": tolerance,
                "valid": null_valid,
            },
            "bootstrap": band,
            "margins": margins,
        },
        "prompt_component": prompt_sufficiency,
        "overall_G1": overall_record,
        "fixed_sequence": downstream,
        "prompt_corpus_decision": prompt_corpus_decision,
        "decision_interpretation": interpretation,
        "prior_result_unchanged": "noise_floor_only",
        "signed_edits_authorized": False,
        "recursive_experiment_authorized": False,
        "claim_boundary": protocol["claim_boundary"],
    }

    profile_output = out_dir / "soft_atlas_profile.csv"
    edge_output = out_dir / "measurement_edges.csv"
    result_output = out_dir / "measurement_gate_result.json"
    prompt_output = out_dir / "prompt_family_sufficiency.json"
    report_output = out_dir / "measurement_gate_report.md"
    write_csv(
        profile_output,
        profile_rows,
        [
            "lambda",
            "minimum_soft_similarity",
            "median_soft_similarity",
            "median_effective_dimension",
            "minimum_effective_dimension",
            "maximum_effective_dimension",
            "median_spectral_anisotropy",
            "informative_fraction_anisotropy_ge_0_10",
        ],
    )
    edge_rows = [
        {
            "edge_index": index,
            "left_prompt": left[0],
            "left_replica": left[1],
            "left_checkpoint": left[2],
            "right_prompt": right[0],
            "right_replica": right[1],
            "right_checkpoint": right[2],
            "lambda_max_squared_difference": edge_values[index],
        }
        for index, (left, right) in enumerate(edges)
    ]
    write_csv(
        edge_output,
        edge_rows,
        [
            "edge_index",
            "left_prompt",
            "left_replica",
            "left_checkpoint",
            "right_prompt",
            "right_replica",
            "right_checkpoint",
            "lambda_max_squared_difference",
        ],
    )
    write_json(result_output, result)
    write_json(prompt_output, prompt_sufficiency)
    report_output.write_text(_report(result), encoding="utf-8")
    output_paths = [result_output, prompt_output, profile_output, edge_output, report_output]
    receipt = {
        "schema_version": "qwen_soft_atlas_measurement_receipt_v1",
        "status": "complete",
        "protocol_sha256": sha256_file(protocol_path),
        "source_sha256": actual_hashes,
        "implementation_sha256": implementation,
        "output_sha256": {path.name: sha256_file(path) for path in output_paths},
    }
    write_json(out_dir / "run_receipt.json", receipt)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--primitives", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--prompt-manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(
        protocol_path=args.protocol.resolve(),
        primitives_path=args.primitives.resolve(),
        summary_path=args.summary.resolve(),
        prompt_manifest_path=args.prompt_manifest.resolve(),
        out_dir=args.out_dir.resolve(),
    )
    print(
        json.dumps(
            {
                "measurement_decision": result["measurement_component"]["gate_record"]["gate_decision"],
                "overall_G1": result["overall_G1"]["gate_decision"],
                "prompt_corpus_decision": result["prompt_corpus_decision"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
