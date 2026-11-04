from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations
from math import factorial
from pathlib import Path


N = 9
P = Fraction(1, 5)
LIMIT = Fraction(1, 20)

ORDER_THREE_WITNESS = {
    0: Fraction(136, 625),
    2: Fraction(84, 125),
    3: Fraction(6, 125),
    5: Fraction(39, 625),
}
ORDER_FOUR_WITNESS = {
    0: Fraction(404, 3125),
    1: Fraction(207, 625),
    2: Fraction(144, 625),
    3: Fraction(168, 625),
    5: Fraction(126, 3125),
}


def falling(value: int, order: int) -> Fraction:
    result = 1
    for offset in range(order):
        result *= value - offset
    return Fraction(result)


def reference_moment(order: int) -> Fraction:
    return Fraction(factorial(N), factorial(N - order)) * P**order


def tail(law: dict[int, Fraction]) -> Fraction:
    return sum((weight for count, weight in law.items() if count >= 5), Fraction(0))


def validate_law(law: dict[int, Fraction], order: int) -> None:
    if any(count < 0 or count > N for count in law):
        raise ValueError("count outside support")
    if any(weight < 0 for weight in law.values()):
        raise ValueError("negative probability")
    if sum(law.values(), Fraction(0)) != 1:
        raise ValueError("normalization mismatch")
    for degree in range(1, order + 1):
        observed = sum(
            (falling(count, degree) * weight for count, weight in law.items()),
            Fraction(0),
        )
        if observed != reference_moment(degree):
            raise ValueError(f"moment {degree} mismatch")


def solve_square(matrix: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction] | None:
    size = len(rhs)
    augmented = [row[:] + [value] for row, value in zip(matrix, rhs)]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if augmented[row][column] != 0),
            None,
        )
        if pivot is None:
            return None
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            scale = augmented[row][column]
            if scale:
                augmented[row] = [
                    value - scale * pivot_value
                    for value, pivot_value in zip(augmented[row], augmented[column])
                ]
    return [augmented[row][-1] for row in range(size)]


def solve_support(support: tuple[int, ...], order: int) -> dict[int, Fraction] | None:
    matrix = [
        [falling(count, degree) for count in support]
        for degree in range(order + 1)
    ]
    rhs = [Fraction(1)] + [reference_moment(degree) for degree in range(1, order + 1)]
    weights = solve_square(matrix, rhs)
    if weights is None or any(weight < 0 for weight in weights):
        return None
    return {count: weight for count, weight in zip(support, weights) if weight}


def exact_upper_envelope(order: int) -> tuple[Fraction, dict[int, Fraction]]:
    best_value = Fraction(-1)
    best_law: dict[int, Fraction] | None = None
    for support in combinations(range(N + 1), order + 1):
        law = solve_support(support, order)
        if law is None:
            continue
        value = tail(law)
        if value > best_value:
            best_value = value
            best_law = law
    if best_law is None:
        raise RuntimeError(f"no feasible vertex at order {order}")
    validate_law(best_law, order)
    return best_value, best_law


def order_four_dual(count: int) -> Fraction:
    return falling(count, 4) / 120


def order_three_dual(count: int) -> Fraction:
    return (
        Fraction(count, 15)
        - falling(count, 2) / 15
        + falling(count, 3) / 30
    )


def fraction_record(value: Fraction) -> dict[str, object]:
    return {"exact": str(value), "decimal": float(value)}


def law_record(law: dict[int, Fraction]) -> dict[str, str]:
    return {str(count): str(weight) for count, weight in sorted(law.items())}


def build_result() -> dict[str, object]:
    envelope = []
    for order in range(1, N + 1):
        maximum, witness = exact_upper_envelope(order)
        envelope.append(
            {
                "order": order,
                "sharp_upper": fraction_record(maximum),
                "passes_5_percent": maximum <= LIMIT,
                "vertex_witness": law_record(witness),
            }
        )

    validate_law(ORDER_THREE_WITNESS, 3)
    validate_law(ORDER_FOUR_WITNESS, 4)
    order_three_dual_valid = all(
        order_three_dual(count) >= (1 if count >= 5 else 0)
        for count in range(N + 1)
    )
    order_three_dual_expectation = (
        reference_moment(1) / 15
        - reference_moment(2) / 15
        + reference_moment(3) / 30
    )
    dual_valid = all(
        order_four_dual(count) >= (1 if count >= 5 else 0)
        for count in range(N + 1)
    )
    dual_expectation = reference_moment(4) / 120
    order_three_tail = tail(ORDER_THREE_WITNESS)
    order_four_tail = tail(ORDER_FOUR_WITNESS)
    minimum_order = next(
        row["order"] for row in envelope if row["passes_5_percent"]
    )
    certified = (
        order_three_tail == Fraction(39, 625)
        and order_three_tail > LIMIT
        and order_three_dual_valid
        and order_three_dual_expectation == order_three_tail
        and dual_valid
        and dual_expectation == Fraction(126, 3125)
        and order_four_tail == dual_expectation
        and envelope[2]["sharp_upper"]["exact"] == "39/625"
        and envelope[3]["sharp_upper"]["exact"] == "126/3125"
        and minimum_order == 4
    )
    return {
        "experiment_id": "ASMP-3-MINIMUM-CERTIFYING-MOMENT-ORDER-v0.1.3",
        "status": "post_result_exact_characterization",
        "certified": certified,
        "reference": {
            "panel_size": N,
            "independent_error": str(P),
            "majority_failure_threshold": 5,
            "admissible_error": str(LIMIT),
            "moment_basis": "falling factorial",
        },
        "minimum_certifying_order": minimum_order,
        "order_three_counterexample": {
            "law": law_record(ORDER_THREE_WITNESS),
            "tail": fraction_record(order_three_tail),
            "dual": "1{S>=5} <= S/15-(S)_2/15+(S)_3/30",
            "dual_valid_on_counts_0_to_9": order_three_dual_valid,
            "dual_expectation": fraction_record(order_three_dual_expectation),
        },
        "order_four_certificate": {
            "dual": "1{S>=5} <= (S)_4/120",
            "dual_valid_on_counts_0_to_9": dual_valid,
            "sharp_law": law_record(ORDER_FOUR_WITNESS),
            "sharp_tail": fraction_record(order_four_tail),
        },
        "upper_envelope_by_order": envelope,
        "claim_boundary": (
            "Exact specialization of the classical discrete moment problem for "
            "the independent Binomial(9,1/5) reference moments; not a general "
            "moment-order theorem or an empirical verifier result."
        ),
    }


def main() -> None:
    result = build_result()
    if not result["certified"]:
        raise RuntimeError("moment-order characterization failed")
    output = Path(__file__).resolve().parent / "moment_order_v0_1_3.json"
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
