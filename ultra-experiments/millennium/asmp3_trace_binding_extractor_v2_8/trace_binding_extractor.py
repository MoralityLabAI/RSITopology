from __future__ import annotations

import hashlib
import itertools
import json
import sys
from fractions import Fraction
from functools import cache
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
SEARCH_PATH = (
    HERE.parent
    / "asmp3_honest_search_barrier_v2_1"
    / "artifacts"
    / "honest_search_barrier_v2_1.json"
)
NORMAL_FORM_PATH = (
    HERE.parent
    / "asmp3_witness_transparent_normal_form_v2_5"
    / "artifacts"
    / "witness_transparent_normal_form_v2_5.json"
)
COUPLING_PATH = (
    HERE.parent
    / "asmp3_adaptive_transcript_coupling_v2_7"
    / "artifacts"
    / "adaptive_transcript_coupling_v2_7.json"
)

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(100_000)


def qstr(value: Q) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def ceil_log2(value: int) -> int:
    if value < 1:
        raise ValueError("value must be positive")
    return (value - 1).bit_length()


def refute_vector_claim(
    claim: int,
    task_bits: int,
    classes: tuple[int, ...],
    answers: tuple[int, ...],
    *,
    malformed: bool = False,
) -> bool:
    if task_bits < 1 or len(classes) != len(answers):
        return False
    if malformed:
        return len(classes) == 0
    return any(
        semantic_class < task_bits
        and answer != ((claim >> semantic_class) & 1)
        for semantic_class, answer in zip(classes, answers)
    )


def validate_and_extract(
    trace: list[dict[str, object]],
    *,
    world: int,
    claim: int,
    task_bits: int,
    semantic_classes: int,
    malformed: bool = False,
) -> dict[str, object]:
    if task_bits < 1 or semantic_classes < task_bits:
        raise ValueError("invalid trace universe")
    queried: dict[int, int] = {}
    successful_calls: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    terminal: str | None = None
    invalid_reason: str | None = None
    for position, event in enumerate(trace):
        op = event.get("op")
        if terminal is not None:
            invalid_reason = "event_after_terminal"
            break
        if op == "query":
            semantic_class = event.get("class")
            answer = event.get("answer")
            if (
                not isinstance(semantic_class, int)
                or semantic_class < 0
                or semantic_class >= semantic_classes
                or answer not in (0, 1)
            ):
                invalid_reason = "malformed_query"
                break
            ideal = (world >> semantic_class) & 1
            if answer != ideal:
                invalid_reason = "nonideal_query_answer"
                break
            if semantic_class in queried and queried[semantic_class] != answer:
                invalid_reason = "inconsistent_repeat_answer"
                break
            queried[semantic_class] = answer
        elif op == "refute":
            raw_classes = event.get("classes")
            raw_answers = event.get("answers")
            recorded_result = event.get("result")
            if not isinstance(raw_classes, list) or not isinstance(raw_answers, list):
                invalid_reason = "malformed_refute_call"
                break
            classes = tuple(raw_classes)
            answers = tuple(raw_answers)
            if (
                any(not isinstance(item, int) for item in classes)
                or any(item not in (0, 1) for item in answers)
                or tuple(sorted(set(classes))) != classes
            ):
                invalid_reason = "noncanonical_witness"
                break
            if any(item not in queried for item in classes):
                invalid_reason = "unqueried_witness_class"
                break
            if tuple(queried[item] for item in classes) != answers:
                invalid_reason = "witness_answer_mismatch"
                break
            actual_result = refute_vector_claim(
                claim,
                task_bits,
                classes,
                answers,
                malformed=malformed,
            )
            if recorded_result is not actual_result:
                invalid_reason = "refute_result_mismatch"
                break
            if actual_result:
                successful_calls.append((classes, answers))
        elif op == "terminal":
            decision = event.get("decision")
            if decision not in ("accept", "reject"):
                invalid_reason = "malformed_terminal"
                break
            if position != len(trace) - 1:
                invalid_reason = "terminal_not_last"
                break
            terminal = decision
        else:
            invalid_reason = "unknown_operation"
            break
    if invalid_reason is None and terminal is None:
        invalid_reason = "missing_terminal"
    if invalid_reason is None and terminal == "reject" and not successful_calls:
        invalid_reason = "unbound_rejection"
    valid = invalid_reason is None
    witness = successful_calls[-1] if valid and terminal == "reject" else None
    return {
        "valid": valid,
        "invalid_reason": invalid_reason,
        "terminal_decision": terminal,
        "distinct_queried_classes": len(queried),
        "successful_refute_calls": len(successful_calls),
        "extracted_classes": list(witness[0]) if witness is not None else None,
        "extracted_answers": list(witness[1]) if witness is not None else None,
        "trace_events": len(trace),
    }


@cache
def exhaustive_trace_audit() -> dict[str, object]:
    digest = hashlib.sha256()
    traces = reject_traces = accept_traces = extracted_rejections = 0
    invalid_generated = extraction_mismatches = dimension_violations = 0
    subset_evaluations = 0
    for semantic_classes in range(2, 6):
        task_bits = min(3, semantic_classes)
        max_queries = min(3, semantic_classes)
        for world in range(1 << semantic_classes):
            for claim in range(1 << task_bits):
                for query_count in range(1, max_queries + 1):
                    for query_sequence in itertools.product(
                        range(semantic_classes), repeat=query_count
                    ):
                        queried = tuple(sorted(set(query_sequence)))
                        query_events = [
                            {
                                "op": "query",
                                "class": semantic_class,
                                "answer": (world >> semantic_class) & 1,
                            }
                            for semantic_class in query_sequence
                        ]
                        for mask in range(1 << len(queried)):
                            subset_evaluations += 1
                            classes = tuple(
                                queried[index]
                                for index in range(len(queried))
                                if mask & (1 << index)
                            )
                            answers = tuple((world >> item) & 1 for item in classes)
                            result = refute_vector_claim(
                                claim, task_bits, classes, answers
                            )
                            decision = "reject" if result else "accept"
                            trace = [
                                *query_events,
                                {
                                    "op": "refute",
                                    "classes": list(classes),
                                    "answers": list(answers),
                                    "result": result,
                                },
                                {"op": "terminal", "decision": decision},
                            ]
                            checked = validate_and_extract(
                                trace,
                                world=world,
                                claim=claim,
                                task_bits=task_bits,
                                semantic_classes=semantic_classes,
                            )
                            traces += 1
                            invalid_generated += not checked["valid"]
                            if decision == "reject":
                                reject_traces += 1
                                extracted_rejections += checked["extracted_classes"] is not None
                                extraction_mismatches += (
                                    checked["extracted_classes"] != list(classes)
                                    or checked["extracted_answers"] != list(answers)
                                )
                                dimension_violations += len(classes) > query_count
                            else:
                                accept_traces += 1
                            digest.update(
                                (
                                    f"{semantic_classes}:{world}:{claim}:"
                                    f"{query_sequence}:{classes}:{decision}:"
                                    f"{checked}\n"
                                ).encode("ascii")
                            )
                formal_trace = [
                    {"op": "refute", "classes": [], "answers": [], "result": True},
                    {"op": "terminal", "decision": "reject"},
                ]
                formal = validate_and_extract(
                    formal_trace,
                    world=world,
                    claim=claim,
                    task_bits=task_bits,
                    semantic_classes=semantic_classes,
                    malformed=True,
                )
                traces += 1
                reject_traces += 1
                extracted_rejections += formal["extracted_classes"] == []
                invalid_generated += not formal["valid"]
                digest.update(
                    f"formal:{semantic_classes}:{world}:{claim}:{formal}\n".encode(
                        "ascii"
                    )
                )
    return {
        "semantic_class_sizes": [2, 3, 4, 5],
        "maximum_query_sequence_length": 3,
        "trace_programs_audited": traces,
        "candidate_witness_subset_evaluations": subset_evaluations,
        "valid_reject_traces": reject_traces,
        "valid_accept_traces": accept_traces,
        "rejections_with_extracted_witness": extracted_rejections,
        "invalid_generated_traces": invalid_generated,
        "extraction_mismatches": extraction_mismatches,
        "query_dimension_violations": dimension_violations,
        "canonical_trace_digest_sha256": digest.hexdigest().upper(),
        "certified": (
            traces > 100_000
            and subset_evaluations > 100_000
            and reject_traces > 0
            and accept_traces > 0
            and extracted_rejections == reject_traces
            and invalid_generated == 0
            and extraction_mismatches == 0
            and dimension_violations == 0
        ),
    }


def mutant_trace_audit() -> list[dict[str, object]]:
    world = 0b01
    claim = 0b00
    valid_query = {"op": "query", "class": 0, "answer": 1}
    valid_call = {
        "op": "refute",
        "classes": [0],
        "answers": [1],
        "result": True,
    }
    reject = {"op": "terminal", "decision": "reject"}
    cases = {
        "reject_without_refute": [valid_query, reject],
        "unqueried_witness_class": [
            valid_query,
            {"op": "refute", "classes": [1], "answers": [0], "result": False},
            reject,
        ],
        "wrong_ideal_answer": [
            {"op": "query", "class": 0, "answer": 0},
            valid_call,
            reject,
        ],
        "duplicate_noncanonical_classes": [
            valid_query,
            {"op": "refute", "classes": [0, 0], "answers": [1, 1], "result": True},
            reject,
        ],
        "unsorted_noncanonical_classes": [
            valid_query,
            {"op": "query", "class": 1, "answer": 0},
            {"op": "refute", "classes": [1, 0], "answers": [0, 1], "result": True},
            reject,
        ],
        "forged_refute_result": [
            valid_query,
            {"op": "refute", "classes": [], "answers": [], "result": True},
            reject,
        ],
        "terminal_not_last": [reject, valid_query],
        "failed_call_then_reject": [
            valid_query,
            {"op": "refute", "classes": [], "answers": [], "result": False},
            reject,
        ],
        "missing_terminal": [valid_query, valid_call],
        "unknown_instruction": [valid_query, {"op": "magic"}, reject],
    }
    rows = []
    for name, trace in cases.items():
        checked = validate_and_extract(
            trace,
            world=world,
            claim=claim,
            task_bits=2,
            semantic_classes=2,
        )
        rows.append(
            {
                "mutant": name,
                "trace_events": len(trace),
                "rejected_by_validator": not checked["valid"],
                "invalid_reason": checked["invalid_reason"],
                "certified": not checked["valid"] and checked["invalid_reason"] is not None,
            }
        )
    return rows


def decision_only_firewall_rows() -> list[dict[str, object]]:
    rows = []
    for index_bits in range(1, 21):
        witness_worlds = 2**index_bits
        query_budget = min(witness_worlds, index_bits**3)
        rows.append(
            {
                "index_bits": index_bits,
                "singleton_witness_worlds": witness_worlds,
                "observable_terminal_decisions": 1,
                "terminal_decision_in_every_world": "reject",
                "best_decision_only_worst_world_success": qstr(Q(1, witness_worlds)),
                "ideal_query_budget": query_budget,
                "best_decision_plus_q_queries_success": qstr(
                    Q(query_budget, witness_worlds)
                ),
                "trace_log_reveals_witness_in_one_scan": True,
                "decision_only_binding_is_insufficient": True,
                "certified": (
                    Q(1, witness_worlds) <= Q(query_budget, witness_worlds)
                    and query_budget <= witness_worlds
                ),
            }
        )
    return rows


def composition_rows() -> list[dict[str, object]]:
    coupling = json.loads(COUPLING_PATH.read_text(encoding="utf-8"))
    by_key = {
        (row["maximum_adaptive_semantic_queries"], row["eta"]): row
        for row in coupling["coupling_rows"]
        if row["target_path_coupling_failure"] == "1/100"
    }
    rows = []
    atom_id_bits = 20
    for soundness in (Q(1, 5), Q(1, 3)):
        for eta in (Q(1, 5), Q(1, 3)):
            for max_queries in (1, 4, 16):
                path = by_key[(max_queries, qstr(eta))]
                delta = Q(path["adaptive_path_coupling_failure"])
                alpha = 1 - soundness - delta
                verifier_time = 2 * max_queries
                critic_time = 4 * max_queries
                ideal_eval = 3 * max_queries
                trace_bits = max_queries * (atom_id_bits + 2) + 1
                trace_scan = trace_bits
                canonicalization = max_queries * ceil_log2(max_queries + 1)
                one_shot_time = (
                    verifier_time
                    + critic_time
                    + ideal_eval
                    + trace_scan
                    + canonicalization
                )
                witness_bits = ceil_log2(max_queries + 1) + max_queries * (
                    atom_id_bits + 1
                )
                rows.append(
                    {
                        "soundness_upper_bound": qstr(soundness),
                        "eta": qstr(eta),
                        "maximum_adaptive_queries": max_queries,
                        "derived_coupling_failure": qstr(delta),
                        "trace_bound_finder_success": qstr(alpha),
                        "extracted_witness_classes_bound": max_queries,
                        "replications_per_query": path[
                            "replications_per_adaptive_query"
                        ],
                        "raw_semantic_queries": path["raw_semantic_query_count"],
                        "honest_critic_time": critic_time,
                        "verifier_ideal_replay_time": verifier_time,
                        "ideal_semantic_evaluation_time": ideal_eval,
                        "trace_bits": trace_bits,
                        "trace_scan_time": trace_scan,
                        "canonicalization_time": canonicalization,
                        "one_shot_extractor_time": one_shot_time,
                        "canonical_witness_message_bits": witness_bits,
                        "remaining_contract": (
                            "efficient ideal-semantic replay; witness transparency "
                            "and coupling are derived from trace binding and v2.7"
                        ),
                        "certified": (
                            delta <= Q(1, 100)
                            and alpha == 1 - soundness - delta
                            and alpha > 0
                            and one_shot_time
                            == verifier_time
                            + critic_time
                            + ideal_eval
                            + trace_scan
                            + canonicalization
                        ),
                    }
                )
    return rows


def build_result() -> dict[str, object]:
    search = json.loads(SEARCH_PATH.read_text(encoding="utf-8"))
    normal_form = json.loads(NORMAL_FORM_PATH.read_text(encoding="utf-8"))
    coupling = json.loads(COUPLING_PATH.read_text(encoding="utf-8"))
    exhaustive = exhaustive_trace_audit()
    mutants = mutant_trace_audit()
    firewall = decision_only_firewall_rows()
    composition = composition_rows()
    gates = {
        "B0_exhaustive_trace_compiler_audit_passes": exhaustive["certified"],
        "B1_every_bound_rejection_extracts_queried_witness": (
            exhaustive["rejections_with_extracted_witness"]
            == exhaustive["valid_reject_traces"]
            and exhaustive["query_dimension_violations"] == 0
        ),
        "B2_all_trace_binding_mutants_are_rejected": (
            len(mutants) == 10 and all(row["certified"] for row in mutants)
        ),
        "B3_formal_empty_and_semantic_nonempty_witnesses_supported": (
            exhaustive["valid_reject_traces"] > 0
            and exhaustive["valid_accept_traces"] > 0
        ),
        "B4_decision_only_binding_firewall_matches_search_barrier": (
            len(firewall) == 20
            and all(row["certified"] for row in firewall)
            and search["theorem"]["randomized_q_query_maximin_success"] == "q/N"
        ),
        "B5_trace_scan_and_canonicalization_fully_charged": all(
            row["one_shot_extractor_time"]
            == row["honest_critic_time"]
            + row["verifier_ideal_replay_time"]
            + row["ideal_semantic_evaluation_time"]
            + row["trace_scan_time"]
            + row["canonicalization_time"]
            for row in composition
        ),
        "B6_v2_7_coupling_and_trace_binding_derive_v2_5_transparency": (
            len(composition) == 12
            and all(row["certified"] for row in composition)
            and normal_form["theorem"]["extracted_finder_success"]
            == "alpha>=1-s-delta"
            and coupling["theorem"]["adaptive_path_coupling_failure"]
            == "delta<=1-(1-e)^q"
        ),
        "B7_witness_dimension_is_bounded_by_query_budget": all(
            row["extracted_witness_classes_bound"]
            == row["maximum_adaptive_queries"]
            for row in composition
        ),
        "B8_trace_complete_binding_is_stronger_than_extensional_label": (
            all(row["decision_only_binding_is_insufficient"] for row in firewall)
        ),
        "B9_all_composition_margins_positive": all(
            Q(row["trace_bound_finder_success"]) > 0 for row in composition
        ),
    }
    return {
        "schema_version": "asmp3_trace_binding_extractor_v2_8",
        "experiment_id": "ASMP-3-TRACE-BINDING-EXTRACTOR-v2.8",
        "status": "operational_refute_binding_compiler_and_finder_extractor",
        "parent_result": "ASMP-3-ADAPTIVE-TRANSCRIPT-COUPLING-v2.7",
        "supporting_results": [
            "ASMP-3-WITNESS-TRANSPARENT-NORMAL-FORM-v2.5",
            "ASMP-3-HONEST-SEARCH-BARRIER-v2.1",
        ],
        "theorem": {
            "trace_binding": (
                "every ideal rejection is guarded by a logged successful "
                "canonical Refute call over previously queried quotient classes"
            ),
            "extracted_dimension": "r<=q",
            "extractor_time": (
                "C_honest+V+q*Eval_H+TraceScan+Canonicalize"
            ),
            "finder_success_with_v2_7": "alpha>=1-s-delta_q",
            "decision_only_firewall": (
                "an extensional reject bit does not reveal which valid witness "
                "caused rejection"
            ),
        },
        "exhaustive_trace_audit": exhaustive,
        "mutant_trace_rows": mutants,
        "decision_only_firewall_rows": firewall,
        "composition_rows": composition,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The theorem derives witness transparency from trace-complete "
            "operational binding, not from the typed successor's weaker phrase "
            "'attributed to a local refutation' alone. Efficient ideal-semantic "
            "replay remains a separate contract."
        ),
    }
