from __future__ import annotations

import random
from fractions import Fraction

import pytest

from behavioral_access import (
    adaptive_interval,
    bridge_indices,
    coherence_only_query_indices,
    fundamental_residuals,
    gradient_scores,
    is_coherent,
    least_squares_projection,
    nonadaptive_cells,
    optimal_nonadaptive_thresholds,
    reconstruct_from_forest,
    residual_is_orthogonal,
    spanning_forest_indices,
    weak_components,
    worst_cell_width,
)


def test_spanning_forest_has_rank_many_edges() -> None:
    edges = ((0, 1), (1, 2), (2, 0), (3, 4))
    components = weak_components(6, edges)
    forest = spanning_forest_indices(6, edges)
    assert len(forest) == 6 - len(components)


def test_tree_queries_reconstruct_coherent_scores() -> None:
    edges = ((0, 1), (1, 2), (2, 3), (0, 2), (1, 3))
    utility = tuple(map(Fraction, (3, -2, 5, 11)))
    scores = gradient_scores(utility, edges)
    recovered = reconstruct_from_forest(4, edges, scores)
    assert gradient_scores(recovered, edges) == scores
    assert is_coherent(4, edges, scores)
    assert all(value == 0 for value in fundamental_residuals(4, edges, scores))


def test_rock_paper_scissors_cycle_has_no_scalar_value() -> None:
    edges = ((0, 1), (1, 2), (2, 0))
    scores = (Fraction(1), Fraction(1), Fraction(1))
    assert not is_coherent(3, edges, scores)
    residuals = fundamental_residuals(3, edges, scores)
    assert residuals[-1] == 3


def test_unqueried_chord_can_falsify_same_tree_reconstruction() -> None:
    edges = ((0, 1), (1, 2), (2, 0))
    coherent = (Fraction(2), Fraction(3), Fraction(-5))
    corrupted = coherent[:-1] + (Fraction(-4),)
    forest = spanning_forest_indices(3, edges)
    assert all(coherent[index] == corrupted[index] for index in forest)
    assert is_coherent(3, edges, coherent)
    assert not is_coherent(3, edges, corrupted)


def test_coherence_only_skips_bridges_but_not_cycle_edges() -> None:
    edges = (
        (0, 1),
        (1, 2),
        (2, 0),
        (2, 3),
        (3, 4),
    )
    assert bridge_indices(5, edges) == (3, 4)
    assert coherence_only_query_indices(5, edges) == (0, 1, 2)


def test_parallel_edges_are_not_bridges() -> None:
    edges = ((0, 1), (0, 1), (1, 2))
    assert bridge_indices(3, edges) == (2,)
    assert coherence_only_query_indices(3, edges) == (0, 1)


def test_exact_hodge_projection_is_orthogonal() -> None:
    edges = ((0, 1), (1, 2), (2, 0), (0, 2))
    scores = tuple(map(Fraction, (1, 2, 4, -3)))
    _, residual = least_squares_projection(3, edges, scores)
    assert residual_is_orthogonal(3, edges, residual)
    assert any(value != 0 for value in residual)


@pytest.mark.parametrize("seed", range(8))
def test_exact_projection_recovers_seeded_gradient(seed: int) -> None:
    rng = random.Random(seed)
    vertex_count = 7
    edges = tuple(
        (left, right)
        for left in range(vertex_count)
        for right in range(left + 1, vertex_count)
        if rng.random() < 0.55
    )
    utility = tuple(Fraction(rng.randint(-9, 9), 3) for _ in range(vertex_count))
    scores = gradient_scores(utility, edges)
    fitted, residual = least_squares_projection(vertex_count, edges, scores)
    assert gradient_scores(fitted, edges) == scores
    assert all(value == 0 for value in residual)


@pytest.mark.parametrize("query_count", range(0, 12))
def test_adaptive_binary_search_has_exact_worst_width(query_count: int) -> None:
    denominator = 2 ** (query_count + 2)
    observed_widths = []
    for numerator in range(1, denominator, 2):
        theta = Fraction(numerator, denominator)
        lower, upper = adaptive_interval(theta, query_count)
        observed_widths.append(upper - lower)
    assert max(observed_widths) == Fraction(1, 2**query_count)


@pytest.mark.parametrize("query_count", range(0, 32))
def test_equispaced_nonadaptive_design_attains_bound(query_count: int) -> None:
    thresholds = optimal_nonadaptive_thresholds(query_count)
    cells = nonadaptive_cells(thresholds)
    assert worst_cell_width(cells) == Fraction(1, query_count + 1)


def test_nonuniform_nonadaptive_design_cannot_beat_bound() -> None:
    thresholds = (Fraction(1, 10), Fraction(1, 5), Fraction(9, 10))
    assert worst_cell_width(nonadaptive_cells(thresholds)) >= Fraction(1, 4)
