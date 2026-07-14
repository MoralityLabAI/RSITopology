from __future__ import annotations

import pytest

from rsi_topology.attestation import AnchorRegistry
from rsi_topology.vpd_stratification import (
    analyze_stratified_outcomes,
    seal_identity_strata,
    seal_identity_strata_v02,
)
from rsi_topology.attestation import AnchorRecord
from test_attestation import make_record


def feature(candidate, pair, arm, replicate):
    return {
        "candidate_id": candidate,
        "pair_id": pair,
        "arm": arm,
        "site_id": "layer.12.mlp",
        "run_replicate": replicate,
        "prompt_group": f"prompt-{replicate}",
        "family": "factual_recall",
        "norm": 0.5,
        "rank": 2,
    }


def test_seal_and_analyze_only_within_identity_strata():
    registry = AnchorRegistry(records=[make_record()])
    features = [
        feature("c1", "p1", "intervention", "r1"),
        feature("c2", "p1", "matched_random", "r1"),
        feature("c3", "p2", "intervention", "r2"),
        feature("c4", "p2", "matched_random", "r2"),
    ]
    sealed, registration = seal_identity_strata(features, registry)
    assert registration["outcomes_present"] is False
    assert all(row["identity_stratum"] == "holonomy_clean" for row in sealed)
    outcomes = [
        {"candidate_id": "c1", "accepted": 1, "repair_auc": 0.8, "initial_decay": 0.4},
        {"candidate_id": "c2", "accepted": 0, "repair_auc": 0.2, "initial_decay": 0.1},
        {"candidate_id": "c3", "accepted": 1, "repair_auc": 0.7, "initial_decay": 0.3},
        {"candidate_id": "c4", "accepted": 0, "repair_auc": 0.1, "initial_decay": 0.0},
    ]
    result = analyze_stratified_outcomes(sealed, outcomes, registration)
    assert result["pooled_effect"] == "prohibited"
    assert set(result["strata"]) == {"holonomy_clean"}
    assert result["strata"]["holonomy_clean"]["accepted"]["mean_paired_difference"] == 1.0


def test_reveal_rejects_bad_id_universe_and_broken_pair():
    registry = AnchorRegistry(records=[make_record()])
    features = [
        feature("c1", "p1", "intervention", "r1"),
        feature("c2", "p1", "matched_random", "r1"),
    ]
    sealed, registration = seal_identity_strata(features, registry)
    with pytest.raises(ValueError, match="universe mismatch"):
        analyze_stratified_outcomes(
            sealed,
            [{"candidate_id": "c1", "accepted": 1, "repair_auc": 0.8, "initial_decay": 0.4}],
            registration,
        )
    features[1]["rank"] = 4
    with pytest.raises(ValueError, match="not matched on rank"):
        seal_identity_strata(features, registry)


def feature_v02(candidate, pair, arm, contrast, site, direction_policy, *, jacobian=0.5, activation=1.0):
    return {
        **feature(candidate, pair, arm, "r1"),
        "contrast_type": contrast,
        "site_id": site,
        "layer_index": 12,
        "component_type": "mlp_output",
        "direction_policy": direction_policy,
        "jacobian_visibility": jacobian,
        "baseline_activation_rms": activation,
    }


def two_site_registry():
    first = make_record()
    second = AnchorRecord(**{**first.__dict__, "site_id": "layer.12.mlp.random"})
    return AnchorRegistry(records=[first, second])


def test_v02_separates_direction_and_site_selection_estimands():
    registry = two_site_registry()
    features = [
        feature_v02("d1", "direction-pair", "intervention", "direction_value", "layer.12.mlp", "attribution_selected"),
        feature_v02("d2", "direction-pair", "matched_random", "direction_value", "layer.12.mlp", "matched_random"),
        feature_v02("s1", "site-pair", "intervention", "site_selection", "layer.12.mlp", "attribution_selected", jacobian=0.50),
        feature_v02("s2", "site-pair", "matched_random", "site_selection", "layer.12.mlp.random", "attribution_selected", jacobian=0.55),
    ]
    sealed, registration = seal_identity_strata_v02(features, registry)
    assert registration["schema_version"] == "0.2.0"
    assert registration["contrast_pair_counts"] == {"direction_value": 1, "site_selection": 1}
    outcomes = [
        {"candidate_id": "d1", "accepted": 1, "repair_auc": 0.8, "initial_decay": 0.4},
        {"candidate_id": "d2", "accepted": 0, "repair_auc": 0.2, "initial_decay": 0.1},
        {"candidate_id": "s1", "accepted": 0, "repair_auc": 0.3, "initial_decay": 0.2},
        {"candidate_id": "s2", "accepted": 1, "repair_auc": 0.7, "initial_decay": 0.5},
    ]
    result = analyze_stratified_outcomes(sealed, outcomes, registration)
    assert result["pooled_across_contrasts"] == "prohibited"
    direction = result["contrasts"]["direction_value"]["strata"]["holonomy_clean"]
    site = result["contrasts"]["site_selection"]["strata"]["holonomy_clean"]
    assert direction["accepted"]["mean_paired_difference"] == 1.0
    assert site["accepted"]["mean_paired_difference"] == -1.0


def test_v02_reports_cross_site_pairs_outside_frozen_support():
    registry = two_site_registry()
    features = [
        feature_v02("s1", "site-pair", "intervention", "site_selection", "layer.12.mlp", "attribution_selected", jacobian=0.2),
        feature_v02("s2", "site-pair", "matched_random", "site_selection", "layer.12.mlp.random", "attribution_selected", jacobian=0.8),
    ]
    sealed, registration = seal_identity_strata_v02(features, registry)
    assert registration["outside_support_pair_count"] == 1
    assert registration["eligible_contrast_pair_counts"]["site_selection"] == 0
    assert all(not row["matched_support"] for row in sealed)
    outcomes = [
        {"candidate_id": "s1", "accepted": 1, "repair_auc": 0.8, "initial_decay": 0.4},
        {"candidate_id": "s2", "accepted": 0, "repair_auc": 0.2, "initial_decay": 0.1},
    ]
    result = analyze_stratified_outcomes(sealed, outcomes, registration)
    assert result["contrasts"]["site_selection"]["strata"] == {}
    assert result["outside_matched_support"][0]["support_failures"] == [
        "jacobian_visibility_outside_caliper"
    ]
