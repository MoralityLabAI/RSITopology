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
RESULT_PATH = HERE / "artifacts" / "randomized_finder_amplification_v2_4.json"
OUTPUT_PATH = (
    HERE / "artifacts" / "randomized_finder_amplification_verification_v2_4.json"
)
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


def text(value: Q) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


@cache
def majority_error(depth: int, eta: Q) -> Q:
    value = sum(
        (
            Q(comb(depth, count))
            * eta**count
            * (1 - eta) ** (depth - count)
            for count in range(depth // 2 + 1, depth + 1)
        ),
        Q(0),
    )
    if depth % 2 == 0:
        value += (
            Q(comb(depth, depth // 2))
            * eta ** (depth // 2)
            * (1 - eta) ** (depth // 2)
            / 2
        )
    return value


def noise_risk(size: int, depth: int, eta: Q) -> Q:
    return 1 - (1 - majority_error(depth, eta)) ** size


def min_attempts(alpha: Q, target: Q) -> int:
    for count in range(1, 100_001):
        if (1 - alpha) ** count <= target:
            return count
    raise RuntimeError("verification restart search exceeded limit")


def min_depth(size: int, eta: Q, target: Q) -> int:
    for depth in (1, *range(3, 2048, 2)):
        if noise_risk(size, depth, eta) <= target:
            return depth
    raise RuntimeError("verification depth search exceeded limit")


def reconstruct_row(
    alpha: Q,
    target_failure: Q,
    size: int,
    eta: Q,
    target_noise: Q,
    *,
    atom_bits: int = 20,
    trial_time: int | None = None,
    honest_budget: int = 10_000,
) -> dict[str, object]:
    if trial_time is None:
        trial_time = size * atom_bits
    attempts = min_attempts(alpha, target_failure)
    failure = (1 - alpha) ** attempts
    previous_failure = (1 - alpha) ** (attempts - 1) if attempts > 1 else None
    depth = min_depth(size, eta, target_noise)
    risk = noise_risk(size, depth, eta)
    previous_risk = noise_risk(size, depth - 2, eta) if depth > 1 else None
    completeness = 1 - risk
    soundness = failure + (1 - failure) * risk
    gap = completeness - soundness
    prefix = size.bit_length()
    finder_time = attempts * trial_time
    return {
        "one_shot_finder_success_lower_bound": text(alpha),
        "target_finder_failure": text(target_failure),
        "finder_attempts": attempts,
        "exact_amplified_finder_failure": text(failure),
        "exact_amplified_finder_success": text(1 - failure),
        "previous_attempt_failure": text(previous_failure) if previous_failure is not None else None,
        "maximum_refutation_classes": size,
        "eta": text(eta),
        "target_joint_noise_risk": text(target_noise),
        "replications_per_atom": depth,
        "joint_decoding_error": text(risk),
        "previous_odd_depth_joint_error": text(previous_risk) if previous_risk is not None else None,
        "completeness_lower_bound": text(completeness),
        "soundness_upper_bound": text(soundness),
        "gap_lower_bound": text(gap),
        "decoupled_target_gap_lower_bound": text(
            1 - target_failure - 2 * target_noise + target_failure * target_noise
        ),
        "atom_id_bits": atom_bits,
        "critic_message_length_prefix_bits": prefix,
        "critic_message_bits": prefix + size * (atom_bits + 1),
        "semantic_query_count": size * depth,
        "finder_trial_time": trial_time,
        "total_honest_finder_time": finder_time,
        "honest_prover_budget": honest_budget,
        "within_honest_prover_budget": finder_time <= honest_budget,
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
            risk <= target_noise and (previous_risk is None or previous_risk > target_noise)
        ),
        "certified": True,
    }


def reconstruct_restart_rows() -> list[dict[str, object]]:
    rows = []
    for alpha in (Q(1, 4), Q(1, 2), Q(2, 3)):
        for attempts in range(1, 7):
            yes = Q(0)
            no = Q(0)
            patterns = list(itertools.product((0, 1), repeat=attempts))
            for pattern in patterns:
                count = sum(pattern)
                probability = alpha**count * (1 - alpha) ** (attempts - count)
                if count:
                    yes += probability
                else:
                    no += probability
            rows.append(
                {
                    "one_shot_success": text(alpha),
                    "attempts": attempts,
                    "boolean_outcome_patterns": len(patterns),
                    "enumerated_success_probability": text(yes),
                    "enumerated_failure_probability": text(no),
                    "closed_form_success_probability": text(1 - (1 - alpha) ** attempts),
                    "closed_form_failure_probability": text((1 - alpha) ** attempts),
                    "certified": yes + no == 1 and no == (1 - alpha) ** attempts,
                }
            )
    return rows


def reconstruct_scaling() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows = []
    for log_work in range(20, 101, 10):
        row = reconstruct_row(
            Q(1, log_work),
            Q(1, log_work),
            log_work,
            Q(1, 5),
            Q(1, log_work),
            atom_bits=log_work,
            trial_time=log_work**2,
            honest_budget=2**log_work,
        )
        quartic = log_work**4
        target_gap = 1 - Q(3, log_work) + Q(1, log_work**2)
        rows.append(
            {
                "log2_prover_budget": log_work,
                "one_shot_finder_success": text(Q(1, log_work)),
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
                "symbolic_target_gap": text(target_gap),
                "certified": (
                    row["within_honest_prover_budget"]
                    and row["total_honest_finder_time"] <= quartic
                    and Q(row["gap_lower_bound"]) >= target_gap
                ),
            }
        )
    return rows[:6], rows[6:]


def reconstruct_marker_rows() -> list[dict[str, object]]:
    rows = []
    for bits in (20, 24, 28, 32, 36, 40):
        count = 2**bits
        q = bits**3
        attempts = (2 * count + 3 * q - 1) // (3 * q)
        previous = Q((attempts - 1) * q, count)
        success = min(Q(attempts * q, count), Q(1))
        total = attempts * q
        rows.append(
            {
                "index_bits": bits,
                "semantic_atom_count": count,
                "queries_per_coordinated_trial": q,
                "target_success": "2/3",
                "minimal_coordinated_attempts": attempts,
                "previous_attempt_success_upper_bound": text(previous),
                "amplified_success_upper_bound": text(success),
                "total_honest_search_queries": total,
                "registered_one_trial_budget": q,
                "exceeds_registered_one_trial_budget": total > q,
                "linear_query_floor": (2 * count + 2) // 3,
                "certified": (
                    previous < Q(2, 3)
                    and success >= Q(2, 3)
                    and total >= Q(2 * count, 3)
                    and total > q
                ),
            }
        )
    return rows


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_PATH.read_text(encoding="utf-8"))
    search = json.loads(SEARCH_PATH.read_text(encoding="utf-8"))
    expected_rows = [
        reconstruct_row(alpha, target, size, eta, target)
        for alpha in (Q(1, 4), Q(1, 2), Q(2, 3), Q(3, 4))
        for size in (1, 4, 16)
        for eta in (Q(1, 5), Q(1, 3), Q(2, 5))
        for target in (Q(1, 10), Q(1, 100))
    ]
    restart = reconstruct_restart_rows()
    registered, confirmation = reconstruct_scaling()
    marker = reconstruct_marker_rows()
    rows = result.get("protocol_rows", [])
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version")
            == "asmp3_randomized_finder_amplification_v2_4"
            and result.get("status")
            == "exact_randomized_finder_restart_noise_and_budget_frontier"
            and result.get("parent_result")
            == "ASMP-3-CONSTRUCTIVE-REFUTATION-PROTOCOL-v2.3"
            and result.get("certified") is True
            and "does not derive such a finder" in result.get("claim_boundary", "")
        ),
        "V1_all_72_protocol_rows_reconstructed": len(rows) == 72 and rows == expected_rows,
        "V2_restart_minimality_and_gap_reconstructed": all(
            row["minimal_attempt_count_certified"]
            and Q(row["gap_lower_bound"])
            == 1
            - Q(row["exact_amplified_finder_failure"])
            - 2 * Q(row["joint_decoding_error"])
            + Q(row["exact_amplified_finder_failure"])
            * Q(row["joint_decoding_error"])
            for row in rows
        ),
        "V3_noise_depth_minimality_reconstructed": all(
            row["minimal_odd_depth_certified"] for row in rows
        ),
        "V4_exhaustive_boolean_restart_spaces_reconstructed": (
            result.get("exhaustive_restart_rows") == restart
            and all(row["certified"] for row in restart)
        ),
        "V5_registered_and_held_out_scaling_reconstructed": (
            result.get("registered_scaling_rows") == registered
            and result.get("held_out_scaling_rows") == confirmation
            and all(row["certified"] for row in (*registered, *confirmation))
        ),
        "V6_unique_marker_obstruction_reconstructed": (
            result.get("unique_marker_retry_obstruction_rows") == marker
            and all(row["certified"] for row in marker)
            and search["theorem"]["randomized_q_query_maximin_success"] == "q/N"
        ),
        "V7_parent_alpha_one_endpoint_matches": (
            parent["theorem"]["gap"] == "at least 1-2delta"
            and result["theorem"]["gap"] == "at least 1-f-2delta+f*delta"
        ),
        "V8_all_11_producer_gates_true": (
            len(result.get("gates", {})) == 11 and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_randomized_finder_amplification_verification_v2_4",
        "checker": "clean_room_restart_noise_budget_and_obstruction_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker certifies the independent-restart theorem and its charged "
            "resource frontier. It does not prove a randomized finder exists for all "
            "positive ASMP-3 interfaces or cover correlated retry failures."
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
        failed = [name for name, ok in result["checks"].items() if not ok]
        raise SystemExit(f"randomized-finder verification failed: {failed}")
    print(
        "ASMP-3 randomized-finder verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
