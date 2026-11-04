import json
from pathlib import Path

import numpy as np

import run as parent
from run_v0_2_1 import fast_census


HERE = Path(__file__).resolve().parent


def test_amendment_binds_unchanged_parent_protocol():
    amendment = json.loads((HERE / "protocol_v0_2_1.json").read_text(encoding="utf-8"))
    assert parent.sha256_file(HERE / amendment["parent_protocol"]) == amendment["parent_protocol_sha256"]
    assert amendment["scientific_contract_changes"] == "none"


def test_rank_one_projector_update_matches_direct_svd_on_registered_rows():
    features = parent.feature_matrix(parent.corners())
    direct, direct_rank = parent.null_projector(features[[0, 3, 5, 12]], features.shape[1], 1e-12)
    projector = np.eye(features.shape[1])
    rank = 0
    for environment in (0, 3, 5, 12):
        residual = projector @ features[environment]
        norm_squared = residual @ residual
        if norm_squared > 1e-10:
            projector -= np.outer(residual, residual) / norm_squared
            rank += 1
    assert rank == direct_rank
    assert np.allclose(projector, direct, atol=1e-10, rtol=0)


def test_parent_choice_does_not_change_representative_projector():
    features = parent.feature_matrix(parent.corners())
    selected = (0, 2, 7, 11, 15)
    projectors = []
    for ordering in (selected, tuple(reversed(selected))):
        projector = np.eye(features.shape[1])
        for environment in ordering:
            residual = projector @ features[environment]
            norm_squared = residual @ residual
            if norm_squared > 1e-10:
                projector = projector - np.outer(residual, residual) / norm_squared
        projectors.append(projector)
    assert np.allclose(projectors[0], projectors[1], atol=1e-10, rtol=0)


def test_performance_amendment_preserves_parent_thresholds_and_seeds():
    parent_protocol = json.loads((HERE / "protocol_v0_2.json").read_text(encoding="utf-8"))
    amendment = json.loads((HERE / "protocol_v0_2_1.json").read_text(encoding="utf-8"))
    for field in amendment["frozen_parent_fields"]:
        assert field in parent_protocol
    assert parent_protocol["selectors"]["random"]["seed_sequence_root"] == 20402026
    assert parent_protocol["scientific_thresholds"]["first_budget_excluded"] is True
