from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ARTIFACT_DIR = HERE / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "consolidated_resource_scope_v2_17.json"
CANONICAL_PATH = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY_PATH = ROOT / "problem_set_v0_1.json"
EXPERT_PATH = ROOT / "asmp3_resolution_boundary_v0_3" / "artifacts" / "expert_review_status_v0_6.json"
BASE_PATH = ROOT / "asmp3_consolidated_path_risk_disposition_v2_14" / "artifacts" / "consolidated_path_risk_disposition_v2_14.json"
BASE_DOC_PATH = ROOT / "asmp3_consolidated_path_risk_disposition_v2_14" / "RESOLUTION_DISPOSITION_v2_14.md"
INTERACTIVE_PATH = ROOT / "asmp3_interactive_covering_frontier_v2_15" / "artifacts" / "interactive_covering_frontier_v2_15.json"
INTERACTIVE_DOC_PATH = ROOT / "asmp3_interactive_covering_frontier_v2_15" / "INTERACTIVE_COVERING_THEOREM_v2_15.md"
BOUNDED_PATH = ROOT / "asmp3_bounded_soundness_frontier_v2_16" / "artifacts" / "bounded_soundness_frontier_v2_16.json"
BOUNDED_DOC_PATH = ROOT / "asmp3_bounded_soundness_frontier_v2_16" / "BOUNDED_SOUNDNESS_THEOREM_v2_16.md"


EVIDENCE_PACKAGES = (
    ("v0.7_protocol_quantifier", "asmp3_protocol_quantifier_v0_7", "RELEASE_MANIFEST_v0_7.json", "artifacts/protocol_quantifier_v0_7.json", "artifacts/protocol_quantifier_verification_v0_7.json"),
    ("v2.0_encoding_invariance", "asmp3_encoding_invariance_v2_0", "RELEASE_MANIFEST_v2_0.json", "artifacts/encoding_invariance_v2_0.json", "artifacts/encoding_invariance_verification_v2_0.json"),
    ("v2.1_honest_search", "asmp3_honest_search_barrier_v2_1", "RELEASE_MANIFEST_v2_1.json", "artifacts/honest_search_barrier_v2_1.json", "artifacts/honest_search_barrier_verification_v2_1.json"),
    ("v2.2_resource_tradeoff", "asmp3_resource_tradeoff_v2_2", "RELEASE_MANIFEST_v2_2.json", "artifacts/resource_tradeoff_v2_2.json", "artifacts/resource_tradeoff_verification_v2_2.json"),
    ("v2.3_constructive_protocol", "asmp3_constructive_refutation_protocol_v2_3", "RELEASE_MANIFEST_v2_3.json", "artifacts/constructive_refutation_protocol_v2_3.json", "artifacts/constructive_refutation_protocol_verification_v2_3.json"),
    ("v2.4_randomized_finder", "asmp3_randomized_finder_amplification_v2_4", "RELEASE_MANIFEST_v2_4.json", "artifacts/randomized_finder_amplification_v2_4.json", "artifacts/randomized_finder_amplification_verification_v2_4.json"),
    ("v2.5_witness_normal_form", "asmp3_witness_transparent_normal_form_v2_5", "RELEASE_MANIFEST_v2_5.json", "artifacts/witness_transparent_normal_form_v2_5.json", "artifacts/witness_transparent_normal_form_verification_v2_5.json"),
    ("v2.7_adaptive_coupling", "asmp3_adaptive_transcript_coupling_v2_7", "RELEASE_MANIFEST_v2_7.json", "artifacts/adaptive_transcript_coupling_v2_7.json", "artifacts/adaptive_transcript_coupling_verification_v2_7.json"),
    ("v2.8_trace_binding", "asmp3_trace_binding_extractor_v2_8", "RELEASE_MANIFEST_v2_8.json", "artifacts/trace_binding_extractor_v2_8.json", "artifacts/trace_binding_extractor_verification_v2_8.json"),
    ("v2.9_oracle_replay", "asmp3_oracle_parametric_replay_v2_9", "RELEASE_MANIFEST_v2_9.json", "artifacts/oracle_parametric_replay_v2_9.json", "artifacts/oracle_parametric_replay_verification_v2_9.json"),
    ("v2.10_online_extractor", "asmp3_online_noisy_trace_extractor_v2_10", "RELEASE_MANIFEST_v2_10.json", "artifacts/online_noisy_trace_extractor_v2_10.json", "artifacts/online_noisy_trace_extractor_verification_v2_10.json"),
    ("v2.11_contract_minimality", "asmp3_online_contract_minimality_v2_11", "RELEASE_MANIFEST_v2_11.json", "artifacts/online_contract_minimality_v2_11.json", "artifacts/online_contract_minimality_verification_v2_11.json"),
    ("v2.13_correlated_path_risk", "asmp3_correlated_path_risk_v2_13", "RELEASE_MANIFEST_v2_13.json", "artifacts/correlated_path_risk_v2_13.json", "artifacts/correlated_path_risk_verification_v2_13.json"),
    ("v2.15_interactive_covering", "asmp3_interactive_covering_frontier_v2_15", "RELEASE_MANIFEST_v2_15.json", "artifacts/interactive_covering_frontier_v2_15.json", "artifacts/interactive_covering_frontier_verification_v2_15.json"),
    ("v2.16_bounded_soundness", "asmp3_bounded_soundness_frontier_v2_16", "RELEASE_MANIFEST_v2_16.json", "artifacts/bounded_soundness_frontier_v2_16.json", "artifacts/bounded_soundness_frontier_verification_v2_16.json"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def verify_manifest(path: Path) -> tuple[bool, int, int]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    files = manifest.get("files", {})
    valid = manifest.get("file_count") == len(files)
    total_bytes = 0
    for relative, receipt in files.items():
        member = path.parent / relative
        if not member.is_file():
            valid = False
            continue
        size = member.stat().st_size
        total_bytes += size
        valid &= receipt.get("bytes") == size
        valid &= receipt.get("sha256") == sha256(member)
    return bool(valid), len(files), total_bytes


def package_rows() -> list[dict[str, object]]:
    rows = []
    for evidence_id, directory, manifest_name, result_name, verifier_name in EVIDENCE_PACKAGES:
        package = ROOT / directory
        manifest_path = package / manifest_name
        result = json.loads((package / result_name).read_text(encoding="utf-8"))
        verifier = json.loads((package / verifier_name).read_text(encoding="utf-8"))
        manifest_valid, sealed_files, sealed_bytes = verify_manifest(manifest_path)
        row = {
            "evidence_id": evidence_id,
            "directory": directory,
            "manifest": manifest_name,
            "manifest_sha256": sha256(manifest_path),
            "manifest_valid": manifest_valid,
            "sealed_files": sealed_files,
            "sealed_member_bytes": sealed_bytes,
            "result_schema": result.get("schema_version"),
            "result_status": result.get("status"),
            "producer_certified": result.get("certified") is True,
            "verification_schema": verifier.get("schema_version"),
            "independent_check_count": verifier.get("check_count"),
            "independent_verifier_passed": verifier.get("passed") is True,
        }
        row["certified"] = bool(manifest_valid and row["producer_certified"] and row["independent_verifier_passed"] and int(row["independent_check_count"] or 0) > 0)
        rows.append(row)
    return rows


def updated_requirements(base: dict[str, object], packages: list[dict[str, object]], interactive: dict[str, object], bounded: dict[str, object]) -> list[dict[str, object]]:
    rows = copy.deepcopy(base["requirement_rows"])
    by_id = {row["id"]: row for row in rows}
    by_id["R2"].update(
        {
            "status": "exact_arbitrary_round_public_coin_bounded_soundness_marker_family_cross_task_open",
            "evidence": "v2.1 exact honest Find; v2.15 exact min(1,Kq/N) interactive Check frontier; v2.16 exact s+(1-s)min(1,Kq/N) bounded-soundness frontier",
            "evidence_check": interactive["theorem"]["exact_value"] == "min(1,K*q/N)" and bounded["theorem"]["exact_completeness"] == "C*=s+(1-s)*min(1,K*q/N)" and bounded["theorem"]["exact_gap"] == "C*-s=(1-s)*min(1,K*q/N)",
        }
    )
    by_id["A0"].update({"evidence": "fifteen decisive evidence packages with valid release manifests", "evidence_check": len(packages) == 15 and all(row["manifest_valid"] for row in packages)})
    by_id["A1"].update({"evidence": "all fifteen decisive packages have passing clean-room verifiers", "evidence_check": len(packages) == 15 and all(row["independent_verifier_passed"] for row in packages)})
    by_id["A4"].update({"evidence": "(3/5)^d, q/N, k/N, path-risk law, interactive min(1,Kq/N), and bounded-soundness exact gap", "evidence_check": interactive["certified"] is True and bounded["certified"] is True and by_id["A4"]["evidence_check"] is True})
    return rows


def build_artifact() -> dict[str, object]:
    canonical = CANONICAL_PATH.read_text(encoding="utf-8")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    expert = json.loads(EXPERT_PATH.read_text(encoding="utf-8"))
    base = json.loads(BASE_PATH.read_text(encoding="utf-8"))
    base_doc = BASE_DOC_PATH.read_text(encoding="utf-8")
    interactive_doc = INTERACTIVE_DOC_PATH.read_text(encoding="utf-8")
    bounded_doc = BOUNDED_DOC_PATH.read_text(encoding="utf-8")
    interactive_doc_flat = " ".join(interactive_doc.split())
    interactive = json.loads(INTERACTIVE_PATH.read_text(encoding="utf-8"))
    bounded = json.loads(BOUNDED_PATH.read_text(encoding="utf-8"))
    packages = package_rows()
    requirements = updated_requirements(base, packages, interactive, bounded)
    statuses = {row["id"]: row["status"] for row in requirements}
    source_checks = {
        "canonical_requires_formal_complexity_class": "A formal complexity class for the protocols above" in canonical,
        "canonical_requires_matching_resource_lower_bounds": "Matching communication, semantic-query, and honest-prover lower bounds." in canonical,
        "canonical_freezes_public_coin_message_order": "a public-coin message" in canonical,
        "registry_is_not_normative": registry["registry_is_normative"] is False,
        "base_has_four_blockers": "Exactly four blockers remain" in base_doc,
        "v2_15_removes_round_and_adaptivity_firewalls": "arbitrary-round public-coin interaction" in interactive_doc_flat,
        "v2_16_removes_positive_soundness_firewall": "maximum worst-marker completeness" in bounded_doc,
    }
    resource_progress = {
        "id": "P2_interactive_resource_scope",
        "former_status": "partial_registered_families_and_black_box_model",
        "new_status": statuses["R2"],
        "cleared_firewalls": [
            "one_message_only",
            "nonadaptive_queries_only",
            "perfect_completeness_only",
            "perfect_soundness_only",
            "fixed_round_schedule_only",
        ],
        "exact_marker_frontier": interactive["theorem"]["exact_value"],
        "exact_bounded_soundness_frontier": bounded["theorem"]["exact_completeness"],
        "exact_bounded_soundness_gap": bounded["theorem"]["exact_gap"],
        "remaining_scope": "cross-task class theorem after a formal protocol/task class is frozen",
        "fully_cleared": False,
        "certified": interactive["certified"] is True and bounded["certified"] is True,
    }
    blockers = [
        {"id": "B0_normative_interface", "category": "definition_authority", "blocker": "v0.1 does not authoritatively choose FIX versus ADM or the six-clause online contract", "why_current_harness_cannot_clear_it": "exact calculations cannot choose normative scope", "clearing_event": "authoritative successor definition or scope adjudication"},
        {"id": "B1_non_black_box_scope", "category": "new_mathematical_theory", "blocker": "black-box online minimality does not classify every task-specific non-black-box protocol", "why_current_harness_cannot_clear_it": "larger observation grids cannot prove a theorem using absent task structure", "clearing_event": "concrete non-black-box family or universal structure theorem"},
        {"id": "B2_cross_task_resources", "category": "definition_dependent_theorem", "blocker": "marker-family Find/message/Check frontiers are exact through arbitrary public-coin rounds and bounded soundness, but no frozen cross-task protocol class exists for a universal matching lower bound", "why_current_harness_cannot_clear_it": "a universal quantifier over an unspecified task/protocol class has no determinate truth condition", "clearing_event": "freeze a formal cross-task class and its reduction-preserving resource measures"},
        {"id": "B3_external_review", "category": "external_evidence", "blocker": "expert gate remains 0/2 with 0/1 independent team checkers", "why_current_harness_cannot_clear_it": "repository-generated receipts cannot establish external identity or independence", "clearing_event": "two attributable expert reproductions including one independently implemented checker"},
    ]
    totals = {
        "decisive_evidence_packages": len(packages),
        "sealed_manifest_members": sum(int(row["sealed_files"]) for row in packages),
        "sealed_member_bytes": sum(int(row["sealed_member_bytes"]) for row in packages),
        "requirement_rows": len(requirements),
        "direct_requirement_evidence_checks": sum(bool(row["evidence_check"]) for row in requirements),
        "resource_progress_events": 1,
        "remaining_blockers": len(blockers),
        "external_expert_teams": expert["qualifying_receipts"],
    }
    gates = {
        "C0_all_authoritative_source_clauses_present": all(source_checks.values()),
        "C1_all_fifteen_decisive_packages_sealed_and_verified": len(packages) == 15 and all(row["certified"] for row in packages),
        "C2_v2_14_literal_noise_and_online_disposition_is_preserved": base["certified"] is True and statuses["N2"] == "refuted_exact_both_readings" and statuses["R3"] == "exact_for_declared_online_subclass_via_selected_path_risk_unrestricted_open",
        "C3_v2_15_arbitrary_round_interactive_frontier_is_recorded": interactive["theorem"]["exact_value"] == "min(1,K*q/N)" and interactive["certified"] is True,
        "C4_v2_16_bounded_soundness_frontier_and_gap_are_recorded": bounded["theorem"]["exact_completeness"] == "C*=s+(1-s)*min(1,K*q/N)" and bounded["theorem"]["exact_gap"] == "C*-s=(1-s)*min(1,K*q/N)" and bounded["certified"] is True,
        "C5_R2_is_strengthened_without_cross_task_overclaim": statuses["R2"] == "exact_arbitrary_round_public_coin_bounded_soundness_marker_family_cross_task_open" and resource_progress["fully_cleared"] is False,
        "C6_all_eighteen_requirement_rows_have_direct_evidence": len(requirements) == 18 and all(row["evidence_check"] for row in requirements),
        "C7_remaining_resource_target_is_definition_dependent_not_a_grid_gap": blockers[2]["category"] == "definition_dependent_theorem" and "unspecified task/protocol class" in blockers[2]["why_current_harness_cannot_clear_it"],
        "C8_exactly_four_non_grid_blockers_and_external_gate_remain": len(blockers) == 4 and expert["completion_gate_satisfied"] is False and statuses["A2"] == "missing_external_0_of_2",
        "C9_disposition_separates_literal_subclass_marker_resource_cross_task_and_external_layers": statuses["N2"].startswith("refuted") and statuses["R0"].endswith("unrestricted_open") and statuses["R2"].endswith("cross_task_open") and statuses["A2"].startswith("missing_external"),
    }
    return {
        "schema_version": "asmp3_consolidated_resource_scope_v2_17",
        "experiment_id": "ASMP-3-CONSOLIDATED-RESOURCE-SCOPE-v2.17",
        "parent_results": [
            "ASMP-3-CONSOLIDATED-PATH-RISK-DISPOSITION-v2.14",
            "ASMP-3-INTERACTIVE-COVERING-FRONTIER-v2.15",
            "ASMP-3-BOUNDED-SOUNDNESS-FRONTIER-v2.16",
        ],
        "status": "interactive_resource_frontier_strengthened_and_cross_task_definition_boundary",
        "source_hashes": {
            "canonical_sha256": sha256(CANONICAL_PATH),
            "registry_sha256": sha256(REGISTRY_PATH),
            "expert_status_sha256": sha256(EXPERT_PATH),
            "v2_14_artifact_sha256": sha256(BASE_PATH),
            "v2_15_artifact_sha256": sha256(INTERACTIVE_PATH),
            "v2_16_artifact_sha256": sha256(BOUNDED_PATH),
        },
        "source_checks": source_checks,
        "evidence_package_rows": packages,
        "requirement_rows": requirements,
        "resource_progress": resource_progress,
        "remaining_blockers": blockers,
        "totals": totals,
        "disposition": {
            "literal_v0_1_named_conjecture": "refuted_internal_exact_both_directions",
            "repaired_online_contract_subclass": "constructively_characterized_black_box_minimal_and_dependence_agnostic_via_selected_path_risk",
            "marker_family_resource_theorem": "exact_for_arbitrary_round_public_coin_adaptive_queries_and_bounded_soundness",
            "cross_task_resource_classification": "not_well_posed_until_formal_class_is_frozen",
            "unrestricted_asmp3_classification": "not_established",
            "normative_definition": "unclosed",
            "community_or_prize_style_acceptance": "not_established_external_gate_0_of_2",
            "safe_public_label": "ASMP-3 v0.1 iff refuted internally; repaired online subclass characterized; marker-family interactive resource frontier exact through bounded soundness; cross-task classification, normative closure, and external acceptance not established",
        },
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "This internal disposition strengthens the registered marker-family resource theorem. "
            "It does not invent a cross-task complexity class, amend the normative problem, classify "
            "unrestricted ASMP-3 protocols, or establish external acceptance."
        ),
    }


def write_artifact() -> dict[str, object]:
    artifact = build_artifact()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return artifact


if __name__ == "__main__":
    result = write_artifact()
    passed = sum(bool(value) for value in result["gates"].values())
    print(f"ASMP-3 consolidated resource scope certified: {passed}/{len(result['gates'])}")
