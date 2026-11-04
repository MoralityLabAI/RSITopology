"""Import-independent replay for ASMP-9 capped-simplex modulus v0.63."""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys


Q = Fraction
CAPS = (Q(2, 5), Q(3, 5), Q(2, 5))
FLOOR = Q(1, 10)


def parse(value):
    numerator, mark, denominator = str(value).partition("/")
    return Q(int(numerator), int(denominator)) if mark else Q(int(numerator))


def show(value):
    value = Q(value)
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def grid_laws(denominator):
    floor_count = denominator // 10
    return tuple(
        (
            Q(a_count, denominator),
            Q(b_count, denominator),
            Q(denominator - a_count - b_count, denominator),
        )
        for a_count in range(
            floor_count,
            denominator - 2 * floor_count + 1,
        )
        for b_count in range(
            floor_count,
            denominator - a_count - floor_count + 1,
        )
        if denominator - a_count - b_count >= floor_count
    )


def weights(law):
    a, b, c = law
    return (
        Q(3, 5) - b,
        Q(2, 5) - c,
        Q(3, 5) - a,
        Q(2, 5) - c,
        Q(2, 5) - a,
        Q(3, 5) - b,
    )


def is_rum(law):
    return all(value <= cap for value, cap in zip(law, CAPS))


def violation(law):
    return sum(
        (value - cap for value, cap in zip(law, CAPS) if value > cap),
        Q(0),
    )


def tv(left, right):
    return sum(abs(a - b) for a, b in zip(left, right)) / 2


def ratio(left, right):
    return max(max(a / b, b / a) for a, b in zip(left, right))


def project(law):
    result = list(law)
    removed = Q(0)
    for index, cap in enumerate(CAPS):
        if result[index] > cap:
            removed += result[index] - cap
            result[index] = cap
    for index, cap in enumerate(CAPS):
        addition = min(max(Q(0), cap - result[index]), removed)
        result[index] += addition
        removed -= addition
    assert removed == 0
    return tuple(result)


def supports():
    return tuple(
        support
        for size in range(1, 4)
        for support in combinations(range(3), size)
        if sum((CAPS[index] for index in support), Q(0)) < 1
    )


def bound(gamma, support):
    cap_sum = sum((CAPS[index] for index in support), Q(0))
    return max(
        1 + gamma / cap_sum,
        (1 - cap_sum) / (1 - cap_sum - gamma),
    )


def run(cells):
    gates = {
        "C0": True,
        "M0": True,
        "P0": True,
        "R0": True,
        "X0": True,
    }
    rows = []
    counts = {
        "corruption_checks": 0,
        "gamma_cells": 0,
        "grid_points": 0,
        "modulus_checks": 0,
        "projection_comparisons": 0,
        "reconstruction_checks": 0,
        "support_checks": 0,
    }
    gates["X0"] &= not set(cells["burned"]["gamma_cells"]).intersection(
        cells["gamma_cells"]
    )
    gates["X0"] &= not set(
        cells["burned"]["grid_denominators"]
    ).intersection(cells["grid_denominators"])

    for denominator in cells["grid_denominators"]:
        laws = grid_laws(denominator)
        rum_laws = tuple(law for law in laws if is_rum(law))
        for law in laws:
            ranking = weights(law)
            classified = min(ranking) >= 0
            gates["R0"] &= sum(ranking, Q(0)) == 1
            gates["R0"] &= classified == is_rum(law)
            if classified:
                reconstructed = (
                    ranking[0] + ranking[1],
                    ranking[2] + ranking[3],
                    ranking[4] + ranking[5],
                )
                gates["R0"] &= reconstructed == law
            counts["reconstruction_checks"] += 1

            projection = project(law)
            distance = violation(law)
            minimum = min(tv(law, candidate) for candidate in rum_laws)
            gates["P0"] &= is_rum(projection)
            gates["P0"] &= min(projection) >= FLOOR
            gates["P0"] &= tv(law, projection) == distance
            gates["P0"] &= minimum == distance
            counts["projection_comparisons"] += len(rum_laws)
        counts["grid_points"] += len(laws)
        rows.append(
            {
                "denominator": denominator,
                "grid_points": len(laws),
                "kind": "grid",
                "projection_comparisons": len(laws) * len(rum_laws),
                "rum_points": len(rum_laws),
            }
        )

    for gamma_text in cells["gamma_cells"]:
        gamma = parse(gamma_text)
        left = (Q(2, 5), Q(3, 10), Q(3, 10))
        right = (
            Q(2, 5) + gamma,
            Q(3, 10) - gamma / 2,
            Q(3, 10) - gamma / 2,
        )
        expected_delta = gamma
        expected_lambda = 1 + Q(5, 2) * gamma
        bounds = {
            support: bound(gamma, support)
            for support in supports()
        }
        gates["M0"] &= tv(left, right) == expected_delta
        gates["M0"] &= ratio(left, right) == expected_lambda
        gates["M0"] &= min(bounds.values()) == expected_lambda
        counts["modulus_checks"] += 3
        counts["support_checks"] += len(bounds)

        epsilon = gamma / (1 + gamma)
        observed = tuple(
            max(a, b) / (1 + gamma)
            for a, b in zip(left, right)
        )
        for clean in (left, right):
            contaminant = tuple(
                (
                    observed[index] - (1 - epsilon) * clean[index]
                )
                / epsilon
                for index in range(3)
            )
            gates["C0"] &= min(contaminant) >= 0
            gates["C0"] &= sum(contaminant, Q(0)) == 1
            counts["corruption_checks"] += 1

        lower = 1 / expected_lambda
        joint = tuple(
            lower * max(a, b)
            for a, b in zip(left, right)
        )
        for clean in (left, right):
            recording = tuple(
                joint[index] / clean[index]
                for index in range(3)
            )
            gates["C0"] &= all(
                clean[index] * recording[index] == joint[index]
                for index in range(3)
            )
            gates["C0"] &= all(lower <= value <= 1 for value in recording)
            counts["corruption_checks"] += 1

        rows.append(
            {
                "delta": show(expected_delta),
                "epsilon": show(epsilon),
                "gamma": show(gamma),
                "kind": "modulus",
                "lambda": show(expected_lambda),
                "support_bounds": {
                    ",".join(str(index) for index in support): show(value)
                    for support, value in sorted(bounds.items())
                },
            }
        )
        counts["gamma_cells"] += 1

    return {
        "counts": counts,
        "fact_digest": digest(rows),
        "gates": gates,
        "rows": rows,
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: independent_replay_v0_63.py CELLS.json")
    cells = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(run(cells), sort_keys=True))


if __name__ == "__main__":
    main()

