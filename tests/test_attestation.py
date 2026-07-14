from __future__ import annotations

import numpy as np
import pytest

from rsi_topology.attestation import (
    ENGINEERING_EVIDENCE,
    HOLONOMY_CLEAN,
    LINEAGE_CERTIFIED,
    AnchorRecord,
    AnchorRegistry,
    EdgeReceipt,
    HolonomyBudget,
    LoopReceipt,
    array_sha256,
)


def make_record(*, mean=0.99, worst=0.98, angle=1.0, loss=0.01, det=-1.0 + 2.0):
    reference = np.eye(4, 2)
    current = np.linalg.qr(np.array([[1.0, 0.0], [0.0, 1.0], [0.02, 0.0], [0.0, 0.02]]))[0]
    ref_hash = array_sha256(reference)
    current_hash = array_sha256(current)
    reversal = det < 0
    return AnchorRecord(
        site_id="layer.12.mlp",
        consumer="vpd_edit_program",
        artifact_kind="disparate_weight_edit",
        reference_node="checkpoint.0",
        site_node="checkpoint.1",
        reference_basis_sha256=ref_hash,
        current_basis_sha256=current_hash,
        selected_band="low",
        spanning_tree_transport_path=("edge.0.1",),
        edge_receipts=(
            EdgeReceipt(
                edge_id="edge.0.1",
                source_node="checkpoint.0",
                target_node="checkpoint.1",
                selected_band="low",
                source_basis_sha256=ref_hash,
                target_basis_sha256=current_hash,
                transport_sha256="a" * 64,
                mean_edge_chordal_lineage=mean,
                minimum_edge_worst_direction_retention=worst,
            ),
            EdgeReceipt(
                edge_id="audit.1.0",
                source_node="checkpoint.1",
                target_node="checkpoint.0",
                selected_band="low",
                source_basis_sha256=current_hash,
                target_basis_sha256=ref_hash,
                transport_sha256="b" * 64,
                mean_edge_chordal_lineage=mean,
                minimum_edge_worst_direction_retention=worst,
            ),
        ),
        loop_receipts=(
            LoopReceipt(
                loop_id="loop.0",
                edge_ids=("edge.0.1", "audit.1.0"),
                determinant=det,
                det_h_flag=reversal,
                maximum_canonical_angle_degrees=None if reversal else angle,
                identity_loss=loss,
            ),
        ),
        holonomy_budget=HolonomyBudget(5.0, 0.05),
        det_h_flag=reversal,
    )


def test_certification_levels_and_frozen_consumer_rule():
    clean = AnchorRegistry(records=[make_record()])
    certificate = clean.certify("layer.12.mlp", requested_use="disparate_weight_edit")
    assert certificate.certification_level == HOLONOMY_CLEAN
    assert certificate.authorized
    assert certificate.margins["holonomy_angle_degrees"] == pytest.approx(4.0)

    lineage = AnchorRegistry(records=[make_record(angle=8.0)])
    certificate = lineage.certify("layer.12.mlp", requested_use="energy_reward")
    assert certificate.certification_level == LINEAGE_CERTIFIED
    assert certificate.authorized
    assert not lineage.certify("layer.12.mlp", requested_use="signed_reward").authorized

    engineering = AnchorRegistry(records=[make_record(mean=0.8)])
    certificate = engineering.certify("layer.12.mlp", requested_use="energy_reward")
    assert certificate.certification_level == ENGINEERING_EVIDENCE
    assert not certificate.authorized


def test_orientation_reversal_blocks_signed_use():
    registry = AnchorRegistry(records=[make_record(det=-1.0)])
    certificate = registry.certify("layer.12.mlp", requested_use="signed_intervention")
    assert certificate.certification_level == LINEAGE_CERTIFIED
    assert not certificate.authorized
    assert "holonomy:orientation_reversal" in certificate.failures


def test_registry_is_write_once_and_path_checked(tmp_path):
    registry = AnchorRegistry(records=[make_record()])
    path = tmp_path / "registry.json"
    first = registry.write_once(path)
    assert registry.write_once(path) == first
    broken = make_record()
    broken = AnchorRecord(**{**broken.__dict__, "site_node": "wrong"})
    with pytest.raises(ValueError, match="does_not_terminate"):
        AnchorRegistry(records=[broken])


def test_forged_scalar_receipts_are_rejected():
    forged = make_record(mean=2.0, worst=2.0, angle=-10.0, loss=-1.0)
    with pytest.raises(ValueError, match="metric_out_of_range"):
        AnchorRegistry(records=[forged])
