#!/usr/bin/env python3
"""Independent artifact verifier for ASMP-11 v0.2.1.

This file deliberately does not import ``crossover_frontier`` or ``run``.  It
reimplements cover replay, lower bounds, exact binomial calibration,
classification, brackets, and all five metric probes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parent
CERTIFIED = "crossover_certified"
IMPOSSIBLE = "crossover_impossible_under_bounds"
UNRESOLVED = "unresolved_covering_gap"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def independent_schoenheim(n: int, block_size: int, support_size: int) -> int:
    if support_size == 0:
        return 1
    return ceil_div(
        n * independent_schoenheim(n - 1, block_size - 1, support_size - 1),
        block_size,
    )


def independent_lower_bounds(n: int, block_size: int, support_size: int) -> dict[str, int]:
    counting = ceil_div(comb(n, support_size), comb(block_size, support_size))
    schoenheim = independent_schoenheim(n, block_size, support_size)
    return {
        "counting": counting,
        "schoenheim": schoenheim,
        "certified": max(counting, schoenheim),
    }


def independent_verify_cover(
    n: int,
    block_size: int,
    support_size: int,
    selected_blocks: Sequence[Sequence[int]],
) -> bool:
    target = set(combinations(range(n), support_size))
    observed: set[tuple[int, ...]] = set()
    for raw_block in selected_blocks:
        block = tuple(raw_block)
        if len(block) != block_size or tuple(sorted(block)) != block:
            return False
        if len(set(block)) != block_size or any(point not in range(n) for point in block):
            return False
        observed.update(combinations(block, support_size))
    return observed == target


@lru_cache(maxsize=None)
def independent_tail(samples: int, cutoff: int, probability: Fraction) -> Fraction:
    if cutoff < 0:
        return Fraction(0)
    if 2 * cutoff >= samples:
        return Fraction(1)
    numerator = probability.numerator
    denominator = probability.denominator
    complement = denominator - numerator
    low = sum(
        comb(samples, count)
        * numerator**count
        * complement ** (samples - count)
        for count in range(cutoff + 1)
    )
    high = sum(
        comb(samples, count)
        * numerator**count
        * complement ** (samples - count)
        for count in range(samples - cutoff, samples + 1)
    )
    return Fraction(low + high, denominator**samples)


def independent_fwer(tail: Fraction, query_count: int, mode: str) -> Fraction:
    if mode == "bonferroni":
        return min(Fraction(1), query_count * tail)
    if mode == "independent_exact":
        return Fraction(1) - (Fraction(1) - tail) ** query_count
    raise ValueError(mode)


@lru_cache(maxsize=None)
def independent_design(
    query_count: int,
    flip_rate: Fraction,
    alpha: Fraction,
    power: Fraction,
    sample_cap: int,
    mode: str = "bonferroni",
) -> dict[str, object] | None:
    for samples in range(1, sample_cap + 1):
        accepted_cutoff = None
        for cutoff in range((samples - 1) // 2 + 1):
            null_tail = independent_tail(samples, cutoff, Fraction(1, 2))
            if independent_fwer(null_tail, query_count, mode) <= alpha:
                accepted_cutoff = cutoff
            else:
                break
        if accepted_cutoff is None:
            continue
        null_tail = independent_tail(samples, accepted_cutoff, Fraction(1, 2))
        signal = independent_tail(samples, accepted_cutoff, Fraction(1) - flip_rate)
        if signal >= power:
            return {
                "query_count": query_count,
                "samples_per_query": samples,
                "total_samples": query_count * samples,
                "cutoff": accepted_cutoff,
                "null_tail": str(null_tail),
                "familywise_error_upper": str(
                    independent_fwer(null_tail, query_count, mode)
                ),
                "signal_power_lower": str(signal),
                "fwer_mode": mode,
            }
    return None


def independent_classification(
    lower: int,
    upper: int,
    baseline_q: int,
    flip_rate: Fraction,
    alpha: Fraction,
    power: Fraction,
    sample_cap: int,
    mode: str = "bonferroni",
) -> dict[str, object]:
    baseline = independent_design(baseline_q, flip_rate, alpha, power, sample_cap, mode)
    if baseline is None:
        raise AssertionError("baseline exceeded cap")
    certified = independent_design(upper, flip_rate, alpha, power, sample_cap, mode)
    feasible = [
        design
        for query_count in range(lower, upper + 1)
        if (
            design := independent_design(
                query_count, flip_rate, alpha, power, sample_cap, mode
            )
        )
        is not None
    ]
    optimistic = min(
        feasible,
        key=lambda row: (int(row["total_samples"]), int(row["query_count"])),
        default=None,
    )
    if certified is not None and int(certified["total_samples"]) < int(
        baseline["total_samples"]
    ):
        status = CERTIFIED
    elif optimistic is None or int(optimistic["total_samples"]) >= int(
        baseline["total_samples"]
    ):
        status = IMPOSSIBLE
    else:
        status = UNRESOLVED
    return {
        "status": status,
        "baseline": baseline,
        "best_certified": certified,
        "optimistic_floor": optimistic,
    }


def independent_query_status(lower: int, upper: int, baseline: int) -> str:
    if upper < baseline:
        return CERTIFIED
    if lower >= baseline:
        return IMPOSSIBLE
    return UNRESOLVED


def independent_probe_statuses(
    lower: int,
    upper: int,
    baseline_q: int,
    flip_rate: Fraction,
    alpha: Fraction,
    power: Fraction,
    sample_cap: int,
) -> dict[str, str]:
    primary = independent_classification(
        lower, upper, baseline_q, flip_rate, alpha, power, sample_cap
    )["status"]
    return {
        "P1_bound_interval_adversary": str(primary),
        "P2_query_count_only": independent_query_status(lower, upper, baseline_q),
        "P3_stricter_familywise_error": str(
            independent_classification(
                lower, upper, baseline_q, flip_rate, alpha / 2, power, sample_cap
            )["status"]
        ),
        "P4_stricter_power": str(
            independent_classification(
                lower,
                upper,
                baseline_q,
                flip_rate,
                alpha,
                Fraction(19, 20),
                sample_cap,
            )["status"]
        ),
        "P5_exact_independent_fwer": str(
            independent_classification(
                lower,
                upper,
                baseline_q,
                flip_rate,
                alpha,
                power,
                sample_cap,
                "independent_exact",
            )["status"]
        ),
    }


def independent_bracket(k: int, rows: Sequence[dict[str, Any]], anchor: int) -> dict[str, object]:
    statuses = {k: IMPOSSIBLE, anchor: CERTIFIED}
    statuses.update({int(row["block_size"]): row["primary"]["status"] for row in rows})
    s_yes = min(width for width, status in statuses.items() if status == CERTIFIED)
    unresolved = [
        width
        for width in range(k, s_yes)
        if statuses.get(width) == UNRESOLVED
    ]
    impossible = [
        width
        for width in range(k, s_yes)
        if statuses.get(width) == IMPOSSIBLE
    ]
    s_no = max(impossible) if impossible else None
    s_star = s_yes if not unresolved and len(impossible) == s_yes - k else None
    return {
        "s_no": s_no,
        "s_yes": s_yes,
        "s_star": s_star,
        "unresolved_widths": unresolved,
        "interval": None if s_star is not None else f"({s_no},{s_yes}]",
        "status_by_width": {str(width): statuses[width] for width in sorted(statuses)},
    }


def compare_design(actual: dict[str, Any] | None, expected: dict[str, object] | None) -> bool:
    if actual is None or expected is None:
        return actual is expected
    keys = {
        "query_count",
        "samples_per_query",
        "total_samples",
        "cutoff",
        "null_tail",
        "familywise_error_upper",
        "signal_power_lower",
        "fwer_mode",
    }
    return all(actual[key] == expected[key] for key in keys)


def verify_bundle(registration_path: Path, artifacts: Path) -> dict[str, object]:
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "experiment_v0_2_1.json").read_text(encoding="utf-8"))
    config = manifest["asmp11"]
    alpha = Fraction(config["alpha"])
    power = Fraction(config["target_power"])
    sample_cap = int(config["sample_cap"])
    receipt = json.loads((artifacts / "receipt.json").read_text(encoding="utf-8"))
    result = json.loads((artifacts / "result_layer.json").read_text(encoding="utf-8"))
    reliability = json.loads((artifacts / "reliability_layer.json").read_text(encoding="utf-8"))
    claim = json.loads((artifacts / "claim_layer.json").read_text(encoding="utf-8"))
    operation = json.loads((artifacts / "operation_layer.json").read_text(encoding="utf-8"))
    covers = read_jsonl(artifacts / "covering_cells.jsonl")
    costs = read_jsonl(artifacts / "cost_cells.jsonl")

    source_binding = all(
        (ROOT / relative).is_file() and sha256(ROOT / relative) == expected
        for relative, expected in registration["source_hashes"].items()
    )
    output_hashes = all(
        (artifacts / relative).is_file() and sha256(artifacts / relative) == expected
        for relative, expected in receipt["outputs"].items()
    )
    cover_checks = []
    cover_index = {}
    for row in covers:
        lower = independent_lower_bounds(row["n"], row["block_size"], row["k"])
        passed = (
            independent_verify_cover(
                row["n"], row["block_size"], row["k"], row["selected_blocks"]
            )
            and len(row["selected_blocks"]) == row["upper_bound"]
            and lower["counting"] == row["lower_bound_components"]["counting"]
            and lower["schoenheim"] == row["lower_bound_components"]["schoenheim"]
            and lower["certified"] == row["lower_bound"]
            and row["lower_bound"] <= row["upper_bound"]
            and bool(row["optimum_certified"])
            == (row["lower_bound"] == row["upper_bound"])
        )
        cover_checks.append(passed)
        cover_index[(row["n"], row["k"], row["block_size"])] = row

    cost_checks = []
    probe_checks = []
    grouped: dict[tuple[int, int, str], list[dict[str, Any]]] = {}
    for row in costs:
        cover = cover_index[(row["n"], row["k"], row["block_size"])]
        expected = independent_classification(
            cover["lower_bound"],
            cover["upper_bound"],
            comb(row["n"], row["k"]),
            Fraction(row["flip_rate"]),
            alpha,
            power,
            sample_cap,
        )
        actual = row["primary"]
        cost_checks.append(
            actual["status"] == expected["status"]
            and actual["lower_query_bound"] == cover["lower_bound"]
            and actual["upper_query_bound"] == cover["upper_bound"]
            and compare_design(actual["baseline"], expected["baseline"])
            and compare_design(actual["best_certified"], expected["best_certified"])
            and compare_design(actual["optimistic_floor"], expected["optimistic_floor"])
        )
        expected_probes = independent_probe_statuses(
            cover["lower_bound"],
            cover["upper_bound"],
            comb(row["n"], row["k"]),
            Fraction(row["flip_rate"]),
            alpha,
            power,
            sample_cap,
        )
        actual_probes = {
            probe["probe_id"]: probe["status"]
            for probe in row["metric_robustness_probes"]
        }
        probe_checks.append(actual_probes == expected_probes)
        grouped.setdefault((row["n"], row["k"], row["flip_rate"]), []).append(row)

    bracket_checks = []
    bracket_index = {
        (row["n"], row["k"], row["flip_rate"]): row
        for row in result["brackets"]
    }
    for key, rows in grouped.items():
        n, k, _ = key
        anchor = n - 3 if k == 3 else n - 2
        expected_bracket = independent_bracket(k, rows, anchor)
        actual = bracket_index.get(key)
        bracket_checks.append(
            actual is not None
            and all(actual[field] == value for field, value in expected_bracket.items())
        )

    layer_separation = (
        result["schema_version"].endswith("result_layer_v0_2_1")
        and reliability["schema_version"].endswith("reliability_layer_v0_2_1")
        and claim["schema_version"].endswith("claim_layer_v0_2_1")
        and operation["schema_version"].endswith("operation_layer_v0_2_1")
        and not (
            set(reliability["metric_firewall"]["selection"])
            & set(reliability["metric_firewall"]["evidence"])
        )
    )
    expected_counts = config["expected_counts"]
    complete = (
        len(covers) == int(expected_counts["covering_cells"])
        and len(costs) == int(expected_counts["cost_cells"])
        and len(result["brackets"]) == int(expected_counts["brackets"])
    )
    gates = {
        "V0_source_binding": source_binding,
        "V1_output_hashes": output_hashes,
        "V2_cover_witnesses_and_lower_bounds": bool(cover_checks) and all(cover_checks),
        "V3_exact_cost_classification": bool(cost_checks) and all(cost_checks),
        "V4_metric_probe_replay": bool(probe_checks) and all(probe_checks),
        "V5_minimum_width_brackets": bool(bracket_checks) and all(bracket_checks),
        "V6_layer_and_metric_firewall": layer_separation,
        "V7_complete_registered_grid": complete,
        "V8_primary_gates_passed": all(reliability["binding_gates"].values()),
        "V9_claim_operation_consistency": (
            claim["verdict"] == "claim_ready_for_independent_verification"
            and operation["run_status"] == "complete"
        ),
    }
    return {
        "schema_version": "asmp11_intermediate_crossover_independent_verification_v0_2_1",
        "verified": all(gates.values()),
        "gates": gates,
        "registration_sha256": sha256(registration_path),
        "receipt_sha256": sha256(artifacts / "receipt.json"),
        "counts": {
            "covering_cells": len(covers),
            "cost_cells": len(costs),
            "brackets": len(result["brackets"]),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Defaults to ARTIFACTS/independent_verification_v0_2_1.json",
    )
    args = parser.parse_args()
    result = verify_bundle(args.registration.resolve(), args.artifacts.resolve())
    output = args.output.resolve() if args.output else args.artifacts.resolve() / "independent_verification_v0_2_1.json"
    if output.exists():
        raise FileExistsError(f"verification receipt is write-once: {output}")
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
