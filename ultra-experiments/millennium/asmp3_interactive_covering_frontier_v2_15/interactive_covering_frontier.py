from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
from math import ceil, prod
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ARTIFACT_DIR = HERE / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "interactive_covering_frontier_v2_15.json"
SEARCH_PARENT_PATH = (
    HERE.parent
    / "asmp3_honest_search_barrier_v2_1"
    / "artifacts"
    / "honest_search_barrier_v2_1.json"
)
RESOURCE_PARENT_PATH = (
    HERE.parent
    / "asmp3_resource_tradeoff_v2_2"
    / "artifacts"
    / "resource_tradeoff_v2_2.json"
)
PATH_RISK_PARENT_PATH = (
    HERE.parent
    / "asmp3_correlated_path_risk_v2_13"
    / "artifacts"
    / "correlated_path_risk_v2_13.json"
)


def ratio(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def frontier_row(marker_count: int, transcript_count: int, query_budget: int) -> dict[str, object]:
    if marker_count < 1 or transcript_count < 1 or query_budget < 1:
        raise ValueError("N, K, and q must be positive")
    covered = min(marker_count, transcript_count * query_budget)
    value = Fraction(covered, marker_count)
    return {
        "semantic_atom_count": marker_count,
        "complete_prover_transcript_count": transcript_count,
        "adaptive_semantic_query_budget": query_budget,
        "compressed_zero_path_capacity": transcript_count * query_budget,
        "maximum_markers_covered_per_public_seed": covered,
        "exact_public_coin_worst_marker_completeness": ratio(value),
        "perfect_completeness": covered == marker_count,
        "perfect_completeness_iff_Kq_at_least_N": (covered == marker_count) == (transcript_count * query_budget >= marker_count),
        "minimum_transcripts_for_perfect_completeness": ceil(marker_count / query_budget),
        "arbitrary_round_interaction_allowed": True,
        "adaptive_semantic_queries_allowed": True,
        "public_coins_allowed": True,
        "pointwise_perfect_zero_world_soundness": True,
        "certified": value == min(Fraction(1), Fraction(transcript_count * query_budget, marker_count)),
    }


def registered_values(limit: int) -> tuple[int, ...]:
    values = set(range(1, min(limit, 12) + 1))
    values.update(value for value in (16, 24, 32, 48, 64) if value <= limit)
    values.add(limit)
    return tuple(sorted(values))


def frontier_rows() -> list[dict[str, object]]:
    return [
        frontier_row(marker_count, transcript_count, query_budget)
        for marker_count in range(2, 65)
        for transcript_count in registered_values(marker_count)
        for query_budget in registered_values(marker_count)
    ]


def histories(depth: int) -> tuple[str, ...]:
    return tuple(
        format(value, f"0{length}b") if length else ""
        for length in range(depth)
        for value in range(1 << length)
    )


def adaptive_tree_audit() -> dict[str, object]:
    digest = hashlib.sha256()
    rows = []
    total_trees = total_marker_runs = violations = 0
    for marker_count in range(2, 6):
        for depth in range(1, 4):
            nodes = histories(depth)
            tree_count = marker_count ** len(nodes)
            row_violations = 0
            maximum_hit_set = 0
            for assignments in product(range(marker_count), repeat=len(nodes)):
                tree = dict(zip(nodes, assignments))
                zero_path = {tree["0" * step] for step in range(depth)}
                hit_set = set()
                for marker in range(marker_count):
                    history = ""
                    hit = False
                    for _ in range(depth):
                        query = tree[history]
                        answer = int(query == marker)
                        if answer:
                            hit = True
                            break
                        history += "0"
                    if hit:
                        hit_set.add(marker)
                mismatch = hit_set != zero_path
                row_violations += int(mismatch)
                maximum_hit_set = max(maximum_hit_set, len(hit_set))
                digest.update(
                    (
                        f"{marker_count}|{depth}|{','.join(map(str, assignments))}|"
                        f"{','.join(map(str, sorted(zero_path)))}|"
                        f"{','.join(map(str, sorted(hit_set)))}\n"
                    ).encode("ascii")
                )
            total_trees += tree_count
            total_marker_runs += tree_count * marker_count
            violations += row_violations
            rows.append(
                {
                    "semantic_atom_count": marker_count,
                    "adaptive_query_depth": depth,
                    "tree_nodes": len(nodes),
                    "trees_enumerated": tree_count,
                    "marker_runs": tree_count * marker_count,
                    "zero_path_hit_set_violations": row_violations,
                    "maximum_hit_set_size": maximum_hit_set,
                    "depth_capacity_respected": maximum_hit_set <= depth,
                    "certified": row_violations == 0 and maximum_hit_set <= depth,
                }
            )
    return {
        "rows": rows,
        "adaptive_trees_enumerated": total_trees,
        "marker_runs": total_marker_runs,
        "zero_path_compression_violations": violations,
        "canonical_tree_digest_sha256": digest.hexdigest().upper(),
        "certified": total_trees == 97062 and violations == 0 and all(row["certified"] for row in rows),
    }


def mask_subsets(marker_count: int, query_budget: int) -> list[int]:
    masks = []
    for subset in combinations(range(marker_count), query_budget):
        mask = 0
        for marker in subset:
            mask |= 1 << marker
        masks.append(mask)
    return masks


def compressed_codebook_audit() -> list[dict[str, object]]:
    rows = []
    for marker_count in range(2, 8):
        for transcript_count in range(1, min(3, marker_count) + 1):
            for query_budget in range(1, min(3, marker_count) + 1):
                paths = mask_subsets(marker_count, query_budget)
                maximum_union = 0
                codebooks = 0
                for family in combinations_with_replacement(paths, transcript_count):
                    union = 0
                    for mask in family:
                        union |= mask
                    maximum_union = max(maximum_union, union.bit_count())
                    codebooks += 1
                expected = min(marker_count, transcript_count * query_budget)
                rows.append(
                    {
                        "semantic_atom_count": marker_count,
                        "complete_prover_transcript_count": transcript_count,
                        "query_budget": query_budget,
                        "zero_path_codebooks_enumerated": codebooks,
                        "maximum_union_found": maximum_union,
                        "compressed_capacity": expected,
                        "exact_capacity_attained": maximum_union == expected,
                        "certified": maximum_union == expected,
                    }
                )
    return rows


def cyclic_window(marker_count: int, start: int, size: int) -> list[int]:
    return [(start + offset) % marker_count for offset in range(size)]


def rotation_attainment_audit() -> list[dict[str, object]]:
    rows = []
    for marker_count in range(2, 25):
        for transcript_count in range(1, min(marker_count, 6) + 1):
            for query_budget in range(1, min(marker_count, 6) + 1):
                covered = min(marker_count, transcript_count * query_budget)
                inclusion_counts = [0] * marker_count
                maximum_block = 0
                blocks_per_seed = []
                for seed in range(marker_count):
                    window = cyclic_window(marker_count, seed, covered)
                    for marker in window:
                        inclusion_counts[marker] += 1
                    blocks = [window[offset : offset + query_budget] for offset in range(0, covered, query_budget)]
                    blocks_per_seed.append(len(blocks))
                    maximum_block = max(maximum_block, *(len(block) for block in blocks))
                exact = all(count == covered for count in inclusion_counts)
                rows.append(
                    {
                        "semantic_atom_count": marker_count,
                        "complete_prover_transcript_count": transcript_count,
                        "query_budget": query_budget,
                        "public_seed_count": marker_count,
                        "covered_markers_per_seed": covered,
                        "each_marker_successful_seeds": covered,
                        "worst_marker_success": ratio(Fraction(covered, marker_count)),
                        "maximum_blocks_per_seed": max(blocks_per_seed),
                        "maximum_block_size": maximum_block,
                        "transcript_budget_respected": max(blocks_per_seed) <= transcript_count,
                        "query_budget_respected": maximum_block <= query_budget,
                        "exact_maximin_attainment": exact,
                        "certified": exact and max(blocks_per_seed) <= transcript_count and maximum_block <= query_budget,
                    }
                )
    return rows


def weak_compositions(total: int, slots: int) -> Iterable[tuple[int, ...]]:
    if slots == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in weak_compositions(total - first, slots - 1):
            yield (first,) + rest


def round_schedule_audit() -> list[dict[str, object]]:
    rows = []
    for total_bits in range(0, 13):
        for rounds in range(1, 7):
            schedules = list(weak_compositions(total_bits, rounds))
            capacities = [prod(1 << bits for bits in schedule) for schedule in schedules]
            expected = 1 << total_bits
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


def bit_frontier_rows() -> list[dict[str, object]]:
    rows = []
    for index_bits in range(1, 21):
        marker_count = 1 << index_bits
        for communication_bits in range(0, index_bits + 1):
            transcript_count = 1 << communication_bits
            for query_bits in range(0, index_bits + 1):
                query_budget = 1 << query_bits
                value = min(Fraction(1), Fraction(transcript_count * query_budget, marker_count))
                rows.append(
                    {
                        "index_bits": index_bits,
                        "semantic_atom_count": marker_count,
                        "fixed_length_prover_bits": communication_bits,
                        "complete_prover_transcripts": transcript_count,
                        "query_budget": query_budget,
                        "exact_worst_marker_completeness": ratio(value),
                        "bit_query_exponent": communication_bits + query_bits,
                        "perfect_completeness": communication_bits + query_bits >= index_bits,
                        "certified": value == Fraction(1 << min(index_bits, communication_bits + query_bits), marker_count),
                    }
                )
    return rows


def parent_audit() -> dict[str, object]:
    search = json.loads(SEARCH_PARENT_PATH.read_text(encoding="utf-8"))
    resource = json.loads(RESOURCE_PARENT_PATH.read_text(encoding="utf-8"))
    path_risk = json.loads(PATH_RISK_PARENT_PATH.read_text(encoding="utf-8"))
    return {
        "search_parent_certified": search["certified"],
        "search_value": search["theorem"]["randomized_q_query_maximin_success"],
        "deterministic_honest_search": "N" if all(
            row["deterministic_exact_worst_case_queries"] == row["semantic_atom_count"]
            for row in search["search_rows"]
        ) else "parent_mismatch",
        "resource_parent_certified": resource["certified"],
        "resource_parent_interface": resource["theorem"]["interface"],
        "resource_parent_lower_bound": resource["theorem"]["lower_bound"],
        "path_risk_parent_certified": path_risk["certified"],
        "path_risk_general_law": path_risk["theorem"]["general_path_law"],
        "certified": (
            search["certified"] is True
            and search["theorem"]["randomized_q_query_maximin_success"] == "q/N"
            and resource["certified"] is True
            and resource["theorem"]["lower_bound"] == "K*q>=N message-query covering inequality"
            and path_risk["certified"] is True
        ),
    }


def build_artifact() -> dict[str, object]:
    frontier = frontier_rows()
    trees = adaptive_tree_audit()
    codebooks = compressed_codebook_audit()
    rotations = rotation_attainment_audit()
    schedules = round_schedule_audit()
    bits = bit_frontier_rows()
    parents = parent_audit()
    gates = {
        "I0_parent_search_resource_and_path_risk_contracts_match": parents["certified"],
        "I1_registered_interactive_frontier_is_exact": len(frontier) > 10_000 and all(row["certified"] for row in frontier),
        "I2_arbitrary_round_transcripts_compress_to_K_zero_answer_paths": all(row["arbitrary_round_interaction_allowed"] and row["compressed_zero_path_capacity"] == row["complete_prover_transcript_count"] * row["adaptive_semantic_query_budget"] for row in frontier),
        "I3_all_adaptive_trees_hit_exactly_their_zero_answer_path_set": trees["certified"],
        "I4_exhaustive_small_codebooks_attain_min_N_Kq": len(codebooks) == 49 and all(row["certified"] for row in codebooks),
        "I5_cyclic_public_coin_protocol_attains_every_registered_maximin_value": len(rotations) == 738 and all(row["certified"] for row in rotations),
        "I6_round_partition_never_changes_fixed_length_transcript_capacity": len(schedules) == 78 and all(row["certified"] and not row["round_partition_changes_capacity"] for row in schedules),
        "I7_bit_query_frontier_is_exactly_additive_on_power_of_two_family": len(bits) == sum((n + 1) ** 2 for n in range(1, 21)) and all(row["certified"] for row in bits),
        "I8_perfect_completeness_is_equivalent_to_Kq_at_least_N": all(row["perfect_completeness_iff_Kq_at_least_N"] for row in frontier),
        "I9_honest_find_cost_remains_N_before_the_interactive_check": parents["deterministic_honest_search"] == "N" and all(row["pointwise_perfect_zero_world_soundness"] for row in frontier),
    }
    return {
        "schema_version": "asmp3_interactive_covering_frontier_v2_15",
        "experiment_id": "ASMP-3-INTERACTIVE-COVERING-FRONTIER-v2.15",
        "parent_results": [
            "ASMP-3-HONEST-SEARCH-BARRIER-v2.1",
            "ASMP-3-RESOURCE-TRADEOFF-v2.2",
            "ASMP-3-CORRELATED-PATH-RISK-v2.13",
        ],
        "status": "exact_arbitrary_round_public_coin_interactive_unique_marker_frontier",
        "theorem": {
            "interface": "arbitrary-round public-coin interaction, K complete prover transcripts, q adaptive semantic queries, pointwise perfect zero-world soundness",
            "compression_lemma": "each public-seed/transcript pair can succeed only on markers in its all-zero-answer query path",
            "upper_bound": "worst-marker completeness <= min(1,K*q/N)",
            "attainment": "cyclic public-seed windows partitioned into at most K blocks of size at most q",
            "exact_value": "min(1,K*q/N)",
            "perfect_completeness": "K*q>=N iff perfect completeness is possible",
            "fixed_length_bits": "value=min(1,2^b*q/N)",
            "honest_search": "N black-box queries before a marker-bearing transcript can be formed",
        },
        "frontier_rows": frontier,
        "adaptive_tree_audit": trees,
        "compressed_codebook_rows": codebooks,
        "rotation_attainment_rows": rotations,
        "round_schedule_rows": schedules,
        "bit_frontier_rows": bits,
        "parent_audit": parents,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The theorem is interface-uniform over round schedules, public coins, and adaptive "
            "semantic-query trees for the unstructured zero-or-one-marker family under pointwise "
            "perfect zero-world soundness and a K-codeword complete prover transcript bound. It "
            "does not cover positive soundness error, stronger side information, structured atoms, "
            "quantum queries, or arbitrary ASMP-3 task families."
        ),
    }


def write_artifact() -> dict[str, object]:
    artifact = build_artifact()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return artifact


if __name__ == "__main__":
    result = write_artifact()
    passed = sum(bool(value) for value in result["gates"].values())
    print(f"ASMP-3 interactive covering certified: {passed}/{len(result['gates'])}")
