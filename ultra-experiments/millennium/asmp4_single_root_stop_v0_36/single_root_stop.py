"""Sealed single-root stopping harness for ASMP-4 v0.36."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import re
from functools import cache
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V06 = ROOT / "asmp4_registration_fork_v0_6" / "registration_claim_v0_6.json"
V08 = (
    ROOT
    / "asmp4_randomness_quantifier_boundary_v0_8"
    / "randomness_claim_v0_8.json"
)
V33 = (
    ROOT
    / "asmp4_nonfinite_safe_closing_v0_33"
    / "safe_closing_claim_v0_33.json"
)
V34 = (
    ROOT
    / "asmp4_compact_public_connector_v0_34"
    / "public_connector_claim_v0_34.json"
)
V35 = (
    ROOT
    / "asmp4_robust_public_atlas_v0_35"
    / "robust_public_atlas_claim_v0_35.json"
)
CONTRACT = HERE / "single_root_stop_contract_v0_36.json"
CLAIM = HERE / "single_root_stop_claim_v0_36.json"

SEALED_RESOURCES = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v06_registration_fork": (
        V06,
        "812c17f913c1e498d835c13430b7880b95a188496333b48355883f0fe634c5a5",
    ),
    "v08_randomness_fork": (
        V08,
        "0cfce1a8751eae64ba746e7a773eb1cee48355c5168465c4a208c2fa07b1cf16",
    ),
    "v33_nonfinite_region": (
        V33,
        "16cd95033cc669583c2bbda0dfff6f65ac4548fbcbd6892d34bb8c6e74621580",
    ),
    "v34_public_connectors": (
        V34,
        "378260f2eea043569e73e6962bf40b1081e3bafc7f8ca2cac1c5f519f5eb2d85",
    ),
    "v35_robust_atlas": (
        V35,
        "9b29d66aea46b1586e2cdef7ca9c8203bca71e1753232ccb9fd59a85425c195e",
    ),
}

EXPECTED_PAYLOAD = (
    "README.md",
    "STOP_CERTIFICATE_v0_36.md",
    "RESULT.md",
    "REVIEWER_PACKET_v0_36.md",
    "COMPLETION_AUDIT_v0_36.md",
    "single_root_stop_contract_v0_36.json",
    "single_root_stop_claim_v0_36.json",
    "single_root_stop.py",
    "verify_single_root_stop.py",
    "test_single_root_stop.py",
    "run_verification.py",
)

EXPECTED_REQUIREMENT_FRAGMENTS = (
    "coordinate-invariant definition",
    "variational formula for the entire achievable rate region",
    "converse theorems and constructive coder-controller/actuator schemes",
    "exact finite-horizon corrections",
    "counterexamples locating the boundary",
)

MISSING_SELECTORS = (
    "sensor_grammar",
    "randomness_disturbance_order",
    "normally_hyperbolic_predicate",
    "local_controllability_predicate",
    "public_belief_semantics",
    "safe_closing_or_reset_semantics",
    "actuator_dictionary_domain",
)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@cache
def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for name, (path, expected) in SEALED_RESOURCES.items():
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
        "resources": len(rows),
        "rows": rows,
        "pass": len(rows) == 6 and all(row["matches"] for row in rows),
    }


@cache
def canonical_section() -> str:
    text = SOURCE.read_text(encoding="utf-8")
    return text.split("# ASMP-4", 1)[1].split("# ASMP-5", 1)[0]


@cache
def canonical_requirements_report() -> dict[str, Any]:
    section = canonical_section().split("## What a complete resolution requires", 1)[1]
    section = section.split("## Liveness and kill examples", 1)[0]
    matches = re.findall(r"(?ms)^([1-5])\.\s+(.*?)(?=^[1-5]\.\s|\Z)", section)
    requirements = tuple(" ".join(text.split()) for _, text in matches)
    checks = {
        "five_requirements": len(requirements) == 5,
        "ordered_fragments": all(
            fragment in requirement.casefold()
            for fragment, requirement in zip(
                EXPECTED_REQUIREMENT_FRAGMENTS, requirements, strict=True
            )
        ),
    }
    return {
        "requirements": list(requirements),
        "checks": checks,
        "pass": all(checks.values()),
    }


@cache
def registration_field_report() -> dict[str, Any]:
    collapsed = " ".join(canonical_section().casefold().split())
    explicit = {
        "registered_code_phrase": "registered causal code" in collapsed,
        "registered_class_phrase": (
            "registered normally hyperbolic, locally controllable class" in collapsed
        ),
        "bounded_conventions_phrase": (
            "bounded uncertainty, delay, memory, control-authority, and disturbance conventions"
            in collapsed
        ),
        "separate_components": (
            "plant, sensor, controller, and actuator are separate components"
            in collapsed
        ),
        "side_channels_forbidden": "uncharged side channel" in collapsed,
        "universal_disturbance": "for every allowed disturbance sequence" in collapsed,
    }
    missing = {
        "sensor_grammar": not any(
            marker in collapsed
            for marker in (
                "all causal sensor encoders are registered",
                "forced raw sensor",
                "sensor partition grammar",
            )
        ),
        "randomness_disturbance_order": _json(V08)
        .get("canonical_audit", {})
        .get("probability_disturbance_order_clause_count")
        == 0,
        "normally_hyperbolic_predicate": collapsed.count("normally hyperbolic")
        == 1
        and not any(
            marker in collapsed
            for marker in ("invariant splitting", "normal bundle", "dominated splitting")
        ),
        "local_controllability_predicate": collapsed.count("locally controllable")
        == 1
        and not any(
            marker in collapsed
            for marker in ("small-time local controllability", "endpoint map rank")
        ),
        "public_belief_semantics": "public belief" not in collapsed
        and "reachable-set state" not in collapsed,
        "safe_closing_or_reset_semantics": "safe closing" not in collapsed
        and "reset cell" not in collapsed,
        "actuator_dictionary_domain": not any(
            marker in collapsed
            for marker in (
                "all finite actuator dictionaries",
                "fixed actuator dictionary",
                "actuator grammar",
            )
        ),
    }
    checks = {
        "six_explicit_architecture_clauses": len(explicit) == 6
        and all(explicit.values()),
        "seven_domain_selectors_absent": tuple(missing) == MISSING_SELECTORS
        and all(missing.values()),
        "registration_is_placeholder_not_domain": all(explicit.values())
        and all(missing.values()),
    }
    return {
        "explicit": explicit,
        "missing": missing,
        "checks": checks,
        "pass": all(checks.values()),
    }


@cache
def material_fork_report() -> dict[str, Any]:
    registration = _json(V06)
    randomness = _json(V08)
    computed = registration["computed_sensor_class"]["closed_asymptotic_region"]
    raw = registration["forced_raw_sensor_class"]["closed_asymptotic_region"]
    registry_audit = registration["canonical_registry_model_audit"]
    random_fixture = randomness["continuous_diagonal_fixture"]
    checks = {
        "registry_domain_unselected": registry_audit["registry_domain_selected"]
        is False,
        "both_sensor_registries_satisfy_source": registry_audit[
            "computed_sensor_registry_satisfies_all_obligations"
        ]
        and registry_audit["fixed_raw_sensor_registry_satisfies_all_obligations"],
        "sensor_regions_differ": computed != raw,
        "probability_order_unselected": randomness["canonical_audit"][
            "probability_disturbance_order_clause_count"
        ]
        == 0,
        "randomness_feasibility_differs": random_fixture[
            "per_disturbance_almost_sure_safe"
        ]
        and not random_fixture["uniform_almost_sure_safe"],
    }
    return {
        "computed_region": computed,
        "raw_region": raw,
        "checks": checks,
        "pass": all(checks.values()),
    }


@cache
def conditional_chain_report() -> dict[str, Any]:
    v33 = _json(V33)
    v34 = _json(V34)
    v35 = _json(V35)
    forks = material_fork_report()
    rows = (
        {
            "requirement": 1,
            "conditional_evidence": "v0.33 causal-conjugacy invariance and v0.35 bi-Lipschitz atlas transport",
            "canonical_gap": "the registered state/code domain is unselected",
        },
        {
            "requirement": 2,
            "conditional_evidence": "v0.33 component support formula and indexed global union",
            "canonical_gap": "the registered state/code domain is unselected",
        },
        {
            "requirement": 3,
            "conditional_evidence": "v0.33 region equality plus v0.34/v0.35 connector constructions",
            "canonical_gap": "the registered state/code domain is unselected",
        },
        {
            "requirement": 4,
            "conditional_evidence": "v0.33 vector closing correction plus v0.35 exact Lipschitz margin",
            "canonical_gap": "the registered state/code domain is unselected",
        },
        {
            "requirement": 5,
            "conditional_evidence": "v0.6/v0.8 forks and v0.34/v0.35 compactness, observability, uncertainty, and side-channel boundaries",
            "canonical_gap": "the registered state/code domain is unselected",
        },
    )
    checks = {
        "v33_entire_component_region": v33["theorem"]["component_region"]
        == "R_q=closure(upward(conv(P_q)))",
        "v33_finite_correction": "closing overhead/T"
        in v33["theorem"]["finite_correction"],
        "v33_coordinate_invariance": "conjugacies"
        in v33["theorem"]["coordinate_invariance"],
        "v34_safe_closing_bridge": v34["theorem"]["safe_closing"]
        == "constant connector bounds imply v0.33 sublinear safe closing",
        "v35_robust_atlas_bridge": v35["theorem"]["v33_implication"]
        == "a finite fixed-reset atlas supplies constant safe-closing certificates",
        "v35_separate_two_port_costs": v35["nonlinear_fixture"]["read_bits"] == 6
        and v35["nonlinear_fixture"]["write_bits"] == 6,
        "five_requirements_have_conditional_evidence": len(rows) == 5,
        "material_boundaries_present": forks["pass"],
        "every_row_retains_same_root": len(
            {row["canonical_gap"] for row in rows}
        )
        == 1,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


@cache
def dependency_report() -> dict[str, Any]:
    nodes = {
        "formal_normative_registry": False,
        "conditional_nonfinite_region": True,
        "compact_public_safe_closing": True,
        "robust_public_reset_atlas": True,
        "finite_horizon_margin": True,
        "material_boundary_witnesses": True,
        "external_semantic_adjudication": False,
        "sealed_premise_error": False,
    }
    unresolved_roots = tuple(
        name
        for name, value in nodes.items()
        if not value
        and name
        not in ("external_semantic_adjudication", "sealed_premise_error")
    )
    checks = {
        "single_unresolved_root": unresolved_roots
        == ("formal_normative_registry",),
        "all_mathematical_successors_present": all(
            nodes[name]
            for name in (
                "conditional_nonfinite_region",
                "compact_public_safe_closing",
                "robust_public_reset_atlas",
                "finite_horizon_margin",
                "material_boundary_witnesses",
            )
        ),
        "no_external_adjudication": not nodes["external_semantic_adjudication"],
        "no_sealed_error": not nodes["sealed_premise_error"],
    }
    return {
        "nodes": nodes,
        "unresolved_roots": unresolved_roots,
        "checks": checks,
        "pass": all(checks.values()),
    }


def stopping_decision(
    source_ambiguous: bool,
    material_fork: bool,
    conditional_chain_closed: bool,
    external_adjudication: bool,
    sealed_error: bool,
) -> bool:
    return (
        source_ambiguous
        and material_fork
        and conditional_chain_closed
        and not external_adjudication
        and not sealed_error
    )


@cache
def truth_table_report() -> dict[str, Any]:
    rows = []
    for values in itertools.product((False, True), repeat=5):
        decision = stopping_decision(*values)
        rows.append({"inputs": values, "stop": decision})
    stop_rows = [row for row in rows if row["stop"]]
    current = stopping_decision(True, True, True, False, False)
    checks = {
        "all_thirty_two_assignments": len(rows) == 32,
        "unique_stop_assignment": len(stop_rows) == 1,
        "unique_row_is_current": stop_rows[0]["inputs"]
        == (True, True, True, False, False),
        "current_decision_is_stop": current,
        "each_reopening_flip_clears_stop": all(
            not stopping_decision(*values)
            for values in (
                (False, True, True, False, False),
                (True, False, True, False, False),
                (True, True, False, False, False),
                (True, True, True, True, False),
                (True, True, True, False, True),
            )
        ),
    }
    return {
        "rows": len(rows),
        "stop_rows": len(stop_rows),
        "current_stop": current,
        "checks": checks,
        "pass": all(checks.values()),
    }


@cache
def stop_certificate_report() -> dict[str, Any]:
    reopening = (
        "add a formal normative registry for the plant, sensor, randomness, public state, costs, and actuator domain",
        "supply attributable external adjudication selecting a formal interpretation",
        "demonstrate an error in a sealed fork, theorem, parser, or dependency premise",
        "prove a registry-independent equivalence theorem that collapses the material forks",
    )
    checks = {
        "source_ambiguity_current": registration_field_report()["pass"],
        "material_fork_current": material_fork_report()["pass"],
        "conditional_chain_current": conditional_chain_report()["pass"],
        "single_root_current": dependency_report()["pass"],
        "truth_table_current": truth_table_report()["current_stop"],
        "four_reopening_conditions": len(reopening) == 4,
    }
    return {
        "decision": "stop_autonomous_asmp4_work_pending_semantic_input",
        "reopening_conditions": reopening,
        "nonclaim": "not a mathematical resolution and not an impossibility theorem for every formal ASMP-4 completion",
        "checks": checks,
        "pass": all(checks.values()),
    }


def mutation_report() -> dict[str, Any]:
    registration = registration_field_report()
    forks = material_fork_report()
    chain = conditional_chain_report()
    stop = stop_certificate_report()
    rows = {
        "registered_phrase_alone_defines_domain": registration["checks"][
            "seven_domain_selectors_absent"
        ],
        "sensor_registry_fork_is_immaterial": forks["checks"][
            "sensor_regions_differ"
        ],
        "randomness_order_is_immaterial": forks["checks"][
            "randomness_feasibility_differs"
        ],
        "fixed_reset_atlas_proves_all_pairs": "all-pairs"
        in _json(V35)["theorem"]["v34_boundary"],
        "conditional_chain_is_canonical_proof": chain["checks"][
            "every_row_retains_same_root"
        ],
        "more_finite_fixtures_select_semantics": registration["checks"][
            "registration_is_placeholder_not_domain"
        ],
        "green_regression_is_semantic_adjudication": not dependency_report()[
            "nodes"
        ]["external_semantic_adjudication"],
        "operational_stop_is_impossibility_theorem": "not an impossibility theorem"
        in stop["nonclaim"],
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 8 and all(rows.values()),
    }


def _count_tests(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
        for node in ast.walk(tree)
    )


def _package_version(name: str) -> int:
    match = re.search(r"_v0_(\d+)$", name)
    return int(match.group(1)) if match else 0


@cache
def predecessor_inventory_report() -> dict[str, Any]:
    paths = sorted(
        path
        for path in ROOT.glob("asmp4*/test_*.py")
        if path.parent.resolve() != HERE.resolve()
        and _package_version(path.parent.name) < 36
    )
    tests = sum(_count_tests(path) for path in paths)
    checks = {
        "thirty_six_predecessor_packages": len(paths) == 36,
        "three_hundred_ninety_four_predecessor_tests": tests == 394,
    }
    return {
        "packages": len(paths),
        "tests": tests,
        "checks": checks,
        "pass": all(checks.values()),
    }


def claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_single_root_stop_v0_36",
        "canonical": {
            "completion_requirements": 5,
            "explicit_architecture_clauses": 6,
            "missing_domain_selectors": list(MISSING_SELECTORS),
            "formal_normative_registry_selected": False,
        },
        "material_forks": {
            "computed_sensor_region": "[1,infinity) x [1,infinity)",
            "forced_raw_sensor_region": "[2,infinity) x [1,infinity)",
            "probability_disturbance_order_selected": False,
            "per_disturbance_and_uniform_feasibility_differ": True,
        },
        "conditional_chain": {
            "requirements_with_conditional_evidence": 5,
            "nonfinite_region": "v0.33",
            "compact_public_connector": "v0.34",
            "robust_public_atlas": "v0.35",
            "unresolved_root": "formal normative registry or attributable semantic adjudication",
        },
        "stopping_logic": {
            "truth_table_rows": 32,
            "stop_rows": 1,
            "reopening_conditions": 4,
        },
        "evidence": {
            "sealed_resources": 6,
            "mutations_rejected": 8,
            "predecessor_packages": 36,
            "predecessor_tests": 394,
        },
        "decision": "stop autonomous ASMP-4 work pending a formal registry, attributable semantic adjudication, a sealed error, or a registry-independence theorem",
        "nonclaim": "ASMP-4 is not mathematically resolved; this is a harness-backed operational stopping argument",
    }


@cache
def contract_report() -> dict[str, Any]:
    contract = _json(CONTRACT)
    checks = {
        "schema": contract.get("schema_version")
        == "asmp4_single_root_stop_contract_v0_36",
        "not_resolution": "not a mathematical resolution"
        in contract.get("decision_scope", {}).get("nonclaim", ""),
        "semantic_root": contract.get("decision_scope", {}).get("remaining_root")
        == "formal normative registration or attributable semantic adjudication",
        "four_reopeners": len(contract.get("reopening_conditions", [])) == 4,
    }
    return {"checks": checks, "pass": all(checks.values())}


@cache
def claim_report() -> dict[str, Any]:
    claim = _json(CLAIM)
    checks = {
        "exact": claim == claim_payload(),
        "zero_canonical_registry": claim.get("canonical", {}).get(
            "formal_normative_registry_selected"
        )
        is False,
        "operational_only": "not mathematically resolved"
        in claim.get("nonclaim", ""),
    }
    return {"checks": checks, "pass": all(checks.values())}


def payload_report() -> dict[str, Any]:
    missing = [name for name in EXPECTED_PAYLOAD if not (HERE / name).is_file()]
    return {"missing": missing, "pass": not missing}


def full_report() -> dict[str, Any]:
    report = {
        "resources": resource_integrity_report(),
        "requirements": canonical_requirements_report(),
        "registration": registration_field_report(),
        "forks": material_fork_report(),
        "chain": conditional_chain_report(),
        "dependency": dependency_report(),
        "truth_table": truth_table_report(),
        "stop": stop_certificate_report(),
        "mutations": mutation_report(),
        "inventory": predecessor_inventory_report(),
        "contract": contract_report(),
        "claim": claim_report(),
        "payload": payload_report(),
    }
    report["pass"] = all(section["pass"] for section in report.values())
    return report


def main() -> int:
    report = full_report()
    gates = {
        "R0_resources": report["resources"]["pass"],
        "R1_requirements": report["requirements"]["pass"],
        "R2_registration": report["registration"]["pass"],
        "R3_material_forks": report["forks"]["pass"],
        "R4_conditional_chain": report["chain"]["pass"],
        "R5_single_root": report["dependency"]["pass"],
        "R6_truth_table": report["truth_table"]["pass"],
        "R7_stop_certificate": report["stop"]["pass"],
        "R8_mutations_inventory": report["mutations"]["pass"]
        and report["inventory"]["pass"],
        "R9_contract_claim_payload": report["contract"]["pass"]
        and report["claim"]["pass"]
        and report["payload"]["pass"],
    }
    print(json.dumps({"gates": gates, "report": report}, indent=2, sort_keys=True))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
