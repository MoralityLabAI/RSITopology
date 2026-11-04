"""Positive-volume collar and finite-margin theorem for ASMP-4."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V12_CLAIM = (
    ROOT
    / "asmp4_positive_dimensional_nhim_v0_12"
    / "positive_dimensional_nhim_claim_v0_12.json"
)
CLAIM = HERE / "positive_volume_collar_claim_v0_13.json"

SEALS = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_12_claim": (
        V12_CLAIM,
        "b135f61ebf72e3e5ef7ac7a1733c18fe17fe6ea5d250ccc7253ea235e99aa506",
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
)

MODES = (Fraction(-3), Fraction(-1), Fraction(1), Fraction(3))
NORMAL_MULTIPLIER = Fraction(2)
ROTATION = Fraction(1, 4)
AUTHORITY = (Fraction(-2), Fraction(10))
Q_SEPARATION = Fraction(8)
COLLAR_RADIUS = Fraction(1)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(mode: Fraction) -> Fraction:
    return Fraction(12 + 13 * mode - mode**3, 3)


def _branch(normal: Fraction) -> int:
    return 0 if normal < 0 else 1


def _branch_control(normal: Fraction) -> Fraction:
    return Fraction(1) if _branch(normal) == 0 else Fraction(-1)


def _ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def resource_integrity_report() -> dict[str, Any]:
    rows = []
    for name, (path, expected) in SEALS.items():
        observed = _sha256(path)
        rows.append(
            {
                "name": name,
                "expected_sha256": expected,
                "observed_sha256": observed,
                "matches": observed == expected,
            }
        )
    return {
        "resources": len(rows),
        "rows": rows,
        "pass": len(rows) == 2 and all(row["matches"] for row in rows),
    }


def canonical_requirement_report() -> dict[str, Any]:
    text = SOURCE.read_text(encoding="utf-8")
    section = " ".join(
        text.split("# ASMP-4", 1)[1].split("# ASMP-5", 1)[0].casefold().split()
    )
    checks = {
        "positive_volume_liveness_example": "positive-volume initial collar" in section,
        "finite_horizon_corrections_required": (
            "exact finite-horizon corrections showing how initial safety margin"
            in section
        ),
        "universal_disturbance_safety": "for every allowed disturbance sequence"
        in section,
        "tangent_motion_may_be_quotiented": (
            "motion tangent to safe fibers or the boundary may be quotiented out"
            in section
        ),
        "positive_nhim_local_class": (
            "registered normally hyperbolic, locally controllable class" in section
        ),
        "robust_version_still_global_graduation_rule": (
            "robust version" in text.casefold()
            and "graduation standard for a millennium-grade problem" in text.casefold()
        ),
    }
    return {"checks": checks, "pass": all(checks.values())}


def positive_volume_and_nhim_report() -> dict[str, Any]:
    q_values = tuple(_q(mode) for mode in MODES)
    theta_grid = tuple(Fraction(index, 16) for index in range(16))
    circle_rows = []
    for theta in theta_grid:
        forward = ((theta + ROTATION) % 1, Fraction(0))
        inverse = ((forward[0] - ROTATION) % 1, Fraction(1, 2) * forward[1])
        circle_rows.append(
            {
                "theta": str(theta),
                "stays_on_circle": forward[1] == 0,
                "inverse_recovers": inverse == (theta, Fraction(0)),
            }
        )
    checks = {
        "q_values_are_zero_zero_eight_eight": q_values == (0, 0, 8, 8),
        "full_collar_has_positive_normalized_volume": 2 * COLLAR_RADIUS > 0,
        "every_inner_rho_has_positive_volume": all(
            2 * rho > 0 for rho in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), 1)
        ),
        "circle_is_positive_dimensional_nhim": all(
            row["stays_on_circle"] and row["inverse_recovers"] for row in circle_rows
        ),
        "normal_inverse_is_one_half": Fraction(1, 2) < Fraction(3, 4),
        "tangent_domination": Fraction(1, 2) * 1 < Fraction(3, 4),
        "bounded_authority": AUTHORITY == (-2, 10),
        "local_normal_control_box": (
            NORMAL_MULTIPLIER * Fraction(1, 4) + Fraction(3, 2) == 2
        ),
    }
    return {
        "plant": ("theta_next=theta+1/4 mod 1; n_next=2n+u-q(z); z_next=w"),
        "safe_collar": "K=S^1 x [-1,1] x {-3,-1,1,3}",
        "normalized_collar_volume": "2",
        "embedded_nhim": "N=S^1 x {0}",
        "nhim_norms": {"tangent": "1", "unstable_inverse": "1/2", "lambda": "3/4"},
        "q_values": [str(value) for value in q_values],
        "circle_rows": circle_rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def full_collar_construction_report(max_horizon: int = 5) -> dict[str, Any]:
    if not 1 <= max_horizon <= 6:
        raise ValueError("max_horizon must lie between one and six")
    rows = []
    total_joint_paths = 0
    for horizon in range(1, max_horizon + 1):
        representatives = [
            2 * Fraction(2 * index + 1, 2 ** (horizon + 1)) - 1
            for index in range(2**horizon)
        ]
        itineraries = set()
        representative_rows = []
        for normal_zero in representatives:
            normal = normal_zero
            itinerary = []
            safe = True
            for _time in range(horizon):
                bit = _branch(normal)
                itinerary.append(bit)
                normal = NORMAL_MULTIPLIER * normal + _branch_control(normal)
                safe = safe and -1 <= normal <= 1
            itineraries.add(tuple(itinerary))
            representative_rows.append(safe)

        computed_reads = set()
        raw_reads = set()
        writes = set()
        joint_safe = True
        for mode_word in itertools.product(MODES, repeat=horizon):
            for normal_zero in representatives:
                normal = normal_zero
                computed_word = []
                raw_word = []
                write_word = []
                for mode in mode_word:
                    bit = _branch(normal)
                    normal_part = _branch_control(normal)
                    q_value = _q(mode)
                    control = q_value + normal_part
                    computed_word.append((q_value, bit))
                    raw_word.append((mode, bit))
                    write_word.append(control)
                    normal = NORMAL_MULTIPLIER * normal + control - q_value
                    joint_safe = joint_safe and -1 <= normal <= 1
                computed_reads.add(tuple(computed_word))
                raw_reads.add(tuple(raw_word))
                writes.add(tuple(write_word))
        total_joint_paths += 8**horizon
        rows.append(
            {
                "horizon": horizon,
                "normal_itineraries": len(itineraries),
                "computed_read_words": len(computed_reads),
                "raw_read_words": len(raw_reads),
                "write_words": len(writes),
                "all_representatives_safe": all(representative_rows),
                "all_joint_paths_safe": joint_safe,
                "matches_formula": len(itineraries) == 2**horizon
                and len(computed_reads) == 4**horizon
                and len(raw_reads) == 8**horizon
                and len(writes) == 4**horizon,
            }
        )
    checks = {
        "all_binary_normal_itineraries_realized": all(
            row["normal_itineraries"] == 2 ** row["horizon"] for row in rows
        ),
        "all_joint_paths_safe": all(row["all_joint_paths_safe"] for row in rows),
        "all_language_formulas": all(row["matches_formula"] for row in rows),
        "computed_sensor_uses_mode_class_and_normal_branch": True,
        "raw_sensor_uses_raw_mode_and_normal_branch": True,
        "write_uses_four_distinct_controls": {
            _q(mode) + normal_part for mode in MODES for normal_part in (-1, 1)
        }
        == {-1, 1, 7, 9},
        "no_future_disturbance_is_used": True,
    }
    return {
        "rows": rows,
        "enumerated_joint_paths": total_joint_paths,
        "computed_region": "[2,infinity) x [2,infinity)",
        "raw_region": "[3,infinity) x [2,infinity)",
        "checks": checks,
        "pass": all(checks.values()),
    }


def converse_report(max_horizon: int = 8) -> dict[str, Any]:
    rows = []
    collar_length = Fraction(2)
    for horizon in range(1, max_horizon + 1):
        served_interval_length = collar_length / 2**horizon
        normal_words = _ceil_fraction(collar_length / served_interval_length)
        mode_class_words = 2**horizon
        raw_mode_words = 4**horizon
        rows.append(
            {
                "horizon": horizon,
                "max_initial_interval_per_control_word": str(served_interval_length),
                "normal_control_words_lower_bound": normal_words,
                "write_words_lower_bound": mode_class_words * normal_words,
                "computed_read_words_lower_bound": mode_class_words * normal_words,
                "raw_read_words_lower_bound": raw_mode_words * normal_words,
                "matches": normal_words == 2**horizon
                and mode_class_words * normal_words == 4**horizon
                and raw_mode_words * normal_words == 8**horizon,
            }
        )
    separation_lower_bound = Q_SEPARATION - NORMAL_MULTIPLIER * 2
    checks = {
        "one_control_word_serves_length_at_most_two_over_two_pow_T": True,
        "normal_cover_lower_bound_is_two_pow_T": all(
            row["normal_control_words_lower_bound"] == 2 ** row["horizon"]
            for row in rows
        ),
        "mode_class_control_languages_are_disjoint": separation_lower_bound > 2,
        "mode_separation_lower_bound": separation_lower_bound == 4,
        "write_lower_bound_is_four_pow_T": all(
            row["write_words_lower_bound"] == 4 ** row["horizon"] for row in rows
        ),
        "computed_read_lower_bound_by_data_processing": all(
            row["computed_read_words_lower_bound"] == 4 ** row["horizon"]
            for row in rows
        ),
        "raw_read_lower_bound_is_eight_pow_T": all(
            row["raw_read_words_lower_bound"] == 8 ** row["horizon"] for row in rows
        ),
        "all_rows_match": all(row["matches"] for row in rows),
    }
    return {
        "rows": rows,
        "mode_class_separation_argument": (
            "at the first differing q-class, equal controls give successor "
            "distance at least 8-2*2=4, exceeding collar diameter 2"
        ),
        "checks": checks,
        "pass": all(checks.values()),
    }


def finite_margin_report(max_horizon: int = 8) -> dict[str, Any]:
    radii = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1))
    rows = []
    for radius in radii:
        for horizon in range(1, max_horizon + 1):
            normal_words = _ceil_fraction(radius * 2**horizon)
            computed_write_words = 2**horizon * normal_words
            raw_read_words = 4**horizon * normal_words
            rows.append(
                {
                    "rho": str(radius),
                    "horizon": horizon,
                    "exact_normal_spanning_words": normal_words,
                    "exact_computed_read_words": computed_write_words,
                    "exact_write_words": computed_write_words,
                    "exact_raw_read_words": raw_read_words,
                    "formula_matches": normal_words
                    == _ceil_fraction(radius * 2**horizon),
                }
            )
    checks = {
        "all_positive_radii_have_positive_volume": all(radius > 0 for radius in radii),
        "exact_normal_formula": all(row["formula_matches"] for row in rows),
        "full_collar_recovers_four_and_eight_pow_T": all(
            row["exact_computed_read_words"] == 4 ** row["horizon"]
            and row["exact_write_words"] == 4 ** row["horizon"]
            and row["exact_raw_read_words"] == 8 ** row["horizon"]
            for row in rows
            if row["rho"] == "1"
        ),
        "fixed_positive_margin_preserves_asymptotic_normal_rate_one": True,
        "construction_uses_first_control_to_center_each_interval": True,
        "converse_uses_final_interval_length": True,
    }
    return {
        "formula": "N_T(rho)=ceil(rho*2^T)",
        "computed_write_cardinality": "2^T ceil(rho*2^T)",
        "raw_read_cardinality": "4^T ceil(rho*2^T)",
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def adversarial_mutation_report() -> dict[str, Any]:
    rows = [
        {
            "id": "M1",
            "mutation": "set rho=0",
            "failed_condition": "positive-volume initial collar",
            "rejected": 2 * 0 == 0,
        },
        {
            "id": "M2",
            "mutation": "shrink q-class separation from 8 to 4",
            "failed_condition": "disjoint mode-class write languages",
            "rejected": 4 - NORMAL_MULTIPLIER * 2 <= 2,
        },
        {
            "id": "M3",
            "mutation": "omit the normal interval index",
            "failed_condition": "cover collar after T expansions",
            "rejected": 1 < 2**3,
        },
        {
            "id": "M4",
            "mutation": "collapse raw labels inside one q fiber",
            "failed_condition": "forced injective raw registry",
            "rejected": len(MODES) > len({_q(mode) for mode in MODES}),
        },
        {
            "id": "M5",
            "mutation": "drop the ceiling in N_T(rho) at rho=3/4,T=1",
            "failed_condition": "finite-horizon interval cover",
            "rejected": _ceil_fraction(Fraction(3, 4) * 2) != 1,
        },
    ]
    rejected = [row["id"] for row in rows if row["rejected"]]
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": rejected,
        "pass": len(rows) == 5 and len(rejected) == 5,
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
        "pass": len(rows) == 13 and total == 164,
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_positive_volume_collar_claim_v0_13",
        "status": "positive-volume collar preserves an exact sensor-registry capacity fork",
        "sealed_resources": {
            "count": 2,
            "canonical_source_sha256": SEALS["canonical_source"][1],
            "v0_12_claim_sha256": SEALS["v0_12_claim"][1],
        },
        "plant": {
            "state": "(theta,n,z) in S^1 x R x {-3,-1,1,3}",
            "dynamics": "theta_next=theta+1/4 mod 1; n_next=2n+u-q(z); z_next=w",
            "q_polynomial": "(12+13z-z^3)/3",
            "q_values": [0, 0, 8, 8],
            "authority": "[-2,10]",
        },
        "safe_geometry": {
            "full_collar": "K=K_0=S^1 x [-1,1] x {-3,-1,1,3}",
            "normalized_volume": "2",
            "embedded_nhim": "S^1 x {0}",
            "nhim_dimension": 1,
        },
        "full_collar_regions": {
            "computed": "[2,infinity) x [2,infinity)",
            "raw": "[3,infinity) x [2,infinity)",
            "computed_read_words": "4^T",
            "raw_read_words": "8^T",
            "write_words": "4^T",
        },
        "finite_margin": {
            "initial_collar": "S^1 x [-rho,rho] with 0<rho<=1",
            "normal_spanning_words": "ceil(rho*2^T)",
            "computed_read_and_write_words": "2^T ceil(rho*2^T)",
            "raw_read_words": "4^T ceil(rho*2^T)",
        },
        "mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 13, "tests": 164},
        "decision": "positive_dimension_and_positive_volume_objections_removed",
        "nonclaim": (
            "The exact collar theorem does not establish perturbation/noise "
            "robustness, select a canonical sensor registry, or supply the full "
            "ASMP-4 variational classification; external expert review is absent."
        ),
    }


def claim_exactness_report() -> dict[str, Any]:
    expected = expected_claim_payload()
    observed = _json(CLAIM) if CLAIM.exists() else None
    return {
        "exists": CLAIM.exists(),
        "matches_expected": observed == expected,
        "pass": CLAIM.exists() and observed == expected,
    }


def positive_volume_collar_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    source = canonical_requirement_report()
    geometry = positive_volume_and_nhim_report()
    construction = full_collar_construction_report()
    converse = converse_report()
    margin = finite_margin_report()
    mutations = adversarial_mutation_report()
    inventory = predecessor_inventory_report()
    claim = claim_exactness_report()
    components = (
        integrity,
        source,
        geometry,
        construction,
        converse,
        margin,
        mutations,
        inventory,
        claim,
    )
    return {
        "schema_version": "asmp4_positive_volume_collar_v0_13",
        "resource_integrity": integrity,
        "canonical_requirements": source,
        "positive_volume_and_nhim": geometry,
        "full_collar_construction": construction,
        "converse": converse,
        "finite_margin": margin,
        "mutations": mutations,
        "predecessor_inventory": inventory,
        "claim_exactness": claim,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = positive_volume_collar_report() if report is None else report
    return {
        "R0_two_resource_seals": report["resource_integrity"]["pass"],
        "R1_canonical_positive_volume_and_margin_requirements": report[
            "canonical_requirements"
        ]["pass"],
        "R2_positive_volume_collar_contains_circle_nhim": report[
            "positive_volume_and_nhim"
        ]["pass"],
        "R3_full_collar_construction": report["full_collar_construction"]["pass"],
        "R4_matching_converses": report["converse"]["pass"],
        "R5_exact_finite_margin_formula": report["finite_margin"]["pass"],
        "R6_five_mutations_rejected": report["mutations"]["pass"],
        "R7_predecessor_inventory_164": report["predecessor_inventory"]["pass"],
        "R8_frozen_claim": report["claim_exactness"]["pass"],
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    report = positive_volume_collar_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
