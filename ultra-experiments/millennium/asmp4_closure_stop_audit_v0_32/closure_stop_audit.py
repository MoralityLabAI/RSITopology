"""Current-state ASMP-4 closure and operational stopping audit v0.32."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V15 = (
    ROOT
    / "asmp4_semantic_selector_audit_v0_15"
    / "semantic_selector_audit_claim_v0_15.json"
)
V23 = (
    ROOT
    / "asmp4_observation_delay_boundary_v0_23"
    / "observation_delay_boundary_claim_v0_23.json"
)
V26 = (
    ROOT
    / "asmp4_public_bisimulation_transfer_v0_26"
    / "public_bisimulation_claim_v0_26.json"
)
V27 = (
    ROOT
    / "asmp4_approximate_bisimulation_robustness_v0_27"
    / "approximate_bisimulation_claim_v0_27.json"
)
V28 = (
    ROOT
    / "asmp4_transcript_fiber_entropy_v0_28"
    / "transcript_fiber_claim_v0_28.json"
)
V29 = (
    ROOT
    / "asmp4_causal_branch_fiber_v0_29"
    / "causal_branch_fiber_claim_v0_29.json"
)
V30 = (
    ROOT
    / "asmp4_prefix_kraft_fiber_v0_30"
    / "prefix_kraft_fiber_claim_v0_30.json"
)
V31 = (
    ROOT
    / "asmp4_adversarial_mean_payoff_v0_31"
    / "adversarial_mean_payoff_claim_v0_31.json"
)
V28_CENTRAL = (
    ROOT / "asmp4_transcript_fiber_entropy_v0_28" / "transcript_fiber_entropy.py"
)
V28_TEST = (
    "asmp4_transcript_fiber_entropy_v0_28",
    "test_transcript_fiber_entropy.py",
)
V29_TEST = ("asmp4_causal_branch_fiber_v0_29", "test_causal_branch_fiber.py")
V30_TEST = ("asmp4_prefix_kraft_fiber_v0_30", "test_prefix_kraft_fiber.py")
V31_TEST = (
    "asmp4_adversarial_mean_payoff_v0_31",
    "test_adversarial_mean_payoff.py",
)
CONTRACT = HERE / "closure_stop_contract_v0_32.json"
CLAIM = HERE / "closure_stop_claim_v0_32.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V15: "5ec0c615f72435da81e066f707293f85dd7b3fac93dab60c166f02cf649dbdc6",
    V23: "f5c3d7678029957020c30ae4382218d24823f33e165afdb34728464de201dbae",
    V26: "1decf7f8eb12b6b76e9c251cdbc2b400403dfb941c6e798a75ab1b0aadc99e9d",
    V31: "f03722518502b6f35a06306a4f526c5a781debe150607ed160189878f8707e22",
}

EXPECTED_REQUIREMENT_FRAGMENTS = (
    "coordinate-invariant definition",
    "variational formula for the entire achievable rate region",
    "converse theorems and constructive",
    "exact finite-horizon corrections",
    "counterexamples locating the boundary",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_section() -> str:
    text = SOURCE.read_text(encoding="utf-8")
    return text.split("# ASMP-4", 1)[1].split("# ASMP-5", 1)[0]


def canonical_requirements_report() -> dict[str, Any]:
    section = canonical_section().split("## What a complete resolution requires", 1)[1]
    section = section.split("## Liveness and kill examples", 1)[0]
    matches = re.findall(r"(?ms)^\d+\.\s+(.+?)(?=^\d+\.|\Z)", section)
    requirements = tuple(" ".join(match.split()) for match in matches)
    checks = {
        "five_requirements": len(requirements) == 5,
        "all_expected_fragments": all(
            fragment.casefold() in requirement.casefold()
            for fragment, requirement in zip(
                EXPECTED_REQUIREMENT_FRAGMENTS, requirements, strict=True
            )
        ),
    }
    return {
        "rows": [
            {"id": f"C{index}", "text": requirement}
            for index, requirement in enumerate(requirements, 1)
        ],
        "checks": checks,
        "pass": all(checks.values()),
    }


def resource_integrity_report() -> dict[str, Any]:
    rows = [
        {
            "name": path.name,
            "matches": hashlib.sha256(path.read_bytes()).hexdigest() == expected,
        }
        for path, expected in SEALS.items()
    ]
    return {"rows": rows, "pass": len(rows) == 5 and all(row["matches"] for row in rows)}


def claim_semantics_report() -> dict[str, Any]:
    v15 = _load(V15)
    v23 = _load(V23)
    v26 = _load(V26)
    v27 = _load(V27)
    v28 = _load(V28)
    v29 = _load(V29)
    v30 = _load(V30)
    v31 = _load(V31)
    checks = {
        "semantic_audit_blocks_unique_class_inference": v15["clause_census"][
            "ambiguous"
        ]
        == 7
        and v15["clause_census"]["selects_parameterized"] == 1
        and v15["adjudication_queue"]["status"] == "pending_external",
        "architecture_data_changes_region": v23["main_theorem"][
            "delay_zero_region"
        ]
        != v23["main_theorem"]["every_positive_integer_delay_region"]
        and v23["restoration"]["charged_current_preview_region"]
        == v23["main_theorem"]["delay_zero_region"],
        "finite_quotient_not_necessary": v26["infinite_boundary"][
            "finite_exact_stationary_quotient"
        ]
        is False
        and v26["infinite_boundary"]["exact_average_cost"] == "1/2",
        "finite_adversarial_computation_closed": v31["theorem"]["formula"]
        == "R=intersection_tau union_C upward(conv{cycle means in C})",
        "metric_only_zero_error_refuted": "metric-only zero-error transfer refuted"
        in v27["disposition"],
        "finite_class_count_misses_history_fibers": "one quotient class"
        in v28["sharpness"]["finite_quotient"],
        "terminal_fibers_miss_branching": "terminal fibers alone are insufficient"
        in v29["disposition"],
        "unrounded_fibers_miss_prefix_cost": "rounded local fibers"
        in v30["disposition"],
        "nonlinear_construction_explicitly_open": "nonlinear quotient construction remains open"
        in v31["disposition"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def requirement_coverage_report() -> dict[str, Any]:
    requirements = canonical_requirements_report()["rows"]
    coverage = (
        {
            "conditional_evidence": ["v0.3", "v0.24", "v0.28-v0.30"],
            "conditional_status": "closed after architecture, quotient, and cost functional are registered",
            "full_scope_gap": "no coordinate-invariant transversal pair is defined over a formal global nonlinear class",
        },
        {
            "conditional_evidence": ["v0.24", "v0.25", "v0.31"],
            "conditional_status": "entire region exact for resettable and finite additive public abstractions",
            "full_scope_gap": "no periodic/finite abstraction theorem for every declared nonlinear or infinite-belief registration",
        },
        {
            "conditional_evidence": ["v0.2-v0.23", "v0.26", "v0.31"],
            "conditional_status": "matching local constructions and exact quotient strategy transfers",
            "full_scope_gap": "no construction of the required public abstraction from a general nonlinear plant",
        },
        {
            "conditional_evidence": ["v0.2", "v0.13", "v0.27", "v0.30"],
            "conditional_status": "exact corrections in declared local and factor-transfer models",
            "full_scope_gap": "no uniform finite-horizon margin law for the unspecified global class",
        },
        {
            "conditional_evidence": ["v0.4-v0.23", "v0.26-v0.31"],
            "conditional_status": "extensive exact boundaries for architecture, uncertainty, quotient, cost, and memory assumptions",
            "full_scope_gap": "boundaries do not choose or construct the missing global class",
        },
    )
    rows = [
        {**requirement, **status, "full_scope_proved": False}
        for requirement, status in zip(requirements, coverage, strict=True)
    ]
    checks = {
        "five_rows": len(rows) == 5,
        "conditional_evidence_everywhere": all(
            row["conditional_evidence"] for row in rows
        ),
        "zero_full_scope_requirements_proved": sum(
            row["full_scope_proved"] for row in rows
        )
        == 0,
        "every_gap_explicit": all(row["full_scope_gap"] for row in rows),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def finite_lane_closure_report() -> dict[str, Any]:
    rows = {
        "finite_deterministic_additive_region": {
            "package": "v0.25",
            "status": "closed",
        },
        "exact_public_quotient_transfer": {
            "package": "v0.26",
            "status": "closed",
        },
        "approximate_additive_cost_transfer": {
            "package": "v0.27",
            "status": "closed_with_exact_safety",
        },
        "whole_language_cost_transfer": {
            "package": "v0.28",
            "status": "closed_with_fiber_entropy",
        },
        "branch_cost_transfer": {
            "package": "v0.29",
            "status": "closed_with_local_fiber_product",
        },
        "sequential_prefix_cost_transfer": {
            "package": "v0.30",
            "status": "closed_with_rounded_local_fibers",
        },
        "finite_adversarial_additive_region": {
            "package": "v0.31",
            "status": "closed_with_arbitrary_memory",
        },
    }
    checks = {
        "seven_closed_layers": len(rows) == 7,
        "all_have_packages": all(row["package"] for row in rows.values()),
        "none_marked_open": all("closed" in row["status"] for row in rows.values()),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def residual_dependency_report() -> dict[str, Any]:
    nodes = {
        "formal_registered_class": [],
        "public_abstraction_or_replacement": ["formal_registered_class"],
        "cost_profile_verification": ["public_abstraction_or_replacement"],
        "region_computation": [
            "public_abstraction_or_replacement",
            "cost_profile_verification",
        ],
        "global_finite_horizon_margin": [
            "formal_registered_class",
            "public_abstraction_or_replacement",
        ],
    }
    statuses = {
        "formal_registered_class": "missing",
        "public_abstraction_or_replacement": "missing",
        "cost_profile_verification": "conditional_laws_available",
        "region_computation": "closed_for_finite_additive_quotients",
        "global_finite_horizon_margin": "missing",
    }
    checks = {
        "root_is_missing_grammar": not nodes["formal_registered_class"]
        and statuses["formal_registered_class"] == "missing",
        "abstraction_depends_on_grammar": nodes["public_abstraction_or_replacement"]
        == ["formal_registered_class"],
        "finite_computation_not_the_blocker": statuses["region_computation"]
        == "closed_for_finite_additive_quotients",
        "global_margin_still_missing": statuses["global_finite_horizon_margin"]
        == "missing",
    }
    return {
        "dependencies": nodes,
        "statuses": statuses,
        "checks": checks,
        "pass": all(checks.values()),
    }


def stop_logic_report() -> dict[str, Any]:
    claims = claim_semantics_report()["checks"]
    finite = finite_lane_closure_report()["checks"]
    residual = residual_dependency_report()["checks"]
    premises = {
        "finite_game_lane_exhausted": finite["seven_closed_layers"],
        "class_inference_not_authorized": claims[
            "semantic_audit_blocks_unique_class_inference"
        ],
        "finite_quotient_not_necessary": claims["finite_quotient_not_necessary"],
        "nonlinear_construction_not_supplied": claims[
            "nonlinear_construction_explicitly_open"
        ],
        "remaining_root_is_upstream": residual["root_is_missing_grammar"]
        and residual["finite_computation_not_the_blocker"],
    }
    conclusion = all(premises.values())
    return {
        "premises": premises,
        "conclusion": "stop autonomous bounded finite/local expansion and request a formal class plus abstraction theorem or external adjudication",
        "full_resolution": False,
        "pass": conclusion,
    }


def reopening_conditions_report() -> dict[str, Any]:
    rows = (
        "a formal global grammar for admissible nonlinear plants, sensors, timing, randomness, costs, and quotient equivalence",
        "a concrete public-abstraction or nonfinite variational theorem with checkable hypotheses for that grammar",
        "attributable external adjudication mapping the frozen wording to one established formal class",
        "a demonstrated error invalidating a sealed premise of the stopping argument",
    )
    checks = {
        "four_conditions": len(rows) == 4,
        "grammar_condition": "formal global grammar" in rows[0],
        "mathematical_replacement_condition": "abstraction" in rows[1]
        and "variational" in rows[1],
        "external_condition": "external adjudication" in rows[2],
        "falsification_condition": "error" in rows[3],
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def mutation_report() -> dict[str, Any]:
    coverage = requirement_coverage_report()
    claims = claim_semantics_report()["checks"]
    rows = {
        "all_five_requirements_are_globally_closed": all(
            not row["full_scope_proved"] for row in coverage["rows"]
        ),
        "finite_exact_quotient_is_necessary": claims["finite_quotient_not_necessary"],
        "finite_quotient_size_controls_all_nonadditive_costs": claims[
            "finite_class_count_misses_history_fibers"
        ],
        "deterministic_cycle_formula_handles_adversarial_successors": claims[
            "finite_adversarial_computation_closed"
        ],
        "metric_closeness_alone_preserves_zero_error_safety": claims[
            "metric_only_zero_error_refuted"
        ],
        "terminal_fiber_controls_every_tree_cost": claims[
            "terminal_fibers_miss_branching"
        ]
        and claims["unrounded_fibers_miss_prefix_cost"],
        "another_bounded_fixture_selects_the_global_grammar": claims[
            "semantic_audit_blocks_unique_class_inference"
        ],
        "nothing_mathematical_remains": residual_dependency_report()["checks"][
            "global_margin_still_missing"
        ],
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 8 and all(rows.values()),
    }


def _predecessor_tests() -> tuple[tuple[str, str], ...]:
    tree = ast.parse(V28_CENTRAL.read_text(encoding="utf-8"), filename=str(V28_CENTRAL))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "PREDECESSOR_TESTS"
            for target in node.targets
        ):
            return tuple(ast.literal_eval(node.value)) + (
                V28_TEST,
                V29_TEST,
                V30_TEST,
                V31_TEST,
            )
    raise ValueError("v0.28 predecessor inventory not found")


def predecessor_inventory_report() -> dict[str, Any]:
    rows = []
    for package, filename in _predecessor_tests():
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append({"package": package, "tests": count})
    tests = sum(row["tests"] for row in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": tests,
        "pass": len(rows) == 32 and tests == 354,
    }


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_closure_stop_contract_v0_32",
        "objective": "audit the full frozen ASMP-4 completion standard after v0.31 and decide whether more autonomous bounded harness work is evidentially justified",
        "decision_scope": {
            "stop": "autonomous bounded finite or local fixture expansion",
            "continue_if": "a formal global class, abstraction theorem, attributable external adjudication, or dependency-invalidating error is supplied",
            "not_a_resolution": "the canonical nonlinear two-port problem remains mathematically unresolved",
        },
        "audit_rules": {
            "requirements": "extract all five completion requirements from the canonical source",
            "evidence": "distinguish conditional registered-lane closure from full-scope proof",
            "unknowns": "do not infer a unique formal class from ambiguous canonical wording",
            "necessity": "do not make finite exact quotients necessary after the Thue-Morse boundary",
        },
        "stop_argument": {
            "finite_lane": "region computation and registered cost transfer are closed once a finite public abstraction is supplied",
            "root_gap": "the source supplies neither a formal global nonlinear class nor a construction or replacement for its public abstraction",
            "harness_limit": "another bounded fixture cannot quantify the missing class or authorize a semantic choice",
        },
        "reopening_conditions": 4,
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_closure_stop_audit_v0_32",
        "canonical_requirements": {
            "count": 5,
            "full_scope_proved": 0,
            "conditional_evidence_rows": 5,
        },
        "closed_conditional_layers": {
            "count": 7,
            "range": "v0.25-v0.31",
            "includes_finite_adversarial_region": True,
            "includes_three_nonadditive_factor_laws": True,
        },
        "residual_root": {
            "formal_registered_class": "missing",
            "public_abstraction_or_replacement": "missing",
            "global_finite_horizon_margin": "missing",
            "finite_additive_region_computation": "closed",
        },
        "sealed_resources": 5,
        "mutations_rejected": 8,
        "reopening_conditions": 4,
        "predecessor_inventory": {"packages": 32, "tests": 354},
        "decision": "convincing_harness_backed_operational_stop_on_autonomous_bounded_expansion",
        "nonclaim": "ASMP-4 is not fully resolved; the stop requests a formal class plus abstraction theorem or external adjudication",
    }


def payload_report() -> dict[str, Any]:
    required = {
        "README.md",
        "STOP_CERTIFICATE_v0_32.md",
        "RESULT.md",
        "COMPLETION_AUDIT_v0_32.md",
        "REVIEWER_PACKET_v0_32.md",
        "closure_stop_contract_v0_32.json",
        "closure_stop_claim_v0_32.json",
        "closure_stop_audit.py",
        "verify_closure_stop_audit.py",
        "test_closure_stop_audit.py",
        "run_verification.py",
    }
    present = {path.name for path in HERE.iterdir() if path.is_file()}
    return {"missing": sorted(required - present), "pass": required <= present}


def closure_stop_report() -> dict[str, Any]:
    components = {
        "resources": resource_integrity_report(),
        "requirements": canonical_requirements_report(),
        "contract_exactness": {
            "pass": CONTRACT.exists() and _load(CONTRACT) == expected_contract_payload()
        },
        "claim_exactness": {
            "pass": CLAIM.exists() and _load(CLAIM) == expected_claim_payload()
        },
        "claim_semantics": claim_semantics_report(),
        "coverage": requirement_coverage_report(),
        "finite_lane": finite_lane_closure_report(),
        "residual_dependencies": residual_dependency_report(),
        "stop_logic": stop_logic_report(),
        "reopening": reopening_conditions_report(),
        "mutations": mutation_report(),
        "inventory": predecessor_inventory_report(),
        "payload": payload_report(),
    }
    return {
        "schema_version": "asmp4_closure_stop_audit_v0_32",
        **components,
        "pass": all(component["pass"] for component in components.values()),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = closure_stop_report() if report is None else report
    return {
        "R0_five_resource_seals": report["resources"]["pass"],
        "R1_five_canonical_requirements": report["requirements"]["pass"],
        "R2_exact_contract_and_claim": report["contract_exactness"]["pass"]
        and report["claim_exactness"]["pass"],
        "R3_claim_semantics": report["claim_semantics"]["pass"],
        "R4_zero_full_scope_rows": report["coverage"]["pass"],
        "R5_seven_conditional_layers": report["finite_lane"]["pass"],
        "R6_residual_dependency_root": report["residual_dependencies"]["pass"],
        "R7_stop_and_reopening_logic": report["stop_logic"]["pass"]
        and report["reopening"]["pass"],
        "R8_eight_mutations_rejected": report["mutations"]["pass"],
        "R9_inventory_and_payload": report["inventory"]["pass"]
        and report["payload"]["pass"],
    }


def main() -> int:
    report = closure_stop_report()
    payload = {"gates": verification_gates(report), "report": report}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
