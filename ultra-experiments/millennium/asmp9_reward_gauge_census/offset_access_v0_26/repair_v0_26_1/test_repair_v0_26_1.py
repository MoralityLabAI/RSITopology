import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protocol():
    return json.loads((HERE / "protocol_v0_26_1.json").read_text())


def test_all_source_hashes_are_pinned_and_current():
    value = protocol()
    for source in value["source_artifacts"].values():
        assert sha256(REPO / source["path"]) == source["sha256"]


def test_repair_scope_is_explicit():
    value = protocol()
    assert "mechanical re-adjudication" in value["claim_boundary"]
    assert "It may not claim that v0.26 passed" in value["claim_boundary"]
    assert "V0.26 itself passed." in value["structured_claims"]["forbidden"]
    assert "ASMP-9 is resolved." in value["structured_claims"]["forbidden"]


def test_gate_and_prior_art_universes_are_frozen():
    value = protocol()
    assert len(value["gate_ids"]) == len(set(value["gate_ids"])) == 8
    assert len(value["required_prior_art_identifiers"]) == 6
    assert set(value["verdict_map"]) == {"all_gates_pass", "any_gate_fails"}
