from __future__ import annotations

import json
from pathlib import Path

from rsi_topology.qwen_percolation_reanalysis import qwen_edge_class


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "protocols" / "qwen08_percolation_reanalysis_v0_1.json"


def test_edge_classification_is_frozen_and_exhaustive():
    assert qwen_edge_class("site:r1:precision:00") == "checkpoint"
    assert qwen_edge_class("site:r1:base:shard-00-01") == "context"


def test_protocol_preserves_retrospective_claim_boundary():
    value = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert value["epistemic_status"] == "retrospective_engineering_evidence"
    assert value["new_invariant_levels"] is False
    assert "no ordering" in value["threshold_ordering"]["not_assumed"]


def test_protocol_freezes_the_exact_four_site_universe():
    value = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert value["site_universe"] == [
        "model.layers.11",
        "model.layers.15",
        "model.layers.19",
        "model.layers.23",
    ]
