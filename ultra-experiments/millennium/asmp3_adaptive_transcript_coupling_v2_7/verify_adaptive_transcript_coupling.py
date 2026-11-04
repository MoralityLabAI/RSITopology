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
RESULT_PATH = HERE / "artifacts" / "adaptive_transcript_coupling_v2_7.json"
OUTPUT_PATH = HERE / "artifacts" / "adaptive_transcript_coupling_verification_v2_7.json"
BLOCK_PATH = HERE.parent / "asmp3_block_selection_composition_v1_9" / "artifacts" / "block_selection_composition_v1_9.json"
NORMAL_PATH = HERE.parent / "asmp3_witness_transparent_normal_form_v2_5" / "artifacts" / "witness_transparent_normal_form_v2_5.json"
DISPOSITION_PATH = HERE.parent / "asmp3_resolution_disposition_v2_6" / "artifacts" / "resolution_disposition_v2_6.json"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(100_000)


def text(value: Q) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


@cache
def block_error(depth: int, eta: Q) -> Q:
    value = sum(
        (Q(comb(depth, k)) * eta**k * (1 - eta) ** (depth - k) for k in range(depth // 2 + 1, depth + 1)),
        Q(0),
    )
    if depth % 2 == 0:
        value += Q(comb(depth, depth // 2)) * eta ** (depth // 2) * (1 - eta) ** (depth // 2) / 2
    return value


def risk(q: int, depth: int, eta: Q) -> Q:
    return 1 - (1 - block_error(depth, eta)) ** q


def min_depth(q: int, eta: Q, target: Q) -> int:
    for depth in (1, *range(3, 2048, 2)):
        if risk(q, depth, eta) <= target:
            return depth
    raise RuntimeError("clean-room depth search exceeded limit")


def reconstruct_row(q: int, eta: Q, target: Q) -> dict[str, object]:
    depth = min_depth(q, eta, target)
    error = block_error(depth, eta)
    delta = risk(q, depth, eta)
    previous = risk(q, depth - 2, eta) if depth > 1 else None
    c, s, g = Q(4, 5), Q(1, 5), Q(3, 5)
    return {
        "maximum_adaptive_semantic_queries": q,
        "eta": text(eta),
        "target_path_coupling_failure": text(target),
        "replications_per_adaptive_query": depth,
        "single_block_majority_error": text(error),
        "adaptive_path_coupling_failure": text(delta),
        "previous_odd_depth_path_failure": text(previous) if previous is not None else None,
        "raw_semantic_query_count": q * depth,
        "ideal_example_completeness": text(c),
        "ideal_example_soundness": text(s),
        "ideal_example_gap": text(g),
        "noisy_completeness_lower_bound": text(c - delta),
        "noisy_soundness_upper_bound": text(s + delta),
        "noisy_gap_lower_bound": text(g - 2 * delta),
        "path_contract": "fresh conditional block sampled only after the current adaptive history fixes the next semantic query",
        "coupled_history_contract": "all nonsemantic coins and strategy kernels are shared; identical decoded prefixes force identical messages, queries, and stopping",
        "minimal_odd_depth_certified": delta <= target and (previous is None or previous > target),
        "certified": True,
    }


def reconstruct_patterns() -> list[dict[str, object]]:
    rows = []
    for eta, depth in ((Q(1, 5), 3), (Q(1, 3), 5), (Q(2, 5), 9)):
        error = block_error(depth, eta)
        for q in range(1, 11):
            no = yes = Q(0)
            count = 0
            for pattern in itertools.product((0, 1), repeat=q):
                failures = sum(pattern)
                probability = error**failures * (1 - error) ** (q - failures)
                if failures:
                    yes += probability
                else:
                    no += probability
                count += 1
            rows.append({
                "eta": text(eta), "replication_depth": depth, "single_block_error": text(error),
                "maximum_adaptive_queries": q, "error_indicator_patterns": count,
                "enumerated_no_error_probability": text(no), "enumerated_any_error_probability": text(yes),
                "closed_form_no_error_probability": text((1-error)**q),
                "closed_form_any_error_probability": text(1-(1-error)**q),
                "certified": count == 2**q and no == (1-error)**q and yes == 1-(1-error)**q and no+yes == 1,
            })
    return rows


def run_tree(policy, stop, world, errors, depth):
    node = 0
    history = []
    rounds = 0
    while rounds < depth:
        if stop & (1 << node):
            return node, tuple(history), rounds, True
        answer = ((world >> policy[node]) & 1) ^ errors[rounds]
        history.append(answer)
        node = 2 * node + 1 + answer
        rounds += 1
    return node, tuple(history), rounds, False


def reconstruct_tree() -> dict[str, object]:
    atoms, depth = 2, 3
    nodes = 2**depth - 1
    policies = list(itertools.product(range(atoms), repeat=nodes))
    errors_all = list(itertools.product((0, 1), repeat=depth))
    digest = hashlib.sha256()
    cases = no_cases = identical = divergent = bad = stopping = 0
    for pi, policy in enumerate(policies):
        for stop in range(1 << nodes):
            for world in range(1 << atoms):
                ideal = run_tree(policy, stop, world, (0,)*depth, depth)
                for errors in errors_all:
                    noisy = run_tree(policy, stop, world, errors, depth)
                    different = ideal != noisy
                    has_error = any(errors)
                    cases += 1
                    if not has_error:
                        no_cases += 1
                        identical += not different
                    if different:
                        divergent += 1
                        bad += not has_error
                    stopping += ideal[3] != noisy[3]
                    digest.update(f"{pi}:{stop}:{world}:{''.join(map(str,errors))}:{ideal}:{noisy}\n".encode("ascii"))
    expected = atoms**nodes * 2**nodes * 2**atoms * 2**depth
    return {
        "atom_count": atoms, "maximum_adaptive_depth": depth, "internal_history_nodes": nodes,
        "deterministic_query_policies": len(policies), "history_dependent_stopping_policies": 2**nodes,
        "semantic_worlds": 2**atoms, "decoded_error_patterns": 2**depth,
        "coupled_execution_cases": cases, "expected_coupled_execution_cases": expected,
        "no_error_cases": no_cases, "identical_paths_on_every_no_error_case": identical,
        "divergent_paths": divergent, "divergence_without_any_error": bad,
        "different_stopping_outcomes_after_errors": stopping,
        "canonical_execution_digest_sha256": digest.hexdigest().upper(),
        "strategy_scope": "all deterministic binary-history query and stopping kernels; conditioning on shared prover/verifier coins reduces randomized strategies to this pathwise form",
        "certified": cases == expected and identical == no_cases and bad == 0 and divergent > 0 and stopping > 0,
    }


def reconstruct_tightness() -> list[dict[str, object]]:
    rows=[]
    for error in (Q(1,10),Q(1,5),Q(1,3)):
        for q in range(1,13):
            mismatch=Q(0); count=0
            for pattern in itertools.product((0,1),repeat=q):
                failures=sum(pattern); probability=error**failures*(1-error)**(q-failures)
                if failures: mismatch+=probability
                count+=1
            bound=1-(1-error)**q
            rows.append({"single_decoded_query_error":text(error),"adaptive_queries":q,"full_depth_error_patterns":count,
                "tight_tree":"query a fresh all-zero atom each round; decide one iff the observed answer history is not all zero",
                "decision_mismatch_probability":text(mismatch),"adaptive_path_bound":text(bound),"bound_attained":mismatch==bound,
                "certified":count==2**q and mismatch==bound})
    return rows


def reconstruct_extraction() -> list[dict[str, object]]:
    rows=[]
    for soundness in (Q(1,5),Q(1,3)):
        for eta in (Q(1,5),Q(1,3)):
            for q in (1,4,16):
                row=reconstruct_row(q,eta,Q(1,100)); delta=Q(row["adaptive_path_coupling_failure"]); alpha=1-soundness-delta
                rows.append({"noisy_protocol_soundness_upper_bound":text(soundness),"maximum_adaptive_queries":q,"eta":text(eta),
                    "replications_per_query":row["replications_per_adaptive_query"],"derived_decision_coupling_failure":row["adaptive_path_coupling_failure"],
                    "v2_5_extracted_finder_success":text(alpha),"extracted_quotient_dimension_bound":q,"raw_semantic_queries":row["raw_semantic_query_count"],
                    "positive_extraction_margin":alpha>0,"remaining_contracts":"witness-transparent ideal rejection and efficient ideal simulation; coupling is now derived",
                    "certified":delta<=Q(1,100) and alpha==1-soundness-delta and alpha>0})
    return rows


def verify() -> dict[str, object]:
    result=json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    block=json.loads(BLOCK_PATH.read_text(encoding="utf-8")); normal=json.loads(NORMAL_PATH.read_text(encoding="utf-8")); disposition=json.loads(DISPOSITION_PATH.read_text(encoding="utf-8"))
    rows=[reconstruct_row(q,eta,target) for eta in (Q(1,5),Q(1,3),Q(2,5)) for q in (1,2,4,8,16,32,64) for target in (Q(1,10),Q(1,100))]
    patterns=reconstruct_patterns(); tree=reconstruct_tree(); tight=reconstruct_tightness(); extraction=reconstruct_extraction()
    checks={
        "V0_schema_parent_status_boundary": result.get("schema_version")=="asmp3_adaptive_transcript_coupling_v2_7" and result.get("status")=="pathwise_adaptive_protocol_coupling_and_robustification_theorem" and result.get("parent_result")=="ASMP-3-WITNESS-TRANSPARENT-NORMAL-FORM-v2.5" and result.get("certified") is True and "does not apply" in result.get("claim_boundary",""),
        "V1_all_42_coupling_rows_reconstructed": result.get("coupling_rows")==rows,
        "V2_all_30_error_pattern_spaces_reconstructed": result.get("error_pattern_rows")==patterns and all(r["certified"] for r in patterns),
        "V3_all_524288_adaptive_tree_cases_reconstructed": result.get("exhaustive_adaptive_tree_audit")==tree and tree["certified"],
        "V4_all_36_tightness_rows_reconstructed": result.get("tightness_rows")==tight and all(r["certified"] for r in tight),
        "V5_all_12_extraction_rows_reconstructed": result.get("derived_extraction_rows")==extraction and all(r["certified"] for r in extraction),
        "V6_path_risk_resource_and_gap_formulas_exact": all(Q(r["noisy_gap_lower_bound"])==Q(3,5)-2*Q(r["adaptive_path_coupling_failure"]) and r["raw_semantic_query_count"]==r["maximum_adaptive_semantic_queries"]*r["replications_per_adaptive_query"] for r in rows),
        "V7_parent_and_resume_trigger_contracts_match": block["theorem"]["independent_M_atom_risk"]=="1-(1-e_d)^M" and normal["theorem"]["extracted_finder_success"]=="alpha>=1-s-delta" and "broader theorem/counterexample" in disposition["disposition"]["resume_condition"],
        "V8_all_11_producer_gates_true": len(result.get("gates",{}))==11 and all(result["gates"].values()),
    }
    return {"schema_version":"asmp3_adaptive_transcript_coupling_verification_v2_7","checker":"clean_room_adaptive_tree_pattern_depth_gap_and_extraction_reconstruction","check_count":len(checks),"checks":checks,"passed":all(checks.values()),
        "claim_boundary":"This checker certifies adaptive path coupling under the declared fresh conditional block law. It does not extend the result to persistent, preselected, or adversarially correlated noise."}


def main() -> None:
    result=verify(); OUTPUT_PATH.parent.mkdir(parents=True,exist_ok=True); OUTPUT_PATH.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    if not result["passed"]:
        raise SystemExit(f"adaptive-transcript verification failed: {[k for k,v in result['checks'].items() if not v]}")
    print(f"ASMP-3 adaptive-transcript verification passed: {result['check_count']}/{result['check_count']}")


if __name__=="__main__":
    main()
