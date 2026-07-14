from __future__ import annotations

import pytest

from rsi_topology.bluebeam_tamper import (
    band_failover,
    curvature_injection,
    generate_tamper_suite,
    score_bluebeam_detections,
    spectrum_preserving_conjugation,
    write_tamper_pack,
)


def test_spectrum_conjugation_holds_spectrum_and_breaks_lineage():
    item = spectrum_preserving_conjugation()
    assert item.metrics["spectrum_max_absolute_difference"] < 1e-12
    assert item.metrics["selected_rank_before"] == item.metrics["selected_rank_after"]
    assert item.metrics["worst_direction_retention"] < 1e-12


def test_band_failover_holds_rank_and_occupancy():
    item = band_failover()
    assert item.metrics["selected_band_before"] == "low"
    assert item.metrics["selected_band_after"] == "middle"
    assert item.metrics["selected_rank_before"] == item.metrics["selected_rank_after"] == 8
    assert item.metrics["minimum_occupancy_before"] == item.metrics["minimum_occupancy_after"]


def test_curvature_injection_matches_edges_but_changes_loop():
    item = curvature_injection()
    assert item.metrics["flat_minimum_edge_worst_direction_retention"] == pytest.approx(
        item.metrics["curved_minimum_edge_worst_direction_retention"], abs=1e-12
    )
    assert item.metrics["curved_maximum_canonical_rotation_degrees"] > 50.0
    assert item.metrics["flat_maximum_canonical_rotation_degrees"] < 1e-6


def test_bluebeam_missing_or_negative_detection_is_blind_spot(tmp_path):
    suite = generate_tamper_suite()
    score = score_bluebeam_detections(
        suite,
        [{"tamper_id": suite[0].tamper_id, "detected": True, "detector": "lineage_certificate"}],
    )
    assert not score["all_detected"]
    assert [row["status"] for row in score["results"]].count("demonstrated_blind_spot") == 2
    manifest = write_tamper_pack(tmp_path)
    assert manifest["scenario_count"] == 3
    assert (tmp_path / "bluebeam_proposals.jsonl").exists()
