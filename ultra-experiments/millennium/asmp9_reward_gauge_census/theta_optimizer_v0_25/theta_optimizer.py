"""Exact generalized-theta allocation tools for ASMP-9 v0.25 development.

A generalized theta block consists of internally vertex-disjoint paths with
common terminals.  At the maximally noisy endpoint, every path has four
effective states: forward only, reverse only, both, or neither.

The exact strong-availability numerator is

    product_j (2 A_j - B_j) - 2 product_j (A_j - B_j),

where

    A_j = product_(e in path j) (2**n_e - 1)
    B_j = product_(e in path j) (2**n_e - 2).

Strict pair smoothing shows that counts inside each path differ by at most
one in every global optimum.  The remaining exact search is over path totals.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterator, Sequence


Edge = tuple[int, int]


@dataclass(frozen=True)
class ThetaGraph:
    node_count: int
    edges: tuple[Edge, ...]
    path_edge_indices: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class ThetaOptimum:
    numerator: int
    path_totals: tuple[tuple[int, ...], ...]
    composition_count: int


def validate_path_lengths(path_lengths: Sequence[int]) -> tuple[int, ...]:
    lengths = tuple(path_lengths)
    if len(lengths) < 2:
        raise ValueError("a theta block requires at least two paths")
    if any(not isinstance(length, int) or length < 1 for length in lengths):
        raise ValueError("path lengths must be positive integers")
    if lengths.count(1) > 1:
        raise ValueError(
            "a simple theta graph can contain at most one length-one path"
        )
    return lengths


def build_theta_graph(path_lengths: Sequence[int]) -> ThetaGraph:
    """Build a simple generalized theta graph with terminals 0 and 1."""

    lengths = validate_path_lengths(path_lengths)
    edges: list[Edge] = []
    paths: list[tuple[int, ...]] = []
    next_node = 2
    for length in lengths:
        path_nodes = [0]
        for _ in range(length - 1):
            path_nodes.append(next_node)
            next_node += 1
        path_nodes.append(1)
        indices: list[int] = []
        for source, target in zip(
            path_nodes[:-1], path_nodes[1:], strict=True
        ):
            indices.append(len(edges))
            edges.append((source, target))
        paths.append(tuple(indices))
    return ThetaGraph(next_node, tuple(edges), tuple(paths))


def _path_products(counts: Sequence[int]) -> tuple[int, int]:
    if not counts or any(
        not isinstance(count, int) or count < 1 for count in counts
    ):
        raise ValueError("path counts must be positive integers")
    product_one_missing = 1
    product_two_missing = 1
    for count in counts:
        product_one_missing *= 2**count - 1
        product_two_missing *= 2**count - 2
    return product_one_missing, product_two_missing


def theta_numerator_from_path_counts(
    path_counts: Sequence[Sequence[int]],
) -> int:
    """Return the common-denominator strong-availability numerator."""

    if len(path_counts) < 2:
        raise ValueError("at least two paths are required")
    all_usable = 1
    all_one_direction = 1
    for counts in path_counts:
        product_a, product_b = _path_products(tuple(counts))
        all_usable *= 2 * product_a - product_b
        all_one_direction *= product_a - product_b
    result = all_usable - 2 * all_one_direction
    if result < 0:
        raise AssertionError("strong-availability numerator became negative")
    return result


def theta_availability_from_path_counts(
    path_counts: Sequence[Sequence[int]],
) -> Fraction:
    counts = tuple(tuple(path) for path in path_counts)
    numerator = theta_numerator_from_path_counts(counts)
    total_trials = sum(sum(path) for path in counts)
    return Fraction(numerator, 2**total_trials)


def balanced_path_counts(path_length: int, total: int) -> tuple[int, ...]:
    """Return one canonical within-path balanced allocation."""

    if path_length < 1 or total < path_length:
        raise ValueError("path total must cover one trial per edge")
    quotient, remainder = divmod(total, path_length)
    return (quotient + 1,) * remainder + (quotient,) * (
        path_length - remainder
    )


def theta_numerator_from_path_totals(
    path_lengths: Sequence[int], path_totals: Sequence[int]
) -> int:
    lengths = validate_path_lengths(path_lengths)
    totals = tuple(path_totals)
    if len(lengths) != len(totals):
        raise ValueError("path length/total dimensions differ")
    path_counts = tuple(
        balanced_path_counts(length, total)
        for length, total in zip(lengths, totals, strict=True)
    )
    return theta_numerator_from_path_counts(path_counts)


def path_total_compositions(
    total_budget: int, path_lengths: Sequence[int]
) -> Iterator[tuple[int, ...]]:
    """Yield all path totals above their positive-count floors."""

    lengths = validate_path_lengths(path_lengths)
    if total_budget < sum(lengths):
        raise ValueError("total budget is below the positive-count floor")

    def recurse(
        remaining: int, index: int
    ) -> Iterator[tuple[int, ...]]:
        if index == len(lengths) - 1:
            if remaining >= lengths[index]:
                yield (remaining,)
            return
        minimum_rest = sum(lengths[index + 1 :])
        for current in range(
            lengths[index], remaining - minimum_rest + 1
        ):
            for suffix in recurse(remaining - current, index + 1):
                yield (current,) + suffix

    yield from recurse(total_budget, 0)


def optimize_theta(
    path_lengths: Sequence[int], total_budget: int
) -> ThetaOptimum:
    """Solve the exact global allocation after path-internal reduction."""

    lengths = validate_path_lengths(path_lengths)
    optimum: int | None = None
    optimizers: list[tuple[int, ...]] = []
    composition_count = 0
    for totals in path_total_compositions(total_budget, lengths):
        composition_count += 1
        numerator = theta_numerator_from_path_totals(lengths, totals)
        if optimum is None or numerator > optimum:
            optimum = numerator
            optimizers = [totals]
        elif numerator == optimum:
            optimizers.append(totals)
    if optimum is None:
        raise AssertionError("path-total enumeration produced no cells")
    return ThetaOptimum(
        numerator=optimum,
        path_totals=tuple(optimizers),
        composition_count=composition_count,
    )


def smooth_within_path(
    path_counts: Sequence[Sequence[int]],
    path_index: int,
    high_index: int,
    low_index: int,
) -> tuple[tuple[int, ...], ...]:
    """Move one trial from a path-internal high edge to a low edge."""

    result = [list(path) for path in path_counts]
    path = result[path_index]
    if path[high_index] < path[low_index] + 2:
        raise ValueError("selected pair does not admit strict smoothing")
    path[high_index] -= 1
    path[low_index] += 1
    return tuple(tuple(values) for values in result)


def flatten_balanced_allocation(
    path_lengths: Sequence[int], path_totals: Sequence[int]
) -> tuple[int, ...]:
    lengths = validate_path_lengths(path_lengths)
    totals = tuple(path_totals)
    if len(lengths) != len(totals):
        raise ValueError("path length/total dimensions differ")
    return tuple(
        count
        for length, total in zip(lengths, totals, strict=True)
        for count in balanced_path_counts(length, total)
    )


def _load_v023_module():
    source = (
        Path(__file__).resolve().parents[1]
        / "nonuniform_multivariate_v0_23"
        / "nonuniform_multivariate.py"
    )
    spec = importlib.util.spec_from_file_location(
        "_asmp9_nonuniform_multivariate_v023_for_theta", source
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load v0.23 source from {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def predecessor_availability(
    graph: ThetaGraph, counts: Sequence[int]
) -> Fraction:
    """Call the independent v0.23 multivariate evaluator."""

    module = _load_v023_module()
    return Fraction(
        module.multivariate_tutte_availability(
            graph.node_count, graph.edges, tuple(counts)
        )
    )

