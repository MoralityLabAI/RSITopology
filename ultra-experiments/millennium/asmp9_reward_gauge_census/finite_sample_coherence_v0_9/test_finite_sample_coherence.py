from __future__ import annotations

from math import isclose

import numpy as np
import pytest

from finite_sample_coherence import (
    certify_coherence,
    circulations,
    expit,
    fundamental_cycle_basis,
    gradient_logits,
    hoeffding_probability_radius,
    sample_binomial_counts,
    simultaneous_event_holds,
    sufficient_samples_per_edge,
)


TRIANGLE = ((0, 1), (1, 2), (0, 2))


def test_triangle_basis_and_gradient_coherence() -> None:
    basis = fundamental_cycle_basis(3, TRIANGLE)
    assert basis == ((-1, -1, 1),)
    logits = gradient_logits((0.0, 0.2, -0.1), TRIANGLE)
    assert isclose(circulations(basis, logits)[0], 0.0, abs_tol=1e-15)


def test_parallel_edge_is_a_two_edge_cycle() -> None:
    edges = ((0, 1), (0, 1))
    assert fundamental_cycle_basis(2, edges) == ((-1, 1),)


def test_self_loop_is_a_one_edge_cycle() -> None:
    edges = ((0, 0),)
    assert fundamental_cycle_basis(1, edges) == ((1,),)


def test_forest_is_unavailable_not_coherent() -> None:
    certificate = certify_coherence(
        3,
        ((0, 1), (1, 2)),
        (5000, 5000),
        10000,
        alpha=0.05,
        probability_floor=0.1,
        coherent_tolerance=0.5,
        incoherent_margin=0.6,
    )
    assert certificate.status == "unavailable_no_cycles"


def test_probability_floor_is_an_admission_gate() -> None:
    certificate = certify_coherence(
        3,
        TRIANGLE,
        (1, 5000, 5000),
        10000,
        alpha=0.05,
        probability_floor=0.1,
        coherent_tolerance=0.5,
        incoherent_margin=0.6,
    )
    assert certificate.status == "unavailable_probability_floor"


def test_large_exact_coherent_counts_certify() -> None:
    n = 2_000_000
    certificate = certify_coherence(
        3,
        TRIANGLE,
        (n // 2, n // 2, n // 2),
        n,
        alpha=0.05,
        probability_floor=0.1,
        coherent_tolerance=0.5,
        incoherent_margin=0.6,
    )
    assert certificate.status == "certified_coherent_within_tolerance"


def test_large_planted_cycle_certifies_incoherence() -> None:
    n = 2_000_000
    probabilities = (0.5, 0.5, expit(1.2))
    counts = tuple(round(n * value) for value in probabilities)
    certificate = certify_coherence(
        3,
        TRIANGLE,
        counts,
        n,
        alpha=0.05,
        probability_floor=0.1,
        coherent_tolerance=0.5,
        incoherent_margin=0.6,
    )
    assert certificate.status == "certified_incoherent"


def test_small_sample_is_inconclusive_not_coherent() -> None:
    certificate = certify_coherence(
        3,
        TRIANGLE,
        (50, 50, 50),
        100,
        alpha=0.05,
        probability_floor=0.1,
        coherent_tolerance=0.5,
        incoherent_margin=0.6,
    )
    assert certificate.status in {
        "inconclusive",
        "unavailable_probability_floor",
    }
    assert certificate.status != "certified_coherent_within_tolerance"


def test_sufficient_bound_is_decisive_at_deterministic_center() -> None:
    n = sufficient_samples_per_edge(
        3,
        3,
        alpha=0.05,
        probability_floor=0.1,
        probability_interior_margin=0.2,
        coherent_tolerance=0.5,
        planted_circulation=1.2,
        incoherent_margin=0.6,
    )
    coherent = certify_coherence(
        3,
        TRIANGLE,
        (n // 2, n // 2, n // 2),
        n,
        alpha=0.05,
        probability_floor=0.1,
        coherent_tolerance=0.5,
        incoherent_margin=0.6,
    )
    assert coherent.status == "certified_coherent_within_tolerance"


def test_simultaneous_event_uses_raw_proportions() -> None:
    radius = hoeffding_probability_radius(3, 1000, 0.05)
    assert simultaneous_event_holds((500, 500, 500), 1000, (0.5, 0.5, 0.5), radius)
    assert not simultaneous_event_holds((0, 500, 500), 1000, (0.5, 0.5, 0.5), radius)


@pytest.mark.parametrize("seed", range(64))
def test_seeded_sampling_respects_binomial_support(seed: int) -> None:
    rng = np.random.default_rng(seed)
    counts = sample_binomial_counts((0.2, 0.5, 0.8), 100, rng)
    assert len(counts) == 3
    assert all(0 <= value <= 100 for value in counts)
