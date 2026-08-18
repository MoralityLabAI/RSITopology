from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULT_PATH = HERE / "artifacts" / "consolidated_resolution_disposition_v2_12.json"
VERIFY_PATH = HERE / "artifacts" / "consolidated_resolution_disposition_verification_v2_12.json"

SPECS = (
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
)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def audit_manifest(path: Path) -> tuple[bool, int, int]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    members = manifest.get("files", {})
    valid = manifest.get("file_count") == len(members)
    total = 0
    for relative, receipt in members.items():
        member = path.parent / relative
        if not member.is_file():
            valid = False
            continue
        size = member.stat().st_size
        total += size
        valid &= receipt.get("bytes") == size and receipt.get("sha256") == sha(member)
    return bool(valid), len(members), total


def reconstruct_packages() -> list[dict[str, object]]:
    rows = []
    for evidence_id, directory, manifest_name, result_name, verifier_name in SPECS:
        base = ROOT / directory
        manifest_path = base / manifest_name
        result = json.loads((base / result_name).read_text(encoding="utf-8"))
        verifier = json.loads((base / verifier_name).read_text(encoding="utf-8"))
        valid, count, total = audit_manifest(manifest_path)
        row = {
            "evidence_id": evidence_id,
            "directory": directory,
            "manifest": manifest_name,
            "manifest_sha256": sha(manifest_path),
            "manifest_valid": valid,
            "sealed_files": count,
            "sealed_member_bytes": total,
            "result_schema": result.get("schema_version"),
            "result_status": result.get("status"),
            "producer_certified": result.get("certified") is True,
            "verification_schema": verifier.get("schema_version"),
            "independent_check_count": verifier.get("check_count"),
            "independent_verifier_passed": verifier.get("passed") is True,
        }
        row["certified"] = (
            valid
            and row["producer_certified"]
            and row["independent_verifier_passed"]
            and int(row["independent_check_count"] or 0) > 0
        )
        rows.append(row)
    return rows


def load(evidence_id: str) -> dict[str, object]:
    spec = next(item for item in SPECS if item[0] == evidence_id)
    return json.loads((ROOT / spec[1] / spec[3]).read_text(encoding="utf-8"))


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    packages = reconstruct_packages()
    registry_path = ROOT / "problem_set_v0_1.json"
    canonical_path = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
    typed_path = ROOT / "asmp3_typed_successor_v0_2" / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md"
    expert_path = ROOT / "asmp3_resolution_boundary_v0_3" / "artifacts" / "expert_review_status_v0_6.json"
    stop_path = ROOT / "asmp3_online_contract_minimality_v2_11" / "STOPPING_BOUNDARY_v2_11.md"
    expert = json.loads(expert_path.read_text(encoding="utf-8"))
    v07 = load("v0.7_protocol_quantifier")
    v25 = load("v2.5_witness_normal_form")
    v210 = load("v2.10_online_extractor")
    v211 = load("v2.11_contract_minimality")
    statuses = {row["id"]: row["status"] for row in result.get("requirement_rows", [])}
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
        "R3": "partial_fresh_conditional_path_noise_only",
        "R4": "satisfied_component",
        "A0": "satisfied_internal",
        "A1": "satisfied_internal_repository",
        "A2": "missing_external_0_of_2",
        "A3": "satisfied_internal",
        "A4": "satisfied_for_registered_claims",
    }
    source_hashes = {
        "canonical_markdown_sha256": sha(canonical_path),
        "problem_registry_sha256": sha(registry_path),
        "typed_successor_sha256": sha(typed_path),
        "expert_status_sha256": sha(expert_path),
        "v2_11_stopping_boundary_sha256": sha(stop_path),
    }
    disposition = result.get("disposition", {})
    checks = {
        "V0_schema_parent_status": (
            result.get("schema_version")
            == "asmp3_consolidated_resolution_disposition_v2_12"
            and result.get("parent_result")
            == "ASMP-3-ONLINE-CONTRACT-MINIMALITY-v2.11"
            and result.get("status")
            == "literal_refutation_online_subclass_minimality_and_updated_stop_disposition"
        ),
        "V1_all_source_hashes_reconstructed": result.get("source_hashes") == source_hashes,
        "V2_all_twelve_package_manifests_rehashed": (
            len(packages) == 12
            and result.get("evidence_package_rows") == packages
            and all(row["certified"] for row in packages)
        ),
        "V3_all_18_requirement_statuses_match": (
            len(statuses) == 18
            and statuses == expected_statuses
            and all(row.get("evidence_check") is True for row in result["requirement_rows"])
        ),
        "V4_literal_two_sided_refutation_reconstructed": (
            v07["frozen_encoding_branch"]["asymptotic_gap"] == "(3/5)^d -> 0"
            and v25["theorem"]["literal_necessity_separation"].startswith(
                "a nonbinding decidable Refute"
            )
            and statuses["N2"] == "refuted_exact_both_readings"
        ),
        "V5_online_one_shot_and_minimality_progress_reconstructed": (
            v210["theorem"]["restart"] == "neither ideal replay nor strategy restart is required"
            and len(v211["premise_necessity_rows"]) == 6
            and disposition.get("repaired_online_contract_subclass")
            == "constructively_characterized_and_black_box_minimal"
        ),
        "V6_five_remaining_blockers_are_non_grid": (
            len(result.get("remaining_blockers", [])) == 5
            and {row["category"] for row in result["remaining_blockers"]}
            == {
                "definition_authority",
                "new_mathematical_theory",
                "new_noise_theory",
                "external_evidence",
            }
        ),
        "V7_external_gate_reconstructed_as_zero_of_two": (
            expert["qualifying_receipts"] == 0
            and expert["minimum_independent_teams"] == 2
            and expert["completion_gate_satisfied"] is False
            and statuses["A2"] == "missing_external_0_of_2"
        ),
        "V8_all_10_producer_gates_true": (
            len(result.get("gates", {})) == 10
            and all(result.get("gates", {}).values())
            and result.get("certified") is True
        ),
        "V9_claim_boundary_forbids_normative_or_acceptance_overclaim": all(
            phrase in result.get("claim_boundary", "")
            for phrase in (
                "not a normative amendment",
                "exact internal refutation",
                "remaining unrestricted, normative, and external gates",
            )
        ),
    }
    return {
        "schema_version": "asmp3_consolidated_resolution_disposition_verification_v2_12",
        "checker": "clean_room_source_hash_manifest_status_disposition_and_external_gate_audit",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker validates the internal evidence disposition. It does not "
            "supply normative authority, unrestricted classification, or external "
            "expert acceptance."
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
        raise RuntimeError(f"ASMP-3 v2.12 verification failed: {failed}")
    print(
        "ASMP-3 consolidated disposition verification passed: "
        f"{receipt['check_count']}/{receipt['check_count']}"
    )


if __name__ == "__main__":
    main()
