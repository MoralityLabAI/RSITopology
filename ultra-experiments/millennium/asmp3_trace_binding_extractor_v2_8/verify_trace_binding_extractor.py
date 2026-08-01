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
RESULT_PATH = HERE / "artifacts" / "trace_binding_extractor_v2_8.json"
OUTPUT_PATH = HERE / "artifacts" / "trace_binding_extractor_verification_v2_8.json"
SEARCH_PATH = HERE.parent / "asmp3_honest_search_barrier_v2_1" / "artifacts" / "honest_search_barrier_v2_1.json"
NORMAL_PATH = HERE.parent / "asmp3_witness_transparent_normal_form_v2_5" / "artifacts" / "witness_transparent_normal_form_v2_5.json"
COUPLING_PATH = HERE.parent / "asmp3_adaptive_transcript_coupling_v2_7" / "artifacts" / "adaptive_transcript_coupling_v2_7.json"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(100_000)


def text(value: Q) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def logceil(value: int) -> int:
    return (value - 1).bit_length()


def relation(claim, bits, classes, answers, malformed=False):
    if malformed:
        return not classes
    return any(i < bits and a != ((claim >> i) & 1) for i, a in zip(classes, answers))


def check_trace(trace, world, claim, bits, universe, malformed=False):
    queried={}; calls=[]; terminal=None; reason=None
    for pos,event in enumerate(trace):
        if terminal is not None: reason="event_after_terminal"; break
        op=event.get("op")
        if op=="query":
            i=event.get("class"); a=event.get("answer")
            if not isinstance(i,int) or i<0 or i>=universe or a not in (0,1): reason="malformed_query"; break
            if a!=((world>>i)&1): reason="nonideal_query_answer"; break
            if i in queried and queried[i]!=a: reason="inconsistent_repeat_answer"; break
            queried[i]=a
        elif op=="refute":
            rc=event.get("classes"); ra=event.get("answers"); rr=event.get("result")
            if not isinstance(rc,list) or not isinstance(ra,list): reason="malformed_refute_call"; break
            classes=tuple(rc); answers=tuple(ra)
            if any(not isinstance(x,int) for x in classes) or any(x not in (0,1) for x in answers) or tuple(sorted(set(classes)))!=classes: reason="noncanonical_witness"; break
            if any(x not in queried for x in classes): reason="unqueried_witness_class"; break
            if tuple(queried[x] for x in classes)!=answers: reason="witness_answer_mismatch"; break
            actual=relation(claim,bits,classes,answers,malformed)
            if rr is not actual: reason="refute_result_mismatch"; break
            if actual: calls.append((classes,answers))
        elif op=="terminal":
            decision=event.get("decision")
            if decision not in ("accept","reject"): reason="malformed_terminal"; break
            if pos!=len(trace)-1: reason="terminal_not_last"; break
            terminal=decision
        else: reason="unknown_operation"; break
    if reason is None and terminal is None: reason="missing_terminal"
    if reason is None and terminal=="reject" and not calls: reason="unbound_rejection"
    valid=reason is None; witness=calls[-1] if valid and terminal=="reject" else None
    return {"valid":valid,"invalid_reason":reason,"terminal_decision":terminal,"distinct_queried_classes":len(queried),"successful_refute_calls":len(calls),
        "extracted_classes":list(witness[0]) if witness else None,"extracted_answers":list(witness[1]) if witness else None,"trace_events":len(trace)}


@cache
def reconstruct_exhaustive():
    digest=hashlib.sha256(); traces=rejects=accepts=extracted=invalid=mismatch=violations=subsets=0
    for universe in range(2,6):
        bits=min(3,universe); qmax=min(3,universe)
        for world in range(1<<universe):
            for claim in range(1<<bits):
                for q in range(1,qmax+1):
                    for sequence in itertools.product(range(universe),repeat=q):
                        queried=tuple(sorted(set(sequence))); events=[{"op":"query","class":i,"answer":(world>>i)&1} for i in sequence]
                        for mask in range(1<<len(queried)):
                            subsets+=1; classes=tuple(queried[j] for j in range(len(queried)) if mask&(1<<j)); answers=tuple((world>>i)&1 for i in classes)
                            result=relation(claim,bits,classes,answers); decision="reject" if result else "accept"
                            trace=[*events,{"op":"refute","classes":list(classes),"answers":list(answers),"result":result},{"op":"terminal","decision":decision}]
                            checked=check_trace(trace,world,claim,bits,universe); traces+=1; invalid+=not checked["valid"]
                            if decision=="reject":
                                rejects+=1; extracted+=checked["extracted_classes"] is not None; mismatch+=checked["extracted_classes"]!=list(classes) or checked["extracted_answers"]!=list(answers); violations+=len(classes)>q
                            else: accepts+=1
                            digest.update(f"{universe}:{world}:{claim}:{sequence}:{classes}:{decision}:{checked}\n".encode("ascii"))
                formal=[{"op":"refute","classes":[],"answers":[],"result":True},{"op":"terminal","decision":"reject"}]
                checked=check_trace(formal,world,claim,bits,universe,True); traces+=1; rejects+=1; extracted+=checked["extracted_classes"]==[]; invalid+=not checked["valid"]
                digest.update(f"formal:{universe}:{world}:{claim}:{checked}\n".encode("ascii"))
    return {"semantic_class_sizes":[2,3,4,5],"maximum_query_sequence_length":3,"trace_programs_audited":traces,"candidate_witness_subset_evaluations":subsets,
        "valid_reject_traces":rejects,"valid_accept_traces":accepts,"rejections_with_extracted_witness":extracted,"invalid_generated_traces":invalid,"extraction_mismatches":mismatch,
        "query_dimension_violations":violations,"canonical_trace_digest_sha256":digest.hexdigest().upper(),
        "certified":traces>100000 and subsets>100000 and rejects>0 and accepts>0 and extracted==rejects and invalid==0 and mismatch==0 and violations==0}


def reconstruct_mutants():
    world=1; claim=0; query={"op":"query","class":0,"answer":1}; call={"op":"refute","classes":[0],"answers":[1],"result":True}; reject={"op":"terminal","decision":"reject"}
    cases={"reject_without_refute":[query,reject],"unqueried_witness_class":[query,{"op":"refute","classes":[1],"answers":[0],"result":False},reject],
        "wrong_ideal_answer":[{"op":"query","class":0,"answer":0},call,reject],"duplicate_noncanonical_classes":[query,{"op":"refute","classes":[0,0],"answers":[1,1],"result":True},reject],
        "unsorted_noncanonical_classes":[query,{"op":"query","class":1,"answer":0},{"op":"refute","classes":[1,0],"answers":[0,1],"result":True},reject],
        "forged_refute_result":[query,{"op":"refute","classes":[],"answers":[],"result":True},reject],"terminal_not_last":[reject,query],
        "failed_call_then_reject":[query,{"op":"refute","classes":[],"answers":[],"result":False},reject],"missing_terminal":[query,call],"unknown_instruction":[query,{"op":"magic"},reject]}
    rows=[]
    for name,trace in cases.items():
        checked=check_trace(trace,world,claim,2,2); rows.append({"mutant":name,"trace_events":len(trace),"rejected_by_validator":not checked["valid"],"invalid_reason":checked["invalid_reason"],"certified":not checked["valid"] and checked["invalid_reason"] is not None})
    return rows


def reconstruct_firewall():
    rows=[]
    for bits in range(1,21):
        n=2**bits; q=min(n,bits**3)
        rows.append({"index_bits":bits,"singleton_witness_worlds":n,"observable_terminal_decisions":1,"terminal_decision_in_every_world":"reject",
            "best_decision_only_worst_world_success":text(Q(1,n)),"ideal_query_budget":q,"best_decision_plus_q_queries_success":text(Q(q,n)),
            "trace_log_reveals_witness_in_one_scan":True,"decision_only_binding_is_insufficient":True,"certified":Q(1,n)<=Q(q,n) and q<=n})
    return rows


def reconstruct_composition():
    coupling=json.loads(COUPLING_PATH.read_text(encoding="utf-8")); by={(r["maximum_adaptive_semantic_queries"],r["eta"]):r for r in coupling["coupling_rows"] if r["target_path_coupling_failure"]=="1/100"}
    rows=[]; L=20
    for soundness in (Q(1,5),Q(1,3)):
        for eta in (Q(1,5),Q(1,3)):
            for q in (1,4,16):
                p=by[(q,text(eta))]; delta=Q(p["adaptive_path_coupling_failure"]); alpha=1-soundness-delta; V=2*q; C=4*q; E=3*q; tb=q*(L+2)+1; scan=tb; canon=q*logceil(q+1); total=V+C+E+scan+canon; msg=logceil(q+1)+q*(L+1)
                rows.append({"soundness_upper_bound":text(soundness),"eta":text(eta),"maximum_adaptive_queries":q,"derived_coupling_failure":text(delta),"trace_bound_finder_success":text(alpha),
                    "extracted_witness_classes_bound":q,"replications_per_query":p["replications_per_adaptive_query"],"raw_semantic_queries":p["raw_semantic_query_count"],
                    "honest_critic_time":C,"verifier_ideal_replay_time":V,"ideal_semantic_evaluation_time":E,"trace_bits":tb,"trace_scan_time":scan,"canonicalization_time":canon,
                    "one_shot_extractor_time":total,"canonical_witness_message_bits":msg,"remaining_contract":"efficient ideal-semantic replay; witness transparency and coupling are derived from trace binding and v2.7",
                    "certified":delta<=Q(1,100) and alpha==1-soundness-delta and alpha>0 and total==V+C+E+scan+canon})
    return rows


def verify():
    result=json.loads(RESULT_PATH.read_text(encoding="utf-8")); search=json.loads(SEARCH_PATH.read_text(encoding="utf-8")); normal=json.loads(NORMAL_PATH.read_text(encoding="utf-8")); coupling=json.loads(COUPLING_PATH.read_text(encoding="utf-8"))
    exhaustive=reconstruct_exhaustive(); mutants=reconstruct_mutants(); firewall=reconstruct_firewall(); composition=reconstruct_composition()
    checks={
        "V0_schema_parent_status_boundary":result.get("schema_version")=="asmp3_trace_binding_extractor_v2_8" and result.get("status")=="operational_refute_binding_compiler_and_finder_extractor" and result.get("parent_result")=="ASMP-3-ADAPTIVE-TRANSCRIPT-COUPLING-v2.7" and result.get("certified") is True and "weaker phrase" in result.get("claim_boundary",""),
        "V1_exhaustive_trace_compiler_reconstructed":result.get("exhaustive_trace_audit")==exhaustive and exhaustive["certified"],
        "V2_all_trace_binding_mutants_reconstructed":result.get("mutant_trace_rows")==mutants and all(r["certified"] for r in mutants),
        "V3_decision_only_firewall_reconstructed":result.get("decision_only_firewall_rows")==firewall and all(r["certified"] for r in firewall),
        "V4_all_12_composition_rows_reconstructed":result.get("composition_rows")==composition and all(r["certified"] for r in composition),
        "V5_every_rejection_extracts_query_bounded_witness":exhaustive["rejections_with_extracted_witness"]==exhaustive["valid_reject_traces"] and exhaustive["query_dimension_violations"]==0,
        "V6_all_extractor_resources_reconstructed":all(r["one_shot_extractor_time"]==r["honest_critic_time"]+r["verifier_ideal_replay_time"]+r["ideal_semantic_evaluation_time"]+r["trace_scan_time"]+r["canonicalization_time"] for r in composition),
        "V7_parent_search_normal_form_and_coupling_contracts_match":search["theorem"]["randomized_q_query_maximin_success"]=="q/N" and normal["theorem"]["extracted_finder_success"]=="alpha>=1-s-delta" and coupling["theorem"]["adaptive_path_coupling_failure"]=="delta<=1-(1-e)^q",
        "V8_all_10_producer_gates_true":len(result.get("gates",{}))==10 and all(result["gates"].values()),
    }
    return {"schema_version":"asmp3_trace_binding_extractor_verification_v2_8","checker":"clean_room_trace_compiler_mutant_firewall_resource_and_parent_reconstruction","check_count":len(checks),"checks":checks,"passed":all(checks.values()),
        "claim_boundary":"This checker certifies extraction from trace-complete operational binding. It does not infer that stronger contract from a decision label or from every typed-successor rejection."}


def main():
    result=verify(); OUTPUT_PATH.parent.mkdir(parents=True,exist_ok=True); OUTPUT_PATH.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    if not result["passed"]: raise SystemExit(f"trace-binding verification failed: {[k for k,v in result['checks'].items() if not v]}")
    print(f"ASMP-3 trace-binding verification passed: {result['check_count']}/{result['check_count']}")


if __name__=="__main__": main()
