"""Burned smoke tests for the v0.61 verifier implementations."""

from fractions import Fraction
from pathlib import Path

import independent_replay_v0_61 as replay
import stack_verifier_v0_61 as primary


def test_fraction_and_canonical_rendering_agree():
    values = ("0", "7/13", "11", "-3/5")
    for value in values:
        assert primary.fraction(value) == replay.parse(value)
        assert primary.qtext(primary.fraction(value)) == replay.show(
            replay.parse(value)
        )


def test_interpolation_norm_implementations_agree_on_burned_grid():
    for n in range(3, 9):
        for degree in range(n - 1):
            assert primary.maximum_interpolation_norm(
                n, degree
            ) == replay.maximum_norm(n, degree)
            assert primary.coordinate_count(n, degree) == replay.q_count(
                n, degree
            )


def test_sample_count_implementations_agree_on_burned_v058_cell():
    cell = {"n": 3, "r": 1, "a": "1/5", "gamma": "1/5", "delta": "1/20"}
    primary_row, primary_passed = primary.sample_cell_row(cell)
    replay_row, replay_passed = replay.sample_row(cell)
    assert primary_passed and replay_passed
    assert primary_row == replay_row
    assert primary_row["count"] == 68_407


def test_huber_construction_hits_the_exact_overlap_boundary():
    left = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
    right = (Fraction(1, 3), Fraction(1, 2), Fraction(1, 6))
    distance = primary.total_variation(left, right)
    epsilon = distance / (1 + distance)
    observed = primary.common_huber(left, right, epsilon)
    assert distance == Fraction(1, 6)
    assert epsilon == Fraction(1, 7)
    assert sum(observed, Fraction(0)) == 1


def test_alternate_simplex_generators_have_known_burned_counts():
    assert len(tuple(primary.simplex_nonnegative(5, 3))) == 21
    assert len(replay.nonnegative_grid(5, 3)) == 21
    assert len(tuple(primary.simplex_positive(7, 3))) == 15
    assert len(replay.positive_grid(7, 3)) == 15


def test_independent_replay_does_not_import_primary_or_development_modules():
    source = Path(replay.__file__).read_text(encoding="utf-8")
    forbidden = (
        "import stack_verifier_v0_61",
        "bounded_context_degree_v0_57",
        "finite_sample_tiers_v0_58",
        "contamination_radius_v0_59",
        "selection_channel_v0_60",
    )
    assert not any(token in source for token in forbidden)

