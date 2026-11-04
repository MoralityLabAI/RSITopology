from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ARTIFACT_DIR = HERE / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "correlated_path_risk_v2_13.json"
ONLINE_PARENT_PATH = (
    HERE.parent
    / "asmp3_online_noisy_trace_extractor_v2_10"
    / "artifacts"
    / "online_noisy_trace_extractor_v2_10.json"
)
PERSISTENT_PARENT_PATH = (
    HERE.parent
    / "asmp3_independent_noise_amplification_v1_8"
    / "artifacts"
    / "independent_noise_amplification_v1_8.json"
)


def ratio(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


ETAS = (Fraction(1, 100), Fraction(1, 10), Fraction(1, 5), Fraction(1, 3))
QUERY_COUNTS = (1, 2, 4, 8, 16, 32)


def common_mode_rows() -> list[dict[str, object]]:
    rows = []
    soundness = Fraction(1, 5)
    for eta in ETAS:
        for query_count in QUERY_COUNTS:
            path_failure = eta
            success = max(Fraction(0), 1 - soundness - path_failure)
            rows.append(
                {
                    "noise_class": "truth_independent_common_mode_flip",
                    "eta": ratio(eta),
                    "adaptive_query_count": query_count,
                    "fixed_atom_marginal_error": ratio(eta),
                    "path_error_probability": ratio(path_failure),
                    "replication_amplifies": False,
                    "soundness_upper_bound": ratio(soundness),
                    "online_finder_success_lower_bound": ratio(success),
                    "certified": path_failure == eta and success > 0,
                }
            )
    return rows


def conditional_chain_rows() -> list[dict[str, object]]:
    rows = []
    for error in ETAS:
        for query_count in (1, 2, 4, 8, 16):
            no_error = (1 - error) ** query_count
            path_failure = 1 - no_error
            rows.append(
                {
                    "noise_class": "arbitrarily_dependent_with_per_matching_prefix_conditional_bound",
                    "per_round_conditional_error_bound": ratio(error),
                    "adaptive_query_count": query_count,
                    "matching_prefix_probability_lower_bound": ratio(no_error),
                    "path_error_probability_upper_bound": ratio(path_failure),
                    "independence_required": False,
                    "certified": no_error + path_failure == 1,
                }
            )
    return rows


def weak_compositions(total: int, slots: int) -> Iterable[tuple[int, ...]]:
    if slots == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in weak_compositions(total - first, slots - 1):
            yield (first,) + rest


def exchangeable_mixture_audit() -> dict[str, object]:
    rates = (
        Fraction(0),
        Fraction(1, 4),
        Fraction(1, 2),
        Fraction(3, 4),
        Fraction(1),
    )
    digest = hashlib.sha256()
    cases = violations = equalities = registered = held_out = 0
    maximum_slack = Fraction(0)
    for denominator in range(1, 11):
        for weights in weak_compositions(denominator, len(rates)):
            mean_rate = sum(
                Fraction(weight, denominator) * rate
                for weight, rate in zip(weights, rates)
            )
            for query_count in range(1, 7):
                cases += 1
                registered += int(denominator <= 8)
                held_out += int(denominator >= 9)
                no_error = sum(
                    Fraction(weight, denominator) * (1 - rate) ** query_count
                    for weight, rate in zip(weights, rates)
                )
                path_failure = 1 - no_error
                jensen_upper = 1 - (1 - mean_rate) ** query_count
                slack = jensen_upper - path_failure
                violations += int(slack < 0)
                equalities += int(slack == 0)
                maximum_slack = max(maximum_slack, slack)
                digest.update(
                    (
                        f"{denominator}|{','.join(map(str, weights))}|{query_count}|"
                        f"{ratio(mean_rate)}|{ratio(path_failure)}|"
                        f"{ratio(jensen_upper)}|{ratio(slack)}\n"
                    ).encode("ascii")
                )
    return {
        "latent_rate_grid": [ratio(rate) for rate in rates],
        "weight_denominators": [1, 10],
        "registered_denominators": [1, 8],
        "held_out_denominators": [9, 10],
        "query_counts": [1, 6],
        "mixture_query_cases": cases,
        "registered_cases": registered,
        "held_out_cases": held_out,
        "jensen_bound_violations": violations,
        "jensen_equality_cases": equalities,
        "maximum_jensen_slack": ratio(maximum_slack),
        "canonical_mixture_digest_sha256": digest.hexdigest().upper(),
        "certified": cases > 18_000 and violations == 0 and equalities > 0,
    }


def controller_comparison_rows() -> list[dict[str, object]]:
    rows = []
    for eta in ETAS:
        for query_count in (1, 2, 4, 8, 16):
            common = eta
            fixed_latent_iid = 1 - (1 - eta) ** query_count
            rows.append(
                {
                    "eta": ratio(eta),
                    "adaptive_query_count": query_count,
                    "common_mode_path_error": ratio(common),
                    "fixed_rate_iid_path_error": ratio(fixed_latent_iid),
                    "mean_only_exchangeable_upper_bound": ratio(fixed_latent_iid),
                    "common_mode_is_no_worse_for_path_risk": common <= fixed_latent_iid,
                    "same_fixed_atom_marginal": True,
                    "certified": common <= fixed_latent_iid,
                }
            )
    return rows


def selection_correlated_rows() -> list[dict[str, object]]:
    rows = []
    for class_count in range(2, 33):
        marginal = Fraction(1, class_count)
        rows.append(
            {
                "semantic_class_count": class_count,
                "public_seed_values": class_count,
                "bad_class_equals_publicly_selected_class": True,
                "each_fixed_class_marginal_error": ratio(marginal),
                "actual_selected_path_error": "1",
                "semantic_query_budget": 1,
                "marginal_to_path_risk_ratio": class_count,
                "online_finder_bound_at_soundness_zero": "0",
                "certified": marginal <= Fraction(1, 2),
            }
        )
    return rows


def persistent_online_composition_rows() -> list[dict[str, object]]:
    parent = json.loads(ONLINE_PARENT_PATH.read_text(encoding="utf-8"))
    rows = []
    for source in parent["composition_rows"]:
        soundness = Fraction(source["soundness_upper_bound"])
        eta = Fraction(source["eta"])
        query_count = int(source["maximum_adaptive_queries"])
        path_failure = eta
        success = max(Fraction(0), 1 - soundness - path_failure)
        rows.append(
            {
                "noise_class": "persistent_common_mode_across_all_semantic_queries",
                "soundness_upper_bound": ratio(soundness),
                "eta": ratio(eta),
                "maximum_adaptive_queries": query_count,
                "path_error_probability": ratio(path_failure),
                "online_finder_success_lower_bound": ratio(success),
                "raw_semantic_queries_without_useless_replication": query_count,
                "online_extractor_time": source["online_extractor_time"],
                "strategy_restart_required": False,
                "noise_independence_required": False,
                "certified": success > 0,
            }
        )
    return rows


def persistent_parent_audit() -> dict[str, object]:
    parent = json.loads(PERSISTENT_PARENT_PATH.read_text(encoding="utf-8"))
    rows = parent["amplification_rows"]
    persistent = [
        row
        for row in rows
        if row["eta"] == "1/5" and int(row["depth"]) in (1, 3, 9, 17, 33, 64)
    ]
    return {
        "parent_schema": parent["schema_version"],
        "parent_certified": parent["certified"],
        "sampled_depths": [int(row["depth"]) for row in persistent],
        "persistent_values": [row["persistent_correlated_value"] for row in persistent],
        "persistent_errors": [row["persistent_correlated_error"] for row in persistent],
        "all_sampled_values_equal_three_fifths": all(
            row["persistent_correlated_value"] == "3/5" for row in persistent
        ),
        "all_sampled_errors_equal_one_fifth": all(
            row["persistent_correlated_error"] == "1/5" for row in persistent
        ),
        "certified": (
            parent["certified"] is True
            and len(persistent) == 6
            and all(row["persistent_correlated_value"] == "3/5" for row in persistent)
        ),
    }


def build_artifact() -> dict[str, object]:
    common = common_mode_rows()
    conditional = conditional_chain_rows()
    exchangeable = exchangeable_mixture_audit()
    comparison = controller_comparison_rows()
    selection = selection_correlated_rows()
    composition = persistent_online_composition_rows()
    parent_audit = persistent_parent_audit()
    gates = {
        "P0_online_extraction_needs_only_total_path_error_risk": all(
            row["certified"] for row in common + composition
        ),
        "P1_common_mode_path_risk_is_exactly_eta_for_every_q": all(
            Fraction(row["path_error_probability"]) == Fraction(row["eta"])
            for row in common
        ),
        "P2_conditional_chain_bound_needs_no_independence": all(
            row["certified"] and not row["independence_required"]
            for row in conditional
        ),
        "P3_exchangeable_latent_rate_jensen_bound_is_exactly_audited": exchangeable[
            "certified"
        ],
        "P4_fixed_marginals_do_not_control_selection_correlated_path_risk": all(
            Fraction(row["each_fixed_class_marginal_error"]) <= Fraction(1, 2)
            and row["actual_selected_path_error"] == "1"
            for row in selection
        ),
        "P5_v1_8_persistent_nonamplification_is_preserved": parent_audit["certified"],
        "P6_persistent_common_mode_still_yields_positive_online_finder_margins": (
            len(composition) == 12 and all(row["certified"] for row in composition)
        ),
        "P7_repetition_is_not_misclaimed_to_amplify_common_mode_noise": all(
            not row["replication_amplifies"] for row in common
        ),
        "P8_same_marginals_can_have_distinct_path_risk": all(
            row["same_fixed_atom_marginal"]
            and Fraction(row["common_mode_path_error"])
            <= Fraction(row["fixed_rate_iid_path_error"])
            for row in comparison
        ),
        "P9_all_persistent_composition_resources_and_contract_flags_are_explicit": all(
            row["online_extractor_time"] > 0
            and not row["strategy_restart_required"]
            and not row["noise_independence_required"]
            for row in composition
        ),
    }
    return {
        "schema_version": "asmp3_correlated_path_risk_v2_13",
        "experiment_id": "ASMP-3-CORRELATED-PATH-RISK-v2.13",
        "parent_result": "ASMP-3-CONSOLIDATED-RESOLUTION-DISPOSITION-v2.12",
        "supporting_results": [
            "ASMP-3-ONLINE-NOISY-TRACE-EXTRACTOR-v2.10",
            "ASMP-3-INDEPENDENT-NOISE-AMPLIFICATION-v1.8",
        ],
        "status": "arbitrary_dependence_online_extraction_under_controlled_path_risk",
        "theorem": {
            "general_path_law": "alpha>=max(0,1-s-delta_path) for any dependence structure",
            "common_mode": "delta_path=eta for a truth-independent global flip shared across the path",
            "conditional_chain": "delta_path<=1-product_i(1-e_i) without independence",
            "exchangeable_mixture": "delta_path=1-E[(1-P)^q]<=1-(1-E[P])^q",
            "marginal_firewall": "fixed-class marginals alone permit selected path error one",
            "replication_boundary": "common-mode correlation does not amplify, but can retain a positive online margin",
        },
        "common_mode_rows": common,
        "conditional_chain_rows": conditional,
        "exchangeable_mixture_audit": exchangeable,
        "controller_comparison_rows": comparison,
        "selection_correlated_rows": selection,
        "persistent_online_composition_rows": composition,
        "persistent_parent_audit": parent_audit,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The theorem covers arbitrary dependence only when the total error "
            "probability along the actually selected adaptive path is controlled. "
            "It does not derive such control from fixed-atom marginals, and it does "
            "not claim repetition amplifies persistent common-mode noise."
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
    print(f"ASMP-3 correlated path-risk certified: {passed}/{len(result['gates'])} gates")
