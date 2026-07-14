from __future__ import annotations

import json
from itertools import product
from pathlib import Path

from rsi_topology.composite_gate_v2 import (
    COMPONENT_STATES,
    composite_decision,
    composite_record,
    total_mapping_table,
)


ROOT = Path(__file__).resolve().parents[1]


def test_all_25_cells_match_frozen_protocol_exactly() -> None:
    protocol = json.loads(
        (ROOT / "protocols/proposal_recursive_composite_gate_v2.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(protocol["mapping_table"]) == 25
    assert protocol["mapping_table"] == total_mapping_table()
    assert len({(row["left_state"], row["right_state"]) for row in protocol["mapping_table"]}) == 25
    assert set(product(COMPONENT_STATES, repeat=2)) == {
        (row["left_state"], row["right_state"])
        for row in protocol["mapping_table"]
    }


def test_any_component_fail_is_composite_fail() -> None:
    for other in COMPONENT_STATES:
        assert composite_decision("fail", other) == "fail"
        assert composite_decision(other, "fail") == "fail"


def test_partial_or_invalid_instrument_cannot_pass() -> None:
    assert composite_decision("pass", "unavailable") == "not_evaluated"
    assert composite_decision("pass", "invalid") == "not_evaluated"
    assert composite_decision("inconclusive", "unavailable") == "not_evaluated"
    assert composite_decision("inconclusive", "invalid") == "not_evaluated"


def test_v1_observed_cell_carries_both_consequences_without_dominance() -> None:
    record = composite_record(
        [
            {"component_id": "measurement_component", "state": "fail"},
            {"component_id": "prompt_component", "state": "unavailable"},
        ]
    )
    assert record["composite_decision"] == "fail"
    assert record["stop_reasons"] == [
        "measurement_component_fail",
        "prompt_component_unavailable",
    ]
    assert len(record["component_consequences"]) == 2
    assert record["consequence_ranking_applied"] is False
    assert "dominant_sequence_stop" not in record


def test_inconclusive_plus_unavailable_preserves_component_specific_rights() -> None:
    record = composite_record(
        [
            {"component_id": "measured", "state": "inconclusive"},
            {"component_id": "missing", "state": "unavailable"},
        ]
    )
    assert record["composite_decision"] == "not_evaluated"
    rights = {
        item["component_id"]: item["extension_right"]
        for item in record["component_consequences"]
    }
    assert rights["measured"] == "versioned_fresh_disjoint_holdout_for_component_no_pooling"
    assert rights["missing"] == "preregister_missing_component_instrument_and_collect_first_measurement"
