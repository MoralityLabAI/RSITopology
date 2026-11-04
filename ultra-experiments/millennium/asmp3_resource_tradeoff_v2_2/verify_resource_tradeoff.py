from __future__ import annotations

import json
from itertools import combinations
from math import ceil
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "resource_tradeoff_v2_2.json"
OUTPUT_PATH = HERE / "artifacts" / "resource_tradeoff_verification_v2_2.json"
PARENT_PATH = (
    HERE.parent
    / "asmp3_honest_search_barrier_v2_1"
    / "artifacts"
    / "honest_search_barrier_v2_1.json"
)
COMPOSITION_PATH = (
    HERE.parent
    / "asmp3_block_selection_composition_v1_9"
    / "artifacts"
    / "block_selection_composition_v1_9.json"
)


def log_bits(value: int) -> int:
    return (value - 1).bit_length()


def q_values(index_bits: int) -> tuple[int, ...]:
    count = 1 << index_bits
    values = {1 << exponent for exponent in range(index_bits + 1)}
    values |= {value for value in (3, 5, 7, 10, count - 1) if 1 <= value <= count}
    return tuple(sorted(values))


def reconstruct_row(marker_count: int, queries: int) -> dict[str, object]:
    messages = ceil(marker_count / queries)
    bits = log_bits(messages)
    full, remainder = divmod(marker_count, queries)
    block_count = full + int(remainder > 0)
    histogram = {str(queries): full}
    if remainder:
        histogram[str(remainder)] = histogram.get(str(remainder), 0) + 1
    maximum = queries if full else remainder
    capacity = (1 << bits) * queries
    prior = (1 << (bits - 1)) * queries if bits else 0
    return {
        "semantic_atom_count": marker_count,
        "verifier_ideal_semantic_queries": queries,
        "minimum_message_count": messages,
        "minimum_communication_bits": bits,
        "covering_lower_bound": "K*q>=N",
        "bit_query_capacity": capacity,
        "one_fewer_bit_capacity": prior,
        "capacity_sufficient": capacity >= marker_count,
        "one_fewer_bit_insufficient": bits == 0 or prior < marker_count,
        "constructive_block_count": block_count,
        "constructive_block_size_histogram": histogram,
        "constructive_max_block_size": maximum,
        "constructive_cover_size": marker_count,
        "perfect_completeness": block_count == messages,
        "perfect_zero_input_soundness": True,
        "honest_marker_search_queries": marker_count,
        "post_search_prover_message_bits": bits,
        "certified": True,
    }


def cover_exists(marker_count: int, queries: int, messages: int) -> tuple[bool, int]:
    masks = []
    for subset in combinations(range(marker_count), queries):
        mask = sum(1 << item for item in subset)
        masks.append(mask)
    if messages == 0:
        return False, 1
    full = (1 << marker_count) - 1
    checked = 0
    for family in combinations(masks, messages):
        union = 0
        for mask in family:
            union |= mask
        checked += 1
        if union == full:
            return True, checked
    return False, checked


def reconstruct_exhaustive() -> list[dict[str, object]]:
    rows = []
    for marker_count in range(2, 9):
        for queries in range(1, marker_count + 1):
            messages = ceil(marker_count / queries)
            lower, lower_checked = cover_exists(marker_count, queries, messages - 1)
            exact, exact_checked = cover_exists(marker_count, queries, messages)
            rows.append(
                {
                    "semantic_atom_count": marker_count,
                    "verifier_queries": queries,
                    "claimed_minimum_messages": messages,
                    "families_checked_below_minimum": lower_checked,
                    "cover_below_minimum_exists": lower,
                    "families_checked_at_minimum_until_witness": exact_checked,
                    "cover_at_minimum_exists": exact,
                    "minimum_certified": not lower and exact,
                }
            )
    return rows


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_PATH.read_text(encoding="utf-8"))
    composition = json.loads(COMPOSITION_PATH.read_text(encoding="utf-8"))
    rows = result.get("frontier_rows", [])
    expected = [
        reconstruct_row(1 << bits, queries)
        for bits in range(1, 25)
        for queries in q_values(bits)
    ]
    exhaustive = reconstruct_exhaustive()
    requirements = {
        (row["atoms"], row["eta"], row["target_joint_risk"]): row
        for row in composition["depth_requirement_rows"]
    }
    robust_expected = []
    marker_count = 1 << 20
    for queries in (1, 4, 16, 64):
        requirement = requirements[(queries, "1/5", "1/100")]
        ideal = reconstruct_row(marker_count, queries)
        depth = requirement["minimal_union_safe_odd_depth"]
        robust_expected.append(
            {
                "semantic_atom_count": marker_count,
                "verifier_candidate_queries": queries,
                "communication_bits": ideal["minimum_communication_bits"],
                "eta": "1/5",
                "target_joint_noise_risk": "1/100",
                "replications_per_candidate": depth,
                "total_noisy_semantic_queries": queries * depth,
                "union_bound_at_depth": requirement["union_bound_at_safe_depth"],
                "certified": queries * depth == requirement["union_safe_total_queries"],
            }
        )
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version") == "asmp3_resource_tradeoff_v2_2"
            and result.get("status") == "exact_unique_marker_communication_query_frontier"
            and result.get("parent_result") == "ASMP-3-HONEST-SEARCH-BARRIER-v2.1"
            and result.get("certified") is True
            and "Shared randomness" in result.get("claim_boundary", "")
        ),
        "V1_all_433_frontier_rows_reconstructed": len(rows) == 433 and rows == expected,
        "V2_lower_bound_and_partition_attainment_exact": all(
            row["minimum_message_count"]
            == ceil(row["semantic_atom_count"] / row["verifier_ideal_semantic_queries"])
            and row["constructive_block_count"] == row["minimum_message_count"]
            and row["perfect_completeness"]
            and row["perfect_zero_input_soundness"]
            for row in rows
        ),
        "V3_small_cover_search_replayed": (
            result.get("exhaustive_cover_rows") == exhaustive
            and len(exhaustive) == 35
            and all(row["minimum_certified"] for row in exhaustive)
        ),
        "V4_robust_replication_operating_points_reconstructed": (
            result.get("robust_replication_rows") == robust_expected
            and all(row["certified"] for row in robust_expected)
        ),
        "V5_endpoint_and_capacity_frontiers_exact": all(
            reconstruct_row(1 << bits, 1)["minimum_communication_bits"] == bits
            and reconstruct_row(1 << bits, 1 << bits)["minimum_communication_bits"] == 0
            for bits in range(1, 25)
        ),
        "V6_parent_search_and_noise_contracts_match": (
            parent["theorem"]["randomized_q_query_maximin_success"] == "q/N"
            and composition["theorem"]["query_cost"] == "M*d semantic queries"
        ),
        "V7_producer_gates_all_true": (
            len(result.get("gates", {})) == 10 and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_resource_tradeoff_verification_v2_2",
        "checker": "clean_room_cover_frontier_and_noise_cost_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker validates the one-message deterministic perfect "
            "completeness/soundness cover interface. It does not extend the lower "
            "bound to interactive, randomized, bounded-error, or adaptive protocols."
        ),
    }


def main() -> None:
    result = verify()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not result["passed"]:
        failed = [name for name, passed in result["checks"].items() if not passed]
        raise SystemExit(f"resource-tradeoff verification failed: {failed}")
    print(
        "ASMP-3 resource-tradeoff verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
