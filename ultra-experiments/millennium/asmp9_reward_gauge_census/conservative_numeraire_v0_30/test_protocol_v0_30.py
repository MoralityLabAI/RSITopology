import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def protocol():
    return json.loads((HERE / "protocol_v0_30.json").read_text())


def test_gate_and_claim_universes_are_frozen():
    value = protocol()
    assert len(value["gate_ids"]) == len(set(value["gate_ids"])) == 11
    assert len(value["structured_claims"]["allowed"]) == 7
    assert len(value["structured_claims"]["forbidden"]) == 8
    assert "ASMP-9 is resolved." in value["structured_claims"]["forbidden"]


def test_prior_art_identifiers_are_frozen():
    assert {row["identifier"] for row in protocol()["prior_art"]} == {
        "DOI:10.1016/0022-2496(64)90015-X",
        "Krantz-Luce-Suppes-Tversky-1971",
        "ICML-1999-Ng-Harada-Russell",
        "PMLR:80:1262-1270",
        "PMLR:202:32033-32058",
        "PMLR:235:24808-24828",
        "ASMP-9-v0.28",
        "ASMP-9-v0.29",
    }


def test_fresh_cells_do_not_reuse_burned_dimensions_or_levels():
    fresh = protocol()["fresh_validation"]
    assert fresh["baseline_mdp"]["horizon"] == 4
    assert fresh["baseline_mdp"]["feature_dimension"] == 3
    assert fresh["declared_offsets"] == ["-7/4", 0, "5/3", "13/4"]
    assert fresh["constraint_cell"] == {
        "base_object_count": 5,
        "consequence_count": 6,
        "reference_index": 3,
    }


def test_all_mechanical_failure_channels_are_mandatory():
    controls = protocol()["fresh_validation"]["mechanical_controls"]
    expected = {
        "horizon",
        "action_sets",
        "transitions",
        "features",
    }
    observed = {
        field
        for control in controls
        for field in control["expected_changed_fields"]
    }
    assert observed == expected


def test_semantic_controls_and_approximate_sharpness_are_mandatory():
    fresh = protocol()["fresh_validation"]
    assert set(fresh["semantic_cells"]) == {
        "calibrated",
        "unknown_scale",
        "interaction",
        "incomplete",
    }
    residuals = fresh["approximate_cell"]["residuals"]
    assert any("3/17" in row for row in residuals)
    assert any("-3/17" in row for row in residuals)


def test_claim_boundary_preserves_semantic_no_go():
    forbidden = protocol()["structured_claims"]["forbidden"]
    assert "Mechanical noninterference proves semantic calibration." in forbidden
    assert "A real consequence has stable known cardinal utility." in forbidden
