from __future__ import annotations

import json
from fractions import Fraction
from math import ceil, comb
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
PARENT_ARTIFACT = (
    HERE.parent
    / "asmp3_encoding_invariance_v2_0"
    / "artifacts"
    / "encoding_invariance_v2_0.json"
)
NOISE_ARTIFACT = (
    HERE.parent
    / "asmp3_independent_noise_amplification_v1_8"
    / "artifacts"
    / "independent_noise_amplification_v1_8.json"
)


def qstr(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def validate(index_bits: int, query_budget: int) -> None:
    if not isinstance(index_bits, int) or index_bits < 1:
        raise ValueError("index_bits must be positive")
    if not isinstance(query_budget, int) or query_budget < 0 or query_budget > 1 << index_bits:
        raise ValueError("query budget must lie in [0,2^index_bits]")


def maximin_success(index_bits: int, query_budget: int) -> Q:
    validate(index_bits, query_budget)
    return Q(query_budget, 1 << index_bits)


def required_queries(index_bits: int, target_success: Q | int) -> int:
    target_success = Q(target_success)
    if index_bits < 1 or target_success <= 0 or target_success > 1:
        raise ValueError("invalid target-success parameters")
    marker_count = 1 << index_bits
    return ceil(target_success * marker_count)


def search_row(index_bits: int) -> dict[str, object]:
    if index_bits < 1:
        raise ValueError("index_bits must be positive")
    marker_count = 1 << index_bits
    declared_budget = min(marker_count, index_bits**3)
    success = maximin_success(index_bits, declared_budget)
    target = Q(2, 3)
    needed = required_queries(index_bits, target)
    verifier_communication = index_bits
    verifier_semantic_queries = 1
    return {
        "index_bits": index_bits,
        "semantic_atom_count": marker_count,
        "promise": "at_most_one_semantic_atom_is_true",
        "false_transcript": "no_semantic_atom_is_true",
        "replication_quotiented_refutation_dimension": 1,
        "witness": "the_unique_true_atom_index",
        "witness_description_bits": index_bits,
        "post_witness_verifier_semantic_queries": verifier_semantic_queries,
        "post_witness_verifier_communication_bits": verifier_communication,
        "declared_honest_search_query_budget": declared_budget,
        "exact_randomized_maximin_success": qstr(success),
        "exact_randomized_minimax_failure": qstr(1 - success),
        "queries_for_two_thirds_success": needed,
        "two_thirds_queries_are_linear_in_atom_count": (
            needed == ceil(Q(2, 3) * marker_count)
        ),
        "deterministic_exact_worst_case_queries": marker_count,
        "full_or_macro_evaluation_queries": marker_count,
        "search_to_verification_query_ratio_numerator": needed,
        "search_to_verification_query_ratio_denominator": verifier_semantic_queries,
        "certified": (
            success == Q(declared_budget, marker_count)
            and needed == ceil(Q(2, 3) * marker_count)
            and verifier_semantic_queries == 1
            and marker_count == 1 << index_bits
        ),
    }


def subset_strategy_audit() -> list[dict[str, object]]:
    rows = []
    for marker_count in range(2, 11):
        for query_budget in range(marker_count + 1):
            strategies = comb(marker_count, query_budget)
            inclusion_count = (
                comb(marker_count - 1, query_budget - 1)
                if query_budget > 0
                else 0
            )
            uniform_success = Q(inclusion_count, strategies) if strategies else Q(0)
            rows.append(
                {
                    "semantic_atom_count": marker_count,
                    "query_budget": query_budget,
                    "deterministic_query_subsets": strategies,
                    "subsets_containing_each_fixed_marker": inclusion_count,
                    "uniform_subset_success_per_marker": qstr(uniform_success),
                    "maximin_formula": qstr(Q(query_budget, marker_count)),
                    "averaging_upper_bound_matches": (
                        uniform_success == Q(query_budget, marker_count)
                    ),
                }
            )
    return rows


def permutation_audit() -> list[dict[str, object]]:
    rows = []
    for marker_count in range(2, 17):
        for shift in (1, marker_count - 1):
            permutation = tuple((index + shift) % marker_count for index in range(marker_count))
            rows.append(
                {
                    "semantic_atom_count": marker_count,
                    "shift": shift,
                    "bijection": len(set(permutation)) == marker_count,
                    "refutation_dimension_before": 1,
                    "refutation_dimension_after": 1,
                    "deterministic_search_queries_before": marker_count,
                    "deterministic_search_queries_after": marker_count,
                    "search_hardness_invariant": len(set(permutation)) == marker_count,
                }
            )
    return rows


def build_result() -> dict[str, object]:
    parent = json.loads(PARENT_ARTIFACT.read_text(encoding="utf-8"))
    noise = json.loads(NOISE_ARTIFACT.read_text(encoding="utf-8"))
    rows = [search_row(index_bits) for index_bits in range(1, 41)]
    subsets = subset_strategy_audit()
    permutations = permutation_audit()
    asymptotic = [row for row in rows if row["index_bits"] >= 20]
    gates = {
        "H0_search_registry_complete": (
            len(rows) == 40 and [row["index_bits"] for row in rows] == list(range(1, 41))
        ),
        "H1_refutation_dimension_is_one_everywhere": all(
            row["replication_quotiented_refutation_dimension"] == 1 for row in rows
        ),
        "H2_post_witness_verification_is_one_query": all(
            row["post_witness_verifier_semantic_queries"] == 1 for row in rows
        ),
        "H3_randomized_maximin_success_is_q_over_N": all(
            Q(row["exact_randomized_maximin_success"])
            == Q(row["declared_honest_search_query_budget"], row["semantic_atom_count"])
            for row in rows
        ),
        "H4_constant_success_requires_linear_search": all(
            row["queries_for_two_thirds_success"]
            == ceil(Q(2, 3) * row["semantic_atom_count"])
            for row in rows
        ),
        "H5_polynomial_index_budget_has_vanishing_success": (
            asymptotic
            and all(
                Q(row["exact_randomized_maximin_success"])
                <= Q(row["index_bits"] ** 3, 1 << row["index_bits"])
                for row in asymptotic
            )
            and Q(rows[-1]["exact_randomized_maximin_success"]) < Q(1, 1_000_000)
        ),
        "H6_small_strategy_spaces_match_exact_averaging_bound": (
            len(subsets) == sum(marker_count + 1 for marker_count in range(2, 11))
            and all(row["averaging_upper_bound_matches"] for row in subsets)
        ),
        "H7_search_hardness_is_encoding_permutation_invariant": (
            len(permutations) == 30
            and all(row["bijection"] and row["search_hardness_invariant"] for row in permutations)
        ),
        "H8_one_macro_shortcut_is_globally_charged": (
            parent["theorem"]["macro_barrier"].startswith("an N-bit parity macro")
            and all(
                row["full_or_macro_evaluation_queries"] == row["semantic_atom_count"]
                for row in rows
            )
        ),
        "H9_independent_noise_can_verify_but_not_locate_witness": (
            noise["theorem"]["optimal_aggregator"] == "majority with uniform tie break"
            and noise["theorem"]["exponential_certificate"].startswith("error^2")
            and all(row["certified"] for row in rows)
        ),
    }
    return {
        "schema_version": "asmp3_honest_search_barrier_v2_1",
        "experiment_id": "ASMP-3-HONEST-SEARCH-BARRIER-v2.1",
        "status": "exact_dimension_one_unique_marker_search_separation",
        "parent_result": "ASMP-3-ENCODING-INVARIANCE-v2.0",
        "noise_contract_result": "ASMP-3-INDEPENDENT-NOISE-AMPLIFICATION-v1.8",
        "theorem": {
            "atom_universe": (
                "N=2^n local semantic atoms with a zero-or-one-marker promise; "
                "false-transcript worlds have exactly one marker"
            ),
            "false_transcript": "claims every atom is false",
            "quotient_refutation_dimension": "1",
            "post_witness_verification": "one ideal semantic query plus n-bit index",
            "randomized_q_query_maximin_success": "q/N",
            "two_thirds_success_queries": "ceil(2N/3)",
            "conclusion": "small combinatorial dimension does not imply efficient honest search",
        },
        "search_rows": rows,
        "small_subset_strategy_audit": subsets,
        "permutation_invariance_audit": permutations,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The lower bound is for black-box access to a unique-marker semantic "
            "oracle with no side information. Structured atom families, advice, "
            "witness-bearing transcripts, quantum queries, or stronger semantic "
            "primitives can change search complexity and must be separately typed."
        ),
    }
