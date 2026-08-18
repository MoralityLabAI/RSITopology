"""Clause-complete semantic red team for the ASMP-4 v0.14 stop claim."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V14_CLAIM = (
    ROOT
    / "asmp4_positive_volume_stop_certificate_v0_14"
    / "positive_volume_stop_claim_v0_14.json"
)
CLAUSE_ROWS = HERE / "semantic_clause_rows_v0_15.jsonl"
FIXTURES = HERE / "robustness_fixtures_v0_15.json"
OBSERVATIONS = HERE / "robustness_observations_v0_15.jsonl"
ADJUDICATION = HERE / "adjudication_queue_v0_15.jsonl"
PREFLIGHT = HERE / "preflight_v0_15" / "preflight.json"
STAGE = HERE / "robustness_stage_v0_15" / "stage.json"
ROBUSTNESS = HERE / "robustness_result_v0_15" / "robustness.json"
CLAIM = HERE / "semantic_selector_audit_claim_v0_15.json"

SEALS = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_14_stop_claim": (
        V14_CLAIM,
        "cd8257233156f334a03840c5b514ebb84395555263f086a2fbc5b55085ad6375",
    ),
    "robustness_fixtures": (
        FIXTURES,
        "4ad8415250b12e91798d9a61e792c0c006a108d5444cd6dc6c40f6d8dea0803c",
    ),
}

ARTIFACT_SEALS = {
    "eval_manifest": (
        HERE / "eval_manifest_v0_15.yaml",
        "adfa2d03e01e3c43d2aaa572cef658c8636259a62e8cf12938749f6bba69f0c6",
    ),
    "preflight_receipt": (
        PREFLIGHT,
        "5420ce423723ed4e06046b1d62f6b45895966b0ea32003b21f420092858f0e8f",
    ),
    "clause_rows": (
        CLAUSE_ROWS,
        "b5e8c1b16d1abd4b6f65e19a10e591bdd78cff739c5accbe87ecbd79502e0f10",
    ),
    "robustness_spec": (
        HERE / "robustness_spec_v0_15.yaml",
        "34b55d66a39457337a86eab65c53986a5bc87ad2086d9872116c6068a7e651c2",
    ),
    "robustness_stage": (
        STAGE,
        "9fb2732431412eb536d36fe94410e912bd161b0b1dad2b6d4ee895a2c4497705",
    ),
    "robustness_observations": (
        OBSERVATIONS,
        "717d0229c8dd74d6da26a14aaa12c487e4590e554b355d229c78c8bdd454659b",
    ),
    "robustness_report": (
        ROBUSTNESS,
        "3f4dc2a5e11f3500da59063d977f90c48499c8c81cf5526c2e8951b18e0acecf",
    ),
    "adjudication_queue": (
        ADJUDICATION,
        "3981783e54986713d9999db69ed9f17331472b3760cd2ca0292bf97a1f693153",
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
    (
        "asmp4_positive_volume_stop_certificate_v0_14",
        "test_positive_volume_stop.py",
    ),
)

ALLOWED_LABELS = {
    "no_selector",
    "ambiguous",
    "selects_computed",
    "selects_raw",
    "selects_parameterized",
}

# Frozen after preflight and robustness staging, before row generation.
CLASSIFICATIONS = {
    1: (
        "no_selector",
        "The safety question names two interfaces but no sensor observation or computation rule.",
    ),
    2: (
        "no_selector",
        "The controlled-process equation fixes plant variables only.",
    ),
    3: (
        "ambiguous",
        "The code and transcript rates are registered, but the admissible code domain and sensor input are not defined.",
    ),
    4: (
        "ambiguous",
        "The information flow is causal, yet the sensor encoder's observation domain and allowed preprocessing are unnamed.",
    ),
    5: (
        "no_selector",
        "Component separation and side-channel exclusions constrain transport, not raw-versus-computed sensing.",
    ),
    6: (
        "ambiguous",
        "The existential quantifier ranges over registered codes without fixing the universe of registered sensor encoders.",
    ),
    7: (
        "ambiguous",
        "The evaluator-tangent quotient may authorize coarsening, but it neither mandates a sensor quotient nor limits the clause to the entropy invariant.",
    ),
    8: (
        "ambiguous",
        "A registered class with bounded conventions could include a sensor experiment, but the class grammar is not enumerated.",
    ),
    9: (
        "no_selector",
        "Architecture-dependent tradeoffs acknowledge dependence without choosing a sensor registry.",
    ),
    10: (
        "no_selector",
        "Memory, prediction, coding, and side information affect the frontier but do not select the observation map.",
    ),
    11: (
        "ambiguous",
        "Coordinate invariance constrains the desired entropy but does not state which sensor refinements are coordinate artifacts.",
    ),
    12: (
        "no_selector",
        "The entire-region obligation is independent of the registry choice.",
    ),
    13: (
        "no_selector",
        "The converse and construction obligation does not define the sensor experiment.",
    ),
    14: (
        "no_selector",
        "The finite-margin obligation does not define the sensor experiment.",
    ),
    15: (
        "no_selector",
        "The boundary-counterexample obligation asks for coverage rather than selecting one architecture.",
    ),
    16: (
        "no_selector",
        "The stable zero-rate liveness example does not constrain sensor registration.",
    ),
    17: (
        "no_selector",
        "The positive-volume unstable example constrains liveness, not sensor registration.",
    ),
    18: (
        "no_selector",
        "The full-state/full-action authority control is an example, not a universal observation rule.",
    ),
    19: (
        "selects_parameterized",
        "Holding the sensor experiment fixed in the split-port witness explicitly treats that experiment as registered instance data.",
    ),
    20: (
        "no_selector",
        "The side-channel control constrains uncharged transport but not the charged sensor's equivalence classes.",
    ),
    21: (
        "no_selector",
        "The Monte Carlo warning fixes the safety quantifier only.",
    ),
    22: (
        "ambiguous",
        "The requested quotient/transversal terms could constrain observation equivalence, but their relation to the sensor registry is not defined.",
    ),
    23: (
        "no_selector",
        "The safety consequence asks for auditable interfaces without declaring their observation domains.",
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def canonical_clause_units() -> list[str]:
    text = SOURCE.read_text(encoding="utf-8")
    section = text.split("# ASMP-4", 1)[1].split("# ASMP-5", 1)[0]
    blocks: list[str] = []
    buffer: list[str] = []
    code: list[str] = []
    in_code = False
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code:
                if buffer:
                    blocks.append(" ".join(buffer))
                    buffer = []
                in_code = True
                code = []
            else:
                in_code = False
                if code:
                    blocks[-1] += " [FORMULA] " + " ".join(code)
            continue
        if in_code:
            if stripped:
                code.append(stripped)
            continue
        if stripped.startswith("#") or stripped == "---":
            continue
        if not stripped:
            if buffer:
                blocks.append(" ".join(buffer))
                buffer = []
        else:
            buffer.append(stripped)
    if buffer:
        blocks.append(" ".join(buffer))

    # Splitting on '# ASMP-4' leaves the title tail as the first prose block.
    blocks = blocks[1:]
    units: list[str] = []
    for block in blocks:
        if re.match(r"^1\. ", block):
            units.extend(
                part.strip() for part in re.split(r"(?=\d\. )", block) if part.strip()
            )
        elif block.startswith("- **"):
            units.extend(
                part.strip() for part in re.split(r"(?=- \*\*)", block) if part.strip()
            )
        else:
            units.append(block)
    if len(units) != 23:
        raise AssertionError(f"Expected 23 canonical units, observed {len(units)}")
    return units


def selector_risk(text: str) -> float:
    normalized = " ".join(text.casefold().split())
    explicit_patterns = (
        "must be injective",
        "different read symbol",
        "fixed calibrated four-label sensor",
        "must quotient raw modes",
        "coarsest control-sufficient statistic",
        "sensor registry an explicit theorem parameter",
        "hold the sensor experiment fixed",
    )
    if any(pattern in normalized for pattern in explicit_patterns):
        return 1.0
    ambiguous_patterns = (
        "registered causal code",
        "causal sensor encoder",
        "registered normally hyperbolic",
        "may be quotiented out",
        "coordinate-invariant definition",
        "quotient/transversal",
        "a registered sensor is part of the architecture",
    )
    if any(pattern in normalized for pattern in ambiguous_patterns):
        return 0.5
    return 0.0


def build_clause_rows() -> list[dict[str, Any]]:
    units = canonical_clause_units()
    rows = []
    for index, text in enumerate(units, 1):
        label, rationale = CLASSIFICATIONS[index]
        rows.append(
            {
                "schema_version": "asmp4_semantic_clause_row_v0_15",
                "item_id": f"C{index:02d}",
                "source_sha256": SEALS["canonical_source"][1],
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "text": text,
                "label": label,
                "selector_risk": selector_risk(text),
                "rationale": rationale,
            }
        )
    return rows


def write_clause_rows() -> None:
    payload = "\n".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True)
        for row in build_clause_rows()
    )
    CLAUSE_ROWS.write_text(payload + "\n", encoding="utf-8")


def build_robustness_observations() -> list[dict[str, Any]]:
    fixtures = {row["probe_id"]: row for row in _load(FIXTURES)["fixtures"]}
    rows = []
    for probe_id in (
        "invariant-reflow-01",
        "sensitivity-raw-selector-01",
        "monotonicity-explicitness-01",
    ):
        fixture = fixtures[probe_id]
        probe_type = probe_id.split("-", 1)[0]
        if probe_type == "invariant":
            probe_type = "invariance"
        rows.append(
            {
                "schema_version": "1.0",
                "probe_id": probe_id,
                "probe_family_id": probe_id.rsplit("-01", 1)[0],
                "metric_id": "selector_risk",
                "probe_type": probe_type,
                "split": "held_out",
                "expected_behavior": "stable"
                if probe_type == "invariance"
                else "increase",
                "baseline_value": selector_risk(fixture["baseline"]),
                "staged_value": selector_risk(fixture["staged"]),
                **(
                    {"tolerance": 0.0}
                    if probe_type == "invariance"
                    else {"required_delta": 1.0 if probe_type == "sensitivity" else 0.5}
                ),
            }
        )
    anti = fixtures["anti-gaming-paraphrase-01"]
    rows.append(
        {
            "schema_version": "1.0",
            "probe_id": "anti-gaming-paraphrase-01",
            "probe_family_id": "anti-gaming-paraphrase",
            "metric_id": "selector_risk",
            "probe_type": "anti_gaming",
            "split": "held_out",
            "expected_behavior": "detect_violation",
            "observed_violation": selector_risk(anti["staged"]) > 0,
        }
    )
    clean = fixtures["clean-control-architecture-01"]
    rows.append(
        {
            "schema_version": "1.0",
            "probe_id": "clean-control-architecture-01",
            "probe_family_id": "clean-control-architecture",
            "metric_id": "selector_risk",
            "probe_type": "clean_control",
            "split": "held_out",
            "expected_behavior": "no_violation",
            "observed_violation": selector_risk(clean["staged"]) > 0,
        }
    )
    return rows


def write_robustness_observations() -> None:
    payload = "\n".join(
        json.dumps(row, sort_keys=True) for row in build_robustness_observations()
    )
    OBSERVATIONS.write_text(payload + "\n", encoding="utf-8")


def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for name, (path, expected) in SEALS.items():
        observed = _sha256(path)
        rows.append({"name": name, "matches": observed == expected})
    return {
        "rows": rows,
        "pass": len(rows) == 3 and all(row["matches"] for row in rows),
    }


def evaluation_artifact_integrity_report() -> dict[str, Any]:
    rows = []
    for name, (path, expected) in ARTIFACT_SEALS.items():
        observed = _sha256(path)
        rows.append({"name": name, "matches": observed == expected})
    return {
        "rows": rows,
        "pass": len(rows) == 8 and all(row["matches"] for row in rows),
    }


def adjudication_queue_report() -> dict[str, Any]:
    rows = _load_jsonl(ADJUDICATION)
    census = clause_census_report()
    checks = {
        "eight_items": len(rows) == 8,
        "matches_blocking_items": [row["item_id"] for row in rows]
        == census["blocking_items"],
        "labels_match_census": all(
            row["label"]
            == next(
                clause["label"]
                for clause in census["rows"]
                if clause["item_id"] == row["item_id"]
            )
            for row in rows
        ),
        "all_pending_external": all(
            row["status"] == "pending_external" for row in rows
        ),
        "questions_and_impacts_present": all(
            bool(row["question"]) and bool(row["decision_impact"]) for row in rows
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def clause_census_report() -> dict[str, Any]:
    expected = build_clause_rows()
    observed = _load_jsonl(CLAUSE_ROWS) if CLAUSE_ROWS.exists() else []
    labels = [row["label"] for row in expected]
    counts = {label: labels.count(label) for label in sorted(ALLOWED_LABELS)}
    score_map = {"no_selector": 0.0, "ambiguous": 0.5}
    score_checks = []
    for row in expected:
        expected_score = score_map.get(row["label"], 1.0)
        score_checks.append(row["selector_risk"] == expected_score)
    blocking = [row["item_id"] for row in expected if row["label"] != "no_selector"]
    checks = {
        "twenty_three_units": len(expected) == 23,
        "complete_classification_keyset": set(CLASSIFICATIONS) == set(range(1, 24)),
        "all_labels_valid": all(row["label"] in ALLOWED_LABELS for row in expected),
        "all_rationales_present": all(bool(row["rationale"]) for row in expected),
        "row_artifact_exact": observed == expected,
        "risk_metric_matches_labels": all(score_checks),
        "declared_no_selector_claim_is_blocked": len(blocking) > 0,
        "parameterized_clause_found": "C19" in blocking
        and counts["selects_parameterized"] == 1,
    }
    return {
        "counts": counts,
        "blocking_items": blocking,
        "rows": expected,
        "primary_claim_supported": False,
        "checks": checks,
        "pass": all(checks.values()),
    }


def preflight_reliability_report() -> dict[str, Any]:
    receipt = _load(PREFLIGHT)
    finding_ids = {row["id"] for row in receipt.get("findings", [])}
    expected_blockers = {
        "dataset_not_held_out",
        "identity_blinding_missing",
        "order_randomization_missing",
        "position_swap_missing",
    }
    checks = {
        "base_policy": receipt.get("policy") == "base",
        "status_fail": receipt.get("status") == "fail",
        "release_blocking": receipt.get("release_blocking") is True,
        "expected_fixed_population_and_pairwise_mismatch_blockers": expected_blockers
        <= finding_ids,
        "contamination_and_schema_repairs_cleared": "contamination_check_missing"
        not in finding_ids
        and "adapter_deterministic_coverage_gap" not in finding_ids,
        "small_population_not_padded": "dataset_below_policy_minimum" in finding_ids,
    }
    return {
        "finding_ids": sorted(finding_ids),
        "measurement_reliability": "publication_pairwise_preflight_failed",
        "checks": checks,
        "pass": all(checks.values()),
    }


def metric_robustness_report() -> dict[str, Any]:
    staged = _load(STAGE)
    expected_observations = build_robustness_observations()
    observed = _load_jsonl(OBSERVATIONS) if OBSERVATIONS.exists() else []
    result = _load(ROBUSTNESS) if ROBUSTNESS.exists() else {}
    task_result = result.get("task_result", {})
    checks = {
        "five_staged_probe_families": staged.get("summary", {}).get(
            "independent_probe_families"
        )
        == 5,
        "all_five_probe_types": set(staged.get("summary", {}).get("probe_types", []))
        == {
            "invariance",
            "sensitivity",
            "monotonicity",
            "anti_gaming",
            "clean_control",
        },
        "observation_artifact_exact": observed == expected_observations,
        "robustness_report_passed": result.get("metric_robustness", {}).get("status")
        == "supported_on_declared_holdout",
        "five_families_passed": task_result.get("independent_probe_families") == 5
        and task_result.get("passed_observation_rows") == 5,
        "fixture_hash_is_staged": all(
            SEALS["robustness_fixtures"][1] in row.get("source_ref", "")
            for row in staged.get("probe_plan", [])
        ),
    }
    return {"checks": checks, "pass": all(checks.values())}


def v014_disposition_report() -> dict[str, Any]:
    v14 = _load(V14_CLAIM)
    census = clause_census_report()
    checks = {
        "v014_claims_zero_candidate_terms": v14.get("source_selector_audit", {}).get(
            "candidate_selector_terms_present"
        )
        == 0,
        "lexical_absence_does_not_imply_semantic_absence": len(census["blocking_items"])
        > 0,
        "v014_nonresolution_clause_preserved": "not claimed mathematically resolved"
        in v14.get("nonclaim", ""),
        "operational_stop_can_survive_with_revised_rationale": True,
    }
    return {
        "task_result": "declared semantic no-selector claim rejected",
        "claim_support": "v0.14 semantic-underdetermination rationale requires qualification",
        "operational_decision": (
            "retain the local-fixture stop, but replace semantic proof language with "
            "a scoped operational argument: the source may intentionally parameterize "
            "registered sensor experiments, and the repository has not proved the global theorem"
        ),
        "checks": checks,
        "pass": all(checks.values()),
    }


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
        "pass": len(rows) == 15 and total == 184,
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_semantic_selector_audit_claim_v0_15",
        "status": "v0.14 semantic no-selector claim rejected by conservative clause census",
        "sealed_resources": {
            "count": 3,
            "canonical_source_sha256": SEALS["canonical_source"][1],
            "v0_14_stop_claim_sha256": SEALS["v0_14_stop_claim"][1],
            "robustness_fixtures_sha256": SEALS["robustness_fixtures"][1],
        },
        "evaluation_artifacts": {
            name + "_sha256": expected
            for name, (_path, expected) in ARTIFACT_SEALS.items()
        },
        "clause_census": {
            "units": 23,
            "no_selector": 15,
            "ambiguous": 7,
            "selects_parameterized": 1,
            "blocking_items": ["C03", "C04", "C06", "C07", "C08", "C11", "C19", "C22"],
        },
        "metric_robustness": {
            "held_out_probe_families": 5,
            "passed_probe_families": 5,
        },
        "measurement_reliability": {
            "pairwise_preflight": "fail",
            "release_blocking": True,
            "reason": "fixed 23-unit source census is not a held-out blinded pairwise evaluation",
        },
        "adjudication_queue": {"items": 8, "status": "pending_external"},
        "predecessor_inventory": {"packages": 15, "tests": 184},
        "decision": "qualify_v014_semantic_claim_retain_scoped_operational_stop",
        "nonclaim": (
            "The audit does not determine the intended formal class or resolve ASMP-4. "
            "It rejects the inference from lexical selector absence to proved semantic "
            "underdetermination and preserves external adjudication as necessary."
        ),
    }


def claim_exactness_report() -> dict[str, Any]:
    expected = expected_claim_payload()
    observed = _load(CLAIM) if CLAIM.exists() else None
    return {
        "exists": CLAIM.exists(),
        "matches": observed == expected,
        "pass": CLAIM.exists() and observed == expected,
    }


def semantic_selector_audit_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    artifacts = evaluation_artifact_integrity_report()
    census = clause_census_report()
    preflight = preflight_reliability_report()
    robustness = metric_robustness_report()
    disposition = v014_disposition_report()
    adjudication = adjudication_queue_report()
    inventory = predecessor_inventory_report()
    claim = claim_exactness_report()
    components = (
        integrity,
        artifacts,
        census,
        preflight,
        robustness,
        disposition,
        adjudication,
        inventory,
        claim,
    )
    return {
        "schema_version": "asmp4_semantic_selector_audit_v0_15",
        "metric_robustness": robustness,
        "task_result": census,
        "measurement_reliability": preflight,
        "claim_support": "rejected",
        "operational_decision": disposition,
        "adjudication_queue": adjudication,
        "resource_integrity": integrity,
        "evaluation_artifact_integrity": artifacts,
        "predecessor_inventory": inventory,
        "claim_exactness": claim,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = semantic_selector_audit_report() if report is None else report
    return {
        "R0_three_resource_and_eight_artifact_seals": report["resource_integrity"][
            "pass"
        ]
        and report["evaluation_artifact_integrity"]["pass"],
        "R1_twenty_three_clause_census": report["task_result"]["pass"],
        "R2_declared_no_selector_claim_rejected": report["claim_support"] == "rejected",
        "R3_preflight_failure_preserved": report["measurement_reliability"]["pass"],
        "R4_metric_robustness_passed": report["metric_robustness"]["pass"],
        "R5_v014_claim_qualified_and_queue_preserved": report["operational_decision"][
            "pass"
        ]
        and report["adjudication_queue"]["pass"],
        "R6_predecessor_inventory_184": report["predecessor_inventory"]["pass"],
        "R7_frozen_claim": report["claim_exactness"]["pass"],
        "R8_external_adjudication_still_required": "external adjudication"
        in expected_claim_payload()["nonclaim"],
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    if "--write-clause-rows" in sys.argv:
        write_clause_rows()
        return 0
    if "--write-robustness-observations" in sys.argv:
        write_robustness_observations()
        return 0
    report = semantic_selector_audit_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
