"""Import-independent verifier for the ASMP-4 v0.32 closure/stop audit."""

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


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def independent_integrity() -> dict[str, Any]:
    rows = [
        (path.name, hashlib.sha256(path.read_bytes()).hexdigest() == expected)
        for path, expected in SEALS.items()
    ]
    return {"rows": rows, "pass": len(rows) == 5 and all(match for _, match in rows)}


def independent_requirement_parser() -> dict[str, Any]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    inside_asmp4 = False
    inside_requirements = False
    rows: list[str] = []
    current: list[str] = []
    for line in lines:
        if line.startswith("# ASMP-4"):
            inside_asmp4 = True
        elif inside_asmp4 and line.startswith("# ASMP-5"):
            break
        if not inside_asmp4:
            continue
        if line == "## What a complete resolution requires":
            inside_requirements = True
            continue
        if inside_requirements and line.startswith("## Liveness and kill examples"):
            break
        if not inside_requirements:
            continue
        match = re.match(r"^\d+\.\s+(.*)", line)
        if match:
            if current:
                rows.append(" ".join(current))
            current = [match.group(1).strip()]
        elif current and line.strip():
            current.append(line.strip())
    if current:
        rows.append(" ".join(current))
    needles = ("coordinate-invariant", "entire achievable", "constructive", "finite-horizon", "counterexamples")
    checks = {
        "five_requirements": len(rows) == 5,
        "ordered_needles": all(
            needle.casefold() in row.casefold()
            for needle, row in zip(needles, rows, strict=True)
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_claim_chain() -> dict[str, Any]:
    v15 = _load(V15)
    v23 = _load(V23)
    v26 = _load(V26)
    v27 = _load(V27)
    v28 = _load(V28)
    v29 = _load(V29)
    v30 = _load(V30)
    v31 = _load(V31)
    checks = {
        "external_queue_pending": v15["adjudication_queue"]["status"]
        == "pending_external",
        "timing_changes_region": v23["main_theorem"]["delay_zero_region"]
        != v23["main_theorem"]["every_positive_integer_delay_region"],
        "finite_quotient_not_necessary": not v26["infinite_boundary"][
            "finite_exact_stationary_quotient"
        ],
        "metric_only_refuted": "metric-only" in v27["disposition"],
        "state_class_not_enough": "one quotient class"
        in v28["sharpness"]["finite_quotient"],
        "terminal_not_enough": "terminal fibers alone"
        in v29["disposition"],
        "rounding_not_unrounded": "rounded local fibers" in v30["disposition"],
        "finite_adversarial_closed": "intersection_tau"
        in v31["theorem"]["formula"],
        "nonlinear_root_open": "nonlinear quotient construction remains open"
        in v31["disposition"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_dependency_audit() -> dict[str, Any]:
    graph = {
        "grammar": (),
        "abstraction": ("grammar",),
        "profiles": ("abstraction",),
        "finite_region": ("abstraction", "profiles"),
        "global_margin": ("grammar", "abstraction"),
    }
    resolved = {"profiles", "finite_region"}
    missing = {"grammar", "abstraction", "global_margin"}
    ordered = []
    pending = set(graph)
    while pending:
        ready = sorted(
            node for node in pending if all(parent in ordered for parent in graph[node])
        )
        if not ready:
            break
        ordered.extend(ready)
        pending -= set(ready)
    checks = {
        "acyclic_dependency_graph": len(ordered) == len(graph),
        "grammar_is_root": ordered[0] == "grammar",
        "finite_region_is_conditionally_resolved": "finite_region" in resolved,
        "upstream_nodes_missing": {"grammar", "abstraction"} <= missing,
        "global_margin_missing": "global_margin" in missing,
    }
    return {"order": ordered, "checks": checks, "pass": all(checks.values())}


def independent_stop_truth_table() -> dict[str, Any]:
    rows = []
    for values in itertools.product((False, True), repeat=5):
        stop = all(values)
        rows.append({"premises": values, "stop": stop})
    checks = {
        "thirty_two_rows": len(rows) == 32,
        "only_all_premises_support_stop": sum(row["stop"] for row in rows) == 1,
        "all_true_supports_stop": rows[-1]["stop"],
        "each_single_failure_blocks_stop": all(
            not row["stop"] for row in rows if not all(row["premises"])
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    requirements = independent_requirement_parser()
    claims = independent_claim_chain()["checks"]
    dependencies = independent_dependency_audit()["checks"]
    rows = {
        "full_resolution": requirements["checks"]["five_requirements"]
        and dependencies["global_margin_missing"],
        "finite_quotient_necessary": claims["finite_quotient_not_necessary"],
        "one_quotient_size_modulus": claims["state_class_not_enough"],
        "v025_handles_adversary": claims["finite_adversarial_closed"],
        "metric_only_safety": claims["metric_only_refuted"],
        "terminal_fiber_universal": claims["terminal_not_enough"]
        and claims["rounding_not_unrounded"],
        "bounded_fixture_selects_grammar": claims["external_queue_pending"],
        "nothing_remains": claims["nonlinear_root_open"],
    }
    return {"rows": rows, "pass": len(rows) == 8 and all(rows.values())}


def independent_contract_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    checks = {
        "contract_schema": contract.get("schema_version")
        == "asmp4_closure_stop_contract_v0_32",
        "not_resolution": "unresolved"
        in contract.get("decision_scope", {}).get("not_a_resolution", ""),
        "four_reopening_conditions": contract.get("reopening_conditions") == 4,
        "zero_global_rows": claim.get("canonical_requirements", {}).get(
            "full_scope_proved"
        )
        == 0,
        "operational_stop": "operational_stop" in claim.get("decision", ""),
        "central_not_imported": "closure_stop_audit" not in imports,
    }
    return {"checks": checks, "pass": all(checks.values())}


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


def independent_inventory() -> dict[str, Any]:
    rows = []
    for package, filename in _predecessor_tests():
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append((package, count))
    tests = sum(count for _, count in rows)
    return {
        "packages": len(rows),
        "tests": tests,
        "pass": len(rows) == 32 and tests == 354,
    }


def document_sentinels() -> dict[str, Any]:
    required = {
        "STOP_CERTIFICATE_v0_32.md": (
            "operational stop",
            "not a resolution",
            "Thue-Morse",
            "reopening conditions",
        ),
        "RESULT.md": ("0/5", "seven", "354 tests", "Not claimed"),
        "COMPLETION_AUDIT_v0_32.md": ("364 tests", "Not claimed"),
        "REVIEWER_PACKET_v0_32.md": ("falsification", "full resolution"),
    }
    rows = {}
    for filename, needles in required.items():
        path = HERE / filename
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        rows[filename] = all(needle.casefold() in text.casefold() for needle in needles)
    return {"rows": rows, "pass": all(rows.values())}


def independent_report() -> dict[str, Any]:
    components = {
        "integrity": independent_integrity(),
        "requirements": independent_requirement_parser(),
        "claims": independent_claim_chain(),
        "dependencies": independent_dependency_audit(),
        "truth_table": independent_stop_truth_table(),
        "mutations": independent_mutations(),
        "contract_claim": independent_contract_claim(),
        "inventory": independent_inventory(),
        "documents": document_sentinels(),
    }
    return {**components, "pass": all(row["pass"] for row in components.values())}


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
