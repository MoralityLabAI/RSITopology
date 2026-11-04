"""Primary exact verifier for ASMP-9 capped-simplex modulus v0.63."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json

from capped_simplex_modulus import (
    FLOOR,
    all_support_bounds,
    binary_probabilities_from_weights,
    common_huber_observation,
    common_recording_observation,
    delta_modulus,
    full_from_ranking_weights,
    huber_threshold,
    in_floor_class,
    is_rum,
    lambda_modulus,
    primal_pair,
    ranking_weights,
    rum_projection,
    symmetric_ratio,
    tv,
    violation_mass,
)


Q = Fraction


def parse(value) -> Fraction:
    numerator, mark, denominator = str(value).partition("/")
    return Q(int(numerator), int(denominator)) if mark else Q(int(numerator))


def show(value: Fraction) -> str:
    value = Q(value)
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def grid_laws(denominator: int):
    if denominator % 10:
        raise ValueError("grid denominator must preserve the 1/10 floor")
    floor_count = denominator // 10
    for a_count in range(
        floor_count,
        denominator - 2 * floor_count + 1,
    ):
        for b_count in range(
            floor_count,
            denominator - a_count - floor_count + 1,
        ):
            c_count = denominator - a_count - b_count
            if c_count >= floor_count:
                yield (
                    Q(a_count, denominator),
                    Q(b_count, denominator),
                    Q(c_count, denominator),
                )


def run_primary(cells: dict) -> dict:
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

    burned_gammas = set(cells["burned"]["gamma_cells"])
    burned_denominators = set(cells["burned"]["grid_denominators"])
    gates["X0"] &= not burned_gammas.intersection(cells["gamma_cells"])
    gates["X0"] &= not burned_denominators.intersection(
        cells["grid_denominators"]
    )

    for denominator in cells["grid_denominators"]:
        laws = tuple(grid_laws(int(denominator)))
        rum_laws = tuple(law for law in laws if is_rum(law))
        for law in laws:
            weights = ranking_weights(law)
            classified = min(weights) >= 0
            gates["R0"] &= sum(weights, Q(0)) == 1
            gates["R0"] &= classified == is_rum(law)
            if classified:
                gates["R0"] &= full_from_ranking_weights(weights) == law
                gates["R0"] &= (
                    binary_probabilities_from_weights(weights)
                    == (Q(2, 5), Q(3, 5), Q(3, 5))
                )
            counts["reconstruction_checks"] += 1

            projected = rum_projection(law)
            distance = violation_mass(law)
            minimum = min(tv(law, candidate) for candidate in rum_laws)
            gates["P0"] &= is_rum(projected)
            gates["P0"] &= in_floor_class(projected)
            gates["P0"] &= tv(law, projected) == distance
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
        left, right = primal_pair(gamma)
        expected_delta = delta_modulus(gamma)
        expected_lambda = lambda_modulus(gamma)
        bounds = all_support_bounds(gamma)
        gates["M0"] &= tv(left, right) == expected_delta
        gates["M0"] &= symmetric_ratio(left, right) == expected_lambda
        gates["M0"] &= min(bounds.values()) == expected_lambda
        counts["modulus_checks"] += 3
        counts["support_checks"] += len(bounds)

        epsilon = huber_threshold(gamma)
        observed = common_huber_observation(gamma)
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

        joint, left_recording, right_recording = (
            common_recording_observation(gamma)
        )
        lower = 1 / expected_lambda
        for clean, recording in (
            (left, left_recording),
            (right, right_recording),
        ):
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

