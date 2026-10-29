from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULT_PATH = HERE / "artifacts" / "normative_closure_impossibility_v2_18.json"
VERIFY_PATH = HERE / "artifacts" / "normative_closure_impossibility_verification_v2_18.json"
CANONICAL_PATH = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
REGISTRY_PATH = ROOT / "problem_set_v0_1.json"
TYPED_MD_PATH = ROOT / "asmp3_typed_successor_v0_2" / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md"
TYPED_JSON_PATH = ROOT / "asmp3_typed_successor_v0_2" / "typed_successor_v0_2.json"
FORK_THEOREM_PATH = ROOT / "asmp3_protocol_quantifier_v0_7" / "PROTOCOL_QUANTIFIER_THEOREM_v0_7.md"
FORK_PATH = ROOT / "asmp3_protocol_quantifier_v0_7" / "artifacts" / "protocol_quantifier_v0_7.json"
DISPOSITION_PATH = ROOT / "asmp3_consolidated_resource_scope_v2_17" / "artifacts" / "consolidated_resource_scope_v2_17.json"
EXPERT_PATH = ROOT / "asmp3_resolution_boundary_v0_3" / "artifacts" / "expert_review_status_v0_6.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def collapsed(text: str) -> str:
    return " ".join(text.split())


def canonical_section() -> str:
    text = CANONICAL_PATH.read_text(encoding="utf-8")
    if "# ASMP-3" not in text or "# ASMP-4" not in text:
        raise ValueError("ASMP-3 delimiters missing")
    return text.split("# ASMP-3", 1)[1].split("# ASMP-4", 1)[0]


def exact_random_frontier() -> tuple[list[dict[str, object]], Fraction]:
    rows: list[dict[str, object]] = []
    global_best = Fraction(1)
    for denominator in range(1, 65):
        candidates = []
        for numerator in range(denominator + 1):
            p_fix = Fraction(numerator, denominator)
            candidates.append((max(p_fix, 1 - p_fix), numerator))
        best = min(value for value, _ in candidates)
        minimizers = [numerator for value, numerator in candidates if value == best]
        rows.append(
            {
                "denominator": denominator,
                "minimax_numerators_choosing_FIX": minimizers,
                "minimum_worst_model_error": str(best),
                "zero_error_possible": best == 0,
            }
        )
        global_best = min(global_best, best)
    return rows, global_best


def expected_selector_rows() -> list[dict[str, object]]:
    worlds = {"FIX", "ADM"}
    candidates = (
        ("ABSTAIN", "no_claim", set()),
        ("FIX", "model_set_claim", {"FIX"}),
        ("ADM", "model_set_claim", {"ADM"}),
        ("BOTH", "model_set_claim", worlds),
    )
    rows = []
    for output, kind, selected in candidates:
        makes_claim = kind == "model_set_claim"
        excluded = sorted(worlds - selected) if makes_claim else []
        covers = makes_claim and not excluded
        sound = not makes_claim or covers
        decisive = makes_claim and len(selected) == 1
        rows.append(
            {
                "selector_output": output,
                "action_kind": kind,
                "selected_modes": sorted(selected),
                "decisive_singleton": decisive,
                "excluded_clause_preserving_models": excluded,
                "entailment_sound": sound,
                "covers_every_clause_preserving_model": covers,
                "sound_and_decisive_normative_closure": sound and decisive,
            }
        )
    return rows


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    canonical = CANONICAL_PATH.read_text(encoding="utf-8")
    section = canonical_section()
    flat = collapsed(section)
    lower = flat.casefold()
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    typed_md = TYPED_MD_PATH.read_text(encoding="utf-8")
    typed = json.loads(TYPED_JSON_PATH.read_text(encoding="utf-8"))
    fork_md = collapsed(FORK_THEOREM_PATH.read_text(encoding="utf-8"))
    fork = json.loads(FORK_PATH.read_text(encoding="utf-8"))
    disposition = json.loads(DISPOSITION_PATH.read_text(encoding="utf-8"))
    expert = json.loads(EXPERT_PATH.read_text(encoding="utf-8"))

    hashes = {
        "canonical_sha256": sha256(CANONICAL_PATH),
        "registry_sha256": sha256(REGISTRY_PATH),
        "typed_markdown_sha256": sha256(TYPED_MD_PATH),
        "typed_json_sha256": sha256(TYPED_JSON_PATH),
        "fork_theorem_sha256": sha256(FORK_THEOREM_PATH),
        "fork_artifact_sha256": sha256(FORK_PATH),
        "v2_17_disposition_sha256": sha256(DISPOSITION_PATH),
        "expert_status_sha256": sha256(EXPERT_PATH),
    }

    required_clauses = (
        "freeze a decision relation `R_n`",
        "a public-coin message order and stopping rule",
        "an atomic semantic-query language `A_n`",
        "Admissible transcript encodings, verifier and prover randomness, and adaptive query access are part of the game",
        "A task family admits a constant-gap, doubly efficient, noise-robust oversight protocol",
        "r_R(n) = max_(false admissible transcript tau)",
        "a_H(k) = inf_(registered k-query aggregators A)",
        "A formal complexity class for the protocols above",
    )
    forbidden_selectors = (
        "wv-fix",
        "wv-adm",
        "interface is fixed before protocol algorithms",
        "protocol may select an interface",
        "normative mode is fixed",
        "normative mode is admissible",
    )
    expected_obligations = {
        "decision_relation_is_frozen": "freeze a decision relation `R_n`" in flat,
        "public_coin_order_and_stopping_are_frozen_within_realized_game": "a public-coin message order and stopping rule" in flat,
        "atomic_semantic_query_language_is_frozen_within_realized_game": "an atomic semantic-query language `A_n`" in flat,
        "transcript_encoding_is_part_of_realized_game": "Admissible transcript encodings" in flat and "are part of the game" in flat,
        "verifier_and_prover_randomness_are_part_of_game": "verifier and prover randomness" in flat and "are part of the game" in flat,
        "adaptive_query_access_is_part_of_game": "adaptive query access" in flat and "are part of the game" in flat,
        "verifier_query_and_transcript_budgets_are_polylogarithmic": all(marker in flat for marker in ("A verifier has time `s(n)`", "semantic-query budget `q(n)`", "transcript budget `B(n)`", "intended to be `polylog(T(n))`")),
        "honest_prover_strategy_is_efficient": "The honest prover must itself have an efficient strategy" in flat,
        "noise_model_is_complete_and_nonzero": "marginal error bound `eta<1/2`" in flat and "a complete correlation/adaptivity class" in flat,
        "protocol_admission_phrase_is_present": "A task family admits a constant-gap, doubly efficient, noise-robust oversight protocol" in flat,
    }

    models = result.get("completion_models", [])
    by_mode = {row.get("mode"): row for row in models}
    same_substrate = "same task relation, semantic worlds, oracle law, prover budget, and verifier resource scale" in fork_md
    models_valid = (
        set(by_mode) == {"FIX", "ADM"}
        and all(row.get("clause_preserving_completion") is True for row in models)
        and all(row.get("all_explicit_obligations_satisfied") is True for row in models)
        and all(row.get("explicit_obligations") == expected_obligations for row in models)
        and all(expected_obligations.values())
        and all(row.get("same_task_relation_world_oracle_and_budgets") is same_substrate for row in models)
        and by_mode["FIX"].get("quantifier_order") == "forall frozen game G, exists protocol algorithms Pi inside G"
        and by_mode["ADM"].get("quantifier_order") == "exists game G in declared Interfaces(E), exists protocol algorithms Pi inside G"
    )

    material_fork = (
        same_substrate
        and fork.get("certified") is True
        and fork.get("frozen_encoding_branch", {}).get("asymptotic_gap") == "(3/5)^d -> 0"
        and fork.get("existential_encoding_branch", {}).get("constant_gap") == "3/5"
        and by_mode.get("FIX", {}).get("parity_gap") == "(3/5)^d -> 0"
        and by_mode.get("ADM", {}).get("parity_gap") == "3/5"
        and by_mode.get("FIX", {}).get("parity_counterexample_status") != by_mode.get("ADM", {}).get("parity_counterexample_status")
    )

    selector_rows = expected_selector_rows()
    random_rows, global_best = exact_random_frontier()
    random_result = result.get("randomized_selector_audit", {})
    mutations = result.get("mutation_audit", [])
    expected_mutations = [
        ("sealed_v0_1", ["ADM", "FIX"], False),
        ("add_FIX_scope_axiom", ["FIX"], True),
        ("add_ADM_scope_axiom", ["ADM"], True),
        ("add_both_incompatible_scope_axioms", [], False),
    ]
    mutations_valid = len(mutations) == 4 and all(
        row.get("mutation") == name
        and row.get("surviving_completion_modes") == survivors
        and row.get("unique_normative_closure") is unique
        and row.get("matches") is True
        for row, (name, survivors, unique) in zip(mutations, expected_mutations)
    )

    boundary = result.get("claim_boundary", "")
    checks = {
        "V0_schema_status_parent_and_hashes": result.get("schema_version") == "asmp3_normative_closure_impossibility_v2_18" and result.get("status") == "source_relative_impossibility_of_sound_decisive_normative_closure" and result.get("parent_results") == ["ASMP-3-PROTOCOL-QUANTIFIER-FORK-v0.7", "ASMP-3-CONSOLIDATED-RESOURCE-SCOPE-v2.17"] and result.get("sealed_source_hashes") == hashes,
        "V1_canonical_clause_inventory_and_selector_absence": all(marker in flat for marker in required_clauses) and "a change to its objects, quantifiers, adversary, or resolution criterion changes the problem" in collapsed(canonical) and not any(marker in lower for marker in forbidden_selectors) and result.get("source_scope_audit", {}).get("certified") is True,
        "V2_current_authority_state_has_no_selector": registry.get("registry_is_normative") is False and registry.get("graduation_standard_satisfied") is False and typed.get("status") == "nonnormative_successor_draft" and typed.get("changes_parent_problem") is False and "This draft does not decide v0.1 authorial intent" in typed_md and disposition.get("disposition", {}).get("normative_definition") == "unclosed" and expert.get("qualifying_receipts") == 0 and expert.get("completion_gate_satisfied") is False and result.get("authority_audit", {}).get("authoritative_selecting_channels") == 0,
        "V3_two_incompatible_clause_preserving_completions": models_valid and by_mode["FIX"].get("added_scope_axiom") != by_mode["ADM"].get("added_scope_axiom"),
        "V4_same_substrate_has_material_FIX_ADM_fork": material_fork and result.get("material_fork_audit", {}).get("certified") is True,
        "V5_deterministic_selector_frontier_reconstructed": result.get("selector_audit", {}).get("rows") == selector_rows and sum(row["sound_and_decisive_normative_closure"] for row in selector_rows) == 0 and result.get("selector_audit", {}).get("sound_decisive_selector_count") == 0,
        "V6_randomized_minimax_frontier_reconstructed": random_result.get("rows") == random_rows and global_best == Fraction(1, 2) and random_result.get("global_minimum_worst_model_error") == "1/2" and random_result.get("zero_error_randomized_selector_exists") is False,
        "V7_one_normative_bit_is_necessary_and_sufficient_inside_audited_fork": result.get("authority_bit_audit", {}).get("scope") == "selection within the audited binary FIX/ADM fork" and result.get("authority_bit_audit", {}).get("zero_external_bits_partition") == [["ADM", "FIX"]] and result.get("authority_bit_audit", {}).get("one_external_bit_partition") == [["ADM"], ["FIX"]] and result.get("authority_bit_audit", {}).get("minimum_external_normative_bits") == 1,
        "V8_scope_axiom_mutations_close_exactly_as_claimed": mutations_valid,
        "V9_claim_is_source_relative_repairable_and_not_metaphysical": all(phrase in boundary for phrase in ("sealed v0.1 source and current authority channels", "does not prove that normative choice is metaphysically impossible", "recover authorial intent", "authorized maintainer from adding one scope axiom", "choosing it is an amendment")) and result.get("claim_boundary_audit", {}).get("certified") is True and result.get("certified") is True and len(result.get("gates", {})) == 10 and all(result.get("gates", {}).values()),
    }
    return {
        "schema_version": "asmp3_normative_closure_impossibility_verification_v2_18",
        "checker": "clean_room_source_authority_model_selector_minimax_mutation_and_claim_boundary_audit",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": "This verifies source-relative underdetermination of a unique FIX/ADM selection; it neither supplies authority nor decides authorial intent.",
    }


def main() -> None:
    receipt = verify()
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if not receipt["passed"]:
        failed = [name for name, value in receipt["checks"].items() if not value]
        raise RuntimeError(f"ASMP-3 v2.18 verification failed: {failed}")
    print(f"ASMP-3 normative-closure impossibility verification passed: {receipt['check_count']}/{receipt['check_count']}")


if __name__ == "__main__":
    main()
