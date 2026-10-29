import numpy as np

from rsi_topology.projector_tomography import (
    design_matrix,
    exact_boolean_coefficients,
    interaction_order_energy,
    orthogonal_random_direction,
    reconstruct_rank_one,
    relative_sse_reduction,
)


def test_rank_one_reconstruction_and_random_control():
    rng = np.random.default_rng(7)
    direction = np.zeros(12)
    direction[3] = 1.0
    labels = np.repeat(np.arange(4), 20)
    features = rng.normal(scale=0.1, size=(80, 12)) + labels[:, None] * direction
    recovered, center, eigenvalue = reconstruct_rank_one(features, labels)
    assert abs(recovered @ direction) > 0.99
    assert center.shape == (12,)
    assert eigenvalue > 0
    control = orthogonal_random_direction(recovered, seed=8)
    assert abs(control @ recovered) < 1e-12
    assert np.isclose(np.linalg.norm(control), 1.0)


def test_complete_cube_recovers_pair_and_quadruple_terms():
    bits = np.array(
        [[(mask >> index) & 1 for index in range(4)] for mask in range(16)],
        dtype=float,
    )
    y = 1.2 + 0.3 * bits[:, 0] - 0.7 * bits[:, 1] * bits[:, 3]
    y += 0.9 * np.prod(bits, axis=1)
    coefficients = exact_boolean_coefficients(bits, y)
    assert np.isclose(coefficients[(0,)], 0.3)
    assert np.isclose(coefficients[(1, 3)], -0.7)
    assert np.isclose(coefficients[(0, 1, 2, 3)], 0.9)
    energies = interaction_order_energy(coefficients)
    assert np.isclose(energies[2], 0.49)
    assert np.isclose(energies[4], 0.81)


def test_degree_two_design_strictly_contains_degree_one():
    bits = np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=float)
    assert design_matrix(bits, 1).shape == (4, 2)
    assert design_matrix(bits, 2).shape == (4, 3)
    y = bits[:, 0] * bits[:, 1]
    low = design_matrix(bits, 1) @ np.linalg.lstsq(design_matrix(bits, 1), y, rcond=None)[0]
    high = design_matrix(bits, 2) @ np.linalg.lstsq(design_matrix(bits, 2), y, rcond=None)[0]
    assert relative_sse_reduction(y, low, high) > 0.99
