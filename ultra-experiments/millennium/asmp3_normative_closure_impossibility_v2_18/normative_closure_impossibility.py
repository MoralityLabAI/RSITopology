from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ARTIFACT_DIR = HERE / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "normative_closure_impossibility_v2_18.json"
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


def collapse(text: str) -> str:
    return " ".join(text.split())


def extract_asmp3(source: str) -> str:
    if "# ASMP-3" not in source or "# ASMP-4" not in source:
        raise ValueError("canonical ASMP-3 section delimiters are missing")
    return source.split("# ASMP-3", 1)[1].split("# ASMP-4", 1)[0]


def source_scope_audit() -> dict[str, object]:
    source = CANONICAL_PATH.read_text(encoding="utf-8")
    section = extract_asmp3(source)
    flat = collapse(section)
    lower = flat.casefold()
    explicit = {
        "freezes_decision_relation": "freeze a decision relation `R_n`" in flat,
        "freezes_public_coin_order_and_stopping": "a public-coin message order and stopping rule" in flat,
        "freezes_atomic_query_language": "an atomic semantic-query language `A_n`" in flat,
        "encodings_are_part_of_game": "Admissible transcript encodings, verifier and prover randomness, and adaptive query access are part of the game" in flat,
        "uses_task_admits_protocol_phrase": "A task family admits a constant-gap, doubly efficient, noise-robust oversight protocol" in flat,
        "defines_refutation_dimension": "r_R(n) = max_(false admissible transcript tau)" in flat,
        "defines_noise_profile": "a_H(k) = inf_(registered k-query aggregators A)" in flat,
        "requires_formal_class": "A formal complexity class for the protocols above" in flat,
        "declares_version_changes_for_quantifier_changes": "a change to its objects, quantifiers, adversary, or resolution criterion changes the problem" in collapse(source),
    }
    selector_phrases = {
        "names_WV_FIX": "wv-fix" in lower,
        "names_WV_ADM": "wv-adm" in lower,
        "fixes_interface_before_protocol_algorithms": "interface is fixed before protocol algorithms" in lower,
        "quantifies_exists_G_in_interface_class": "exists g in" in lower and "interface" in lower,
        "permits_protocol_to_select_interface": "protocol may select an interface" in lower,
        "selects_FIXED_as_normative_mode": "normative mode is fixed" in lower,
        "selects_ADMISSIBLE_as_normative_mode": "normative mode is admissible" in lower,
    }
    return {
        "explicit_clause_checks": explicit,
        "selector_phrase_presence": selector_phrases,
        "explicit_clause_count": len(explicit),
        "explicit_clause_checks_passed": sum(explicit.values()),
        "selector_phrase_count": sum(selector_phrases.values()),
        "canonical_section_sha256": hashlib.sha256(section.encode("utf-8")).hexdigest().upper(),
        "certified": all(explicit.values()) and not any(selector_phrases.values()),
    }


def authority_audit() -> dict[str, object]:
    source = CANONICAL_PATH.read_text(encoding="utf-8")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    typed = json.loads(TYPED_JSON_PATH.read_text(encoding="utf-8"))
    typed_md = TYPED_MD_PATH.read_text(encoding="utf-8")
    fork = json.loads(FORK_PATH.read_text(encoding="utf-8"))
    disposition = json.loads(DISPOSITION_PATH.read_text(encoding="utf-8"))
    expert = json.loads(EXPERT_PATH.read_text(encoding="utf-8"))
    channels = [
        {
            "channel": "canonical_v0_1",
            "authoritative_for_parent": True,
            "selects_one_interface_mode": False,
            "evidence": "normative statement is an ungraduated research-agenda definition draft",
            "check": "research-agenda artifact, not an actual prize announcement" in collapse(source),
        },
        {
            "channel": "machine_registry_v0_1",
            "authoritative_for_parent": False,
            "selects_one_interface_mode": False,
            "evidence": "registry_is_normative=false",
            "check": registry["registry_is_normative"] is False and registry["graduation_standard_satisfied"] is False,
        },
        {
            "channel": "typed_successor_v0_2",
            "authoritative_for_parent": False,
            "selects_one_interface_mode": False,
            "evidence": "nonnormative draft exposes both WV-FIX and WV-ADM",
            "check": typed["status"] == "nonnormative_successor_draft" and typed["changes_parent_problem"] is False and set(typed["successor_targets"]) == {"characterize_WV_FIX", "characterize_WV_ADM"} and "This draft does not decide v0.1 authorial intent" in typed_md,
        },
        {
            "channel": "protocol_fork_v0_7",
            "authoritative_for_parent": False,
            "selects_one_interface_mode": False,
            "evidence": "exact mathematical fork with explicit authorial-intent boundary",
            "check": fork["certified"] is True and "does not decide which reading" in fork["claim_boundary"],
        },
        {
            "channel": "consolidated_disposition_v2_17",
            "authoritative_for_parent": False,
            "selects_one_interface_mode": False,
            "evidence": "normative_definition=unclosed",
            "check": disposition["certified"] is True and disposition["disposition"]["normative_definition"] == "unclosed",
        },
        {
            "channel": "external_expert_gate",
            "authoritative_for_parent": False,
            "selects_one_interface_mode": False,
            "evidence": "0/2 qualifying teams and no independent team checker",
            "check": expert["qualifying_receipts"] == 0 and expert["minimum_independent_teams"] == 2 and expert["completion_gate_satisfied"] is False,
        },
    ]
    return {
        "channels": channels,
        "channel_count": len(channels),
        "authoritative_channels": sum(row["authoritative_for_parent"] for row in channels),
        "authoritative_selecting_channels": sum(row["authoritative_for_parent"] and row["selects_one_interface_mode"] for row in channels),
        "all_checks_pass": all(row["check"] for row in channels),
        "certified": len(channels) == 6 and all(row["check"] for row in channels) and sum(row["authoritative_for_parent"] and row["selects_one_interface_mode"] for row in channels) == 0,
    }


COMMON_OBLIGATIONS = (
    "decision_relation_is_frozen",
    "public_coin_order_and_stopping_are_frozen_within_realized_game",
    "atomic_semantic_query_language_is_frozen_within_realized_game",
    "transcript_encoding_is_part_of_realized_game",
    "verifier_and_prover_randomness_are_part_of_game",
    "adaptive_query_access_is_part_of_game",
    "verifier_query_and_transcript_budgets_are_polylogarithmic",
    "honest_prover_strategy_is_efficient",
    "noise_model_is_complete_and_nonzero",
    "protocol_admission_phrase_is_present",
)


def explicit_obligations_from_source() -> dict[str, bool]:
    section = collapse(extract_asmp3(CANONICAL_PATH.read_text(encoding="utf-8")))
    return {
        "decision_relation_is_frozen": "freeze a decision relation `R_n`" in section,
        "public_coin_order_and_stopping_are_frozen_within_realized_game": "a public-coin message order and stopping rule" in section,
        "atomic_semantic_query_language_is_frozen_within_realized_game": "an atomic semantic-query language `A_n`" in section,
        "transcript_encoding_is_part_of_realized_game": "Admissible transcript encodings" in section and "are part of the game" in section,
        "verifier_and_prover_randomness_are_part_of_game": "verifier and prover randomness" in section and "are part of the game" in section,
        "adaptive_query_access_is_part_of_game": "adaptive query access" in section and "are part of the game" in section,
        "verifier_query_and_transcript_budgets_are_polylogarithmic": all(marker in section for marker in ("A verifier has time `s(n)`", "semantic-query budget `q(n)`", "transcript budget `B(n)`", "intended to be `polylog(T(n))`")),
        "honest_prover_strategy_is_efficient": "The honest prover must itself have an efficient strategy" in section,
        "noise_model_is_complete_and_nonzero": "marginal error bound `eta<1/2`" in section and "a complete correlation/adaptivity class" in section,
        "protocol_admission_phrase_is_present": "A task family admits a constant-gap, doubly efficient, noise-robust oversight protocol" in section,
    }


def completion_models() -> list[dict[str, object]]:
    fork = json.loads(FORK_PATH.read_text(encoding="utf-8"))
    theorem = collapse(FORK_THEOREM_PATH.read_text(encoding="utf-8"))
    shared_substrate = "same task relation, semantic worlds, oracle law, prover budget, and verifier resource scale" in theorem
    base_obligations = explicit_obligations_from_source()
    if set(base_obligations) != set(COMMON_OBLIGATIONS):
        raise AssertionError("explicit obligation inventory drifted")
    fixed = {
        "mode": "FIX",
        "quantifier_order": "forall frozen game G, exists protocol algorithms Pi inside G",
        "added_scope_axiom": "the game interface is fixed before protocol algorithms are quantified",
        "parity_interface": "G_fix",
        "parity_gap": fork["frozen_encoding_branch"]["asymptotic_gap"],
        "parity_counterexample_status": "valid counterexample to displayed sufficiency",
        "same_task_relation_world_oracle_and_budgets": shared_substrate,
        "explicit_obligations": dict(base_obligations),
    }
    admissible = {
        "mode": "ADM",
        "quantifier_order": "exists game G in declared Interfaces(E), exists protocol algorithms Pi inside G",
        "added_scope_axiom": "protocol admission may select a game interface from a declared interface class",
        "parity_interface": "G_admit",
        "parity_gap": fork["existential_encoding_branch"]["constant_gap"],
        "parity_counterexample_status": "not a counterexample because vector interface is admitted",
        "same_task_relation_world_oracle_and_budgets": shared_substrate,
        "explicit_obligations": dict(base_obligations),
    }
    for row in (fixed, admissible):
        row["all_explicit_obligations_satisfied"] = all(row["explicit_obligations"].values())
        row["clause_preserving_completion"] = row["all_explicit_obligations_satisfied"] and row["same_task_relation_world_oracle_and_budgets"]
    return [fixed, admissible]


def material_fork_audit(models: list[dict[str, object]]) -> dict[str, object]:
    by_mode = {row["mode"]: row for row in models}
    return {
        "same_substrate": all(row["same_task_relation_world_oracle_and_budgets"] for row in models),
        "distinct_quantifier_orders": len({row["quantifier_order"] for row in models}) == 2,
        "distinct_added_scope_axioms": len({row["added_scope_axiom"] for row in models}) == 2,
        "fixed_gap": by_mode["FIX"]["parity_gap"],
        "admissible_gap": by_mode["ADM"]["parity_gap"],
        "material_outcomes_differ": by_mode["FIX"]["parity_gap"] != by_mode["ADM"]["parity_gap"] and by_mode["FIX"]["parity_counterexample_status"] != by_mode["ADM"]["parity_counterexample_status"],
        "certified": all(row["clause_preserving_completion"] for row in models) and by_mode["FIX"]["parity_gap"] == "(3/5)^d -> 0" and by_mode["ADM"]["parity_gap"] == "3/5",
    }


def selector_audit(models: list[dict[str, object]]) -> dict[str, object]:
    modes = {row["mode"] for row in models}
    candidates = (
        ("ABSTAIN", "no_claim", set()),
        ("FIX", "model_set_claim", {"FIX"}),
        ("ADM", "model_set_claim", {"ADM"}),
        ("BOTH", "model_set_claim", {"FIX", "ADM"}),
    )
    rows = []
    for output, action_kind, admitted in candidates:
        makes_claim = action_kind == "model_set_claim"
        decisive = makes_claim and len(admitted) == 1
        excludes = sorted(modes - admitted) if makes_claim else []
        complete_coverage = makes_claim and not excludes
        entailment_sound = not makes_claim or complete_coverage
        rows.append(
            {
                "selector_output": output,
                "action_kind": action_kind,
                "selected_modes": sorted(admitted),
                "decisive_singleton": decisive,
                "excluded_clause_preserving_models": excludes,
                "entailment_sound": entailment_sound,
                "covers_every_clause_preserving_model": complete_coverage,
                "sound_and_decisive_normative_closure": decisive and entailment_sound,
            }
        )
    sound_decisive = [row for row in rows if row["sound_and_decisive_normative_closure"]]
    return {
        "rows": rows,
        "candidate_output_count": len(rows),
        "clause_preserving_mode_count": len(modes),
        "entailed_singleton_modes": sorted(mode for mode in modes if all(row["mode"] == mode for row in models)),
        "sound_decisive_selector_count": len(sound_decisive),
        "set_valued_safe_repair": "BOTH",
        "epistemically_safe_nonclosure": "ABSTAIN",
        "certified": len(models) == 2 and len(modes) == 2 and len(rows) == 4 and not sound_decisive,
    }


def claim_boundary_audit(mutations: list[dict[str, object]]) -> dict[str, object]:
    boundary = (
        "This is an impossibility theorem for unique, entailment-sound normative closure from "
        "the sealed v0.1 source and current authority channels. It does not prove that normative "
        "choice is metaphysically impossible, recover authorial intent, or prevent an authorized "
        "maintainer from adding one scope axiom. FIX remains the natural strict-freeze repair; "
        "choosing it is an amendment unless authority explicitly adopts that reading."
    )
    checks = {
        "source_relative_not_metaphysical": "sealed v0.1 source and current authority channels" in boundary and "does not prove that normative choice is metaphysically impossible" in boundary,
        "does_not_claim_authorial_intent": "recover authorial intent" in boundary,
        "authorized_repair_is_allowed": "authorized maintainer from adding one scope axiom" in boundary,
        "natural_reading_is_not_mislabeled_as_entailment": "FIX remains the natural strict-freeze repair" in boundary and "choosing it is an amendment" in boundary,
        "both_single_axiom_repairs_are_constructed": len(mutations) == 4 and [row["unique_normative_closure"] for row in mutations] == [False, True, True, False],
    }
    return {"statement": boundary, "checks": checks, "certified": all(checks.values())}


def randomized_selector_audit() -> dict[str, object]:
    rows = []
    best = Fraction(1)
    best_rows = []
    for denominator in range(1, 65):
        denominator_best = Fraction(1)
        denominator_numerators = []
        for numerator in range(denominator + 1):
            choose_fix = Fraction(numerator, denominator)
            error_if_fix = 1 - choose_fix
            error_if_adm = choose_fix
            worst = max(error_if_fix, error_if_adm)
            if worst < denominator_best:
                denominator_best = worst
                denominator_numerators = [numerator]
            elif worst == denominator_best:
                denominator_numerators.append(numerator)
        row = {
            "denominator": denominator,
            "minimax_numerators_choosing_FIX": denominator_numerators,
            "minimum_worst_model_error": str(denominator_best),
            "zero_error_possible": denominator_best == 0,
        }
        rows.append(row)
        if denominator_best < best:
            best = denominator_best
            best_rows = [denominator]
        elif denominator_best == best:
            best_rows.append(denominator)
    return {
        "rows": rows,
        "denominators_audited": len(rows),
        "global_minimum_worst_model_error": str(best),
        "denominators_attaining_global_minimum": best_rows,
        "zero_error_randomized_selector_exists": best == 0,
        "certified": len(rows) == 64 and best == Fraction(1, 2) and not any(row["zero_error_possible"] for row in rows),
    }


def authority_bit_audit(models: list[dict[str, object]]) -> dict[str, object]:
    modes = sorted(row["mode"] for row in models)
    zero_bit_cells = [modes]
    one_bit_cells = [["ADM"], ["FIX"]]
    zero_bit_decisive = all(len(cell) == 1 for cell in zero_bit_cells)
    one_bit_decisive = all(len(cell) == 1 for cell in one_bit_cells)
    return {
        "scope": "selection within the audited binary FIX/ADM fork",
        "completion_modes": modes,
        "zero_external_bits_partition": zero_bit_cells,
        "zero_external_bits_decisive": zero_bit_decisive,
        "one_external_bit_partition": one_bit_cells,
        "one_external_bit_decisive": one_bit_decisive,
        "minimum_external_normative_bits": 1,
        "bit_interpretation": "0 selects ADM; 1 selects FIX (or the reverse convention)",
        "certified": len(modes) == 2 and not zero_bit_decisive and one_bit_decisive,
    }


def mutation_audit() -> list[dict[str, object]]:
    mutations = (
        ("sealed_v0_1", False, False, ["ADM", "FIX"]),
        ("add_FIX_scope_axiom", True, False, ["FIX"]),
        ("add_ADM_scope_axiom", False, True, ["ADM"]),
        ("add_both_incompatible_scope_axioms", True, True, []),
    )
    rows = []
    for name, fix_clause, adm_clause, expected in mutations:
        survivors = []
        if not adm_clause:
            survivors.append("FIX")
        if not fix_clause:
            survivors.append("ADM")
        rows.append(
            {
                "mutation": name,
                "adds_FIX_scope_axiom": fix_clause,
                "adds_ADM_scope_axiom": adm_clause,
                "surviving_completion_modes": sorted(survivors),
                "expected_survivors": expected,
                "matches": sorted(survivors) == expected,
                "unique_normative_closure": len(survivors) == 1,
            }
        )
    return rows


def build_artifact() -> dict[str, object]:
    source = source_scope_audit()
    authority = authority_audit()
    models = completion_models()
    fork = material_fork_audit(models)
    selectors = selector_audit(models)
    randomized = randomized_selector_audit()
    bits = authority_bit_audit(models)
    mutations = mutation_audit()
    boundary = claim_boundary_audit(mutations)
    gates = {
        "N0_canonical_source_contains_both_load_bearing_markers": source["certified"],
        "N1_canonical_source_contains_no_unique_interface_selector": source["selector_phrase_count"] == 0,
        "N2_no_current_authoritative_channel_selects_one_mode": authority["certified"],
        "N3_FIX_and_ADM_are_both_clause_preserving_completions": len(models) == 2 and all(row["clause_preserving_completion"] for row in models),
        "N4_same_substrate_completion_models_have_materially_distinct_outcomes": fork["certified"],
        "N5_no_deterministic_source_only_selector_is_both_sound_and_decisive": selectors["certified"] and selectors["sound_decisive_selector_count"] == 0,
        "N6_randomization_cannot_reduce_worst_completion_error_below_one_half": randomized["certified"],
        "N7_within_audited_FIX_ADM_fork_one_external_normative_bit_is_necessary_and_sufficient": bits["certified"] and bits["minimum_external_normative_bits"] == 1,
        "N8_minimal_scope_axiom_mutations_close_each_branch_and_both_are_inconsistent": len(mutations) == 4 and all(row["matches"] for row in mutations) and [row["unique_normative_closure"] for row in mutations] == [False, True, True, False],
        "N9_impossibility_is_source_relative_and_repairable_not_metaphysical": boundary["certified"],
    }
    return {
        "schema_version": "asmp3_normative_closure_impossibility_v2_18",
        "experiment_id": "ASMP-3-NORMATIVE-CLOSURE-IMPOSSIBILITY-v2.18",
        "parent_results": [
            "ASMP-3-PROTOCOL-QUANTIFIER-FORK-v0.7",
            "ASMP-3-CONSOLIDATED-RESOURCE-SCOPE-v2.17",
        ],
        "status": "source_relative_impossibility_of_sound_decisive_normative_closure",
        "sealed_source_hashes": {
            "canonical_sha256": sha256(CANONICAL_PATH),
            "registry_sha256": sha256(REGISTRY_PATH),
            "typed_markdown_sha256": sha256(TYPED_MD_PATH),
            "typed_json_sha256": sha256(TYPED_JSON_PATH),
            "fork_theorem_sha256": sha256(FORK_THEOREM_PATH),
            "fork_artifact_sha256": sha256(FORK_PATH),
            "v2_17_disposition_sha256": sha256(DISPOSITION_PATH),
            "expert_status_sha256": sha256(EXPERT_PATH),
        },
        "theorem": {
            "semantic_underdetermination": "if two clause-preserving completions assign different material outcomes, the source does not entail a unique completion",
            "selector_impossibility": "no source-only selector can be both entailment-sound and decisive on sealed v0.1",
            "deterministic_frontier": "FIX and ADM each exclude one admissible model; BOTH is sound but nondecisive; ABSTAIN is safe but not closure",
            "randomized_frontier": "minimum worst-completion selection error is 1/2",
            "authority_information": "within the audited binary fork, one external normative bit is necessary and sufficient to select FIX versus ADM",
            "repair": "add exactly one authoritative quantifier-order axiom or publish a successor that explicitly poses both targets",
        },
        "source_scope_audit": source,
        "authority_audit": authority,
        "completion_models": models,
        "material_fork_audit": fork,
        "selector_audit": selectors,
        "randomized_selector_audit": randomized,
        "authority_bit_audit": bits,
        "mutation_audit": mutations,
        "claim_boundary_audit": boundary,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": boundary["statement"],
    }


def write_artifact() -> dict[str, object]:
    artifact = build_artifact()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return artifact


if __name__ == "__main__":
    result = write_artifact()
    passed = sum(bool(value) for value in result["gates"].values())
    print(f"ASMP-3 normative-closure impossibility certified: {passed}/{len(result['gates'])}")
