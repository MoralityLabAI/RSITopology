from __future__ import annotations

import itertools
import importlib.util
import json
import math
import sys
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_verification as runner  # noqa: E402
from general_graph import (  # noqa: E402
    FULL,
    INTERIOR,
    ZERO,
    full_quotient_availability,
    graph_cycle_rank,
)

verifier_spec = importlib.util.spec_from_file_location(
    "asmp9_general_graph_v017_independent_verifier",
    HERE / "verify_result.py",
)
if verifier_spec is None or verifier_spec.loader is None:
    raise ImportError("unable to load v0.17 independent verifier")
independent = importlib.util.module_from_spec(verifier_spec)
verifier_spec.loader.exec_module(independent)


PROTOCOL = json.loads(
    (HERE / "protocol_v0_17.json").read_text(encoding="utf-8")
)


def test_gate_universe_and_resource_scope_are_frozen() -> None:
    assert PROTOCOL["gate_ids"] == [
        "G0_registration_binding",
        "G1_registry_completeness",
        "G2_residual_rank_identity",
        "G3_representative_invariance",
        "G4_three_state_exactness",
        "G5_endpoint_reduction",
        "G6_bad_support_completeness",
        "G7_primal_dual_exponent_certificates",
        "G8_finite_nonuniform_counterexample",
        "G9_resource_and_scope",
    ]
    assert PROTOCOL["resource_caps"] == {
        "gpu_allowed": False,
        "peak_resident_bytes": 1_073_741_824,
        "wall_seconds": 180,
    }
    assert "not an every-budget optimum theorem" in PROTOCOL[
        "claim_boundary"
    ]
    assert "ASMP-9 resolution" in PROTOCOL["claim_boundary"]


def test_fresh_graphs_are_internally_valid_and_not_burned() -> None:
    fresh = {}
    for name, raw in PROTOCOL["graphs"].items():
        edges = tuple(tuple(edge) for edge in raw["edges"])
        assert graph_cycle_rank(raw["node_count"], edges) == raw[
            "expected_beta1"
        ]
        fresh[name] = runner.canonical_graph_signature(
            raw["node_count"], edges
        )
    burned = {
        name: runner.canonical_graph_signature(
            raw["node_count"], tuple(tuple(edge) for edge in raw["edges"])
        )
        for name, raw in PROTOCOL["burned_graph_registry"].items()
    }
    assert not {
        (fresh_name, burned_name)
        for fresh_name, fresh_value in fresh.items()
        for burned_name, burned_value in burned.items()
        if fresh_value == burned_value
    }


def test_registered_cell_counts_are_complete_without_outcomes() -> None:
    record = runner.registry_record(PROTOCOL)
    assert record["residual_cell_count"] == 6
    assert record["residual_unique_count"] == 6
    assert record["availability_cell_count"] == 3
    assert record["availability_unique_count"] == 3
    assert record["bad_support_cell_count"] == 3
    assert record["bad_support_unique_count"] == 3
    assert record["finite_counterexample_count"] == 1
    finite = PROTOCOL["finite_counterexample"]
    assert math.comb(
        finite["total_trials"] - 1,
        len(finite["uniform_allocation"]) - 1,
    ) == 1716


def test_primal_dual_payloads_are_algebraically_well_formed() -> None:
    for name, certificate in PROTOCOL[
        "bad_support_certificates"
    ].items():
        edge_count = len(PROTOCOL["graphs"][name]["edges"])
        supports = tuple(
            tuple(value) for value in certificate["expected_supports"]
        )
        threshold = runner.parse_fraction(certificate["threshold"])
        weights = tuple(
            runner.parse_fraction(value)
            for value in certificate["primal_weights"]
        )
        dual = tuple(
            (
                tuple(row["support"]),
                runner.parse_fraction(row["mass"]),
            )
            for row in certificate["dual_distribution"]
        )
        assert len(weights) == edge_count
        assert sum(weights, Fraction(0)) == 1
        assert min(
            sum((weights[edge] for edge in support), Fraction(0))
            for support in supports
        ) == threshold
        assert sum((mass for _, mass in dual), Fraction(0)) == 1
        loads = [
            sum(
                (
                    mass
                    for support, mass in dual
                    if edge in support
                ),
                Fraction(0),
            )
            for edge in range(edge_count)
        ]
        assert max(loads) == threshold


def test_independent_residual_algorithm_matches_on_burned_fixture() -> None:
    node_count = 4
    edges = ((0, 2), (0, 1), (1, 2), (0, 3), (3, 2))
    for state in itertools.product(
        (ZERO, INTERIOR, FULL), repeat=len(edges)
    ):
        assert runner.selected_cycle_rank(
            node_count, edges, state
        ) == independent.residual_rank(node_count, edges, state)


def test_independent_probability_replay_matches_on_burned_fixture() -> None:
    node_count = 4
    edges = ((0, 2), (0, 1), (1, 2), (0, 3), (3, 2))
    counts = (1, 2, 1, 2, 1)
    probabilities = (
        Fraction(1, 4),
        Fraction(2, 5),
        Fraction(1, 2),
        Fraction(3, 5),
        Fraction(3, 4),
    )
    implementation = full_quotient_availability(
        node_count, edges, counts, probabilities
    )
    compressed = independent.independent_status_availability(
        node_count, edges, counts, probabilities
    )
    raw = independent.independent_raw_availability(
        node_count, edges, counts, probabilities
    )
    assert implementation == compressed == raw
