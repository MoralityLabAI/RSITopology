from fractions import Fraction as Q

from confirmation import (
    ALIGNMENTS,
    CONFIRMATION_STRENGTHS,
    INTERVENTION_PROBABILITIES,
    LEAKAGE_VECTORS,
)
from gauge_leakage import DEVELOPMENT_STRENGTHS


def test_confirmation_strengths_are_disjoint_from_burned_development():
    assert set(CONFIRMATION_STRENGTHS).isdisjoint(DEVELOPMENT_STRENGTHS)
    assert len(CONFIRMATION_STRENGTHS) == 4
    assert all(high + low == 1 for high, low in CONFIRMATION_STRENGTHS)


def test_confirmation_universe_is_frozen_and_nontrivial():
    assert ALIGNMENTS == ("q0", "q0_complement", "q1", "q2", "constant")
    assert len(LEAKAGE_VECTORS) == 3
    assert INTERVENTION_PROBABILITIES == (Q(2, 7), Q(5, 9))
