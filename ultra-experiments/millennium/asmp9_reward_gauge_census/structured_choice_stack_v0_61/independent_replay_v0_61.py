"""Import-independent replay for ASMP-9 structured-choice stack v0.61.

This implementation intentionally uses closed-form counts and Cartesian
enumeration rather than the primary verifier's subset and composition
generators.  It imports neither the primary verifier nor any v0.57-v0.60
development module.
"""

from __future__ import annotations

from collections import Counter
from decimal import Decimal, ROUND_CEILING, localcontext
from fractions import Fraction
import hashlib
from itertools import combinations_with_replacement, product
import json
from math import comb
from pathlib import Path
import sys


Q = Fraction


def parse(value) -> Fraction:
    if isinstance(value, int):
        return Q(value)
    numerator, mark, denominator = str(value).partition("/")
    return Q(int(numerator), int(denominator)) if mark else Q(int(numerator))


def show(value: Fraction) -> str:
    value = Q(value)
    return str(value.numerator) if value.denominator == 1 else (
        f"{value.numerator}/{value.denominator}"
    )


def dec(value) -> Decimal:
    value = parse(value)
    return Decimal(value.numerator) / Decimal(value.denominator)


def atanh(value: Decimal) -> Decimal:
    return ((1 + value).ln() - (1 - value).ln()) / 2


def tanh(value: Decimal) -> Decimal:
    exponential = (2 * value).exp()
    return (exponential - 1) / (exponential + 1)


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def norm_at(size: int, degree: int) -> int:
    if size <= degree:
        return 1
    total = 0
    for u in range(degree + 1):
        total += comb(size, u) * comb(size - u - 1, degree - u)
    return total


def maximum_norm(n: int, degree: int) -> int:
    return max(norm_at(size, degree) for size in range(n - 1))


def q_count(n: int, degree: int) -> int:
    return sum(
        size * comb(n, size)
        for size in range(2, min(n, degree + 2) + 1)
    )


def polynomial_target(n: int, degree: int, seed: int) -> int:
    width = n - 2
    result = 0
    for mask in range(1 << width):
        if mask.bit_count() > degree:
            continue
        weighted = sum(
            (index + 1) * (index + 3)
            for index in range(width)
            if mask & (1 << index)
        )
        result += (
            weighted + seed + 17 * n + 31 * degree + 13 * mask.bit_count()
        ) % 11 - 5
    return result


def sample_row(cell: dict) -> tuple[dict, bool]:
    n = int(cell["n"])
    degree = int(cell["r"])
    a_value = parse(cell["a"])
    gamma = parse(cell["gamma"])
    delta = parse(cell["delta"])
    condition = maximum_norm(n, degree)
    coordinates = q_count(n, degree)
    with localcontext() as context:
        context.prec = 90
        tolerance = dec(a_value) * (
            1 - (-atanh(dec(gamma) / 6) / Decimal(condition)).exp()
        )
        raw = (
            (Decimal(2 * coordinates) / dec(delta)).ln()
            / (2 * tolerance**2)
        )
        count = int(raw.to_integral_value(rounding=ROUND_CEILING))
        union = Decimal(2 * coordinates) * (
            -2 * Decimal(count) * tolerance**2
        ).exp()
        e_value = -2 * Decimal(condition) * (
            1 - tolerance / dec(a_value)
        ).ln()
        error = 2 * tanh(e_value / 2)
        passed = union <= dec(delta) and error <= dec(gamma) / 3
    return {
        "compact_exponent": 2 * condition,
        "compact_positive": a_value > 0,
        "count": count,
        "n": n,
        "norm": condition,
        "q": coordinates,
        "r": degree,
    }, passed


def nonnegative_grid(denominator: int, dimension: int):
    return tuple(
        tuple(Q(value, denominator) for value in values)
        for values in product(range(denominator + 1), repeat=dimension)
        if sum(values) == denominator
    )


def positive_grid(denominator: int, dimension: int):
    return tuple(
        tuple(Q(value, denominator) for value in values)
        for values in product(range(1, denominator), repeat=dimension)
        if sum(values) == denominator
    )


def tv(left, right) -> Fraction:
    return sum(abs(a - b) for a, b in zip(left, right)) / 2


def robust_row(cell: dict, contamination_text: str) -> tuple[dict, bool]:
    base, base_passed = sample_row(cell)
    fraction_value = parse(contamination_text)
    n = int(cell["n"])
    degree = int(cell["r"])
    condition = maximum_norm(n, degree)
    coordinates = q_count(n, degree)
    with localcontext() as context:
        context.prec = 90
        clean = dec(cell["a"]) * (
            1 - (-atanh(dec(cell["gamma"]) / 6) / Decimal(condition)).exp()
        )
        contamination = dec(fraction_value) * clean
        available = clean - contamination
        raw = (
            (Decimal(2 * coordinates) / dec(cell["delta"])).ln()
            / (2 * available**2)
        )
        count = int(raw.to_integral_value(rounding=ROUND_CEILING))
        empirical = (
            (Decimal(2 * coordinates) / dec(cell["delta"])).ln()
            / (2 * Decimal(count))
        ).sqrt()
        total = contamination + empirical
        e_value = -2 * Decimal(condition) * (1 - total / dec(cell["a"])).ln()
        passed = (
            base_passed
            and total < clean
            and 2 * tanh(e_value / 2) < dec(cell["gamma"]) / 3
        )
    return {
        "contamination_fraction": show(fraction_value),
        "count": count,
        "n": n,
        "r": degree,
    }, passed


def run_replay(cells: dict) -> dict:
    rows = []
    gates = {"B57": True, "C59": True, "M58": True, "S60": True, "X0": True}

    agreement_total = 0
    high_total = 0
    for cell in cells["v57_cells"]:
        n = int(cell["n"])
        degree = int(cell["r"])
        agreement = sum(
            size * comb(n, size)
            for size in range(2, degree + 2)
        )
        high = comb(n, 2) * sum(
            comb(n - 2, order)
            for order in range(degree + 1, n - 1)
        )
        special_probability = Q(degree + 2, 2 * degree + 3)
        target = polynomial_target(n, degree, int(cells["seed"]))
        gates["B57"] &= (
            len(cell["special_menu"]) == degree + 2
            and int(cell["special_item"]) in cell["special_menu"]
            and special_probability > Q(1, 2)
        )
        rows.append(
            {
                "agreement_coordinates": agreement,
                "high_degree_zero_checks": high,
                "kind": "v57",
                "max_degree": degree,
                "n": n,
                "norm": maximum_norm(n, degree),
                "r": degree,
                "special_probability": show(special_probability),
                "target_value": target,
            }
        )
        agreement_total += agreement
        high_total += high
    counts57 = {
        "agreement_coordinates": agreement_total,
        "cells": len(cells["v57_cells"]),
        "high_degree_zero_checks": high_total,
    }

    for eta_text in cells["v58_eta_paths"]:
        eta = parse(eta_text)
        full = (Q(1, 3) - eta, Q(1, 3), Q(1, 3) + eta)
        gates["M58"] &= 0 < eta < Q(1, 6) and min(full) > 0
        rows.append(
            {
                "binary_uniform": True,
                "eta": show(eta),
                "full": [show(value) for value in full],
                "kind": "v58_eta",
            }
        )
    for gamma_text in cells["v58_gamma_paths"]:
        gamma = parse(gamma_text)
        full = (Q(2, 5) + 2 * gamma, Q(2, 5) - 2 * gamma, Q(1, 5))
        gates["M58"] &= 0 < gamma <= Q(1, 125) and min(full) > 0
        rows.append(
            {
                "full": [show(value) for value in full],
                "gamma": show(gamma),
                "kind": "v58_gamma",
                "regularity_gap": show(2 * gamma),
            }
        )
    for cell in cells["v58_sample_cells"]:
        row, passed = sample_row(cell)
        gates["M58"] &= passed
        gates["X0"] &= row["compact_positive"]
        rows.append({"kind": "v58_sample", **row})
    counts58 = {
        "eta_paths": len(cells["v58_eta_paths"]),
        "gamma_paths": len(cells["v58_gamma_paths"]),
        "sample_cells": len(cells["v58_sample_cells"]),
    }

    grid_spec = cells["v59_simplex"]
    grid = nonnegative_grid(
        int(grid_spec["denominator"]),
        int(grid_spec["dimension"]),
    )
    histogram = Counter()
    for i, j in combinations_with_replacement(range(len(grid)), 2):
        distance = tv(grid[i], grid[j])
        threshold = distance / (1 + distance)
        histogram[show(threshold)] += 1
        gates["C59"] &= (1 - threshold) * distance <= threshold
        if threshold:
            gates["C59"] &= (1 - threshold / 2) * distance > threshold / 2
    pairs59 = len(grid) * (len(grid) + 1) // 2
    rows.append(
        {
            "dimension": int(grid_spec["dimension"]),
            "distributions": len(grid),
            "histogram_sha256": digest(dict(sorted(histogram.items()))),
            "kind": "v59_grid",
            "pairs": pairs59,
        }
    )
    for gamma_text in cells["v59_gamma_witnesses"]:
        gamma = parse(gamma_text)
        distance = 2 * gamma
        epsilon = distance / (1 + distance)
        observed = tuple(
            value / (1 + 2 * gamma)
            for value in (Q(2, 5) + 2 * gamma, Q(2, 5), Q(1, 5))
        )
        gates["C59"] &= gamma <= Q(1, 125)
        rows.append(
            {
                "epsilon": show(epsilon),
                "gamma": show(gamma),
                "kind": "v59_witness",
                "observed": [show(value) for value in observed],
                "tv": show(distance),
            }
        )
    robust_count = 0
    for cell in cells["v58_sample_cells"]:
        for contamination in cells["v59_contamination_fractions"]:
            row, passed = robust_row(cell, contamination)
            gates["C59"] &= passed
            rows.append({"kind": "v59_sample", **row})
            robust_count += 1
    counts59 = {
        "construction_checks": pairs59,
        "grid_pairs": pairs59,
        "robust_sample_cells": robust_count,
        "witnesses": len(cells["v59_gamma_witnesses"]),
    }

    positive_spec = cells["v60_positive_simplex"]
    positive = positive_grid(
        int(positive_spec["denominator"]),
        int(positive_spec["dimension"]),
    )
    pairs60 = len(positive) * (len(positive) + 1) // 2
    overlap_counts = Counter()
    bounded_checks = 0
    target = (Q(1, int(positive_spec["dimension"])),) * int(
        positive_spec["dimension"]
    )
    for i, j in combinations_with_replacement(range(len(positive)), 2):
        left = positive[i]
        right = positive[j]
        largest = min(
            tuple(p / q for p, q in zip(left, target))
            + tuple(p / q for p, q in zip(right, target))
        )
        z = min(Q(1), largest) / 2
        gates["S60"] &= all(
            0 < z * q / p <= 1
            for distribution in (left, right)
            for p, q in zip(distribution, target)
        )
        required = max(max(a / b, b / a) for a, b in zip(left, right))
        for bound in cells["v60_recording_bounds"]:
            lower = parse(bound["lower"])
            upper = parse(bound["upper"])
            admitted = required <= upper / lower
            overlap_counts[f"{show(lower)}:{show(upper)}"] += int(admitted)
            coordinatewise = all(
                max(lower * a, lower * b) <= min(upper * a, upper * b)
                for a, b in zip(left, right)
            )
            gates["S60"] &= admitted == coordinatewise
            bounded_checks += 1

    conditional = cells["v60_conditional_cell"]
    conditional_cell = {
        "a": conditional["a"],
        "delta": conditional["conditional_delta"],
        "gamma": conditional["gamma"],
        "n": conditional["n"],
        "r": conditional["r"],
    }
    response, response_passed = sample_row(conditional_cell)
    gates["S60"] &= response_passed
    per_menu = response["count"]
    menu_count = int(conditional["menu_count"])
    with localcontext() as context:
        context.prec = 90
        lower_gamma = dec(conditional["lower_gamma"])
        information = (
            -Decimal(2)
            / 5
            * (1 - 25 * lower_gamma**2).ln()
        )
        for floor_text in cells["v60_selection_floors"]:
            floor_value = parse(floor_text)
            gates["S60"] &= floor_value <= Q(1, menu_count)
            count_term = Decimal(2 * per_menu) / dec(floor_value)
            chance_term = (
                Decimal(8)
                / dec(floor_value)
                * (Decimal(menu_count) / dec(conditional["undercount_delta"])).ln()
            )
            total = int(
                max(count_term, chance_term).to_integral_value(
                    rounding=ROUND_CEILING
                )
            )
            lower = (
                2
                * (1 - 2 * Decimal("0.1")) ** 2
                / (dec(floor_value) * information)
            )
            rows.append(
                {
                    "floor": show(floor_value),
                    "kind": "v60_selection",
                    "lecam_floor_product": str(
                        (lower * dec(floor_value)).quantize(Decimal("1e-60"))
                    ),
                    "per_menu_count": per_menu,
                    "total": total,
                }
            )
    rows.append(
        {
            "bounded_checks": bounded_checks,
            "confounding_checks": pairs60,
            "distributions": len(positive),
            "kind": "v60_grid",
            "overlap_counts": dict(sorted(overlap_counts.items())),
            "support": [0, 2, 3],
            "tier_handoff": {
                "luce_completion": ["L", "R", "N"],
                "no_rum_completion": ["N"],
                "rum_no_luce_completion": ["R", "N"],
            },
        }
    )
    counts60 = {
        "bounded_checks": bounded_checks,
        "confounding_checks": pairs60,
        "distributions": len(positive),
        "selection_cells": len(cells["v60_selection_floors"]),
    }

    return {
        "counts": {
            "v57": counts57,
            "v58": counts58,
            "v59": counts59,
            "v60": counts60,
        },
        "fact_digest": digest(rows),
        "gates": gates,
        "rows": rows,
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: independent_replay_v0_61.py CELLS.json")
    cells = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(run_replay(cells), sort_keys=True))


if __name__ == "__main__":
    main()
