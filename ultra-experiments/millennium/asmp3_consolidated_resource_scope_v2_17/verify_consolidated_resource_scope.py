from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULT_PATH = HERE / "artifacts" / "consolidated_resource_scope_v2_17.json"
VERIFY_PATH = HERE / "artifacts" / "consolidated_resource_scope_verification_v2_17.json"
CANONICAL_PATH = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY_PATH = ROOT / "problem_set_v0_1.json"
EXPERT_PATH = ROOT / "asmp3_resolution_boundary_v0_3" / "artifacts" / "expert_review_status_v0_6.json"
BASE_PATH = ROOT / "asmp3_consolidated_path_risk_disposition_v2_14" / "artifacts" / "consolidated_path_risk_disposition_v2_14.json"
INTERACTIVE_PATH = ROOT / "asmp3_interactive_covering_frontier_v2_15" / "artifacts" / "interactive_covering_frontier_v2_15.json"
BOUNDED_PATH = ROOT / "asmp3_bounded_soundness_frontier_v2_16" / "artifacts" / "bounded_soundness_frontier_v2_16.json"


PACKAGE_SPECS = (
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


def reconstruct_packages() -> list[dict[str, object]]:
    rows = []
    for evidence_id, directory, manifest_name, result_name, verifier_name in PACKAGE_SPECS:
        package = ROOT / directory
        manifest_path = package / manifest_name
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        producer = json.loads((package / result_name).read_text(encoding="utf-8"))
        verifier = json.loads((package / verifier_name).read_text(encoding="utf-8"))
        files = manifest.get("files", {})
        valid = manifest.get("file_count") == len(files)
        total_bytes = 0
        for relative, receipt in files.items():
            member = manifest_path.parent / relative
            if not member.is_file():
                valid = False
                continue
            size = member.stat().st_size
            total_bytes += size
            valid &= receipt.get("bytes") == size
            valid &= receipt.get("sha256") == sha256(member)
        row = {
            "evidence_id": evidence_id,
            "directory": directory,
            "manifest": manifest_name,
            "manifest_sha256": sha256(manifest_path),
            "manifest_valid": bool(valid),
            "sealed_files": len(files),
            "sealed_member_bytes": total_bytes,
            "result_schema": producer.get("schema_version"),
            "result_status": producer.get("status"),
            "producer_certified": producer.get("certified") is True,
            "verification_schema": verifier.get("schema_version"),
            "independent_check_count": verifier.get("check_count"),
            "independent_verifier_passed": verifier.get("passed") is True,
        }
        row["certified"] = bool(row["manifest_valid"] and row["producer_certified"] and row["independent_verifier_passed"] and int(row["independent_check_count"] or 0) > 0)
        rows.append(row)
    return rows


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    expert = json.loads(EXPERT_PATH.read_text(encoding="utf-8"))
    base = json.loads(BASE_PATH.read_text(encoding="utf-8"))
    interactive = json.loads(INTERACTIVE_PATH.read_text(encoding="utf-8"))
    bounded = json.loads(BOUNDED_PATH.read_text(encoding="utf-8"))
    packages = reconstruct_packages()
    source_hashes = {
        "canonical_sha256": sha256(CANONICAL_PATH),
        "registry_sha256": sha256(REGISTRY_PATH),
        "expert_status_sha256": sha256(EXPERT_PATH),
        "v2_14_artifact_sha256": sha256(BASE_PATH),
        "v2_15_artifact_sha256": sha256(INTERACTIVE_PATH),
        "v2_16_artifact_sha256": sha256(BOUNDED_PATH),
    }
    statuses = {row["id"]: row["status"] for row in result["requirement_rows"]}
    expected = {row["id"]: row["status"] for row in base["requirement_rows"]}
    expected["R2"] = "exact_arbitrary_round_public_coin_bounded_soundness_marker_family_cross_task_open"
    totals = result.get("totals", {})
    progress = result.get("resource_progress", {})
    blockers = result.get("remaining_blockers", [])
    disposition = result.get("disposition", {})
    checks = {
        "V0_schema_parent_and_status": result.get("schema_version") == "asmp3_consolidated_resource_scope_v2_17" and result.get("parent_results") == ["ASMP-3-CONSOLIDATED-PATH-RISK-DISPOSITION-v2.14", "ASMP-3-INTERACTIVE-COVERING-FRONTIER-v2.15", "ASMP-3-BOUNDED-SOUNDNESS-FRONTIER-v2.16"] and result.get("status") == "interactive_resource_frontier_strengthened_and_cross_task_definition_boundary",
        "V1_all_source_hashes_reconstructed": result.get("source_hashes") == source_hashes,
        "V2_all_fifteen_manifests_independently_rehashed": len(packages) == 15 and result.get("evidence_package_rows") == packages and all(row["certified"] for row in packages) and totals.get("sealed_manifest_members") == 344,
        "V3_all_eighteen_requirement_statuses_and_evidence_match": statuses == expected and len(result.get("requirement_rows", [])) == 18 and all(row.get("evidence_check") is True for row in result["requirement_rows"]),
        "V4_literal_online_and_path_risk_disposition_preserved": base["certified"] is True and statuses["N2"] == "refuted_exact_both_readings" and statuses["R0"] == "online_subclass_characterized_black_box_minimal_unrestricted_open" and statuses["R3"] == "exact_for_declared_online_subclass_via_selected_path_risk_unrestricted_open",
        "V5_interactive_marker_frontier_reconstructed": interactive["theorem"]["exact_value"] == "min(1,K*q/N)" and len(interactive["frontier_rows"]) == 13413 and interactive["adaptive_tree_audit"]["adaptive_trees_enumerated"] == 97062 and interactive["certified"] is True,
        "V6_bounded_soundness_frontier_reconstructed": bounded["theorem"]["exact_completeness"] == "C*=s+(1-s)*min(1,K*q/N)" and bounded["theorem"]["exact_gap"] == "C*-s=(1-s)*min(1,K*q/N)" and len(bounded["bounded_frontier_rows"]) == 17784 and bounded["finite_seed_exhaustive_audit"]["families_enumerated"] == 25523 and bounded["certified"] is True,
        "V7_resource_progress_is_strong_but_not_overclaimed": len(progress.get("cleared_firewalls", [])) == 5 and progress.get("exact_marker_frontier") == "min(1,K*q/N)" and progress.get("fully_cleared") is False and disposition.get("cross_task_resource_classification") == "not_well_posed_until_formal_class_is_frozen",
        "V8_four_blockers_and_definition_dependent_resource_boundary_match": len(blockers) == 4 and blockers[2].get("id") == "B2_cross_task_resources" and blockers[2].get("category") == "definition_dependent_theorem" and registry["registry_is_normative"] is False and expert["completion_gate_satisfied"] is False,
        "V9_all_gates_and_claim_boundaries_hold": len(result.get("gates", {})) == 10 and all(result.get("gates", {}).values()) and result.get("certified") is True and all(phrase in result.get("claim_boundary", "") for phrase in ("does not invent a cross-task complexity class", "normative problem", "external acceptance")),
    }
    return {
        "schema_version": "asmp3_consolidated_resource_scope_verification_v2_17",
        "checker": "clean_room_manifest_requirement_interactive_bounded_soundness_and_definition_boundary_audit",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": "This checker validates internal resource-scope evidence; it does not define the missing cross-task class or supply external acceptance.",
    }


def main() -> None:
    receipt = verify()
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if not receipt["passed"]:
        failed = [name for name, value in receipt["checks"].items() if not value]
        raise RuntimeError(f"ASMP-3 v2.17 verification failed: {failed}")
    print(f"ASMP-3 consolidated resource scope verification passed: {receipt['check_count']}/{receipt['check_count']}")


if __name__ == "__main__":
    main()
