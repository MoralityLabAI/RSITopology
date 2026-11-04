import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def protocol():
    return json.loads((HERE / "protocol_v0_29.json").read_text())


def test_gate_and_claim_universes_are_frozen():
    value = protocol()
    assert len(value["gate_ids"]) == len(set(value["gate_ids"])) == 10
    assert len(value["structured_claims"]["allowed"]) == 6
    assert len(value["structured_claims"]["forbidden"]) == 7
    assert "ASMP-9 is resolved." in value["structured_claims"]["forbidden"]


def test_prior_art_identifiers_are_frozen():
    assert {row["identifier"] for row in protocol()["prior_art"]} == {
        "ASMP-9-v0.28",
        "ICML-2004-Abbeel-Ng",
        "PMLR:139:5496-5505",
        "PMLR:162:4618-4629",
        "PMLR:202:32033-32058",
        "PMLR:235:60957-61020",
    }


def test_fresh_values_do_not_reuse_burned_sharpness_or_scale_cells():
    fresh = protocol()["fresh_validation"]
    assert fresh["sharp_cell"]["magnitude"] == "11/13"
    assert fresh["scale_cell"]["scale_factors"] == ["1/5", "7/3"]
    assert fresh["scale_cell"]["fixed_regret_threshold"] == 4


def test_invalid_gauge_and_margin_equality_are_mandatory():
    fresh = protocol()["fresh_validation"]
    assert sum(fresh["invalid_gauge_cell"]["policy_occupancies"][0]) != sum(
        fresh["invalid_gauge_cell"]["policy_occupancies"][1]
    )
    assert fresh["equality_margin_cell"]["true_reward"] == [0, 0]


def test_claim_boundary_keeps_safety_reduction_narrow():
    forbidden = protocol()["structured_claims"]["forbidden"]
    assert "Small reward regret proves broad AI safety." in forbidden
    assert "The registered policy family contains a safe policy." in forbidden
