"""Import-independent verifier for the ASMP-4 v0.15 semantic audit."""

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
V14 = (
    ROOT
    / "asmp4_positive_volume_stop_certificate_v0_14"
    / "positive_volume_stop_claim_v0_14.json"
)
FIXTURES = HERE / "robustness_fixtures_v0_15.json"
ROWS = HERE / "semantic_clause_rows_v0_15.jsonl"
PREFLIGHT = HERE / "preflight_v0_15" / "preflight.json"
STAGE = HERE / "robustness_stage_v0_15" / "stage.json"
ROBUSTNESS = HERE / "robustness_result_v0_15" / "robustness.json"
ADJUDICATION = HERE / "adjudication_queue_v0_15.jsonl"
CLAIM = HERE / "semantic_selector_audit_claim_v0_15.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V14: "cd8257233156f334a03840c5b514ebb84395555263f086a2fbc5b55085ad6375",
    FIXTURES: "4ad8415250b12e91798d9a61e792c0c006a108d5444cd6dc6c40f6d8dea0803c",
}

ARTIFACT_SEALS = {
    HERE
    / "eval_manifest_v0_15.yaml": "adfa2d03e01e3c43d2aaa572cef658c8636259a62e8cf12938749f6bba69f0c6",
    PREFLIGHT: "5420ce423723ed4e06046b1d62f6b45895966b0ea32003b21f420092858f0e8f",
    ROWS: "b5e8c1b16d1abd4b6f65e19a10e591bdd78cff739c5accbe87ecbd79502e0f10",
    HERE
    / "robustness_spec_v0_15.yaml": "34b55d66a39457337a86eab65c53986a5bc87ad2086d9872116c6068a7e651c2",
    STAGE: "9fb2732431412eb536d36fe94410e912bd161b0b1dad2b6d4ee895a2c4497705",
    HERE
    / "robustness_observations_v0_15.jsonl": "717d0229c8dd74d6da26a14aaa12c487e4590e554b355d229c78c8bdd454659b",
    ROBUSTNESS: "3f4dc2a5e11f3500da59063d977f90c48499c8c81cf5526c2e8951b18e0acecf",
    ADJUDICATION: "3981783e54986713d9999db69ed9f17331472b3760cd2ca0292bf97a1f693153",
}

TEST_FILES = (
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
    (
        "asmp4_positive_volume_stop_certificate_v0_14",
        "test_positive_volume_stop.py",
    ),
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def independent_integrity() -> dict[str, Any]:
    rows = []
    for path, expected in SEALS.items():
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append((path.name, observed == expected))
    return {
        "rows": rows,
        "pass": len(rows) == 3 and all(matches for _, matches in rows),
    }


def independent_artifact_integrity() -> dict[str, Any]:
    rows = []
    for path, expected in ARTIFACT_SEALS.items():
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append((path.name, observed == expected))
    return {
        "rows": rows,
        "pass": len(rows) == 8 and all(matches for _, matches in rows),
    }


def independent_adjudication() -> dict[str, Any]:
    rows = _jsonl(ADJUDICATION)
    expected_ids = ["C03", "C04", "C06", "C07", "C08", "C11", "C19", "C22"]
    checks = {
        "eight_rows": len(rows) == 8,
        "exact_ids": [row["item_id"] for row in rows] == expected_ids,
        "seven_ambiguous_one_parameterized": sum(
            row["label"] == "ambiguous" for row in rows
        )
        == 7
        and sum(row["label"] == "selects_parameterized" for row in rows) == 1,
        "all_pending_external": all(
            row["status"] == "pending_external" for row in rows
        ),
        "all_actionable": all(
            row["question"].endswith("?") and bool(row["decision_impact"])
            for row in rows
        ),
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_units() -> list[str]:
    section = (
        SOURCE.read_text(encoding="utf-8")
        .split("# ASMP-4", 1)[1]
        .split("# ASMP-5", 1)[0]
    )
    blocks: list[str] = []
    prose: list[str] = []
    formula: list[str] = []
    fenced = False
    for raw in section.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            if fenced:
                fenced = False
                if formula:
                    blocks[-1] = f"{blocks[-1]} [FORMULA] {' '.join(formula)}"
            else:
                if prose:
                    blocks.append(" ".join(prose))
                    prose = []
                fenced = True
                formula = []
            continue
        if fenced:
            if line:
                formula.append(line)
            continue
        if line.startswith("#") or line == "---":
            continue
        if line:
            prose.append(line)
        elif prose:
            blocks.append(" ".join(prose))
            prose = []
    if prose:
        blocks.append(" ".join(prose))

    units: list[str] = []
    for block in blocks[1:]:
        if block.startswith("1. "):
            units.extend(
                filter(None, (part.strip() for part in re.split(r"(?=\d\. )", block)))
            )
        elif block.startswith("- **"):
            units.extend(
                filter(None, (part.strip() for part in re.split(r"(?=- \*\*)", block)))
            )
        else:
            units.append(block)
    return units


def independent_clause_census() -> dict[str, Any]:
    units = independent_units()
    rows = _jsonl(ROWS)
    exact_rows = []
    for index, (unit, row) in enumerate(zip(units, rows, strict=True), 1):
        exact_rows.append(
            row["item_id"] == f"C{index:02d}"
            and row["text"] == unit
            and row["text_sha256"] == hashlib.sha256(unit.encode("utf-8")).hexdigest()
            and row["source_sha256"] == SEALS[SOURCE]
        )

    blocking_expectations = {
        "C03": ("ambiguous", "registered causal code"),
        "C04": ("ambiguous", "sensor encoder"),
        "C06": ("ambiguous", "there exists a registered causal code"),
        "C07": ("ambiguous", "may be quotiented out"),
        "C08": ("ambiguous", "registered normally hyperbolic"),
        "C11": ("ambiguous", "coordinate-invariant"),
        "C19": ("selects_parameterized", "hold the sensor experiment fixed"),
        "C22": ("ambiguous", "quotient/transversal"),
    }
    by_id = {row["item_id"]: row for row in rows}
    semantic_rows = []
    for item_id, (label, marker) in blocking_expectations.items():
        row = by_id[item_id]
        semantic_rows.append(row["label"] == label and marker in row["text"].casefold())
    counts = {
        label: sum(row["label"] == label for row in rows)
        for label in ("no_selector", "ambiguous", "selects_parameterized")
    }
    checks = {
        "twenty_three_units": len(units) == len(rows) == 23,
        "all_rows_exact": all(exact_rows),
        "eight_blocking_semantic_markers": len(semantic_rows) == 8
        and all(semantic_rows),
        "counts": counts
        == {"no_selector": 15, "ambiguous": 7, "selects_parameterized": 1},
        "no_explicit_raw_or_computed_label": all(
            row["label"] not in {"selects_raw", "selects_computed"} for row in rows
        ),
        "claim_blocked_by_conservative_rule": any(
            row["label"] != "no_selector" for row in rows
        ),
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_preflight() -> dict[str, Any]:
    receipt = _load(PREFLIGHT)
    findings = {row["id"] for row in receipt["findings"]}
    checks = {
        "status_fail": receipt["status"] == "fail" and receipt["release_blocking"],
        "six_findings": receipt["summary"]["finding_count"] == 6,
        "four_blockers": receipt["summary"]["blocking_count"] == 4,
        "fixed_population_finding": "dataset_not_held_out" in findings
        and "dataset_below_policy_minimum" in findings,
        "pairwise_mismatch_findings": {
            "identity_blinding_missing",
            "order_randomization_missing",
            "position_swap_missing",
        }
        <= findings,
        "resolved_design_omissions_absent": "contamination_check_missing"
        not in findings
        and "adapter_deterministic_coverage_gap" not in findings,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_robustness() -> dict[str, Any]:
    stage = _load(STAGE)
    result = _load(ROBUSTNESS)
    family_results = result["metric_robustness"]["family_results"]
    checks = {
        "stage_has_five_families": stage["summary"]["independent_probe_families"] == 5,
        "all_fixture_refs_sealed": all(
            SEALS[FIXTURES] in row["source_ref"] for row in stage["probe_plan"]
        ),
        "all_five_observed": result["task_result"]["observed_probe_rows"] == 5,
        "all_five_passed": result["task_result"]["passed_observation_rows"] == 5,
        "no_repeat_disagreement": result["measurement_reliability"][
            "repeat_disagreement_families"
        ]
        == 0,
        "supported_on_holdout": result["metric_robustness"]["status"]
        == "supported_on_declared_holdout",
        "five_types": {row["probe_type"] for row in family_results}
        == {
            "invariance",
            "sensitivity",
            "monotonicity",
            "anti_gaming",
            "clean_control",
        },
        "all_family_results_pass": all(row["passed"] for row in family_results),
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_claim_audit() -> dict[str, Any]:
    claim = _load(CLAIM)
    checks = {
        "schema": claim["schema_version"]
        == "asmp4_semantic_selector_audit_claim_v0_15",
        "seals": claim["sealed_resources"]
        == {
            "count": 3,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_14_stop_claim_sha256": SEALS[V14],
            "robustness_fixtures_sha256": SEALS[FIXTURES],
        },
        "evaluation_artifacts": claim["evaluation_artifacts"]
        == {
            "eval_manifest_sha256": ARTIFACT_SEALS[HERE / "eval_manifest_v0_15.yaml"],
            "preflight_receipt_sha256": ARTIFACT_SEALS[PREFLIGHT],
            "clause_rows_sha256": ARTIFACT_SEALS[ROWS],
            "robustness_spec_sha256": ARTIFACT_SEALS[
                HERE / "robustness_spec_v0_15.yaml"
            ],
            "robustness_stage_sha256": ARTIFACT_SEALS[STAGE],
            "robustness_observations_sha256": ARTIFACT_SEALS[
                HERE / "robustness_observations_v0_15.jsonl"
            ],
            "robustness_report_sha256": ARTIFACT_SEALS[ROBUSTNESS],
            "adjudication_queue_sha256": ARTIFACT_SEALS[ADJUDICATION],
        },
        "census": claim["clause_census"]
        == {
            "units": 23,
            "no_selector": 15,
            "ambiguous": 7,
            "selects_parameterized": 1,
            "blocking_items": [
                "C03",
                "C04",
                "C06",
                "C07",
                "C08",
                "C11",
                "C19",
                "C22",
            ],
        },
        "metric": claim["metric_robustness"]
        == {"held_out_probe_families": 5, "passed_probe_families": 5},
        "preflight_failed": claim["measurement_reliability"]["pairwise_preflight"]
        == "fail"
        and claim["measurement_reliability"]["release_blocking"] is True,
        "adjudication": claim["adjudication_queue"]
        == {"items": 8, "status": "pending_external"},
        "inventory": claim["predecessor_inventory"] == {"packages": 15, "tests": 184},
        "decision": claim["decision"]
        == "qualify_v014_semantic_claim_retain_scoped_operational_stop",
        "nonclaim": "does not determine the intended formal class" in claim["nonclaim"]
        and "external adjudication" in claim["nonclaim"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_inventory() -> dict[str, Any]:
    rows = []
    for package, filename in TEST_FILES:
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append((package, count))
    total = sum(count for _, count in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": total,
        "pass": len(rows) == 15 and total == 184,
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "audit": HERE / "SEMANTIC_SELECTOR_AUDIT_v0_15.md",
        "result": HERE / "RESULT.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_15.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_15.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").casefold().split())
        for name, path in paths.items()
    }
    checks = {
        "five_layers": all(
            phrase in docs["audit"]
            for phrase in (
                "metric robustness",
                "task result",
                "measurement reliability",
                "claim support",
                "operational decision",
            )
        ),
        "census_counts": "15 no-selector" in docs["audit"]
        and "seven ambiguous" in docs["audit"]
        and "one parameterized" in docs["audit"],
        "preflight_failure": "preflight failed" in docs["audit"],
        "v014_qualified": "v0.14" in docs["result"]
        and "requires qualification" in docs["result"],
        "nonresolution": "does not resolve asmp-4" in docs["result"],
        "expanded_count": "194" in docs["completion"],
        "entrypoints": "run_verification.py" in docs["readme"]
        and "verify_semantic_selector_audit.py" in docs["readme"],
        "review_attack": "falsify v0.15" in docs["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "artifact_integrity": independent_artifact_integrity()["pass"],
        "clause_census": independent_clause_census()["pass"],
        "preflight": independent_preflight()["pass"],
        "metric_robustness": independent_robustness()["pass"],
        "adjudication": independent_adjudication()["pass"],
        "claim": independent_claim_audit()["pass"],
        "inventory": independent_inventory()["pass"],
        "documents": document_sentinels()["pass"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
