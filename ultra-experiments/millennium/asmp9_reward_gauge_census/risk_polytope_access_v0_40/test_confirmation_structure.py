from confirmation import (
    CONFIRMATION_QUERIES,
    S0_LABELS,
    S1_LABELS,
)
from risk_polytope_access import DEVELOPMENT_QUERIES


def test_confirmation_is_disjoint_in_targets_and_query_ids():
    assert len(next(iter(CONFIRMATION_QUERIES.values()))) == 4
    assert len(next(iter(DEVELOPMENT_QUERIES.values()))) == 3
    assert set(CONFIRMATION_QUERIES).isdisjoint(DEVELOPMENT_QUERIES)


def test_confirmation_partitions_are_distinct_and_nontrivial():
    assert S0_LABELS == (0, 0, 1, 1)
    assert S1_LABELS == (0, 1, 0, 1)
    assert S0_LABELS != S1_LABELS
    assert CONFIRMATION_QUERIES["s_const"] == (1, 1, 1, 1)
