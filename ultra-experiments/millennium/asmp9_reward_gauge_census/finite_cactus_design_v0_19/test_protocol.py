import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def protocol() -> dict:
    return json.loads(
        (HERE / "protocol_v0_19.json").read_text(encoding="utf-8")
    )


def test_gate_registry_is_total() -> None:
    assert protocol()["gate_ids"] == [
        "G0_registration_binding",
        "G1_fresh_registry",
        "G2_exact_cactus_factorization",
        "G3_bridge_irrelevance_and_floor",
        "G4_dp_equals_independent_exhaustive_totals",
        "G5_dp_equals_all_edge_census",
        "G6_nonconcavity_and_comparator_certificates",
        "G7_fresh_comparator_classification",
        "G8_resource_and_scope",
    ]


def test_fresh_epsilons_are_outside_burned_set_without_execution() -> None:
    value = protocol()
    burned = {
        Fraction(text)
        for text in value["development_registry"][
            "burned_epsilon_values"
        ]
    }
    sections = (
        value["factorization_cells"].values(),
        value["dp_cells"].values(),
        value["comparator_cells"].values(),
        (value["global_edge_census"],),
    )
    fresh = [
        Fraction(cell["epsilon"])
        for section in sections
        for cell in section
    ]
    assert fresh
    assert all(epsilon not in burned for epsilon in fresh)


def test_fresh_registry_dimensions_without_scientific_execution() -> None:
    value = protocol()
    direct = value["factorization_cells"]["fresh_figure_3_4"]
    assert sum(direct["cycle_lengths"]) + direct["bridge_count"] == len(
        direct["counts"]
    )
    bridge = value["factorization_cells"][
        "fresh_figure_3_5_bridge"
    ]
    edge_count = sum(bridge["cycle_lengths"]) + bridge["bridge_count"]
    assert len(bridge["counts_a"]) == edge_count
    assert len(bridge["counts_b"]) == edge_count
    assert all(len(labels) == edge_count for labels in bridge["label_vectors"])


def test_claim_boundary_retains_resolution_exclusions() -> None:
    boundary = protocol()["claim_boundary"]
    for phrase in (
        "classical series-product",
        "not claimed as new",
        "arbitrary-graph",
        "adaptive allocation",
        "dependent-response",
        "behavioral reward-identification",
        "general IRL",
        "ASMP-9 resolution",
    ):
        assert phrase in boundary

