import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def protocol():
    return json.loads((HERE / "protocol_v0_26.json").read_text(encoding="utf-8"))


def test_gate_universe_and_verdicts_are_total():
    value = protocol()
    assert len(value["gate_ids"]) == 11
    assert len(set(value["gate_ids"])) == 11
    assert set(value["verdict_map"]) == {
        "all_gates_pass",
        "any_substantive_gate_fails",
        "binding_or_resource_gate_fails",
    }


def test_claim_boundary_forbids_scale_and_resolution_overclaims():
    value = protocol()
    forbidden = "\n".join(value["structured_claims"]["forbidden"])
    assert "Ordinary uncalibrated" in forbidden
    assert "ASMP-9 is resolved" in forbidden
    assert "known reward-unit intervention" in value["claim_boundary"]
    assert "no novelty is claimed" in value["claim_boundary"]


def test_fresh_cells_do_not_overlap_burned_cells():
    value = protocol()
    fresh = value["fresh_validation"]
    burned = value["freshness_rule"]["burned_cells"]
    assert not {
        (cell["radius"], cell["tolerance"])
        for cell in fresh["population_cells"]
    } & {
        (cell["radius"], cell["tolerance"])
        for cell in burned["population"]
    }
    assert not {
        (cell["radius"], cell["tolerance"])
        for cell in fresh["robust_cells"]
    } & {
        (cell["radius"], cell["tolerance"])
        for cell in burned["robust"]
    }
    assert not {
        (cell["radius"], cell["maximum_offset"])
        for cell in fresh["restricted_cells"]
    } & {
        (cell["radius"], cell["maximum_offset"])
        for cell in burned["restricted"]
    }


def test_resource_and_statistical_policy_are_frozen():
    value = protocol()
    assert value["resource_caps"] == {
        "gpu_allowed": False,
        "peak_resident_bytes": 1073741824,
        "wall_seconds": 180,
    }
    assert "no random response outcomes" in value["statistical_policy"]
