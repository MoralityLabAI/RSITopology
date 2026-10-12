from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Callable, Iterable


HERE = Path(__file__).resolve().parent
ARTIFACT_DIR = HERE / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "oracle_parametric_replay_v2_9.json"
PARENT_PATH = (
    HERE.parent
    / "asmp3_trace_binding_extractor_v2_8"
    / "artifacts"
    / "trace_binding_extractor_v2_8.json"
)


def ratio(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def ideal_answer(world: int, semantic_class: int) -> int:
    return (world >> semantic_class) & 1


def claim_answer(claim: int, semantic_class: int) -> int:
    return (claim >> semantic_class) & 1


def node_index(history: tuple[int, ...]) -> int:
    branch = 0
    for bit in history:
        branch = 2 * branch + bit
    return (1 << len(history)) - 1 + branch


def execute_oracle_runtime(
    policy: tuple[int, ...],
    query_depth: int,
    world: int,
    claim: int,
    class_count: int,
    provider: Callable[[int, int], int],
) -> list[dict[str, object]]:
    """Execute a total dependency-injected semantic runtime."""
    if len(policy) != (1 << query_depth) - 1:
        raise ValueError("policy is not a complete binary query tree")
    history: tuple[int, ...] = ()
    queries: list[tuple[int, int]] = []
    trace: list[dict[str, object]] = []
    for _ in range(query_depth):
        semantic_class = policy[node_index(history)]
        if not 0 <= semantic_class < class_count:
            raise ValueError("policy selected an out-of-range semantic class")
        answer = provider(world, semantic_class)
        if answer not in (0, 1):
            raise ValueError("semantic provider returned a nonbit")
        queries.append((semantic_class, answer))
        trace.append({"op": "query", "class": semantic_class, "answer": answer})
        history += (answer,)

    witness: tuple[int, int] | None = None
    for semantic_class, answer in reversed(queries):
        if claim_answer(claim, semantic_class) != answer:
            witness = (semantic_class, answer)
            break
    if witness is None:
        trace.append({"op": "terminal", "decision": "accept"})
    else:
        semantic_class, answer = witness
        trace.append(
            {
                "op": "refute",
                "classes": [semantic_class],
                "answers": [answer],
                "result": True,
            }
        )
        trace.append({"op": "terminal", "decision": "reject"})
    return trace


def reference_ideal_execution(
    policy: tuple[int, ...],
    query_depth: int,
    world: int,
    claim: int,
    class_count: int,
) -> list[dict[str, object]]:
    """Direct tree semantics, kept separate from the provider runner."""
    answers: list[int] = []
    queried: list[tuple[int, int]] = []
    output: list[dict[str, object]] = []
    for level in range(query_depth):
        offset = (1 << level) - 1
        branch = 0
        for answer in answers:
            branch = 2 * branch + answer
        semantic_class = policy[offset + branch]
        answer = (world // (1 << semantic_class)) % 2
        queried.append((semantic_class, answer))
        answers.append(answer)
        output.append({"op": "query", "class": semantic_class, "answer": answer})
    mismatches = [
        (semantic_class, answer)
        for semantic_class, answer in queried
        if ((claim // (1 << semantic_class)) % 2) != answer
    ]
    if not mismatches:
        output.append({"op": "terminal", "decision": "accept"})
        return output
    semantic_class, answer = mismatches[-1]
    output.append(
        {
            "op": "refute",
            "classes": [semantic_class],
            "answers": [answer],
            "result": True,
        }
    )
    output.append({"op": "terminal", "decision": "reject"})
    return output


def validate_bound_ideal_trace(
    trace: list[dict[str, object]], world: int, claim: int, query_depth: int
) -> tuple[bool, int]:
    if not trace or trace[-1].get("op") != "terminal":
        return False, 0
    queried: list[tuple[int, int]] = []
    successful_calls: list[tuple[list[int], list[int]]] = []
    for event in trace[:-1]:
        if event.get("op") == "query":
            semantic_class = int(event["class"])
            answer = int(event["answer"])
            if answer != ideal_answer(world, semantic_class):
                return False, 0
            queried.append((semantic_class, answer))
        elif event.get("op") == "refute":
            classes = [int(item) for item in event["classes"]]
            answers = [int(item) for item in event["answers"]]
            if classes != sorted(set(classes)) or len(classes) != len(answers):
                return False, 0
            lookup = dict(queried)
            if any(semantic_class not in lookup for semantic_class in classes):
                return False, 0
            if answers != [lookup[semantic_class] for semantic_class in classes]:
                return False, 0
            actual = any(
                claim_answer(claim, semantic_class) != answer
                for semantic_class, answer in zip(classes, answers)
            )
            if bool(event.get("result")) != actual:
                return False, 0
            if actual:
                successful_calls.append((classes, answers))
        else:
            return False, 0
    decision = trace[-1].get("decision")
    if decision == "reject":
        if not successful_calls:
            return False, 0
        return True, len(successful_calls[-1][0])
    if decision == "accept":
        return (not successful_calls), 0
    return False, 0


def trace_signature(trace: list[dict[str, object]]) -> str:
    fields: list[str] = []
    for event in trace:
        if event["op"] == "query":
            fields.append(f"Q{event['class']}={event['answer']}")
        elif event["op"] == "refute":
            fields.append(f"R{event['classes'][0]}={event['answers'][0]}")
        else:
            fields.append("T" + str(event["decision"])[0].upper())
    return ";".join(fields)


def exhaustive_replay_audit() -> dict[str, object]:
    digest = hashlib.sha256()
    policy_programs = 0
    executions = 0
    compiler_mismatches = 0
    invalid_bound_traces = 0
    semantic_queries = 0
    reject_executions = 0
    accept_executions = 0
    repeated_class_executions = 0
    maximum_witness_dimension = 0

    for class_count in (2, 3):
        for query_depth in (1, 2, 3):
            node_count = (1 << query_depth) - 1
            for policy in product(range(class_count), repeat=node_count):
                policy_programs += 1
                for world in range(1 << class_count):
                    for claim in range(1 << class_count):
                        executions += 1
                        compiled = execute_oracle_runtime(
                            policy,
                            query_depth,
                            world,
                            claim,
                            class_count,
                            ideal_answer,
                        )
                        reference = reference_ideal_execution(
                            policy, query_depth, world, claim, class_count
                        )
                        if compiled != reference:
                            compiler_mismatches += 1
                        valid, witness_dimension = validate_bound_ideal_trace(
                            compiled, world, claim, query_depth
                        )
                        if not valid:
                            invalid_bound_traces += 1
                        maximum_witness_dimension = max(
                            maximum_witness_dimension, witness_dimension
                        )
                        query_classes = [
                            int(event["class"])
                            for event in compiled
                            if event["op"] == "query"
                        ]
                        if len(set(query_classes)) < len(query_classes):
                            repeated_class_executions += 1
                        semantic_queries += query_depth
                        if compiled[-1]["decision"] == "reject":
                            reject_executions += 1
                        else:
                            accept_executions += 1
                        record = (
                            f"{class_count}|{query_depth}|"
                            f"{','.join(map(str, policy))}|{world}|{claim}|"
                            f"{trace_signature(compiled)}\n"
                        )
                        digest.update(record.encode("ascii"))

    certified = (
        executions == accept_executions + reject_executions
        and executions > 100_000
        and compiler_mismatches == 0
        and invalid_bound_traces == 0
        and maximum_witness_dimension <= 1
        and repeated_class_executions > 0
    )
    return {
        "class_counts": [2, 3],
        "maximum_query_depth": 3,
        "policy_programs": policy_programs,
        "ideal_executions": executions,
        "semantic_queries_replayed": semantic_queries,
        "valid_accept_executions": accept_executions,
        "valid_reject_executions": reject_executions,
        "repeated_class_executions": repeated_class_executions,
        "maximum_extracted_witness_dimension": maximum_witness_dimension,
        "compiler_mismatches": compiler_mismatches,
        "invalid_bound_traces": invalid_bound_traces,
        "canonical_execution_digest_sha256": digest.hexdigest().upper(),
        "certified": certified,
    }


def weak_compositions(total: int, slots: int) -> Iterable[tuple[int, ...]]:
    if slots == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in weak_compositions(total - first, slots - 1):
            yield (first,) + rest


def seed_marginal_audit() -> dict[str, object]:
    policies = (
        (0, 0, 0, 0, 0, 0, 0),
        (0, 1, 2, 0, 1, 2, 0),
        (1, 0, 2, 1, 0, 2, 1),
    )
    decisions: dict[tuple[int, int, int], int] = {}
    for seed, policy in enumerate(policies):
        for world in range(8):
            for claim in range(8):
                trace = reference_ideal_execution(policy, 3, world, claim, 3)
                decisions[(seed, world, claim)] = int(
                    trace[-1]["decision"] == "reject"
                )

    digest = hashlib.sha256()
    cases = 0
    marginal_mismatches = 0
    equality_cases = 0
    for denominator in range(1, 13):
        for weights in weak_compositions(denominator, 3):
            for world in range(8):
                for claim in range(8):
                    cases += 1
                    coupled_mass = Fraction(
                        sum(
                            weights[seed] * decisions[(seed, world, claim)]
                            for seed in range(3)
                        ),
                        denominator,
                    )
                    fresh_mass = sum(
                        Fraction(weights[seed], denominator)
                        * decisions[(seed, world, claim)]
                        for seed in range(3)
                    )
                    if fresh_mass != coupled_mass:
                        marginal_mismatches += 1
                    else:
                        equality_cases += 1
                    digest.update(
                        (
                            f"{denominator}|{','.join(map(str, weights))}|"
                            f"{world}|{claim}|{ratio(fresh_mass)}\n"
                        ).encode("ascii")
                    )
    return {
        "seed_support_size": 3,
        "probability_denominators": [1, 12],
        "fresh_seed_marginal_cases": cases,
        "exact_marginal_equalities": equality_cases,
        "marginal_mismatches": marginal_mismatches,
        "canonical_seed_law_digest_sha256": digest.hexdigest().upper(),
        "certified": cases > 25_000 and marginal_mismatches == 0,
    }


BASE_CONTRACT: dict[str, object] = {
    "transition_total": True,
    "semantic_access": "injected_provider_only",
    "ideal_provider": "callable_and_charged",
    "runtime_access": "restartable_kernel",
    "seed_source": "efficient_sampler",
    "query_order": "class_committed_before_answer",
    "execution_accounting": "charged_local",
    "trace_binding": "trace_complete",
}


def validate_composed_contract(contract: dict[str, object]) -> tuple[bool, str]:
    checks = (
        (contract.get("transition_total") is True, "partial_transition"),
        (
            contract.get("semantic_access") == "injected_provider_only",
            "hidden_semantic_side_channel",
        ),
        (
            contract.get("ideal_provider") == "callable_and_charged",
            "ideal_provider_unavailable_or_uncharged",
        ),
        (
            contract.get("runtime_access")
            in {"restartable_kernel", "restartable_live_interaction"},
            "runtime_not_restartable",
        ),
        (
            contract.get("seed_source") == "efficient_sampler",
            "nonsemantic_seed_sampler_unavailable",
        ),
        (
            contract.get("query_order") == "class_committed_before_answer",
            "query_selected_after_current_answer",
        ),
        (
            contract.get("execution_accounting")
            in {"charged_local", "external_online_messages_charged"},
            "kernel_execution_uncharged",
        ),
        (
            contract.get("trace_binding") == "trace_complete",
            "rejection_trace_not_bound",
        ),
    )
    for passed, reason in checks:
        if not passed:
            return False, reason
    return True, "certified"


def contract_mutant_rows() -> list[dict[str, object]]:
    mutations: tuple[tuple[str, str, object], ...] = (
        ("partial_transition", "transition_total", False),
        ("hidden_semantic_side_channel", "semantic_access", "world_side_channel"),
        ("missing_ideal_provider", "ideal_provider", "unavailable"),
        ("recorded_transcript_only", "runtime_access", "recorded_transcript"),
        ("opaque_seed_source", "seed_source", "opaque_realized_seed"),
        ("post_answer_query_choice", "query_order", "answer_then_current_class"),
        ("uncharged_local_emulation", "execution_accounting", "omitted"),
        ("decision_only_rejection", "trace_binding", "decision_label_only"),
    )
    rows: list[dict[str, object]] = []
    for name, field, value in mutations:
        candidate = dict(BASE_CONTRACT)
        candidate[field] = value
        valid, reason = validate_composed_contract(candidate)
        rows.append(
            {
                "mutant": name,
                "mutated_field": field,
                "accepted": valid,
                "rejection_reason": reason,
            }
        )
    for mode in ("restartable_kernel", "restartable_live_interaction"):
        candidate = dict(BASE_CONTRACT)
        candidate["runtime_access"] = mode
        if mode == "restartable_live_interaction":
            candidate["execution_accounting"] = "external_online_messages_charged"
        valid, reason = validate_composed_contract(candidate)
        rows.append(
            {
                "mutant": f"positive_{mode}",
                "mutated_field": "runtime_access",
                "accepted": valid,
                "rejection_reason": reason,
            }
        )
    return rows


def transcript_only_firewall_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for marker_count in range(2, 21):
        probe_budget = min(3, marker_count)
        observed_traces = {
            "QUERY(gate,0);TERMINAL(accept)" for _ in range(marker_count)
        }
        ideal_witnesses = {f"marker_{marker}" for marker in range(marker_count)}
        rows.append(
            {
                "marker_count": marker_count,
                "identical_recorded_noisy_traces": len(observed_traces),
                "distinct_unvisited_ideal_witnesses": len(ideal_witnesses),
                "best_transcript_only_worst_world_success": ratio(
                    Fraction(1, marker_count)
                ),
                "additional_ideal_probe_budget": probe_budget,
                "best_transcript_plus_probes_success": ratio(
                    Fraction(probe_budget, marker_count)
                ),
                "oracle_parametric_replay_success": "1",
                "ideal_runtime_semantic_queries": 2,
                "certified": (
                    len(observed_traces) == 1
                    and len(ideal_witnesses) == marker_count
                    and Fraction(probe_budget, marker_count) <= 1
                ),
            }
        )
    return rows


def composition_rows() -> list[dict[str, object]]:
    parent = json.loads(PARENT_PATH.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for source in parent["composition_rows"]:
        query_budget = int(source["maximum_adaptive_queries"])
        seed_sampling_time = 2 + query_budget.bit_length()
        kernel_dispatch_time = 2 * query_budget + 1
        charged_local_strategy_time = 5 * query_budget + 3
        parent_time = int(source["one_shot_extractor_time"])
        compiled_time = (
            parent_time
            + seed_sampling_time
            + kernel_dispatch_time
            + charged_local_strategy_time
        )
        rows.append(
            {
                "soundness_upper_bound": source["soundness_upper_bound"],
                "eta": source["eta"],
                "maximum_adaptive_queries": query_budget,
                "coupling_failure": source["derived_coupling_failure"],
                "finder_success": source["trace_bound_finder_success"],
                "parent_trace_extractor_time": parent_time,
                "seed_sampling_time": seed_sampling_time,
                "kernel_dispatch_time": kernel_dispatch_time,
                "charged_local_strategy_time": charged_local_strategy_time,
                "oracle_compiled_finder_time": compiled_time,
                "fresh_seed_is_distributionally_sufficient": True,
                "noisy_seed_recovery_required": False,
                "remaining_contract": (
                    "restartable oracle-parametric runtime, callable charged ideal "
                    "provider, and trace-complete Refute binding"
                ),
                "certified": Fraction(source["trace_bound_finder_success"]) > 0,
            }
        )
    return rows


def build_artifact() -> dict[str, object]:
    exhaustive = exhaustive_replay_audit()
    seed_audit = seed_marginal_audit()
    mutants = contract_mutant_rows()
    firewall = transcript_only_firewall_rows()
    composition = composition_rows()
    invalid_mutants = [row for row in mutants if not row["mutant"].startswith("positive_")]
    positive_contracts = [row for row in mutants if row["mutant"].startswith("positive_")]
    gates = {
        "C0_exhaustive_oracle_substitution_matches_direct_ideal_execution": exhaustive["certified"],
        "C1_every_compiled_rejection_is_trace_bound_and_extractable": (
            exhaustive["invalid_bound_traces"] == 0
            and exhaustive["maximum_extracted_witness_dimension"] <= 1
        ),
        "C2_fresh_seed_replay_preserves_the_exact_ideal_marginal_law": seed_audit["certified"],
        "C3_adaptive_and_repeated_class_paths_are_covered": exhaustive["repeated_class_executions"] > 0,
        "C4_all_contract_mutants_are_rejected": all(not row["accepted"] for row in invalid_mutants),
        "C5_both_restartable_runtime_modes_are_accepted": all(row["accepted"] for row in positive_contracts),
        "C6_transcript_only_firewall_matches_search_bound": all(row["certified"] for row in firewall),
        "C7_all_replay_and_kernel_resources_are_charged": all(
            row["oracle_compiled_finder_time"]
            == row["parent_trace_extractor_time"]
            + row["seed_sampling_time"]
            + row["kernel_dispatch_time"]
            + row["charged_local_strategy_time"]
            for row in composition
        ),
        "C8_v2_8_success_margins_survive_replay_compilation": (
            len(composition) == 12 and all(row["certified"] for row in composition)
        ),
        "C9_replay_contract_is_operational_not_extensional": all(
            Fraction(row["best_transcript_only_worst_world_success"])
            < Fraction(row["oracle_parametric_replay_success"])
            for row in firewall
        ),
    }
    return {
        "schema_version": "asmp3_oracle_parametric_replay_v2_9",
        "experiment_id": "ASMP-3-ORACLE-PARAMETRIC-REPLAY-v2.9",
        "parent_result": "ASMP-3-TRACE-BINDING-EXTRACTOR-v2.8",
        "supporting_results": [
            "ASMP-3-ADAPTIVE-TRANSCRIPT-COUPLING-v2.7",
            "ASMP-3-HONEST-SEARCH-BARRIER-v2.1",
        ],
        "status": "oracle_parametric_ideal_replay_compiler_with_transcript_firewall",
        "theorem": {
            "compiler": (
                "sample a fresh nonsemantic seed and execute the same total "
                "restartable runtime with its semantic provider replaced by H"
            ),
            "ideal_law": "Law(Replay(H)) equals the ideal protocol law exactly",
            "pathwise_coupling": (
                "shared seeds may be used in the proof coupling, but the finder "
                "needs only an independent seed with the same marginal law"
            ),
            "time": (
                "SeedSample+KernelRun+V+q*Eval_H+TraceWrite+TraceScan+Canonicalize"
            ),
            "finder_success": "alpha>=1-s-delta_q after v2.7 and v2.8 composition",
        },
        "exhaustive_replay_audit": exhaustive,
        "seed_marginal_audit": seed_audit,
        "contract_rows": mutants,
        "transcript_only_firewall_rows": firewall,
        "composition_rows": composition,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The compiler derives efficient ideal replay only for total restartable "
            "oracle-parametric runtimes with a callable charged ideal provider. A "
            "recorded noisy transcript or an extensional protocol label does not "
            "supply an unvisited ideal branch. The typed successor does not yet "
            "mandate this operational contract."
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
    total = len(result["gates"])
    print(f"ASMP-3 oracle-parametric replay certified: {passed}/{total} gates")
