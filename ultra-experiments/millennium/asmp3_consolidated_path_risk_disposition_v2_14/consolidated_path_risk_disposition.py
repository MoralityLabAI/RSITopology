from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ARTIFACT_DIR = HERE / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "consolidated_path_risk_disposition_v2_14.json"
CANONICAL_PATH = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY_PATH = ROOT / "problem_set_v0_1.json"
TYPED_PATH = ROOT / "asmp3_typed_successor_v0_2" / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md"
EXPERT_PATH = (
    ROOT
    / "asmp3_resolution_boundary_v0_3"
    / "artifacts"
    / "expert_review_status_v0_6.json"
)
V2_12_PATH = (
    ROOT
    / "asmp3_consolidated_resolution_disposition_v2_12"
    / "RESOLUTION_DISPOSITION_v2_12.md"
)
V2_13_PATH = (
    ROOT
    / "asmp3_correlated_path_risk_v2_13"
    / "CORRELATED_PATH_RISK_THEOREM_v2_13.md"
)


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
    rows: list[dict[str, object]] = []
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
        row["certified"] = bool(
            manifest_valid
            and row["producer_certified"]
            and row["independent_verifier_passed"]
            and int(row["independent_check_count"] or 0) > 0
        )
        rows.append(row)
    return rows


def load_result(evidence_id: str) -> dict[str, object]:
    spec = next(spec for spec in EVIDENCE_PACKAGES if spec[0] == evidence_id)
    return json.loads((ROOT / spec[1] / spec[3]).read_text(encoding="utf-8"))


def requirement_rows(
    registry: dict[str, object],
    expert: dict[str, object],
    packages: list[dict[str, object]],
    evidence: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    problem = next(item for item in registry["problems"] if item["id"] == "ASMP-3")
    v07 = evidence["v0.7_protocol_quantifier"]
    v20 = evidence["v2.0_encoding_invariance"]
    v21 = evidence["v2.1_honest_search"]
    v22 = evidence["v2.2_resource_tradeoff"]
    v23 = evidence["v2.3_constructive_protocol"]
    v25 = evidence["v2.5_witness_normal_form"]
    v27 = evidence["v2.7_adaptive_coupling"]
    v210 = evidence["v2.10_online_extractor"]
    v211 = evidence["v2.11_contract_minimality"]
    v213 = evidence["v2.13_correlated_path_risk"]
    return [
        {"id": "D0", "layer": "definition", "requirement": "exact problem ID, version, and foundational base", "status": "satisfied_internal", "evidence": "ASMP-3 / ASMP-CANDIDATE-SET-v0.1 / declared ZFC base", "evidence_check": expert["problem_id"] == "ASMP-3" and expert["problem_version"] == "ASMP-CANDIDATE-SET-v0.1" and registry["foundational_base"].startswith("ZFC")},
        {"id": "D1", "layer": "definition", "requirement": "authoritatively closed formal core", "status": "not_satisfied_authoritative", "evidence": "v0.1 remains a research-agenda artifact; graduation is false", "evidence_check": registry["graduation_standard_satisfied"] is False},
        {"id": "D2", "layer": "definition", "requirement": "normative FIX/ADM and Refute-binding choice", "status": "definitionally_unclosed", "evidence": "typed successor remains nonnormative", "evidence_check": registry["registry_is_normative"] is False},
        {"id": "N0", "layer": "named_conjecture", "requirement": "frozen-interface sufficiency direction", "status": "refuted_exact", "evidence": "v0.7 optimal gap (3/5)^d tends to zero although the three displayed conditions hold", "evidence_check": v07["status"] == "exact_quantifier_fork" and v07["frozen_encoding_branch"]["asymptotic_gap"] == "(3/5)^d -> 0"},
        {"id": "N1", "layer": "named_conjecture", "requirement": "literal nonbinding-Refute necessity direction", "status": "refuted_exact", "evidence": v25["theorem"]["literal_necessity_separation"], "evidence_check": v25["theorem"]["literal_necessity_separation"].startswith("a nonbinding decidable Refute") and v25["certified"] is True},
        {"id": "N2", "layer": "named_conjecture", "requirement": "two-sided disposition under both principal literal readings", "status": "refuted_exact_both_readings", "evidence": "v0.7 refutes sufficiency; v2.5 refutes necessity", "evidence_check": v25["theorem"]["literal_sufficiency_separation"].startswith("v0.7 frozen parity") and v25["theorem"]["literal_necessity_separation"].startswith("a nonbinding decidable Refute")},
        {"id": "G0", "layer": "registry_negative_route", "requirement": problem["negative_resolution_requires"][0], "status": "satisfied_internal", "evidence": "v0.7 exact frozen-message separation", "evidence_check": v07["certified"] is True},
        {"id": "G1", "layer": "registry_negative_route", "requirement": problem["negative_resolution_requires"][1], "status": "satisfied_internal", "evidence": "v0.7 retains Theta(n) honest work and persistent semantic error 1/5", "evidence_check": v07["formal_game"]["prover_budget"] == "Theta(n)" and v07["existential_encoding_branch"]["constant_gap"] == "3/5"},
        {"id": "R0", "layer": "complete_item_1", "requirement": "formal class equality, separation, or complete invariant", "status": "online_subclass_characterized_black_box_minimal_unrestricted_open", "evidence": "v2.10 one-shot normal form plus v2.11 six-premise black-box minimality", "evidence_check": v210["theorem"]["restart"] == "neither ideal replay nor strategy restart is required" and v211["status"] == "black_box_las_vegas_online_contract_minimality"},
        {"id": "R1", "layer": "complete_item_2", "requirement": "constructive protocol against adaptive obfuscation", "status": "satisfied_for_declared_online_subclass_only", "evidence": "v2.3 constructive protocol, v2.7 adaptive coupling, v2.10 one-shot converse", "evidence_check": v23["theorem"]["gap"] == "at least 1-2delta" and v27["theorem"]["adaptive_scope"].startswith("history-dependent") and v210["theorem"]["success"].endswith(">=1-s-delta_q")},
        {"id": "R2", "layer": "complete_item_3", "requirement": "matching communication, query, and honest-prover lower bounds", "status": "partial_registered_families_and_black_box_model", "evidence": "v2.1 q/N search, v2.2 Kq>=N covering, v2.11 exact observation frontiers", "evidence_check": v21["theorem"]["randomized_q_query_maximin_success"] == "q/N" and v22["theorem"]["lower_bound"] == "K*q>=N message-query covering inequality" and v211["theorem"]["probe_frontier"].startswith("k candidate-independent")},
        {"id": "R3", "layer": "complete_item_4", "requirement": "robust theorem for correlated/noisy semantic judgments", "status": "exact_for_declared_online_subclass_via_selected_path_risk_unrestricted_open", "evidence": "v2.13 proves alpha>=max(0,1-s-delta_path) for arbitrary dependence with controlled selected-path risk and a sharp marginal-only firewall", "evidence_check": v213["theorem"]["general_path_law"] == "alpha>=max(0,1-s-delta_path) for any dependence structure" and v213["theorem"]["marginal_firewall"] == "fixed-class marginals alone permit selected path error one" and v213["certified"] is True},
        {"id": "R4", "layer": "complete_item_5", "requirement": "benign encoding invariance and full-answer macro firewall", "status": "satisfied_component", "evidence": "v2.0 exact quotient transport and N-query parity macro barrier", "evidence_check": v20["theorem"]["dimension_result"].endswith("exact invariant") and "cost N" in v20["theorem"]["macro_barrier"]},
        {"id": "A0", "layer": "acceptance", "requirement": "sealed public proof and machine artifacts", "status": "satisfied_internal", "evidence": "thirteen decisive evidence packages with valid release manifests", "evidence_check": len(packages) == 13 and all(row["manifest_valid"] for row in packages)},
        {"id": "A1", "layer": "acceptance", "requirement": "independently implemented machine checks", "status": "satisfied_internal_repository", "evidence": "all thirteen decisive packages have passing clean-room verifiers", "evidence_check": len(packages) == 13 and all(row["independent_verifier_passed"] for row in packages)},
        {"id": "A2", "layer": "acceptance", "requirement": "two independent expert teams including one independent checker", "status": "missing_external_0_of_2", "evidence": "0/2 qualifying teams and 0/1 independent team checker", "evidence_check": expert["qualifying_receipts"] == 0 and expert["minimum_independent_teams"] == 2 and expert["qualifying_independently_implemented_checkers"] == 0 and expert["completion_gate_satisfied"] is False},
        {"id": "A3", "layer": "acceptance", "requirement": "deductive rather than simulation-only resolution evidence", "status": "satisfied_internal", "evidence": "counterfamilies and exact finite identities; empirical-only resolution disabled", "evidence_check": registry["resolution_policy"]["benchmark_or_simulation_alone_can_resolve"] is False},
        {"id": "A4", "layer": "acceptance", "requirement": "sharp negative and normal-form boundaries", "status": "satisfied_for_registered_claims", "evidence": "(3/5)^d, q/N, k/N, and sharp max(0,1-s-delta_path)", "evidence_check": v07["frozen_encoding_branch"]["asymptotic_gap"] == "(3/5)^d -> 0" and v21["theorem"]["randomized_q_query_maximin_success"] == "q/N" and v211["theorem"]["sharpness"].startswith("max(0,1-s-delta)") and v213["theorem"]["general_path_law"].endswith("for any dependence structure")},
    ]


def build_artifact() -> dict[str, object]:
    canonical = CANONICAL_PATH.read_text(encoding="utf-8")
    typed = TYPED_PATH.read_text(encoding="utf-8")
    old_disposition = V2_12_PATH.read_text(encoding="utf-8")
    path_theorem = V2_13_PATH.read_text(encoding="utf-8")
    canonical_flat = " ".join(canonical.split())
    old_disposition_flat = " ".join(old_disposition.split())
    path_theorem_flat = " ".join(path_theorem.split())
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    expert = json.loads(EXPERT_PATH.read_text(encoding="utf-8"))
    packages = package_rows()
    evidence = {spec[0]: load_result(spec[0]) for spec in EVIDENCE_PACKAGES}
    requirements = requirement_rows(registry, expert, packages, evidence)
    v213 = evidence["v2.13_correlated_path_risk"]
    source_checks = {
        "canonical_names_weak_verifier_conjecture": "## Weak-Verifier Characterization Conjecture" in canonical,
        "canonical_requires_five_complete_items": "A robust theorem for correlated/noisy semantic judgments." in canonical,
        "canonical_requires_declared_complete_correlation_class": "complete correlation/adaptivity class" in canonical,
        "canonical_is_research_agenda_not_prize": "research-agenda artifact, not an actual prize announcement" in canonical_flat,
        "typed_successor_is_nonnormative": "document_status = nonnormative_successor_draft" in typed,
        "v2_12_contains_superseded_fresh_only_boundary": "fresh conditional post-history blocks" in old_disposition_flat,
        "v2_13_states_selected_path_correction": "controlled selected-path risk" in path_theorem_flat,
    }
    resolved_triggers = [
        {
            "id": "T3_correlated_noise_path_theorem",
            "former_blocker": "v2.12 B3_noise_scope",
            "clearing_event": "broader correlated-noise hypothesis with a path theorem or sharp impossibility",
            "evidence": "v2.13 dependence-agnostic selected-path law plus fixed-marginal selection counterexample",
            "scope": "declared six-clause online subclass",
            "cleared": (
                v213["certified"] is True
                and v213["exchangeable_mixture_audit"]["jensen_bound_violations"] == 0
                and len(v213["selection_correlated_rows"]) == 31
            ),
        }
    ]
    blockers = [
        {"id": "B0_normative_interface", "category": "definition_authority", "blocker": "v0.1 does not authoritatively choose FIX versus ADM or the six-clause online contract", "why_current_harness_cannot_clear_it": "exact calculations cannot choose normative scope", "clearing_event": "authoritative successor definition or scope adjudication"},
        {"id": "B1_non_black_box_scope", "category": "new_mathematical_theory", "blocker": "black-box online minimality does not classify every task-specific non-black-box protocol", "why_current_harness_cannot_clear_it": "larger observation grids cannot prove a theorem using absent task structure", "clearing_event": "concrete non-black-box family or universal structure theorem"},
        {"id": "B2_universal_resources", "category": "new_mathematical_theory", "blocker": "matching resource lower bounds remain family- and interface-specific", "why_current_harness_cannot_clear_it": "more marker instances do not quantify over arbitrary interaction", "clearing_event": "interface-uniform interactive communication/query/honest-work lower bounds"},
        {"id": "B3_external_review", "category": "external_evidence", "blocker": "expert gate remains 0/2 with 0/1 independent team checkers", "why_current_harness_cannot_clear_it": "repository-generated receipts cannot establish external identity or independence", "clearing_event": "two attributable expert reproductions including one independently implemented checker"},
    ]
    totals = {
        "decisive_evidence_packages": len(packages),
        "sealed_manifest_members": sum(int(row["sealed_files"]) for row in packages),
        "sealed_member_bytes": sum(int(row["sealed_member_bytes"]) for row in packages),
        "requirement_rows": len(requirements),
        "direct_requirement_evidence_checks": sum(bool(row["evidence_check"]) for row in requirements),
        "resolved_resume_triggers": sum(bool(row["cleared"]) for row in resolved_triggers),
        "remaining_blockers": len(blockers),
        "external_expert_teams": expert["qualifying_receipts"],
    }
    statuses = {row["id"]: row["status"] for row in requirements}
    gates = {
        "F0_all_authoritative_source_clauses_present": all(source_checks.values()),
        "F1_all_thirteen_decisive_packages_sealed_and_verified": len(packages) == 13 and all(row["certified"] for row in packages),
        "F2_literal_named_conjecture_two_sided_refutation_preserved": statuses["N2"] == "refuted_exact_both_readings",
        "F3_online_subclass_characterization_and_minimality_preserved": statuses["R0"] == "online_subclass_characterized_black_box_minimal_unrestricted_open",
        "F4_correlated_noise_is_exactly_parameterized_by_selected_path_risk": statuses["R3"] == "exact_for_declared_online_subclass_via_selected_path_risk_unrestricted_open",
        "F5_v2_12_noise_resume_trigger_is_cleared_not_silently_dropped": len(resolved_triggers) == 1 and all(row["cleared"] for row in resolved_triggers),
        "F6_all_requirement_rows_have_direct_passing_evidence": len(requirements) == 18 and all(row["evidence_check"] for row in requirements),
        "F7_remaining_four_blockers_are_non_grid_events": len(blockers) == 4 and {row["category"] for row in blockers} == {"definition_authority", "new_mathematical_theory", "external_evidence"},
        "F8_external_acceptance_gate_correctly_fails": statuses["A2"] == "missing_external_0_of_2" and expert["completion_gate_satisfied"] is False,
        "F9_disposition_separates_literal_subclass_unrestricted_and_external_layers": statuses["N2"].startswith("refuted") and statuses["R0"].endswith("unrestricted_open") and statuses["A2"].startswith("missing_external"),
    }
    return {
        "schema_version": "asmp3_consolidated_path_risk_disposition_v2_14",
        "experiment_id": "ASMP-3-CONSOLIDATED-PATH-RISK-DISPOSITION-v2.14",
        "parent_results": [
            "ASMP-3-CONSOLIDATED-RESOLUTION-DISPOSITION-v2.12",
            "ASMP-3-CORRELATED-PATH-RISK-v2.13",
        ],
        "status": "literal_refutation_online_path_risk_characterization_and_four_blocker_stop_disposition",
        "source_hashes": {
            "canonical_sha256": sha256(CANONICAL_PATH),
            "registry_sha256": sha256(REGISTRY_PATH),
            "typed_successor_sha256": sha256(TYPED_PATH),
            "expert_status_sha256": sha256(EXPERT_PATH),
            "v2_12_disposition_sha256": sha256(V2_12_PATH),
            "v2_13_theorem_sha256": sha256(V2_13_PATH),
        },
        "source_checks": source_checks,
        "evidence_package_rows": packages,
        "requirement_rows": requirements,
        "resolved_resume_triggers": resolved_triggers,
        "remaining_blockers": blockers,
        "totals": totals,
        "disposition": {
            "literal_v0_1_named_conjecture": "refuted_internal_exact_both_directions",
            "nonnormative_registry_negative_route": "mathematical_conditions_satisfied_internal",
            "repaired_online_contract_subclass": "constructively_characterized_black_box_minimal_and_dependence_agnostic_via_selected_path_risk",
            "correlated_noise_block": "cleared_for_online_subclass_with_marginal_only_impossibility_firewall",
            "unrestricted_asmp3_classification": "not_established",
            "normative_definition": "unclosed",
            "community_or_prize_style_acceptance": "not_established_external_gate_0_of_2",
            "current_black_box_harness": "stop_extension_until_one_of_four_registered_resume_triggers",
            "safe_public_label": "ASMP-3 v0.1 named iff refuted internally; repaired online subclass characterized, black-box minimal, and correlated-noise robust through selected-path risk; unrestricted classification and external acceptance not established",
        },
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "This packet is an evidence-backed internal disposition, not a normative amendment, "
            "unrestricted ASMP-3 classification, or community-acceptance claim. It clears the "
            "former correlated-noise blocker only for the declared six-clause online subclass."
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
    print(f"ASMP-3 v2.14 consolidated disposition certified: {passed}/{len(result['gates'])}")
