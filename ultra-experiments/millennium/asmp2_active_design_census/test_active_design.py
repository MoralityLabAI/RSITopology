import json
from pathlib import Path

import numpy as np

from run import (
    corners,
    deployment_families,
    exact_score,
    feature_matrix,
    map_corner,
    map_subset,
    score_mask,
    space_filling_masks,
)


HERE = Path(__file__).resolve().parent


def test_feature_basis_is_registered_walsh_subsystem():
    features = feature_matrix(corners())
    assert features.shape == (16, 11)
    assert np.array_equal(features.T @ features, 16 * np.eye(11))


def test_deployment_family_sizes_are_fixed():
    families = deployment_families(corners())
    assert len(families["full_cube"]) == 16
    assert len(families["nonnegative_sum"]) == 11
    assert len(families["even_parity"]) == 8


def test_empty_and_full_design_boundaries():
    features = feature_matrix(corners())
    for targets in deployment_families(corners()).values():
        empty, empty_rank = score_mask(0, features, targets, 1e-12)
        full, full_rank = score_mask((1 << 16) - 1, features, targets, 1e-12)
        assert empty == 11
        assert empty_rank == 0
        assert full == 0
        assert full_rank == 11


def test_exact_and_numeric_score_agree_on_nontrivial_design():
    features = feature_matrix(corners())
    targets = deployment_families(corners())["full_cube"]
    mask = (1 << 0) | (1 << 3) | (1 << 5) | (1 << 12)
    numeric, _ = score_mask(mask, features, targets, 1e-12)
    exact = exact_score(mask, features.astype(int).tolist(), targets)
    assert abs(float(exact) - numeric) < 1e-8


def test_signed_coordinate_mapping_is_bijective_and_subset_count_preserving():
    permutation = (2, 0, 3, 1)
    mapped = [map_corner(mask, permutation, 0b1010) for mask in range(16)]
    assert sorted(mapped) == list(range(16))
    source_mask = (1 << 0) | (1 << 4) | (1 << 15)
    assert map_subset(source_mask, permutation, 0b1010).bit_count() == 3


def test_space_filling_sequence_has_unique_environments_and_consecutive_budgets():
    records = space_filling_masks(range(1, 11))
    assert [record["budget"] for record in records] == list(range(1, 11))
    assert len({record["selected_environment"] for record in records}) == 10
    assert records[-1]["mask"].bit_count() == 10


def test_protocol_declares_complete_subset_universe():
    protocol = json.loads((HERE / "protocol_v0_2.json").read_text(encoding="utf-8"))
    assert protocol["instrument_gates"]["complete_subset_count"] == 2 ** 16
    assert protocol["scientific_thresholds"]["first_budget_excluded"] is True
