import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def protocol():
    return json.loads((HERE / "protocol_v0_27.json").read_text())


def test_gate_and_claim_universes_are_total():
    value = protocol()
    assert len(value["gate_ids"]) == len(set(value["gate_ids"])) == 9
    assert len(value["structured_claims"]["allowed"]) == 5
    assert len(value["structured_claims"]["forbidden"]) == 6
    assert "ASMP-9 is resolved." in value["structured_claims"]["forbidden"]


def test_prior_art_is_structural_and_complete():
    identifiers = {row["identifier"] for row in protocol()["prior_art"]}
    assert identifiers == {
        "ASMP-9-v0.11-v0.12",
        "ASMP-9-v0.26.2",
        "doi:10.1007/BF02293919",
        "doi:10.1007/s10107-010-0419-x",
        "doi:10.1093/biomet/asm029",
    }


def test_fresh_cells_are_distinct_from_burned_development_fixtures():
    names = {
        cell["name"] for cell in protocol()["fresh_validation"]["graph_cells"]
    }
    assert names == {
        "fresh_hexagon_with_leaf",
        "fresh_complete_2_by_3",
        "fresh_disconnected_square_and_path",
        "fresh_bipartite_chain",
    }
    assert len(names) == 4


def test_negative_claims_cover_liveness_and_access():
    forbidden = protocol()["structured_claims"]["forbidden"]
    assert (
        "A tree design provides empirical evidence for context-only midpoint factorization."
        in forbidden
    )
    assert (
        "Every environment intervention implements a known cardinal reward offset."
        in forbidden
    )

