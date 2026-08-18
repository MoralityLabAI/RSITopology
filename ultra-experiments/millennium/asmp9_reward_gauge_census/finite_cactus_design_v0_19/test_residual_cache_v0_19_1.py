from fractions import Fraction
from itertools import product

from finite_cactus_design import (
    bouquet_cactus,
    graph_availability_direct,
)
from residual_cache_v0_19_1 import (
    graph_availability_cached,
    integer_status_law,
    live_status_table,
)


def test_integer_status_law_is_exact():
    epsilon = Fraction(3, 11)
    for count in range(1, 7):
        for label in (0, 1):
            law, denominator = integer_status_law(
                count, epsilon, label
            )
            assert sum(law.values()) == denominator
            assert all(value >= 0 for value in law.values())


def test_cached_contraction_matches_burned_fraction_evaluator():
    graph = bouquet_cactus((3, 3), bridge_count=1)
    live = live_status_table(graph)
    counts = (1, 2, 3, 2, 1, 3, 4)
    epsilon = Fraction(1, 3)
    for labels in product((0, 1), repeat=len(graph.edges)):
        assert graph_availability_cached(
            graph, live, counts, epsilon, labels
        ) == graph_availability_direct(
            graph, counts, epsilon, labels
        )


def test_liveness_table_is_reused_across_bridge_counts():
    graph = bouquet_cactus((3, 4), bridge_count=1)
    live = live_status_table(graph)
    epsilon = Fraction(1, 5)
    labels = (0, 1, 0, 1, 0, 1, 0, 1)
    first = graph_availability_cached(
        graph, live, (1, 2, 1, 2, 1, 2, 1, 1), epsilon, labels
    )
    second = graph_availability_cached(
        graph, live, (1, 2, 1, 2, 1, 2, 1, 8), epsilon, labels
    )
    assert first == second
