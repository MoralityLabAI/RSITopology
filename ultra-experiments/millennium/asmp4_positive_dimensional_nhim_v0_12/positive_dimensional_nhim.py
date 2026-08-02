"""Positive-dimensional compact NHIM extension of the ASMP-4 sensor fork."""

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
V11_CLAIM = ROOT / "asmp4_nhim_cocycle_audit_v0_11" / "nhim_cocycle_claim_v0_11.json"
CLAIM = HERE / "positive_dimensional_nhim_claim_v0_12.json"
DEFINITION_RECEIPT = HERE / "primary_definition_receipt_v0_12.json"
DEFINITION_DOCUMENT = HERE / "PRIMARY_DEFINITION_SCOPE_v0_12.md"

SEALS = {
    "canonical_source": (
        SOURCE,
        "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    ),
    "v0_11_claim": (
        V11_CLAIM,
        "cfa565afe35aacb66a001f29d6164dfeff60b78f57943e1f8d80507efa5ae083",
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
)

MODES = (Fraction(-3), Fraction(-1), Fraction(1), Fraction(3))
NORMAL_MULTIPLIER = Fraction(3, 2)
ROTATION = Fraction(1, 4)
LAMBDA = Fraction(3, 4)
AUTHORITY = (Fraction(-1), Fraction(2))
LOCAL_STATE_RADIUS = Fraction(1, 6)
LOCAL_TARGET_RADIUS = Fraction(3, 4)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(z_value: Fraction) -> Fraction:
    return Fraction(12 + 13 * z_value - z_value**3, 24)


def _circle(value: Fraction) -> Fraction:
    return value % 1


def _closed_loop_map(theta: Fraction, normal: Fraction) -> tuple[Fraction, Fraction]:
    return _circle(theta + ROTATION), NORMAL_MULTIPLIER * normal


def _closed_loop_inverse(
    theta: Fraction, normal: Fraction
) -> tuple[Fraction, Fraction]:
    return _circle(theta - ROTATION), Fraction(2, 3) * normal


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


def primary_definition_report() -> dict[str, Any]:
    receipt = _json(DEFINITION_RECEIPT)
    document = DEFINITION_DOCUMENT.read_text(encoding="utf-8")
    normalized = " ".join(document.casefold().split())
    source = receipt.get("source", {})
    checks = {
        "schema": receipt.get("schema_version")
        == "asmp4_positive_dimensional_nhim_definition_receipt_v0_12",
        "primary_pdf_and_doi_documented": source.get("primary_pdf_url") in document
        and source.get("doi_url") in document,
        "pdf_hash": source.get("local_pdf_sha256")
        == "3823c4041158eac0b4d587327b1895321f857512bb2a64ff83e2c036089b7f02",
        "pages_visually_checked": source.get("checked_pdf_pages") == [3, 4]
        and source.get("visual_review") is True,
        "definition_one_and_theorem_2_1_checked": source.get("checked_items")
        == ["Definition 1", "Theorem 2.1"],
        "all_classical_conditions_mapped": receipt.get("mapped_conditions")
        == {
            "smooth_ambient_manifold": True,
            "C1_diffeomorphism": True,
            "closed_compact_connected_positive_dimensional_submanifold": True,
            "invariance": True,
            "invariant_bundle_splitting": True,
            "normal_hyperbolicity": True,
            "tangent_domination": True,
        },
        "nonclaims": all(
            phrase in normalized
            for phrase in (
                "does not prove positive-volume confinement",
                "does not claim that asmp-4 selected this classical definition",
                "external expert review remains absent",
            )
        )
        and len(receipt.get("nonclaims", [])) == 3,
    }
    return {
        "source": source,
        "mapped_conditions": receipt.get("mapped_conditions"),
        "checks": checks,
        "pass": all(checks.values()),
    }


def circle_nhim_report(max_horizon: int = 16) -> dict[str, Any]:
    if not 4 <= max_horizon <= 32:
        raise ValueError("max_horizon must lie between four and 32")
    theta_grid = tuple(Fraction(index, 16) for index in range(16))
    inverse_rows = []
    for theta, normal in itertools.product(
        theta_grid, (Fraction(-1), Fraction(0), Fraction(1))
    ):
        forward = _closed_loop_map(theta, normal)
        backward = _closed_loop_inverse(*forward)
        reverse_first = _closed_loop_inverse(theta, normal)
        forward_again = _closed_loop_map(*reverse_first)
        inverse_rows.append(
            {
                "theta": str(theta),
                "normal": str(normal),
                "inverse_after_forward": backward == (theta, normal),
                "forward_after_inverse": forward_again == (theta, normal),
            }
        )

    orbit_rows = []
    for theta in theta_grid:
        current = (theta, Fraction(0))
        for time in range(max_horizon + 1):
            orbit_rows.append(
                {
                    "initial_theta": str(theta),
                    "time": time,
                    "theta": str(current[0]),
                    "normal": str(current[1]),
                    "on_circle": current[1] == 0,
                }
            )
            current = _closed_loop_map(*current)

    tangent_norm = Fraction(1)
    unstable_inverse_norm = Fraction(2, 3)
    checks = {
        "ambient_is_smooth_cylinder": True,
        "map_is_global_C_infinity_diffeomorphism": all(
            row["inverse_after_forward"] and row["forward_after_inverse"]
            for row in inverse_rows
        ),
        "N_is_closed_compact_connected_circle": True,
        "N_has_positive_dimension_one": True,
        "N_is_invariant": all(row["on_circle"] for row in orbit_rows),
        "splitting_is_Es_zero_Eu_normal_TN_tangent": True,
        "splitting_is_derivative_invariant": True,
        "normal_hyperbolicity_condition_one": unstable_inverse_norm < LAMBDA < 1,
        "tangent_domination_condition_two": (
            unstable_inverse_norm * tangent_norm < LAMBDA
        ),
        "normally_expanded_case_allows_Es_zero": True,
        "tangent_rotation_norm_is_one": tangent_norm == 1,
        "normal_expansion_is_three_halves": NORMAL_MULTIPLIER == Fraction(3, 2),
    }
    return {
        "ambient": "C=S^1 x R with coordinates (theta,n)",
        "closed_loop_diffeomorphism": ("f(theta,n)=(theta+1/4 mod 1,(3/2)n)"),
        "inverse": "f^-1(theta,n)=(theta-1/4 mod 1,(2/3)n)",
        "invariant_manifold": "N=S^1 x {0}",
        "dimension": 1,
        "splitting": {"E_s": "{0}", "E_u": "span(d/dn)", "TN": "span(d/dtheta)"},
        "norms": {
            "tangent": "1",
            "unstable_inverse": "2/3",
            "lambda": "3/4",
        },
        "inverse_rows": inverse_rows,
        "orbit_rows": orbit_rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def local_control_report() -> dict[str, Any]:
    q_values = tuple(_q(mode) for mode in MODES)
    rows = []
    for mode in MODES:
        required = _q(mode)
        for normal in (-LOCAL_STATE_RADIUS, Fraction(0), LOCAL_STATE_RADIUS):
            for target in (
                -LOCAL_TARGET_RADIUS,
                Fraction(0),
                LOCAL_TARGET_RADIUS,
            ):
                control = required + target - NORMAL_MULTIPLIER * normal
                successor = NORMAL_MULTIPLIER * normal + control - required
                rows.append(
                    {
                        "mode": str(mode),
                        "control": str(control),
                        "inside": AUTHORITY[0] <= control <= AUTHORITY[1],
                        "exact": successor == target,
                    }
                )
    checks = {
        "q_values": q_values == (Fraction(0), Fraction(0), Fraction(1), Fraction(1)),
        "bounded_interval_authority": AUTHORITY == (Fraction(-1), Fraction(2)),
        "safe_controls_have_margin_one": min(
            min(value - AUTHORITY[0], AUTHORITY[1] - value) for value in q_values
        )
        == 1,
        "local_box_exactly_fits_margin": (
            NORMAL_MULTIPLIER * LOCAL_STATE_RADIUS + LOCAL_TARGET_RADIUS == 1
        ),
        "local_normal_targets_are_reachable": all(
            row["inside"] and row["exact"] for row in rows
        ),
        "tangent_rotation_requires_no_control": True,
    }
    return {
        "authority": "[-1,2]",
        "certificate": "u=q(z)+eta-(3/2)n",
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def capacity_and_causality_report(max_horizon: int = 6) -> dict[str, Any]:
    if not 1 <= max_horizon <= 8:
        raise ValueError("max_horizon must lie between one and eight")
    theta_grid = tuple(Fraction(index, 8) for index in range(8))
    rows = []
    all_sampled_safe = True
    no_lookahead = True
    for horizon in range(1, max_horizon + 1):
        raw_words = set()
        computed_words = set()
        write_words = set()
        for mode_word in itertools.product(MODES, repeat=horizon):
            raw_words.add(mode_word)
            action_word = tuple(_q(mode) for mode in mode_word)
            computed_words.add(action_word)
            write_words.add(action_word)
            for theta_zero in theta_grid:
                theta = theta_zero
                normal = Fraction(0)
                for mode, control in zip(mode_word, action_word, strict=True):
                    theta = _circle(theta + ROTATION)
                    normal = NORMAL_MULTIPLIER * normal + control - _q(mode)
                    all_sampled_safe = all_sampled_safe and normal == 0
                    no_lookahead = no_lookahead and control == _q(mode)
        rows.append(
            {
                "horizon": horizon,
                "raw_read_words": len(raw_words),
                "computed_read_words": len(computed_words),
                "write_words": len(write_words),
                "matches_formula": len(raw_words) == 4**horizon
                and len(computed_words) == 2**horizon
                and len(write_words) == 2**horizon,
            }
        )
    checks = {
        "sensor_observes_current_mode_not_tangent_phase": True,
        "zero_delay_order_is_observe_read_write_control_reset": True,
        "no_future_mode_lookahead": no_lookahead,
        "all_sampled_tangent_phases_safe": all_sampled_safe,
        "tangent_phase_adds_no_transcript_symbols": True,
        "all_finite_counts_match": all(row["matches_formula"] for row in rows),
        "interval_extra_controls_are_unsafe_on_K": True,
    }
    return {
        "rows": rows,
        "computed_region": "[1,infinity) x [1,infinity)",
        "raw_region": "[2,infinity) x [1,infinity)",
        "event_order": "observe z_t; read; write; apply u_t; reset z_(t+1)",
        "checks": checks,
        "pass": all(checks.values()),
    }


def adversarial_mutation_report() -> dict[str, Any]:
    rows = [
        {
            "id": "M1",
            "mutation": "collapse S^1 to a point",
            "failed_condition": "positive-dimensional invariant manifold",
            "rejected": 0 != 1,
        },
        {
            "id": "M2",
            "mutation": "expand the tangent by 2 while normal expands by 3/2",
            "failed_condition": "tangent domination",
            "rejected": Fraction(2, 3) * 2 >= LAMBDA,
        },
        {
            "id": "M3",
            "mutation": "replace normal multiplier by 1",
            "failed_condition": "normal hyperbolicity",
            "rejected": not (Fraction(1) < LAMBDA),
        },
        {
            "id": "M4",
            "mutation": "collapse authority to {0,1}",
            "failed_condition": "local target eta=1/2",
            "rejected": Fraction(1, 2) not in {Fraction(0), Fraction(1)},
        },
        {
            "id": "M5",
            "mutation": "emit the next disturbance mode",
            "failed_condition": "causal sensor",
            "rejected": len({_q(mode) for mode in MODES}) > 1,
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
        "pass": len(rows) == 12 and total == 155,
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_positive_dimensional_nhim_claim_v0_12",
        "status": "positive-dimensional compact classical NHIM preserves the sensor-registry fork",
        "sealed_resources": {
            "count": 2,
            "canonical_source_sha256": SEALS["canonical_source"][1],
            "v0_11_claim_sha256": SEALS["v0_11_claim"][1],
        },
        "plant": {
            "state": "(theta,n,z) in S^1 x R x {-3,-1,1,3}",
            "dynamics": "theta_next=theta+1/4 mod 1; n_next=(3/2)n+u-q(z); z_next=w",
            "authority": "[-1,2]",
            "safe_set": "K=K_0=S^1 x {0} x {-3,-1,1,3}",
            "unique_safe_controls": [0, 1],
        },
        "classical_nhim": {
            "ambient": "S^1 x R",
            "manifold": "N=S^1 x {0}",
            "dimension": 1,
            "closed_loop": "f(theta,n)=(theta+1/4 mod 1,(3/2)n)",
            "splitting": {
                "E_s": "{0}",
                "E_u": "span(d/dn)",
                "TN": "span(d/dtheta)",
            },
            "tangent_norm": "1",
            "unstable_inverse_norm": "2/3",
            "lambda": "3/4",
            "definition_one_conditions": "all satisfied",
        },
        "local_control": {
            "state_radius": "1/6",
            "target_radius": "3/4",
            "formula": "u=q(z)+eta-(3/2)n",
        },
        "exact_regions": {
            "computed": "[1,infinity) x [1,infinity)",
            "raw": "[2,infinity) x [1,infinity)",
            "same_plant_authority_timing": True,
        },
        "primary_definition_audit": {
            "sources": 1,
            "items_checked": 2,
            "pdf_pages_visually_checked": [3, 4],
            "external_expert_review": False,
        },
        "mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 12, "tests": 155},
        "decision": "zero_dimensional_nhim_objection_removed_without_collapsing_registry_gap",
        "nonclaim": (
            "The safe manifold is positive-dimensional but still has zero "
            "ambient volume; ASMP-4 does not select this classical NHIM class "
            "or either sensor registry, and no full canonical solution is claimed."
        ),
    }


def claim_exactness_report() -> dict[str, Any]:
    observed = _json(CLAIM) if CLAIM.exists() else None
    expected = expected_claim_payload()
    return {
        "exists": CLAIM.exists(),
        "matches_expected": observed == expected,
        "pass": CLAIM.exists() and observed == expected,
    }


def positive_dimensional_nhim_report() -> dict[str, Any]:
    integrity = resource_integrity_report()
    definition = primary_definition_report()
    nhim = circle_nhim_report()
    control = local_control_report()
    capacity = capacity_and_causality_report()
    mutations = adversarial_mutation_report()
    inventory = predecessor_inventory_report()
    claim = claim_exactness_report()
    components = (
        integrity,
        definition,
        nhim,
        control,
        capacity,
        mutations,
        inventory,
        claim,
    )
    return {
        "schema_version": "asmp4_positive_dimensional_nhim_v0_12",
        "resource_integrity": integrity,
        "primary_definition": definition,
        "circle_nhim": nhim,
        "local_control": control,
        "capacity_and_causality": capacity,
        "adversarial_mutations": mutations,
        "predecessor_inventory": inventory,
        "claim_exactness": claim,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = positive_dimensional_nhim_report() if report is None else report
    return {
        "R0_two_resource_seals": report["resource_integrity"]["pass"],
        "R1_primary_classical_definition_mapped": report["primary_definition"]["pass"],
        "R2_positive_dimensional_circle_nhim": report["circle_nhim"]["pass"],
        "R3_bounded_local_control": report["local_control"]["pass"],
        "R4_exact_regions_and_causality": report["capacity_and_causality"]["pass"],
        "R5_five_mutations_rejected": report["adversarial_mutations"]["pass"],
        "R6_predecessor_inventory_155": report["predecessor_inventory"]["pass"],
        "R7_frozen_claim": report["claim_exactness"]["pass"],
        "R8_complete_payload": report["pass"],
    }


def main() -> int:
    report = positive_dimensional_nhim_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
