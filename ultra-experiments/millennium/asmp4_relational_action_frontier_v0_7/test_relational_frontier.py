"""Focused tests for the ASMP-4 v0.7 relational frontier."""

from __future__ import annotations

import json
from pathlib import Path

from relational_frontier import (
    COARSE_PARTITION,
    EXPECTED_ADAPTIVE_FRONTIERS,
    RAW_PARTITION,
    adaptive_tree_census,
    asymptotic_frontier_report,
    continuous_embedding_report,
    local_scheme_census,
    minimal_tradeoff_census,
    moment_converse_certificate,
    prefix_and_randomness_report,
    randomized_kernel_census,
    relational_frontier_report,
    safe_assignments,
    set_partitions,
    three_registry_fork_report,
    verification_gates,
)
from verify_relational_frontier import (
    document_sentinels,
    independent_adaptive_census,
    independent_embedding,
    independent_local_census,
    independent_minimality_census,
    independent_partitions,
    independent_randomized_kernel_census,
    independent_registry_fork,
    predecessor_firewall,
)

HERE = Path(__file__).resolve().parent


def test_partition_generators_reproduce_bell_counts() -> None:
    assert [len(set_partitions(size)) for size in range(1, 5)] == [1, 2, 5, 15]
    assert [len(independent_partitions(size)) for size in range(1, 5)] == [
        1,
        2,
        5,
        15,
    ]


def test_registered_local_schemes_are_exhaustive() -> None:
    report = local_scheme_census()
    assert report["pass"]
    assert len(safe_assignments(COARSE_PARTITION)) == 1
    assert len(safe_assignments(RAW_PARTITION)) == 4
    assert report["nondominated_count_pairs"] == [[3, 3], [4, 2]]


def test_independent_local_scheme_representation_agrees() -> None:
    report = independent_local_census()
    assert report["pass"]
    assert report["nondominated"] == [[3, 3], [4, 2]]


def test_four_modes_are_exhaustively_minimal() -> None:
    report = minimal_tradeoff_census()
    assert report["pass"]
    assert report["total_relations"] == 2800
    assert report["total_feasible_cells"] == 24221
    assert report["strict_tradeoff_partition_pairs"] == 72
    assert report["strict_tradeoff_signature_histogram"] == {"(3,3)->(4,2)": 72}


def test_independent_relation_sets_reproduce_minimality_census() -> None:
    report = independent_minimality_census()
    assert report["pass"]
    assert [row["tradeoff_relations"] for row in report["rows"]] == [0, 0, 0, 72]


def test_adaptive_tree_frontier_is_exact_through_horizon_three() -> None:
    report = adaptive_tree_census()
    assert report["pass"]
    assert [row["candidate_trees"] for row in report["rows"]] == [5, 72, 84672]
    assert [row["undominated_support_states"] for row in report["rows"]] == [
        2,
        12,
        1872,
    ]
    assert (
        tuple(map(tuple, report["rows"][-1]["count_frontier"]))
        == (EXPECTED_ADAPTIVE_FRONTIERS[3])
    )


def test_explicit_word_language_verifier_reproduces_adaptive_frontier() -> None:
    report = independent_adaptive_census()
    assert report["pass"]
    assert report["rows"][-1]["candidates"] == 84672
    assert report["rows"][-1]["states"] == 1872


def test_concave_moment_certificate_closes_all_horizons() -> None:
    report = moment_converse_certificate()
    assert report["pass"]
    assert [row["moment_factor"] for row in report["local_rows"]].count("3") == 2
    assert [row["moment_factor"] for row in report["local_rows"]].count("7/2") == 3
    assert report["finite_inequalities"] == [
        "R_T >= 3^T",
        "W_T >= 2^T",
        "R_T^theta W_T^(1-theta) >= 3^T",
    ]


def test_asymptotic_region_is_genuinely_nonrectangular() -> None:
    report = asymptotic_frontier_report()
    assert report["pass"]
    assert report["nonrectangular"]
    assert report["lower_corner_excluded"]
    assert report["pareto_endpoints"] == [
        ["log2(3)", "log2(3)"],
        ["2", "1"],
    ]


def test_same_plant_has_three_exact_registration_regions() -> None:
    report = three_registry_fork_report()
    assert report["pass"]
    assert report["computed_count_pair"] == [2, 2]
    assert report["raw_count_pair"] == [4, 2]
    assert report["regions_pairwise_distinct"]
    assert independent_registry_fork()["pass"]


def test_rational_embedding_realizes_exact_relation() -> None:
    report = continuous_embedding_report()
    assert report["pass"]
    assert report["normal_multiplier"] == "3/2"
    assert report["safe_paths"] == 7776
    assert len(report["safe_pairs"]) == 6
    assert len(report["unsafe_pairs"]) == 6
    assert independent_embedding()["pass"]


def test_prefix_and_independent_seed_robustness() -> None:
    report = prefix_and_randomness_report()
    assert report["pass"]
    assert report["checked_seed_mixtures"] == 152
    assert len(report["prefix_rows"]) == 44


def test_randomized_observation_kernels_derandomize_exhaustively() -> None:
    report = randomized_kernel_census()
    assert report["pass"]
    assert report["totals"] == {
        "support_kernels": 53108,
        "surjective_support_kernels": 43744,
        "zero_error_feasible": 994,
        "genuinely_randomized_feasible": 950,
        "deterministic_sensor_maps_checked": 4280,
        "controller_support_kernels_checked": 3058,
    }
    assert report["derandomization_failures"] == []


def test_explicit_set_kernel_verifier_reproduces_derandomization() -> None:
    report = independent_randomized_kernel_census()
    assert report["pass"]
    assert report["totals"] == {
        "support_kernels": 53108,
        "surjective": 43744,
        "feasible": 994,
        "randomized": 950,
        "sensor_maps": 4280,
        "controller_kernels": 3058,
    }
    assert report["failures"] == 0


def test_frozen_claim_matches_exact_counts() -> None:
    claim = json.loads(
        (HERE / "relational_claim_v0_7.json").read_text(encoding="utf-8")
    )
    assert claim["minimality_census"] == {
        "relations_through_four_modes": 2800,
        "feasible_relation_partition_cells": 24221,
        "strict_tradeoff_relations_at_four_modes": 72,
        "strict_tradeoff_partition_pairs": 72,
        "first_tradeoff_signature": "(3,3)->(4,2)",
    }
    assert claim["exact_closed_region"]["nonrectangular"] is True
    assert claim["randomized_kernel_census"]["derandomization_failures"] == 0


def test_documents_and_predecessor_firewall_are_present() -> None:
    assert document_sentinels()["pass"]
    assert predecessor_firewall()["pass"]


def test_complete_payload_passes_every_named_gate() -> None:
    report = relational_frontier_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
