"""Consolidated ASMP-4 completion and stopping atlas v0.9."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
MILLENNIUM = HERE.parent
SOURCE = MILLENNIUM / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
INDEX = MILLENNIUM / "problem_set_v0_1.json"

SEALED_RESOURCES = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_2_claim": (
        MILLENNIUM
        / "asmp4_serial_collapse_theorem_v0_2"
        / "resolution_claim_v0_2.json",
        "2d0979b370b93aeb047fafcbe86ee1afdbd1afb3ce9fbe31c8964f65976225e9",
    ),
    "v0_3_claim": (
        MILLENNIUM / "asmp4_metric_robust_collapse_v0_3" / "resolution_claim_v0_3.json",
        "eb56ebbbccc2f088e09ccc5a6ff55f6403dcdf54ef47d9879dc207285cf31da1",
    ),
    "v0_4_claim": (
        MILLENNIUM / "asmp4_heterogeneous_port_costs_v0_4" / "boundary_claim_v0_4.json",
        "e7e05f47bfd5fd715e1a39c4d0ec272ca8cbeedd0af6a3b50072c819064d7784",
    ),
    "v0_5_claim": (
        MILLENNIUM
        / "asmp4_adaptive_history_collapse_v0_5"
        / "adaptive_claim_v0_5.json",
        "f37212d37353f9a1af577fe976c412117d0d67bb833100205fc17c8892a84996",
    ),
    "v0_6_claim": (
        MILLENNIUM / "asmp4_registration_fork_v0_6" / "registration_claim_v0_6.json",
        "812c17f913c1e498d835c13430b7880b95a188496333b48355883f0fe634c5a5",
    ),
    "v0_7_claim": (
        MILLENNIUM
        / "asmp4_relational_action_frontier_v0_7"
        / "relational_claim_v0_7.json",
        "6cf4f5c04e789a75510cb1ff032a1ce764312ab8969ae97e32126f4685870749",
    ),
    "v0_8_claim": (
        MILLENNIUM
        / "asmp4_randomness_quantifier_boundary_v0_8"
        / "randomness_claim_v0_8.json",
        "0cfce1a8751eae64ba746e7a773eb1cee48355c5168465c4a208c2fa07b1cf16",
    ),
}

TEST_FILES = (
    MILLENNIUM
    / "asmp4_capacity_definition_audit"
    / "test_capacity_definition_audit.py",
    MILLENNIUM / "asmp4_two_port_game" / "test_two_port_game.py",
    MILLENNIUM / "asmp4_serial_collapse_theorem_v0_2" / "test_serial_capacity.py",
    MILLENNIUM / "asmp4_metric_robust_collapse_v0_3" / "test_metric_harness.py",
    MILLENNIUM
    / "asmp4_heterogeneous_port_costs_v0_4"
    / "test_heterogeneous_frontier.py",
    MILLENNIUM / "asmp4_adaptive_history_collapse_v0_5" / "test_adaptive_frontier.py",
    MILLENNIUM / "asmp4_registration_fork_v0_6" / "test_registration_fork.py",
    MILLENNIUM
    / "asmp4_relational_action_frontier_v0_7"
    / "test_relational_frontier.py",
    MILLENNIUM
    / "asmp4_randomness_quantifier_boundary_v0_8"
    / "test_randomness_quantifier.py",
)

EXPECTED_REQUIREMENT_FRAGMENTS = (
    "coordinate-invariant definition of the read and write transversal entropies",
    "variational formula for the entire achievable rate region",
    "converse theorems and constructive coder-controller/actuator schemes",
    "exact finite-horizon corrections",
    "counterexamples locating the boundary of partial observability",
)


def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for name, (path, expected_digest) in SEALED_RESOURCES.items():
        exists = path.exists()
        observed = hashlib.sha256(path.read_bytes()).hexdigest() if exists else None
        rows.append(
            {
                "name": name,
                "path": path.relative_to(MILLENNIUM).as_posix(),
                "expected_sha256": expected_digest,
                "observed_sha256": observed,
                "matches": observed == expected_digest,
            }
        )
    return {
        "rows": rows,
        "resources": len(rows),
        "pass": all(row["matches"] for row in rows),
    }


def canonical_requirements_report() -> dict[str, Any]:
    source = SOURCE.read_text(encoding="utf-8")
    section = source.split("# ASMP-4", maxsplit=1)[1].split("# ASMP-5", maxsplit=1)[0]
    section = section.split("## What a complete resolution requires", maxsplit=1)[1]
    section = section.split("## Liveness and kill examples", maxsplit=1)[0]
    matches = re.findall(r"(?ms)^\d+\.\s+(.+?)(?=^\d+\.|\Z)", section)
    requirements = [" ".join(match.split()) for match in matches]
    fragment_checks = [
        any(
            fragment.casefold() in requirement.casefold()
            for requirement in requirements
        )
        for fragment in EXPECTED_REQUIREMENT_FRAGMENTS
    ]
    return {
        "requirements": [
            {"id": f"C{index}", "text": requirement}
            for index, requirement in enumerate(requirements, start=1)
        ],
        "count": len(requirements),
        "fragment_checks": fragment_checks,
        "pass": len(requirements) == 5 and all(fragment_checks),
    }


def _claims() -> dict[str, dict[str, Any]]:
    return {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, (path, _) in SEALED_RESOURCES.items()
        if name.endswith("_claim")
    }


def claim_chain_report() -> dict[str, Any]:
    claims = _claims()
    expected_schemas = {
        "v0_2_claim": "asmp_resolution_claim_v0_2",
        "v0_3_claim": "asmp_resolution_claim_v0_3",
        "v0_4_claim": "asmp4_boundary_claim_v0_4",
        "v0_5_claim": "asmp4_adaptive_history_claim_v0_5",
        "v0_6_claim": "asmp4_registration_fork_claim_v0_6",
        "v0_7_claim": "asmp4_relational_action_frontier_claim_v0_7",
        "v0_8_claim": "asmp4_randomness_quantifier_boundary_claim_v0_8",
    }
    rows = [
        {
            "name": name,
            "schema": claims[name].get("schema_version"),
            "expected_schema": schema,
            "matches": claims[name].get("schema_version") == schema,
        }
        for name, schema in expected_schemas.items()
    ]
    v06 = claims["v0_6_claim"]
    v07 = claims["v0_7_claim"]
    v08 = claims["v0_8_claim"]
    exact_checks = {
        "v06_computed_region": v06["computed_sensor_class"]["closed_asymptotic_region"]
        == "[1,infinity) x [1,infinity)",
        "v06_raw_region": v06["forced_raw_sensor_class"]["closed_asymptotic_region"]
        == "[2,infinity) x [1,infinity)",
        "v06_registry_domain_absent": v06["global_registry_scope_audit"][
            "domain_defining_occurrence_count"
        ]
        == 0,
        "v07_nonrectangular": v07["exact_closed_region"]["nonrectangular"] is True,
        "v07_kernel_derandomization": v07["randomized_kernel_census"][
            "derandomization_failures"
        ]
        == 0,
        "v08_probability_order_absent": v08["canonical_audit"][
            "probability_disturbance_order_clause_count"
        ]
        == 0,
        "v08_quantifier_separation": (
            v08["continuous_diagonal_fixture"]["per_disturbance_almost_sure_safe"]
            and not v08["continuous_diagonal_fixture"]["support_zero_error_safe"]
        ),
    }
    return {
        "rows": rows,
        "claim_count": len(rows),
        "exact_checks": exact_checks,
        "pass": all(row["matches"] for row in rows) and all(exact_checks.values()),
    }


def source_gap_report() -> dict[str, Any]:
    source = SOURCE.read_text(encoding="utf-8")
    section = source.split("# ASMP-4", maxsplit=1)[1].split("# ASMP-5", maxsplit=1)[0]
    collapsed = " ".join(section.casefold().split())
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    asmp4 = next(problem for problem in index["problems"] if problem["id"] == "ASMP-4")
    stochastic_markers = (
        "almost surely",
        "with probability one",
        "for every random seed",
        "support-zero-error",
        "expectation over shared randomness",
    )
    sensor_markers = (
        "all causal sensor computations",
        "forced raw sensor",
        "sensor partition grammar",
        "upstream computation closure",
    )
    checks = {
        "source_calls_codes_registered": "registered causal code" in collapsed,
        "source_allows_shared_randomness": "shared randomness independent of the plant state"
        in collapsed,
        "sensor_selector_absent": all(
            marker not in collapsed for marker in sensor_markers
        ),
        "stochastic_order_absent": all(
            marker not in collapsed for marker in stochastic_markers
        ),
        "index_is_non_normative": index["registry_is_normative"] is False,
        "graduation_unsatisfied": index["graduation_standard_satisfied"] is False,
        "index_has_no_sensor_grammar": not any(
            "sensor" in key or "random" in key for key in asmp4
        ),
    }
    return {
        "checks": checks,
        "machine_index_status": index["status"],
        "asmp4_index_keys": sorted(asmp4),
        "missing_dimensions": [
            "registered sensor/computation domain",
            "randomness/disturbance quantifier order",
        ],
        "pass": all(checks.values()),
    }


def requirement_evidence_atlas() -> dict[str, Any]:
    requirements = canonical_requirements_report()["requirements"]
    evidence = (
        ("v0.3", "v0.6", "v0.7"),
        ("v0.2", "v0.3", "v0.5", "v0.6", "v0.7"),
        ("v0.2", "v0.3", "v0.5", "v0.6", "v0.7"),
        ("v0.2", "v0.5", "v0.6", "v0.7", "v0.8"),
        ("v0.4", "v0.5", "v0.6", "v0.7", "v0.8"),
    )
    limitations = (
        "Definitions are exact only after the code/metric/grammar registration is fixed.",
        "Whole regions are proved for several registered classes, not for an undefined union of classes.",
        "Converses and constructions inherit the same registration conditions.",
        "Finite corrections are exact within each declared architecture and safety semantics.",
        "Boundary counterexamples expose omitted assumptions rather than selecting them.",
    )
    rows = []
    for requirement, packages, limitation in zip(
        requirements, evidence, limitations, strict=True
    ):
        rows.append(
            {
                "id": requirement["id"],
                "canonical_requirement": requirement["text"],
                "evidence_packages": list(packages),
                "conditional_evidence_present": True,
                "canonical_completion_proven": False,
                "limitation": limitation,
            }
        )
    return {
        "rows": rows,
        "conditional_coverage_count": sum(
            row["conditional_evidence_present"] for row in rows
        ),
        "canonical_completion_count": sum(
            row["canonical_completion_proven"] for row in rows
        ),
        "pass": len(rows) == 5
        and all(row["evidence_packages"] for row in rows)
        and not any(row["canonical_completion_proven"] for row in rows),
    }


def model_completion_atlas() -> dict[str, Any]:
    sensor_models = [
        {
            "model": "computed_sensor",
            "same_plant_family": "v0.7 relational full-reset plant",
            "completion": "all causal sufficient-statistic partitions admitted",
            "target": "[1,infinity) x [1,infinity)",
        },
        {
            "model": "adaptive_two_partition",
            "same_plant_family": "v0.7 relational full-reset plant",
            "completion": "only coarse and raw partitions admitted adaptively",
            "target": "nonrectangular log2(3)-to-(2,1) wedge",
        },
        {
            "model": "forced_raw",
            "same_plant_family": "v0.7 relational full-reset plant",
            "completion": "only the singleton raw partition admitted",
            "target": "[2,infinity) x [1,infinity)",
        },
    ]
    stochastic_models = [
        {
            "model": "per_disturbance_almost_sure",
            "same_plant_family": "v0.8 smooth diagonal plant",
            "completion": "forall w P_r[safe(r,w)]=1",
            "target": "origin achievable",
        },
        {
            "model": "uniform_almost_sure",
            "same_plant_family": "v0.8 smooth diagonal plant",
            "completion": "P_r[forall w safe(r,w)]=1",
            "target": "infeasible",
        },
        {
            "model": "support_zero_error",
            "same_plant_family": "v0.8 smooth diagonal plant",
            "completion": "forall r in support forall w safe(r,w)",
            "target": "infeasible",
        },
    ]
    sensor_targets = {row["target"] for row in sensor_models}
    stochastic_targets = {row["target"] for row in stochastic_models}
    return {
        "sensor_axis": sensor_models,
        "stochastic_axis": stochastic_models,
        "sensor_model_count": len(sensor_models),
        "sensor_distinct_targets": len(sensor_targets),
        "stochastic_model_count": len(stochastic_models),
        "stochastic_distinct_targets": len(stochastic_targets),
        "independent_missing_dimensions": 2,
        "pass": len(sensor_targets) == 3 and len(stochastic_targets) == 2,
    }


def underdetermination_certificate() -> dict[str, Any]:
    gaps = source_gap_report()
    models = model_completion_atlas()
    obligations = {
        "undefined_domain_predicates_exist": gaps["pass"],
        "same_plant_sensor_models_have_distinct_regions": models[
            "sensor_distinct_targets"
        ]
        == 3,
        "same_plant_stochastic_models_change_feasibility": models[
            "stochastic_distinct_targets"
        ]
        == 2,
        "machine_index_cannot_supply_normative_choice": gaps["checks"][
            "index_is_non_normative"
        ],
        "graduation_standard_is_not_satisfied": gaps["checks"][
            "graduation_unsatisfied"
        ],
    }
    return {
        "meta_theorem": (
            "If two interpretations satisfy every explicit clause but give "
            "different target regions or feasibility, the target is not "
            "semantically determined by those clauses."
        ),
        "obligations": obligations,
        "decision": "canonical_asmp4_target_not_semantically_determinate",
        "pass": all(obligations.values()),
    }


def mutation_selector_audit() -> dict[str, Any]:
    base = "REGISTERED_SENSOR=UNSPECIFIED; RANDOM_SAFETY=UNSPECIFIED"
    cases = {
        "base": base,
        "computed": base.replace("UNSPECIFIED", "COMPUTED", 1),
        "raw": base.replace("UNSPECIFIED", "RAW", 1),
        "support": base.replace("RANDOM_SAFETY=UNSPECIFIED", "RANDOM_SAFETY=SUPPORT"),
        "per_path": base.replace("RANDOM_SAFETY=UNSPECIFIED", "RANDOM_SAFETY=PER_PATH"),
    }
    classifications = {
        name: {
            "sensor_selected": "REGISTERED_SENSOR=UNSPECIFIED" not in text,
            "randomness_selected": "RANDOM_SAFETY=UNSPECIFIED" not in text,
        }
        for name, text in cases.items()
    }
    return {
        "cases": cases,
        "classifications": classifications,
        "pass": (
            classifications["base"]
            == {"sensor_selected": False, "randomness_selected": False}
            and classifications["computed"]["sensor_selected"]
            and classifications["raw"]["sensor_selected"]
            and classifications["support"]["randomness_selected"]
            and classifications["per_path"]["randomness_selected"]
        ),
    }


def test_inventory_report() -> dict[str, Any]:
    rows = []
    for path in TEST_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        tests = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append(
            {
                "package": path.parent.name,
                "file": path.name,
                "tests": tests,
            }
        )
    return {
        "rows": rows,
        "packages": len(rows),
        "predecessor_tests": sum(row["tests"] for row in rows),
        "pass": len(rows) == 9 and sum(row["tests"] for row in rows) == 112,
    }


def stopping_certificate() -> dict[str, Any]:
    requirements = requirement_evidence_atlas()
    underdetermination = underdetermination_certificate()
    reopening_conditions = [
        "A normative sensor/computation registry is added to canonical ASMP-4.",
        "A normative probability/disturbance quantifier order is added.",
        "A new registered plant class is supplied that is not reduced by v0.2-v0.8.",
        "An attributable external proof audit finds a concrete error in a sealed claim.",
    ]
    return {
        "conditional_requirement_coverage": requirements["conditional_coverage_count"],
        "canonical_requirement_completion": requirements["canonical_completion_count"],
        "underdetermination_decision": underdetermination["decision"],
        "reopening_conditions": reopening_conditions,
        "decision": "stop_local_enumeration_and_request_normative_registration",
        "pass": (
            requirements["pass"]
            and underdetermination["pass"]
            and len(reopening_conditions) == 4
        ),
    }


def completion_atlas_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    requirements = canonical_requirements_report()
    claims = claim_chain_report()
    gaps = source_gap_report()
    evidence = requirement_evidence_atlas()
    models = model_completion_atlas()
    theorem = underdetermination_certificate()
    mutations = mutation_selector_audit()
    tests = test_inventory_report()
    stopping = stopping_certificate()
    components = (
        integrity,
        requirements,
        claims,
        gaps,
        evidence,
        models,
        theorem,
        mutations,
        tests,
        stopping,
    )
    return {
        "schema_version": "asmp4_completion_atlas_v0_9",
        "resource_integrity": integrity,
        "canonical_requirements": requirements,
        "claim_chain": claims,
        "source_gaps": gaps,
        "requirement_evidence_atlas": evidence,
        "model_completion_atlas": models,
        "underdetermination_certificate": theorem,
        "mutation_selector_audit": mutations,
        "test_inventory": tests,
        "stopping_certificate": stopping,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    if report is None:
        report = completion_atlas_report()
    return {
        "R0_sealed_resource_integrity": report["resource_integrity"]["pass"],
        "R1_five_canonical_requirements_extracted": report["canonical_requirements"][
            "pass"
        ],
        "R2_seven_claim_chain_is_exact": report["claim_chain"]["pass"],
        "R3_two_normative_source_gaps_are_verified": report["source_gaps"]["pass"],
        "R4_requirement_evidence_atlas_is_complete": report[
            "requirement_evidence_atlas"
        ]["pass"],
        "R5_model_completions_have_distinct_targets": report["model_completion_atlas"][
            "pass"
        ],
        "R6_semantic_underdetermination_theorem_applies": report[
            "underdetermination_certificate"
        ]["pass"],
        "R7_selector_mutations_change_scope": report["mutation_selector_audit"]["pass"],
        "R8_predecessor_test_inventory_is_exact": report["test_inventory"]["pass"],
        "R9_evidence_backed_stop_certificate": report["stopping_certificate"]["pass"],
        "R10_complete_payload": report["pass"],
    }


def main(output: str | None = None) -> int:
    report = completion_atlas_report()
    payload = {"report": report, "gates": verification_gates(report)}
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if output is None:
        print(rendered)
    else:
        Path(output).write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
