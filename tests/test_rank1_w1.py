from __future__ import annotations

import numpy as np
import pytest

from rsi_topology.rank1_w1 import (
    LoopInterval,
    clopper_pearson,
    edge_transport_sign,
    exact_uniform_class_probability,
    gf2_rank,
    predict_composite_sign,
    rank_one_between_class_basis,
    rectangular_loop_sign,
)


def test_loop_sign_is_invariant_to_node_gauge_flips():
    angles = [0.1, 0.2, 0.35, 0.5, 0.7, 0.9, 1.15, 1.3]
    keys = [(state, shard) for state in ("a", "b") for shard in range(4)]
    bases = {
        key: np.array([np.cos(angle), np.sin(angle)])
        for key, angle in zip(keys, angles)
    }
    interval = LoopInterval(0, 3)
    reference = rectangular_loop_sign(bases, states=("a", "b"), interval=interval)
    reframed = {key: value * (-1 if index % 3 == 0 else 1) for index, (key, value) in enumerate(bases.items())}
    assert rectangular_loop_sign(reframed, states=("a", "b"), interval=interval) == reference


def test_composite_sign_is_product_of_elementary_generators():
    signs = (1, -1, -1)
    assert predict_composite_sign(signs, LoopInterval(0, 2)) == -1
    assert predict_composite_sign(signs, LoopInterval(1, 3)) == 1
    assert predict_composite_sign(signs, LoopInterval(0, 3)) == 1


def test_registered_three_column_constraints_have_full_gf2_rank():
    rows = ((1, 1, 0), (0, 1, 1), (1, 1, 1))
    assert gf2_rank(rows) == 3
    assert exact_uniform_class_probability(7) == pytest.approx(1 / 128)


def test_rank_one_basis_and_precision_agree_on_separated_fixture():
    rng = np.random.default_rng(17)
    direction = np.array([0.8, -0.3, 0.4, 0.2])
    direction /= np.linalg.norm(direction)
    labels = np.repeat(np.arange(4), 30)
    features = np.vstack(
        [item * direction + 0.01 * rng.normal(size=4) for item in labels]
    )
    basis32 = rank_one_between_class_basis(features, labels, dtype=np.float32)
    basis64 = rank_one_between_class_basis(features, labels, dtype=np.float64)
    assert abs(float(basis32 @ basis64)) > 0.999999
    assert edge_transport_sign(basis32, basis64) in (-1, 1)


def test_degenerate_overlap_is_rejected_and_interval_is_exact():
    with pytest.raises(ValueError, match="sign-degenerate"):
        edge_transport_sign(np.array([1.0, 0.0]), np.array([0.0, 1.0]))
    lower, upper = clopper_pearson(128, 128)
    assert lower > 0.95
    assert upper == 1.0
