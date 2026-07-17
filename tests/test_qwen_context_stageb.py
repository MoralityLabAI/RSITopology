from __future__ import annotations

import json
from pathlib import Path

import pytest

from rsi_topology.qwen_context_stageb import (
    _cp_upper,
    generate_manifest,
    load_protocol,
    precision_comparison,
    validate_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "protocols" / "qwen08_context_stageb_v0_1.json"
MANIFEST = ROOT / "protocols" / "qwen08_context_stageb_prompt_manifest_v0_1.json"


def test_stageb_manifest_is_deterministic_fresh_and_context_restricted():
    protocol = load_protocol(PROTOCOL)
    observed = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert generate_manifest(protocol_path=PROTOCOL) == observed
    validate_manifest(observed, protocol_path=PROTOCOL)
    assert observed["families"] == ["graph_reachability"]
    assert observed["prompt_count"] == 2304
    assert {row["context_neighborhood"] for row in observed["rows"]} == {
        "old_shard_02",
        "old_shard_03",
    }
    assert protocol["new_invariant_levels"] is False


def test_stageb_clopper_pearson_gate_has_registered_zero_failure_margin():
    assert _cp_upper(0, 256, 0.05) < 0.05
    assert _cp_upper(13, 256, 0.05) > 0.05
    with pytest.raises(ValueError):
        _cp_upper(2, 1, 0.05)


def test_precision_control_requires_common_loops_signs_and_coherent_phases():
    loop = {"loop_id": "loop-0", "admitted": True, "det_h": 1.0}
    geometry = {
        "site_results": [
            {
                "site": "model.layers.19",
                "phase_at_registered_floor": {"phase": "coherent"},
                "loops": [loop],
            }
        ]
    }
    passed = precision_comparison(
        geometry, geometry, site="model.layers.19"
    )
    assert passed["passed"] is True
    reversed_geometry = json.loads(json.dumps(geometry))
    reversed_geometry["site_results"][0]["loops"][0]["det_h"] = -1.0
    failed = precision_comparison(
        geometry, reversed_geometry, site="model.layers.19"
    )
    assert failed["passed"] is False
    assert failed["determinant_sign_agreement"] is False

