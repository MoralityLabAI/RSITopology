from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULT_PATH = HERE / "artifacts" / "resolution_disposition_v2_6.json"
OUTPUT_PATH = HERE / "artifacts" / "resolution_disposition_verification_v2_6.json"
CANONICAL_PATH = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY_PATH = ROOT / "problem_set_v0_1.json"
TYPED_PATH = ROOT / "asmp3_typed_successor_v0_2" / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md"
EXPERT_PATH = ROOT / "asmp3_resolution_boundary_v0_3" / "artifacts" / "expert_review_status_v0_6.json"

PACKAGE_SPECS = (
    ("v0.7_protocol_quantifier", "asmp3_protocol_quantifier_v0_7", "RELEASE_MANIFEST_v0_7.json", "artifacts/protocol_quantifier_v0_7.json", "artifacts/protocol_quantifier_verification_v0_7.json"),
    ("v1.9_block_selection", "asmp3_block_selection_composition_v1_9", "RELEASE_MANIFEST_v1_9.json", "artifacts/block_selection_composition_v1_9.json", "artifacts/block_selection_composition_verification_v1_9.json"),
    ("v2.0_encoding_invariance", "asmp3_encoding_invariance_v2_0", "RELEASE_MANIFEST_v2_0.json", "artifacts/encoding_invariance_v2_0.json", "artifacts/encoding_invariance_verification_v2_0.json"),
    ("v2.1_honest_search", "asmp3_honest_search_barrier_v2_1", "RELEASE_MANIFEST_v2_1.json", "artifacts/honest_search_barrier_v2_1.json", "artifacts/honest_search_barrier_verification_v2_1.json"),
    ("v2.2_resource_tradeoff", "asmp3_resource_tradeoff_v2_2", "RELEASE_MANIFEST_v2_2.json", "artifacts/resource_tradeoff_v2_2.json", "artifacts/resource_tradeoff_verification_v2_2.json"),
    ("v2.3_constructive_protocol", "asmp3_constructive_refutation_protocol_v2_3", "RELEASE_MANIFEST_v2_3.json", "artifacts/constructive_refutation_protocol_v2_3.json", "artifacts/constructive_refutation_protocol_verification_v2_3.json"),
    ("v2.4_randomized_finder", "asmp3_randomized_finder_amplification_v2_4", "RELEASE_MANIFEST_v2_4.json", "artifacts/randomized_finder_amplification_v2_4.json", "artifacts/randomized_finder_amplification_verification_v2_4.json"),
    ("v2.5_witness_normal_form", "asmp3_witness_transparent_normal_form_v2_5", "RELEASE_MANIFEST_v2_5.json", "artifacts/witness_transparent_normal_form_v2_5.json", "artifacts/witness_transparent_normal_form_verification_v2_5.json"),
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1_048_576), b""):
            value.update(block)
    return value.hexdigest().upper()


def reconstruct_packages() -> list[dict[str, object]]:
    rows = []
    for evidence_id, directory, manifest_name, result_name, verification_name in PACKAGE_SPECS:
        package = ROOT / directory
        manifest_path = package / manifest_name
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        valid = manifest.get("file_count") == len(manifest.get("files", {}))
        bytes_total = 0
        for relative, receipt in manifest.get("files", {}).items():
            member = package / relative
            if not member.is_file():
                valid = False
                continue
            size = member.stat().st_size
            bytes_total += size
            valid &= receipt.get("bytes") == size and receipt.get("sha256") == digest(member)
        result = json.loads((package / result_name).read_text(encoding="utf-8"))
        verification = json.loads((package / verification_name).read_text(encoding="utf-8"))
        rows.append(
            {
                "evidence_id": evidence_id,
                "directory": directory,
                "manifest": manifest_name,
                "manifest_sha256": digest(manifest_path),
                "manifest_valid": bool(valid),
                "sealed_files": len(manifest.get("files", {})),
                "sealed_member_bytes": bytes_total,
                "experiment_id": result.get("experiment_id"),
                "result_status": result.get("status"),
                "producer_certified": result.get("certified") is True,
                "verification_schema": verification.get("schema_version"),
                "independent_verifier_passed": verification.get("passed") is True,
                "independent_check_count": verification.get("check_count"),
                "certified": (
                    valid
                    and result.get("certified") is True
                    and verification.get("passed") is True
                    and verification.get("check_count", 0) > 0
                ),
            }
        )
    return rows


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    canonical = CANONICAL_PATH.read_text(encoding="utf-8")
    typed = TYPED_PATH.read_text(encoding="utf-8")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    expert = json.loads(EXPERT_PATH.read_text(encoding="utf-8"))
    packages = reconstruct_packages()
    requirements = {row["id"]: row for row in result.get("requirement_rows", [])}
    expected_clauses = {
        "canonical_is_research_agenda_artifact": "research-agenda artifact" in canonical,
        "canonical_not_every_formulation_known_open": "not an assertion that every formulation" in canonical,
        "canonical_closed_formal_core_required": "**Closed formal core.**" in canonical,
        "canonical_warns_criterion_refutation_not_broader_resolution": "Refuting one proposed criterion does not resolve a" in canonical,
        "canonical_names_five_asmp3_resolution_items": "Matching communication, semantic-query, and honest-prover lower bounds." in canonical,
        "canonical_requires_two_expert_teams": "At least two independent expert teams" in canonical,
        "canonical_final_boundary_says_definition_review": "ready for external definition review" in canonical,
        "typed_successor_is_nonnormative": "document_status = nonnormative_successor_draft" in typed and "changes_parent_problem = false" in typed,
        "typed_successor_does_not_adjudicate_intent": "does not decide v0.1 authorial intent" in typed,
    }
    checks = {
        "V0_schema_problem_status_boundary": (
            result.get("schema_version") == "asmp3_resolution_disposition_v2_6"
            and result.get("status") == "evidence_backed_negative_conjecture_disposition_and_stop_boundary"
            and result.get("problem_id") == "ASMP-3"
            and result.get("problem_version") == "ASMP-CANDIDATE-SET-v0.1"
            and result.get("certified") is True
            and "does not label" in result.get("claim_boundary", "")
        ),
        "V1_authoritative_source_hashes_and_clauses_reconstructed": (
            result.get("canonical_source_sha256") == digest(CANONICAL_PATH)
            and result.get("registry_source_sha256") == digest(REGISTRY_PATH)
            and result.get("typed_successor_sha256") == digest(TYPED_PATH)
            and result.get("source_clause_checks") == expected_clauses
            and all(expected_clauses.values())
        ),
        "V2_all_eight_package_manifests_and_verifiers_reconstructed": (
            result.get("evidence_packages") == packages
            and len(packages) == 8
            and all(row["certified"] for row in packages)
        ),
        "V3_named_conjecture_and_registry_route_dispositions_consistent": (
            requirements["N0"]["status"] == "refuted_exact"
            and requirements["N1"]["status"] == "refuted_exact"
            and requirements["N2"]["status"] == "refuted_exact_both_readings"
            and requirements["G0"]["status"] == "satisfied_internal"
            and requirements["G1"]["status"] == "satisfied_internal"
        ),
        "V4_full_classification_gaps_not_overclaimed": (
            requirements["D1"]["status"] == "not_satisfied_authoritative"
            and requirements["D3"]["status"] == "definitionally_unclosed"
            and requirements["R0"]["status"] == "partial_subclass_only"
            and requirements["R2"]["status"] == "partial_family_only"
            and requirements["R3"]["status"] == "partial_noise_class_only"
        ),
        "V5_external_gate_reconstructed_as_zero_of_two": (
            result["expert_review_status"]
            == {
                "qualifying_teams": expert["qualifying_receipts"],
                "required_teams": expert["minimum_independent_teams"],
                "qualifying_independent_team_checkers": expert["qualifying_independently_implemented_checkers"],
                "required_independent_team_checkers": expert["minimum_independently_implemented_checkers"],
                "completion_gate_satisfied": expert["completion_gate_satisfied"],
            }
            and expert["qualifying_receipts"] == 0
            and expert["completion_gate_satisfied"] is False
        ),
        "V6_all_requirement_evidence_checks_true": (
            len(requirements) == 19 and all(row["evidence_check"] for row in requirements.values())
        ),
        "V7_disposition_distinguishes_four_truth_states": (
            result["disposition"]["named_weak_verifier_characterization_conjecture"].startswith("refuted")
            and result["disposition"]["nonnormative_registry_negative_route_mathematics"] == "satisfied_internal"
            and result["disposition"]["full_asmp3_v0_1_classification_program"].startswith("not_resolved")
            and result["disposition"]["community_or_prize_style_acceptance"].startswith("not_established")
        ),
        "V8_stopping_boundary_has_only_nonenumerative_clearance_events": (
            len(result.get("remaining_blockers", [])) == 4
            and result["disposition"]["current_harness_architecture"] == "stop_further_grid_extension"
            and all("cannot" in row["why_more_current_harness_rows_cannot_clear_it"] for row in result["remaining_blockers"])
        ),
        "V9_all_10_producer_gates_true": (
            len(result.get("gates", {})) == 10 and all(result["gates"].values())
            and registry["status"] == "proposed_candidate_definition_draft"
        ),
    }
    return {
        "schema_version": "asmp3_resolution_disposition_verification_v2_6",
        "checker": "clean_room_source_manifest_requirement_disposition_and_stop_boundary_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This verifier establishes that the disposition follows from the sealed "
            "repository evidence and authoritative status clauses. It cannot supply "
            "the missing normative decision, universal theorem, or external experts."
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
        raise SystemExit(f"resolution-disposition verification failed: {failed}")
    print(
        "ASMP-3 resolution-disposition verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
