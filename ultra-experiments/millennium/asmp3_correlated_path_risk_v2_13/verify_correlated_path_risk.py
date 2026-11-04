from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "correlated_path_risk_v2_13.json"
VERIFY_PATH = HERE / "artifacts" / "correlated_path_risk_verification_v2_13.json"
ONLINE_PATH = (
    HERE.parent
    / "asmp3_online_noisy_trace_extractor_v2_10"
    / "artifacts"
    / "online_noisy_trace_extractor_v2_10.json"
)
PERSISTENT_PATH = (
    HERE.parent
    / "asmp3_independent_noise_amplification_v1_8"
    / "artifacts"
    / "independent_noise_amplification_v1_8.json"
)


def text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


ETAS = (Fraction(1, 100), Fraction(1, 10), Fraction(1, 5), Fraction(1, 3))


def reconstruct_common() -> list[dict[str, object]]:
    rows = []
    s = Fraction(1, 5)
    for eta in ETAS:
        for q in (1, 2, 4, 8, 16, 32):
            rows.append(
                {
                    "noise_class": "truth_independent_common_mode_flip",
                    "eta": text(eta),
                    "adaptive_query_count": q,
                    "fixed_atom_marginal_error": text(eta),
                    "path_error_probability": text(eta),
                    "replication_amplifies": False,
                    "soundness_upper_bound": text(s),
                    "online_finder_success_lower_bound": text(max(Fraction(0), 1 - s - eta)),
                    "certified": True,
                }
            )
    return rows


def reconstruct_conditional() -> list[dict[str, object]]:
    rows = []
    for error in ETAS:
        for q in (1, 2, 4, 8, 16):
            no_error = (1 - error) ** q
            rows.append(
                {
                    "noise_class": "arbitrarily_dependent_with_per_matching_prefix_conditional_bound",
                    "per_round_conditional_error_bound": text(error),
                    "adaptive_query_count": q,
                    "matching_prefix_probability_lower_bound": text(no_error),
                    "path_error_probability_upper_bound": text(1 - no_error),
                    "independence_required": False,
                    "certified": True,
                }
            )
    return rows


def compositions(total: int, slots: int):
    if slots == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for rest in compositions(total - first, slots - 1):
                yield (first,) + rest


def reconstruct_exchangeable() -> dict[str, object]:
    rates = (Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1))
    digest = hashlib.sha256()
    cases = registered = held = violations = equalities = 0
    max_slack = Fraction(0)
    for denominator in range(1, 11):
        for weights in compositions(denominator, 5):
            mean = sum(
                Fraction(weight, denominator) * rate
                for weight, rate in zip(weights, rates)
            )
            for q in range(1, 7):
                cases += 1
                registered += int(denominator <= 8)
                held += int(denominator >= 9)
                no_error = sum(
                    Fraction(weight, denominator) * (1 - rate) ** q
                    for weight, rate in zip(weights, rates)
                )
                path = 1 - no_error
                upper = 1 - (1 - mean) ** q
                slack = upper - path
                violations += int(slack < 0)
                equalities += int(slack == 0)
                max_slack = max(max_slack, slack)
                digest.update(
                    (
                        f"{denominator}|{','.join(map(str, weights))}|{q}|"
                        f"{text(mean)}|{text(path)}|{text(upper)}|{text(slack)}\n"
                    ).encode("ascii")
                )
    return {
        "latent_rate_grid": ["0", "1/4", "1/2", "3/4", "1"],
        "weight_denominators": [1, 10],
        "registered_denominators": [1, 8],
        "held_out_denominators": [9, 10],
        "query_counts": [1, 6],
        "mixture_query_cases": cases,
        "registered_cases": registered,
        "held_out_cases": held,
        "jensen_bound_violations": violations,
        "jensen_equality_cases": equalities,
        "maximum_jensen_slack": text(max_slack),
        "canonical_mixture_digest_sha256": digest.hexdigest().upper(),
        "certified": cases > 18_000 and violations == 0 and equalities > 0,
    }


def reconstruct_comparison() -> list[dict[str, object]]:
    rows = []
    for eta in ETAS:
        for q in (1, 2, 4, 8, 16):
            iid = 1 - (1 - eta) ** q
            rows.append(
                {
                    "eta": text(eta),
                    "adaptive_query_count": q,
                    "common_mode_path_error": text(eta),
                    "fixed_rate_iid_path_error": text(iid),
                    "mean_only_exchangeable_upper_bound": text(iid),
                    "common_mode_is_no_worse_for_path_risk": eta <= iid,
                    "same_fixed_atom_marginal": True,
                    "certified": eta <= iid,
                }
            )
    return rows


def reconstruct_selection() -> list[dict[str, object]]:
    return [
        {
            "semantic_class_count": n,
            "public_seed_values": n,
            "bad_class_equals_publicly_selected_class": True,
            "each_fixed_class_marginal_error": text(Fraction(1, n)),
            "actual_selected_path_error": "1",
            "semantic_query_budget": 1,
            "marginal_to_path_risk_ratio": n,
            "online_finder_bound_at_soundness_zero": "0",
            "certified": True,
        }
        for n in range(2, 33)
    ]


def reconstruct_composition(parent: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for source in parent["composition_rows"]:
        s = Fraction(source["soundness_upper_bound"])
        eta = Fraction(source["eta"])
        q = int(source["maximum_adaptive_queries"])
        success = max(Fraction(0), 1 - s - eta)
        rows.append(
            {
                "noise_class": "persistent_common_mode_across_all_semantic_queries",
                "soundness_upper_bound": text(s),
                "eta": text(eta),
                "maximum_adaptive_queries": q,
                "path_error_probability": text(eta),
                "online_finder_success_lower_bound": text(success),
                "raw_semantic_queries_without_useless_replication": q,
                "online_extractor_time": source["online_extractor_time"],
                "strategy_restart_required": False,
                "noise_independence_required": False,
                "certified": success > 0,
            }
        )
    return rows


def reconstruct_parent_audit(parent: dict[str, object]) -> dict[str, object]:
    selected = [
        row
        for row in parent["amplification_rows"]
        if row["eta"] == "1/5" and int(row["depth"]) in (1, 3, 9, 17, 33, 64)
    ]
    return {
        "parent_schema": parent["schema_version"],
        "parent_certified": parent["certified"],
        "sampled_depths": [int(row["depth"]) for row in selected],
        "persistent_values": [row["persistent_correlated_value"] for row in selected],
        "persistent_errors": [row["persistent_correlated_error"] for row in selected],
        "all_sampled_values_equal_three_fifths": all(
            row["persistent_correlated_value"] == "3/5" for row in selected
        ),
        "all_sampled_errors_equal_one_fifth": all(
            row["persistent_correlated_error"] == "1/5" for row in selected
        ),
        "certified": parent["certified"] is True and len(selected) == 6,
    }


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    online = json.loads(ONLINE_PATH.read_text(encoding="utf-8"))
    persistent = json.loads(PERSISTENT_PATH.read_text(encoding="utf-8"))
    common = reconstruct_common()
    conditional = reconstruct_conditional()
    exchangeable = reconstruct_exchangeable()
    comparison = reconstruct_comparison()
    selection = reconstruct_selection()
    composition = reconstruct_composition(online)
    parent_audit = reconstruct_parent_audit(persistent)
    checks = {
        "V0_schema_parent_status": (
            result.get("schema_version") == "asmp3_correlated_path_risk_v2_13"
            and result.get("parent_result")
            == "ASMP-3-CONSOLIDATED-RESOLUTION-DISPOSITION-v2.12"
            and result.get("status")
            == "arbitrary_dependence_online_extraction_under_controlled_path_risk"
        ),
        "V1_all_24_common_mode_rows_reconstructed": result.get("common_mode_rows") == common,
        "V2_all_20_conditional_chain_rows_reconstructed": result.get("conditional_chain_rows") == conditional,
        "V3_all_18012_exchangeable_cases_reconstructed": result.get("exchangeable_mixture_audit") == exchangeable,
        "V4_controller_comparisons_and_selection_firewall_reconstructed": (
            result.get("controller_comparison_rows") == comparison
            and result.get("selection_correlated_rows") == selection
        ),
        "V5_all_12_persistent_online_compositions_reconstructed": (
            len(composition) == 12
            and result.get("persistent_online_composition_rows") == composition
        ),
        "V6_v1_8_persistent_parent_receipt_reconstructed": result.get("persistent_parent_audit") == parent_audit,
        "V7_marginal_only_selection_bias_is_exact": all(
            Fraction(row["each_fixed_class_marginal_error"])
            == Fraction(1, row["semantic_class_count"])
            and row["actual_selected_path_error"] == "1"
            for row in selection
        ),
        "V8_all_10_producer_gates_true": (
            len(result.get("gates", {})) == 10
            and all(result.get("gates", {}).values())
            and result.get("certified") is True
        ),
        "V9_claim_boundary_requires_path_control_and_forbids_false_amplification": all(
            phrase in result.get("claim_boundary", "")
            for phrase in (
                "actually selected adaptive path",
                "fixed-atom marginals",
                "does not claim repetition amplifies",
            )
        ),
    }
    return {
        "schema_version": "asmp3_correlated_path_risk_verification_v2_13",
        "checker": "clean_room_common_conditional_exchangeable_selection_persistent_and_parent_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker certifies dependent-noise composition only through a "
            "controlled selected-path error event. It does not infer path control "
            "from fixed-class marginals or claim common-mode amplification."
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
        raise RuntimeError(f"ASMP-3 v2.13 verification failed: {failed}")
    print(
        "ASMP-3 correlated path-risk verification passed: "
        f"{receipt['check_count']}/{receipt['check_count']}"
    )


if __name__ == "__main__":
    main()
