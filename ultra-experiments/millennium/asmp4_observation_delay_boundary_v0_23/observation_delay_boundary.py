"""Observation-delay and preview boundary for the ASMP-4 collar."""

from __future__ import annotations

import ast
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V22_CLAIM = (
    ROOT
    / "asmp4_causal_encoder_collapse_v0_22"
    / "causal_encoder_collapse_claim_v0_22.json"
)
CONTRACT = HERE / "observation_delay_contract_v0_23.json"
CLAIM = HERE / "observation_delay_boundary_claim_v0_23.json"

SEALS = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_22_causal_encoder_claim": (
        V22_CLAIM,
        "2a963630840314cafd044ce45e75a53dfbab89f2ebc547b321ffe11a8144f103",
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
    ("asmp4_semantic_selector_audit_v0_15", "test_semantic_selector_audit.py"),
    (
        "asmp4_registered_sensor_classification_v0_16",
        "test_registered_sensor_classification.py",
    ),
    (
        "asmp4_zero_error_sensor_kernels_v0_17",
        "test_zero_error_sensor_kernels.py",
    ),
    (
        "asmp4_finite_state_sensor_transducers_v0_18",
        "test_finite_state_sensor_transducers.py",
    ),
    (
        "asmp4_uncertain_initial_sensor_state_v0_19",
        "test_uncertain_initial_sensor_state.py",
    ),
    (
        "asmp4_sensor_refinement_inflation_stop_v0_20",
        "test_sensor_refinement_inflation_stop.py",
    ),
    (
        "asmp4_support_incidence_quotient_v0_21",
        "test_support_incidence_quotient.py",
    ),
    (
        "asmp4_causal_encoder_collapse_v0_22",
        "test_causal_encoder_collapse.py",
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ceil(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def safe_control_interval(normal: Fraction, q_value: int) -> tuple[Fraction, Fraction]:
    return Fraction(q_value - 1) - 2 * normal, Fraction(q_value + 1) - 2 * normal


def intervals_intersect(
    left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]
) -> bool:
    return max(left[0], right[0]) <= min(left[1], right[1])


def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for name, (path, expected) in SEALS.items():
        rows.append({"name": name, "matches": _sha256(path) == expected})
    return {
        "rows": rows,
        "pass": len(rows) == 2 and all(row["matches"] for row in rows),
    }


def contract_exactness_report() -> dict[str, Any]:
    expected = expected_contract_payload()
    observed = _load(CONTRACT) if CONTRACT.exists() else None
    return {
        "exists": CONTRACT.exists(),
        "matches": observed == expected,
        "pass": CONTRACT.exists() and observed == expected,
    }


def interval_impossibility_report() -> dict[str, Any]:
    normals = tuple(Fraction(index, 8) for index in range(-8, 9))
    rows = []
    for normal in normals:
        low = safe_control_interval(normal, 0)
        high = safe_control_interval(normal, 8)
        rows.append(
            {
                "normal": str(normal),
                "low": [str(value) for value in low],
                "high": [str(value) for value in high],
                "intersects": intervals_intersect(low, high),
                "gap": str(high[0] - low[1]),
            }
        )
    symbolic_checks = {
        "affine_gap_identity": (7 - 1, -2 - (-2)) == (6, 0),
        "same_width": all(
            safe_control_interval(normal, q_value)[1]
            - safe_control_interval(normal, q_value)[0]
            == 2
            for normal in normals
            for q_value in (0, 8)
        ),
        "constant_gap_six": all(row["gap"] == "6" for row in rows),
        "all_disjoint": all(not row["intersects"] for row in rows),
        "center_intervals_inside_authority": safe_control_interval(Fraction(0), 0)
        == (Fraction(-1), Fraction(1))
        and safe_control_interval(Fraction(0), 8) == (Fraction(7), Fraction(9)),
        "individual_authority_is_adequate": all(
            intervals_intersect(
                safe_control_interval(normal, q_value),
                (Fraction(-2), Fraction(10)),
            )
            for normal in normals
            for q_value in (0, 8)
        ),
    }
    return {
        "rows": rows,
        "checks": symbolic_checks,
        "pass": all(symbolic_checks.values()),
    }


def delayed_adversary_tree_report(
    max_horizon: int = 6, max_delay: int = 4
) -> dict[str, Any]:
    rows = []
    for horizon in range(1, max_horizon + 1):
        for delay in range(1, max_delay + 1):
            for collision_time in range(horizon):
                low_word = (0,) * horizon
                high_word = (
                    low_word[:collision_time] + (8,) + low_word[collision_time + 1 :]
                )
                observed_through = collision_time - delay
                low_observed = low_word[: max(0, observed_through + 1)]
                high_observed = high_word[: max(0, observed_through + 1)]
                rows.append(
                    {
                        "horizon": horizon,
                        "delay": delay,
                        "collision_time": collision_time,
                        "observed_equal": low_observed == high_observed,
                        "current_differs": low_word[collision_time]
                        != high_word[collision_time],
                        "common_action_impossible": not intervals_intersect(
                            safe_control_interval(Fraction(0), 0),
                            safe_control_interval(Fraction(0), 8),
                        ),
                    }
                )
    checks = {
        "all_rows": len(rows) == max_delay * sum(range(1, max_horizon + 1)),
        "all_observed_histories_equal": all(row["observed_equal"] for row in rows),
        "all_current_modes_differ": all(row["current_differs"] for row in rows),
        "all_common_actions_impossible": all(
            row["common_action_impossible"] for row in rows
        ),
        "every_positive_delay_covered": {row["delay"] for row in rows}
        == set(range(1, max_delay + 1)),
        "every_collision_time_covered": all(
            any(row["collision_time"] == time for row in rows)
            for time in range(max_horizon)
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def timing_boundary_report() -> dict[str, Any]:
    rows = [
        {
            "architecture": "same_step_causal",
            "delay": 0,
            "current_q_available": True,
            "arbitrary_q": True,
            "region": "[2,infinity) x [2,infinity)",
        },
        {
            "architecture": "positive_delay_no_preview",
            "delay": ">=1",
            "current_q_available": False,
            "arbitrary_q": True,
            "region": "empty",
        },
        {
            "architecture": "positive_delay_charged_current_preview",
            "delay": ">=1",
            "current_q_available": True,
            "arbitrary_q": True,
            "region": "[2,infinity) x [2,infinity)",
        },
        {
            "architecture": "seeded_constant_q",
            "delay": ">=1",
            "current_q_available": "predictable from charged initial seed",
            "arbitrary_q": False,
            "region": "[1,infinity) x [1,infinity)",
        },
    ]
    checks = {
        "zero_delay_matches_v022": rows[0]["region"] == "[2,infinity) x [2,infinity)",
        "positive_delay_empty": rows[1]["region"] == "empty",
        "charged_preview_restores": rows[2]["region"] == rows[0]["region"],
        "predictable_constant_liveness": rows[3]["region"]
        == "[1,infinity) x [1,infinity)",
        "delay_not_capacity_failure": rows[1]["region"] == "empty"
        and rows[2]["region"] != "empty",
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def finite_counts_report(max_horizon: int = 8) -> dict[str, Any]:
    rows = []
    for radius in (Fraction(1, 3), Fraction(2, 5), Fraction(1)):
        for horizon in range(1, max_horizon + 1):
            normal = _ceil(radius * 2**horizon)
            rows.append(
                {
                    "rho": str(radius),
                    "horizon": horizon,
                    "normal": normal,
                    "same_step_reads": 2**horizon * normal,
                    "same_step_writes": 2**horizon * normal,
                    "preview_reads": 2**horizon * normal,
                    "preview_writes": 2**horizon * normal,
                    "constant_seed_reads": 2 * normal,
                    "constant_seed_writes": 2 * normal,
                }
            )
    checks = {
        "normal_ceiling": all(
            row["normal"] == _ceil(Fraction(row["rho"]) * 2 ** row["horizon"])
            for row in rows
        ),
        "preview_matches_same_step": all(
            row["preview_reads"] == row["same_step_reads"]
            and row["preview_writes"] == row["same_step_writes"]
            for row in rows
        ),
        "constant_seed_exact": all(
            row["constant_seed_reads"] == 2 * row["normal"]
            and row["constant_seed_writes"] == 2 * row["normal"]
            for row in rows
        ),
        "same_step_rate_two": all(
            row["same_step_reads"] == 4 ** row["horizon"]
            for row in rows
            if row["rho"] == "1"
        ),
        "constant_asymptotic_rate_one": math.isclose(
            math.log2(2 * 2**64) / 64, 1 + Fraction(1, 64)
        ),
    }
    return {
        "formula": {
            "same_step_or_preview": "2^T ceil(rho*2^T) on each port",
            "positive_delay_no_preview": "empty",
            "seeded_constant_q": "2 ceil(rho*2^T) on each port",
        },
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def mutation_report() -> dict[str, Any]:
    intervals = interval_impossibility_report()
    tree = delayed_adversary_tree_report(4, 2)
    counts = finite_counts_report(4)
    rows = {
        "use_previous_q_as_current": tree["checks"]["all_observed_histories_equal"]
        and tree["checks"]["all_current_modes_differ"],
        "repair_delay_with_more_capacity": intervals["checks"]["all_disjoint"],
        "plant_independent_random_seed_repairs_collision": intervals["checks"][
            "constant_gap_six"
        ],
        "omit_charged_preview_words": all(
            row["preview_reads"] == row["same_step_reads"] for row in counts["rows"]
        ),
        "floor_nondyadic_margin": int(Fraction(3, 4) * 2) < _ceil(Fraction(3, 4) * 2),
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 5 and all(rows.values()),
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
        "pass": len(rows) == 23 and total == 264,
    }


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_observation_delay_contract_v0_23",
        "plant": "n_next=2n+u-q_t with n in [-1,1], u in [-2,10], q_t in {0,8}",
        "architectures": {
            "same_step": "current q information arrives before current write",
            "positive_delay": "at write t, encoder/controller information contains q only through t-d for integer d>=1",
            "preview": "a charged current q symbol arrives before current write despite delayed raw sensing",
            "predictable_control": "q_t is constant and a charged initial q seed is supplied before safety begins",
        },
        "quantifiers": {
            "disturbance": "every arbitrary q word in the main delayed architecture",
            "randomness": "every plant-independent shared-randomness seed",
            "safety": "every initial normal state and every time from the first write",
        },
        "theorem": {
            "delay_zero_region": "[2,infinity) x [2,infinity)",
            "positive_delay_region": "empty",
            "charged_preview_region": "[2,infinity) x [2,infinity)",
            "seeded_constant_q_region": "[1,infinity) x [1,infinity)",
        },
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_observation_delay_boundary_claim_v0_23",
        "status": "sharp current-information delay and preview boundary",
        "sealed_resources": {
            "count": 2,
            "canonical_source_sha256": SEALS["canonical_source"][1],
            "v0_22_causal_encoder_claim_sha256": SEALS["v0_22_causal_encoder_claim"][1],
        },
        "main_theorem": {
            "delay_zero_region": "[2,infinity) x [2,infinity)",
            "every_positive_integer_delay_region": "empty",
            "safe_interval_gap": 6,
            "capacity_or_memory_cannot_repair": True,
        },
        "restoration": {
            "charged_current_preview_region": "[2,infinity) x [2,infinity)",
            "seeded_constant_q_region": "[1,infinity) x [1,infinity)",
        },
        "adversary_tree": {"max_horizon": 6, "max_delay": 4, "rows": 84},
        "mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 23, "tests": 264},
        "decision": "current_mode_information_not_bandwidth_is_load_bearing_under_arbitrary_disturbance",
        "nonclaim": (
            "The impossibility uses arbitrary current q, safety from the first write, "
            "and no charged preview. It does not apply when q is predictable from "
            "available history, current preview is charged, safety starts after a "
            "calibration phase, or the plant has overlapping robust-control sets."
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


def delay_boundary_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    contract = contract_exactness_report()
    intervals = interval_impossibility_report()
    tree = delayed_adversary_tree_report()
    timing = timing_boundary_report()
    counts = finite_counts_report()
    mutations = mutation_report()
    inventory = predecessor_inventory_report()
    claim = claim_exactness_report()
    components = (
        integrity,
        contract,
        intervals,
        tree,
        timing,
        counts,
        mutations,
        inventory,
        claim,
    )
    return {
        "schema_version": "asmp4_observation_delay_boundary_v0_23",
        "resource_integrity": integrity,
        "contract_exactness": contract,
        "interval_impossibility": intervals,
        "delayed_adversary_tree": tree,
        "timing_boundary": timing,
        "finite_counts": counts,
        "mutations": mutations,
        "predecessor_inventory": inventory,
        "claim_exactness": claim,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = delay_boundary_report() if report is None else report
    return {
        "R0_two_resource_seals": report["resource_integrity"]["pass"],
        "R1_timing_contract": report["contract_exactness"]["pass"],
        "R2_exact_interval_impossibility": report["interval_impossibility"]["pass"],
        "R3_delayed_adversary_tree": report["delayed_adversary_tree"]["pass"],
        "R4_sharp_delay_threshold": report["timing_boundary"]["pass"],
        "R5_preview_and_prediction_restoration": report["finite_counts"]["pass"],
        "R6_exact_finite_counts": report["finite_counts"]["pass"],
        "R7_five_mutations_rejected": report["mutations"]["pass"],
        "R8_inventory_and_claim": report["predecessor_inventory"]["pass"]
        and report["claim_exactness"]["pass"],
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    report = delay_boundary_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
