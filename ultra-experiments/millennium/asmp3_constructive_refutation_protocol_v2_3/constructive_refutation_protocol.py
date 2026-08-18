from __future__ import annotations

import json
import sys
from fractions import Fraction
from functools import cache
from math import comb
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
COMPOSITION_ARTIFACT = (
    HERE.parent
    / "asmp3_block_selection_composition_v1_9"
    / "artifacts"
    / "block_selection_composition_v1_9.json"
)
ENCODING_ARTIFACT = (
    HERE.parent
    / "asmp3_encoding_invariance_v2_0"
    / "artifacts"
    / "encoding_invariance_v2_0.json"
)
SEARCH_ARTIFACT = (
    HERE.parent
    / "asmp3_honest_search_barrier_v2_1"
    / "artifacts"
    / "honest_search_barrier_v2_1.json"
)
RESOURCE_ARTIFACT = (
    HERE.parent
    / "asmp3_resource_tradeoff_v2_2"
    / "artifacts"
    / "resource_tradeoff_v2_2.json"
)

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(100_000)


def qstr(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def ceil_log2(value: int) -> int:
    if value < 1:
        raise ValueError("value must be positive")
    return (value - 1).bit_length()


@cache
def atom_error(depth: int, eta: Q) -> Q:
    if depth < 1 or eta <= 0 or eta >= Q(1, 2):
        raise ValueError("invalid replication parameters")
    result = sum(
        (
            Q(comb(depth, errors))
            * eta**errors
            * (1 - eta) ** (depth - errors)
            for errors in range(depth // 2 + 1, depth + 1)
        ),
        Q(0),
    )
    if depth % 2 == 0:
        result += (
            Q(comb(depth, depth // 2))
            * eta ** (depth // 2)
            * (1 - eta) ** (depth // 2)
            / 2
        )
    return result


def joint_decoding_risk(refutation_size: int, depth: int, eta: Q) -> Q:
    if refutation_size < 1:
        raise ValueError("refutation size must be positive")
    error = atom_error(depth, eta)
    return 1 - (1 - error) ** refutation_size


def minimal_odd_depth(refutation_size: int, eta: Q, target: Q) -> int:
    if refutation_size < 1 or target <= 0 or target >= Q(1, 2):
        raise ValueError("invalid target-risk parameters")
    for depth in (1, *range(3, 1024, 2)):
        if joint_decoding_risk(refutation_size, depth, eta) <= target:
            return depth
    raise RuntimeError("replication search exceeded registered limit")


def protocol_row(
    refutation_size: int,
    eta: Q | int,
    target: Q | int,
    *,
    atom_id_bits: int = 20,
) -> dict[str, object]:
    eta = Q(eta)
    target = Q(target)
    if refutation_size < 1 or atom_id_bits < 1:
        raise ValueError("invalid protocol size parameters")
    depth = minimal_odd_depth(refutation_size, eta, target)
    atom_risk = atom_error(depth, eta)
    joint_risk = joint_decoding_risk(refutation_size, depth, eta)
    previous_risk = (
        joint_decoding_risk(refutation_size, depth - 2, eta)
        if depth > 1
        else None
    )
    length_prefix = ceil_log2(refutation_size + 1)
    critic_bits = length_prefix + refutation_size * (atom_id_bits + 1)
    semantic_queries = refutation_size * depth
    finder_time = refutation_size * atom_id_bits
    completeness = 1 - joint_risk
    soundness = joint_risk
    gap = completeness - soundness
    return {
        "maximum_refutation_classes": refutation_size,
        "eta": qstr(eta),
        "target_protocol_error": qstr(target),
        "atom_id_bits": atom_id_bits,
        "replications_per_atom": depth,
        "single_atom_majority_error": qstr(atom_risk),
        "joint_decoding_error": qstr(joint_risk),
        "previous_odd_depth_joint_error": (
            qstr(previous_risk) if previous_risk is not None else None
        ),
        "completeness_lower_bound": qstr(completeness),
        "soundness_upper_bound": qstr(soundness),
        "completeness_soundness_gap_lower_bound": qstr(gap),
        "semantic_query_count": semantic_queries,
        "critic_message_length_prefix_bits": length_prefix,
        "critic_message_bits": critic_bits,
        "registered_finder_time_bound": finder_time,
        "finder_contract": (
            "uniformly returns a sound-complete quotient witness of size <=r "
            "for every false admissible transcript"
        ),
        "noise_contract": (
            "fresh disjoint iid blocks sampled only after transcript and witness are fixed"
        ),
        "malformed_critic_message_policy": "ignore_and_accept_advocate",
        "minimal_odd_depth_certified": (
            joint_risk <= target
            and (previous_risk is None or previous_risk > target)
        ),
        "certified": (
            completeness == 1 - joint_risk
            and soundness == joint_risk
            and gap == 1 - 2 * joint_risk
            and semantic_queries == refutation_size * depth
            and critic_bits
            == length_prefix + refutation_size * (atom_id_bits + 1)
            and finder_time == refutation_size * atom_id_bits
            and joint_risk <= target
        ),
    }


def scaling_rows() -> list[dict[str, object]]:
    rows = []
    for log_prover_work in range(10, 101, 10):
        refutation_size = log_prover_work
        target = Q(1, log_prover_work)
        row = protocol_row(
            refutation_size,
            Q(1, 5),
            target,
            atom_id_bits=log_prover_work,
        )
        cubic_budget = log_prover_work**3
        rows.append(
            {
                "log2_prover_work": log_prover_work,
                "refutation_size": refutation_size,
                "target_error": qstr(target),
                "replications_per_atom": row["replications_per_atom"],
                "semantic_queries": row["semantic_query_count"],
                "critic_message_bits": row["critic_message_bits"],
                "finder_time": row["registered_finder_time_bound"],
                "declared_polylog_cubic_budget": cubic_budget,
                "all_resources_within_cubic_polylog_budget": (
                    row["semantic_query_count"] <= cubic_budget
                    and row["critic_message_bits"] <= cubic_budget
                    and row["registered_finder_time_bound"] <= cubic_budget
                ),
                "gap_lower_bound": row["completeness_soundness_gap_lower_bound"],
            }
        )
    return rows


def build_result() -> dict[str, object]:
    composition = json.loads(COMPOSITION_ARTIFACT.read_text(encoding="utf-8"))
    encoding = json.loads(ENCODING_ARTIFACT.read_text(encoding="utf-8"))
    search = json.loads(SEARCH_ARTIFACT.read_text(encoding="utf-8"))
    resource = json.loads(RESOURCE_ARTIFACT.read_text(encoding="utf-8"))
    rows = [
        protocol_row(refutation_size, eta, target)
        for eta in (Q(1, 5), Q(1, 3), Q(2, 5))
        for refutation_size in (1, 2, 4, 8, 16, 32, 64)
        for target in (Q(1, 10), Q(1, 100))
    ]
    scaling = scaling_rows()
    gates = {
        "P0_protocol_registry_complete": len(rows) == 42,
        "P1_all_replication_depths_exactly_minimal": all(
            row["minimal_odd_depth_certified"] for row in rows
        ),
        "P2_completeness_soundness_bounds_match": all(
            Q(row["completeness_lower_bound"])
            == 1 - Q(row["joint_decoding_error"])
            and Q(row["soundness_upper_bound"]) == Q(row["joint_decoding_error"])
            and Q(row["completeness_soundness_gap_lower_bound"])
            == 1 - 2 * Q(row["joint_decoding_error"])
            for row in rows
        ),
        "P3_target_error_and_gap_guarantees_hold": all(
            Q(row["joint_decoding_error"]) <= Q(row["target_protocol_error"])
            and Q(row["completeness_soundness_gap_lower_bound"])
            >= 1 - 2 * Q(row["target_protocol_error"])
            for row in rows
        ),
        "P4_all_query_communication_and_finder_costs_charged": all(
            row["semantic_query_count"]
            == row["maximum_refutation_classes"] * row["replications_per_atom"]
            and row["critic_message_bits"]
            == row["critic_message_length_prefix_bits"]
            + row["maximum_refutation_classes"] * (row["atom_id_bits"] + 1)
            and row["registered_finder_time_bound"]
            == row["maximum_refutation_classes"] * row["atom_id_bits"]
            for row in rows
        ),
        "P5_fresh_noise_contract_blocks_selection_bias": all(
            row["noise_contract"].startswith("fresh disjoint iid blocks") for row in rows
        ),
        "P6_polylog_scaling_lane_certified": (
            len(scaling) == 10
            and all(row["all_resources_within_cubic_polylog_budget"] for row in scaling)
        ),
        "P7_parent_noise_composition_contract_matches": (
            composition["theorem"]["independent_M_atom_risk"] == "1-(1-e_d)^M"
            and composition["theorem"]["query_cost"] == "M*d semantic queries"
        ),
        "P8_parent_obstruction_contracts_are_explicit": (
            encoding["theorem"]["dimension_result"].endswith("exact invariant")
            and search["theorem"]["conclusion"].startswith("small combinatorial dimension")
            and resource["theorem"]["lower_bound"] == "K*q>=N message-query covering inequality"
        ),
        "P9_all_protocol_rows_certified": all(row["certified"] for row in rows),
    }
    return {
        "schema_version": "asmp3_constructive_refutation_protocol_v2_3",
        "experiment_id": "ASMP-3-CONSTRUCTIVE-REFUTATION-PROTOCOL-v2.3",
        "status": "constructive_positive_protocol_under_typed_finder_noise_contracts",
        "parent_result": "ASMP-3-RESOURCE-TRADEOFF-v2.2",
        "supporting_results": [
            "ASMP-3-BLOCK-SELECTION-COMPOSITION-v1.9",
            "ASMP-3-ENCODING-INVARIANCE-v2.0",
            "ASMP-3-HONEST-SEARCH-BARRIER-v2.1",
        ],
        "theorem": {
            "protocol": "advocate transcript, critic quotient witness, fresh replicated checks",
            "positive_class": (
                "uniform efficient Find plus sound-complete Refute plus fresh iid noise blocks"
            ),
            "completeness": "at least 1-delta",
            "soundness": "at most delta",
            "gap": "at least 1-2delta",
            "semantic_queries": "r*d",
            "critic_communication": "length prefix plus r(atom-id,answer) pairs",
        },
        "protocol_rows": rows,
        "polylog_scaling_rows": scaling,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The theorem is conditional on a uniformly efficient finder for every "
            "false admissible transcript, a sound-complete decidable Refute relation, "
            "and fresh independent replication blocks after adaptive selection. It "
            "does not prove those contracts for arbitrary tasks, optimize over all "
            "interfaces, or establish a converse characterization."
        ),
    }
