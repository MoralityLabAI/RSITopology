"""Primary exact computation for the prospectively frozen ASMP-9 v0.61 stack.

This module does not import the v0.57-v0.60 development implementations.
The orchestration layer verifies their hashes because they are the burned
objects whose proof handoffs are being checked.
"""

from __future__ import annotations

from collections import Counter
from decimal import Decimal, ROUND_CEILING, localcontext
from fractions import Fraction
import hashlib
from itertools import combinations, combinations_with_replacement, permutations
import json
from math import comb
from typing import Iterable, Iterator, Sequence


Q = Fraction


def fraction(text: str | int | Fraction) -> Fraction:
    if isinstance(text, Fraction):
        return text
    if isinstance(text, int):
        return Q(text)
    numerator, separator, denominator = str(text).partition("/")
    return Q(int(numerator), int(denominator)) if separator else Q(int(numerator))


def qtext(value: Fraction) -> str:
    value = Q(value)
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def decimal(value: Fraction | str | int) -> Decimal:
    value = fraction(value)
    return Decimal(value.numerator) / Decimal(value.denominator)


def atanh_decimal(value: Decimal) -> Decimal:
    return ((Decimal(1) + value).ln() - (Decimal(1) - value).ln()) / 2


def tanh_decimal(value: Decimal) -> Decimal:
    doubled = (2 * value).exp()
    return (doubled - 1) / (doubled + 1)


def canonical_digest(value) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def subsets(items: Sequence[int], maximum: int | None = None) -> Iterator[tuple[int, ...]]:
    items = tuple(sorted(items))
    stop = len(items) if maximum is None else min(maximum, len(items))
    for size in range(stop + 1):
        yield from combinations(items, size)


def menus(n: int, maximum: int | None = None) -> Iterator[tuple[int, ...]]:
    stop = n if maximum is None else min(maximum, n)
    for size in range(2, stop + 1):
        yield from combinations(range(n), size)


def interpolation_norm(context_size: int, degree: int) -> int:
    if context_size <= degree:
        return 1
    return sum(
        comb(context_size, u) * comb(context_size - u - 1, degree - u)
        for u in range(degree + 1)
    )


def maximum_interpolation_norm(n: int, degree: int) -> int:
    return max(interpolation_norm(size, degree) for size in range(n - 1))


def coordinate_count(n: int, degree: int) -> int:
    return sum(
        size * comb(n, size)
        for size in range(2, min(n, degree + 2) + 1)
    )


def score_exponent(menu: Iterable[int], item: int, active: frozenset[int]) -> int:
    return int(active.issubset(frozenset(menu) - {item}))


def pair_value(
    x: int,
    y: int,
    context: Iterable[int],
    active: frozenset[int],
) -> int:
    menu = frozenset(context) | {x, y}
    return score_exponent(menu, x, active) - score_exponent(menu, y, active)


def mobius_array(values: list[int], width: int) -> list[int]:
    coefficients = list(values)
    for bit in range(width):
        flag = 1 << bit
        for mask in range(1 << width):
            if mask & flag:
                coefficients[mask] -= coefficients[mask ^ flag]
    return coefficients


def deterministic_polynomial_target(n: int, degree: int, seed: int) -> tuple[int, int]:
    width = n - 2
    coefficients: dict[int, int] = {}
    for mask in range(1 << width):
        if mask.bit_count() <= degree:
            weighted = sum(
                (bit + 1) * (value + 3)
                for bit, value in enumerate(range(width))
                if mask & (1 << bit)
            )
            coefficients[mask] = (
                weighted + seed + 17 * n + 31 * degree + 13 * mask.bit_count()
            ) % 11 - 5

    values: dict[int, int] = {}
    for mask in range(1 << width):
        if mask.bit_count() > degree:
            continue
        values[mask] = sum(
            coefficient
            for term, coefficient in coefficients.items()
            if term & ~mask == 0
        )
    recovered_coefficients = mobius_array(
        [values.get(mask, 0) for mask in range(1 << width)],
        width,
    )
    # Only the lower-layer transform entries are used.  Entries obtained from
    # zero-filled unobserved values are intentionally discarded.
    reconstructed = sum(
        recovered_coefficients[mask]
        for mask in range(1 << width)
        if mask.bit_count() <= degree
    )
    target = sum(coefficients.values())
    return target, reconstructed


def run_v57(cells: dict) -> tuple[bool, list[dict], dict]:
    rows = []
    total_high_zero = 0
    total_agreement_coordinates = 0
    passed = True
    seed = int(cells["seed"])

    for cell in cells["v57_cells"]:
        n = int(cell["n"])
        degree = int(cell["r"])
        special = frozenset(int(x) for x in cell["special_menu"])
        special_item = int(cell["special_item"])
        active = special - {special_item}
        if (
            len(special) != degree + 2
            or special_item not in special
            or max(special) >= n
        ):
            passed = False

        agreement_coordinates = 0
        for menu in menus(n, degree + 1):
            exponents = [score_exponent(menu, item, active) for item in menu]
            passed &= not any(exponents)
            agreement_coordinates += len(menu)
        total_agreement_coordinates += agreement_coordinates

        base = degree + 2
        scores = {
            item: Q(base) ** score_exponent(special, item, active)
            for item in special
        }
        special_probability = scores[special_item] / sum(scores.values(), Q(0))
        passed &= special_probability == Q(degree + 2, 2 * degree + 3)
        passed &= special_probability > Q(1, 2)
        for other in special - {special_item}:
            binary = (special_item, other)
            binary_scores = [
                Q(base) ** score_exponent(binary, item, active)
                for item in binary
            ]
            passed &= binary_scores[0] / sum(binary_scores, Q(0)) == Q(1, 2)

        global_max_degree = -1
        high_zero = 0
        for x, y in combinations(range(n), 2):
            rest = tuple(value for value in range(n) if value not in (x, y))
            values = []
            for mask in range(1 << len(rest)):
                context = tuple(
                    rest[bit]
                    for bit in range(len(rest))
                    if mask & (1 << bit)
                )
                values.append(pair_value(x, y, context, active))
            coefficients = mobius_array(values, len(rest))
            for mask, coefficient in enumerate(coefficients):
                order = mask.bit_count()
                if order > degree:
                    high_zero += 1
                    passed &= coefficient == 0
                if coefficient:
                    global_max_degree = max(global_max_degree, order)
            reconstructed_full = sum(
                coefficient
                for mask, coefficient in enumerate(coefficients)
                if mask.bit_count() <= degree
            )
            passed &= reconstructed_full == values[-1]
        total_high_zero += high_zero
        passed &= global_max_degree == degree

        target, reconstructed = deterministic_polynomial_target(
            n,
            degree,
            seed,
        )
        passed &= target == reconstructed
        norm = maximum_interpolation_norm(n, degree)
        row = {
            "agreement_coordinates": agreement_coordinates,
            "high_degree_zero_checks": high_zero,
            "max_degree": global_max_degree,
            "n": n,
            "norm": norm,
            "r": degree,
            "special_probability": qtext(special_probability),
            "target_value": target,
        }
        rows.append({"kind": "v57", **row})

    return passed, rows, {
        "agreement_coordinates": total_agreement_coordinates,
        "cells": len(rows),
        "high_degree_zero_checks": total_high_zero,
    }


def ranking_choice(weights: Sequence[Fraction]) -> dict[tuple[tuple[str, ...], str], Fraction]:
    alternatives = ("a", "b", "c")
    rankings = tuple(permutations(alternatives))
    result = {}
    for size in (2, 3):
        for menu in combinations(alternatives, size):
            for choice in menu:
                result[(menu, choice)] = sum(
                    weight
                    for ranking, weight in zip(rankings, weights)
                    if next(x for x in ranking if x in menu) == choice
                )
    return result


def sample_cell_row(cell: dict) -> tuple[dict, bool]:
    n = int(cell["n"])
    degree = int(cell["r"])
    floor_value = fraction(cell["a"])
    gamma = fraction(cell["gamma"])
    delta = fraction(cell["delta"])
    condition = maximum_interpolation_norm(n, degree)
    coordinates = coordinate_count(n, degree)
    with localcontext() as context:
        context.prec = 90
        a_d = decimal(floor_value)
        gamma_d = decimal(gamma)
        delta_d = decimal(delta)
        tolerance = a_d * (
            Decimal(1)
            - (-atanh_decimal(gamma_d / 6) / Decimal(condition)).exp()
        )
        real_count = (
            (Decimal(2 * coordinates) / delta_d).ln()
            / (2 * tolerance * tolerance)
        )
        count = int(real_count.to_integral_value(rounding=ROUND_CEILING))
        union_bound = (
            Decimal(2 * coordinates)
            * (-2 * Decimal(count) * tolerance * tolerance).exp()
        )
        log_score_error = (
            -2
            * Decimal(condition)
            * (Decimal(1) - tolerance / a_d).ln()
        )
        l1_bound = 2 * tanh_decimal(log_score_error / 2)
        passed = union_bound <= delta_d and l1_bound <= gamma_d / 3
    return {
        "compact_exponent": 2 * condition,
        "compact_positive": floor_value > 0,
        "count": count,
        "n": n,
        "norm": condition,
        "q": coordinates,
        "r": degree,
    }, passed


def run_v58(cells: dict) -> tuple[bool, list[dict], dict]:
    rows = []
    passed = True
    rankings = tuple(permutations(("a", "b", "c")))

    for eta_text in cells["v58_eta_paths"]:
        eta = fraction(eta_text)
        direction = (0, -1, 1, -1, 1, 0)
        weights = tuple(Q(1, 6) + eta * shift for shift in direction)
        passed &= all(weight >= 0 for weight in weights) and sum(weights, Q(0)) == 1
        kernel = ranking_choice(weights)
        binary_uniform = all(
            kernel[(menu, item)] == Q(1, 2)
            for menu in (("a", "b"), ("a", "c"), ("b", "c"))
            for item in menu
        )
        full = tuple(kernel[(("a", "b", "c"), item)] for item in ("a", "b", "c"))
        expected = (Q(1, 3) - eta, Q(1, 3), Q(1, 3) + eta)
        passed &= binary_uniform and full == expected and full != (Q(1, 3),) * 3
        rows.append(
            {
                "binary_uniform": binary_uniform,
                "eta": qtext(eta),
                "full": [qtext(value) for value in full],
                "kind": "v58_eta",
            }
        )

    boundary_weights = (Q(1, 5), Q(1, 5), Q(1, 5), Q(1, 5), Q(0), Q(1, 5))
    boundary_kernel = ranking_choice(boundary_weights)
    boundary_full = tuple(
        boundary_kernel[(("a", "b", "c"), item)]
        for item in ("a", "b", "c")
    )
    passed &= boundary_full == (Q(2, 5), Q(2, 5), Q(1, 5))
    passed &= boundary_kernel[(("a", "b"), "a")] == Q(2, 5)
    for gamma_text in cells["v58_gamma_paths"]:
        gamma = fraction(gamma_text)
        nonrum = (Q(2, 5) + 2 * gamma, Q(2, 5) - 2 * gamma, Q(1, 5))
        regularity_gap = nonrum[0] - boundary_kernel[(("a", "b"), "a")]
        passed &= Q(0) < gamma <= Q(1, 125)
        passed &= regularity_gap == 2 * gamma and min(nonrum) > 0
        rows.append(
            {
                "full": [qtext(value) for value in nonrum],
                "gamma": qtext(gamma),
                "kind": "v58_gamma",
                "regularity_gap": qtext(regularity_gap),
            }
        )

    sample_rows = []
    for cell in cells["v58_sample_cells"]:
        row, cell_passed = sample_cell_row(cell)
        passed &= cell_passed
        sample_rows.append(row)
        rows.append({"kind": "v58_sample", **row})

    return passed, rows, {
        "eta_paths": len(cells["v58_eta_paths"]),
        "gamma_paths": len(cells["v58_gamma_paths"]),
        "sample_cells": len(sample_rows),
    }


def simplex_nonnegative(denominator: int, dimension: int) -> Iterator[tuple[Fraction, ...]]:
    def rec(remaining: int, slots: int, prefix: tuple[int, ...]):
        if slots == 1:
            yield prefix + (remaining,)
            return
        for value in range(remaining + 1):
            yield from rec(remaining - value, slots - 1, prefix + (value,))

    for numerators in rec(denominator, dimension, ()):
        yield tuple(Q(value, denominator) for value in numerators)


def simplex_positive(denominator: int, dimension: int) -> Iterator[tuple[Fraction, ...]]:
    for distribution in simplex_nonnegative(denominator, dimension):
        if min(distribution) > 0:
            yield distribution


def total_variation(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return sum((abs(a - b) for a, b in zip(left, right)), Q(0)) / 2


def common_huber(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
    epsilon: Fraction,
) -> tuple[Fraction, ...]:
    if epsilon == 0:
        return tuple(left)
    observed = [(1 - epsilon) * max(a, b) for a, b in zip(left, right)]
    observed[0] += 1 - sum(observed, Q(0))
    return tuple(observed)


def robust_sample_row(cell: dict, fraction_text: str) -> tuple[dict, bool]:
    base, base_passed = sample_cell_row(cell)
    fraction_value = fraction(fraction_text)
    n = int(cell["n"])
    degree = int(cell["r"])
    a_value = fraction(cell["a"])
    gamma = fraction(cell["gamma"])
    delta = fraction(cell["delta"])
    condition = maximum_interpolation_norm(n, degree)
    coordinates = coordinate_count(n, degree)
    with localcontext() as context:
        context.prec = 90
        a_d = decimal(a_value)
        gamma_d = decimal(gamma)
        delta_d = decimal(delta)
        clean = a_d * (
            1 - (-atanh_decimal(gamma_d / 6) / Decimal(condition)).exp()
        )
        epsilon = decimal(fraction_value) * clean
        sample_tolerance = clean - epsilon
        real_count = (
            (Decimal(2 * coordinates) / delta_d).ln()
            / (2 * sample_tolerance * sample_tolerance)
        )
        count = int(real_count.to_integral_value(rounding=ROUND_CEILING))
        empirical = (
            (Decimal(2 * coordinates) / delta_d).ln()
            / (2 * Decimal(count))
        ).sqrt()
        total = epsilon + empirical
        log_error = -2 * Decimal(condition) * (1 - total / a_d).ln()
        l1 = 2 * tanh_decimal(log_error / 2)
        passed = base_passed and total < clean and l1 < gamma_d / 3
    return {
        "contamination_fraction": qtext(fraction_value),
        "count": count,
        "n": n,
        "r": degree,
    }, passed


def run_v59(cells: dict) -> tuple[bool, list[dict], dict]:
    rows = []
    passed = True
    grid = cells["v59_simplex"]
    distributions = tuple(
        simplex_nonnegative(int(grid["denominator"]), int(grid["dimension"]))
    )
    histogram: Counter[str] = Counter()
    pair_checks = 0
    construction_checks = 0
    for left_index, right_index in combinations_with_replacement(
        range(len(distributions)),
        2,
    ):
        left = distributions[left_index]
        right = distributions[right_index]
        distance = total_variation(left, right)
        threshold = distance / (1 + distance)
        histogram[qtext(threshold)] += 1
        pair_checks += 1
        passed &= (1 - threshold) * distance <= threshold
        if threshold > 0:
            passed &= (1 - threshold / 2) * distance > threshold / 2
        observed = common_huber(left, right, threshold)
        passed &= sum(observed, Q(0)) == 1 and min(observed) >= 0
        if threshold == 0:
            passed &= left == right == observed
        else:
            left_bad = tuple(
                (value - (1 - threshold) * clean) / threshold
                for value, clean in zip(observed, left)
            )
            right_bad = tuple(
                (value - (1 - threshold) * clean) / threshold
                for value, clean in zip(observed, right)
            )
            passed &= min(left_bad + right_bad) >= 0
            passed &= sum(left_bad, Q(0)) == sum(right_bad, Q(0)) == 1
        construction_checks += 1

    rows.append(
        {
            "dimension": int(grid["dimension"]),
            "distributions": len(distributions),
            "histogram_sha256": canonical_digest(dict(sorted(histogram.items()))),
            "kind": "v59_grid",
            "pairs": pair_checks,
        }
    )

    for gamma_text in cells["v59_gamma_witnesses"]:
        gamma = fraction(gamma_text)
        left = (Q(2, 5), Q(2, 5), Q(1, 5))
        right = (Q(2, 5) + 2 * gamma, Q(2, 5) - 2 * gamma, Q(1, 5))
        distance = total_variation(left, right)
        epsilon = distance / (1 + distance)
        observed = common_huber(left, right, epsilon)
        passed &= gamma <= Q(1, 125)
        passed &= distance == 2 * gamma
        passed &= observed == tuple(
            value / (1 + 2 * gamma)
            for value in (Q(2, 5) + 2 * gamma, Q(2, 5), Q(1, 5))
        )
        rows.append(
            {
                "epsilon": qtext(epsilon),
                "gamma": qtext(gamma),
                "kind": "v59_witness",
                "observed": [qtext(value) for value in observed],
                "tv": qtext(distance),
            }
        )

    robust_cells = 0
    for cell in cells["v58_sample_cells"]:
        for contamination_fraction in cells["v59_contamination_fractions"]:
            row, cell_passed = robust_sample_row(cell, contamination_fraction)
            passed &= cell_passed
            robust_cells += 1
            rows.append({"kind": "v59_sample", **row})

    return passed, rows, {
        "construction_checks": construction_checks,
        "grid_pairs": pair_checks,
        "robust_sample_cells": robust_cells,
        "witnesses": len(cells["v59_gamma_witnesses"]),
    }


def symmetric_ratio(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return max(max(a / b, b / a) for a, b in zip(left, right))


def run_v60(cells: dict) -> tuple[bool, list[dict], dict]:
    rows = []
    passed = True
    grid = cells["v60_positive_simplex"]
    distributions = tuple(
        simplex_positive(int(grid["denominator"]), int(grid["dimension"]))
    )
    target = (Q(1, int(grid["dimension"])),) * int(grid["dimension"])
    confounding_checks = 0
    bounded_checks = 0
    overlap_counts = Counter()

    for left_index, right_index in combinations_with_replacement(
        range(len(distributions)),
        2,
    ):
        left = distributions[left_index]
        right = distributions[right_index]
        largest = min(
            tuple(p / q for p, q in zip(left, target))
            + tuple(p / q for p, q in zip(right, target))
        )
        record_rate = min(Q(1), largest) / 2
        left_recording = tuple(record_rate * q / p for p, q in zip(left, target))
        right_recording = tuple(record_rate * q / p for p, q in zip(right, target))
        left_joint = tuple(p * rho for p, rho in zip(left, left_recording))
        right_joint = tuple(p * rho for p, rho in zip(right, right_recording))
        passed &= left_joint == right_joint
        passed &= sum(left_joint, Q(0)) == record_rate
        passed &= min(left_recording + right_recording) > 0
        passed &= max(left_recording + right_recording) <= 1
        confounding_checks += 1

        required = symmetric_ratio(left, right)
        for bound in cells["v60_recording_bounds"]:
            lower = fraction(bound["lower"])
            upper = fraction(bound["upper"])
            admitted = required <= upper / lower
            interval_key = f"{qtext(lower)}:{qtext(upper)}"
            overlap_counts[interval_key] += int(admitted)
            coordinate_overlap = all(
                max(lower * a, lower * b) <= min(upper * a, upper * b)
                for a, b in zip(left, right)
            )
            passed &= admitted == coordinate_overlap
            if admitted:
                joint = tuple(max(lower * a, lower * b) for a, b in zip(left, right))
                rho_left = tuple(h / p for h, p in zip(joint, left))
                rho_right = tuple(h / p for h, p in zip(joint, right))
                passed &= all(
                    lower <= value <= upper
                    for value in rho_left + rho_right
                )
                passed &= sum(joint, Q(0)) <= 1
            bounded_checks += 1

    selection = (Q(2, 11), Q(0), Q(3, 11), Q(6, 11))
    selected_kernel = distributions[:4]
    joint = tuple(
        tuple(menu_mass * response for response in menu)
        for menu_mass, menu in zip(selection, selected_kernel)
    )
    recovered_selection = tuple(sum(menu, Q(0)) for menu in joint)
    passed &= recovered_selection == selection
    recovered_support = []
    for index, (mass, menu_joint, clean) in enumerate(
        zip(selection, joint, selected_kernel)
    ):
        if mass == 0:
            continue
        recovered_support.append(index)
        passed &= tuple(value / mass for value in menu_joint) == clean
    passed &= tuple(recovered_support) == (0, 2, 3)
    tier_handoff = {
        "no_rum_completion": ["N"],
        "rum_no_luce_completion": ["R", "N"],
        "luce_completion": ["L", "R", "N"],
    }
    passed &= [len(value) for value in tier_handoff.values()] == [1, 2, 3]

    conditional = cells["v60_conditional_cell"]
    conditional_cell = {
        "a": conditional["a"],
        "delta": conditional["conditional_delta"],
        "gamma": conditional["gamma"],
        "n": conditional["n"],
        "r": conditional["r"],
    }
    conditional_row, conditional_passed = sample_cell_row(conditional_cell)
    passed &= conditional_passed
    per_menu_count = conditional_row["count"]
    menu_count = int(conditional["menu_count"])
    undercount_delta = fraction(conditional["undercount_delta"])
    lower_gamma = fraction(conditional["lower_gamma"])
    with localcontext() as context:
        context.prec = 90
        gamma_d = decimal(lower_gamma)
        informative_kl = (
            -Decimal(2)
            / 5
            * (Decimal(1) - 25 * gamma_d * gamma_d).ln()
        )
        for floor_text in cells["v60_selection_floors"]:
            floor_value = fraction(floor_text)
            passed &= floor_value <= Q(1, menu_count)
            count_term = Decimal(2 * per_menu_count) / decimal(floor_value)
            probability_term = (
                Decimal(8)
                / decimal(floor_value)
                * (Decimal(menu_count) / decimal(undercount_delta)).ln()
            )
            total = int(
                max(count_term, probability_term).to_integral_value(
                    rounding=ROUND_CEILING
                )
            )
            lower = (
                2
                * (Decimal(1) - 2 * Decimal("0.1")) ** 2
                / (decimal(floor_value) * informative_kl)
            )
            rows.append(
                {
                    "floor": qtext(floor_value),
                    "kind": "v60_selection",
                    "lecam_floor_product": str(
                        (lower * decimal(floor_value)).quantize(
                            Decimal("1e-60")
                        )
                    ),
                    "per_menu_count": per_menu_count,
                    "total": total,
                }
            )

    rows.append(
        {
            "bounded_checks": bounded_checks,
            "confounding_checks": confounding_checks,
            "distributions": len(distributions),
            "kind": "v60_grid",
            "overlap_counts": dict(sorted(overlap_counts.items())),
            "support": recovered_support,
            "tier_handoff": tier_handoff,
        }
    )

    return passed, rows, {
        "bounded_checks": bounded_checks,
        "confounding_checks": confounding_checks,
        "distributions": len(distributions),
        "selection_cells": len(cells["v60_selection_floors"]),
    }


def run_primary(cells: dict) -> dict:
    b57, rows57, counts57 = run_v57(cells)
    m58, rows58, counts58 = run_v58(cells)
    c59, rows59, counts59 = run_v59(cells)
    s60, rows60, counts60 = run_v60(cells)
    rows = rows57 + rows58 + rows59 + rows60

    # Cross-version conventions are materialized in every sample row.  The
    # replay must reproduce the same canonical rows byte-for-byte.
    x0 = all(
        row.get("compact_positive", True)
        for row in rows
        if row["kind"] == "v58_sample"
    )
    gates = {
        "B57": bool(b57),
        "C59": bool(c59),
        "M58": bool(m58),
        "S60": bool(s60),
        "X0": bool(x0),
    }
    return {
        "counts": {
            "v57": counts57,
            "v58": counts58,
            "v59": counts59,
            "v60": counts60,
        },
        "fact_digest": canonical_digest(rows),
        "gates": gates,
        "rows": rows,
    }
