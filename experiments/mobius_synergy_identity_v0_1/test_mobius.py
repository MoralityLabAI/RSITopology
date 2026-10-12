from __future__ import annotations

import numpy as np

from .mobius import (
    evaluate_grid,
    mobius_coefficients,
    mobius_units,
    worst_principal_retention,
)


def test_additive_factor_grid_has_zero_mobius_interaction() -> None:
    rng = np.random.default_rng(7)
    base = rng.normal(size=24)
    effect_a = rng.normal(size=(3, 24))
    effect_b = rng.normal(size=(4, 24))
    cells = np.empty((3, 4, 24))
    for axis_a in range(3):
        for axis_b in range(4):
            cells[axis_a, axis_b] = base + effect_a[axis_a] + effect_b[axis_b]
    assert np.max(np.abs(mobius_coefficients(cells))) <= 1e-10


def test_product_poset_mobius_recovers_planted_interaction() -> None:
    rng = np.random.default_rng(11)
    direction = rng.normal(size=32)
    direction /= np.linalg.norm(direction)
    cells = np.zeros((3, 3, 32))
    for axis_a in range(3):
        for axis_b in range(3):
            cells[axis_a, axis_b] = axis_a * axis_b * direction
    coefficients = mobius_coefficients(cells)
    expected = np.repeat(direction[None, :], 4, axis=0)
    assert np.allclose(coefficients, expected, atol=1e-12)


def _planted_split_cells(seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    shards, axis_a_count, axis_b_count, ambient = 20, 3, 3, 48
    interaction = rng.normal(size=ambient)
    interaction /= np.linalg.norm(interaction)
    halves = []
    for _ in range(2):
        half_specific_b = rng.normal(size=(axis_b_count, ambient)) * 3.0
        cells = np.empty((shards, axis_a_count, axis_b_count, ambient))
        for shard in range(shards):
            base = rng.normal(size=ambient)
            effect_a = rng.normal(size=(axis_a_count, ambient))
            for axis_a in range(axis_a_count):
                for axis_b in range(axis_b_count):
                    cells[shard, axis_a, axis_b] = (
                        base
                        + effect_a[axis_a]
                        + half_specific_b[axis_b]
                        + 4.0 * axis_a * axis_b * interaction
                        + rng.normal(scale=0.01, size=ambient)
                    )
        halves.append(cells)
    return halves[0], halves[1]


def test_planted_interaction_passes_split_stability_and_label_null() -> None:
    construction, validation = _planted_split_cells(23)
    result = evaluate_grid(
        construction,
        validation,
        ranks=[1],
        bootstrap_replicates=48,
        permutation_replicates=48,
        lower_quantile=0.05,
        upper_quantile=0.95,
        minimum_strict_margin=0.02,
        seed=29,
    )
    receipt = result.receipts[0]
    assert receipt["observed_retention"] > 0.95
    assert receipt["strict_margin"] > 0.02
    assert receipt["passed"] is True


def test_principal_retention_is_basis_gauge_invariant() -> None:
    rng = np.random.default_rng(31)
    basis, _ = np.linalg.qr(rng.normal(size=(40, 5)))
    gauge_left, _ = np.linalg.qr(rng.normal(size=(5, 5)))
    gauge_right, _ = np.linalg.qr(rng.normal(size=(5, 5)))
    assert np.isclose(
        worst_principal_retention(basis @ gauge_left, basis @ gauge_right),
        1.0,
        atol=1e-12,
    )


def test_mobius_unit_order_is_shard_then_plaquette() -> None:
    cells = np.zeros((2, 2, 2, 1))
    cells[0, 1, 1, 0] = 3.0
    cells[1, 1, 1, 0] = 7.0
    assert np.array_equal(mobius_units(cells).ravel(), np.array([3.0, 7.0]))
