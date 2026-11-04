from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DRAFT_PATH = HERE / "typed_successor_v0_2.json"
DOCUMENT_PATH = HERE / "ASMP3_TYPED_SUCCESSOR_DRAFT_v0_2.md"
OUTPUT_PATH = HERE / "artifacts" / "typed_successor_validation_v0_2.json"

EXPECTED_LAYERS = {
    "environment": {
        "public_instances",
        "semantic_worlds",
        "outputs",
        "decision_relation",
        "semantic_atoms",
        "registered_replications",
        "ideal_oracle",
        "complete_noise_class",
        "prover_information",
        "verifier_information",
        "prover_budget",
    },
    "fixed_game": {
        "message_alphabet",
        "canonical_serialization",
        "message_order",
        "stopping_rule",
        "randomness",
        "resource_budgets",
        "malformed_and_abort_behavior",
        "payoff",
        "refute_relation",
    },
    "protocol": {
        "honest_prover_algorithm",
        "adversarial_strategy_class",
        "verifier_algorithm",
    },
}

EXPECTED_REFUTE_AXIOMS = {
    "soundness",
    "coverage_of_every_false_terminal_claim",
    "binding_to_refutation_based_decisions",
    "registered_replication_quotient",
}

EXPECTED_JOINT_RISK_CONDITIONS = {
    "adversarial_refutation_selection",
    "history_conditional_noise",
    "registered_replications",
    "adaptive_query_and_stopping",
    "full_joint_refute_predicate",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def validate() -> dict[str, Any]:
    draft = load_json(DRAFT_PATH)
    document = DOCUMENT_PATH.read_text(encoding="utf-8")
    witness_path = (HERE / draft["witness_artifact"]).resolve()
    witness = load_json(witness_path)

    layers = draft.get("typed_layers", {})
    fixed_mode = draft.get("interface_modes", {}).get("fixed", {})
    admissible_mode = draft.get("interface_modes", {}).get(
        "existential", {}
    )
    noise = draft.get("noise_objects", {})

    checks = {
        "D0_schema_and_status_are_draft_only": (
            draft.get("schema_version")
            == "asmp3_typed_successor_draft_v0_2"
            and draft.get("status") == "nonnormative_successor_draft"
            and draft.get("parent_problem_id") == "ASMP-3"
            and draft.get("parent_problem_version")
            == "ASMP-CANDIDATE-SET-v0.1"
            and draft.get("changes_parent_problem") is False
        ),
        "D1_typed_layers_are_complete_and_disjoint": (
            set(layers) == set(EXPECTED_LAYERS)
            and all(
                set(layers.get(name, [])) == fields
                for name, fields in EXPECTED_LAYERS.items()
            )
            and not (
                set(layers.get("fixed_game", []))
                & set(layers.get("protocol", []))
            )
        ),
        "D2_fixed_and_existential_quantifiers_are_distinct": (
            fixed_mode.get("class_name") == "WV-FIX"
            and fixed_mode.get("interface_quantifier")
            == "fixed_before_protocol_algorithms"
            and admissible_mode.get("class_name") == "WV-ADM"
            and admissible_mode.get("interface_quantifier")
            == "exists_G_in_declared_Interfaces_E"
        ),
        "D3_refute_relation_has_all_adequacy_axioms": (
            set(draft.get("refute_adequacy_axioms", []))
            == EXPECTED_REFUTE_AXIOMS
            and fixed_mode.get("refutation_invariant")
            == "replication_quotiented_r_E_G"
            and set(
                admissible_mode.get("refutation_invariant_options", [])
            )
            == {
                "protocol_relative_r_E_G",
                "effective_best_interface_r_star_E",
                "proved_equivalent_operational_invariant",
            }
        ),
        "D4_joint_noise_object_replaces_marginal_condition": (
            noise.get("single_atom_profile_role")
            == "marginal_diagnostic_only"
            and noise.get("required_characterization_object")
            == "joint_transcript_conditional_selected_refutation_risk"
            and set(noise.get("conditions_in_scope", []))
            == EXPECTED_JOINT_RISK_CONDITIONS
        ),
        "D5_successor_targets_both_classes": (
            set(draft.get("successor_targets", []))
            == {"characterize_WV_FIX", "characterize_WV_ADM"}
        ),
        "D6_document_preserves_nonnormative_firewall": (
            "document_status = nonnormative_successor_draft" in document
            and "changes_parent_problem = false" in document
            and "This draft does not amend v0.1." in document
            and "This is a nonnormative problem-definition draft." in document
        ),
        "W0_witness_is_exact_and_certified": (
            witness.get("schema_version")
            == "asmp3_protocol_quantifier_v0_7"
            and witness.get("status") == "exact_quantifier_fork"
            and witness.get("certified") is True
            and witness.get("experiment_id")
            == draft.get("motivation_experiment")
        ),
        "W1_frozen_branch_matches_fixed_target": (
            witness.get("frozen_encoding_branch", {}).get("asymptotic_gap")
            == fixed_mode.get("v0_7_witness_gap")
            and witness.get("frozen_encoding_branch", {}).get(
                "asymptotic_gap"
            )
            == "(3/5)^d -> 0"
        ),
        "W2_vector_branch_matches_admissible_target": (
            witness.get("existential_encoding_branch", {}).get("constant_gap")
            == admissible_mode.get("v0_7_vector_protocol_gap")
            and witness.get("existential_encoding_branch", {}).get(
                "constant_gap"
            )
            == "3/5"
        ),
        "W3_witness_gates_and_resource_ledger_pass": (
            bool(witness.get("gates"))
            and all(witness["gates"].values())
            and bool(witness.get("resource_rows"))
            and all(
                row.get("both_are_polylog_in_prover_budget") is True
                for row in witness["resource_rows"]
            )
        ),
    }

    return {
        "schema_version": "asmp3_typed_successor_validation_v0_2",
        "draft_status": draft.get("status"),
        "witness_experiment_id": witness.get("experiment_id"),
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This validation establishes internal type consistency and exact "
            "alignment with the v0.7 witness only. It does not adopt the "
            "draft, amend ASMP-3 v0.1, or resolve either characterization."
        ),
    }


def main() -> None:
    result = validate()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not result["passed"]:
        failed = [
            name
            for name, passed in result["checks"].items()
            if not passed
        ]
        raise SystemExit(f"typed successor validation failed: {failed}")
    print(
        "ASMP-3 typed successor validation passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
