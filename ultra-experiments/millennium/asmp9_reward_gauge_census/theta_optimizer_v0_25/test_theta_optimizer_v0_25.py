"""Development tests for the generalized-theta optimizer reduction."""

from __future__ import annotations

import itertools
import math
import random

import pytest

from theta_optimizer import (
    balanced_path_counts,
    build_theta_graph,
    flatten_balanced_allocation,
    optimize_theta,
    predecessor_availability,
    smooth_within_path,
    theta_availability_from_path_counts,
    theta_numerator_from_path_counts,
)


FORMULA_CELLS = (
    ((1, 2, 2), ((1,), (2, 2), (2, 3))),
    ((1, 2, 3), ((2,), (1, 3), (2, 3, 4))),
    ((2, 2, 3), ((1, 4), (2, 3), (1, 2, 5))),
)


@pytest.mark.parametrize("lengths,path_counts", FORMULA_CELLS)
def test_theta_formula_matches_v023_multivariate_evaluator(
    lengths: tuple[int, ...],
    path_counts: tuple[tuple[int, ...], ...],
) -> None:
    graph = build_theta_graph(lengths)
    flat_counts = tuple(
        count for path in path_counts for count in path
    )
    assert theta_availability_from_path_counts(path_counts) == (
        predecessor_availability(graph, flat_counts)
    )


def test_theta_formula_matches_v023_on_seeded_heterogeneous_cells() -> None:
    generator = random.Random(25025)
    length_cells = ((1, 2, 2), (1, 2, 3), (2, 2, 3), (1, 3, 3))
    for _ in range(64):
        lengths = generator.choice(length_cells)
        graph = build_theta_graph(lengths)
        flat_counts = tuple(
            generator.randint(1, 5) for _ in range(sum(lengths))
        )
        paths: list[tuple[int, ...]] = []
        offset = 0
        for length in lengths:
            paths.append(flat_counts[offset : offset + length])
            offset += length
        assert theta_availability_from_path_counts(tuple(paths)) == (
            predecessor_availability(graph, flat_counts)
        )


def test_strict_smoothing_inside_every_path() -> None:
    lengths = (1, 2, 3)
    for flat_counts in itertools.product(range(1, 5), repeat=sum(lengths)):
        paths = (
            flat_counts[:1],
            flat_counts[1:3],
            flat_counts[3:],
        )
        before = theta_numerator_from_path_counts(paths)
        for path_index, path in enumerate(paths):
            for high_index in range(len(path)):
                for low_index in range(len(path)):
                    if path[high_index] < path[low_index] + 2:
                        continue
                    after_paths = smooth_within_path(
                        paths, path_index, high_index, low_index
                    )
                    assert (
                        theta_numerator_from_path_counts(after_paths)
                        > before
                    )


def _positive_compositions(
    total: int, dimension: int
) -> tuple[tuple[int, ...], ...]:
    if dimension == 1:
        return ((total,),)
    result: list[tuple[int, ...]] = []
    for first in range(1, total - dimension + 2):
        for suffix in _positive_compositions(
            total - first, dimension - 1
        ):
            result.append((first,) + suffix)
    return tuple(result)


@pytest.mark.parametrize(
    "lengths,total_budget",
    (
        ((1, 2, 2), 10),
        ((1, 2, 3), 11),
        ((2, 2, 3), 12),
    ),
)
def test_reduced_optimizer_matches_full_edge_enumeration(
    lengths: tuple[int, ...], total_budget: int
) -> None:
    graph = build_theta_graph(lengths)
    reduced = optimize_theta(lengths, total_budget)
    full_values = [
        predecessor_availability(graph, counts)
        for counts in _positive_compositions(
            total_budget, len(graph.edges)
        )
    ]
    full_numerator = max(full_values) * 2**total_budget
    assert full_numerator.denominator == 1
    assert reduced.numerator == full_numerator.numerator


def test_theta_122_has_nonbalanced_global_optimum_at_budget_ten() -> None:
    result = optimize_theta((1, 2, 2), 10)
    assert result.path_totals == ((1, 4, 5), (1, 5, 4))
    assert result.numerator == 750
    assert result.composition_count == math.comb(10 - 5 + 3 - 1, 3 - 1)

    balanced = ((2,), (2, 2), (2, 2))
    assert theta_numerator_from_path_counts(balanced) == 734
    assert result.numerator - 734 == 16


def test_optimizer_emits_canonical_balanced_path_counts() -> None:
    result = optimize_theta((1, 2, 2), 10)
    allocations = tuple(
        flatten_balanced_allocation((1, 2, 2), totals)
        for totals in result.path_totals
    )
    assert allocations == (
        (1, 2, 2, 3, 2),
        (1, 3, 2, 2, 2),
    )


def test_cycle_is_included_as_two_path_boundary() -> None:
    result = optimize_theta((2, 3), 10)
    assert result.numerator > 0
    for totals in result.path_totals:
        allocation = flatten_balanced_allocation((2, 3), totals)
        assert max(allocation) - min(allocation) <= 1


def test_simple_graph_rejects_two_length_one_paths() -> None:
    with pytest.raises(ValueError, match="at most one"):
        build_theta_graph((1, 1, 2))


def test_balanced_path_counts_are_positive_and_nearly_equal() -> None:
    counts = balanced_path_counts(5, 17)
    assert sum(counts) == 17
    assert min(counts) >= 1
    assert max(counts) - min(counts) <= 1
