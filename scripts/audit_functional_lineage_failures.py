"""Seal a target-blind failure-localization audit of functional-lineage v2.

This script consumes only prereveal geometry and the registered construction
summary.  It never reads behavioral outcomes and never changes the original
minimum-retention gate.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.failure_localization import (
    balanced_axis_decomposition,
    fragility_curve,
    heldout_retention_rows,
    leave_one_level_out,
    projector_from_signature,
    quantile_receipt,
    spectral_endpoint,
)


SIGNATURE_RE = re.compile(r"signature__m(\d+)__p(\d+)__r(\d+)__t(\d+)")
SPECTRUM_RE = re.compile(r"signature_spectrum__m(\d+)__p(\d+)__r(\d+)__t(\d+)")


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


def folds_for_design(design: dict[str, Any]) -> list[tuple[str, list[tuple[str, str, int]], list[tuple[str, str, int]]]]:
    prompts = design["prompt_group_halves"]
    replicas = design["replica_halves"]
    checkpoints = [int(value) for value in design["checkpoints"]]

    def cells(prompt_values: list[str], replica_values: list[str]) -> list[tuple[str, str, int]]:
        return [
            (prompt, replica, checkpoint)
            for prompt in prompt_values
            for replica in replica_values
            for checkpoint in checkpoints
        ]

    quadrants = {
        "Q00": cells(prompts["P0"], replicas["S0"]),
        "Q01": cells(prompts["P0"], replicas["S1"]),
        "Q10": cells(prompts["P1"], replicas["S0"]),
        "Q11": cells(prompts["P1"], replicas["S1"]),
    }
    return [
        ("Q00->Q11", quadrants["Q00"], quadrants["Q11"]),
        ("Q11->Q00", quadrants["Q11"], quadrants["Q00"]),
        ("Q01->Q10", quadrants["Q01"], quadrants["Q10"]),
        ("Q10->Q01", quadrants["Q10"], quadrants["Q01"]),
    ]


def layer_number(module: str) -> int:
    match = re.search(r"layers\.(\d+)", module)
    if not match:
        raise ValueError(f"cannot parse layer from {module}")
    return int(match.group(1))


def source_rank_rows(summary: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    return {
        (module["module_path"], int(row["rank"])): row
        for module in summary["module_summaries"]
        for row in module["rank_curve"]
    }


def failure_axis_summary(
    rows: list[dict[str, Any]], *, ranks: set[int] | None = None
) -> dict[str, Any]:
    selected = rows if ranks is None else [row for row in rows if int(row["rank"]) in ranks]
    result: dict[str, Any] = {}
    for axis in ("prompt", "replica", "checkpoint"):
        axis_rows: dict[str, Any] = {}
        for level in sorted({str(row[axis]) for row in selected}):
            subset = [row for row in selected if str(row[axis]) == level]
            counts = Counter(str(row["spectral_status"]) for row in subset)
            failures = len(subset) - counts.get("local_endpoint_pass", 0)
            axis_rows[level] = {
                "rows": len(subset),
                "local_endpoint_pass": counts.get("local_endpoint_pass", 0),
                "unresolved_boundary": counts.get("unresolved_boundary", 0),
                "below_spectral_floor": counts.get("below_spectral_floor", 0),
                "failure_rate": float(failures / len(subset)),
            }
        result[axis] = axis_rows
    return result


def run_audit(
    *,
    protocol_path: Path,
    protocol_amendment_path: Path,
    summary_path: Path,
    primitives_path: Path,
    out_dir: Path,
) -> dict[str, Any]:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if protocol.get("status") != "frozen_target_blind_diagnostic":
        raise ValueError("diagnostic protocol is not frozen")
    if protocol.get("outcomes_used") is not False:
        raise ValueError("diagnostic protocol must prohibit outcomes")
    amendment = json.loads(protocol_amendment_path.read_text(encoding="utf-8"))
    if amendment.get("status") != "frozen_prereveal_engineering_amendment":
        raise ValueError("diagnostic protocol amendment is not frozen")
    if amendment.get("parent_protocol_sha256") != sha256_file(protocol_path):
        raise ValueError("diagnostic amendment does not bind the supplied protocol")
    if amendment.get("outcomes_existed_at_freeze") is not False:
        raise ValueError("diagnostic amendment must precede outcomes")
    own_hashes = {
        "cli": sha256_file(Path(__file__).resolve()),
        "failure_localization_module": sha256_file(
            Path(__file__).resolve().parents[1] / "rsi_topology" / "failure_localization.py"
        ),
    }
    if own_hashes != amendment["implementation_sha256"]:
        raise ValueError("implementation hashes do not match the frozen protocol")
    expected = protocol["source_artifacts"]
    actual_source_hashes = {
        "summary": sha256_file(summary_path),
        "primitives": sha256_file(primitives_path),
    }
    if actual_source_hashes != expected:
        raise ValueError("source artifact hashes do not match the frozen protocol")
    if out_dir.exists():
        raise FileExistsError(f"refusing to overwrite output directory: {out_dir}")
    out_dir.mkdir(parents=True)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    design = protocol["design"]
    modules = list(design["module_paths"])
    prompts = list(design["prompt_groups"])
    replicas = list(design["replicas"])
    checkpoints = [int(value) for value in design["checkpoints"]]
    ranks = list(range(1, int(protocol["maximum_rank"]) + 1))
    relative_floor = float(protocol["relative_singular_value_floor"])
    boundary_gap = float(protocol["minimum_boundary_gap_ratio"])
    thresholds = {
        int(rank): (None if value is None else float(value))
        for rank, value in summary["null_thresholds"].items()
    }
    folds = folds_for_design(design)

    signature_arrays: dict[tuple[str, str, str, int], np.ndarray] = {}
    spectrum_arrays: dict[tuple[str, str, str, int], np.ndarray] = {}
    stored_projectors: dict[tuple[str, int, tuple[str, str, int]], np.ndarray] = {}
    with np.load(primitives_path, allow_pickle=False) as archive:
        primitive_manifest = json.loads(
            archive["manifest_json_utf8"].tobytes().decode("utf-8")
        )
        if primitive_manifest["protocol_sha256"] != summary["protocol_sha256"]:
            raise ValueError("primitive manifest and source summary protocol disagree")
        for key in archive.files:
            signature_match = SIGNATURE_RE.fullmatch(key)
            spectrum_match = SPECTRUM_RE.fullmatch(key)
            match = signature_match or spectrum_match
            if not match:
                continue
            module_index, prompt_index, replica_index, checkpoint = map(int, match.groups())
            cell_key = (
                modules[module_index],
                prompts[prompt_index],
                replicas[replica_index],
                checkpoint,
            )
            if signature_match:
                signature_arrays[cell_key] = np.asarray(archive[key], dtype=np.float64)
            else:
                spectrum_arrays[cell_key] = np.asarray(archive[key], dtype=np.float64)
        for item in primitive_manifest["geometry_index"]:
            if item["kind"] != "local_projector":
                continue
            cell = (str(item["cell"][0]), str(item["cell"][1]), int(item["cell"][2]))
            stored_projectors[(str(item["module"]), int(item["rank"]), cell)] = np.asarray(
                archive[item["array_key"]], dtype=np.float64
            )

    expected_nodes = {
        (module, prompt, replica, checkpoint)
        for module in modules
        for prompt in prompts
        for replica in replicas
        for checkpoint in checkpoints
    }
    if set(signature_arrays) != expected_nodes or set(spectrum_arrays) != expected_nodes:
        raise ValueError("signature/spectrum universe is incomplete or contains extras")

    spectral_rows: list[dict[str, Any]] = []
    family_cells: dict[tuple[str, int], dict[tuple[str, str, int], np.ndarray]] = defaultdict(dict)
    for module in modules:
        for prompt in prompts:
            for replica in replicas:
                for checkpoint in checkpoints:
                    node = (module, prompt, replica, checkpoint)
                    signature = signature_arrays[node]
                    spectrum = spectrum_arrays[node]
                    reproduced = np.linalg.svd(signature, compute_uv=False)
                    if not np.allclose(reproduced, spectrum, atol=1e-12, rtol=1e-12):
                        raise ValueError(f"stored spectrum does not reproduce for {node}")
                    for rank in ranks:
                        endpoint = spectral_endpoint(
                            spectrum,
                            rank=rank,
                            relative_floor=relative_floor,
                            minimum_boundary_gap_ratio=boundary_gap,
                        )
                        spectral_rows.append(
                            {
                                "module_path": module,
                                "layer": layer_number(module),
                                "rank": rank,
                                "prompt": prompt,
                                "replica": replica,
                                "checkpoint": checkpoint,
                                "spectral_status": endpoint["status"],
                                "spectral_ratio": endpoint["spectral_ratio"],
                                "boundary_gap_ratio": endpoint["boundary_gap_ratio"],
                            }
                        )
                        if endpoint["eligible"]:
                            family_cells[(module, rank)][(prompt, replica, checkpoint)] = (
                                projector_from_signature(signature, rank)
                            )

    source_rows = source_rank_rows(summary)
    family_rows: list[dict[str, Any]] = []
    retention_rows: list[dict[str, Any]] = []
    fragility_rows: list[dict[str, Any]] = []
    module_analyses: list[dict[str, Any]] = []
    max_projector_error = 0.0
    max_summary_error = 0.0
    expected_cell_count = len(prompts) * len(replicas) * len(checkpoints)
    for module in modules:
        for rank in ranks:
            local_projectors = family_cells[(module, rank)]
            local_failures = [
                row
                for row in spectral_rows
                if row["module_path"] == module
                and int(row["rank"]) == rank
                and row["spectral_status"] != "local_endpoint_pass"
            ]
            source_row = source_rows[(module, rank)]
            row = {
                "module_path": module,
                "layer": layer_number(module),
                "rank": rank,
                "local_endpoint_pass_cells": len(local_projectors),
                "local_endpoint_failure_cells": len(local_failures),
                "unresolved_boundary_cells": sum(
                    item["spectral_status"] == "unresolved_boundary"
                    for item in local_failures
                ),
                "below_spectral_floor_cells": sum(
                    item["spectral_status"] == "below_spectral_floor"
                    for item in local_failures
                ),
                "eligible_family": False,
                "family_failure": "local_spectral_endpoint",
            }
            if len(local_projectors) == expected_cell_count:
                try:
                    cell_rows, fold_receipts = heldout_retention_rows(
                        local_projectors,
                        folds,
                        rank=rank,
                        minimum_consensus_gap_ratio=boundary_gap,
                    )
                    row["eligible_family"] = True
                    row["family_failure"] = None
                except ValueError as exc:
                    row["family_failure"] = f"consensus:{exc}"
                    cell_rows = []
                    fold_receipts = []
            else:
                cell_rows = []
                fold_receipts = []
            if bool(source_row["eligible_band_endpoint"]) != bool(row["eligible_family"]):
                raise ValueError(f"family eligibility disagrees with source summary: {(module, rank)}")
            family_rows.append(row)
            if not row["eligible_family"]:
                continue

            threshold = thresholds[rank]
            if threshold is None:
                raise ValueError("eligible family has no registered null threshold")
            for cell_row in cell_rows:
                prompt, replica, checkpoint = cell_row.pop("cell")
                cell_row.update(
                    {
                        "module_path": module,
                        "layer": layer_number(module),
                        "rank": rank,
                        "prompt": prompt,
                        "replica": replica,
                        "checkpoint": checkpoint,
                        "registered_null_threshold": threshold,
                        "at_or_below_registered_null": bool(
                            cell_row["worst_direction_retention"] <= threshold
                        ),
                    }
                )
                retention_rows.append(cell_row)
            values = [float(item["worst_direction_retention"]) for item in cell_rows]
            energy_values = [
                float(item["gauge_invariant_energy_retention"]) for item in cell_rows
            ]
            registered_min = min(values)
            registered_mean = min(
                float(item["mean_principal_retention"]) for item in fold_receipts
            )
            max_summary_error = max(
                max_summary_error,
                abs(registered_min - float(source_row["worst_direction_retention"])),
                abs(registered_mean - float(source_row["mean_principal_retention"])),
                abs(threshold - float(source_row["null_threshold"])),
            )
            for cell, projector in local_projectors.items():
                stored = stored_projectors.get((module, rank, cell))
                if stored is None:
                    raise ValueError("eligible projector is missing from primitive geometry")
                max_projector_error = max(
                    max_projector_error, float(np.max(np.abs(projector - stored)))
                )
            curve = fragility_curve(values, threshold)
            for point in curve.pop("points"):
                fragility_rows.append(
                    {
                        "module_path": module,
                        "layer": layer_number(module),
                        "rank": rank,
                        **point,
                    }
                )
            sorted_cells = sorted(
                cell_rows, key=lambda item: float(item["worst_direction_retention"])
            )
            axis_decomposition = balanced_axis_decomposition(
                cell_rows,
                value_field="worst_direction_retention",
                axes=("prompt", "replica", "checkpoint"),
            )
            leave_one = {
                axis: leave_one_level_out(
                    cell_rows,
                    value_field="worst_direction_retention",
                    axis=axis,
                    threshold=threshold,
                )
                for axis in ("prompt", "replica", "checkpoint")
            }
            diagnostic_thresholds = protocol["diagnostic_thresholds"]
            axis_fractions = {
                axis: float(
                    axis_decomposition["axes"][axis]["fraction_total"]
                )
                for axis in ("prompt", "replica", "checkpoint")
            }
            largest_axis = max(axis_fractions, key=axis_fractions.get)
            dominant_axis = (
                largest_axis
                if axis_fractions[largest_axis]
                >= float(diagnostic_thresholds["axis_dominance_fraction"])
                else "mixed_or_interaction"
            )
            single_level_rescues = [
                item
                for axis_rows in leave_one.values()
                for item in axis_rows
                if float(item["margin_to_registered_null"]) > 0.0
            ]
            below_fraction = float(curve["fraction_at_or_below_threshold"])
            module_analyses.append(
                {
                    "module_path": module,
                    "layer": layer_number(module),
                    "rank": rank,
                    "registered_null_threshold": threshold,
                    "registered_worst_direction_retention": registered_min,
                    "registered_margin": registered_min - threshold,
                    "fold_receipts": fold_receipts,
                    "worst_direction_distribution": quantile_receipt(values),
                    "gauge_invariant_energy_distribution": quantile_receipt(energy_values),
                    "minimum_fold_mean_energy_retention": registered_mean,
                    "mean_energy_to_worst_floor_ratio": (
                        float(np.mean(energy_values) / registered_min)
                        if registered_min > 0.0
                        else None
                    ),
                    "fragility": curve,
                    "axis_decomposition": axis_decomposition,
                    "leave_one_level_out": leave_one,
                    "diagnostic_classification": {
                        "failure_extent": (
                            "sparse"
                            if below_fraction
                            <= float(
                                diagnostic_thresholds[
                                    "sparse_failure_maximum_fraction"
                                ]
                            )
                            else "diffuse"
                        ),
                        "dominant_main_effect_axis": dominant_axis,
                        "dominant_axis_fraction_total": float(
                            axis_fractions[largest_axis]
                        ),
                        "single_axis_level_rescue_exists": bool(
                            single_level_rescues
                        ),
                        "single_axis_level_rescues": single_level_rescues,
                    },
                    "worst_cells": [
                        {
                            "prompt": item["prompt"],
                            "replica": item["replica"],
                            "checkpoint": item["checkpoint"],
                            "fold": item["fold"],
                            "worst_direction_retention": item[
                                "worst_direction_retention"
                            ],
                        }
                        for item in sorted_cells[:10]
                    ],
                }
            )

    if max_projector_error > 1e-10 or max_summary_error > 1e-10:
        raise ValueError("diagnostic replay does not reconcile with sealed primitives/summary")
    eligible_families = [
        {"module_path": row["module_path"], "layer": row["layer"], "rank": row["rank"]}
        for row in family_rows
        if row["eligible_family"]
    ]
    diagnostic_summary = {
        "schema_version": "functional_lineage_failure_localization_v0_1",
        "status": "diagnostic_complete",
        "target_blind": True,
        "outcomes_used": False,
        "registered_result_unchanged": "noise_floor_only",
        "signed_interventions_authorized": False,
        "protocol_sha256": sha256_file(protocol_path),
        "protocol_amendment_sha256": sha256_file(protocol_amendment_path),
        "implementation_sha256": own_hashes,
        "source_artifacts": actual_source_hashes,
        "universe": {
            "modules": len(modules),
            "prompts": len(prompts),
            "replicas": len(replicas),
            "checkpoints": len(checkpoints),
            "nodes": len(expected_nodes),
            "ranks": len(ranks),
            "spectral_cell_rows": len(spectral_rows),
            "retention_cell_rows": len(retention_rows),
        },
        "reconciliation": {
            "eligible_families_match_source": True,
            "maximum_projector_abs_error": max_projector_error,
            "maximum_summary_abs_error": max_summary_error,
        },
        "eligible_families": eligible_families,
        "spectral_failure_axis_summary": {
            "all_ranks": failure_axis_summary(spectral_rows),
            "rank1": failure_axis_summary(spectral_rows, ranks={1}),
        },
        "family_boundaries": family_rows,
        "module_analyses": module_analyses,
        "claim_boundary": protocol["claim_boundary"],
    }

    summary_output = out_dir / "failure_localization_summary.json"
    spectral_output = out_dir / "spectral_cells.csv"
    family_output = out_dir / "family_boundaries.csv"
    retention_output = out_dir / "retention_cells.csv"
    fragility_output = out_dir / "certification_fragility_curve.csv"
    write_json(summary_output, diagnostic_summary)
    write_csv(
        spectral_output,
        spectral_rows,
        [
            "module_path", "layer", "rank", "prompt", "replica", "checkpoint",
            "spectral_status", "spectral_ratio", "boundary_gap_ratio",
        ],
    )
    write_csv(
        family_output,
        family_rows,
        [
            "module_path", "layer", "rank", "local_endpoint_pass_cells",
            "local_endpoint_failure_cells", "unresolved_boundary_cells",
            "below_spectral_floor_cells", "eligible_family", "family_failure",
        ],
    )
    write_csv(
        retention_output,
        retention_rows,
        [
            "module_path", "layer", "rank", "fold", "prompt", "replica",
            "checkpoint", "worst_direction_retention",
            "gauge_invariant_energy_retention", "registered_null_threshold",
            "at_or_below_registered_null",
        ],
    )
    write_csv(
        fragility_output,
        fragility_rows,
        [
            "module_path", "layer", "rank", "excluded_worst_cells",
            "remaining_cells", "retention_floor", "margin_to_registered_null",
        ],
    )
    outputs = [
        summary_output,
        spectral_output,
        family_output,
        retention_output,
        fragility_output,
    ]
    receipt = {
        "schema_version": "functional_lineage_failure_localization_receipt_v0_1",
        "status": "completed",
        "target_blind": True,
        "outcomes_used": False,
        "registered_result_unchanged": "noise_floor_only",
        "protocol_sha256": sha256_file(protocol_path),
        "protocol_amendment_sha256": sha256_file(protocol_amendment_path),
        "implementation_sha256": own_hashes,
        "source_artifacts": actual_source_hashes,
        "output_sha256": {path.name: sha256_file(path) for path in outputs},
    }
    write_json(out_dir / "audit_receipt.json", receipt)
    return diagnostic_summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--protocol-amendment", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--primitives", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run_audit(
        protocol_path=args.protocol.resolve(),
        protocol_amendment_path=args.protocol_amendment.resolve(),
        summary_path=args.summary.resolve(),
        primitives_path=args.primitives.resolve(),
        out_dir=args.out_dir.resolve(),
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "eligible_families": result["eligible_families"],
                "module_analysis_count": len(result["module_analyses"]),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
