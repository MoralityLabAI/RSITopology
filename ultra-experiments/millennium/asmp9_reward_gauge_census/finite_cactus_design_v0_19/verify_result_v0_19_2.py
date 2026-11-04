from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from finite_cactus_design import (
    allocation_value,
    balanced_allocation,
    bounded_compositions,
    globally_balanced_cycle_totals,
    marginal_greedy_endpoints,
    optimize_all_edges_exhaustive,
    optimize_cactus_dp,
    product_fraction,
    cycle_worst_direct,
    bouquet_cactus,
)
from run_verification import regression_certificates
from run_verification_v0_19_1 import (
    cached_bridge_record,
    cached_factorization_record,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_exhaustive(
    lengths: tuple[int, ...],
    total_budget: int,
    bridge_count: int,
    epsilon: Fraction,
) -> tuple[Fraction, tuple[tuple[int, ...], ...], int]:
    budget = total_budget - bridge_count
    cache: dict[tuple[int, int], Fraction] = {}

    def one_cycle(length: int, total: int) -> Fraction:
        key = (length, total)
        if key not in cache:
            counts = balanced_allocation(total, length)
            cache[key] = cycle_worst_direct(counts, epsilon)[0]
        return cache[key]

    rows = [
        (
            product_fraction(
                one_cycle(length, total)
                for length, total in zip(lengths, totals, strict=True)
            ),
            totals,
        )
        for totals in bounded_compositions(budget, lengths)
    ]
    maximum = max(value for value, _ in rows)
    optimizers = tuple(
        totals for value, totals in rows if value == maximum
    )
    return maximum, optimizers, len(cache)


def result_fraction(raw: dict[str, Any]) -> Fraction:
    return Fraction(raw["fraction"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol",
        type=Path,
        default=HERE / "protocol_v0_19_2.json",
    )
    parser.add_argument(
        "--registration",
        type=Path,
        default=HERE / "registration_v0_19_2.json",
    )
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    registration = json.loads(
        args.registration.read_text(encoding="utf-8")
    )
    result = json.loads(args.result.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    checks["sealed_files"] = all(
        (REPO / relative).is_file()
        and sha256(REPO / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )
    checks["protocol_hash"] = (
        sha256(args.protocol) == result["protocol_sha256"]
        and result["protocol_sha256"]
        == registration["sealed_files"][
            args.protocol.relative_to(REPO).as_posix()
        ]
    )
    checks["registration_hash"] = (
        sha256(args.registration) == result["registration_sha256"]
    )

    burned_protocol = json.loads(
        (
            HERE
            / protocol["burned_cache_regression"]["protocol_path"]
        ).read_text(encoding="utf-8")
    )
    burned_result = json.loads(
        (
            HERE / protocol["burned_cache_regression"]["result_path"]
        ).read_text(encoding="utf-8")
    )
    burned_reported = {
        row["name"]: row for row in burned_result["dp_cells"]
    }
    burned_ok = True
    for name, raw in burned_protocol["dp_cells"].items():
        value, optimizers, _ = independent_exhaustive(
            tuple(raw["cycle_lengths"]),
            int(raw["total_budget"]),
            int(raw["bridge_count"]),
            Fraction(raw["epsilon"]),
        )
        expected = burned_reported[name]["dynamic"]
        burned_ok &= (
            value == result_fraction(expected["value"])
            and optimizers
            == tuple(tuple(item) for item in expected["cycle_totals"])
        )
    checks["burned_cycle_cache_regression"] = burned_ok

    factor_name, factor_raw = next(
        (
            (name, raw)
            for name, raw in protocol["factorization_cells"].items()
            if "counts" in raw
        )
    )
    factor = cached_factorization_record(factor_name, factor_raw)
    checks["fresh_factorization"] = (
        factor["mismatch_count"] == 0
        and factor["row_sha256"] == result["factorization"]["row_sha256"]
    )
    bridge_name, bridge_raw = next(
        (
            (name, raw)
            for name, raw in protocol["factorization_cells"].items()
            if "counts_a" in raw
        )
    )
    bridge = cached_bridge_record(bridge_name, bridge_raw)
    checks["fresh_bridge"] = bridge["pass"] and (
        bridge["rows"] == result["bridge"]["rows"]
    )

    dp_reported = {row["name"]: row for row in result["dp_cells"]}
    dp_ok = True
    for name, raw in protocol["dp_cells"].items():
        lengths = tuple(raw["cycle_lengths"])
        epsilon = Fraction(raw["epsilon"])
        dynamic = optimize_cactus_dp(
            lengths,
            int(raw["total_budget"]),
            epsilon,
            int(raw["bridge_count"]),
        )
        value, optimizers, local_count = independent_exhaustive(
            lengths,
            int(raw["total_budget"]),
            int(raw["bridge_count"]),
            epsilon,
        )
        row = dp_reported[name]
        dp_ok &= (
            dynamic.value == value
            and dynamic.cycle_totals == optimizers
            and result_fraction(row["dynamic"]["value"]) == value
            and tuple(
                tuple(item)
                for item in row["dynamic"]["cycle_totals"]
            )
            == optimizers
            and row["independent_exhaustive"][
                "independent_cycle_values_evaluated"
            ]
            == local_count
        )
    checks["dp_cells"] = dp_ok

    raw = protocol["global_edge_census"]
    graph = bouquet_cactus(
        tuple(raw["cycle_lengths"]), int(raw["bridge_count"])
    )
    direct_value, direct_optimizers = optimize_all_edges_exhaustive(
        graph, int(raw["total_budget"]), Fraction(raw["epsilon"])
    )
    dynamic = optimize_cactus_dp(
        tuple(raw["cycle_lengths"]),
        int(raw["total_budget"]),
        Fraction(raw["epsilon"]),
        int(raw["bridge_count"]),
    )
    induced = {
        tuple(
            sum(counts[index] for index in block)
            for block in graph.cycle_blocks
        )
        for counts in direct_optimizers
    }
    checks["all_edge"] = (
        direct_value == dynamic.value
        and induced == set(dynamic.cycle_totals)
        and result_fraction(
            result["all_edge_census"]["direct_value"]
        )
        == direct_value
        and all(
            all(counts[index] == 1 for index in graph.bridge_indices)
            for counts in direct_optimizers
        )
    )

    regressions = regression_certificates()
    checks["regressions"] = (
        regressions["greedy"]["pass"]
        and regressions["finite_uniform"]["pass"]
        and result["regression_certificates"] == regressions
    )

    comparator_reported = {
        row["name"]: row for row in result["comparators"]
    }
    comparators_ok = True
    for name, raw in protocol["comparator_cells"].items():
        lengths = tuple(raw["cycle_lengths"])
        epsilon = Fraction(raw["epsilon"])
        total = int(raw["total_budget"])
        dynamic = optimize_cactus_dp(lengths, total, epsilon)
        value, optimizers, _ = independent_exhaustive(
            lengths, total, 0, epsilon
        )
        greedy_value = max(
            allocation_value(lengths, totals, epsilon)
            for totals in marginal_greedy_endpoints(
                lengths, total, epsilon
            )
        )
        global_value = max(
            allocation_value(lengths, totals, epsilon)
            for totals in globally_balanced_cycle_totals(lengths, total)
        )
        row = comparator_reported[name]
        comparators_ok &= (
            dynamic.value == value
            and dynamic.cycle_totals == optimizers
            and result_fraction(row["greedy_gap"])
            == dynamic.value - greedy_value
            and result_fraction(row["globally_balanced_gap"])
            == dynamic.value - global_value
        )
    checks["comparators"] = comparators_ok

    expected_verdict = (
        "finite_budget_cactus_dp_established_in_frozen_model_v0_19_2"
        if all(result["gates"].values())
        else "finite_budget_cactus_dp_not_established_v0_19_2"
    )
    checks["registered_gate_logic"] = (
        tuple(result["gates"]) == tuple(protocol["gate_ids"])
        and result["verdict"] == expected_verdict
    )

    verification = {
        "verification_id": (
            "ASMP-9-FINITE-CACTUS-DESIGN-v0.19.2-independent"
        ),
        "protocol_sha256": sha256(args.protocol),
        "registration_sha256": sha256(args.registration),
        "result_sha256": sha256(args.result),
        "checks": checks,
        "check_count": len(checks),
        "pass": all(checks.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(verification, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(verification, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
