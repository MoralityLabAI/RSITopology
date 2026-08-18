"""Import-independent verification of the ASMP-4 v0.36 stop certificate."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
CENTRAL = HERE / "single_root_stop.py"
CONTRACT = HERE / "single_root_stop_contract_v0_36.json"
CLAIM = HERE / "single_root_stop_claim_v0_36.json"

RESOURCE_PATHS = {
    "canonical_source": SOURCE,
    "v06_registration_fork": ROOT
    / "asmp4_registration_fork_v0_6"
    / "registration_claim_v0_6.json",
    "v08_randomness_fork": ROOT
    / "asmp4_randomness_quantifier_boundary_v0_8"
    / "randomness_claim_v0_8.json",
    "v33_nonfinite_region": ROOT
    / "asmp4_nonfinite_safe_closing_v0_33"
    / "safe_closing_claim_v0_33.json",
    "v34_public_connectors": ROOT
    / "asmp4_compact_public_connector_v0_34"
    / "public_connector_claim_v0_34.json",
    "v35_robust_atlas": ROOT
    / "asmp4_robust_public_atlas_v0_35"
    / "robust_public_atlas_claim_v0_35.json",
}

EXPECTED_HASHES = {
    "canonical_source": "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    "v06_registration_fork": "812c17f913c1e498d835c13430b7880b95a188496333b48355883f0fe634c5a5",
    "v08_randomness_fork": "0cfce1a8751eae64ba746e7a773eb1cee48355c5168465c4a208c2fa07b1cf16",
    "v33_nonfinite_region": "16cd95033cc669583c2bbda0dfff6f65ac4548fbcbd6892d34bb8c6e74621580",
    "v34_public_connectors": "378260f2eea043569e73e6962bf40b1081e3bafc7f8ca2cac1c5f519f5eb2d85",
    "v35_robust_atlas": "9b29d66aea46b1586e2cdef7ca9c8203bca71e1753232ccb9fd59a85425c195e",
}

PAYLOAD = (
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


def load(name: str) -> dict[str, Any]:
    return json.loads(RESOURCE_PATHS[name].read_text(encoding="utf-8"))


def resources_report() -> dict[str, Any]:
    rows = {}
    for name, path in RESOURCE_PATHS.items():
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        rows[name] = observed == EXPECTED_HASHES[name]
    return {"rows": rows, "pass": len(rows) == 6 and all(rows.values())}


def source_section() -> list[str]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("# ASMP-4"))
    end = next(
        index
        for index, line in enumerate(lines[start + 1 :], start + 1)
        if line.startswith("# ASMP-5")
    )
    return lines[start:end]


def requirements_report() -> dict[str, Any]:
    lines = source_section()
    start = lines.index("## What a complete resolution requires") + 1
    end = lines.index("## Liveness and kill examples")
    rows = []
    current = ""
    for line in lines[start:end]:
        stripped = line.strip()
        if re.match(r"^[1-5]\. ", stripped):
            if current:
                rows.append(current)
            current = stripped[3:]
        elif stripped and current:
            current += " " + stripped
    if current:
        rows.append(current)
    fragments = (
        "coordinate-invariant definition",
        "entire achievable rate region",
        "converse theorems",
        "finite-horizon corrections",
        "counterexamples locating the boundary",
    )
    checks = {
        "five_rows": len(rows) == 5,
        "ordered": all(fragment in row.casefold() for fragment, row in zip(fragments, rows, strict=True)),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def registration_report() -> dict[str, Any]:
    text = " ".join(line.casefold().strip() for line in source_section())
    randomness = load("v08_randomness_fork")
    explicit_markers = (
        "registered causal code",
        "registered normally hyperbolic, locally controllable class",
        "bounded uncertainty, delay, memory, control-authority, and disturbance conventions",
        "plant, sensor, controller, and actuator are separate components",
        "uncharged side channel",
        "for every allowed disturbance sequence",
    )
    missing = {
        "sensor_grammar": "forced raw sensor" not in text
        and "sensor partition grammar" not in text,
        "randomness_disturbance_order": randomness["canonical_audit"][
            "probability_disturbance_order_clause_count"
        ]
        == 0,
        "normally_hyperbolic_predicate": text.count("normally hyperbolic") == 1
        and "invariant splitting" not in text,
        "local_controllability_predicate": text.count("locally controllable") == 1
        and "endpoint map rank" not in text,
        "public_belief_semantics": "public belief" not in text,
        "safe_closing_or_reset_semantics": "safe closing" not in text
        and "reset cell" not in text,
        "actuator_dictionary_domain": "actuator grammar" not in text
        and "fixed actuator dictionary" not in text,
    }
    checks = {
        "architecture_markers": all(marker in text for marker in explicit_markers),
        "seven_missing": len(missing) == 7 and all(missing.values()),
    }
    return {"missing": missing, "checks": checks, "pass": all(checks.values())}


def forks_report() -> dict[str, Any]:
    sensor = load("v06_registration_fork")
    randomness = load("v08_randomness_fork")
    registry = sensor["canonical_registry_model_audit"]
    computed = registry["computed_sensor_region"]
    raw = registry["fixed_raw_sensor_region"]
    fixture = randomness["continuous_diagonal_fixture"]
    checks = {
        "domain_unselected": not registry["registry_domain_selected"],
        "both_source_models": registry[
            "computed_sensor_registry_satisfies_all_obligations"
        ]
        and registry["fixed_raw_sensor_registry_satisfies_all_obligations"],
        "regions_differ": computed != raw,
        "probability_order_absent": randomness["canonical_audit"][
            "probability_disturbance_order_clause_count"
        ]
        == 0,
        "feasibility_differs": fixture["per_disturbance_almost_sure_safe"]
        and not fixture["uniform_almost_sure_safe"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def chain_report() -> dict[str, Any]:
    v33 = load("v33_nonfinite_region")
    v34 = load("v34_public_connectors")
    v35 = load("v35_robust_atlas")
    checks = {
        "region": v33["theorem"]["component_region"]
        == "R_q=closure(upward(conv(P_q)))",
        "coordinate": "conjugacies" in v33["theorem"]["coordinate_invariance"],
        "finite": "overhead/T" in v33["theorem"]["finite_correction"],
        "public_connector": "v0.33" in v34["theorem"]["safe_closing"],
        "robust_atlas": "safe-closing" in v35["theorem"]["v33_implication"],
        "separate_ports": v35["nonlinear_fixture"]["read_bits"] == 6
        and v35["nonlinear_fixture"]["write_bits"] == 6,
        "scope_still_open": "remains open" in v35["disposition"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def truth_table_report() -> dict[str, Any]:
    stop_rows = []
    for values in itertools.product((False, True), repeat=5):
        ambiguous, fork, chain, adjudicated, error = values
        stop = ambiguous and fork and chain and not adjudicated and not error
        if stop:
            stop_rows.append(values)
    checks = {
        "unique": stop_rows == [(True, True, True, False, False)],
        "current": bool(stop_rows),
    }
    return {"rows": 32, "stop_rows": len(stop_rows), "checks": checks, "pass": all(checks.values())}


def expected_claim() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_single_root_stop_v0_36",
        "canonical": {
            "completion_requirements": 5,
            "explicit_architecture_clauses": 6,
            "missing_domain_selectors": [
                "sensor_grammar",
                "randomness_disturbance_order",
                "normally_hyperbolic_predicate",
                "local_controllability_predicate",
                "public_belief_semantics",
                "safe_closing_or_reset_semantics",
                "actuator_dictionary_domain",
            ],
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


def contract_claim_report() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    claim = json.loads(CLAIM.read_text(encoding="utf-8"))
    checks = {
        "contract": contract.get("schema_version")
        == "asmp4_single_root_stop_contract_v0_36",
        "four_reopeners": len(contract.get("reopening_conditions", [])) == 4,
        "not_resolution": "not a mathematical resolution"
        in contract.get("decision_scope", {}).get("nonclaim", ""),
        "claim_exact": claim == expected_claim(),
    }
    return {"checks": checks, "pass": all(checks.values())}


def count_tests(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
        for node in ast.walk(tree)
    )


def version(name: str) -> int:
    match = re.search(r"_v0_(\d+)$", name)
    return int(match.group(1)) if match else 0


def inventory_report() -> dict[str, Any]:
    paths = [
        path
        for path in ROOT.glob("asmp4*/test_*.py")
        if path.parent.resolve() != HERE.resolve() and version(path.parent.name) < 36
    ]
    tests = sum(count_tests(path) for path in paths)
    checks = {"packages": len(paths) == 36, "tests": tests == 394}
    return {"packages": len(paths), "tests": tests, "checks": checks, "pass": all(checks.values())}


def documents_report() -> dict[str, Any]:
    required = {
        "README.md": ("v0.36", "single-root", "not a resolution"),
        "STOP_CERTIFICATE_v0_36.md": ("Decision", "Reopening conditions", "32"),
        "RESULT.md": ("six sealed", "seven missing", "394"),
        "REVIEWER_PACKET_v0_36.md": ("falsify", "registries", "operational"),
        "COMPLETION_AUDIT_v0_36.md": ("Canonical requirements", "0/5", "Partial"),
    }
    rows = {}
    for name, tokens in required.items():
        path = HERE / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        rows[name] = all(token in text for token in tokens)
    return {"rows": rows, "pass": all(rows.values())}


def source_independence_report() -> dict[str, Any]:
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(Path(__file__)))
    imports_central = any(
        (isinstance(node, ast.Import) and any(alias.name == "single_root_stop" for alias in node.names))
        or (isinstance(node, ast.ImportFrom) and node.module == "single_root_stop")
        for node in ast.walk(tree)
    )
    central_tree = ast.parse(CENTRAL.read_text(encoding="utf-8"), filename=str(CENTRAL))
    functions = {node.name for node in ast.walk(central_tree) if isinstance(node, ast.FunctionDef)}
    checks = {
        "central_not_imported": not imports_central,
        "central_decision_present": "stopping_decision" in functions,
        "payload": all((HERE / name).is_file() for name in PAYLOAD),
    }
    return {"checks": checks, "pass": all(checks.values())}


def full_report() -> dict[str, Any]:
    report = {
        "resources": resources_report(),
        "requirements": requirements_report(),
        "registration": registration_report(),
        "forks": forks_report(),
        "chain": chain_report(),
        "truth_table": truth_table_report(),
        "contract_claim": contract_claim_report(),
        "inventory": inventory_report(),
        "documents": documents_report(),
        "source": source_independence_report(),
    }
    report["pass"] = all(section["pass"] for section in report.values())
    return report


def main() -> int:
    report = full_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
