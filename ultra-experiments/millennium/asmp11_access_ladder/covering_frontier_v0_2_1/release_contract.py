"""Frozen release contract for ASMP-11 source hardening v0.2.1.2."""

from __future__ import annotations


RELEASE_VERSION = "v0.2.1.2"
RELEASE_ID = "asmp11.intermediate_width_crossover.v0.2.1.2"
MATHEMATICAL_PROTOCOL_ID = "asmp11.intermediate_width_crossover.v0.2.1"
REGISTRATION_FILENAME = "registration_v0_2_1_2.json"
ARTIFACT_DIRECTORY = "artifacts_v0_2_1_2"
REGISTRATION_SCHEMA = "asmp11_intermediate_crossover_registration_v0_2_1_2"
RESULT_SCHEMA = "asmp11_intermediate_crossover_result_layer_v0_2_1_2"
RELIABILITY_SCHEMA = "asmp11_intermediate_crossover_reliability_layer_v0_2_1_2"
CLAIM_SCHEMA = "asmp11_intermediate_crossover_claim_layer_v0_2_1_2"
OPERATION_SCHEMA = "asmp11_intermediate_crossover_operation_layer_v0_2_1_2"
RECEIPT_SCHEMA = "asmp11_intermediate_crossover_receipt_v0_2_1_2"
VERIFICATION_SCHEMA = "asmp11_intermediate_crossover_independent_verification_v0_2_1_2"
SYNTHESIS_SCHEMA = "asmp11_intermediate_crossover_synthesis_receipt_v0_2_1_2"

CLAIM_BOUNDARY = (
    "Finite bounds-aware crossover surface for the transparent parity oracle only."
)

FROZEN_CLAIM_GRID = {
    "protocol_id": MATHEMATICAL_PROTOCOL_ID,
    "release_id": RELEASE_ID,
    "status": "registration_required_before_execution",
    "dimensions": [13, 15, 17],
    "degrees": [3, 4],
    "width_rule": {
        "3": "every integer s with 3 < s < n-3",
        "4": "every integer s with 4 < s < n-2",
    },
    "flip_rates": ["1/20", "3/20", "1/4"],
    "alpha": "1/20",
    "target_power": "9/10",
    "sample_cap": 4096,
    "resource_policy": {
        "max_greedy_rounds_per_cell": 4096,
        "max_candidate_blocks_per_cell": 30000,
        "hard_wall_seconds_per_cell": 15,
        "max_total_wall_seconds": 900,
        "max_ram_bytes": 4294967296,
        "execution": "sequential_cpu_only",
    },
    "expected_counts": {
        "covering_cells": 48,
        "cost_cells": 144,
        "brackets": 18,
        "metric_records_per_cost_cell": 5,
        "robustness_probes_per_cost_cell": 4,
    },
}

BOUND_SOURCES = (
    "README.md",
    "PROTOCOL_v0_2_1.md",
    "SERIALIZATION_REPAIR_v0_2_1_1.md",
    "SOURCE_HARDENING_v0_2_1_2.md",
    "experiment_v0_2_1.json",
    "prior_anchor_v0_2.json",
    "release_contract.py",
    "crossover_frontier.py",
    "run.py",
    "build_registration.py",
    "verify_result.py",
    "synthesize_receipt.py",
    "test_crossover_frontier.py",
)

PRIMARY_OUTPUTS = frozenset(
    {
        "covering_cells.jsonl",
        "cost_cells.jsonl",
        "covering_checkpoint.json",
        "cost_checkpoint.json",
        "result_layer.json",
        "reliability_layer.json",
        "claim_layer.json",
        "operation_layer.json",
    }
)

DIAGNOSTIC_PROBE_ID = "D1_primary_bound_interval_replay"
ROBUSTNESS_PROBE_IDS = (
    "P2_query_count_only",
    "P3_stricter_familywise_error",
    "P4_stricter_power",
    "P5_exact_independent_fwer",
)
ALL_PROBE_IDS = (DIAGNOSTIC_PROBE_ID, *ROBUSTNESS_PROBE_IDS)

REGISTRATION_KEYS = frozenset(
    {
        "schema_version",
        "release_id",
        "protocol_id",
        "registered_at_utc",
        "status",
        "proposed_asmp_id",
        "source_commit",
        "source_hashes",
        "source_git_blob_oids",
        "manifest_path",
        "manifest_sha256",
        "prior_anchor_path",
        "prior_anchor_sha256",
        "claim_grid",
        "claim_boundary",
        "output_policy",
    }
)

RECEIPT_KEYS = frozenset(
    {
        "schema_version",
        "release_id",
        "registration_sha256",
        "manifest_sha256",
        "prior_anchor_sha256",
        "outputs",
        "verdict",
    }
)

VERIFICATION_FILENAME = "independent_verification_v0_2_1_2.json"
SYNTHESIS_FILENAME = "synthesis_receipt_v0_2_1_2.json"
PRIMARY_GATE_IDS = frozenset(
    {
        "B0_binding",
        "B1_witness_validity",
        "B2_lower_bound_replay",
        "B3_probability_exactness",
        "B4_total_classification",
        "B5_minimum_width",
        "B6_resource_honesty_ram_unmeasured",
        "B7_metric_probe_completeness",
    }
)
VERIFICATION_KEYS = frozenset(
    {
        "schema_version",
        "release_id",
        "verified",
        "gates",
        "registration_sha256",
        "receipt_sha256",
        "primary_outputs",
        "counts",
        "metric_robustness",
        "resource_assessment",
        "claim_boundary",
    }
)
VERIFICATION_GATE_IDS = frozenset(
    {
        "V0_source_registration_binding",
        "V1_receipt_output_link_closure",
        "V2_cover_witnesses_and_lower_bounds",
        "V3_exact_cost_classification",
        "V4_full_metric_probe_replay",
        "V5_minimum_width_brackets",
        "V6_layer_and_metric_firewall",
        "V7_exact_registered_cartesian_grid",
        "V8_primary_gates_exactly_recomputed",
        "V9_operation_and_resource_consistency",
        "V10_prior_anchor_independent_replay",
        "V11_checkpoint_raw_row_consistency",
        "V12_claim_operation_consistency",
    }
)
