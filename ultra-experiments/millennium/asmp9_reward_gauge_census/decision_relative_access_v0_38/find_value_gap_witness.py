"""Burned development search for a value-gap/deficiency separation."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys
from typing import Any


Q = Fraction
HERE = Path(__file__).resolve().parent
V037 = HERE.parent / "stochastic_experiment_v0_37"
sys.path.insert(0, str(V037))

from experiment import (  # noqa: E402
    BinaryExperiment,
    directional_deficiency,
    minimax_sample_risk,
)


GRID = tuple(Q(index, 8) for index in range(9))
DECISION = (0, 1)
CANONICAL_LEFT = (Q(1), Q(1, 2))
CANONICAL_RIGHT = (Q(1, 2), Q(0))


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def channel(values: tuple[Q, Q]) -> BinaryExperiment:
    return BinaryExperiment(tuple((value,) for value in values))


def run() -> dict[str, Any]:
    rows = []
    for values in product(GRID, repeat=2):
        current = channel(values)
        risk = minimax_sample_risk(current, DECISION).value
        rows.append((values, current, risk))

    collisions = 0
    largest = Q(0)
    for _, source, source_risk in rows:
        for _, target, target_risk in rows:
            if source_risk != target_risk:
                continue
            forward = directional_deficiency(source, target).value
            reverse = directional_deficiency(target, source).value
            if forward > 0 or reverse > 0:
                collisions += 1
                largest = max(largest, forward, reverse)

    left = channel(CANONICAL_LEFT)
    right = channel(CANONICAL_RIGHT)
    left_risk = minimax_sample_risk(left, DECISION).value
    right_risk = minimax_sample_risk(right, DECISION).value
    forward = directional_deficiency(left, right).value
    reverse = directional_deficiency(right, left).value
    return {
        "schema_version": "asmp9_v038_burned_value_gap_witness_v0_1",
        "status": "development_not_claim_eligible",
        "grid": [qstr(value) for value in GRID],
        "experiments": len(rows),
        "ordered_equal_value_pairs_with_positive_deficiency": collisions,
        "largest_directional_deficiency_among_collisions": qstr(largest),
        "canonical_witness": {
            "left_probabilities": [qstr(value) for value in CANONICAL_LEFT],
            "right_probabilities": [
                qstr(value) for value in CANONICAL_RIGHT
            ],
            "left_minimax_error": qstr(left_risk),
            "right_minimax_error": qstr(right_risk),
            "left_to_right_deficiency": qstr(forward),
            "right_to_left_deficiency": qstr(reverse),
        },
        "claim_boundary": (
            "Burned exact development control. Equal optimized minimax "
            "error does not imply experiment equivalence. Relative "
            "deficiency remains classical; this is not a new theorem or "
            "an ASMP-9 result."
        ),
    }


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
