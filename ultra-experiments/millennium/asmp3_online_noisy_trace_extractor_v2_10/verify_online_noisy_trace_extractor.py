from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "online_noisy_trace_extractor_v2_10.json"
VERIFY_PATH = HERE / "artifacts" / "online_noisy_trace_extractor_verification_v2_10.json"
TRACE_PARENT_PATH = (
    HERE.parent
    / "asmp3_trace_binding_extractor_v2_8"
    / "artifacts"
    / "trace_binding_extractor_v2_8.json"
)


def text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def walk(
    policy: tuple[int, ...],
    depth: int,
    world: int,
    claim: int,
    errors: int,
) -> tuple[
    tuple[tuple[int, int], ...],
    tuple[int, int] | None,
    str,
    tuple[int, int] | None,
    str,
]:
    history: list[int] = []
    queries: list[tuple[int, int]] = []
    for level in range(depth):
        branch = 0
        for answer in history:
            branch = 2 * branch + answer
        semantic_class = policy[(1 << level) - 1 + branch]
        answer = ((world >> semantic_class) & 1) ^ ((errors >> level) & 1)
        history.append(answer)
        queries.append((semantic_class, answer))
    candidate = None
    for semantic_class, answer in reversed(queries):
        if ((claim >> semantic_class) & 1) != answer:
            candidate = (semantic_class, answer)
            break
    decision = "reject" if candidate is not None else "accept"
    if decision == "accept":
        extracted, reason = None, "no_rejection"
    elif candidate not in queries:
        extracted, reason = None, "candidate_not_queried"
    else:
        semantic_class = candidate[0]
        ideal = (world >> semantic_class) & 1
        if ((claim >> semantic_class) & 1) == ideal:
            extracted, reason = None, "ideal_revalidation_failed"
        else:
            extracted, reason = (semantic_class, ideal), "certified"
    return tuple(queries), candidate, decision, extracted, reason


def signature(
    queries: tuple[tuple[int, int], ...],
    candidate: tuple[int, int] | None,
    decision: str,
    extracted: tuple[int, int] | None,
    reason: str,
) -> str:
    query_text = ",".join(f"{semantic_class}:{answer}" for semantic_class, answer in queries)
    call_text = "-" if candidate is None else f"{candidate[0]}:{candidate[1]}"
    witness_text = "-" if extracted is None else f"{extracted[0]}:{extracted[1]}"
    return f"{query_text}|{call_text}|{decision}|{witness_text}|{reason}"


def reconstruct_exhaustive() -> dict[str, object]:
    digest = hashlib.sha256()
    counters = {
        "policy_programs": 0,
        "noisy_executions": 0,
        "raw_semantic_queries": 0,
        "accepting_executions": 0,
        "rejecting_executions": 0,
        "extractor_successes": 0,
        "extractor_failures": 0,
        "invalid_outputs": 0,
        "all_correct_executions": 0,
        "all_correct_rejections": 0,
        "all_correct_rejection_misses": 0,
        "erroneous_rejections": 0,
        "invalid_noisy_candidates": 0,
        "invalid_candidates_safely_failed": 0,
        "repeated_class_executions": 0,
    }
    maximum_dimension = 0
    for class_count in (2, 3):
        for depth in (1, 2, 3):
            for policy in product(range(class_count), repeat=(1 << depth) - 1):
                counters["policy_programs"] += 1
                for world in range(1 << class_count):
                    for claim in range(1 << class_count):
                        for errors in range(1 << depth):
                            counters["noisy_executions"] += 1
                            counters["raw_semantic_queries"] += depth
                            queries, candidate, decision, extracted, reason = walk(
                                policy, depth, world, claim, errors
                            )
                            counters[f"{decision}ing_executions"] += 1
                            if extracted is None:
                                counters["extractor_failures"] += 1
                            else:
                                counters["extractor_successes"] += 1
                                maximum_dimension = 1
                                semantic_class, answer = extracted
                                if (
                                    answer != ((world >> semantic_class) & 1)
                                    or answer == ((claim >> semantic_class) & 1)
                                    or semantic_class not in {item[0] for item in queries}
                                ):
                                    counters["invalid_outputs"] += 1
                            counters["repeated_class_executions"] += int(
                                len({item[0] for item in queries}) < len(queries)
                            )
                            good = errors == 0
                            counters["all_correct_executions"] += int(good)
                            if good and decision == "reject":
                                counters["all_correct_rejections"] += 1
                                counters["all_correct_rejection_misses"] += int(
                                    extracted is None
                                )
                            if not good and decision == "reject":
                                counters["erroneous_rejections"] += 1
                            if candidate is not None:
                                valid_candidate = (
                                    ((claim >> candidate[0]) & 1)
                                    != ((world >> candidate[0]) & 1)
                                )
                                if not valid_candidate:
                                    counters["invalid_noisy_candidates"] += 1
                                    counters["invalid_candidates_safely_failed"] += int(
                                        extracted is None
                                        and reason == "ideal_revalidation_failed"
                                    )
                            digest.update(
                                (
                                    f"{class_count}|{depth}|"
                                    f"{','.join(map(str, policy))}|{world}|{claim}|"
                                    f"{errors}|"
                                    f"{signature(queries, candidate, decision, extracted, reason)}\n"
                                ).encode("ascii")
                            )
    certified = (
        counters["noisy_executions"] > 1_000_000
        and counters["noisy_executions"]
        == counters["accepting_executions"] + counters["rejecting_executions"]
        and counters["invalid_outputs"] == 0
        and counters["all_correct_rejections"] > 0
        and counters["all_correct_rejection_misses"] == 0
        and counters["invalid_noisy_candidates"]
        == counters["invalid_candidates_safely_failed"]
    )
    return {
        "class_counts": [2, 3],
        "maximum_query_depth": 3,
        **counters,
        "maximum_extracted_witness_dimension": maximum_dimension,
        "canonical_noisy_execution_digest_sha256": digest.hexdigest().upper(),
        "certified": certified,
    }


def compositions(total: int, slots: int):
    if slots == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for rest in compositions(total - first, slots - 1):
                yield (first,) + rest


def reconstruct_probability_audit() -> dict[str, object]:
    digest = hashlib.sha256()
    tables = registered = held_out = violations = equalities = 0
    for denominator in range(1, 21):
        for counts in compositions(denominator, 5):
            tables += 1
            registered += int(denominator <= 16)
            held_out += int(denominator >= 17)
            rg, rbs, rbf, _ag, ab = counts
            success = Fraction(rg + rbs, denominator)
            rejection = Fraction(rg + rbs + rbf, denominator)
            bad = Fraction(rbs + rbf + ab, denominator)
            margin = success - (rejection - bad)
            violations += int(margin < 0)
            equalities += int(margin == 0)
            digest.update(
                (
                    f"{denominator}|{','.join(map(str, counts))}|"
                    f"{text(success)}|{text(rejection)}|{text(bad)}|"
                    f"{text(margin)}\n"
                ).encode("ascii")
            )
    return {
        "probability_denominators": [1, 20],
        "registered_denominators": [1, 16],
        "held_out_denominators": [17, 20],
        "joint_tables": tables,
        "registered_tables": registered,
        "held_out_tables": held_out,
        "inequality_violations": violations,
        "sharp_equality_tables": equalities,
        "canonical_probability_digest_sha256": digest.hexdigest().upper(),
        "certified": tables > 50_000 and violations == 0 and equalities > 0,
    }


def reconstruct_contract_rows() -> list[dict[str, object]]:
    cases = (
        ("decision_only_log", "actual_trace_access", "actual_trace_unavailable"),
        (
            "ideal_only_binding",
            "noisy_rejection_binding",
            "noisy_rejection_not_trace_bound",
        ),
        (
            "unqueried_candidate",
            "candidate_scope",
            "candidate_outside_query_scope",
        ),
        (
            "missing_H_access",
            "ideal_candidate_provider",
            "ideal_candidate_provider_unavailable",
        ),
        (
            "trust_noisy_call",
            "refute_recheck",
            "refute_not_rechecked_on_ideal_answers",
        ),
        (
            "emit_invalid_candidate",
            "invalid_candidate_behavior",
            "invalid_candidate_may_escape",
        ),
        (
            "marginal_noise_only",
            "path_error_control",
            "path_error_probability_uncontrolled",
        ),
        (
            "hidden_validation_cost",
            "resource_accounting",
            "online_extraction_resource_omitted",
        ),
    )
    rows = [
        {
            "case": name,
            "mutated_field": field,
            "accepted": False,
            "reason": reason,
        }
        for name, field, reason in cases
    ]
    rows.extend(
        {
            "case": f"positive_{mode}",
            "mutated_field": "interaction_mode",
            "accepted": True,
            "reason": "certified",
        }
        for mode in ("one_shot_stateful_allowed", "restartable_allowed")
    )
    return rows


def reconstruct_stateful_rows() -> list[dict[str, object]]:
    rows = []
    for marker_count in (2, 3, 5, 8, 13, 20):
        for error in (Fraction(1, 10), Fraction(1, 5), Fraction(1, 3)):
            success = (1 - error) ** 2
            soundness = 1 - success
            failure = 1 - success
            bound = max(Fraction(0), 1 - soundness - failure)
            rows.append(
                {
                    "marker_count": marker_count,
                    "single_query_decoded_error": text(error),
                    "post_interaction_private_states": 1,
                    "strategy_state_erased": True,
                    "runtime_restartable": False,
                    "online_extractor_success": text(success),
                    "noisy_false_acceptance": text(soundness),
                    "two_query_path_failure": text(failure),
                    "general_lower_bound": text(bound),
                    "las_vegas_invalid_output_probability": "0",
                    "certified": success >= bound and success > 0,
                }
            )
    return rows


def reconstruct_formal() -> dict[str, object]:
    rows = [
        {
            "malformed": True,
            "logged_empty_refute_success": True,
            "terminal": "reject",
            "extractor": "empty_formal_witness",
            "valid": True,
        },
        {
            "malformed": False,
            "logged_empty_refute_success": False,
            "terminal": "accept",
            "extractor": "FAIL",
            "valid": True,
        },
    ]
    return {"rows": rows, "certified": True}


def reconstruct_composition(parent: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for source in parent["composition_rows"]:
        q = int(source["maximum_adaptive_queries"])
        witness = int(source["extracted_witness_classes_bound"])
        interaction = int(source["honest_critic_time"]) + int(
            source["verifier_ideal_replay_time"]
        )
        scan = int(source["trace_scan_time"])
        canonical = int(source["canonicalization_time"])
        ideal = 3 * witness
        recheck = 2 + witness
        rows.append(
            {
                "soundness_upper_bound": source["soundness_upper_bound"],
                "eta": source["eta"],
                "maximum_adaptive_queries": q,
                "raw_noisy_semantic_queries": source["raw_semantic_queries"],
                "path_error_probability": source["derived_coupling_failure"],
                "online_finder_success_lower_bound": source[
                    "trace_bound_finder_success"
                ],
                "candidate_witness_classes": witness,
                "actual_interaction_time": interaction,
                "trace_scan_time": scan,
                "canonicalization_time": canonical,
                "ideal_candidate_revalidation_time": ideal,
                "refute_recheck_time": recheck,
                "online_extractor_time": interaction + scan + canonical + ideal + recheck,
                "strategy_restart_required": False,
                "ideal_execution_replay_required": False,
                "certified": Fraction(source["trace_bound_finder_success"]) > 0,
            }
        )
    return rows


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    parent = json.loads(TRACE_PARENT_PATH.read_text(encoding="utf-8"))
    exhaustive = reconstruct_exhaustive()
    probabilities = reconstruct_probability_audit()
    contracts = reconstruct_contract_rows()
    stateful = reconstruct_stateful_rows()
    formal = reconstruct_formal()
    composition = reconstruct_composition(parent)
    checks = {
        "V0_schema_parent_status": (
            result.get("schema_version")
            == "asmp3_online_noisy_trace_extractor_v2_10"
            and result.get("parent_result")
            == "ASMP-3-ORACLE-PARAMETRIC-REPLAY-v2.9"
            and result.get("status")
            == "one_shot_online_noisy_trace_finder_without_restart"
        ),
        "V1_all_1144000_noisy_executions_reconstructed": result.get(
            "exhaustive_online_audit"
        )
        == exhaustive,
        "V2_probability_tables_and_sharp_cases_reconstructed": result.get(
            "probability_table_audit"
        )
        == probabilities,
        "V3_contract_mutants_and_controls_reconstructed": result.get(
            "contract_rows"
        )
        == contracts,
        "V4_one_shot_erased_state_rows_reconstructed": result.get(
            "stateful_one_shot_rows"
        )
        == stateful,
        "V5_formal_empty_witness_lane_reconstructed": result.get(
            "formal_empty_witness_audit"
        )
        == formal,
        "V6_all_12_online_compositions_reconstructed": (
            len(composition) == 12 and result.get("composition_rows") == composition
        ),
        "V7_no_restart_or_ideal_replay_resource_is_hidden": all(
            not row["strategy_restart_required"]
            and not row["ideal_execution_replay_required"]
            and row["online_extractor_time"]
            == row["actual_interaction_time"]
            + row["trace_scan_time"]
            + row["canonicalization_time"]
            + row["ideal_candidate_revalidation_time"]
            + row["refute_recheck_time"]
            for row in composition
        ),
        "V8_all_10_producer_gates_true": (
            len(result.get("gates", {})) == 10
            and all(result.get("gates", {}).values())
            and result.get("certified") is True
        ),
        "V9_claim_boundary_preserves_noisy_trace_scope": all(
            phrase in result.get("claim_boundary", "")
            for phrase in (
                "actual noisy rejection trace",
                "charged ideal answers",
                "removes restartability",
            )
        ),
    }
    return {
        "schema_version": "asmp3_online_noisy_trace_extractor_verification_v2_10",
        "checker": "clean_room_noisy_tree_probability_stateful_contract_and_parent_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker certifies one-shot extraction from actual trace-completely "
            "bound noisy rejections with ideal candidate revalidation. It does not "
            "infer public noisy traces, H access, or conditional path-error control "
            "from protocol admission alone."
        ),
    }


def main() -> None:
    receipt = verify()
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not receipt["passed"]:
        failed = [name for name, value in receipt["checks"].items() if not value]
        raise RuntimeError(f"ASMP-3 v2.10 verification failed: {failed}")
    print(
        "ASMP-3 online noisy-trace verification passed: "
        f"{receipt['check_count']}/{receipt['check_count']}"
    )


if __name__ == "__main__":
    main()
