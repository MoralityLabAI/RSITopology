import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def protocol() -> dict:
    return json.loads(
        (HERE / "protocol_v0_19_1.json").read_text(encoding="utf-8")
    )


def test_amendment_gate_registry_is_total():
    assert protocol()["gate_ids"] == [
        "G0_registration_binding",
        "G1_fresh_registry",
        "G2_cached_engine_reproduces_burned_v0_19",
        "G3_exact_cactus_factorization",
        "G4_bridge_irrelevance_and_floor",
        "G5_dp_equals_independent_exhaustive_totals",
        "G6_dp_equals_all_edge_census",
        "G7_nonconcavity_and_comparator_certificates",
        "G8_fresh_comparator_classification",
        "G9_resource_and_scope",
    ]


def test_amendment_fresh_epsilons_are_outside_all_burned_values():
    value = protocol()
    burned = {
        Fraction(text)
        for text in value["development_registry"][
            "burned_epsilon_values"
        ]
    }
    cells = [
        *value["factorization_cells"].values(),
        *value["dp_cells"].values(),
        *value["comparator_cells"].values(),
        value["global_edge_census"],
    ]
    assert all(Fraction(cell["epsilon"]) not in burned for cell in cells)


def test_amendment_dimensions_without_scientific_execution():
    value = protocol()
    for raw in value["factorization_cells"].values():
        edge_count = sum(raw["cycle_lengths"]) + raw["bridge_count"]
        if "counts" in raw:
            assert len(raw["counts"]) == edge_count
        else:
            assert len(raw["counts_a"]) == edge_count
            assert len(raw["counts_b"]) == edge_count
            assert all(
                len(labels) == edge_count
                for labels in raw["label_vectors"]
            )


def test_amendment_claim_boundary_retains_scope():
    boundary = protocol()["claim_boundary"]
    for phrase in (
        "computation-only successor",
        "wholly new scientific cells",
        "not claimed as new",
        "arbitrary-graph",
        "adaptive allocation",
        "dependent-response",
        "behavioral reward-identification",
        "ASMP-9 resolution",
    ):
        assert phrase in boundary
