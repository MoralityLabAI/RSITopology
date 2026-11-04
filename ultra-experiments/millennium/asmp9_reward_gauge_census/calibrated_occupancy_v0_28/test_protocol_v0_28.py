import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def protocol():
    return json.loads((HERE / "protocol_v0_28.json").read_text())


def test_gate_and_claim_universes_are_frozen():
    value = protocol()
    assert len(value["gate_ids"]) == len(set(value["gate_ids"])) == 10
    assert len(value["structured_claims"]["allowed"]) == 6
    assert len(value["structured_claims"]["forbidden"]) == 7
    assert "ASMP-9 is resolved." in value["structured_claims"]["forbidden"]


def test_prior_art_identifiers_are_structural():
    assert {row["identifier"] for row in protocol()["prior_art"]} == {
        "ASMP-9-v0.10",
        "ASMP-9-v0.26-v0.27",
        "ICML-1999-Ng-Harada-Russell",
        "NeurIPS-2021-671f0311",
        "PMLR:139:5496-5505",
        "PMLR:202:32033-32058",
        "PMLR:235:24808-24828",
        "doi:10.1093/biomet/asm029",
    }


def test_fresh_dimensions_differ_from_burned_fixtures():
    fresh = protocol()["fresh_validation"]
    assert [len(cell["reward"]) for cell in fresh["homogeneous_cells"]] == [
        4,
        5,
    ]
    assert [cell["adaptive_depth"] for cell in fresh["homogeneous_cells"]] == [
        7,
        8,
    ]
    assert fresh["calibrated_numeraire_cell"]["tolerance"] == "5/2048"


def test_claim_boundary_preserves_scale_target_distinction():
    forbidden = protocol()["structured_claims"]["forbidden"]
    assert (
        "Positive reward scale must be identified for every downstream decision target."
        in forbidden
    )
    assert (
        "Money, tokens, or any concrete consequence has known stable cardinal utility."
        in forbidden
    )
