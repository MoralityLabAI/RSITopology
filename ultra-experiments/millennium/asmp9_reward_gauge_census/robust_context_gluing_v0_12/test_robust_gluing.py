from __future__ import annotations

import numpy as np
import pytest

from exact_certificate import smallest_conditioning_witness
from robust_gluing import (
    arbitrary_query_bound,
    cycle_design_census,
    decompose,
    local_global_incidence,
    quotient_basis,
    simple_cycle_vectors,
)


def test_minimal_parallel_witness_has_only_gluing_error() -> None:
    local, shared, _ = local_global_incidence(
        2, (((0, 1),), ((0, 1),))
    )
    result = decompose(local, shared, (0.0, 1.0))
    assert result.obstruction_dimension == 1
    assert result.rho_local == pytest.approx(0.0, abs=1e-12)
    assert result.rho_glue == pytest.approx(2**-0.5)
    assert result.rho_total == pytest.approx(2**-0.5)
    assert result.pythagorean_residual < 1e-12


def test_shared_flow_has_zero_radii() -> None:
    local, shared, _ = local_global_incidence(
        3,
        (
            ((0, 1), (1, 2), (0, 2)),
            ((0, 1), (0, 2)),
        ),
    )
    flow = shared @ np.array((3.0, -2.0, 5.0))
    result = decompose(local, shared, flow)
    assert result.rho_local < 1e-12
    assert result.rho_glue < 1e-12
    assert result.rho_total < 1e-12


def test_local_triangle_inconsistency_is_separated() -> None:
    local, shared, _ = local_global_incidence(
        3,
        (
            ((0, 1), (1, 2), (0, 2)),
            ((0, 1),),
        ),
    )
    observation = np.array((1.0, 1.0, 3.0, 0.0))
    result = decompose(local, shared, observation)
    assert result.rho_local > 0.0
    assert result.rho_total**2 == pytest.approx(
        result.rho_local**2 + result.rho_glue**2
    )


def test_decomposition_is_invariant_to_potential_reparameterization() -> None:
    local, shared, _ = local_global_incidence(
        3,
        (
            ((0, 1), (1, 2)),
            ((0, 1), (0, 2)),
        ),
    )
    y = np.array((1.0, 2.0, -1.0, 3.0))
    base = decompose(local, shared, y)
    rng = np.random.default_rng(12)
    local_change = rng.normal(size=(local.shape[1], local.shape[1]))
    shared_change = rng.normal(size=(shared.shape[1], shared.shape[1]))
    while abs(np.linalg.det(local_change)) < 1e-3:
        local_change = rng.normal(size=local_change.shape)
    while abs(np.linalg.det(shared_change)) < 1e-3:
        shared_change = rng.normal(size=shared_change.shape)
    changed = decompose(local @ local_change, shared @ shared_change, y)
    assert changed.rho_local == pytest.approx(base.rho_local)
    assert changed.rho_glue == pytest.approx(base.rho_glue)
    assert changed.rho_total == pytest.approx(base.rho_total)


def test_query_count_lower_bound_and_orthonormal_optimum() -> None:
    under = arbitrary_query_bound(np.eye(3)[:2])
    optimal = arbitrary_query_bound(np.eye(3))
    scaled = arbitrary_query_bound(
        np.array(((1.0, 0.0), (0.5, 3**-0.5)))
    )
    assert under["rank"] == 2
    assert under["sigma_min"] == 0.0
    assert optimal["sigma_min"] == pytest.approx(1.0)
    assert optimal["amplification"] == pytest.approx(1.0)
    assert 0.0 < scaled["sigma_min"] < 1.0
    assert scaled["amplification"] > 1.0


def test_minimal_parallel_cycle_attains_one_dimensional_optimum() -> None:
    local, shared, labelled = local_global_incidence(
        2, (((0, 1),), ((0, 1),))
    )
    quotient = quotient_basis(local, shared)
    cycles = simple_cycle_vectors(2, labelled)
    census = cycle_design_census(cycles, quotient)
    assert census.obstruction_dimension == 1
    assert census.candidate_count == 1
    assert census.spanning_design_count == 1
    assert census.e_optimal is not None
    assert census.e_optimal.sigma_min == pytest.approx(1.0)


def test_smallest_conditioning_witness_has_exact_gram_certificates() -> None:
    result = smallest_conditioning_witness()
    assert result["local_rank"] == 5
    assert result["shared_rank"] == 3
    assert result["obstruction_dimension"] == 2
    assert result["short_normalized_gram"] == (
        ("2/3", "0"),
        ("0", "2/3"),
    )
    assert result["short_amplification_squared"] == "3/2"
    assert result["robust_normalized_gram"] == (
        ("1", "0"),
        ("0", "1"),
    )
    assert result["robust_amplification_squared"] == "1"
