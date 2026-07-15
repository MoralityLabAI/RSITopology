from __future__ import annotations

import numpy as np

from rsi_topology.attestation import (
    ENGINEERING_EVIDENCE,
    HOLONOMY_CLEAN,
    AnchorRegistry,
)
from rsi_topology.bifiltration import build_lineage_holonomy_bifiltration
from rsi_topology.discovery import (
    DiscoveryConfig,
    discover_between_class_scatter_object,
    discover_lineage_objects_v03,
    evaluate_discovery,
)
from rsi_topology.synthetic import build_fixture
from test_attestation import make_record


def _class_fixture(
    *,
    seed: int,
    separated: bool,
    classes: int = 6,
    rows_per_class_half: int = 24,
    dimension: int = 18,
    rank: int = 3,
):
    rng = np.random.default_rng(seed)
    planted = np.linalg.qr(rng.normal(size=(dimension, rank)), mode="reduced")[0]
    codes = rng.normal(size=(classes, rank))
    codes -= np.mean(codes, axis=0, keepdims=True)
    features = []
    labels = []
    halves = []
    for half in ("construction-a", "construction-b"):
        for class_index in range(classes):
            mean = 4.5 * (planted @ codes[class_index]) if separated else 0.0
            noise = rng.normal(size=(rows_per_class_half, dimension))
            noise *= np.linspace(1.5, 0.35, dimension)
            features.append(noise + mean)
            labels.extend([f"family-{class_index}"] * rows_per_class_half)
            halves.extend([half] * rows_per_class_half)
    return np.vstack(features), np.asarray(labels), np.asarray(halves)


def test_random_labels_with_real_spectrum_fail_control_and_cap_attestation():
    features, labels, halves = _class_fixture(seed=301, separated=False)
    dead = discover_between_class_scatter_object(
        features=features,
        family_labels=labels,
        construction_halves=halves,
        rank=3,
        gate_role="matched_random_label_negative_control",
        object_kind="dead_random_label_control",
        replicates=64,
        seed=302,
    )
    assert not dead.passed

    record = make_record(
        metadata={"matched_random_label_negative_control": dead.receipt()}
    )
    certificate = AnchorRegistry(records=[record]).certify(
        record.site_id, requested_use="disparate_weight_edit"
    )
    assert certificate.certification_level == ENGINEERING_EVIDENCE
    assert not certificate.authorized
    assert "negative_control_not_passed" in certificate.failures


def test_planted_between_class_object_passes_primary_and_control_nulls():
    features, labels, halves = _class_fixture(seed=311, separated=True)
    control_x, control_y, control_halves = _class_fixture(
        seed=312, separated=True
    )
    # The control names are arbitrary and sealed; the planted feature means,
    # not the spelling of the labels, supply the expected recoverable object.
    rename = {
        value: f"random-family-{index}"
        for index, value in enumerate(np.unique(control_y))
    }
    random_control_labels = np.asarray([rename[value] for value in control_y])
    result = discover_lineage_objects_v03(
        features=features,
        family_labels=labels,
        construction_halves=halves,
        negative_control_features=control_x,
        negative_control_labels=random_control_labels,
        negative_control_halves=control_halves,
        rank=3,
        replicates=64,
        seed=313,
    )

    assert result.primary.passed
    assert result.matched_random_label_negative_control.passed
    assert result.primary.null_margin > 0.02
    assert result.matched_random_label_negative_control.null_margin > 0.02
    assert result.passed


def test_zero_cycle_rank_is_holonomy_unavailable_and_caps_clean_record():
    bifiltration = build_lineage_holonomy_bifiltration(
        registered_nodes=("a", "b", "c", "d"),
        edges=(
            {"edge_id": "ab", "source_node": "a", "target_node": "b", "worst_direction_retention": 0.96},
            {"edge_id": "bc", "source_node": "b", "target_node": "c", "worst_direction_retention": 0.003},
            {"edge_id": "cd", "source_node": "c", "target_node": "d", "worst_direction_retention": 0.95},
        ),
        loops=(
            {"loop_id": "attempted", "edge_order": ["ab", "bc", "cd"]},
        ),
        lineage_floor=0.90,
    )

    assert bifiltration.beta_1 == 0
    assert bifiltration.status == "holonomy_unavailable"
    assert bifiltration.connected_component_count == 2
    assert bifiltration.admitted_loop_ids == ()

    passing_control = {
        "random_family_retention_lower_95": 0.96,
        "permutation_null_retention_upper_95": 0.90,
    }
    record = make_record(
        metadata={
            "matched_random_label_negative_control": passing_control,
            "lineage_holonomy_bifiltration": bifiltration.attestation_metadata(),
        }
    )
    certificate = AnchorRegistry(records=[record]).certify(
        record.site_id, requested_use="disparate_weight_edit"
    )
    assert certificate.certification_level != HOLONOMY_CLEAN
    assert "holonomy_unavailable" in certificate.failures


def test_covariance_v022_path_runs_but_v03_marks_it_reported_ungated():
    fixture = build_fixture(
        seed=321,
        contexts=4,
        candidates_per_context=24,
        dimension=24,
        planted_rank=6,
    )
    legacy = evaluate_discovery(
        laplacians=fixture.laplacians,
        vectors=fixture.vectors,
        baseline_covariates=fixture.baseline_covariates,
        outcomes=fixture.outcomes,
        groups=fixture.groups,
        config=DiscoveryConfig(
            minimum_consensus_rank=4,
            maximum_consensus_rank=12,
        ),
    )

    assert legacy.geometry["object_kind"] == "covariance_gram_consensus"
    assert legacy.geometry["v0_3_status"] == "reported_ungated"
    assert legacy.geometry["v0_3_gate_eligible"] is False
    assert legacy.policy["v0_3_status"] == "reported_ungated"
    assert legacy.policy["v0_3_gate_eligible"] is False
    assert legacy.direct_edit["v0_3_status"] == "reported_ungated"
    assert legacy.direct_edit["v0_3_gate_eligible"] is False


def test_positive_cycle_rank_admits_within_component_loop():
    result = build_lineage_holonomy_bifiltration(
        edges=(
            {"edge_id": "ab", "source_node": "a", "target_node": "b", "lineage": 0.99},
            {"edge_id": "bc", "source_node": "b", "target_node": "c", "lineage": 0.99},
            {"edge_id": "ca", "source_node": "c", "target_node": "a", "lineage": 0.99},
        ),
        loops=({"loop_id": "abc", "edge_ids": ["ab", "bc", "ca"]},),
        lineage_floor=0.90,
    )

    assert result.beta_1 == 1
    assert result.status == "holonomy_structurally_available"
    assert result.admitted_loop_ids == ("abc",)
