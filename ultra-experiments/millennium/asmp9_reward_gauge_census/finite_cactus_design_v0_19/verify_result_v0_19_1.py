"""Independent exact replay for the v0.19.1 cached successor."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Sequence

from verify_result import (
    allocation,
    all_edge_optimum,
    all_greedy_endpoints,
    bellman,
    bouquet,
    cycle_value,
    exact_totals,
    global_totals,
    live,
    parse_result_fraction,
    prod,
    sha256,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def json_hash(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def live_states(
    lengths: Sequence[int], bridges: int
) -> tuple[tuple[str, ...], ...]:
    edges, blocks, _ = bouquet(lengths, bridges)
    return tuple(
        statuses
        for statuses in product(("Z", "I", "F"), repeat=len(edges))
        if live(edges, blocks, statuses)
    )


def integer_law(
    n: int, epsilon: Fraction, label: int
) -> tuple[dict[str, int], int]:
    denominator_base = epsilon.denominator
    low = epsilon.numerator
    high = denominator_base - low
    p_value = low if label == 0 else high
    q_value = denominator_base - p_value
    denominator = denominator_base**n
    zero = q_value**n
    full = p_value**n
    return {
        "Z": zero,
        "I": denominator - zero - full,
        "F": full,
    }, denominator


def cached_direct(
    lengths: Sequence[int],
    bridges: int,
    statuses: Sequence[Sequence[str]],
    counts: Sequence[int],
    epsilon: Fraction,
    labels: Sequence[int],
) -> Fraction:
    laws = [
        integer_law(n, epsilon, label)
        for n, label in zip(counts, labels, strict=True)
    ]
    denominator = prod(
        Fraction(edge_denominator)
        for _, edge_denominator in laws
    )
    numerator = 0
    for row in statuses:
        term = 1
        for index, status in enumerate(row):
            term *= laws[index][0][status]
        numerator += term
    return Fraction(numerator, denominator.numerator)


def factorized(
    lengths: Sequence[int],
    bridges: int,
    counts: Sequence[int],
    epsilon: Fraction,
    labels: Sequence[int],
) -> Fraction:
    _, blocks, _ = bouquet(lengths, bridges)
    return prod(
        cycle_value(
            tuple(counts[index] for index in block),
            epsilon,
            tuple(labels[index] for index in block),
        )
        for block in blocks
    )


def factor_rows(raw: dict[str, Any]) -> list[dict[str, Any]]:
    lengths = tuple(raw["cycle_lengths"])
    bridges = int(raw["bridge_count"])
    counts = tuple(raw["counts"])
    epsilon = Fraction(raw["epsilon"])
    statuses = live_states(lengths, bridges)
    rows = []
    for labels in product(
        (0, 1), repeat=sum(lengths) + bridges
    ):
        direct = cached_direct(
            lengths, bridges, statuses, counts, epsilon, labels
        )
        factored = factorized(
            lengths, bridges, counts, epsilon, labels
        )
        rows.append(
            {
                "labels": "".join(str(value) for value in labels),
                "direct": f"{direct.numerator}/{direct.denominator}",
                "factorized": (
                    f"{factored.numerator}/{factored.denominator}"
                ),
            }
        )
    return rows


def bridge_rows(raw: dict[str, Any]) -> list[dict[str, Any]]:
    lengths = tuple(raw["cycle_lengths"])
    bridges = int(raw["bridge_count"])
    epsilon = Fraction(raw["epsilon"])
    statuses = live_states(lengths, bridges)
    rows = []
    for labels in raw["label_vectors"]:
        first = cached_direct(
            lengths,
            bridges,
            statuses,
            raw["counts_a"],
            epsilon,
            labels,
        )
        second = cached_direct(
            lengths,
            bridges,
            statuses,
            raw["counts_b"],
            epsilon,
            labels,
        )
        factored = factorized(
            lengths, bridges, raw["counts_a"], epsilon, labels
        )
        rows.append(
            {
                "labels": "".join(str(value) for value in labels),
                "direct_a": f"{first.numerator}/{first.denominator}",
                "direct_b": f"{second.numerator}/{second.denominator}",
                "factorized": (
                    f"{factored.numerator}/{factored.denominator}"
                ),
                "all_equal": first == second == factored,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol",
        type=Path,
        default=HERE / "protocol_v0_19_1.json",
    )
    parser.add_argument(
        "--registration",
        type=Path,
        default=HERE / "registration_v0_19_1.json",
    )
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    registration = json.loads(
        args.registration.read_text(encoding="utf-8")
    )
    result = json.loads(args.result.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {
        "protocol_hash": (
            result["protocol_sha256"] == sha256(args.protocol)
        ),
        "registration_hash": (
            result["registration_sha256"] == sha256(args.registration)
        ),
        "sealed_files": all(
            (REPO / relative).is_file()
            and sha256(REPO / relative) == expected
            for relative, expected in registration["sealed_files"].items()
        ),
    }

    old_protocol = json.loads(
        (HERE / "protocol_v0_19.json").read_text(encoding="utf-8")
    )
    old_result = json.loads(
        (HERE / "artifacts_v0_19/result_v0_19.json").read_text(
            encoding="utf-8"
        )
    )
    old_rows = factor_rows(
        old_protocol["factorization_cells"]["fresh_figure_3_4"]
    )
    checks["burned_cache_regression"] = (
        json_hash(old_rows)
        == old_result["factorization"]["row_sha256"]
        == result["cache_regression"]["factorization_row_sha256"]
    )

    raw_factor = protocol["factorization_cells"][
        "fresh_19_1_figure_4_4"
    ]
    fresh_rows = factor_rows(raw_factor)
    checks["fresh_factorization"] = (
        all(row["direct"] == row["factorized"] for row in fresh_rows)
        and json_hash(fresh_rows)
        == result["factorization"]["row_sha256"]
    )
    raw_bridge = protocol["factorization_cells"][
        "fresh_19_1_figure_3_6_bridge"
    ]
    fresh_bridge = bridge_rows(raw_bridge)
    checks["fresh_bridge"] = (
        all(row["all_equal"] for row in fresh_bridge)
        and result["bridge"]["pass"]
    )

    reported_dp = {row["name"]: row for row in result["dp_cells"]}
    dp_ok = True
    for name, raw in protocol["dp_cells"].items():
        lengths = tuple(raw["cycle_lengths"])
        epsilon = Fraction(raw["epsilon"])
        dynamic = bellman(
            lengths,
            raw["total_budget"],
            raw["bridge_count"],
            epsilon,
        )
        exhaustive = exact_totals(
            lengths,
            raw["total_budget"],
            raw["bridge_count"],
            epsilon,
        )
        reported = reported_dp[name]
        dp_ok &= (
            dynamic == exhaustive
            and parse_result_fraction(reported["dynamic"]["value"])
            == dynamic[0]
            and tuple(
                tuple(value)
                for value in reported["dynamic"]["cycle_totals"]
            )
            == dynamic[1]
        )
    checks["dp_cells"] = dp_ok

    direct = all_edge_optimum(protocol["global_edge_census"])
    raw_global = protocol["global_edge_census"]
    dynamic = bellman(
        tuple(raw_global["cycle_lengths"]),
        raw_global["total_budget"],
        raw_global["bridge_count"],
        Fraction(raw_global["epsilon"]),
    )
    checks["all_edge"] = (
        direct[0] == dynamic[0]
        and direct[2] == set(dynamic[1])
        and direct[3]
        and direct[4]
        and parse_result_fraction(
            result["all_edge_census"]["direct_value"]
        )
        == direct[0]
    )

    greedy_lengths = (3, 3)
    greedy_epsilon = Fraction(1, 4)
    greedy_endpoints = all_greedy_endpoints(
        greedy_lengths, 10, greedy_epsilon
    )
    greedy_optimum = bellman(greedy_lengths, 10, 0, greedy_epsilon)
    greedy_value = max(
        allocation(greedy_lengths, totals, greedy_epsilon)
        for totals in greedy_endpoints
    )
    uniform_lengths = (3, 4)
    uniform_epsilon = Fraction(1, 10)
    balanced_totals = global_totals(uniform_lengths, 12)
    uniform_optimum = bellman(uniform_lengths, 12, 0, uniform_epsilon)
    balanced_value = max(
        allocation(uniform_lengths, totals, uniform_epsilon)
        for totals in balanced_totals
    )
    checks["regressions"] = (
        greedy_optimum[0] - greedy_value
        == Fraction(45, 262144)
        and uniform_optimum[0] - balanced_value
        == Fraction(26235981, 125000000000)
    )

    comparator_ok = True
    reported_comparators = {
        row["name"]: row for row in result["comparators"]
    }
    for name, raw in protocol["comparator_cells"].items():
        lengths = tuple(raw["cycle_lengths"])
        epsilon = Fraction(raw["epsilon"])
        dynamic = bellman(
            lengths,
            raw["total_budget"],
            raw["bridge_count"],
            epsilon,
        )
        exhaustive = exact_totals(
            lengths,
            raw["total_budget"],
            raw["bridge_count"],
            epsilon,
        )
        reported = reported_comparators[name]
        comparator_ok &= (
            dynamic == exhaustive
            and parse_result_fraction(reported["dynamic"]["value"])
            == dynamic[0]
        )
    checks["comparators"] = comparator_ok
    expected_verdict = (
        "finite_budget_cactus_dp_established_in_frozen_model_v0_19_1"
        if all(result["gates"].values())
        else "finite_budget_cactus_dp_not_established_v0_19_1"
    )
    checks["registered_gate_logic"] = (
        tuple(result["gates"]) == tuple(protocol["gate_ids"])
        and result["verdict"] == expected_verdict
    )
    verification = {
        "verification_id": (
            "ASMP-9-FINITE-CACTUS-DESIGN-v0.19.1-independent"
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
