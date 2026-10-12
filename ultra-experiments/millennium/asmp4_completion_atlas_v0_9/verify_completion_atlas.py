"""Import-independent verifier for the ASMP-4 v0.9 completion atlas."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
MILLENNIUM = HERE.parent
SOURCE = MILLENNIUM / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
INDEX = MILLENNIUM / "problem_set_v0_1.json"

RESOURCES = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_2": (
        MILLENNIUM
        / "asmp4_serial_collapse_theorem_v0_2"
        / "resolution_claim_v0_2.json",
        "2d0979b370b93aeb047fafcbe86ee1afdbd1afb3ce9fbe31c8964f65976225e9",
    ),
    "v0_3": (
        MILLENNIUM / "asmp4_metric_robust_collapse_v0_3" / "resolution_claim_v0_3.json",
        "eb56ebbbccc2f088e09ccc5a6ff55f6403dcdf54ef47d9879dc207285cf31da1",
    ),
    "v0_4": (
        MILLENNIUM / "asmp4_heterogeneous_port_costs_v0_4" / "boundary_claim_v0_4.json",
        "e7e05f47bfd5fd715e1a39c4d0ec272ca8cbeedd0af6a3b50072c819064d7784",
    ),
    "v0_5": (
        MILLENNIUM
        / "asmp4_adaptive_history_collapse_v0_5"
        / "adaptive_claim_v0_5.json",
        "f37212d37353f9a1af577fe976c412117d0d67bb833100205fc17c8892a84996",
    ),
    "v0_6": (
        MILLENNIUM / "asmp4_registration_fork_v0_6" / "registration_claim_v0_6.json",
        "812c17f913c1e498d835c13430b7880b95a188496333b48355883f0fe634c5a5",
    ),
    "v0_7": (
        MILLENNIUM
        / "asmp4_relational_action_frontier_v0_7"
        / "relational_claim_v0_7.json",
        "6cf4f5c04e789a75510cb1ff032a1ce764312ab8969ae97e32126f4685870749",
    ),
    "v0_8": (
        MILLENNIUM
        / "asmp4_randomness_quantifier_boundary_v0_8"
        / "randomness_claim_v0_8.json",
        "0cfce1a8751eae64ba746e7a773eb1cee48355c5168465c4a208c2fa07b1cf16",
    ),
}

TEST_PATHS = tuple(
    MILLENNIUM / package / filename
    for package, filename in (
        ("asmp4_capacity_definition_audit", "test_capacity_definition_audit.py"),
        ("asmp4_two_port_game", "test_two_port_game.py"),
        ("asmp4_serial_collapse_theorem_v0_2", "test_serial_capacity.py"),
        ("asmp4_metric_robust_collapse_v0_3", "test_metric_harness.py"),
        ("asmp4_heterogeneous_port_costs_v0_4", "test_heterogeneous_frontier.py"),
        ("asmp4_adaptive_history_collapse_v0_5", "test_adaptive_frontier.py"),
        ("asmp4_registration_fork_v0_6", "test_registration_fork.py"),
        ("asmp4_relational_action_frontier_v0_7", "test_relational_frontier.py"),
        ("asmp4_randomness_quantifier_boundary_v0_8", "test_randomness_quantifier.py"),
    )
)


def independent_integrity() -> dict[str, Any]:
    rows = []
    for name, (path, expected) in RESOURCES.items():
        observed = (
            hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        )
        rows.append(
            {"name": name, "observed": observed, "matches": observed == expected}
        )
    return {
        "rows": rows,
        "pass": len(rows) == 8 and all(row["matches"] for row in rows),
    }


def independent_requirements() -> dict[str, Any]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    in_asmp4 = False
    in_requirements = False
    rows: list[str] = []
    current: list[str] = []
    for line in lines:
        if line.startswith("# ASMP-4"):
            in_asmp4 = True
            continue
        if in_asmp4 and line.startswith("# ASMP-5"):
            break
        if not in_asmp4:
            continue
        if line == "## What a complete resolution requires":
            in_requirements = True
            continue
        if in_requirements and line.startswith("## "):
            break
        if not in_requirements:
            continue
        stripped = line.strip()
        if len(stripped) >= 3 and stripped[0].isdigit() and stripped[1:3] == ". ":
            if current:
                rows.append(" ".join(current))
            current = [stripped[3:]]
        elif stripped and current:
            current.append(stripped)
    if current:
        rows.append(" ".join(current))
    markers = (
        "coordinate-invariant",
        "entire achievable",
        "converse",
        "finite-horizon",
        "counterexamples",
    )
    return {
        "requirements": rows,
        "count": len(rows),
        "markers": {
            marker: any(marker in row.casefold() for row in rows) for marker in markers
        },
        "pass": len(rows) == 5
        and all(any(marker in row.casefold() for row in rows) for marker in markers),
    }


def _claim(name: str) -> dict[str, Any]:
    return json.loads(RESOURCES[name][0].read_text(encoding="utf-8"))


def independent_claim_chain() -> dict[str, Any]:
    expected = {
        "v0_2": "asmp_resolution_claim_v0_2",
        "v0_3": "asmp_resolution_claim_v0_3",
        "v0_4": "asmp4_boundary_claim_v0_4",
        "v0_5": "asmp4_adaptive_history_claim_v0_5",
        "v0_6": "asmp4_registration_fork_claim_v0_6",
        "v0_7": "asmp4_relational_action_frontier_claim_v0_7",
        "v0_8": "asmp4_randomness_quantifier_boundary_claim_v0_8",
    }
    schemas = {name: _claim(name).get("schema_version") for name in expected}
    return {
        "schemas": schemas,
        "pass": all(schemas[name] == schema for name, schema in expected.items()),
    }


def independent_source_gaps() -> dict[str, Any]:
    source = SOURCE.read_text(encoding="utf-8")
    section = source.split("# ASMP-4", 1)[1].split("# ASMP-5", 1)[0].casefold()
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    asmp4 = next(row for row in index["problems"] if row["id"] == "ASMP-4")
    sensor_selectors = (
        "forced raw sensor",
        "sensor partition grammar",
        "upstream computation closure",
    )
    stochastic_selectors = (
        "almost surely",
        "for every random seed",
        "support-zero-error",
    )
    checks = {
        "registered_code": "registered causal code" in section,
        "sensor_gap": all(marker not in section for marker in sensor_selectors),
        "randomness_allowed": "shared randomness independent of the plant state"
        in section,
        "stochastic_gap": all(marker not in section for marker in stochastic_selectors),
        "index_non_normative": index["registry_is_normative"] is False,
        "ungraduated": index["graduation_standard_satisfied"] is False,
        "index_key_gap": not any("sensor" in key or "random" in key for key in asmp4),
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_model_atlas() -> dict[str, Any]:
    v06 = _claim("v0_6")
    v07 = _claim("v0_7")
    v08 = _claim("v0_8")
    sensor_targets = {
        v06["computed_sensor_class"]["closed_asymptotic_region"],
        v07["three_registry_regions"]["coarse_or_raw_history_adaptive"],
        v06["forced_raw_sensor_class"]["closed_asymptotic_region"],
    }
    stochastic_targets = {
        "origin achievable"
        if v08["continuous_diagonal_fixture"]["per_disturbance_almost_sure_safe"]
        else "infeasible",
        "origin achievable"
        if v08["continuous_diagonal_fixture"]["uniform_almost_sure_safe"]
        else "infeasible",
        "origin achievable"
        if v08["continuous_diagonal_fixture"]["support_zero_error_safe"]
        else "infeasible",
    }
    return {
        "sensor_targets": sorted(sensor_targets),
        "stochastic_targets": sorted(stochastic_targets),
        "sensor_distinct": len(sensor_targets),
        "stochastic_distinct": len(stochastic_targets),
        "pass": len(sensor_targets) == 3 and len(stochastic_targets) == 2,
    }


def independent_test_inventory() -> dict[str, Any]:
    rows = []
    for path in TEST_PATHS:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append((path.parent.name, count))
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": sum(count for _, count in rows),
        "pass": len(rows) == 9 and sum(count for _, count in rows) == 112,
    }


def claim_exactness() -> dict[str, Any]:
    path = HERE / "completion_atlas_claim_v0_9.json"
    if not path.exists():
        return {"exists": False, "pass": False}
    claim = json.loads(path.read_text(encoding="utf-8"))
    return {
        "exists": True,
        "pass": (
            claim.get("schema_version") == "asmp4_completion_atlas_claim_v0_9"
            and claim.get("canonical_requirements")
            == {
                "count": 5,
                "conditional_evidence_coverage": 5,
                "canonical_completion_proven": 0,
            }
            and claim.get("model_completion_atlas", {}).get("sensor_distinct_targets")
            == 3
            and claim.get("model_completion_atlas", {}).get(
                "stochastic_distinct_targets"
            )
            == 2
            and claim.get("test_inventory")
            == {"predecessor_packages": 9, "predecessor_tests": 112}
            and claim.get("underdetermination_decision")
            == "canonical_asmp4_target_not_semantically_determinate"
        ),
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "stopping": HERE / "STOPPING_ARGUMENT_v0_9.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_9.md",
        "prior": HERE / "PRIOR_ART_AUDIT_v0_9.md",
    }
    if not all(path.exists() for path in paths.values()):
        return {"pass": False, "files_exist": False}
    text = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    checks = {
        "semantic_theorem": "semantic underdetermination theorem" in text["theorem"],
        "five_requirements": "five canonical completion requirements" in text["result"],
        "sensor_targets": "three sensor targets" in text["stopping"],
        "stochastic_targets": "two stochastic outcomes" in text["stopping"],
        "tests": "112 predecessor tests" in text["theorem"],
        "hash": "SHA-256" in text["theorem"],
        "stop": "stop local enumeration" in text["stopping"].casefold(),
        "completion": "0/5" in text["completion"],
        "prior": "does not claim" in text["prior"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    integrity = independent_integrity()
    requirements = independent_requirements()
    claims = independent_claim_chain()
    gaps = independent_source_gaps()
    models = independent_model_atlas()
    tests = independent_test_inventory()
    claim = claim_exactness()
    documents = document_sentinels()
    checks = {
        "I0_independent_resource_integrity": integrity["pass"],
        "I1_independent_requirement_parser": requirements["pass"],
        "I2_independent_claim_chain": claims["pass"],
        "I3_independent_source_gap_audit": gaps["pass"],
        "I4_independent_model_completion_atlas": models["pass"],
        "I5_independent_test_inventory": tests["pass"],
        "I6_claim_exactness": claim["pass"],
        "I7_document_sentinels": documents["pass"],
    }
    return {
        "schema_version": "asmp4_completion_atlas_independent_v0_9",
        "resource_integrity": integrity,
        "canonical_requirements": requirements,
        "claim_chain": claims,
        "source_gaps": gaps,
        "model_completion_atlas": models,
        "test_inventory": tests,
        "claim_exactness": claim,
        "document_sentinels": documents,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
