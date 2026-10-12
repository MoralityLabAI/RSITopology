from fractions import Fraction as Q

import pytest

from direct_map_completeness import (
    buehler_map,
    compare_global_optima,
    consistent_orders,
    direct_map_valid,
    dominance_certificate,
    minimal_controls,
    monotone_tables,
    validate_subset_bounds,
)


LEVELS = (Q(0), Q(1), Q(2))


def test_monotone_three_level_table_count():
    tables = monotone_tables(3, 3)
    assert len(tables) == 148
    assert all(table[0] == 0 for table in tables)


def test_direct_validity_uses_strict_failure_threshold():
    table = (Q(0), Q(1), Q(1), Q(2))
    assert direct_map_valid(table, (Q(1), Q(2)), LEVELS)
    assert not direct_map_valid(table, (Q(0), Q(2)), LEVELS)


def test_buehler_map_is_valid():
    table = (Q(0), Q(1), Q(1), Q(2))
    for order in ((0, 1), (1, 0)):
        assert direct_map_valid(
            table, buehler_map(table, order), LEVELS
        )


def test_every_tie_refinement_dominates():
    table = (Q(0), Q(1), Q(1), Q(2))
    reports = (Q(2), Q(2))
    assert consistent_orders(reports) == ((0, 1), (1, 0))
    for order in consistent_orders(reports):
        certificate = dominance_certificate(
            table, reports, LEVELS, order
        )
        assert certificate.input_valid
        assert certificate.buehler_valid
        assert certificate.pointwise_dominates
        assert certificate.strict_coordinates


def test_minimal_controls_separate_equality_and_strictness():
    controls = minimal_controls()
    equality = controls["equality"]
    strict = controls["strict"]
    assert equality.buehler_reports == equality.reports
    assert equality.strict_coordinates == ()
    assert strict.pointwise_dominates
    assert strict.strict_coordinates == (0,)
    assert strict.buehler_reports == (Q(1), Q(2))


def test_global_optima_match():
    table = (Q(0), Q(1), Q(1), Q(2))
    comparison = compare_global_optima(
        table,
        LEVELS,
        LEVELS,
        (Q(3, 4), Q(1, 4)),
    )
    assert comparison.direct_value == comparison.buehler_value


def test_invalid_table_and_inconsistent_order_rejected():
    with pytest.raises(ValueError):
        validate_subset_bounds((Q(0), Q(2), Q(1), Q(1)))
    with pytest.raises(ValueError):
        dominance_certificate(
            (Q(0), Q(1), Q(1), Q(2)),
            (Q(2), Q(1)),
            LEVELS,
            (0, 1),
        )
