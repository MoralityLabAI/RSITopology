from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Iterable


N = 9
MEAN = Fraction(9, 5)
LIMIT = Fraction(1, 20)
LOWER_BREAK = Fraction(7, 32)
UNIVERSAL_FAIL_BOUNDARY = Fraction(53, 128)
AUDIT_GRID = (
    Fraction(0),
    Fraction(1, 20),
    Fraction(1, 10),
    LOWER_BREAK,
    Fraction(1, 3),
    UNIVERSAL_FAIL_BOUNDARY,
    Fraction(1, 2),
    Fraction(1),
)


def second_factorial_moment(rho: Fraction) -> Fraction:
    return Fraction(72, 25) + Fraction(288, 25) * rho


def tail(law: dict[int, Fraction]) -> Fraction:
    return sum((weight for s, weight in law.items() if s >= 5), Fraction(0))


def validate_law(law: dict[int, Fraction], rho: Fraction) -> None:
    if any(s < 0 or s > N for s in law):
        raise ValueError("support outside {0,...,9}")
    if any(weight < 0 for weight in law.values()):
        raise ValueError("negative probability")
    if sum(law.values(), Fraction(0)) != 1:
        raise ValueError("probabilities do not sum to one")
    if sum((s * weight for s, weight in law.items()), Fraction(0)) != MEAN:
        raise ValueError("mean mismatch")
    if sum((s * (s - 1) * weight for s, weight in law.items()), Fraction(0)) != second_factorial_moment(rho):
        raise ValueError("second factorial moment mismatch")


def mix(left: dict[int, Fraction], right: dict[int, Fraction], weight_right: Fraction) -> dict[int, Fraction]:
    keys = set(left) | set(right)
    return {
        s: (1 - weight_right) * left.get(s, Fraction(0))
        + weight_right * right.get(s, Fraction(0))
        for s in keys
        if (1 - weight_right) * left.get(s, Fraction(0))
        + weight_right * right.get(s, Fraction(0))
        != 0
    }


RHO_ZERO_MIN = {0: Fraction(4, 25), 1: Fraction(9, 25), 3: Fraction(12, 25)}
LOWER_BREAK_LAW = {0: Fraction(11, 20), 4: Fraction(9, 20)}
RHO_ZERO_FAIL = {1: Fraction(13, 25), 2: Fraction(28, 75), 5: Fraction(8, 75)}
COMMON_SHOCK = {0: Fraction(4, 5), 9: Fraction(1, 5)}


def minimum_tail_value(rho: Fraction) -> Fraction:
    if not 0 <= rho <= 1:
        raise ValueError("rho outside [0,1]")
    if rho <= LOWER_BREAK:
        return Fraction(0)
    return (32 * rho - 7) / 125


def minimum_witness(rho: Fraction) -> dict[int, Fraction]:
    if rho <= LOWER_BREAK:
        return mix(RHO_ZERO_MIN, LOWER_BREAK_LAW, rho / LOWER_BREAK)
    weight_9 = (32 * rho - 7) / 125
    weight_4 = (MEAN - 9 * weight_9) / 4
    return {s: w for s, w in {0: 1 - weight_4 - weight_9, 4: weight_4, 9: weight_9}.items() if w}


def everywhere_failing_witness(rho: Fraction) -> dict[int, Fraction]:
    return mix(RHO_ZERO_FAIL, COMMON_SHOCK, rho)


def everywhere_failing_tail(rho: Fraction) -> Fraction:
    return Fraction(8, 75) + Fraction(7, 75) * rho


def lower_dual(s: int) -> Fraction:
    return Fraction(s * (s - 1) - 3 * s, 45)


def rho_zero_upper_dual(s: int) -> Fraction:
    return Fraction(1, 6) - Fraction(s, 6) + Fraction(s * (s - 1), 12)


def determinant_3(matrix: tuple[tuple[Fraction, ...], ...]) -> Fraction:
    a = matrix
    return (
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    )


def solve_support(support: tuple[int, int, int], rho: Fraction) -> tuple[Fraction, ...] | None:
    matrix = (
        (Fraction(1), Fraction(1), Fraction(1)),
        tuple(Fraction(s) for s in support),
        tuple(Fraction(s * (s - 1)) for s in support),
    )
    rhs = (Fraction(1), MEAN, second_factorial_moment(rho))
    denominator = determinant_3(matrix)
    if denominator == 0:
        return None
    weights = []
    for column in range(3):
        replaced = [list(row) for row in matrix]
        for row in range(3):
            replaced[row][column] = rhs[row]
        weights.append(determinant_3(tuple(tuple(row) for row in replaced)) / denominator)
    return tuple(weights)


def exact_vertex_envelope(rho: Fraction) -> tuple[Fraction, Fraction]:
    values: list[Fraction] = []
    for support in combinations(range(N + 1), 3):
        weights = solve_support(support, rho)
        if weights is None or any(weight < 0 for weight in weights):
            continue
        values.append(sum((weight for s, weight in zip(support, weights) if s >= 5), Fraction(0)))
    if not values:
        raise RuntimeError("no feasible LP vertices")
    return min(values), max(values)


def fraction_record(value: Fraction) -> dict[str, object]:
    return {"exact": str(value), "decimal": float(value)}


def build_result() -> dict[str, object]:
    lower_dual_valid = all(lower_dual(s) <= (1 if s >= 5 else 0) for s in range(N + 1))
    upper_dual_valid = all(rho_zero_upper_dual(s) >= (1 if s >= 5 else 0) for s in range(N + 1))

    audit = []
    for rho in AUDIT_GRID:
        minimum = minimum_witness(rho)
        failing = everywhere_failing_witness(rho)
        validate_law(minimum, rho)
        validate_law(failing, rho)
        vertex_min, vertex_max = exact_vertex_envelope(rho)
        assert tail(minimum) == minimum_tail_value(rho) == vertex_min
        assert tail(failing) == everywhere_failing_tail(rho)
        assert vertex_max >= tail(failing) > LIMIT
        audit.append(
            {
                "rho": str(rho),
                "sharp_minimum": fraction_record(vertex_min),
                "sharp_maximum": fraction_record(vertex_max),
                "failing_witness_tail": fraction_record(tail(failing)),
            }
        )

    boundary_minimum = minimum_tail_value(UNIVERSAL_FAIL_BOUNDARY)
    certified = (
        lower_dual_valid
        and upper_dual_valid
        and boundary_minimum == LIMIT
        and tail(RHO_ZERO_FAIL) == Fraction(8, 75)
        and all(everywhere_failing_tail(rho) > LIMIT for rho in AUDIT_GRID)
    )
    return {
        "experiment_id": "ASMP-3-EXCHANGEABLE-TWO-MOMENT-CLASSIFICATION-v0.1.2",
        "status": "post_result_exact_characterization",
        "certified": certified,
        "lower_envelope": {
            "rho_0_to_7_over_32": "0",
            "rho_7_over_32_to_1": "(32*rho-7)/125",
            "dual_valid_on_all_counts": lower_dual_valid,
        },
        "rho_zero_upper": {
            "sharp_value": fraction_record(Fraction(8, 75)),
            "dual": "1/6-s/6+s(s-1)/12",
            "dual_valid_on_all_counts": upper_dual_valid,
        },
        "everywhere_failing_family": {
            "tail": "8/75+7*rho/75",
            "construction": "(1-rho)*law_{1,2,5}+rho*law_{0,9}",
        },
        "classification": {
            "universally_pass": "empty",
            "underdetermined": "0 <= rho <= 53/128",
            "universally_fail": "53/128 < rho <= 1",
            "boundary": fraction_record(UNIVERSAL_FAIL_BOUNDARY),
        },
        "audit_grid": audit,
        "claim_boundary": (
            "Exact specialization of the classical two-binomial-moment problem "
            "for nine exchangeable Bernoulli errors; not a novel probability inequality "
            "or an empirical verifier claim."
        ),
    }


def main() -> None:
    result = build_result()
    if not result["certified"]:
        raise RuntimeError("moment-envelope characterization failed")
    output = Path(__file__).resolve().parent / "moment_envelope_v0_1_2.json"
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
