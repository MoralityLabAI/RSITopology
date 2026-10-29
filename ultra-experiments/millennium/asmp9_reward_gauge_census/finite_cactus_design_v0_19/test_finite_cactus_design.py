from fractions import Fraction
from itertools import product

import pytest

from finite_cactus_design import (
    CactusGraph,
    Edge,
    allocation_value,
    balanced_allocation,
    balanced_cycle_value,
    bouquet_cactus,
    cactus_availability_factorized,
    cycle_worst_direct,
    globally_balanced_cycle_totals,
    graph_availability_direct,
    marginal_greedy_endpoints,
    optimize_all_edges_exhaustive,
    optimize_cactus_dp,
    optimize_cycle_totals_exhaustive,
    validate_cactus,
)


def test_compact_cycle_value_matches_direct_endpoint_enumeration():
    epsilon = Fraction(1, 4)
    for length in range(3, 8):
        for total in range(length, length + 9):
            counts = balanced_allocation(total, length)
            direct = cycle_worst_direct(counts, epsilon)[0]
            compact = balanced_cycle_value(length, total, epsilon)[0]
            assert compact == direct


def test_cactus_factorization_matches_direct_residual_enumeration():
    graph = bouquet_cactus((3, 3))
    counts = (1, 2, 1, 2, 1, 2)
    epsilon = Fraction(1, 3)
    for labels in product((0, 1), repeat=len(graph.edges)):
        assert graph_availability_direct(
            graph, counts, epsilon, labels
        ) == cactus_availability_factorized(
            graph, counts, epsilon, labels
        )


def test_bridge_counts_do_not_change_availability():
    graph = bouquet_cactus((3,), bridge_count=2)
    epsilon = Fraction(1, 5)
    labels = (0, 1, 0, 1, 0)
    assert graph_availability_direct(
        graph, (2, 3, 4, 1, 1), epsilon, labels
    ) == graph_availability_direct(
        graph, (2, 3, 4, 7, 9), epsilon, labels
    )


def test_dp_matches_independent_cycle_total_enumeration():
    for lengths, budget, epsilon, bridges in (
        ((3, 4), 13, Fraction(1, 5), 0),
        ((3, 5, 4), 18, Fraction(1, 4), 1),
        ((4, 4, 5), 21, Fraction(1, 3), 2),
    ):
        dynamic = optimize_cactus_dp(
            lengths, budget, epsilon, bridges
        )
        exhaustive = optimize_cycle_totals_exhaustive(
            lengths, budget, epsilon, bridges
        )
        assert dynamic.value == exhaustive.value
        assert dynamic.cycle_totals == exhaustive.cycle_totals


def test_small_all_edge_enumeration_matches_dp_and_reserves_bridge_floor():
    graph = bouquet_cactus((3, 3), bridge_count=1)
    epsilon = Fraction(1, 4)
    total = 11
    direct_value, direct_optimizers = optimize_all_edges_exhaustive(
        graph, total, epsilon
    )
    dynamic = optimize_cactus_dp((3, 3), total, epsilon, bridge_count=1)
    assert direct_value == dynamic.value
    assert all(counts[-1] == 1 for counts in direct_optimizers)
    direct_cycle_totals = {
        (
            sum(counts[index] for index in graph.cycle_blocks[0]),
            sum(counts[index] for index in graph.cycle_blocks[1]),
        )
        for counts in direct_optimizers
    }
    assert direct_cycle_totals == set(dynamic.cycle_totals)


def test_tie_independent_greedy_counterexample():
    lengths = (3, 3)
    epsilon = Fraction(1, 4)
    total = 10
    greedy = marginal_greedy_endpoints(lengths, total, epsilon)
    exact = optimize_cactus_dp(lengths, total, epsilon)
    assert greedy == ((4, 6), (6, 4))
    assert exact.cycle_totals == ((5, 5),)
    assert all(
        allocation_value(lengths, totals, epsilon) < exact.value
        for totals in greedy
    )
    assert exact.value - allocation_value(
        lengths, greedy[0], epsilon
    ) == Fraction(45, 262144)


def test_asymptotic_uniform_edge_design_can_fail_at_finite_budget():
    lengths = (3, 4)
    epsilon = Fraction(1, 10)
    total = 12
    globally_balanced = globally_balanced_cycle_totals(lengths, total)
    exact = optimize_cactus_dp(lengths, total, epsilon)
    best_global = max(
        allocation_value(lengths, totals, epsilon)
        for totals in globally_balanced
    )
    assert globally_balanced == (
        (4, 8),
        (5, 7),
        (6, 6),
    )
    assert exact.cycle_totals == ((3, 9),)
    assert exact.value > best_global


def test_rejects_overlapping_non_cactus_cycles():
    graph = CactusGraph(
        edges=(
            Edge("a", 0, 1),
            Edge("b", 1, 2),
            Edge("c", 2, 0),
            Edge("d", 1, 3),
            Edge("e", 3, 0),
        ),
        cycle_blocks=((0, 1, 2), (0, 3, 4)),
        bridge_indices=(),
    )
    with pytest.raises(ValueError, match="edge-disjoint"):
        validate_cactus(graph)
