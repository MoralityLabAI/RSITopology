from fractions import Fraction as Q

from verify_theorems_v0_52 import (
    denominator_six_grid,
    independent_buehler,
    independent_monotone_tables,
    independent_orders,
    independent_valid,
    table_from_experiment,
)


def test_independent_universe_count():
    assert len(independent_monotone_tables()) == 148
    assert len(denominator_six_grid()) == 10


def test_independent_direct_map_logic():
    table = (0, 1, 1, 2)
    assert independent_valid(table, (1, 2))
    assert not independent_valid(table, (0, 2))
    assert independent_buehler(table, (0, 1)) == (1, 2)


def test_independent_tie_refinements_complete():
    assert independent_orders((2, 2, 2)) == tuple(
        __import__("itertools").permutations(range(3))
    )


def test_probability_experiment_reconstructs_control_table():
    table = table_from_experiment(
        (1, 1, 2),
        (
            (Q(1), Q(0)),
            (Q(0), Q(1)),
            (Q(1, 2), Q(1, 2)),
        ),
        Q(1, 2),
    )
    assert table == (0, 1, 1, 2)
