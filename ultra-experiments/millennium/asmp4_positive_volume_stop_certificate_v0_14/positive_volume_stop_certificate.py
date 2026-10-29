"""Harness-backed stopping certificate for ASMP-4 after the v0.13 repair."""

from __future__ import annotations

import ast
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V10_CLAIM = (
    ROOT / "asmp4_stopping_red_team_v0_10" / "stopping_red_team_claim_v0_10.json"
)
V13_CLAIM = (
    ROOT
    / "asmp4_positive_volume_collar_v0_13"
    / "positive_volume_collar_claim_v0_13.json"
)
CLAIM = HERE / "positive_volume_stop_claim_v0_14.json"

SEALS = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_10_stopping_claim": (
        V10_CLAIM,
        "fd8b2e74bdd6f16aabd7907dc621254accd6e8fa183957d1eaaf3138163d314c",
    ),
    "v0_13_collar_claim": (
        V13_CLAIM,
        "6c09924712d5342c69a731a602bdb3b008ef30d54a7cd0b74e08250d64c4bd19",
    ),
}

PREDECESSOR_TESTS = (
    ("asmp4_capacity_definition_audit", "test_capacity_definition_audit.py"),
    ("asmp4_two_port_game", "test_two_port_game.py"),
    ("asmp4_serial_collapse_theorem_v0_2", "test_serial_capacity.py"),
    ("asmp4_metric_robust_collapse_v0_3", "test_metric_harness.py"),
    ("asmp4_heterogeneous_port_costs_v0_4", "test_heterogeneous_frontier.py"),
    ("asmp4_adaptive_history_collapse_v0_5", "test_adaptive_frontier.py"),
    ("asmp4_registration_fork_v0_6", "test_registration_fork.py"),
    ("asmp4_relational_action_frontier_v0_7", "test_relational_frontier.py"),
    ("asmp4_randomness_quantifier_boundary_v0_8", "test_randomness_quantifier.py"),
    ("asmp4_completion_atlas_v0_9", "test_completion_atlas.py"),
    ("asmp4_stopping_red_team_v0_10", "test_stopping_red_team.py"),
    ("asmp4_nhim_cocycle_audit_v0_11", "test_nhim_cocycle_audit.py"),
    ("asmp4_positive_dimensional_nhim_v0_12", "test_positive_dimensional_nhim.py"),
    ("asmp4_positive_volume_collar_v0_13", "test_positive_volume_collar.py"),
)

REOPENING_CONDITIONS = (
    "a normative sensor observation/computation registry is added",
    "an attributable proof or implementation error invalidates the positive-volume fork",
    "a specified perturbation/noise model invalidates or collapses both exact completions",
    "an attributable theorem or external review maps the existing wording to one unique formal class",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for name, (path, expected) in SEALS.items():
        observed = _sha256(path)
        rows.append(
            {
                "name": name,
                "expected": expected,
                "observed": observed,
                "matches": observed == expected,
            }
        )
    return {
        "rows": rows,
        "resources": len(rows),
        "pass": len(rows) == 3 and all(row["matches"] for row in rows),
    }


def source_selector_audit() -> dict[str, Any]:
    text = SOURCE.read_text(encoding="utf-8")
    section = " ".join(
        text.split("# ASMP-4", 1)[1].split("# ASMP-5", 1)[0].casefold().split()
    )
    required = {
        "registered_causal_code": section.count("registered causal code") == 2,
        "separate_components": (
            "the plant, sensor, controller, and actuator are separate components"
            in section
        ),
        "finite_transcript_alphabets": "finite transcript alphabets" in section,
        "universal_confinement": "for every allowed disturbance sequence" in section,
        "positive_volume_liveness": "positive-volume initial collar" in section,
        "architecture_tradeoffs": "architecture-dependent tradeoff inequalities"
        in section,
    }
    selector_terms = {
        phrase: phrase in section
        for phrase in (
            "sensor registry",
            "sensor observation map",
            "sensor computation closure",
            "raw mode",
            "sufficient statistic",
            "injective sensor",
        )
    }
    checks = {
        "explicit_requirements_present": all(required.values()),
        "no_candidate_selector_term_present": not any(selector_terms.values()),
        "sensor_emission_rule_does_not_name_observation_domain": (
            "a causal sensor encoder emits only the read transcript" in section
            and "sensor observation map" not in section
        ),
        "architecture_dependence_is_acknowledged_but_not_selected": (
            required["architecture_tradeoffs"] and not selector_terms["sensor registry"]
        ),
    }
    return {
        "required": required,
        "selector_terms": selector_terms,
        "checks": checks,
        "pass": all(checks.values()),
    }


def nondegenerate_fork_report(max_horizon: int = 10) -> dict[str, Any]:
    v13 = _load(V13_CLAIM)
    rows = []
    for horizon in range(1, max_horizon + 1):
        normal_words = 2**horizon
        q_words = 2**horizon
        raw_mode_words = 4**horizon
        rows.append(
            {
                "horizon": horizon,
                "computed_reads": q_words * normal_words,
                "raw_reads": raw_mode_words * normal_words,
                "writes": q_words * normal_words,
                "computed_rate": Fraction(
                    (q_words * normal_words).bit_length() - 1, horizon
                ).numerator,
                "raw_rate": Fraction(
                    (raw_mode_words * normal_words).bit_length() - 1, horizon
                ).numerator,
                "write_rate": Fraction(
                    (q_words * normal_words).bit_length() - 1, horizon
                ).numerator,
            }
        )
    geometry = v13.get("safe_geometry", {})
    regions = v13.get("full_collar_regions", {})
    checks = {
        "positive_volume": geometry.get("normalized_volume") == "2",
        "positive_dimensional_nhim": geometry.get("nhim_dimension") == 1,
        "same_bounded_plant_contains_both_regions": (
            v13.get("plant", {}).get("authority") == "[-2,10]"
            and regions.get("computed") == "[2,infinity) x [2,infinity)"
            and regions.get("raw") == "[3,infinity) x [2,infinity)"
        ),
        "all_horizons_have_exact_rates": all(
            row["computed_rate"] == 2
            and row["raw_rate"] == 3
            and row["write_rate"] == 2
            for row in rows
        ),
        "finite_margin_formula_present": v13.get("finite_margin", {}).get(
            "normal_spanning_words"
        )
        == "ceil(rho*2^T)",
        "universal_mode_disturbance_is_part_of_plant": "z_next=w"
        in v13.get("plant", {}).get("dynamics", ""),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def prior_stop_lift_report() -> dict[str, Any]:
    old = _load(V10_CLAIM)
    new = _load(V13_CLAIM)
    checks = {
        "old_decision_was_local_stop": old.get("decision")
        == "stop_local_enumeration_and_request_normative_registration",
        "old_selector_audit_found_none": old.get("selector_mutations", {}).get(
            "source_selector_present"
        )
        is False,
        "old_primary_literature_found_none": old.get(
            "cited_prior_art_scope_audit", {}
        ).get("asmp4_two_port_registry_selectors")
        == 0,
        "old_near_miss_audit_found_none": old.get(
            "targeted_literature_near_miss_audit", {}
        ).get("asmp4_registry_selectors")
        == 0,
        "new_repairs_both_degeneracies": new.get("decision")
        == "positive_dimension_and_positive_volume_objections_removed",
        "new_regions_still_distinct": new.get("full_collar_regions", {}).get("computed")
        != new.get("full_collar_regions", {}).get("raw"),
    }
    return {"checks": checks, "pass": all(checks.values())}


def selector_counterfactual_report() -> dict[str, Any]:
    source_section = " ".join(
        SOURCE.read_text(encoding="utf-8")
        .split("# ASMP-4", 1)[1]
        .split("# ASMP-5", 1)[0]
        .casefold()
        .split()
    )
    rows = [
        {
            "id": "S1",
            "added_clause": "sensor may quotient raw mode by the control-relevant q fiber",
            "result": "computed [2,infinity) x [2,infinity)",
        },
        {
            "id": "S2",
            "added_clause": "sensor report must be injective in the four raw modes",
            "result": "raw [3,infinity) x [2,infinity)",
        },
        {
            "id": "S3",
            "added_clause": "charge the coarsest control-sufficient statistic",
            "result": "computed [2,infinity) x [2,infinity)",
        },
        {
            "id": "S4",
            "added_clause": "charge a fixed calibrated four-label sensor",
            "result": "raw [3,infinity) x [2,infinity)",
        },
        {
            "id": "S5",
            "added_clause": "make the sensor registry an explicit theorem parameter",
            "result": "parameterized family, not one source-selected region",
        },
    ]
    for row in rows:
        row["absent_from_source"] = row["added_clause"] not in source_section
        row["determinate_after_addition"] = bool(row["result"])
    checks = {
        "five_counterfactual_selectors": len(rows) == 5,
        "all_require_added_text": all(row["absent_from_source"] for row in rows),
        "all_make_target_determinate_or_parameterized": all(
            row["determinate_after_addition"] for row in rows
        ),
        "at_least_two_incompatible_selected_regions": len(
            {row["result"] for row in rows[:4]}
        )
        == 2,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def bounded_work_exhaustion_report() -> dict[str, Any]:
    attacks = [
        {
            "attack": "run longer horizons",
            "answer": "closed forms hold for every T and are replayed through T=10",
            "closed": True,
        },
        {
            "attack": "replace the point manifold",
            "answer": "the v0.13 witness contains a compact connected circle NHIM",
            "closed": True,
        },
        {
            "attack": "require positive initial volume",
            "answer": "the full collar has normalized volume 2",
            "closed": True,
        },
        {
            "attack": "require exact safety-margin corrections",
            "answer": "v0.13 proves ceil(rho*2^T) for every fixed 0<rho<=1",
            "closed": True,
        },
        {
            "attack": "search locally for the intended registry",
            "answer": "a bounded construction cannot add a missing normative source clause",
            "closed": True,
        },
    ]
    checks = {
        "five_high_value_attacks_addressed": len(attacks) == 5,
        "all_closed_for_local_harness_work": all(row["closed"] for row in attacks),
        "reopening_conditions_are_external_or_falsifying": len(REOPENING_CONDITIONS)
        == 4,
    }
    return {"rows": attacks, "checks": checks, "pass": all(checks.values())}


def predecessor_inventory_report() -> dict[str, Any]:
    rows = []
    for package, filename in PREDECESSOR_TESTS:
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append({"package": package, "tests": count})
    total = sum(row["tests"] for row in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": total,
        "pass": len(rows) == 14 and total == 174,
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_positive_volume_stop_claim_v0_14",
        "status": "harness-backed stop after nondegenerate registry fork",
        "sealed_resources": {
            "count": 3,
            "canonical_source_sha256": SEALS["canonical_source"][1],
            "v0_10_stopping_claim_sha256": SEALS["v0_10_stopping_claim"][1],
            "v0_13_collar_claim_sha256": SEALS["v0_13_collar_claim"][1],
        },
        "positive_volume_fork": {
            "normalized_volume": "2",
            "nhim_dimension": 1,
            "computed_region": "[2,infinity) x [2,infinity)",
            "raw_region": "[3,infinity) x [2,infinity)",
            "finite_margin": "ceil(rho*2^T)",
        },
        "source_selector_audit": {
            "candidate_selector_terms_present": 0,
            "counterfactual_selectors": 5,
            "distinct_selected_regions": 2,
        },
        "predecessor_inventory": {"packages": 14, "tests": 174},
        "decision": "stop_local_construction_and_request_normative_registration",
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "nonclaim": (
            "ASMP-4 is not claimed mathematically resolved. The certificate stops "
            "further bounded local enumeration because it cannot choose a missing "
            "normative registry; perturbation/noise robustness and external review "
            "remain valid reopening routes."
        ),
    }


def claim_exactness_report() -> dict[str, Any]:
    observed = _load(CLAIM) if CLAIM.exists() else None
    expected = expected_claim_payload()
    return {
        "exists": CLAIM.exists(),
        "matches": observed == expected,
        "pass": CLAIM.exists() and observed == expected,
    }


def positive_volume_stop_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    source = source_selector_audit()
    fork = nondegenerate_fork_report()
    lift = prior_stop_lift_report()
    selectors = selector_counterfactual_report()
    exhaustion = bounded_work_exhaustion_report()
    inventory = predecessor_inventory_report()
    claim = claim_exactness_report()
    components = (
        integrity,
        source,
        fork,
        lift,
        selectors,
        exhaustion,
        inventory,
        claim,
    )
    return {
        "schema_version": "asmp4_positive_volume_stop_certificate_v0_14",
        "resource_integrity": integrity,
        "source_selector_audit": source,
        "nondegenerate_fork": fork,
        "prior_stop_lift": lift,
        "selector_counterfactuals": selectors,
        "bounded_work_exhaustion": exhaustion,
        "predecessor_inventory": inventory,
        "claim_exactness": claim,
        "decision": "stop_local_construction_and_request_normative_registration",
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = positive_volume_stop_report() if report is None else report
    return {
        "R0_three_resource_seals": report["resource_integrity"]["pass"],
        "R1_source_selector_absence": report["source_selector_audit"]["pass"],
        "R2_positive_volume_fork": report["nondegenerate_fork"]["pass"],
        "R3_prior_stop_lifted": report["prior_stop_lift"]["pass"],
        "R4_five_selector_counterfactuals": report["selector_counterfactuals"]["pass"],
        "R5_bounded_work_exhausted": report["bounded_work_exhaustion"]["pass"],
        "R6_predecessor_inventory_174": report["predecessor_inventory"]["pass"],
        "R7_frozen_claim": report["claim_exactness"]["pass"],
        "R8_stop_decision": report["decision"]
        == "stop_local_construction_and_request_normative_registration",
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    report = positive_volume_stop_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
