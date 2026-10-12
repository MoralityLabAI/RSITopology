from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
from math import ceil, prod
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "interactive_covering_frontier_v2_15.json"
VERIFY_PATH = HERE / "artifacts" / "interactive_covering_frontier_verification_v2_15.json"
SEARCH_PARENT_PATH = HERE.parent / "asmp3_honest_search_barrier_v2_1" / "artifacts" / "honest_search_barrier_v2_1.json"
RESOURCE_PARENT_PATH = HERE.parent / "asmp3_resource_tradeoff_v2_2" / "artifacts" / "resource_tradeoff_v2_2.json"
PATH_RISK_PARENT_PATH = HERE.parent / "asmp3_correlated_path_risk_v2_13" / "artifacts" / "correlated_path_risk_v2_13.json"


def ratio(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def values(limit: int) -> tuple[int, ...]:
    result = set(range(1, min(limit, 12) + 1))
    result.update(value for value in (16, 24, 32, 48, 64) if value <= limit)
    result.add(limit)
    return tuple(sorted(result))


def reconstruct_frontier() -> list[dict[str, object]]:
    rows = []
    for marker_count in range(2, 65):
        for transcript_count in values(marker_count):
            for query_budget in values(marker_count):
                covered = min(marker_count, transcript_count * query_budget)
                exact = Fraction(covered, marker_count)
                rows.append(
                    {
                        "semantic_atom_count": marker_count,
                        "complete_prover_transcript_count": transcript_count,
                        "adaptive_semantic_query_budget": query_budget,
                        "compressed_zero_path_capacity": transcript_count * query_budget,
                        "maximum_markers_covered_per_public_seed": covered,
                        "exact_public_coin_worst_marker_completeness": ratio(exact),
                        "perfect_completeness": covered == marker_count,
                        "perfect_completeness_iff_Kq_at_least_N": (covered == marker_count) == (transcript_count * query_budget >= marker_count),
                        "minimum_transcripts_for_perfect_completeness": ceil(marker_count / query_budget),
                        "arbitrary_round_interaction_allowed": True,
                        "adaptive_semantic_queries_allowed": True,
                        "public_coins_allowed": True,
                        "pointwise_perfect_zero_world_soundness": True,
                        "certified": exact == min(Fraction(1), Fraction(transcript_count * query_budget, marker_count)),
                    }
                )
    return rows


def tree_histories(depth: int) -> tuple[str, ...]:
    histories = []
    for length in range(depth):
        if length == 0:
            histories.append("")
        else:
            histories.extend(format(value, f"0{length}b") for value in range(1 << length))
    return tuple(histories)


def reconstruct_tree_audit() -> dict[str, object]:
    digest = hashlib.sha256()
    rows = []
    total_trees = total_runs = total_violations = 0
    for marker_count in range(2, 6):
        for depth in range(1, 4):
            nodes = tree_histories(depth)
            trees = marker_count ** len(nodes)
            violations = 0
            maximum = 0
            for assignment in product(range(marker_count), repeat=len(nodes)):
                lookup = {history: query for history, query in zip(nodes, assignment)}
                zero_path = {lookup["0" * index] for index in range(depth)}
                hits = set()
                for marker in range(marker_count):
                    history = ""
                    for _ in range(depth):
                        query = lookup[history]
                        if query == marker:
                            hits.add(marker)
                            break
                        history += "0"
                violations += int(hits != zero_path)
                maximum = max(maximum, len(hits))
                digest.update(
                    (
                        f"{marker_count}|{depth}|{','.join(map(str, assignment))}|"
                        f"{','.join(map(str, sorted(zero_path)))}|"
                        f"{','.join(map(str, sorted(hits)))}\n"
                    ).encode("ascii")
                )
            total_trees += trees
            total_runs += trees * marker_count
            total_violations += violations
            rows.append(
                {
                    "semantic_atom_count": marker_count,
                    "adaptive_query_depth": depth,
                    "tree_nodes": len(nodes),
                    "trees_enumerated": trees,
                    "marker_runs": trees * marker_count,
                    "zero_path_hit_set_violations": violations,
                    "maximum_hit_set_size": maximum,
                    "depth_capacity_respected": maximum <= depth,
                    "certified": violations == 0 and maximum <= depth,
                }
            )
    return {
        "rows": rows,
        "adaptive_trees_enumerated": total_trees,
        "marker_runs": total_runs,
        "zero_path_compression_violations": total_violations,
        "canonical_tree_digest_sha256": digest.hexdigest().upper(),
        "certified": total_trees == 97062 and total_violations == 0 and all(row["certified"] for row in rows),
    }


def subset_masks(marker_count: int, query_budget: int) -> list[int]:
    masks = []
    for subset in combinations(range(marker_count), query_budget):
        mask = sum(1 << marker for marker in subset)
        masks.append(mask)
    return masks


def reconstruct_codebooks() -> list[dict[str, object]]:
    rows = []
    for marker_count in range(2, 8):
        for transcript_count in range(1, min(3, marker_count) + 1):
            for query_budget in range(1, min(3, marker_count) + 1):
                maximum = 0
                count = 0
                for family in combinations_with_replacement(subset_masks(marker_count, query_budget), transcript_count):
                    union = 0
                    for mask in family:
                        union |= mask
                    maximum = max(maximum, union.bit_count())
                    count += 1
                expected = min(marker_count, transcript_count * query_budget)
                rows.append(
                    {
                        "semantic_atom_count": marker_count,
                        "complete_prover_transcript_count": transcript_count,
                        "query_budget": query_budget,
                        "zero_path_codebooks_enumerated": count,
                        "maximum_union_found": maximum,
                        "compressed_capacity": expected,
                        "exact_capacity_attained": maximum == expected,
                        "certified": maximum == expected,
                    }
                )
    return rows


def reconstruct_rotations() -> list[dict[str, object]]:
    rows = []
    for marker_count in range(2, 25):
        for transcript_count in range(1, min(marker_count, 6) + 1):
            for query_budget in range(1, min(marker_count, 6) + 1):
                covered = min(marker_count, transcript_count * query_budget)
                counts = [0] * marker_count
                maximum_blocks = maximum_block = 0
                for seed in range(marker_count):
                    window = [(seed + offset) % marker_count for offset in range(covered)]
                    for marker in window:
                        counts[marker] += 1
                    blocks = [window[offset : offset + query_budget] for offset in range(0, covered, query_budget)]
                    maximum_blocks = max(maximum_blocks, len(blocks))
                    maximum_block = max(maximum_block, *(len(block) for block in blocks))
                exact = all(count == covered for count in counts)
                rows.append(
                    {
                        "semantic_atom_count": marker_count,
                        "complete_prover_transcript_count": transcript_count,
                        "query_budget": query_budget,
                        "public_seed_count": marker_count,
                        "covered_markers_per_seed": covered,
                        "each_marker_successful_seeds": covered,
                        "worst_marker_success": ratio(Fraction(covered, marker_count)),
                        "maximum_blocks_per_seed": maximum_blocks,
                        "maximum_block_size": maximum_block,
                        "transcript_budget_respected": maximum_blocks <= transcript_count,
                        "query_budget_respected": maximum_block <= query_budget,
                        "exact_maximin_attainment": exact,
                        "certified": exact and maximum_blocks <= transcript_count and maximum_block <= query_budget,
                    }
                )
    return rows


def compositions(total: int, slots: int):
    if slots == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for rest in compositions(total - first, slots - 1):
                yield (first,) + rest


def reconstruct_schedules() -> list[dict[str, object]]:
    rows = []
    for total_bits in range(13):
        for rounds in range(1, 7):
            schedules = list(compositions(total_bits, rounds))
            capacities = [prod(2**bits for bits in schedule) for schedule in schedules]
            expected = 2**total_bits
            rows.append(
                {
                    "total_prover_bits": total_bits,
                    "interaction_rounds": rounds,
                    "bit_schedules_enumerated": len(schedules),
                    "minimum_complete_transcripts": min(capacities),
                    "maximum_complete_transcripts": max(capacities),
                    "fixed_length_transcript_capacity": expected,
                    "round_partition_changes_capacity": any(capacity != expected for capacity in capacities),
                    "certified": all(capacity == expected for capacity in capacities),
                }
            )
    return rows


def reconstruct_bits() -> list[dict[str, object]]:
    rows = []
    for index_bits in range(1, 21):
        marker_count = 2**index_bits
        for communication_bits in range(index_bits + 1):
            for query_bits in range(index_bits + 1):
                transcript_count = 2**communication_bits
                query_budget = 2**query_bits
                exact = min(Fraction(1), Fraction(transcript_count * query_budget, marker_count))
                rows.append(
                    {
                        "index_bits": index_bits,
                        "semantic_atom_count": marker_count,
                        "fixed_length_prover_bits": communication_bits,
                        "complete_prover_transcripts": transcript_count,
                        "query_budget": query_budget,
                        "exact_worst_marker_completeness": ratio(exact),
                        "bit_query_exponent": communication_bits + query_bits,
                        "perfect_completeness": communication_bits + query_bits >= index_bits,
                        "certified": exact == Fraction(2 ** min(index_bits, communication_bits + query_bits), marker_count),
                    }
                )
    return rows


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    search = json.loads(SEARCH_PARENT_PATH.read_text(encoding="utf-8"))
    resource = json.loads(RESOURCE_PARENT_PATH.read_text(encoding="utf-8"))
    path_risk = json.loads(PATH_RISK_PARENT_PATH.read_text(encoding="utf-8"))
    frontier = reconstruct_frontier()
    trees = reconstruct_tree_audit()
    codebooks = reconstruct_codebooks()
    rotations = reconstruct_rotations()
    schedules = reconstruct_schedules()
    bits = reconstruct_bits()
    theorem = result.get("theorem", {})
    checks = {
        "V0_schema_parent_and_status": result.get("schema_version") == "asmp3_interactive_covering_frontier_v2_15" and result.get("parent_results") == ["ASMP-3-HONEST-SEARCH-BARRIER-v2.1", "ASMP-3-RESOURCE-TRADEOFF-v2.2", "ASMP-3-CORRELATED-PATH-RISK-v2.13"] and result.get("status") == "exact_arbitrary_round_public_coin_interactive_unique_marker_frontier",
        "V1_parent_contracts_reconstructed": search["certified"] is True and search["theorem"]["randomized_q_query_maximin_success"] == "q/N" and resource["certified"] is True and resource["theorem"]["lower_bound"] == "K*q>=N message-query covering inequality" and path_risk["certified"] is True and result.get("parent_audit", {}).get("certified") is True,
        "V2_all_13413_frontier_rows_reconstructed": len(frontier) == 13413 and result.get("frontier_rows") == frontier and all(row["certified"] for row in frontier),
        "V3_all_97062_adaptive_trees_reconstructed": trees["adaptive_trees_enumerated"] == 97062 and trees["marker_runs"] == 464010 and trees["zero_path_compression_violations"] == 0 and result.get("adaptive_tree_audit") == trees,
        "V4_all_49_small_codebook_frontiers_reconstructed": len(codebooks) == 49 and result.get("compressed_codebook_rows") == codebooks and all(row["certified"] for row in codebooks),
        "V5_all_738_public_coin_attainments_reconstructed": len(rotations) == 738 and result.get("rotation_attainment_rows") == rotations and all(row["certified"] for row in rotations),
        "V6_all_round_schedules_and_bit_frontiers_reconstructed": len(schedules) == 78 and len(bits) == 3310 and result.get("round_schedule_rows") == schedules and result.get("bit_frontier_rows") == bits and all(row["certified"] for row in schedules + bits),
        "V7_exact_interactive_theorem_fields_match": theorem.get("compression_lemma") == "each public-seed/transcript pair can succeed only on markers in its all-zero-answer query path" and theorem.get("exact_value") == "min(1,K*q/N)" and theorem.get("perfect_completeness") == "K*q>=N iff perfect completeness is possible" and theorem.get("fixed_length_bits") == "value=min(1,2^b*q/N)",
        "V8_interface_and_claim_firewalls_are_explicit": all(phrase in result.get("claim_boundary", "") for phrase in ("pointwise perfect zero-world soundness", "positive soundness error", "arbitrary ASMP-3 task families")) and all(row["arbitrary_round_interaction_allowed"] and row["adaptive_semantic_queries_allowed"] and row["public_coins_allowed"] for row in frontier),
        "V9_all_ten_producer_gates_pass": len(result.get("gates", {})) == 10 and all(result.get("gates", {}).values()) and result.get("certified") is True,
    }
    return {
        "schema_version": "asmp3_interactive_covering_frontier_verification_v2_15",
        "checker": "clean_room_interactive_compression_adaptive_tree_codebook_rotation_round_and_bit_frontier_audit",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": "This checker certifies the declared unique-marker interactive interface, not a universal ASMP-3 resource theorem.",
    }


def main() -> None:
    receipt = verify()
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if not receipt["passed"]:
        failed = [name for name, value in receipt["checks"].items() if not value]
        raise RuntimeError(f"ASMP-3 v2.15 verification failed: {failed}")
    print(f"ASMP-3 interactive covering verification passed: {receipt['check_count']}/{receipt['check_count']}")


if __name__ == "__main__":
    main()
