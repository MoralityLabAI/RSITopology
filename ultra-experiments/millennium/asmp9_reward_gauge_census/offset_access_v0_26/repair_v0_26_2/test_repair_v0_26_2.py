import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protocol():
    return json.loads((HERE / "protocol_v0_26_2.json").read_text())


def test_source_hashes_and_failure_history_are_bound():
    value = protocol()
    for source in value["source_artifacts"].values():
        assert sha256(REPO / source["path"]) == source["sha256"]
    assert "failed_repair_execution_note" in value["source_artifacts"]
    assert "failed_repair_registration" in value["source_artifacts"]


def test_scope_forbids_retroactive_success():
    value = protocol()
    forbidden = value["structured_claims"]["forbidden"]
    assert "V0.26 itself passed." in forbidden
    assert "V0.26.1 produced an adjudication result." in forbidden
    assert "V0.26.2 generated fresh scientific evidence." in forbidden
    assert "ASMP-9 is resolved." in forbidden


def test_corrected_memory_helper_executes():
    path = HERE / "adjudicate_v0_26_2.py"
    spec = importlib.util.spec_from_file_location("repair", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.corrected_peak_resident_bytes() > 0
