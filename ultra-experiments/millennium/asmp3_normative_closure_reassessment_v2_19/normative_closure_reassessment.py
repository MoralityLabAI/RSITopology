from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ARTIFACT_DIR = HERE / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "normative_closure_reassessment_v2_19.json"
CANONICAL_PATH = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY_PATH = ROOT / "problem_set_v0_1.json"
TYPED_MD_PATH = ROOT / "asmp3_typed_successor_v0_2" / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md"
TYPED_JSON_PATH = ROOT / "asmp3_typed_successor_v0_2" / "typed_successor_v0_2.json"
FORK_THEOREM_PATH = ROOT / "asmp3_protocol_quantifier_v0_7" / "PROTOCOL_QUANTIFIER_THEOREM_v0_7.md"
FORK_PATH = ROOT / "asmp3_protocol_quantifier_v0_7" / "artifacts" / "protocol_quantifier_v0_7.json"
NORMAL_FORM_THEOREM_PATH = ROOT / "asmp3_witness_transparent_normal_form_v2_5" / "WITNESS_TRANSPARENT_NORMAL_FORM_THEOREM_v2_5.md"
NORMAL_FORM_PATH = ROOT / "asmp3_witness_transparent_normal_form_v2_5" / "artifacts" / "witness_transparent_normal_form_v2_5.json"
V2_17_PATH = ROOT / "asmp3_consolidated_resource_scope_v2_17" / "artifacts" / "consolidated_resource_scope_v2_17.json"
V2_18_THEOREM_PATH = ROOT / "asmp3_normative_closure_impossibility_v2_18" / "NORMATIVE_CLOSURE_IMPOSSIBILITY_THEOREM_v2_18.md"
V2_18_PATH = ROOT / "asmp3_normative_closure_impossibility_v2_18" / "artifacts" / "normative_closure_impossibility_v2_18.json"
V2_18_VERIFY_PATH = ROOT / "asmp3_normative_closure_impossibility_v2_18" / "artifacts" / "normative_closure_impossibility_verification_v2_18.json"
EXPERT_PATH = ROOT / "asmp3_resolution_boundary_v0_3" / "artifacts" / "expert_review_status_v0_6.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def collapse(text: str) -> str:
    return " ".join(text.split())


def extract_asmp3(text: str) -> str:
    if "# ASMP-3" not in text or "# ASMP-4" not in text:
        raise ValueError("canonical ASMP-3 section delimiters are missing")
    return text.split("# ASMP-3", 1)[1].split("# ASMP-4", 1)[0]


def source_structure_audit() -> dict[str, object]:
    canonical = CANONICAL_PATH.read_text(encoding="utf-8")
    section = extract_asmp3(canonical)
    linear = collapse(section)
    markers = (
        "## Canonical mathematical setting",
        "For input length `n`, freeze a decision relation `R_n`",
        "Admissible transcript encodings, verifier and prover randomness, and adaptive query access are part of the game",
        "Freeze a decidable syntactic relation",
        "## Weak-Verifier Characterization Conjecture",
        "A task family admits a constant-gap, doubly efficient, noise-robust oversight protocol",
        "## What a complete resolution requires",
    )
    positions = {marker: linear.index(marker) if marker in linear else -1 for marker in markers}
    ordered = all(value >= 0 for value in positions.values()) and list(positions.values()) == sorted(positions.values())
    flat = linear
    missing_scope_definitions = {
        "formal_protocol_algorithm_quantifier": "protocol algorithms are quantified" not in flat,
        "declared_interface_class": "Interfaces(E" not in flat,
        "protocol_selects_game_interface": "protocol may select" not in flat and "protocol selects" not in flat,
        "source_language_satisfaction_relation": "satisfaction relation" not in flat and "formal semantics" not in flat,
    }
    return {
        "ordered_markers": positions,
        "canonical_setting_precedes_protocol_admission": ordered,
        "freeze_instruction_precedes_game_membership_and_conjecture": ordered,
        "missing_scope_definitions": missing_scope_definitions,
        "all_scope_definitions_missing": all(missing_scope_definitions.values()),
        "conservative_reading": "FIX",
        "conservative_reading_reason": "ordinary sequential scope keeps protocol algorithms inside the already frozen canonical game",
        "formal_entailment_of_FIX_proved": False,
        "certified_syntactic_facts_only": ordered and all(missing_scope_definitions.values()),
    }


def interface_delta_audit() -> dict[str, object]:
    canonical = extract_asmp3(CANONICAL_PATH.read_text(encoding="utf-8"))
    typed_md = TYPED_MD_PATH.read_text(encoding="utf-8")
    typed = json.loads(TYPED_JSON_PATH.read_text(encoding="utf-8"))
    additions = {
        "typed_environment_E_n": "`E_n`" in typed_md and "`E_n`" not in canonical,
        "typed_game_interface_G_n": "`G_n`" in typed_md and "`G_n`" not in canonical,
        "declared_Interfaces_E_n": "`Interfaces(E_n)`" in typed_md and "`Interfaces(E_n)`" not in canonical,
        "admissible_protocol_package_Q_n": "admissible protocol package" in typed_md and "admissible protocol package" not in canonical,
    }
    typed_status_ok = (
        typed.get("status") == "nonnormative_successor_draft"
        and typed.get("changes_parent_problem") is False
        and set(typed.get("successor_targets", [])) == {"characterize_WV_FIX", "characterize_WV_ADM"}
    )
    return {
        "ADM_added_objects": additions,
        "ADM_added_object_count": sum(additions.values()),
        "typed_successor_status_check": typed_status_ok,
        "ADM_is_reasonable_successor_target": True,
        "ADM_clause_preservation_status": "not_established",
        "why_not_established": "ADM adds an interface class and moves game selection into protocol admission; no formal semantics proves that this preserves the earlier freeze scope",
        "FIX_status": "conservative_natural_reading_not_formally_entailed",
        "certified": all(additions.values()) and typed_status_ok,
    }


def prior_claim_audit() -> dict[str, object]:
    v2_18 = json.loads(V2_18_PATH.read_text(encoding="utf-8"))
    verification = json.loads(V2_18_VERIFY_PATH.read_text(encoding="utf-8"))
    theorem = V2_18_THEOREM_PATH.read_text(encoding="utf-8")
    selector = v2_18.get("selector_audit", {})
    model_rows = v2_18.get("completion_models", [])
    conditional_lemma = (
        selector.get("sound_decisive_selector_count") == 0
        and {row.get("mode") for row in model_rows} == {"FIX", "ADM"}
        and "Assume a source-only rule" in theorem
    )
    satisfaction_proof_fields = {
        "formal_source_semantics": "formal_source_semantics" in v2_18,
        "model_satisfaction_derivation": "model_satisfaction_derivation" in v2_18,
        "independent_ADM_scope_proof": "independent_ADM_scope_proof" in v2_18,
    }
    rows = [
        {
            "claim": "conditional_no_singleton_selector_lemma",
            "status": "valid_conditional_on_two_legitimate_completions",
            "supported": conditional_lemma,
        },
        {
            "claim": "ADM_is_clause_preserving",
            "status": "asserted_not_rigorously_established",
            "supported": False,
        },
        {
            "claim": "v0_1_is_definitely_semantically_underdetermined",
            "status": "plausible_but_incomplete",
            "supported": False,
        },
        {
            "claim": "ASMP_3_is_impossible_to_solve_or_achieve",
            "status": "not_proved",
            "supported": False,
        },
        {
            "claim": "v2_18_satisfies_resolve_or_impossibility_goal",
            "status": "withdrawn",
            "supported": False,
        },
    ]
    return {
        "v2_18_producer_certified": v2_18.get("certified") is True,
        "v2_18_verifier_passed": verification.get("passed") is True,
        "what_those_checks_establish": "internal consistency of the encoded two-completion assumption",
        "satisfaction_proof_fields_present": satisfaction_proof_fields,
        "satisfaction_proof_field_count": sum(satisfaction_proof_fields.values()),
        "claim_rows": rows,
        "conditional_lemma_survives": conditional_lemma,
        "prior_goal_completion_withdrawn": True,
        "certified": conditional_lemma and not any(satisfaction_proof_fields.values()) and rows[-1]["status"] == "withdrawn",
    }


def strict_fix_mathematical_audit() -> dict[str, object]:
    fork = json.loads(FORK_PATH.read_text(encoding="utf-8"))
    normal = json.loads(NORMAL_FORM_PATH.read_text(encoding="utf-8"))
    fork_theorem = FORK_THEOREM_PATH.read_text(encoding="utf-8")
    normal_theorem = collapse(NORMAL_FORM_THEOREM_PATH.read_text(encoding="utf-8"))
    sufficiency = (
        fork.get("certified") is True
        and fork.get("frozen_encoding_branch", {}).get("asymptotic_gap") == "(3/5)^d -> 0"
        and all(fork.get("gates", {}).get(name) is True for name in ("G1_refutation_dimension_equals_depth", "H0_uniform_honest_strategy_case_coverage", "P2_frozen_gap_vanishes"))
        and "displayed sufficiency direction" in fork_theorem
    )
    necessity = (
        normal.get("certified") is True
        and len(normal.get("nonbinding_refute_rows", [])) == 6
        and all(row.get("literal_only_if_direction_fails") is True for row in normal.get("nonbinding_refute_rows", []))
        and "protocol admission and the displayed refutation dimension are logically independent" in normal_theorem
    )
    return {
        "working_interpretation": "strict_FIX",
        "interpretation_authoritative": False,
        "displayed_sufficiency_direction": "exactly_refuted" if sufficiency else "not_certified",
        "displayed_necessity_direction": "exactly_refuted" if necessity else "not_certified",
        "displayed_iff_status": "internally_refuted_in_both_directions" if sufficiency and necessity else "not_certified",
        "v0_7_exact_gap": fork.get("frozen_encoding_branch", {}).get("asymptotic_gap"),
        "v2_5_nonbinding_rows": len(normal.get("nonbinding_refute_rows", [])),
        "broader_classification_resolved": False,
        "mathematical_impossibility_proved": False,
        "certified": sufficiency and necessity,
    }


def resolution_policy_audit() -> dict[str, object]:
    canonical = collapse(CANONICAL_PATH.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    problem = next(row for row in registry["problems"] if row["id"] == "ASMP-3")
    complete_items = (
        "A formal complexity class for the protocols above and a class equality, separation, or complete invariant characterizing it",
        "A constructive protocol with explicit completeness and soundness against adaptive, obfuscating provers",
        "Matching communication, semantic-query, and honest-prover lower bounds",
        "A robust theorem for correlated/noisy semantic judgments",
        "A proof that the local-refutation definition is invariant under benign transcript encodings",
    )
    policy_markers = {
        "single_criterion_refutation_not_enough": "Refuting one proposed criterion does not resolve a broader classification program unless that criterion is the entire frozen statement" in canonical,
        "full_frozen_statement_required": "The result covers the full frozen canonical statement" in canonical,
        "changed_assumption_is_new_version": "Any changed assumption creates a new problem version" in canonical,
        "negative_requires_sharp_boundary": "A negative resolution receives equal standing when it supplies the sharp impossibility boundary required by the statement" in canonical,
    }
    requirement_presence = {item: item in canonical for item in complete_items}
    return {
        "canonical_policy_markers": policy_markers,
        "complete_resolution_item_presence": requirement_presence,
        "complete_resolution_items_present": sum(requirement_presence.values()),
        "registry_is_normative": registry.get("registry_is_normative"),
        "registry_canonical_target": problem.get("canonical_target"),
        "registry_negative_resolution_allowed": problem.get("negative_resolution_allowed"),
        "literal_iff_refutation_is_full_resolution": False,
        "reason": "the displayed iff is one proposed criterion inside a broader class-characterization program",
        "certified": all(policy_markers.values()) and all(requirement_presence.values()) and registry.get("registry_is_normative") is False,
    }


def authority_and_progress_audit() -> dict[str, object]:
    v2_17 = json.loads(V2_17_PATH.read_text(encoding="utf-8"))
    expert = json.loads(EXPERT_PATH.read_text(encoding="utf-8"))
    disposition = v2_17.get("disposition", {})
    return {
        "prior_internal_named_iff_status": disposition.get("literal_v0_1_iff"),
        "prior_unrestricted_classification": disposition.get("unrestricted_classification"),
        "prior_normative_definition": disposition.get("normative_definition"),
        "external_qualifying_teams": expert.get("qualifying_receipts"),
        "external_required_teams": expert.get("minimum_independent_teams"),
        "external_completion_gate": expert.get("completion_gate_satisfied"),
        "certified": (
            v2_17.get("certified") is True
            and disposition.get("normative_definition") == "unclosed"
            and expert.get("qualifying_receipts") == 0
            and expert.get("minimum_independent_teams") == 2
            and expert.get("completion_gate_satisfied") is False
        ),
    }


def build_artifact() -> dict[str, object]:
    source = source_structure_audit()
    delta = interface_delta_audit()
    prior = prior_claim_audit()
    strict_fix = strict_fix_mathematical_audit()
    policy = resolution_policy_audit()
    progress = authority_and_progress_audit()
    disposition = {
        "v2_18_unconditional_closure_claim": "withdrawn",
        "conditional_selector_lemma": "valid",
        "ADM_clause_preservation": "not_established",
        "best_supported_v0_1_reading": "strict_FIX_but_not_formally_entailed",
        "strict_FIX_displayed_iff": "internally_refuted_in_both_directions",
        "full_ASMP_3_classification": "not_established",
        "ASMP_3_mathematical_impossibility": "not_proved",
        "prize_grade_resolution": "not_established",
        "best_operational_conclusion": "formalize a strict FIX target or publish FIX and ADM separately before claiming a unique unrestricted characterization",
    }
    stop_resume = {
        "stop": [
            "treating v2_18 as a completion of the resolve-or-impossibility goal",
            "claiming ADM is clause-preserving without a formal source semantics",
            "extending parity grids whose strict-FIX gap is already symbolic",
        ],
        "continue_or_resume": [
            "an authoritative scope clarification",
            "a registered strict-FIX formal class and reduction notion",
            "a non-black-box task-specific or universal structure theorem",
            "interface-uniform resource lower bounds for that registered class",
            "attributable external reproduction",
        ],
        "all_internal_search_should_stop": False,
        "current_source_only_impossibility_lane_should_stop": True,
    }
    gates = {
        "R0_all_sealed_inputs_hashed": True,
        "R1_source_order_supports_FIX_as_conservative_but_not_formally_entailed": source["certified_syntactic_facts_only"] and not source["formal_entailment_of_FIX_proved"],
        "R2_ADM_introduces_undeclared_interface_objects": delta["certified"] and delta["ADM_added_object_count"] == 4,
        "R3_ADM_clause_preservation_is_not_certified": delta["ADM_clause_preservation_status"] == "not_established",
        "R4_v2_18_survives_only_as_conditional_selector_lemma": prior["certified"] and prior["conditional_lemma_survives"],
        "R5_strict_FIX_sufficiency_and_literal_necessity_are_both_refuted": strict_fix["certified"],
        "R6_canonical_policy_blocks_promotion_of_criterion_refutation_to_full_resolution": policy["certified"] and not policy["literal_iff_refutation_is_full_resolution"],
        "R7_full_classification_and_impossibility_are_not_established": not strict_fix["broader_classification_resolved"] and not strict_fix["mathematical_impossibility_proved"],
        "R8_normative_and_external_gates_remain_open": progress["certified"],
        "R9_stop_is_lane_specific_and_has_concrete_resume_triggers": stop_resume["current_source_only_impossibility_lane_should_stop"] and not stop_resume["all_internal_search_should_stop"] and len(stop_resume["continue_or_resume"]) == 5,
    }
    hashes = {
        "canonical_sha256": sha256(CANONICAL_PATH),
        "registry_sha256": sha256(REGISTRY_PATH),
        "typed_markdown_sha256": sha256(TYPED_MD_PATH),
        "typed_json_sha256": sha256(TYPED_JSON_PATH),
        "v0_7_theorem_sha256": sha256(FORK_THEOREM_PATH),
        "v0_7_artifact_sha256": sha256(FORK_PATH),
        "v2_5_theorem_sha256": sha256(NORMAL_FORM_THEOREM_PATH),
        "v2_5_artifact_sha256": sha256(NORMAL_FORM_PATH),
        "v2_17_artifact_sha256": sha256(V2_17_PATH),
        "v2_18_theorem_sha256": sha256(V2_18_THEOREM_PATH),
        "v2_18_artifact_sha256": sha256(V2_18_PATH),
        "v2_18_verification_sha256": sha256(V2_18_VERIFY_PATH),
        "expert_status_sha256": sha256(EXPERT_PATH),
    }
    gates["R0_all_sealed_inputs_hashed"] = len(hashes) == 13 and all(len(value) == 64 for value in hashes.values())
    return {
        "schema_version": "asmp3_normative_closure_reassessment_v2_19",
        "experiment_id": "ASMP-3-NORMATIVE-CLOSURE-REASSESSMENT-v2.19",
        "status": "v2_18_goal_completion_withdrawn_conditional_lemma_retained_full_ASMP3_open",
        "parent_result": "ASMP-3-NORMATIVE-CLOSURE-IMPOSSIBILITY-v2.18",
        "source_hashes": hashes,
        "source_structure_audit": source,
        "interface_delta_audit": delta,
        "prior_claim_audit": prior,
        "strict_FIX_mathematical_audit": strict_fix,
        "resolution_policy_audit": policy,
        "authority_and_progress_audit": progress,
        "disposition": disposition,
        "stop_resume": stop_resume,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "This reassessment proves that v2.18 does not complete the resolve-or-impossibility goal. "
            "It retains the conditional selector lemma, records strict FIX as the conservative natural "
            "reading, and cross-checks the exact two-sided refutation of the displayed iff. It does not "
            "prove formal-language entailment of FIX, a complete unrestricted characterization, "
            "mathematical impossibility of ASMP-3, or external acceptance."
        ),
    }


def write_artifact() -> dict[str, object]:
    artifact = build_artifact()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return artifact
