#!/usr/bin/env python3
"""Run the prospectively registered ASMP-11 v0.2.1 bounds experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from math import comb
from pathlib import Path
from time import monotonic
from typing import Any, Iterable

from crossover_frontier import (
    CLASSIFICATION_STATUSES,
    STATUS_CERTIFIED,
    build_minimum_width_bracket,
    classification_record,
    deterministic_cover_bounds,
    find_exact_design,
    high_width_anchor,
    intermediate_widths,
    metric_robustness_probes,
    replayable_lower_bound,
    verify_cover,
    classify_cost_interval,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_MANIFEST = ROOT / "experiment_v0_2_1.json"
DEFAULT_ANCHOR = ROOT / "prior_anchor_v0_2.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def compact_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(canonical_json(payload), encoding="utf-8")
    os.replace(temporary, path)


def write_jsonl(path: Path, rows: Iterable[dict[str, object]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(compact_json(row) + "\n")
    os.replace(temporary, path)


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_registration(registration_path: Path) -> dict[str, Any]:
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    if registration.get("status") != "prospective_registration_before_claim_grid_execution":
        raise RuntimeError("registration status does not authorize claim-grid execution")
    mismatches = []
    for relative, expected in registration.get("source_hashes", {}).items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected:
            mismatches.append(relative)
    if mismatches:
        raise RuntimeError(f"registration source mismatch: {mismatches}")
    return registration


def validate_prior_anchor(anchor_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    anchor = json.loads(anchor_path.read_text(encoding="utf-8"))
    source_frontier = (ROOT / anchor["source_frontier"]).resolve()
    source_registration = (ROOT / anchor["source_registration"]).resolve()
    checks = {
        "frontier_exists": source_frontier.is_file(),
        "registration_exists": source_registration.is_file(),
        "frontier_sha256": source_frontier.is_file()
        and sha256(source_frontier) == anchor["source_frontier_sha256"],
        "registration_sha256": source_registration.is_file()
        and sha256(source_registration) == anchor["source_registration_sha256"],
    }
    if not all(checks.values()):
        raise RuntimeError(f"sealed v0.2 prior anchor mismatch: {checks}")
    return anchor, [{"check": key, "pass": value} for key, value in checks.items()]


def cover_record(certificate: Any, elapsed_seconds: float) -> dict[str, object]:
    return {
        "n": certificate.n,
        "k": certificate.support_size,
        "block_size": certificate.block_size,
        "lower_bound": certificate.lower_bound,
        "lower_bound_components": {
            "counting": certificate.counting_lower_bound,
            "schoenheim": certificate.schoenheim_lower_bound,
        },
        "upper_bound": certificate.upper_bound,
        "optimum_certified": certificate.optimum_certified,
        "construction_status": certificate.construction_status,
        "stop_reason": certificate.stop_reason,
        "greedy_rounds": certificate.greedy_rounds,
        "gain_evaluations": certificate.gain_evaluations,
        "universe_size": certificate.universe_size,
        "candidate_block_count": certificate.candidate_block_count,
        "elapsed_seconds": elapsed_seconds,
        "selected_blocks": [list(block) for block in certificate.selected_blocks],
    }


def anchor_lookup(anchor: dict[str, Any]) -> dict[tuple[int, int], dict[str, Any]]:
    return {(int(row["n"]), int(row["k"])): row for row in anchor["rows"]}


def verify_anchor_costs(
    anchor: dict[str, Any],
    flip_rates: tuple[Fraction, ...],
    alpha: Fraction,
    target_power: Fraction,
    sample_cap: int,
) -> list[dict[str, object]]:
    receipts = []
    for row in anchor["rows"]:
        n, k = int(row["n"]), int(row["k"])
        expected_width = high_width_anchor(n, k)
        if int(row["block_size"]) != expected_width:
            raise RuntimeError("sealed anchor width does not match the draft rule")
        for flip_rate in flip_rates:
            design = find_exact_design(
                int(row["query_count"]),
                flip_rate,
                alpha,
                target_power,
                sample_cap,
            )
            expected = int(row["total_samples"][str(flip_rate)])
            passed = design is not None and design.total_samples == expected
            receipts.append(
                {
                    "n": n,
                    "k": k,
                    "block_size": expected_width,
                    "flip_rate": str(flip_rate),
                    "query_count": int(row["query_count"]),
                    "expected_total_samples": expected,
                    "replayed_total_samples": design.total_samples if design else None,
                    "pass": passed,
                }
            )
    if not all(row["pass"] for row in receipts):
        raise RuntimeError("sealed v0.2 anchor cost failed exact replay")
    return receipts


def _design_is_exact(record: dict[str, object] | None, alpha: Fraction, power: Fraction) -> bool:
    if record is None:
        return True
    return (
        Fraction(str(record["familywise_error_upper"])) <= alpha
        and Fraction(str(record["signal_power_lower"])) >= power
        and int(record["total_samples"])
        == int(record["query_count"]) * int(record["samples_per_query"])
    )


def execute(
    registration_path: Path,
    output_dir: Path,
    manifest_path: Path = DEFAULT_MANIFEST,
    anchor_path: Path = DEFAULT_ANCHOR,
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    registration = validate_registration(registration_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    config = manifest["asmp11"]
    resource = config["resource_policy"]
    anchor, anchor_binding_checks = validate_prior_anchor(anchor_path)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"write-once output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    started_utc = utc_now()
    started = monotonic()
    dimensions = tuple(int(value) for value in config["dimensions"])
    degrees = tuple(int(value) for value in config["degrees"])
    flip_rates = tuple(parse_fraction(value) for value in config["flip_rates"])
    alpha = parse_fraction(config["alpha"])
    target_power = parse_fraction(config["target_power"])
    sample_cap = int(config["sample_cap"])
    expected = config["expected_counts"]
    anchor_receipts = verify_anchor_costs(
        anchor, flip_rates, alpha, target_power, sample_cap
    )
    anchors = anchor_lookup(anchor)

    covering_rows: list[dict[str, object]] = []
    certificates: dict[tuple[int, int, int], Any] = {}
    operation_events: list[dict[str, object]] = []
    total_wall_stop = False
    for n in dimensions:
        for k in degrees:
            for block_size in intermediate_widths(n, k):
                if monotonic() - started >= float(resource["max_total_wall_seconds"]):
                    total_wall_stop = True
                    break
                cell_started = monotonic()
                certificate = deterministic_cover_bounds(
                    n,
                    block_size,
                    k,
                    max_greedy_rounds=int(resource["max_greedy_rounds_per_cell"]),
                    max_candidate_blocks=int(resource["max_candidate_blocks_per_cell"]),
                    hard_wall_seconds=float(resource["hard_wall_seconds_per_cell"]),
                )
                elapsed = monotonic() - cell_started
                row = cover_record(certificate, elapsed)
                covering_rows.append(row)
                certificates[(n, k, block_size)] = certificate
                event = {
                    "event": "covering_cell_complete",
                    "n": n,
                    "k": k,
                    "block_size": block_size,
                    "construction_status": certificate.construction_status,
                    "stop_reason": certificate.stop_reason,
                    "elapsed_seconds": elapsed,
                }
                operation_events.append(event)
                atomic_json(
                    output_dir / "covering_checkpoint.json",
                    {
                        "schema_version": "asmp11_v0_2_1_covering_checkpoint",
                        "complete_cells": len(covering_rows),
                        "rows": covering_rows,
                    },
                )
            if total_wall_stop:
                break
        if total_wall_stop:
            break

    cost_rows: list[dict[str, object]] = []
    missing_cost_keys: list[dict[str, object]] = []
    for n in dimensions:
        for k in degrees:
            for block_size in intermediate_widths(n, k):
                certificate = certificates.get((n, k, block_size))
                for flip_rate in flip_rates:
                    if certificate is None or monotonic() - started >= float(
                        resource["max_total_wall_seconds"]
                    ):
                        total_wall_stop = True
                        missing_cost_keys.append(
                            {
                                "n": n,
                                "k": k,
                                "block_size": block_size,
                                "flip_rate": str(flip_rate),
                                "reason": "total_wall_budget",
                            }
                        )
                        continue
                    primary = classify_cost_interval(
                        certificate.lower_bound,
                        certificate.upper_bound,
                        comb(n, k),
                        flip_rate,
                        alpha,
                        target_power,
                        sample_cap,
                    )
                    primary_record = classification_record(primary)
                    probes = metric_robustness_probes(
                        primary,
                        comb(n, k),
                        flip_rate,
                        alpha,
                        target_power,
                        sample_cap,
                    )
                    cost_rows.append(
                        {
                            "n": n,
                            "k": k,
                            "block_size": block_size,
                            "flip_rate": str(flip_rate),
                            "primary": primary_record,
                            "metric_robustness_probes": list(probes),
                        }
                    )
                    atomic_json(
                        output_dir / "cost_checkpoint.json",
                        {
                            "schema_version": "asmp11_v0_2_1_cost_checkpoint",
                            "complete_cells": len(cost_rows),
                            "missing_cells": missing_cost_keys,
                        },
                    )

    brackets: list[dict[str, object]] = []
    grouped: dict[tuple[int, int, str], list[dict[str, object]]] = defaultdict(list)
    for row in cost_rows:
        grouped[(int(row["n"]), int(row["k"]), str(row["flip_rate"]))].append(
            {
                "block_size": row["block_size"],
                "status": row["primary"]["status"],  # type: ignore[index]
            }
        )
    for n in dimensions:
        for k in degrees:
            for flip_rate in flip_rates:
                key = (n, k, str(flip_rate))
                if len(grouped[key]) != len(intermediate_widths(n, k)):
                    continue
                anchor_row = anchors[(n, k)]
                bracket = build_minimum_width_bracket(
                    k, grouped[key], int(anchor_row["block_size"])
                )
                brackets.append(
                    {
                        "n": n,
                        "k": k,
                        "flip_rate": str(flip_rate),
                        "anchor_query_count": int(anchor_row["query_count"]),
                        **bracket,
                    }
                )

    binding_ok = all(row["pass"] for row in anchor_binding_checks) and all(
        row["pass"] for row in anchor_receipts
    )
    witness_ok = all(
        verify_cover(
            int(row["n"]),
            int(row["block_size"]),
            int(row["k"]),
            row["selected_blocks"],  # type: ignore[arg-type]
        )
        and len(row["selected_blocks"]) == int(row["upper_bound"])  # type: ignore[arg-type]
        for row in covering_rows
    )
    lower_ok = all(
        replayable_lower_bound(int(row["n"]), int(row["block_size"]), int(row["k"]))[
            "certified_lower_bound"
        ]
        == int(row["lower_bound"])
        and int(row["lower_bound"]) <= int(row["upper_bound"])
        for row in covering_rows
    )
    probability_ok = all(
        _design_is_exact(row["primary"]["baseline"], alpha, target_power)  # type: ignore[index,arg-type]
        and _design_is_exact(row["primary"]["best_certified"], alpha, target_power)  # type: ignore[index,arg-type]
        and _design_is_exact(row["primary"]["optimistic_floor"], alpha, target_power)  # type: ignore[index,arg-type]
        for row in cost_rows
    )
    total_classification = (
        len(covering_rows) == int(expected["covering_cells"])
        and len(cost_rows) == int(expected["cost_cells"])
        and not missing_cost_keys
        and all(row["primary"]["status"] in CLASSIFICATION_STATUSES for row in cost_rows)  # type: ignore[index]
    )
    bracket_ok = len(brackets) == int(expected["brackets"]) and all(
        row["s_star"] is None
        or not row["unresolved_widths"]
        and all(
            status == "crossover_impossible_under_bounds"
            for width, status in row["status_by_width"].items()  # type: ignore[union-attr]
            if int(width) < int(row["s_star"])
        )
        for row in brackets
    )
    resource_honesty = all(
        not bool(row["optimum_certified"])
        or int(row["lower_bound"]) == int(row["upper_bound"])
        for row in covering_rows
    ) and all(
        row["stop_reason"] == "cover_complete"
        or verify_cover(
            int(row["n"]),
            int(row["block_size"]),
            int(row["k"]),
            row["selected_blocks"],  # type: ignore[arg-type]
        )
        for row in covering_rows
    )
    expected_probe_ids = {
        "P1_bound_interval_adversary",
        "P2_query_count_only",
        "P3_stricter_familywise_error",
        "P4_stricter_power",
        "P5_exact_independent_fwer",
    }
    probes_complete = all(
        len(row["metric_robustness_probes"]) == int(expected["metric_probes_per_cost_cell"])  # type: ignore[arg-type]
        and {probe["probe_id"] for probe in row["metric_robustness_probes"]}  # type: ignore[index,union-attr]
        == expected_probe_ids
        for row in cost_rows
    )
    gates = {
        "B0_binding": binding_ok,
        "B1_witness_validity": witness_ok,
        "B2_lower_bound_replay": lower_ok,
        "B3_probability_exactness": probability_ok,
        "B4_total_classification": total_classification,
        "B5_minimum_width": bracket_ok,
        "B6_resource_honesty": resource_honesty,
        "B7_metric_probe_completeness": probes_complete,
    }
    core_valid = all(gates.values())
    status_counts = Counter(row["primary"]["status"] for row in cost_rows)  # type: ignore[index]
    probe_summary: dict[str, dict[str, int]] = {}
    for probe_id in sorted(expected_probe_ids):
        probe_rows = [
            probe
            for row in cost_rows
            for probe in row["metric_robustness_probes"]  # type: ignore[union-attr]
            if probe["probe_id"] == probe_id
        ]
        probe_summary[probe_id] = {
            "cells": len(probe_rows),
            "agrees_with_primary": sum(bool(row["agrees_with_primary"]) for row in probe_rows),
            "disagrees_with_primary": sum(not bool(row["agrees_with_primary"]) for row in probe_rows),
        }

    result_layer = {
        "schema_version": "asmp11_intermediate_crossover_result_layer_v0_2_1",
        "experimental_unit": "one deterministic (n,k,s) covering cell",
        "counts": {
            "covering_cells": len(covering_rows),
            "cost_cells": len(cost_rows),
            "brackets": len(brackets),
            "status": dict(sorted(status_counts.items())),
        },
        "brackets": brackets,
        "raw_artifacts": {
            "covering_cells": "covering_cells.jsonl",
            "cost_cells": "cost_cells.jsonl",
        },
    }
    reliability_layer = {
        "schema_version": "asmp11_intermediate_crossover_reliability_layer_v0_2_1",
        "binding_gates": gates,
        "metric_firewall": {
            "selection": ["greedy_uncovered_support_gain"],
            "evidence": [
                "verified_cover_upper_bound",
                "replayed_combinatorial_lower_bound",
                "exact_total_oracle_samples",
                "three_way_crossover_status",
            ],
            "hazard": [
                "greedy_round_cap",
                "operational_wall_stop",
                "candidate_family_cap",
                "covering_bound_width",
                "sample_cap_failure",
            ],
            "overlap": [],
        },
        "metric_robustness": probe_summary,
        "anchor_replay": anchor_receipts,
        "independent_verification": "pending separate verify_result.py execution",
    }
    claim_layer = {
        "schema_version": "asmp11_intermediate_crossover_claim_layer_v0_2_1",
        "verdict": "claim_ready_for_independent_verification" if core_valid else "not_established",
        "claim_scope": "model_only",
        "observed": "Deterministic covering bounds and exact cost classifications on the frozen intermediate-width grid.",
        "inferred": "Only strata with complete certified brackets support a minimum-width statement.",
        "not_supported": [
            "general adaptive group-testing rates",
            "an observational minimax lower bound",
            "white-box neural backdoor detection",
            "overall resource dominance after pricing intervention width or harm",
        ],
        "robustness": "Five non-binding metric probes are reported cell by cell; disagreement is retained as sensitivity.",
        "confounds": [
            "covering gaps can widen minimum-width brackets",
            "Bonferroni total samples do not price intervention cost",
            "the parity oracle is transparent and finite",
        ],
        "next_experiment": "Independently verify every artifact, then target unresolved covering cells with a separately frozen proof-producing solver.",
    }
    elapsed_total = monotonic() - started
    operation_layer = {
        "schema_version": "asmp11_intermediate_crossover_operation_layer_v0_2_1",
        "run_status": "complete" if core_valid else "partial_or_invalid",
        "started_utc": started_utc,
        "finished_utc": utc_now(),
        "elapsed_seconds": elapsed_total,
        "total_wall_stop": total_wall_stop,
        "missing_cost_cells": missing_cost_keys,
        "resource_policy": resource,
        "stop_reason_counts": dict(sorted(Counter(row["stop_reason"] for row in covering_rows).items())),
        "registration": {
            "path": str(registration_path),
            "sha256": sha256(registration_path),
            "source_commit": registration.get("source_commit"),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "git_head": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
        },
        "events": operation_events,
    }

    write_jsonl(output_dir / "covering_cells.jsonl", covering_rows)
    write_jsonl(output_dir / "cost_cells.jsonl", cost_rows)
    atomic_json(output_dir / "result_layer.json", result_layer)
    atomic_json(output_dir / "reliability_layer.json", reliability_layer)
    atomic_json(output_dir / "claim_layer.json", claim_layer)
    atomic_json(output_dir / "operation_layer.json", operation_layer)
    outputs = {
        path.name: sha256(path)
        for path in sorted(output_dir.iterdir())
        if path.is_file() and path.name != "receipt.json"
    }
    receipt = {
        "schema_version": "asmp11_intermediate_crossover_receipt_v0_2_1",
        "registration_sha256": sha256(registration_path),
        "manifest_sha256": sha256(manifest_path),
        "prior_anchor_sha256": sha256(anchor_path),
        "outputs": outputs,
        "verdict": claim_layer["verdict"],
    }
    atomic_json(output_dir / "receipt.json", receipt)
    return result_layer, reliability_layer, claim_layer, operation_layer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--prior-anchor", type=Path, default=DEFAULT_ANCHOR)
    args = parser.parse_args()
    _, reliability, claim, operation = execute(
        args.registration.resolve(),
        args.output_dir.resolve(),
        args.manifest.resolve(),
        args.prior_anchor.resolve(),
    )
    print(
        canonical_json(
            {
                "verdict": claim["verdict"],
                "gates": reliability["binding_gates"],
                "run_status": operation["run_status"],
                "output_dir": str(args.output_dir.resolve()),
            }
        ),
        end="",
    )
    return 0 if all(reliability["binding_gates"].values()) else 2  # type: ignore[union-attr]


if __name__ == "__main__":
    raise SystemExit(main())
