from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CANONICAL_PATH = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY_PATH = ROOT / "problem_set_v0_1.json"
TYPED_PATH = (
    ROOT / "asmp3_typed_successor_v0_2" / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md"
)
QUANTIFIER_THEOREM_PATH = (
    ROOT
    / "asmp3_protocol_quantifier_v0_7"
    / "PROTOCOL_QUANTIFIER_THEOREM_v0_7.md"
)
EXPERT_STATUS_PATH = (
    ROOT
    / "asmp3_resolution_boundary_v0_3"
    / "artifacts"
    / "expert_review_status_v0_6.json"
)

EVIDENCE_PACKAGES = (
    {
        "id": "v0.7_protocol_quantifier",
        "directory": "asmp3_protocol_quantifier_v0_7",
        "manifest": "RELEASE_MANIFEST_v0_7.json",
        "result": "artifacts/protocol_quantifier_v0_7.json",
        "verification": "artifacts/protocol_quantifier_verification_v0_7.json",
    },
    {
        "id": "v1.9_block_selection",
        "directory": "asmp3_block_selection_composition_v1_9",
        "manifest": "RELEASE_MANIFEST_v1_9.json",
        "result": "artifacts/block_selection_composition_v1_9.json",
        "verification": "artifacts/block_selection_composition_verification_v1_9.json",
    },
    {
        "id": "v2.0_encoding_invariance",
        "directory": "asmp3_encoding_invariance_v2_0",
        "manifest": "RELEASE_MANIFEST_v2_0.json",
        "result": "artifacts/encoding_invariance_v2_0.json",
        "verification": "artifacts/encoding_invariance_verification_v2_0.json",
    },
    {
        "id": "v2.1_honest_search",
        "directory": "asmp3_honest_search_barrier_v2_1",
        "manifest": "RELEASE_MANIFEST_v2_1.json",
        "result": "artifacts/honest_search_barrier_v2_1.json",
        "verification": "artifacts/honest_search_barrier_verification_v2_1.json",
    },
    {
        "id": "v2.2_resource_tradeoff",
        "directory": "asmp3_resource_tradeoff_v2_2",
        "manifest": "RELEASE_MANIFEST_v2_2.json",
        "result": "artifacts/resource_tradeoff_v2_2.json",
        "verification": "artifacts/resource_tradeoff_verification_v2_2.json",
    },
    {
        "id": "v2.3_constructive_protocol",
        "directory": "asmp3_constructive_refutation_protocol_v2_3",
        "manifest": "RELEASE_MANIFEST_v2_3.json",
        "result": "artifacts/constructive_refutation_protocol_v2_3.json",
        "verification": "artifacts/constructive_refutation_protocol_verification_v2_3.json",
    },
    {
        "id": "v2.4_randomized_finder",
        "directory": "asmp3_randomized_finder_amplification_v2_4",
        "manifest": "RELEASE_MANIFEST_v2_4.json",
        "result": "artifacts/randomized_finder_amplification_v2_4.json",
        "verification": "artifacts/randomized_finder_amplification_verification_v2_4.json",
    },
    {
        "id": "v2.5_witness_normal_form",
        "directory": "asmp3_witness_transparent_normal_form_v2_5",
        "manifest": "RELEASE_MANIFEST_v2_5.json",
        "result": "artifacts/witness_transparent_normal_form_v2_5.json",
        "verification": "artifacts/witness_transparent_normal_form_verification_v2_5.json",
    },
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def verify_manifest(path: Path) -> tuple[bool, int, int]:
    recorded = json.loads(path.read_text(encoding="utf-8"))
    base = path.parent
    files = recorded.get("files", {})
    valid = recorded.get("file_count") == len(files)
    total_bytes = 0
    for relative, receipt in files.items():
        member = base / relative
        if not member.is_file():
            valid = False
            continue
        size = member.stat().st_size
        total_bytes += size
        valid &= receipt.get("bytes") == size
        valid &= receipt.get("sha256") == sha256(member)
    return bool(valid), len(files), total_bytes


def evidence_package_rows() -> list[dict[str, object]]:
    rows = []
    for spec in EVIDENCE_PACKAGES:
        package = ROOT / spec["directory"]
        manifest_path = package / spec["manifest"]
        result_path = package / spec["result"]
        verification_path = package / spec["verification"]
        manifest_valid, sealed_files, sealed_bytes = verify_manifest(manifest_path)
        result = json.loads(result_path.read_text(encoding="utf-8"))
        verification = json.loads(verification_path.read_text(encoding="utf-8"))
        rows.append(
            {
                "evidence_id": spec["id"],
                "directory": spec["directory"],
                "manifest": spec["manifest"],
                "manifest_sha256": sha256(manifest_path),
                "manifest_valid": manifest_valid,
                "sealed_files": sealed_files,
                "sealed_member_bytes": sealed_bytes,
                "experiment_id": result.get("experiment_id"),
                "result_status": result.get("status"),
                "producer_certified": result.get("certified") is True,
                "verification_schema": verification.get("schema_version"),
                "independent_verifier_passed": verification.get("passed") is True,
                "independent_check_count": verification.get("check_count"),
                "certified": (
                    manifest_valid
                    and result.get("certified") is True
                    and verification.get("passed") is True
                    and verification.get("check_count", 0) > 0
                ),
            }
        )
    return rows


def requirement_rows(
    registry: dict[str, object],
    quantifier_theorem: str,
    quantifier: dict[str, object],
    encoding: dict[str, object],
    search: dict[str, object],
    resource: dict[str, object],
    constructive: dict[str, object],
    randomized: dict[str, object],
    normal_form: dict[str, object],
    expert: dict[str, object],
    package_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    asmp3 = next(problem for problem in registry["problems"] if problem["id"] == "ASMP-3")
    return [
        {
            "id": "D0",
            "obligation": "identify exact problem ID, version, and foundation",
            "authority": "prize-style resolution protocol items 1-2",
            "status": "satisfied_internal",
            "evidence": "ASMP-3 / ASMP-CANDIDATE-SET-v0.1 over the declared ZFC base",
            "evidence_check": (
                expert["problem_id"] == "ASMP-3"
                and expert["problem_version"] == "ASMP-CANDIDATE-SET-v0.1"
                and registry["foundational_base"].startswith("ZFC")
            ),
        },
        {
            "id": "D1",
            "obligation": "closed formal core",
            "authority": "graduation standard item 1",
            "status": "not_satisfied_authoritative",
            "evidence": "the normative source calls v0.1 a research-agenda artifact and the registry marks graduation false",
            "evidence_check": registry["graduation_standard_satisfied"] is False,
        },
        {
            "id": "D2",
            "obligation": "normative authority of the machine-readable negative route",
            "authority": "problem registry scope",
            "status": "registry_is_nonnormative",
            "evidence": registry["registry_scope"],
            "evidence_check": registry["registry_is_normative"] is False,
        },
        {
            "id": "D3",
            "obligation": "freeze FIX versus ADM protocol quantifier",
            "authority": "canonical game text and typed successor",
            "status": "definitionally_unclosed",
            "evidence": "v0.7 records both canonical markers; v0.2 explicitly does not adjudicate authorial intent",
            "evidence_check": all(quantifier["canonical_markers"].values()),
        },
        {
            "id": "N0",
            "obligation": "test sufficiency of the displayed iff in a frozen message game",
            "authority": "Weak-Verifier Characterization Conjecture",
            "status": "refuted_exact",
            "evidence": quantifier["frozen_encoding_branch"]["conclusion"],
            "evidence_check": (
                quantifier["status"] == "exact_quantifier_fork"
                and quantifier["frozen_encoding_branch"]["asymptotic_gap"]
                == "(3/5)^d -> 0"
            ),
        },
        {
            "id": "N1",
            "obligation": "test necessity of the displayed iff when Refute is nonbinding",
            "authority": "literal v0.1 decidable-Refute definition",
            "status": "refuted_exact",
            "evidence": normal_form["theorem"]["literal_necessity_separation"],
            "evidence_check": (
                normal_form["certified"] is True
                and len(normal_form["finite_nonbinding_refute_audit"]) == 7
                and all(
                    row["certified"]
                    for row in normal_form["finite_nonbinding_refute_audit"]
                )
            ),
        },
        {
            "id": "N2",
            "obligation": "dispose of the named iff under both principal protocol readings",
            "authority": "v0.1 frozen-encoding and admits-protocol markers",
            "status": "refuted_exact_both_readings",
            "evidence": "v0.7 refutes frozen sufficiency; v2.5 refutes nonbinding necessity",
            "evidence_check": (
                "no constant gap exists"
                in quantifier["frozen_encoding_branch"]["conclusion"]
                and normal_form["theorem"]["literal_sufficiency_separation"].startswith(
                    "v0.7 frozen parity"
                )
            ),
        },
        {
            "id": "G0",
            "obligation": asmp3["negative_resolution_requires"][0],
            "authority": "nonnormative problem registry negative route",
            "status": "satisfied_internal",
            "evidence": "v0.7 exact frozen-game total-variation separation",
            "evidence_check": all(
                row["matches_closed_form"]
                for row in quantifier["frozen_encoding_branch"]["parity_rows"]
            ),
        },
        {
            "id": "G1",
            "obligation": asmp3["negative_resolution_requires"][1],
            "authority": "nonnormative problem registry negative route",
            "status": "satisfied_internal",
            "evidence": "v0.7 keeps Theta(n) honest work and persistent nonzero semantic noise",
            "evidence_check": (
                quantifier["formal_game"]["prover_budget"] == "Theta(n)"
                and quantifier["existential_encoding_branch"]["constant_gap"] == "3/5"
                and "persistent semantic error rate be `1/5`" in quantifier_theorem
                and "a_H(k)<=1/5" in quantifier_theorem
            ),
        },
        {
            "id": "R0",
            "obligation": "formal complexity class and class equality, separation, or complete invariant",
            "authority": "ASMP-3 complete-resolution item 1",
            "status": "partial_subclass_only",
            "evidence": normal_form["theorem"]["normal_form_scope"],
            "evidence_check": "complete characterization"
            in normal_form["claim_boundary"],
        },
        {
            "id": "R1",
            "obligation": "constructive protocol with adaptive-obfuscator soundness and completeness",
            "authority": "ASMP-3 complete-resolution item 2",
            "status": "partial_subclass_only",
            "evidence": constructive["status"],
            "evidence_check": (
                constructive["certified"] is True
                and constructive["theorem"]["completeness"] == "at least 1-delta"
                and constructive["theorem"]["soundness"] == "at most delta"
            ),
        },
        {
            "id": "R2",
            "obligation": "matching communication, semantic-query, and honest-prover lower bounds",
            "authority": "ASMP-3 complete-resolution item 3",
            "status": "partial_family_only",
            "evidence": "v2.1 exact Find barrier and v2.2 one-message covering frontier",
            "evidence_check": (
                search["theorem"]["randomized_q_query_maximin_success"] == "q/N"
                and resource["theorem"]["lower_bound"]
                == "K*q>=N message-query covering inequality"
            ),
        },
        {
            "id": "R3",
            "obligation": "robust theorem for the full legal correlated/noisy class",
            "authority": "ASMP-3 complete-resolution item 4",
            "status": "partial_noise_class_only",
            "evidence": randomized["claim_boundary"],
            "evidence_check": "correlated finder failures" in randomized["claim_boundary"],
        },
        {
            "id": "R4",
            "obligation": "benign encoding invariance and no hidden full-answer atom",
            "authority": "ASMP-3 complete-resolution item 5",
            "status": "satisfied_component",
            "evidence": encoding["theorem"]["dimension_result"],
            "evidence_check": (
                encoding["theorem"]["dimension_result"].endswith("exact invariant")
                and "query cost N" in encoding["theorem"]["macro_barrier"]
            ),
        },
        {
            "id": "A0",
            "obligation": "public proof, definitions, code, and machine-checkable artifacts",
            "authority": "prize-style resolution protocol item 5",
            "status": "satisfied_internal",
            "evidence": "eight sealed public repository evidence packages",
            "evidence_check": (
                len(package_rows) == 8
                and all(row["manifest_valid"] for row in package_rows)
            ),
        },
        {
            "id": "A1",
            "obligation": "exact or interval-certified computation plus independent checker",
            "authority": "prize-style resolution protocol item 6",
            "status": "satisfied_internal",
            "evidence": "all decisive artifacts use exact rational/integer arithmetic and clean-room verifiers",
            "evidence_check": (
                len(package_rows) == 8
                and all(row["independent_verifier_passed"] for row in package_rows)
                and all(row["independent_check_count"] > 0 for row in package_rows)
            ),
        },
        {
            "id": "A2",
            "obligation": "two independent expert teams, one independently implemented checker",
            "authority": "prize-style resolution protocol item 7",
            "status": "missing_external",
            "evidence": "0/2 qualifying teams and 0/1 qualifying independent checker",
            "evidence_check": (
                expert["qualifying_receipts"] == 0
                and expert["minimum_independent_teams"] == 2
                and expert["qualifying_independently_implemented_checkers"] == 0
                and expert["minimum_independently_implemented_checkers"] == 1
                and expert["completion_gate_satisfied"] is False
            ),
        },
        {
            "id": "A3",
            "obligation": "empirical evidence does not fill a deductive gap",
            "authority": "prize-style resolution protocol item 8",
            "status": "satisfied_internal",
            "evidence": "all decisive claims are deductive exact identities or explicit counterfamilies",
            "evidence_check": registry["resolution_policy"][
                "benchmark_or_simulation_alone_can_resolve"
            ]
            is False,
        },
        {
            "id": "A4",
            "obligation": "negative result supplies a sharp impossibility boundary",
            "authority": "prize-style resolution protocol item 9",
            "status": "satisfied_for_named_conjecture",
            "evidence": "v0.7 exact optimum (3/5)^d and v2.5 sharp 1-s-delta extraction boundary",
            "evidence_check": (
                quantifier["frozen_encoding_branch"]["asymptotic_gap"]
                == "(3/5)^d -> 0"
                and all(row["bound_attained"] for row in normal_form["sharpness_rows"])
            ),
        },
    ]


def build_result() -> dict[str, object]:
    canonical = CANONICAL_PATH.read_text(encoding="utf-8")
    typed = TYPED_PATH.read_text(encoding="utf-8")
    quantifier_theorem = QUANTIFIER_THEOREM_PATH.read_text(encoding="utf-8")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    expert = json.loads(EXPERT_STATUS_PATH.read_text(encoding="utf-8"))
    package_rows = evidence_package_rows()
    by_id = {row["evidence_id"]: row for row in package_rows}

    def load(package_id: str) -> dict[str, object]:
        spec = next(item for item in EVIDENCE_PACKAGES if item["id"] == package_id)
        return json.loads((ROOT / spec["directory"] / spec["result"]).read_text(encoding="utf-8"))

    quantifier = load("v0.7_protocol_quantifier")
    block = load("v1.9_block_selection")
    encoding = load("v2.0_encoding_invariance")
    search = load("v2.1_honest_search")
    resource = load("v2.2_resource_tradeoff")
    constructive = load("v2.3_constructive_protocol")
    randomized = load("v2.4_randomized_finder")
    normal_form = load("v2.5_witness_normal_form")
    requirements = requirement_rows(
        registry,
        quantifier_theorem,
        quantifier,
        encoding,
        search,
        resource,
        constructive,
        randomized,
        normal_form,
        expert,
        package_rows,
    )
    remaining_blockers = [
        {
            "id": "B0_definition_authority",
            "category": "normative_definition",
            "blocker": "v0.1 is authoritatively a definition draft and does not freeze FIX versus ADM or Refute binding",
            "why_more_current_harness_rows_cannot_clear_it": (
                "finite or asymptotic calculations cannot choose authorial scope"
            ),
            "clearing_event": "publish a normative repaired problem version or authoritative scope adjudication",
        },
        {
            "id": "B1_unrestricted_characterization",
            "category": "new_mathematical_theory",
            "blocker": "the v2.5 normal form covers only witness-transparent ideal-simulable positive-margin protocols",
            "why_more_current_harness_rows_cannot_clear_it": (
                "more rows cannot replace a new universal extractor theorem or a separating positive interface"
            ),
            "clearing_event": "prove an unrestricted WV-FIX/WV-ADM theorem or sharp impossibility",
        },
        {
            "id": "B2_universal_lower_bounds",
            "category": "new_mathematical_theory",
            "blocker": "communication/query/honest-prover lower bounds are exact only for registered families and interfaces",
            "why_more_current_harness_rows_cannot_clear_it": (
                "larger instances cannot establish quantification over all interactive protocols"
            ),
            "clearing_event": "prove interface-uniform interactive lower bounds",
        },
        {
            "id": "B3_external_reproduction",
            "category": "external_review",
            "blocker": "the acceptance gate has zero of two qualifying expert teams and zero independent team checkers",
            "why_more_current_harness_rows_cannot_clear_it": (
                "repository-generated artifacts cannot establish real reviewer identity or independence"
            ),
            "clearing_event": "two attributable independent expert reproductions, including one independent checker",
        },
    ]
    source_clause_checks = {
        "canonical_is_research_agenda_artifact": "research-agenda artifact" in canonical,
        "canonical_not_every_formulation_known_open": "not an assertion that every formulation" in canonical,
        "canonical_closed_formal_core_required": "**Closed formal core.**" in canonical,
        "canonical_warns_criterion_refutation_not_broader_resolution": (
            "Refuting one proposed criterion does not resolve a" in canonical
        ),
        "canonical_names_five_asmp3_resolution_items": (
            "## What a complete resolution requires" in canonical
            and "Matching communication, semantic-query, and honest-prover lower bounds."
            in canonical
        ),
        "canonical_requires_two_expert_teams": (
            "At least two independent expert teams" in canonical
        ),
        "canonical_final_boundary_says_definition_review": (
            "ready for external definition review" in canonical
        ),
        "typed_successor_is_nonnormative": (
            "document_status = nonnormative_successor_draft" in typed
            and "changes_parent_problem = false" in typed
        ),
        "typed_successor_does_not_adjudicate_intent": (
            "does not decide v0.1 authorial intent" in typed
        ),
    }
    disposition = {
        "named_weak_verifier_characterization_conjecture": "refuted_internal_exact_both_principal_readings",
        "nonnormative_registry_negative_route_mathematics": "satisfied_internal",
        "witness_transparent_repaired_subclass": "conditionally_characterized",
        "full_asmp3_v0_1_classification_program": "not_resolved_definitionally_unclosed_and_mathematically_partial",
        "community_or_prize_style_acceptance": "not_established_external_gate_0_of_2",
        "current_harness_architecture": "stop_further_grid_extension",
        "resume_condition": (
            "resume only for a normative scope freeze, a genuinely broader theorem/counterexample, "
            "or independent external reproduction"
        ),
    }
    status_counts: dict[str, int] = {}
    for row in requirements:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    gates = {
        "D0_all_authoritative_source_clauses_present": all(source_clause_checks.values()),
        "D1_all_eight_evidence_packages_sealed_and_verified": (
            len(package_rows) == 8 and all(row["certified"] for row in package_rows)
        ),
        "D2_named_conjecture_two_sided_separation_certified": (
            requirements[4]["status"] == "refuted_exact"
            and requirements[5]["status"] == "refuted_exact"
            and requirements[6]["status"] == "refuted_exact_both_readings"
        ),
        "D3_registry_negative_route_math_conditions_pass": (
            requirements[7]["status"] == "satisfied_internal"
            and requirements[8]["status"] == "satisfied_internal"
        ),
        "D4_complete_classification_obligations_not_overclaimed": (
            requirements[9]["status"] == "partial_subclass_only"
            and requirements[10]["status"] == "partial_subclass_only"
            and requirements[11]["status"] == "partial_family_only"
            and requirements[12]["status"] == "partial_noise_class_only"
        ),
        "D5_external_acceptance_gate_correctly_fails": (
            expert["qualifying_receipts"] == 0
            and expert["completion_gate_satisfied"] is False
            and requirements[16]["status"] == "missing_external"
        ),
        "D6_all_requirement_adjudications_evidence_backed": all(
            row["evidence_check"] for row in requirements
        ),
        "D7_disposition_has_no_resolution_contradiction": (
            disposition["named_weak_verifier_characterization_conjecture"].startswith(
                "refuted"
            )
            and disposition["full_asmp3_v0_1_classification_program"].startswith(
                "not_resolved"
            )
            and disposition["community_or_prize_style_acceptance"].startswith(
                "not_established"
            )
        ),
        "D8_remaining_blockers_are_non_enumerative": (
            len(remaining_blockers) == 4
            and {row["category"] for row in remaining_blockers}
            == {"normative_definition", "new_mathematical_theory", "external_review"}
            and all("cannot" in row["why_more_current_harness_rows_cannot_clear_it"] for row in remaining_blockers)
        ),
        "D9_parent_noise_selection_contract_retained": (
            block["theorem"]["independent_M_atom_risk"] == "1-(1-e_d)^M"
            and by_id["v1.9_block_selection"]["certified"]
        ),
    }
    return {
        "schema_version": "asmp3_resolution_disposition_v2_6",
        "experiment_id": "ASMP-3-RESOLUTION-DISPOSITION-v2.6",
        "status": "evidence_backed_negative_conjecture_disposition_and_stop_boundary",
        "problem_id": "ASMP-3",
        "problem_version": "ASMP-CANDIDATE-SET-v0.1",
        "canonical_source_sha256": sha256(CANONICAL_PATH),
        "registry_source_sha256": sha256(REGISTRY_PATH),
        "typed_successor_sha256": sha256(TYPED_PATH),
        "source_clause_checks": source_clause_checks,
        "evidence_packages": package_rows,
        "requirement_rows": requirements,
        "requirement_status_counts": status_counts,
        "remaining_blockers": remaining_blockers,
        "disposition": disposition,
        "expert_review_status": {
            "qualifying_teams": expert["qualifying_receipts"],
            "required_teams": expert["minimum_independent_teams"],
            "qualifying_independent_team_checkers": expert[
                "qualifying_independently_implemented_checkers"
            ],
            "required_independent_team_checkers": expert[
                "minimum_independently_implemented_checkers"
            ],
            "completion_gate_satisfied": expert["completion_gate_satisfied"],
        },
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "This audit certifies the internal exact refutation of the named v0.1 "
            "iff and a stopping boundary for the current harness. It deliberately "
            "does not label the broader underclosed ASMP-3 classification program "
            "or community acceptance complete."
        ),
    }
