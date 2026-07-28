from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
CONDITIONAL = HERE.parent / "conditional_fiber_v0_13"
V016 = HERE.parent / "balanced_design_v0_16"
sys.path.insert(0, str(CONDITIONAL))
sys.path.insert(0, str(V016))

from conditional_fiber import (  # noqa: E402
    enumerate_fibers,
    fiber_affine_rank,
    incidence_rows,
)
from experiment import worst_endpoint_availability as cycle_worst  # noqa: E402
from general_graph import (  # noqa: E402
    FULL,
    INTERIOR,
    ZERO,
    full_quotient_availability,
    full_quotient_available,
    fractional_bad_support_design,
    graph_cycle_rank,
    minimal_bad_boundary_supports,
    theta_availability,
    theta_worst_endpoint_availability,
    worst_endpoint_availability,
)


GRAPHS = (
    (3, ((0, 1), (1, 2), (2, 0))),
    (4, ((0, 1), (1, 2), (2, 0), (0, 3), (3, 2))),
    (5, ((0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0))),
)


def test_residual_criterion_matches_full_fiber_rank() -> None:
    for node_count, edges in GRAPHS:
        rows = incidence_rows(node_count, edges)
        beta1 = graph_cycle_rank(node_count, edges)
        for trials_per_edge in (1, 2):
            trials = (trials_per_edge,) * len(edges)
            fibers = enumerate_fibers(trials, rows)
            for fiber in fibers.values():
                expected = fiber_affine_rank(fiber) == beta1
                for representative in fiber:
                    statuses = tuple(
                        ZERO
                        if count == 0
                        else FULL
                        if count == trials_per_edge
                        else INTERIOR
                        for count in representative
                    )
                    assert full_quotient_available(
                        node_count, edges, statuses
                    ) == expected


def test_single_cycle_reduces_to_v016_objective() -> None:
    for length in (3, 4, 5):
        edges = tuple(
            (index, (index + 1) % length)
            for index in range(length)
        )
        for counts in (
            (1,) * length,
            tuple(range(1, length + 1)),
        ):
            for epsilon in (
                Fraction(1, 6),
                Fraction(1, 3),
            ):
                observed, _ = worst_endpoint_availability(
                    length, edges, counts, epsilon
                )
                expected, _ = cycle_worst(counts, epsilon)
                assert observed == expected


def test_theta_closed_form_matches_status_enumeration() -> None:
    node_count = 4
    edges = ((0, 2), (0, 1), (1, 2), (0, 3), (3, 2))
    paths = ((0,), (1, 2), (3, 4))
    for counts in (
        (1, 1, 1, 1, 1),
        (1, 2, 3, 2, 1),
    ):
        for epsilon in (Fraction(1, 5), Fraction(1, 3)):
            for labels in (
                (0, 0, 0, 0, 0),
                (0, 1, 0, 1, 1),
                (1, 0, 1, 0, 1),
            ):
                probabilities = tuple(
                    epsilon if label == 0 else 1 - epsilon
                    for label in labels
                )
                from_statuses = full_quotient_availability(
                    node_count, edges, counts, probabilities
                )
                assert theta_availability(
                    paths, counts, probabilities
                ) == from_statuses
            theta_worst, _ = theta_worst_endpoint_availability(
                paths, counts, epsilon
            )
            generic_worst, _ = worst_endpoint_availability(
                node_count, edges, counts, epsilon
            )
            assert theta_worst == generic_worst


def test_uniform_allocation_counterexample_is_exact() -> None:
    paths = ((0,), (1, 2), (3, 4))
    epsilon = Fraction(1, 4)
    uniform, _ = theta_worst_endpoint_availability(
        paths, (2, 2, 2, 2, 2), epsilon
    )
    better, _ = theta_worst_endpoint_availability(
        paths, (1, 3, 2, 2, 2), epsilon
    )
    assert uniform == Fraction(218403, 524288)
    assert better == Fraction(228591, 524288)
    assert better > uniform


def test_bad_supports_recover_cycle_and_theta_exponents() -> None:
    cycle_edges = ((0, 1), (1, 2), (2, 3), (3, 0))
    assert minimal_bad_boundary_supports(4, cycle_edges) == (
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3),
    )

    theta_edges = (
        (0, 2),
        (0, 1),
        (1, 2),
        (0, 3),
        (3, 2),
    )
    supports = minimal_bad_boundary_supports(4, theta_edges)
    assert (1, 2) in supports
    assert (3, 4) in supports
    assert all(len(support) >= 2 for support in supports)

    cycle_design = fractional_bad_support_design(
        4, minimal_bad_boundary_supports(4, cycle_edges)
    )
    assert cycle_design["threshold"] == Fraction(1, 2)
    assert cycle_design["optimal_vertices"] == [
        (Fraction(1, 4),) * 4
    ]

    theta_design = fractional_bad_support_design(5, supports)
    assert theta_design["threshold"] == Fraction(1, 2)
    assert theta_design["optimal_vertices"] == [
        (
            Fraction(0),
            Fraction(1, 4),
            Fraction(1, 4),
            Fraction(1, 4),
            Fraction(1, 4),
        )
    ]
