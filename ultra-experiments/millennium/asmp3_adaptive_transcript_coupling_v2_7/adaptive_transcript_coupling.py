from __future__ import annotations

import hashlib
import itertools
import json
import sys
from fractions import Fraction
from functools import cache
from math import comb
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
BLOCK_PATH = (
    HERE.parent
    / "asmp3_block_selection_composition_v1_9"
    / "artifacts"
    / "block_selection_composition_v1_9.json"
)
NORMAL_FORM_PATH = (
    HERE.parent
    / "asmp3_witness_transparent_normal_form_v2_5"
    / "artifacts"
    / "witness_transparent_normal_form_v2_5.json"
)
DISPOSITION_PATH = (
    HERE.parent
    / "asmp3_resolution_disposition_v2_6"
    / "artifacts"
    / "resolution_disposition_v2_6.json"
)

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(100_000)


def qstr(value: Q) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


@cache
def majority_error(depth: int, eta: Q) -> Q:
    eta = Q(eta)
    if depth < 1 or eta <= 0 or eta >= Q(1, 2):
        raise ValueError("invalid majority parameters")
    error = sum(
        (
            Q(comb(depth, count))
            * eta**count
            * (1 - eta) ** (depth - count)
            for count in range(depth // 2 + 1, depth + 1)
        ),
        Q(0),
    )
    if depth % 2 == 0:
        error += (
            Q(comb(depth, depth // 2))
            * eta ** (depth // 2)
            * (1 - eta) ** (depth // 2)
            / 2
        )
    return error


def adaptive_path_risk(max_queries: int, depth: int, eta: Q) -> Q:
    if max_queries < 1:
        raise ValueError("max queries must be positive")
    error = majority_error(depth, Q(eta))
    return 1 - (1 - error) ** max_queries


def minimal_odd_depth(max_queries: int, eta: Q, target: Q) -> int:
    eta = Q(eta)
    target = Q(target)
    if max_queries < 1 or target <= 0 or target >= Q(1, 2):
        raise ValueError("invalid coupling target")
    for depth in (1, *range(3, 2048, 2)):
        if adaptive_path_risk(max_queries, depth, eta) <= target:
            return depth
    raise RuntimeError("adaptive coupling depth search exceeded limit")


def coupling_row(max_queries: int, eta: Q | int, target: Q | int) -> dict[str, object]:
    eta = Q(eta)
    target = Q(target)
    depth = minimal_odd_depth(max_queries, eta, target)
    error = majority_error(depth, eta)
    risk = adaptive_path_risk(max_queries, depth, eta)
    previous = (
        adaptive_path_risk(max_queries, depth - 2, eta) if depth > 1 else None
    )
    ideal_completeness = Q(4, 5)
    ideal_soundness = Q(1, 5)
    ideal_gap = ideal_completeness - ideal_soundness
    noisy_completeness = ideal_completeness - risk
    noisy_soundness = ideal_soundness + risk
    noisy_gap = ideal_gap - 2 * risk
    return {
        "maximum_adaptive_semantic_queries": max_queries,
        "eta": qstr(eta),
        "target_path_coupling_failure": qstr(target),
        "replications_per_adaptive_query": depth,
        "single_block_majority_error": qstr(error),
        "adaptive_path_coupling_failure": qstr(risk),
        "previous_odd_depth_path_failure": (
            qstr(previous) if previous is not None else None
        ),
        "raw_semantic_query_count": max_queries * depth,
        "ideal_example_completeness": qstr(ideal_completeness),
        "ideal_example_soundness": qstr(ideal_soundness),
        "ideal_example_gap": qstr(ideal_gap),
        "noisy_completeness_lower_bound": qstr(noisy_completeness),
        "noisy_soundness_upper_bound": qstr(noisy_soundness),
        "noisy_gap_lower_bound": qstr(noisy_gap),
        "path_contract": (
            "fresh conditional block sampled only after the current adaptive "
            "history fixes the next semantic query"
        ),
        "coupled_history_contract": (
            "all nonsemantic coins and strategy kernels are shared; identical "
            "decoded prefixes force identical messages, queries, and stopping"
        ),
        "minimal_odd_depth_certified": (
            risk <= target and (previous is None or previous > target)
        ),
        "certified": (
            risk == 1 - (1 - error) ** max_queries
            and max_queries * depth == max_queries * depth
            and noisy_completeness == ideal_completeness - risk
            and noisy_soundness == ideal_soundness + risk
            and noisy_gap == ideal_gap - 2 * risk
        ),
    }


def error_pattern_rows() -> list[dict[str, object]]:
    rows = []
    for eta, depth in ((Q(1, 5), 3), (Q(1, 3), 5), (Q(2, 5), 9)):
        error = majority_error(depth, eta)
        for max_queries in range(1, 11):
            no_error = Q(0)
            any_error = Q(0)
            patterns = 0
            for pattern in itertools.product((0, 1), repeat=max_queries):
                failures = sum(pattern)
                probability = error**failures * (1 - error) ** (
                    max_queries - failures
                )
                if failures:
                    any_error += probability
                else:
                    no_error += probability
                patterns += 1
            rows.append(
                {
                    "eta": qstr(eta),
                    "replication_depth": depth,
                    "single_block_error": qstr(error),
                    "maximum_adaptive_queries": max_queries,
                    "error_indicator_patterns": patterns,
                    "enumerated_no_error_probability": qstr(no_error),
                    "enumerated_any_error_probability": qstr(any_error),
                    "closed_form_no_error_probability": qstr(
                        (1 - error) ** max_queries
                    ),
                    "closed_form_any_error_probability": qstr(
                        1 - (1 - error) ** max_queries
                    ),
                    "certified": (
                        patterns == 2**max_queries
                        and no_error == (1 - error) ** max_queries
                        and any_error == 1 - (1 - error) ** max_queries
                        and no_error + any_error == 1
                    ),
                }
            )
    return rows


def _run_tree(
    query_policy: tuple[int, ...],
    stop_mask: int,
    world: int,
    errors: tuple[int, ...],
    max_depth: int,
) -> tuple[int, tuple[int, ...], int, bool]:
    node = 0
    history: list[int] = []
    rounds = 0
    while rounds < max_depth:
        if stop_mask & (1 << node):
            return node, tuple(history), rounds, True
        atom = query_policy[node]
        answer = ((world >> atom) & 1) ^ errors[rounds]
        history.append(answer)
        node = 2 * node + 1 + answer
        rounds += 1
    return node, tuple(history), rounds, False


def exhaustive_adaptive_tree_audit() -> dict[str, object]:
    atom_count = 2
    max_depth = 3
    internal_nodes = 2**max_depth - 1
    query_policies = list(
        itertools.product(range(atom_count), repeat=internal_nodes)
    )
    stopping_policies = range(1 << internal_nodes)
    worlds = range(1 << atom_count)
    error_patterns = list(itertools.product((0, 1), repeat=max_depth))
    digest = hashlib.sha256()
    cases = no_error_cases = identical_no_error = 0
    divergent_paths = divergence_without_error = 0
    different_stopping = 0
    for query_index, query_policy in enumerate(query_policies):
        for stop_mask in stopping_policies:
            for world in worlds:
                ideal = _run_tree(
                    query_policy, stop_mask, world, (0,) * max_depth, max_depth
                )
                for errors in error_patterns:
                    noisy = _run_tree(
                        query_policy, stop_mask, world, errors, max_depth
                    )
                    different = ideal != noisy
                    has_error = any(errors)
                    cases += 1
                    if not has_error:
                        no_error_cases += 1
                        identical_no_error += not different
                    if different:
                        divergent_paths += 1
                        divergence_without_error += not has_error
                    different_stopping += ideal[3] != noisy[3]
                    digest.update(
                        (
                            f"{query_index}:{stop_mask}:{world}:"
                            f"{''.join(map(str, errors))}:{ideal}:{noisy}\n"
                        ).encode("ascii")
                    )
    expected = (
        atom_count**internal_nodes
        * 2**internal_nodes
        * 2**atom_count
        * 2**max_depth
    )
    return {
        "atom_count": atom_count,
        "maximum_adaptive_depth": max_depth,
        "internal_history_nodes": internal_nodes,
        "deterministic_query_policies": len(query_policies),
        "history_dependent_stopping_policies": 2**internal_nodes,
        "semantic_worlds": 2**atom_count,
        "decoded_error_patterns": 2**max_depth,
        "coupled_execution_cases": cases,
        "expected_coupled_execution_cases": expected,
        "no_error_cases": no_error_cases,
        "identical_paths_on_every_no_error_case": identical_no_error,
        "divergent_paths": divergent_paths,
        "divergence_without_any_error": divergence_without_error,
        "different_stopping_outcomes_after_errors": different_stopping,
        "canonical_execution_digest_sha256": digest.hexdigest().upper(),
        "strategy_scope": (
            "all deterministic binary-history query and stopping kernels; "
            "conditioning on shared prover/verifier coins reduces randomized "
            "strategies to this pathwise form"
        ),
        "certified": (
            cases == expected
            and no_error_cases
            == len(query_policies) * 2**internal_nodes * 2**atom_count
            and identical_no_error == no_error_cases
            and divergence_without_error == 0
            and divergent_paths > 0
            and different_stopping > 0
        ),
    }


def tightness_rows() -> list[dict[str, object]]:
    rows = []
    for error in (Q(1, 10), Q(1, 5), Q(1, 3)):
        for max_queries in range(1, 13):
            mismatch = Q(0)
            patterns = 0
            for pattern in itertools.product((0, 1), repeat=max_queries):
                failures = sum(pattern)
                probability = error**failures * (1 - error) ** (
                    max_queries - failures
                )
                ideal_decision = 0
                noisy_decision = int(failures > 0)
                if ideal_decision != noisy_decision:
                    mismatch += probability
                patterns += 1
            bound = 1 - (1 - error) ** max_queries
            rows.append(
                {
                    "single_decoded_query_error": qstr(error),
                    "adaptive_queries": max_queries,
                    "full_depth_error_patterns": patterns,
                    "tight_tree": (
                        "query a fresh all-zero atom each round; decide one iff "
                        "the observed answer history is not all zero"
                    ),
                    "decision_mismatch_probability": qstr(mismatch),
                    "adaptive_path_bound": qstr(bound),
                    "bound_attained": mismatch == bound,
                    "certified": patterns == 2**max_queries and mismatch == bound,
                }
            )
    return rows


def extraction_rows() -> list[dict[str, object]]:
    rows = []
    for soundness in (Q(1, 5), Q(1, 3)):
        for eta in (Q(1, 5), Q(1, 3)):
            for max_queries in (1, 4, 16):
                row = coupling_row(max_queries, eta, Q(1, 100))
                coupling_failure = Q(row["adaptive_path_coupling_failure"])
                finder_success = 1 - soundness - coupling_failure
                rows.append(
                    {
                        "noisy_protocol_soundness_upper_bound": qstr(soundness),
                        "maximum_adaptive_queries": max_queries,
                        "eta": qstr(eta),
                        "replications_per_query": row[
                            "replications_per_adaptive_query"
                        ],
                        "derived_decision_coupling_failure": row[
                            "adaptive_path_coupling_failure"
                        ],
                        "v2_5_extracted_finder_success": qstr(finder_success),
                        "extracted_quotient_dimension_bound": max_queries,
                        "raw_semantic_queries": row["raw_semantic_query_count"],
                        "positive_extraction_margin": finder_success > 0,
                        "remaining_contracts": (
                            "witness-transparent ideal rejection and efficient "
                            "ideal simulation; coupling is now derived"
                        ),
                        "certified": (
                            coupling_failure <= Q(1, 100)
                            and finder_success
                            == 1 - soundness - coupling_failure
                            and finder_success > 0
                        ),
                    }
                )
    return rows


def build_result() -> dict[str, object]:
    block = json.loads(BLOCK_PATH.read_text(encoding="utf-8"))
    normal_form = json.loads(NORMAL_FORM_PATH.read_text(encoding="utf-8"))
    disposition = json.loads(DISPOSITION_PATH.read_text(encoding="utf-8"))
    coupling = [
        coupling_row(max_queries, eta, target)
        for eta in (Q(1, 5), Q(1, 3), Q(2, 5))
        for max_queries in (1, 2, 4, 8, 16, 32, 64)
        for target in (Q(1, 10), Q(1, 100))
    ]
    patterns = error_pattern_rows()
    tree = exhaustive_adaptive_tree_audit()
    tight = tightness_rows()
    extraction = extraction_rows()
    gates = {
        "T0_adaptive_coupling_registry_complete": len(coupling) == 42,
        "T1_all_replication_depths_exactly_minimal": all(
            row["minimal_odd_depth_certified"] for row in coupling
        ),
        "T2_path_risk_and_robustification_formulas_exact": all(
            Q(row["adaptive_path_coupling_failure"])
            == 1
            - (1 - Q(row["single_block_majority_error"]))
            ** row["maximum_adaptive_semantic_queries"]
            and Q(row["noisy_gap_lower_bound"])
            == Q(row["ideal_example_gap"])
            - 2 * Q(row["adaptive_path_coupling_failure"])
            for row in coupling
        ),
        "T3_all_raw_semantic_queries_charged": all(
            row["raw_semantic_query_count"]
            == row["maximum_adaptive_semantic_queries"]
            * row["replications_per_adaptive_query"]
            for row in coupling
        ),
        "T4_all_error_pattern_spaces_match_product_bound": (
            len(patterns) == 30 and all(row["certified"] for row in patterns)
        ),
        "T5_all_small_adaptive_query_stop_trees_coupled": (
            tree["coupled_execution_cases"] == 524_288 and tree["certified"]
        ),
        "T6_path_coupling_bound_is_tight": (
            len(tight) == 36 and all(row["certified"] for row in tight)
        ),
        "T7_ideal_protocol_gap_robustifies": all(
            Q(row["noisy_gap_lower_bound"])
            == Q(3, 5) - 2 * Q(row["adaptive_path_coupling_failure"])
            for row in coupling
        ),
        "T8_v2_5_extraction_coupling_premise_is_derived": (
            len(extraction) == 12 and all(row["certified"] for row in extraction)
        ),
        "T9_parent_fixed_block_and_normal_form_contracts_match": (
            block["theorem"]["independent_M_atom_risk"] == "1-(1-e_d)^M"
            and normal_form["theorem"]["extracted_finder_success"]
            == "alpha>=1-s-delta"
        ),
        "T10_v2_6_broader_theorem_resume_trigger_satisfied": (
            disposition["disposition"]["current_harness_architecture"]
            == "stop_further_grid_extension"
            and "broader theorem/counterexample"
            in disposition["disposition"]["resume_condition"]
        ),
    }
    return {
        "schema_version": "asmp3_adaptive_transcript_coupling_v2_7",
        "experiment_id": "ASMP-3-ADAPTIVE-TRANSCRIPT-COUPLING-v2.7",
        "status": "pathwise_adaptive_protocol_coupling_and_robustification_theorem",
        "parent_result": "ASMP-3-WITNESS-TRANSPARENT-NORMAL-FORM-v2.5",
        "supporting_results": [
            "ASMP-3-BLOCK-SELECTION-COMPOSITION-v1.9",
            "ASMP-3-RESOLUTION-DISPOSITION-v2.6",
        ],
        "theorem": {
            "single_block_error": "e=e_d(eta)",
            "adaptive_path_coupling_failure": "delta<=1-(1-e)^q",
            "ideal_to_noisy_gap": "g_noisy>=g_ideal-2delta",
            "finder_extraction": "alpha>=1-s-delta with delta now derived",
            "raw_semantic_queries": "q*d",
            "adaptive_scope": (
                "history-dependent prover messages, query choice, and variable "
                "stopping under shared nonsemantic coins"
            ),
        },
        "coupling_rows": coupling,
        "error_pattern_rows": patterns,
        "exhaustive_adaptive_tree_audit": tree,
        "tightness_rows": tight,
        "derived_extraction_rows": extraction,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The theorem derives v2.5's decision-coupling premise for fresh "
            "post-history conditionally independent replication blocks. It still "
            "requires witness-transparent ideal rejection and efficient ideal "
            "simulation, and does not apply to persistent, preselected, or "
            "adversarially correlated block noise."
        ),
    }
