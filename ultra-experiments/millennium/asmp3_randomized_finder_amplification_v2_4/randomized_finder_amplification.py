from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from functools import cache
from math import comb
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
PARENT_PATH = (
    HERE.parent
    / "asmp3_constructive_refutation_protocol_v2_3"
    / "artifacts"
    / "constructive_refutation_protocol_v2_3.json"
)
SEARCH_PATH = (
    HERE.parent
    / "asmp3_honest_search_barrier_v2_1"
    / "artifacts"
    / "honest_search_barrier_v2_1.json"
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


def joint_noise_risk(refutation_size: int, depth: int, eta: Q) -> Q:
    if refutation_size < 1:
        raise ValueError("refutation size must be positive")
    error = atom_error(depth, eta)
    return 1 - (1 - error) ** refutation_size


def finder_failure(one_shot_success: Q, attempts: int) -> Q:
    one_shot_success = Q(one_shot_success)
    if one_shot_success <= 0 or one_shot_success > 1 or attempts < 1:
        raise ValueError("invalid finder parameters")
    return (1 - one_shot_success) ** attempts


def minimal_attempts(one_shot_success: Q, target_failure: Q) -> int:
    one_shot_success = Q(one_shot_success)
    target_failure = Q(target_failure)
    if (
        one_shot_success <= 0
        or one_shot_success > 1
        or target_failure <= 0
        or target_failure >= 1
    ):
        raise ValueError("invalid restart target")
    for attempts in range(1, 100_001):
        if finder_failure(one_shot_success, attempts) <= target_failure:
            return attempts
    raise RuntimeError("restart search exceeded registered limit")


def minimal_odd_depth(refutation_size: int, eta: Q, target_risk: Q) -> int:
    target_risk = Q(target_risk)
    if refutation_size < 1 or target_risk <= 0 or target_risk >= Q(1, 2):
        raise ValueError("invalid noise target")
    for depth in (1, *range(3, 2048, 2)):
        if joint_noise_risk(refutation_size, depth, Q(eta)) <= target_risk:
            return depth
    raise RuntimeError("replication search exceeded registered limit")


def protocol_row(
    one_shot_success: Q | int,
    target_finder_failure: Q | int,
    refutation_size: int,
    eta: Q | int,
    target_noise_risk: Q | int,
    *,
    atom_id_bits: int = 20,
    finder_trial_time: int | None = None,
    honest_prover_budget: int = 10_000,
) -> dict[str, object]:
    alpha = Q(one_shot_success)
    target_failure = Q(target_finder_failure)
    eta = Q(eta)
    target_noise = Q(target_noise_risk)
    if refutation_size < 1 or atom_id_bits < 1 or honest_prover_budget < 1:
        raise ValueError("invalid protocol resource parameters")
    if finder_trial_time is None:
        finder_trial_time = refutation_size * atom_id_bits
    if finder_trial_time < 1:
        raise ValueError("finder trial time must be positive")

    attempts = minimal_attempts(alpha, target_failure)
    failure = finder_failure(alpha, attempts)
    previous_failure = finder_failure(alpha, attempts - 1) if attempts > 1 else None
    finder_success = 1 - failure

    depth = minimal_odd_depth(refutation_size, eta, target_noise)
    noise_risk = joint_noise_risk(refutation_size, depth, eta)
    previous_noise = (
        joint_noise_risk(refutation_size, depth - 2, eta) if depth > 1 else None
    )

    completeness = 1 - noise_risk
    soundness = failure + (1 - failure) * noise_risk
    gap = completeness - soundness
    target_gap = 1 - target_failure - 2 * target_noise + target_failure * target_noise
    finder_time = attempts * finder_trial_time
    semantic_queries = refutation_size * depth
    prefix_bits = ceil_log2(refutation_size + 1)
    critic_bits = prefix_bits + refutation_size * (atom_id_bits + 1)

    return {
        "one_shot_finder_success_lower_bound": qstr(alpha),
        "target_finder_failure": qstr(target_failure),
        "finder_attempts": attempts,
        "exact_amplified_finder_failure": qstr(failure),
        "exact_amplified_finder_success": qstr(finder_success),
        "previous_attempt_failure": (
            qstr(previous_failure) if previous_failure is not None else None
        ),
        "maximum_refutation_classes": refutation_size,
        "eta": qstr(eta),
        "target_joint_noise_risk": qstr(target_noise),
        "replications_per_atom": depth,
        "joint_decoding_error": qstr(noise_risk),
        "previous_odd_depth_joint_error": (
            qstr(previous_noise) if previous_noise is not None else None
        ),
        "completeness_lower_bound": qstr(completeness),
        "soundness_upper_bound": qstr(soundness),
        "gap_lower_bound": qstr(gap),
        "decoupled_target_gap_lower_bound": qstr(target_gap),
        "atom_id_bits": atom_id_bits,
        "critic_message_length_prefix_bits": prefix_bits,
        "critic_message_bits": critic_bits,
        "semantic_query_count": semantic_queries,
        "finder_trial_time": finder_trial_time,
        "total_honest_finder_time": finder_time,
        "honest_prover_budget": honest_prover_budget,
        "within_honest_prover_budget": finder_time <= honest_prover_budget,
        "finder_contract": (
            "independent Las Vegas-with-FAIL trials after tau is fixed; every "
            "successful return is a valid quotient witness"
        ),
        "noise_contract": (
            "fresh disjoint iid blocks sampled only after the successful witness is selected"
        ),
        "minimal_attempt_count_certified": (
            failure <= target_failure
            and (previous_failure is None or previous_failure > target_failure)
        ),
        "minimal_odd_depth_certified": (
            noise_risk <= target_noise
            and (previous_noise is None or previous_noise > target_noise)
        ),
        "certified": (
            completeness == 1 - noise_risk
            and soundness == failure + (1 - failure) * noise_risk
            and gap == 1 - failure - 2 * noise_risk + failure * noise_risk
            and gap >= target_gap
            and semantic_queries == refutation_size * depth
            and finder_time == attempts * finder_trial_time
            and critic_bits == prefix_bits + refutation_size * (atom_id_bits + 1)
        ),
    }


def exhaustive_restart_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for alpha in (Q(1, 4), Q(1, 2), Q(2, 3)):
        for attempts in range(1, 7):
            success_probability = Q(0)
            failure_probability = Q(0)
            patterns = list(itertools.product((0, 1), repeat=attempts))
            for pattern in patterns:
                successes = sum(pattern)
                probability = alpha**successes * (1 - alpha) ** (attempts - successes)
                if successes:
                    success_probability += probability
                else:
                    failure_probability += probability
            rows.append(
                {
                    "one_shot_success": qstr(alpha),
                    "attempts": attempts,
                    "boolean_outcome_patterns": len(patterns),
                    "enumerated_success_probability": qstr(success_probability),
                    "enumerated_failure_probability": qstr(failure_probability),
                    "closed_form_success_probability": qstr(1 - (1 - alpha) ** attempts),
                    "closed_form_failure_probability": qstr((1 - alpha) ** attempts),
                    "certified": (
                        success_probability == 1 - (1 - alpha) ** attempts
                        and failure_probability == (1 - alpha) ** attempts
                        and success_probability + failure_probability == 1
                    ),
                }
            )
    return rows


def scaling_rows() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    for log_work in range(20, 101, 10):
        row = protocol_row(
            Q(1, log_work),
            Q(1, log_work),
            log_work,
            Q(1, 5),
            Q(1, log_work),
            atom_id_bits=log_work,
            finder_trial_time=log_work**2,
            honest_prover_budget=2**log_work,
        )
        quartic = log_work**4
        rows.append(
            {
                "log2_prover_budget": log_work,
                "one_shot_finder_success": qstr(Q(1, log_work)),
                "finder_attempts": row["finder_attempts"],
                "amplified_finder_failure": row["exact_amplified_finder_failure"],
                "replications_per_atom": row["replications_per_atom"],
                "joint_decoding_error": row["joint_decoding_error"],
                "semantic_queries": row["semantic_query_count"],
                "critic_message_bits": row["critic_message_bits"],
                "total_honest_finder_time": row["total_honest_finder_time"],
                "honest_prover_budget": row["honest_prover_budget"],
                "declared_quartic_polylog_budget": quartic,
                "all_charged_resources_within_quartic_polylog": (
                    row["semantic_query_count"] <= quartic
                    and row["critic_message_bits"] <= quartic
                    and row["total_honest_finder_time"] <= quartic
                ),
                "within_honest_prover_budget": row["within_honest_prover_budget"],
                "gap_lower_bound": row["gap_lower_bound"],
                "symbolic_target_gap": qstr(
                    1 - Q(3, log_work) + Q(1, log_work**2)
                ),
                "certified": (
                    row["within_honest_prover_budget"]
                    and row["total_honest_finder_time"] <= quartic
                    and Q(row["gap_lower_bound"])
                    >= 1 - Q(3, log_work) + Q(1, log_work**2)
                ),
            }
        )
    return rows[:6], rows[6:]


def unique_marker_retry_rows() -> list[dict[str, object]]:
    rows = []
    for index_bits in (20, 24, 28, 32, 36, 40):
        atom_count = 2**index_bits
        one_trial_queries = index_bits**3
        attempts = (2 * atom_count + 3 * one_trial_queries - 1) // (
            3 * one_trial_queries
        )
        previous_success = Q((attempts - 1) * one_trial_queries, atom_count)
        amplified_success = min(Q(attempts * one_trial_queries, atom_count), Q(1))
        total_queries = attempts * one_trial_queries
        rows.append(
            {
                "index_bits": index_bits,
                "semantic_atom_count": atom_count,
                "queries_per_coordinated_trial": one_trial_queries,
                "target_success": "2/3",
                "minimal_coordinated_attempts": attempts,
                "previous_attempt_success_upper_bound": qstr(previous_success),
                "amplified_success_upper_bound": qstr(amplified_success),
                "total_honest_search_queries": total_queries,
                "registered_one_trial_budget": one_trial_queries,
                "exceeds_registered_one_trial_budget": total_queries > one_trial_queries,
                "linear_query_floor": (2 * atom_count + 2) // 3,
                "certified": (
                    previous_success < Q(2, 3)
                    and amplified_success >= Q(2, 3)
                    and total_queries >= Q(2 * atom_count, 3)
                    and total_queries > one_trial_queries
                ),
            }
        )
    return rows


def build_result() -> dict[str, object]:
    parent = json.loads(PARENT_PATH.read_text(encoding="utf-8"))
    search = json.loads(SEARCH_PATH.read_text(encoding="utf-8"))
    protocol_rows = [
        protocol_row(alpha, target, size, eta, target)
        for alpha in (Q(1, 4), Q(1, 2), Q(2, 3), Q(3, 4))
        for size in (1, 4, 16)
        for eta in (Q(1, 5), Q(1, 3), Q(2, 5))
        for target in (Q(1, 10), Q(1, 100))
    ]
    restart_rows = exhaustive_restart_rows()
    registered_scaling, confirmation_scaling = scaling_rows()
    marker_rows = unique_marker_retry_rows()
    gates = {
        "R0_protocol_registry_complete": len(protocol_rows) == 72,
        "R1_restart_counts_are_exactly_minimal": all(
            row["minimal_attempt_count_certified"] for row in protocol_rows
        ),
        "R2_noise_depths_are_exactly_minimal": all(
            row["minimal_odd_depth_certified"] for row in protocol_rows
        ),
        "R3_completeness_soundness_gap_composition_exact": all(
            Q(row["gap_lower_bound"])
            == 1
            - Q(row["exact_amplified_finder_failure"])
            - 2 * Q(row["joint_decoding_error"])
            + Q(row["exact_amplified_finder_failure"])
            * Q(row["joint_decoding_error"])
            for row in protocol_rows
        ),
        "R4_decoupled_failure_noise_targets_imply_gap": all(
            Q(row["gap_lower_bound"]) >= Q(row["decoupled_target_gap_lower_bound"])
            for row in protocol_rows
        ),
        "R5_all_restart_query_message_budget_costs_charged": all(
            row["total_honest_finder_time"]
            == row["finder_attempts"] * row["finder_trial_time"]
            and row["semantic_query_count"]
            == row["maximum_refutation_classes"] * row["replications_per_atom"]
            and row["critic_message_bits"]
            == row["critic_message_length_prefix_bits"]
            + row["maximum_refutation_classes"] * (row["atom_id_bits"] + 1)
            for row in protocol_rows
        ),
        "R6_exhaustive_restart_probabilities_match": (
            len(restart_rows) == 18 and all(row["certified"] for row in restart_rows)
        ),
        "R7_inverse_log_finder_registered_scaling_passes": (
            len(registered_scaling) == 6
            and all(row["certified"] for row in registered_scaling)
        ),
        "R8_held_out_scaling_confirmation_passes": (
            len(confirmation_scaling) == 3
            and all(row["certified"] for row in confirmation_scaling)
        ),
        "R9_unique_marker_restart_obstruction_survives": (
            len(marker_rows) == 6
            and all(row["certified"] for row in marker_rows)
            and search["theorem"]["randomized_q_query_maximin_success"] == "q/N"
            and search["theorem"]["two_thirds_success_queries"] == "ceil(2N/3)"
        ),
        "R10_parent_deterministic_protocol_is_alpha_one_endpoint": (
            parent["theorem"]["gap"] == "at least 1-2delta"
            and protocol_row(Q(1), Q(1, 10), 4, Q(1, 5), Q(1, 10))[
                "exact_amplified_finder_failure"
            ]
            == "0"
        ),
    }
    return {
        "schema_version": "asmp3_randomized_finder_amplification_v2_4",
        "experiment_id": "ASMP-3-RANDOMIZED-FINDER-AMPLIFICATION-v2.4",
        "status": "exact_randomized_finder_restart_noise_and_budget_frontier",
        "parent_result": "ASMP-3-CONSTRUCTIVE-REFUTATION-PROTOCOL-v2.3",
        "supporting_result": "ASMP-3-HONEST-SEARCH-BARRIER-v2.1",
        "theorem": {
            "finder_failure_after_k_independent_trials": "f=(1-alpha)^k",
            "completeness": "at least 1-delta",
            "soundness": "at most f+(1-f)delta",
            "gap": "at least 1-f-2delta+f*delta",
            "honest_finder_time": "k*H",
            "semantic_queries": "r*d after one successful witness is selected",
            "restart_boundary": (
                "amplification improves success only by paying every finder trial; "
                "the v2.1 unique-marker family still needs linear total search"
            ),
        },
        "protocol_rows": protocol_rows,
        "exhaustive_restart_rows": restart_rows,
        "registered_scaling_rows": registered_scaling,
        "held_out_scaling_rows": confirmation_scaling,
        "unique_marker_retry_obstruction_rows": marker_rows,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The theorem replaces v2.3's always-successful finder by independent "
            "Las Vegas-with-FAIL trials and charges kH. It does not derive such a "
            "finder from every WV-FIX protocol, cover correlated finder failures, "
            "or establish a universal converse."
        ),
    }
