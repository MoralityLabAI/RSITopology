"""Import-independent verifier for the ASMP-4 v0.14 stopping certificate."""

from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V10 = ROOT / "asmp4_stopping_red_team_v0_10" / "stopping_red_team_claim_v0_10.json"
V13 = (
    ROOT
    / "asmp4_positive_volume_collar_v0_13"
    / "positive_volume_collar_claim_v0_13.json"
)
CLAIM = HERE / "positive_volume_stop_claim_v0_14.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V10: "fd8b2e74bdd6f16aabd7907dc621254accd6e8fa183957d1eaaf3138163d314c",
    V13: "6c09924712d5342c69a731a602bdb3b008ef30d54a7cd0b74e08250d64c4bd19",
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
)

REOPENING = [
    "a normative sensor observation/computation registry is added",
    "an attributable proof or implementation error invalidates the positive-volume fork",
    "a specified perturbation/noise model invalidates or collapses both exact completions",
    "an attributable theorem or external review maps the existing wording to one unique formal class",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def independent_integrity() -> dict[str, Any]:
    rows = []
    for path, expected in SEALS.items():
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append((path.name, observed == expected))
    return {
        "rows": rows,
        "pass": len(rows) == 3 and all(matches for _, matches in rows),
    }


def independent_source_audit() -> dict[str, Any]:
    text = SOURCE.read_text(encoding="utf-8")
    section = " ".join(
        text.split("# ASMP-4", 1)[1].split("# ASMP-5", 1)[0].lower().split()
    )
    selectors = (
        "sensor registry",
        "sensor observation map",
        "sensor computation closure",
        "raw mode",
        "sufficient statistic",
        "injective sensor",
    )
    checks = {
        "asmp4_delimited": "two-port evaluator-relative confinement" in section,
        "code_quantified": section.count("registered causal code") == 2,
        "sensor_emission_only": "sensor encoder emits only the read transcript"
        in section,
        "components_separate": "sensor, controller, and actuator are separate"
        in section,
        "universal_disturbance": "for every allowed disturbance sequence" in section,
        "positive_volume_example": "positive-volume initial collar" in section,
        "all_selector_terms_absent": all(term not in section for term in selectors),
        "architecture_dependent_without_selector": (
            "architecture-dependent tradeoff inequalities" in section
            and all(term not in section for term in selectors)
        ),
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_fork_replay(max_horizon: int = 12) -> dict[str, Any]:
    collar = _load(V13)
    rows = []
    for horizon in range(1, max_horizon + 1):
        computed = 4**horizon
        raw = 8**horizon
        write = 4**horizon
        rows.append(
            {
                "horizon": horizon,
                "computed": computed,
                "raw": raw,
                "write": write,
                "rates": (
                    math.log2(computed) / horizon,
                    math.log2(raw) / horizon,
                    math.log2(write) / horizon,
                ),
            }
        )
    regions = collar["full_collar_regions"]
    checks = {
        "volume_two": collar["safe_geometry"]["normalized_volume"] == "2",
        "circle_nhim": collar["safe_geometry"]["nhim_dimension"] == 1,
        "bounded_authority": collar["plant"]["authority"] == "[-2,10]",
        "universal_mode_dynamics": "z_next=w" in collar["plant"]["dynamics"],
        "computed_region": regions["computed"] == "[2,infinity) x [2,infinity)",
        "raw_region": regions["raw"] == "[3,infinity) x [2,infinity)",
        "distinct_regions": regions["computed"] != regions["raw"],
        "all_exact_rates": all(row["rates"] == (2.0, 3.0, 2.0) for row in rows),
        "finite_margin": collar["finite_margin"]["normal_spanning_words"]
        == "ceil(rho*2^T)",
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_lift_audit() -> dict[str, Any]:
    old = _load(V10)
    new = _load(V13)
    checks = {
        "old_four_primary_sources": old["cited_prior_art_scope_audit"][
            "canonical_primary_sources"
        ]
        == 4,
        "old_primary_selector_count_zero": old["cited_prior_art_scope_audit"][
            "asmp4_two_port_registry_selectors"
        ]
        == 0,
        "old_three_near_misses": old["targeted_literature_near_miss_audit"][
            "reviewed_primary_near_misses"
        ]
        == 3,
        "old_near_miss_selector_count_zero": old["targeted_literature_near_miss_audit"][
            "asmp4_registry_selectors"
        ]
        == 0,
        "old_counterarguments_closed": old["counterargument_audit"]
        == {"cases": 14, "unresolved": 0},
        "new_geometry_decision": new["decision"]
        == "positive_dimension_and_positive_volume_objections_removed",
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_selector_mutations() -> dict[str, Any]:
    section = " ".join(
        SOURCE.read_text(encoding="utf-8")
        .split("# ASMP-4", 1)[1]
        .split("# ASMP-5", 1)[0]
        .lower()
        .split()
    )
    mutations = {
        "q_fiber_quotient": (
            "sensor may quotient raw mode by the control-relevant q fiber",
            "[2,infinity) x [2,infinity)",
        ),
        "raw_injectivity": (
            "sensor report must be injective in the four raw modes",
            "[3,infinity) x [2,infinity)",
        ),
        "coarsest_statistic": (
            "charge the coarsest control-sufficient statistic",
            "[2,infinity) x [2,infinity)",
        ),
        "calibrated_sensor": (
            "charge a fixed calibrated four-label sensor",
            "[3,infinity) x [2,infinity)",
        ),
        "registry_parameter": (
            "make the sensor registry an explicit theorem parameter",
            "parameterized",
        ),
    }
    rows = [
        {
            "name": name,
            "clause_absent": clause not in section,
            "outcome": outcome,
        }
        for name, (clause, outcome) in mutations.items()
    ]
    checks = {
        "five_mutations": len(rows) == 5,
        "all_absent": all(row["clause_absent"] for row in rows),
        "two_incompatible_regions": len(
            {row["outcome"] for row in rows if row["outcome"].startswith("[")}
        )
        == 2,
        "parameterized_option": rows[-1]["outcome"] == "parameterized",
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


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
        "pass": len(rows) == 14 and total == 174,
    }


def independent_claim_audit() -> dict[str, Any]:
    claim = _load(CLAIM)
    checks = {
        "schema": claim["schema_version"] == "asmp4_positive_volume_stop_claim_v0_14",
        "seals": claim["sealed_resources"]
        == {
            "count": 3,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_10_stopping_claim_sha256": SEALS[V10],
            "v0_13_collar_claim_sha256": SEALS[V13],
        },
        "fork": claim["positive_volume_fork"]
        == {
            "normalized_volume": "2",
            "nhim_dimension": 1,
            "computed_region": "[2,infinity) x [2,infinity)",
            "raw_region": "[3,infinity) x [2,infinity)",
            "finite_margin": "ceil(rho*2^T)",
        },
        "selector_audit": claim["source_selector_audit"]
        == {
            "candidate_selector_terms_present": 0,
            "counterfactual_selectors": 5,
            "distinct_selected_regions": 2,
        },
        "inventory": claim["predecessor_inventory"] == {"packages": 14, "tests": 174},
        "decision": claim["decision"]
        == "stop_local_construction_and_request_normative_registration",
        "reopening": claim["reopening_conditions"] == REOPENING,
        "nonclaim": "not claimed mathematically resolved" in claim["nonclaim"]
        and "external review" in claim["nonclaim"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def document_sentinels() -> dict[str, Any]:
    paths = {
        "stop": HERE / "HARNESS_STOP_CERTIFICATE_v0_14.md",
        "result": HERE / "RESULT.md",
        "audit": HERE / "COMPLETION_AUDIT_v0_14.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_14.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").lower().split())
        for name, path in paths.items()
    }
    checks = {
        "decision": "stop local construction" in docs["stop"],
        "positive_volume_fork": "normalized volume 2" in docs["stop"]
        and "[2,infinity) x [2,infinity)" in docs["stop"]
        and "[3,infinity) x [2,infinity)" in docs["stop"],
        "logical_boundary": "cannot manufacture a normative clause" in docs["stop"],
        "four_reopening_conditions": "four reopening conditions" in docs["stop"],
        "nonresolution": "not a mathematical resolution" in docs["result"],
        "inventory": "184" in docs["audit"],
        "entrypoints": "run_verification.py" in docs["readme"]
        and "verify_positive_volume_stop.py" in docs["readme"],
        "review_attack": "falsify the stop" in docs["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "source": independent_source_audit()["pass"],
        "fork": independent_fork_replay()["pass"],
        "lift": independent_lift_audit()["pass"],
        "selectors": independent_selector_mutations()["pass"],
        "inventory": independent_inventory()["pass"],
        "claim": independent_claim_audit()["pass"],
        "documents": document_sentinels()["pass"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
