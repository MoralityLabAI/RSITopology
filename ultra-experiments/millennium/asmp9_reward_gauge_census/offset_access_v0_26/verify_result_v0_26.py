from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def record_fraction(record: dict[str, int]) -> Fraction:
    return Fraction(record["numerator"], record["denominator"])


def ceil_log2(value: Fraction) -> int:
    if value <= 1:
        return 0
    exponent, power = 0, Fraction(1)
    while power < value:
        power *= 2
        exponent += 1
    return exponent


def independent_bisection(
    gap: Fraction, radius: Fraction, tolerance: Fraction
) -> tuple[Fraction, int]:
    lower, upper = -radius, radius
    rounds = ceil_log2(radius / tolerance)
    used = 0
    for _ in range(rounds):
        midpoint = (lower + upper) / 2
        used += 1
        if gap == midpoint:
            lower = upper = midpoint
            break
        if gap > midpoint:
            lower = midpoint
        else:
            upper = midpoint
    return abs((lower + upper) / 2 - gap), used


def rational_link(value: Fraction) -> Fraction:
    if value < 0:
        return 1 - rational_link(-value)
    return Fraction(1, 2) + value / (2 * (1 + value))


def independent_robust_max_error(
    radius: Fraction, tolerance: Fraction, denominator: int
) -> tuple[Fraction, int]:
    rounds = ceil_log2(radius / tolerance)
    kappa = Fraction(1, 2 * (1 + 2 * radius))
    bound = kappa * tolerance / 2
    maximum = Fraction(0)
    checked = 0
    limit = int(radius * denominator)
    for numerator in range(-limit, limit + 1):
        gap = Fraction(numerator, denominator)
        for errors in itertools.product(
            (-bound, Fraction(0), bound), repeat=rounds
        ):
            lower, upper = -radius, radius
            for error in errors:
                midpoint = (lower + upper) / 2
                estimate = rational_link(gap - midpoint) + error
                if estimate > Fraction(1, 2) + bound:
                    lower = midpoint
                elif estimate < Fraction(1, 2) - bound:
                    upper = midpoint
                else:
                    lower = upper = midpoint
                    break
            maximum = max(maximum, abs((lower + upper) / 2 - gap))
            checked += 1
    return maximum, checked


def independent_sample_repeats(cell: dict[str, Any]) -> tuple[int, int, float]:
    radius = Fraction(str(cell["radius"]))
    tolerance = Fraction(str(cell["tolerance"]))
    rounds = ceil_log2(radius / tolerance)
    query_count = int(cell["dimension"]) * rounds
    error = (
        float(cell["kappa"])
        * float(cell["tolerance"]) ** float(cell["exponent"])
        / 2
    )
    repeats = math.ceil(
        math.log(2 * query_count / float(cell["failure_probability"]))
        / (2 * error**2)
    )
    failure_bound = 2 * query_count * math.exp(-2 * repeats * error**2)
    return query_count, repeats, failure_bound


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    registration = json.loads(args.registration.read_text(encoding="utf-8"))
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    result = json.loads(args.result.read_text(encoding="utf-8"))
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    fresh = protocol["fresh_validation"]
    checks: dict[str, bool] = {}

    checks["registration_hash"] = (
        sha256(args.registration)
        == result["registration_sha256"]
        == receipt["registration_sha256"]
    )
    checks["result_hash"] = sha256(args.result) == receipt["result_sha256"]
    checks["protocol_hash"] = (
        sha256(REPO / registration["protocol_path"])
        == receipt["protocol_sha256"]
    )
    checks["sealed_files"] = all(
        sha256(REPO / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )

    population_by_name = {
        row["name"]: row for row in result["population_rows"]
    }
    population_ok = True
    for cell in fresh["population_cells"]:
        radius = Fraction(cell["radius"])
        tolerance = Fraction(cell["tolerance"])
        denominator = int(cell["denominator"])
        limit = int(radius * denominator)
        maximum_error = Fraction(0)
        maximum_queries = 0
        for numerator in range(-limit, limit + 1):
            error, used = independent_bisection(
                Fraction(numerator, denominator), radius, tolerance
            )
            maximum_error = max(maximum_error, error)
            maximum_queries = max(maximum_queries, used)
        row = population_by_name[cell["name"]]
        population_ok &= (
            row["checked_gap_count"] == 2 * limit + 1
            and record_fraction(row["maximum_absolute_error"])
            == maximum_error
            and row["maximum_query_count"] == maximum_queries
            and row["registered_query_bound"]
            == ceil_log2(radius / tolerance)
            and row["pass"]
        )
    checks["population_rows"] = population_ok

    dyadic_by_name = {row["name"]: row for row in result["dyadic_rows"]}
    dyadic_ok = True
    for cell in fresh["dyadic_cells"]:
        dimension = int(cell["dimension"])
        ratio = Fraction(cell["radius"]) / Fraction(cell["tolerance"])
        upper = dimension * ceil_log2(ratio)
        lower = ceil_log2(ratio**dimension)
        row = dyadic_by_name[cell["name"]]
        dyadic_ok &= (
            row["upper_bound"] == upper
            and row["lower_bound"] == lower
            and upper == lower
            and row["pass"]
        )
    checks["dyadic_bounds"] = dyadic_ok

    restricted_by_name = {
        row["name"]: row for row in result["restricted_rows"]
    }
    restricted_ok = True
    for cell in fresh["restricted_cells"]:
        radius = Fraction(cell["radius"])
        ceiling = Fraction(cell["maximum_offset"])
        first = (radius + ceiling) / 2
        second = radius
        minimax = (second - first) / 2
        row = restricted_by_name[cell["name"]]
        restricted_ok &= (
            record_fraction(row["first_gap"]) == first
            and record_fraction(row["second_gap"]) == second
            and record_fraction(row["minimax_error_lower_bound"]) == minimax
            and minimax > 0
            and row["pass"]
        )
    checks["restricted_witnesses"] = restricted_ok

    robust_by_name = {row["name"]: row for row in result["robust_rows"]}
    robust_ok = True
    for cell in fresh["robust_cells"]:
        maximum, checked = independent_robust_max_error(
            Fraction(cell["radius"]),
            Fraction(cell["tolerance"]),
            int(cell["gap_denominator"]),
        )
        row = robust_by_name[cell["name"]]
        robust_ok &= (
            record_fraction(row["maximum_absolute_error"]) == maximum
            and row["checked_paths"] == checked
            and maximum <= Fraction(cell["tolerance"])
            and row["pass"]
        )
    checks["robust_bounded_error_rows"] = robust_ok

    flat_cell = fresh["flat_link_cell"]
    radius = Fraction(flat_cell["radius"])
    deviations = [
        Fraction(1, 2**power) * radius
        / (1 + 2 * Fraction(1, 2**power) * radius)
        for power in range(
            int(flat_cell["minimum_power"]),
            int(flat_cell["maximum_power"]) + 1,
        )
    ]
    reported_deviations = [
        record_fraction(value) for value in result["flat_row"]["deviations"]
    ]
    checks["flat_link_sequence"] = (
        deviations == reported_deviations
        and all(left > right for left, right in zip(deviations, deviations[1:]))
        and deviations[-1] < Fraction(flat_cell["final_ceiling"])
        and result["flat_row"]["pass"]
    )

    checks["no_offset_control"] = (
        result["no_offset_row"]["same_population_law"]
        and result["no_offset_row"]["admissible_target_knots"]
        and not result["no_offset_row"]["positive_affine_equivalent"]
    )

    sample_by_name = {row["name"]: row for row in result["sample_rows"]}
    sample_ok = True
    for cell in fresh["sample_bound_cells"]:
        queries, repeats, failure = independent_sample_repeats(cell)
        row = sample_by_name[cell["name"]]
        sample_ok &= (
            row["population_query_count"] == queries
            and row["repeats_per_query"] == repeats
            and math.isclose(
                row["union_failure_bound"], failure, rel_tol=1e-15, abs_tol=0
            )
            and failure <= float(cell["failure_probability"])
            and row["pass"]
        )
    checks["sample_certificates"] = sample_ok

    checks["gate_universe"] = set(result["gate_passes"]) == set(
        protocol["gate_ids"]
    )
    checks["all_gates_pass"] = all(result["gate_passes"].values())
    checks["verdict"] = (
        result["verdict"] == protocol["verdict_map"]["all_gates_pass"]
    )
    checks["resource_caps"] = (
        receipt["wall_seconds"]
        <= protocol["resource_caps"]["wall_seconds"]
        and receipt["peak_resident_bytes"]
        <= protocol["resource_caps"]["peak_resident_bytes"]
    )
    checks["claim_boundary"] = (
        "ASMP-9 is resolved."
        in protocol["structured_claims"]["forbidden"]
        and "known reward-unit intervention" in protocol["claim_boundary"]
    )

    output = {
        "check_count": len(checks),
        "checks": checks,
        "pass": all(checks.values()),
        "receipt_sha256": sha256(args.receipt),
        "result_sha256": sha256(args.result),
        "verifier_sha256": sha256(Path(__file__)),
    }
    write_json_exclusive(args.output, output)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
