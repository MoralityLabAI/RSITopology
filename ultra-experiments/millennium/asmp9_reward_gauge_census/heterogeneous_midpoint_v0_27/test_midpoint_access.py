from fractions import Fraction

import numpy as np

from .midpoint_access import (
    effective_thresholds,
    expected_rounds,
    factorize_thresholds,
    graph_invariants,
    link_probability,
    maximum_bisection_error,
    population_bisect,
    projection_diagnostics,
    reparameterize_arbitrary_midpoints,
    robust_reconstruction_check,
    spanning_forest_partition,
    spectral_bound_from_laplacian,
)


def test_shared_midpoint_bisection_ignores_link_shape():
    target = Fraction(37, 19)
    estimate, queries = population_bisect(target, 5, Fraction(1, 128))
    assert abs(estimate - target) <= Fraction(1, 128)
    assert queries <= expected_rounds(Fraction(5), Fraction(1, 128))
    for shape, scale in (
        ("logistic", 0.4),
        ("atan", 1.7),
        ("rational", 3.0),
    ):
        for value in (-5.0, -0.25, 0.0, 0.75, 8.0):
            probability = link_probability(shape, value, scale)
            assert (probability > 0.5) - (probability < 0.5) == (
                value > 0
            ) - (value < 0)


def test_arbitrary_midpoint_drift_confounds_every_item_vector():
    edges = ((0, 0), (0, 1), (1, 0), (1, 1))
    original = (Fraction(1), Fraction(4))
    alternative = (Fraction(-3), Fraction(9))
    biases = (Fraction(2), Fraction(-1), Fraction(5), Fraction(7))
    shifted = reparameterize_arbitrary_midpoints(
        original, alternative, edges, biases
    )
    assert effective_thresholds(original, edges, biases) == effective_thresholds(
        alternative, edges, shifted
    )


def test_square_factorization_and_cycle_conflict():
    edges = ((0, 0), (0, 1), (1, 0), (1, 1))
    factorable = (Fraction(2), Fraction(5), Fraction(7), Fraction(10))
    result = factorize_thresholds(2, 2, edges, factorable)
    assert result.consistent
    assert result.component_count == 1
    assert result.cycle_rank == 1
    broken = list(factorable)
    broken[-1] += 1
    result = factorize_thresholds(2, 2, edges, broken)
    assert not result.consistent
    assert result.conflict_edge is not None


def test_tree_is_structurally_unfalsifiable():
    edges = ((0, 0), (1, 0), (1, 1), (2, 1))
    arbitrary = (Fraction(3), Fraction(-2), Fraction(11), Fraction(5))
    result = factorize_thresholds(3, 2, edges, arbitrary)
    assert result.consistent
    assert result.cycle_rank == 0


def test_component_gauge_and_spanning_ledger():
    edges = ((0, 0), (1, 0), (2, 1))
    invariants = graph_invariants(3, 2, edges)
    forest, chords = spanning_forest_partition(3, 2, edges)
    assert invariants == {
        "vertices": 5,
        "edges": 3,
        "components": 2,
        "incidence_rank": 3,
        "cycle_rank": 0,
    }
    assert len(forest) == invariants["incidence_rank"]
    assert len(chords) == invariants["cycle_rank"]


def test_projection_residual_is_zero_exactly_on_model():
    edges = ((0, 0), (0, 1), (1, 0), (1, 1))
    exact = np.array([2.0, 5.0, 7.0, 10.0])
    broken = exact.copy()
    broken[-1] += 1.0
    assert projection_diagnostics(2, 2, edges, exact)["residual_norm"] < 1e-10
    assert projection_diagnostics(2, 2, edges, broken)[
        "residual_norm"
    ] > 0.4


def test_pseudoinverse_bound_and_laplacian_identity():
    edges = ((0, 0), (0, 1), (1, 0), (1, 1))
    parameters = (1.0, 4.0, -2.0, 3.0)
    error = (0.1, -0.05, 0.07, -0.02)
    result = robust_reconstruction_check(2, 2, edges, parameters, error)
    assert result["pass"]
    diagnostics = projection_diagnostics(
        2, 2, edges, np.array([3.0, -2.0, 6.0, 1.0])
    )
    assert abs(
        diagnostics["quotient_amplification"]
        - spectral_bound_from_laplacian(2, 2, edges)
    ) < 1e-10


def test_exhaustive_bisection_bound_on_burned_grid():
    targets = (Fraction(n, 17) for n in range(-68, 69))
    tolerance = Fraction(1, 64)
    maximum, queries = maximum_bisection_error(
        targets, Fraction(4), tolerance
    )
    assert maximum <= tolerance
    assert queries <= expected_rounds(Fraction(4), tolerance)
