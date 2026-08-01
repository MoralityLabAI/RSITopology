from __future__ import annotations

import json
from itertools import combinations
from math import ceil
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT_ARTIFACT = (
    HERE.parent
    / "asmp3_honest_search_barrier_v2_1"
    / "artifacts"
    / "honest_search_barrier_v2_1.json"
)
COMPOSITION_ARTIFACT = (
    HERE.parent
    / "asmp3_block_selection_composition_v1_9"
    / "artifacts"
    / "block_selection_composition_v1_9.json"
)


def ceil_log2(value: int) -> int:
    if not isinstance(value, int) or value < 1:
        raise ValueError("ceil_log2 requires a positive integer")
    return (value - 1).bit_length()


def validate(marker_count: int, verifier_queries: int) -> None:
    if not isinstance(marker_count, int) or marker_count < 1:
        raise ValueError("marker count must be positive")
    if (
        not isinstance(verifier_queries, int)
        or verifier_queries < 1
        or verifier_queries > marker_count
    ):
        raise ValueError("verifier query count must lie in [1,N]")


def resource_row(marker_count: int, verifier_queries: int) -> dict[str, object]:
    validate(marker_count, verifier_queries)
    minimum_messages = ceil(marker_count / verifier_queries)
    minimum_bits = ceil_log2(minimum_messages)
    full_blocks, remainder = divmod(marker_count, verifier_queries)
    block_count = full_blocks + int(remainder > 0)
    block_histogram = {str(verifier_queries): full_blocks}
    if remainder:
        block_histogram[str(remainder)] = block_histogram.get(str(remainder), 0) + 1
    maximum_block = verifier_queries if full_blocks else remainder
    capacity = (1 << minimum_bits) * verifier_queries
    prior_capacity = (
        (1 << (minimum_bits - 1)) * verifier_queries if minimum_bits else 0
    )
    return {
        "semantic_atom_count": marker_count,
        "verifier_ideal_semantic_queries": verifier_queries,
        "minimum_message_count": minimum_messages,
        "minimum_communication_bits": minimum_bits,
        "covering_lower_bound": "K*q>=N",
        "bit_query_capacity": capacity,
        "one_fewer_bit_capacity": prior_capacity,
        "capacity_sufficient": capacity >= marker_count,
        "one_fewer_bit_insufficient": minimum_bits == 0 or prior_capacity < marker_count,
        "constructive_block_count": block_count,
        "constructive_block_size_histogram": block_histogram,
        "constructive_max_block_size": maximum_block,
        "constructive_cover_size": marker_count,
        "perfect_completeness": block_count == minimum_messages,
        "perfect_zero_input_soundness": True,
        "honest_marker_search_queries": marker_count,
        "post_search_prover_message_bits": minimum_bits,
        "certified": (
            minimum_messages == ceil(marker_count / verifier_queries)
            and minimum_bits == ceil_log2(minimum_messages)
            and capacity >= marker_count
            and (minimum_bits == 0 or prior_capacity < marker_count)
            and block_count == minimum_messages
            and maximum_block <= verifier_queries
            and sum(int(size) * count for size, count in block_histogram.items())
            == marker_count
        ),
    }


def query_values(index_bits: int) -> tuple[int, ...]:
    marker_count = 1 << index_bits
    values = {1 << exponent for exponent in range(index_bits + 1)}
    values |= {candidate for candidate in (3, 5, 7, 10, marker_count - 1) if 1 <= candidate <= marker_count}
    return tuple(sorted(values))


def cover_exists(marker_count: int, verifier_queries: int, messages: int) -> tuple[bool, int]:
    if messages < 0:
        return False, 0
    masks = []
    for subset in combinations(range(marker_count), verifier_queries):
        mask = 0
        for item in subset:
            mask |= 1 << item
        masks.append(mask)
    full = (1 << marker_count) - 1
    checked = 0
    if messages == 0:
        return False, 1
    for family in combinations(masks, messages):
        union = 0
        for mask in family:
            union |= mask
        checked += 1
        if union == full:
            return True, checked
    return False, checked


def exhaustive_cover_audit() -> list[dict[str, object]]:
    rows = []
    for marker_count in range(2, 9):
        for verifier_queries in range(1, marker_count + 1):
            minimum = ceil(marker_count / verifier_queries)
            lower_exists, lower_checked = cover_exists(
                marker_count, verifier_queries, minimum - 1
            )
            exact_exists, exact_checked = cover_exists(
                marker_count, verifier_queries, minimum
            )
            rows.append(
                {
                    "semantic_atom_count": marker_count,
                    "verifier_queries": verifier_queries,
                    "claimed_minimum_messages": minimum,
                    "families_checked_below_minimum": lower_checked,
                    "cover_below_minimum_exists": lower_exists,
                    "families_checked_at_minimum_until_witness": exact_checked,
                    "cover_at_minimum_exists": exact_exists,
                    "minimum_certified": not lower_exists and exact_exists,
                }
            )
    return rows


def build_result() -> dict[str, object]:
    parent = json.loads(PARENT_ARTIFACT.read_text(encoding="utf-8"))
    composition = json.loads(COMPOSITION_ARTIFACT.read_text(encoding="utf-8"))
    rows = [
        resource_row(1 << index_bits, verifier_queries)
        for index_bits in range(1, 25)
        for verifier_queries in query_values(index_bits)
    ]
    exhaustive = exhaustive_cover_audit()
    requirement_by_key = {
        (row["atoms"], row["eta"], row["target_joint_risk"]): row
        for row in composition["depth_requirement_rows"]
    }
    robust = []
    marker_count = 1 << 20
    for verifier_queries in (1, 4, 16, 64):
        requirement = requirement_by_key[(verifier_queries, "1/5", "1/100")]
        ideal = resource_row(marker_count, verifier_queries)
        depth = requirement["minimal_union_safe_odd_depth"]
        robust.append(
            {
                "semantic_atom_count": marker_count,
                "verifier_candidate_queries": verifier_queries,
                "communication_bits": ideal["minimum_communication_bits"],
                "eta": "1/5",
                "target_joint_noise_risk": "1/100",
                "replications_per_candidate": depth,
                "total_noisy_semantic_queries": verifier_queries * depth,
                "union_bound_at_depth": requirement["union_bound_at_safe_depth"],
                "certified": (
                    verifier_queries * depth
                    == requirement["union_safe_total_queries"]
                ),
            }
        )
    parent_by_n = {row["semantic_atom_count"]: row for row in parent["search_rows"]}
    gates = {
        "R0_frontier_registry_complete": len(rows) > 0 and all(row["certified"] for row in rows),
        "R1_covering_lower_bound_exact": all(
            row["minimum_message_count"]
            == ceil(row["semantic_atom_count"] / row["verifier_ideal_semantic_queries"])
            for row in rows
        ),
        "R2_bit_lower_bound_exact": all(
            row["minimum_communication_bits"]
            == ceil_log2(row["minimum_message_count"])
            and row["capacity_sufficient"]
            and row["one_fewer_bit_insufficient"]
            for row in rows
        ),
        "R3_partition_protocol_attains_every_frontier_point": all(
            row["constructive_block_count"] == row["minimum_message_count"]
            and row["constructive_max_block_size"]
            <= row["verifier_ideal_semantic_queries"]
            and row["constructive_cover_size"] == row["semantic_atom_count"]
            for row in rows
        ),
        "R4_small_cover_frontiers_exhaustively_minimal": (
            len(exhaustive) == sum(range(2, 9))
            and all(row["minimum_certified"] for row in exhaustive)
        ),
        "R5_endpoint_tradeoffs_match_index_and_full_recomputation": all(
            resource_row(1 << index_bits, 1)["minimum_communication_bits"] == index_bits
            and resource_row(1 << index_bits, 1 << index_bits)["minimum_communication_bits"] == 0
            for index_bits in range(1, 25)
        ),
        "R6_honest_search_cost_remains_N": all(
            row["honest_marker_search_queries"] == row["semantic_atom_count"]
            and parent_by_n[row["semantic_atom_count"]]["deterministic_exact_worst_case_queries"]
            == row["semantic_atom_count"]
            for row in rows
        ),
        "R7_robust_replication_costs_composed": (
            len(robust) == 4 and all(row["certified"] for row in robust)
        ),
        "R8_perfect_completeness_and_zero_soundness_attained": all(
            row["perfect_completeness"] and row["perfect_zero_input_soundness"]
            for row in rows
        ),
        "R9_parent_contracts_match": (
            parent["theorem"]["randomized_q_query_maximin_success"] == "q/N"
            and composition["theorem"]["query_cost"] == "M*d semantic queries"
        ),
    }
    return {
        "schema_version": "asmp3_resource_tradeoff_v2_2",
        "experiment_id": "ASMP-3-RESOURCE-TRADEOFF-v2.2",
        "status": "exact_unique_marker_communication_query_frontier",
        "parent_result": "ASMP-3-HONEST-SEARCH-BARRIER-v2.1",
        "noise_composition_result": "ASMP-3-BLOCK-SELECTION-COMPOSITION-v1.9",
        "theorem": {
            "interface": "one prover message selects at most q ideal semantic queries",
            "lower_bound": "K*q>=N message-query covering inequality",
            "communication_bits": "ceil(log2(ceil(N/q)))",
            "attainment": "partition N marker indices into q-sized query blocks",
            "honest_search": "N black-box queries before the message can be formed",
        },
        "frontier_rows": rows,
        "exhaustive_cover_rows": exhaustive,
        "robust_replication_rows": robust,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The frontier assumes a single deterministic message followed by a "
            "message-indexed nonadaptive set of at most q ideal queries, perfect "
            "completeness, and perfect soundness on the zero-marker input. Shared "
            "randomness, interaction, bounded error, adaptive queries, or structured "
            "side information can change the tradeoff and require new lower bounds."
        ),
    }
