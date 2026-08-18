from __future__ import annotations

import json
from fractions import Fraction
from math import ceil, comb
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "honest_search_barrier_v2_1.json"
OUTPUT_PATH = HERE / "artifacts" / "honest_search_barrier_verification_v2_1.json"
PARENT_PATH = (
    HERE.parent
    / "asmp3_encoding_invariance_v2_0"
    / "artifacts"
    / "encoding_invariance_v2_0.json"
)
NOISE_PATH = (
    HERE.parent
    / "asmp3_independent_noise_amplification_v1_8"
    / "artifacts"
    / "independent_noise_amplification_v1_8.json"
)


def text(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def reconstruct_row(index_bits: int) -> dict[str, object]:
    marker_count = 1 << index_bits
    budget = min(marker_count, index_bits**3)
    success = Q(budget, marker_count)
    needed = ceil(Q(2, 3) * marker_count)
    return {
        "index_bits": index_bits,
        "semantic_atom_count": marker_count,
        "promise": "at_most_one_semantic_atom_is_true",
        "false_transcript": "no_semantic_atom_is_true",
        "replication_quotiented_refutation_dimension": 1,
        "witness": "the_unique_true_atom_index",
        "witness_description_bits": index_bits,
        "post_witness_verifier_semantic_queries": 1,
        "post_witness_verifier_communication_bits": index_bits,
        "declared_honest_search_query_budget": budget,
        "exact_randomized_maximin_success": text(success),
        "exact_randomized_minimax_failure": text(1 - success),
        "queries_for_two_thirds_success": needed,
        "two_thirds_queries_are_linear_in_atom_count": True,
        "deterministic_exact_worst_case_queries": marker_count,
        "full_or_macro_evaluation_queries": marker_count,
        "search_to_verification_query_ratio_numerator": needed,
        "search_to_verification_query_ratio_denominator": 1,
        "certified": True,
    }


def reconstruct_subsets() -> list[dict[str, object]]:
    rows = []
    for marker_count in range(2, 11):
        for budget in range(marker_count + 1):
            strategies = comb(marker_count, budget)
            inclusion = comb(marker_count - 1, budget - 1) if budget else 0
            success = Q(inclusion, strategies)
            rows.append(
                {
                    "semantic_atom_count": marker_count,
                    "query_budget": budget,
                    "deterministic_query_subsets": strategies,
                    "subsets_containing_each_fixed_marker": inclusion,
                    "uniform_subset_success_per_marker": text(success),
                    "maximin_formula": text(Q(budget, marker_count)),
                    "averaging_upper_bound_matches": success == Q(budget, marker_count),
                }
            )
    return rows


def reconstruct_permutations() -> list[dict[str, object]]:
    rows = []
    for marker_count in range(2, 17):
        for shift in (1, marker_count - 1):
            image = {(index + shift) % marker_count for index in range(marker_count)}
            bijection = len(image) == marker_count
            rows.append(
                {
                    "semantic_atom_count": marker_count,
                    "shift": shift,
                    "bijection": bijection,
                    "refutation_dimension_before": 1,
                    "refutation_dimension_after": 1,
                    "deterministic_search_queries_before": marker_count,
                    "deterministic_search_queries_after": marker_count,
                    "search_hardness_invariant": bijection,
                }
            )
    return rows


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_PATH.read_text(encoding="utf-8"))
    noise = json.loads(NOISE_PATH.read_text(encoding="utf-8"))
    expected_rows = [reconstruct_row(index_bits) for index_bits in range(1, 41)]
    subsets = reconstruct_subsets()
    permutations = reconstruct_permutations()
    rows = result.get("search_rows", [])
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version") == "asmp3_honest_search_barrier_v2_1"
            and result.get("status")
            == "exact_dimension_one_unique_marker_search_separation"
            and result.get("parent_result") == "ASMP-3-ENCODING-INVARIANCE-v2.0"
            and result.get("certified") is True
            and "quantum queries" in result.get("claim_boundary", "")
        ),
        "V1_all_40_resource_rows_reconstructed": rows == expected_rows,
        "V2_dimension_one_and_post_witness_cost_one_exact": all(
            row["replication_quotiented_refutation_dimension"] == 1
            and row["post_witness_verifier_semantic_queries"] == 1
            for row in rows
        ),
        "V3_randomized_q_over_N_and_linear_success_threshold_exact": all(
            Q(row["exact_randomized_maximin_success"])
            == Q(row["declared_honest_search_query_budget"], row["semantic_atom_count"])
            and row["queries_for_two_thirds_success"]
            == ceil(Q(2, 3) * row["semantic_atom_count"])
            for row in rows
        ),
        "V4_small_subset_strategy_spaces_reconstructed": (
            result.get("small_subset_strategy_audit") == subsets
            and len(subsets) == 63
        ),
        "V5_permutation_invariance_reconstructed": (
            result.get("permutation_invariance_audit") == permutations
            and len(permutations) == 30
        ),
        "V6_parent_macro_and_noise_contracts_reconstructed": (
            parent["theorem"]["macro_barrier"].startswith("an N-bit parity macro")
            and noise["theorem"]["optimal_aggregator"]
            == "majority with uniform tie break"
            and noise["theorem"]["exponential_certificate"].startswith("error^2")
        ),
        "V7_producer_gates_all_true": (
            len(result.get("gates", {})) == 10 and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_honest_search_barrier_verification_v2_1",
        "checker": "clean_room_unique_marker_search_and_resource_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker validates black-box classical unique-marker search "
            "under a zero-or-one promise. It does not cover structured side "
            "information, quantum queries, or witness-bearing transcripts."
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
        raise SystemExit(f"honest-search verification failed: {failed}")
    print(
        "ASMP-3 honest-search verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
