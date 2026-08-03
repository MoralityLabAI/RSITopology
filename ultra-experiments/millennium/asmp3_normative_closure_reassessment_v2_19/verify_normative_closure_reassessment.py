from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULT_PATH = HERE / "artifacts" / "normative_closure_reassessment_v2_19.json"
VERIFY_PATH = HERE / "artifacts" / "normative_closure_reassessment_verification_v2_19.json"
PATHS = {
    "canonical_sha256": ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "registry_sha256": ROOT / "problem_set_v0_1.json",
    "typed_markdown_sha256": ROOT / "asmp3_typed_successor_v0_2" / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md",
    "typed_json_sha256": ROOT / "asmp3_typed_successor_v0_2" / "typed_successor_v0_2.json",
    "v0_7_theorem_sha256": ROOT / "asmp3_protocol_quantifier_v0_7" / "PROTOCOL_QUANTIFIER_THEOREM_v0_7.md",
    "v0_7_artifact_sha256": ROOT / "asmp3_protocol_quantifier_v0_7" / "artifacts" / "protocol_quantifier_v0_7.json",
    "v2_5_theorem_sha256": ROOT / "asmp3_witness_transparent_normal_form_v2_5" / "WITNESS_TRANSPARENT_NORMAL_FORM_THEOREM_v2_5.md",
    "v2_5_artifact_sha256": ROOT / "asmp3_witness_transparent_normal_form_v2_5" / "artifacts" / "witness_transparent_normal_form_v2_5.json",
    "v2_17_artifact_sha256": ROOT / "asmp3_consolidated_resource_scope_v2_17" / "artifacts" / "consolidated_resource_scope_v2_17.json",
    "v2_18_theorem_sha256": ROOT / "asmp3_normative_closure_impossibility_v2_18" / "NORMATIVE_CLOSURE_IMPOSSIBILITY_THEOREM_v2_18.md",
    "v2_18_artifact_sha256": ROOT / "asmp3_normative_closure_impossibility_v2_18" / "artifacts" / "normative_closure_impossibility_v2_18.json",
    "v2_18_verification_sha256": ROOT / "asmp3_normative_closure_impossibility_v2_18" / "artifacts" / "normative_closure_impossibility_verification_v2_18.json",
    "expert_status_sha256": ROOT / "asmp3_resolution_boundary_v0_3" / "artifacts" / "expert_review_status_v0_6.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def collapse(text: str) -> str:
    return " ".join(text.split())


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    canonical = PATHS["canonical_sha256"].read_text(encoding="utf-8")
    section = canonical.split("# ASMP-3", 1)[1].split("# ASMP-4", 1)[0]
    flat_section = collapse(section)
    flat_all = collapse(canonical)
    registry = json.loads(PATHS["registry_sha256"].read_text(encoding="utf-8"))
    typed_md = PATHS["typed_markdown_sha256"].read_text(encoding="utf-8")
    typed = json.loads(PATHS["typed_json_sha256"].read_text(encoding="utf-8"))
    fork = json.loads(PATHS["v0_7_artifact_sha256"].read_text(encoding="utf-8"))
    normal = json.loads(PATHS["v2_5_artifact_sha256"].read_text(encoding="utf-8"))
    v2_17 = json.loads(PATHS["v2_17_artifact_sha256"].read_text(encoding="utf-8"))
    v2_18 = json.loads(PATHS["v2_18_artifact_sha256"].read_text(encoding="utf-8"))
    v2_18_verify = json.loads(PATHS["v2_18_verification_sha256"].read_text(encoding="utf-8"))
    expert = json.loads(PATHS["expert_status_sha256"].read_text(encoding="utf-8"))
    hashes = {name: sha256(path) for name, path in PATHS.items()}

    ordered_markers = (
        "## Canonical mathematical setting",
        "For input length `n`, freeze a decision relation `R_n`",
        "Admissible transcript encodings, verifier and prover randomness, and adaptive query access are part of the game",
        "Freeze a decidable syntactic relation",
        "## Weak-Verifier Characterization Conjecture",
        "A task family admits a constant-gap, doubly efficient, noise-robust oversight protocol",
        "## What a complete resolution requires",
    )
    positions = [flat_section.index(marker) if marker in flat_section else -1 for marker in ordered_markers]
    order_ok = all(value >= 0 for value in positions) and positions == sorted(positions)
    source_has_no_adm_layer = all(
        marker not in flat_section
        for marker in ("Interfaces(E", "WV-ADM", "admissible protocol package", "protocol may select")
    )
    typed_adds_adm_layer = all(
        marker in typed_md for marker in ("`E_n`", "`G_n`", "`Interfaces(E_n)`", "admissible protocol package")
    )

    selector_rows = {row["selector_output"]: row for row in v2_18["selector_audit"]["rows"]}
    conditional_lemma = (
        v2_18["selector_audit"]["sound_decisive_selector_count"] == 0
        and selector_rows["FIX"]["entailment_sound"] is False
        and selector_rows["ADM"]["entailment_sound"] is False
        and selector_rows["BOTH"]["decisive_singleton"] is False
    )
    missing_satisfaction_proof = not any(
        name in v2_18
        for name in ("formal_source_semantics", "model_satisfaction_derivation", "independent_ADM_scope_proof")
    )

    strict_fix_sufficiency = (
        fork["certified"] is True
        and fork["frozen_encoding_branch"]["asymptotic_gap"] == "(3/5)^d -> 0"
        and fork["gates"]["G1_refutation_dimension_equals_depth"] is True
        and fork["gates"]["H0_uniform_honest_strategy_case_coverage"] is True
        and fork["gates"]["P2_frozen_gap_vanishes"] is True
    )
    literal_necessity = (
        normal["certified"] is True
        and len(normal["nonbinding_refute_rows"]) == 6
        and all(row["literal_only_if_direction_fails"] is True for row in normal["nonbinding_refute_rows"])
    )
    policy = (
        "Refuting one proposed criterion does not resolve a broader classification program unless that criterion is the entire frozen statement" in flat_all
        and "The result covers the full frozen canonical statement" in flat_all
        and "Any changed assumption creates a new problem version" in flat_all
        and "A negative resolution receives equal standing when it supplies the sharp impossibility boundary required by the statement" in flat_all
    )
    complete_items = all(
        marker in flat_section
        for marker in (
            "A formal complexity class for the protocols above",
            "A constructive protocol with explicit completeness and soundness",
            "Matching communication, semantic-query, and honest-prover lower bounds",
            "A robust theorem for correlated/noisy semantic judgments",
            "invariant under benign transcript encodings",
        )
    )
    disposition = result.get("disposition", {})
    progress = v2_17.get("disposition", {})
    checks = {
        "V0_schema_parent_status_and_all_hashes": result.get("schema_version") == "asmp3_normative_closure_reassessment_v2_19" and result.get("parent_result") == "ASMP-3-NORMATIVE-CLOSURE-IMPOSSIBILITY-v2.18" and result.get("source_hashes") == hashes,
        "V1_canonical_order_makes_FIX_conservative_without_formal_entailment": order_ok and source_has_no_adm_layer and result["source_structure_audit"]["conservative_reading"] == "FIX" and result["source_structure_audit"]["formal_entailment_of_FIX_proved"] is False,
        "V2_ADM_layer_is_added_only_by_nonnormative_successor": typed_adds_adm_layer and typed["status"] == "nonnormative_successor_draft" and typed["changes_parent_problem"] is False and result["interface_delta_audit"]["ADM_clause_preservation_status"] == "not_established",
        "V3_v2_18_checks_only_the_conditional_selector_lemma": v2_18["certified"] is True and v2_18_verify["passed"] is True and conditional_lemma and missing_satisfaction_proof and result["prior_claim_audit"]["prior_goal_completion_withdrawn"] is True,
        "V4_strict_FIX_sufficiency_counterfamily_reconstructed": strict_fix_sufficiency and result["strict_FIX_mathematical_audit"]["displayed_sufficiency_direction"] == "exactly_refuted",
        "V5_literal_necessity_counterfamily_reconstructed": literal_necessity and result["strict_FIX_mathematical_audit"]["displayed_necessity_direction"] == "exactly_refuted",
        "V6_canonical_resolution_policy_prevents_full_resolution_promotion": policy and complete_items and registry["registry_is_normative"] is False and result["resolution_policy_audit"]["literal_iff_refutation_is_full_resolution"] is False,
        "V7_full_classification_and_impossibility_are_restored_to_open": disposition.get("full_ASMP_3_classification") == "not_established" and disposition.get("ASMP_3_mathematical_impossibility") == "not_proved" and disposition.get("prize_grade_resolution") == "not_established",
        "V8_prior_normative_and_external_gates_remain_open": progress.get("normative_definition") == "unclosed" and expert["qualifying_receipts"] == 0 and expert["minimum_independent_teams"] == 2 and expert["completion_gate_satisfied"] is False,
        "V9_stop_is_limited_to_failed_lane_with_resume_triggers": result["stop_resume"]["current_source_only_impossibility_lane_should_stop"] is True and result["stop_resume"]["all_internal_search_should_stop"] is False and len(result["stop_resume"]["continue_or_resume"]) == 5 and result["certified"] is True and all(result["gates"].values()),
    }
    return {
        "schema_version": "asmp3_normative_closure_reassessment_verification_v2_19",
        "checker": "clean_room_source_order_interface_delta_prior_claim_FIX_counterfamily_resolution_policy_and_open_gate_audit",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": "This checker verifies the correction and evidence statuses; it does not supply formal natural-language semantics, an unrestricted characterization, impossibility, or external acceptance.",
    }


def main() -> None:
    receipt = verify()
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if not receipt["passed"]:
        failed = [name for name, passed in receipt["checks"].items() if not passed]
        raise RuntimeError(f"ASMP-3 v2.19 reassessment verification failed: {failed}")
    print(f"ASMP-3 normative-closure reassessment verification passed: {receipt['check_count']}/{receipt['check_count']}")


if __name__ == "__main__":
    main()
