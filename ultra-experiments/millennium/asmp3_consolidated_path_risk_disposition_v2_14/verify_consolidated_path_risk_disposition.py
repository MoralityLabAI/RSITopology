from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULT_PATH = HERE / "artifacts" / "consolidated_path_risk_disposition_v2_14.json"
VERIFY_PATH = HERE / "artifacts" / "consolidated_path_risk_disposition_verification_v2_14.json"
CANONICAL_PATH = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY_PATH = ROOT / "problem_set_v0_1.json"
TYPED_PATH = ROOT / "asmp3_typed_successor_v0_2" / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md"
EXPERT_PATH = ROOT / "asmp3_resolution_boundary_v0_3" / "artifacts" / "expert_review_status_v0_6.json"
V2_12_PATH = ROOT / "asmp3_consolidated_resolution_disposition_v2_12" / "RESOLUTION_DISPOSITION_v2_12.md"
V2_13_PATH = ROOT / "asmp3_correlated_path_risk_v2_13" / "CORRELATED_PATH_RISK_THEOREM_v2_13.md"
V2_13_RESULT_PATH = ROOT / "asmp3_correlated_path_risk_v2_13" / "artifacts" / "correlated_path_risk_v2_13.json"


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
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def reconstruct_package_rows() -> list[dict[str, object]]:
    rows = []
    for evidence_id, directory, manifest_name, result_name, verifier_name in PACKAGE_SPECS:
        package = ROOT / directory
        manifest_path = package / manifest_name
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        result = json.loads((package / result_name).read_text(encoding="utf-8"))
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
            "result_schema": result.get("schema_version"),
            "result_status": result.get("status"),
            "producer_certified": result.get("certified") is True,
            "verification_schema": verifier.get("schema_version"),
            "independent_check_count": verifier.get("check_count"),
            "independent_verifier_passed": verifier.get("passed") is True,
        }
        row["certified"] = bool(
            row["manifest_valid"]
            and row["producer_certified"]
            and row["independent_verifier_passed"]
            and int(row["independent_check_count"] or 0) > 0
        )
        rows.append(row)
    return rows


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    expert = json.loads(EXPERT_PATH.read_text(encoding="utf-8"))
    v213 = json.loads(V2_13_RESULT_PATH.read_text(encoding="utf-8"))
    packages = reconstruct_package_rows()
    source_hashes = {
        "canonical_sha256": sha256(CANONICAL_PATH),
        "registry_sha256": sha256(REGISTRY_PATH),
        "typed_successor_sha256": sha256(TYPED_PATH),
        "expert_status_sha256": sha256(EXPERT_PATH),
        "v2_12_disposition_sha256": sha256(V2_12_PATH),
        "v2_13_theorem_sha256": sha256(V2_13_PATH),
    }
    statuses = {row["id"]: row["status"] for row in result["requirement_rows"]}
    expected_statuses = {
        "D0": "satisfied_internal",
        "D1": "not_satisfied_authoritative",
        "D2": "definitionally_unclosed",
        "N0": "refuted_exact",
        "N1": "refuted_exact",
        "N2": "refuted_exact_both_readings",
        "G0": "satisfied_internal",
        "G1": "satisfied_internal",
        "R0": "online_subclass_characterized_black_box_minimal_unrestricted_open",
        "R1": "satisfied_for_declared_online_subclass_only",
        "R2": "partial_registered_families_and_black_box_model",
        "R3": "exact_for_declared_online_subclass_via_selected_path_risk_unrestricted_open",
        "R4": "satisfied_component",
        "A0": "satisfied_internal",
        "A1": "satisfied_internal_repository",
        "A2": "missing_external_0_of_2",
        "A3": "satisfied_internal",
        "A4": "satisfied_for_registered_claims",
    }
    totals = result.get("totals", {})
    disposition = result.get("disposition", {})
    checks = {
        "V0_schema_parent_and_status": (
            result.get("schema_version") == "asmp3_consolidated_path_risk_disposition_v2_14"
            and result.get("parent_results") == [
                "ASMP-3-CONSOLIDATED-RESOLUTION-DISPOSITION-v2.12",
                "ASMP-3-CORRELATED-PATH-RISK-v2.13",
            ]
            and result.get("status") == "literal_refutation_online_path_risk_characterization_and_four_blocker_stop_disposition"
        ),
        "V1_all_source_hashes_reconstructed": result.get("source_hashes") == source_hashes,
        "V2_all_thirteen_package_manifests_independently_rehashed": (
            len(packages) == 13
            and result.get("evidence_package_rows") == packages
            and all(row["certified"] for row in packages)
            and totals.get("sealed_manifest_members") == 298
        ),
        "V3_all_eighteen_requirement_statuses_and_checks_match": (
            statuses == expected_statuses
            and len(result.get("requirement_rows", [])) == 18
            and all(row.get("evidence_check") is True for row in result["requirement_rows"])
        ),
        "V4_literal_two_sided_refutation_preserved": (
            statuses["N2"] == "refuted_exact_both_readings"
            and disposition.get("literal_v0_1_named_conjecture") == "refuted_internal_exact_both_directions"
        ),
        "V5_online_characterization_and_minimality_preserved": (
            statuses["R0"] == "online_subclass_characterized_black_box_minimal_unrestricted_open"
            and "black_box_minimal" in disposition.get("repaired_online_contract_subclass", "")
        ),
        "V6_correlated_path_risk_theorem_and_firewall_reconstructed": (
            v213["theorem"]["general_path_law"] == "alpha>=max(0,1-s-delta_path) for any dependence structure"
            and len(v213["common_mode_rows"]) == 24
            and len(v213["conditional_chain_rows"]) == 20
            and v213["exchangeable_mixture_audit"]["mixture_query_cases"] == 18012
            and v213["exchangeable_mixture_audit"]["jensen_bound_violations"] == 0
            and len(v213["selection_correlated_rows"]) == 31
            and statuses["R3"] == "exact_for_declared_online_subclass_via_selected_path_risk_unrestricted_open"
        ),
        "V7_noise_trigger_cleared_and_exactly_four_blockers_remain": (
            len(result.get("resolved_resume_triggers", [])) == 1
            and result["resolved_resume_triggers"][0].get("cleared") is True
            and len(result.get("remaining_blockers", [])) == 4
            and {row["category"] for row in result["remaining_blockers"]} == {"definition_authority", "new_mathematical_theory", "external_evidence"}
            and totals.get("remaining_blockers") == 4
        ),
        "V8_external_gate_reconstructed_as_zero_of_two": (
            registry["graduation_standard_satisfied"] is False
            and expert["qualifying_receipts"] == 0
            and expert["minimum_independent_teams"] == 2
            and expert["completion_gate_satisfied"] is False
            and statuses["A2"] == "missing_external_0_of_2"
        ),
        "V9_all_producer_gates_and_claim_boundaries_hold": (
            len(result.get("gates", {})) == 10
            and all(result.get("gates", {}).values())
            and result.get("certified") is True
            and all(
                phrase in result.get("claim_boundary", "")
                for phrase in (
                    "not a normative amendment",
                    "unrestricted ASMP-3 classification",
                    "six-clause online subclass",
                )
            )
        ),
    }
    return {
        "schema_version": "asmp3_consolidated_path_risk_disposition_verification_v2_14",
        "checker": "clean_room_source_manifest_requirement_path_risk_trigger_and_stop_audit",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker validates the internal evidence disposition. It does not "
            "supply normative authority, unrestricted classification, or external acceptance."
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
        raise RuntimeError(f"ASMP-3 v2.14 verification failed: {failed}")
    print(
        "ASMP-3 v2.14 consolidated disposition verification passed: "
        f"{receipt['check_count']}/{receipt['check_count']}"
    )


if __name__ == "__main__":
    main()
