import json
from pathlib import Path

import numpy as np

from rsi_topology.projector_tomography import (
    fold_sign_decision,
    response_rms,
    select_scale_matched_alpha,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "protocols" / "qwen08_projector_tomography_v0_2.json"
MANIFEST = ROOT / "protocols" / "qwen08_dense_local_prompt_manifest_v0_1.json"


def test_successor_is_draft_and_preserves_claim_boundary():
    value = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert value["status"] == "draft_for_external_review_not_frozen"
    assert value["new_invariant_levels"] is False
    assert value["analysis"]["absolute_higher_order_energy"]["practical_ratio_rule"].startswith(
        "The geometric-mean selected/random E_ge2 ratio must exceed 1.5625"
    )


def test_calibration_and_confirmation_prompt_universes_are_disjoint_and_balanced():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = [
        row
        for row in manifest["rows"]
        if row["behavior_family"] == "graph_reachability"
        and row["context_shard"] == "shard-00"
        and row["half"] == "geometry_validation"
    ]
    calibration = {row["prompt_id"] for row in rows if 0 <= row["within_half_index"] <= 7}
    confirmation = {row["prompt_id"] for row in rows if 8 <= row["within_half_index"] <= 15}
    assert len(calibration) == len(confirmation) == 72
    assert calibration.isdisjoint(confirmation)
    for universe in (calibration, confirmation):
        counts = {}
        for row in rows:
            if row["prompt_id"] in universe:
                counts[row["subcondition_id"]] = counts.get(row["subcondition_id"], 0) + 1
        assert sorted(counts.values()) == [8] * 9


def test_response_rms_uses_all_nonbaseline_masks():
    cube = np.zeros((2, 16))
    cube[:, 1:] = 3.0
    assert response_rms(cube) == 3.0


def test_alpha_selection_uses_log_distance_and_lower_alpha_tie_break():
    selected = 2.0
    receipt = select_scale_matched_alpha(selected, {0.5: 1.0, 2.0: 4.0})
    # Ratios 0.5 and 2 are equidistant in log space; lower alpha wins.
    assert receipt["alpha"] == 0.5
    assert receipt["passed"] is False
    assert select_scale_matched_alpha(selected, {1.0: 1.6})["passed"] is True
    assert select_scale_matched_alpha(selected, {1.0: 2.5})["passed"] is True


def test_fold_sign_gate_has_exact_registered_boundaries():
    passed = fold_sign_decision([1.0] * 8 + [-1.0])
    failed = fold_sign_decision([-1.0] * 8 + [1.0])
    inconclusive = fold_sign_decision([1.0] * 7 + [-1.0, 0.0])
    assert passed["decision"] == "pass"
    assert failed["decision"] == "fail"
    assert inconclusive["decision"] == "inconclusive"
    assert np.isclose(passed["one_sided_sign_p"], 10 / 512)
