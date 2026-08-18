import json
from fractions import Fraction
from pathlib import Path

from block_factorization import PreparedGraph
from run_verification_v0_20 import (
    brute_cycle_blocks,
    design_comparison,
    exact_availability,
    product_availability,
    product_worst_endpoint,
    verdict_for_gates,
    worst_endpoint,
)


HERE = Path(__file__).resolve().parent

TWO_DIAMONDS = (
    (0, 1),
    (1, 2),
    (2, 0),
    (0, 3),
    (3, 2),
    (0, 4),
    (4, 5),
    (5, 0),
    (0, 6),
    (6, 5),
)

TWO_TRIANGLES = (
    (0, 1),
    (1, 2),
    (2, 0),
    (0, 3),
    (3, 4),
    (4, 0),
)


def load_protocol() -> dict:
    return json.loads(
        (HERE / "protocol_v0_20.json").read_text(
            encoding="utf-8"
        )
    )


def test_protocol_has_total_gate_universe_and_fresh_full_graphs() -> None:
    protocol = load_protocol()
    assert protocol["protocol_id"] == (
        "ASMP-9-BLOCK-FACTORIZATION-v0.20"
    )
    assert len(protocol["gate_ids"]) == 10
    assert len(set(protocol["gate_ids"])) == 10
    signatures = set()
    for raw in protocol["graphs"].values():
        assert raw["node_count"] >= 7
        signature = (
            raw["node_count"],
            tuple(tuple(edge) for edge in raw["edges"]),
        )
        assert signature not in signatures
        signatures.add(signature)


def test_expected_partitions_are_structurally_well_formed() -> None:
    protocol = load_protocol()
    for raw in protocol["graphs"].values():
        prepared = PreparedGraph.build(
            raw["node_count"],
            tuple(tuple(edge) for edge in raw["edges"]),
        )
        expected = tuple(
            tuple(block) for block in raw["expected_blocks"]
        )
        assert prepared.blocks == expected
        assert brute_cycle_blocks(
            prepared.node_count, prepared.edges
        ) == expected


def test_burned_exact_fixed_label_product() -> None:
    prepared = PreparedGraph.build(7, TWO_DIAMONDS)
    counts = (1, 2, 3, 2, 1, 2, 1, 3, 2, 1)
    labels = (0, 1, 0, 1, 1, 0, 0, 1, 0, 1)
    epsilon = Fraction(3, 11)
    direct = exact_availability(
        prepared, counts, labels, epsilon
    )
    product, _ = product_availability(
        prepared, counts, labels, epsilon
    )
    assert direct == product


def test_burned_rectangular_minimum_product() -> None:
    prepared = PreparedGraph.build(5, TWO_TRIANGLES)
    counts = (1, 2, 1, 2, 1, 2)
    epsilon = Fraction(3, 11)
    direct, _ = worst_endpoint(prepared, counts, epsilon)
    product, _ = product_worst_endpoint(
        prepared, counts, epsilon
    )
    assert direct == product


def test_burned_bellman_matches_full_edge_census() -> None:
    prepared = PreparedGraph.build(5, TWO_TRIANGLES)
    row = design_comparison(
        prepared, total_budget=7, epsilon=Fraction(3, 11)
    )
    assert row["allocation_count"] == 6
    assert row["exact_match"]


def test_verdict_mapping_has_no_positive_outcome_assumption() -> None:
    gate_ids = load_protocol()["gate_ids"]
    passing = {gate_id: True for gate_id in gate_ids}
    assert verdict_for_gates(passing) == (
        "finite_block_factorization_established_in_frozen_model_v0_20"
    )
    for failed_gate in gate_ids:
        values = passing | {failed_gate: False}
        assert verdict_for_gates(values) == (
            "finite_block_factorization_not_established_v0_20"
        )
