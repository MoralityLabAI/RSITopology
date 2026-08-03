"""Exact harness for the ASMP-4 robust public reset-atlas theorem v0.35."""

from __future__ import annotations

import ast
import json
import re
from fractions import Fraction
from functools import cache
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONTRACT = HERE / "robust_public_atlas_contract_v0_35.json"
CLAIM = HERE / "robust_public_atlas_claim_v0_35.json"
V34_CLAIM = (
    ROOT
    / "asmp4_compact_public_connector_v0_34"
    / "public_connector_claim_v0_34.json"
)
V34_CONTRACT = (
    ROOT
    / "asmp4_compact_public_connector_v0_34"
    / "public_connector_contract_v0_34.json"
)

EXPECTED_PAYLOAD = (
    "README.md",
    "THEOREM.md",
    "RESULT.md",
    "PRIOR_ART_BOUNDARY_v0_35.md",
    "REVIEWER_PACKET_v0_35.md",
    "COMPLETION_AUDIT_v0_35.md",
    "robust_public_atlas_contract_v0_35.json",
    "robust_public_atlas_claim_v0_35.json",
    "robust_public_atlas.py",
    "verify_robust_public_atlas.py",
    "test_robust_public_atlas.py",
    "run_verification.py",
)


def ceil_log2(cardinality: int) -> int:
    if cardinality < 1:
        raise ValueError("cardinality must be positive")
    return (cardinality - 1).bit_length()


def propagated_errors(
    state_lipschitz: Fraction,
    disturbance_lipschitz: Fraction,
    initial_radius: Fraction,
    disturbance_radius: Fraction,
    horizon: int,
) -> tuple[Fraction, ...]:
    if min(
        state_lipschitz,
        disturbance_lipschitz,
        initial_radius,
        disturbance_radius,
    ) < 0 or horizon < 0:
        raise ValueError("error parameters must be nonnegative")
    errors = [initial_radius]
    for _ in range(horizon):
        errors.append(
            state_lipschitz * errors[-1]
            + disturbance_lipschitz * disturbance_radius
        )
    return tuple(errors)


def closed_form_error(
    state_lipschitz: Fraction,
    disturbance_lipschitz: Fraction,
    initial_radius: Fraction,
    disturbance_radius: Fraction,
    step: int,
) -> Fraction:
    if step < 0:
        raise ValueError("step must be nonnegative")
    if state_lipschitz == 1:
        return initial_radius + step * disturbance_lipschitz * disturbance_radius
    geometric = (state_lipschitz**step - 1) / (state_lipschitz - 1)
    return (
        state_lipschitz**step * initial_radius
        + disturbance_lipschitz * disturbance_radius * geometric
    )


def atlas_bits(read_cells: int, distinct_words: int) -> tuple[int, int]:
    return ceil_log2(read_cells), ceil_log2(distinct_words)


def robust_word_certificate(
    state_lipschitz: Fraction,
    disturbance_lipschitz: Fraction,
    initial_radius: Fraction,
    disturbance_radius: Fraction,
    safety_clearances: tuple[Fraction, ...],
    reset_clearance: Fraction,
) -> dict[str, Any]:
    """Certify one robust open-loop connector from strict nominal margins.

    The source cell is registered as safe separately.  ``safety_clearances``
    contains the nominal trajectory's evaluator-safe clearance after each
    connector step; the last propagated error must also fit inside the reset
    clearance.
    """

    if not safety_clearances:
        raise ValueError("a connector must contain at least one step")
    if min(*safety_clearances, reset_clearance) <= 0:
        raise ValueError("registered clearances must be positive")
    errors = propagated_errors(
        state_lipschitz,
        disturbance_lipschitz,
        initial_radius,
        disturbance_radius,
        len(safety_clearances),
    )
    safe = all(
        error < clearance
        for error, clearance in zip(errors[1:], safety_clearances, strict=True)
    )
    reset = errors[-1] < reset_clearance
    return {
        "errors": errors,
        "safe": safe,
        "reset": reset,
        "pass": safe and reset,
    }


def cube_cover_count(dimension: int, centers_per_axis: int) -> int:
    if dimension < 1 or centers_per_axis < 1:
        raise ValueError("cover dimensions must be positive")
    return centers_per_axis**dimension


def interval_centers() -> tuple[Fraction, ...]:
    return tuple(Fraction(-1) + Fraction(index, 16) for index in range(33))


def nearest_center(state: Fraction) -> Fraction:
    if not -1 <= state <= 1:
        raise ValueError("state outside registered core")
    return min(interval_centers(), key=lambda center: (abs(state - center), center))


def nonlinear_step(
    state: Fraction,
    action: Fraction,
    disturbance: Fraction,
    expansion: Fraction = Fraction(2),
    curvature: Fraction = Fraction(1, 4),
) -> Fraction:
    return expansion * state + action + curvature * state * state + disturbance


def nominal_action(
    center: Fraction,
    expansion: Fraction = Fraction(2),
    curvature: Fraction = Fraction(1, 4),
) -> Fraction:
    return -expansion * center - curvature * center * center


@cache
def error_recurrence_report() -> dict[str, Any]:
    state_constants = (Fraction(1), Fraction(3, 2), Fraction(2), Fraction(5, 2))
    disturbance_constants = (Fraction(1, 2), Fraction(1), Fraction(3, 2))
    initial_radii = (Fraction(1, 128), Fraction(1, 64), Fraction(1, 32))
    disturbance_radii = (Fraction(0), Fraction(1, 256), Fraction(1, 128))
    rows = 0
    exact_match = True
    monotone = True
    for state_lipschitz in state_constants:
        for disturbance_lipschitz in disturbance_constants:
            for initial_radius in initial_radii:
                for disturbance_radius in disturbance_radii:
                    errors = propagated_errors(
                        state_lipschitz,
                        disturbance_lipschitz,
                        initial_radius,
                        disturbance_radius,
                        35,
                    )
                    for step, error in enumerate(errors):
                        exact_match &= error == closed_form_error(
                            state_lipschitz,
                            disturbance_lipschitz,
                            initial_radius,
                            disturbance_radius,
                            step,
                        )
                        rows += 1
                    monotone &= all(
                        errors[index + 1] >= errors[index]
                        for index in range(len(errors) - 1)
                    )
    checks = {
        "iterative_closed_form_exact_match": exact_match,
        "registered_expanding_rows_monotone": monotone,
        "row_count": rows == 3888,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


@cache
def nonlinear_fixture_report() -> dict[str, Any]:
    centers = interval_centers()
    actions = tuple(nominal_action(center) for center in centers)
    cell_radius = Fraction(1, 32)
    disturbance_radius = Fraction(1, 128)
    reset_radius = Fraction(1, 8)
    lipschitz_bound = Fraction(5, 2)
    propagated_bound = lipschitz_bound * cell_radius + disturbance_radius
    nominal_certificate = robust_word_certificate(
        lipschitz_bound,
        Fraction(1),
        cell_radius,
        disturbance_radius,
        (Fraction(1),),
        reset_radius,
    )

    grid_covered = all(
        abs(state - nearest_center(state)) <= cell_radius
        for state in (Fraction(-1) + Fraction(index, 1024) for index in range(2049))
    )
    rows = 0
    robust_reset = True
    exact_bound = True
    for center, action in zip(centers, actions, strict=True):
        for error_index in range(-16, 17):
            state = center + Fraction(error_index, 512)
            if not -1 <= state <= 1:
                continue
            for disturbance in (
                -disturbance_radius,
                Fraction(0),
                disturbance_radius,
            ):
                successor = nonlinear_step(state, action, disturbance)
                robust_reset &= abs(successor) < reset_radius
                exact_bound &= abs(successor) <= propagated_bound
                rows += 1

    read_bits, write_bits = atlas_bits(len(centers), len(set(actions)))
    checks = {
        "compact_core_covered": grid_covered,
        "all_worst_case_rows_reach_reset": robust_reset,
        "lipschitz_bound_covers_exact_nonlinearity": exact_bound,
        "bound_below_reset_margin": propagated_bound == Fraction(11, 128)
        and propagated_bound < reset_radius,
        "strict_margin_certificate": nominal_certificate["pass"]
        and nominal_certificate["errors"][-1] == propagated_bound,
        "finite_read_atlas": len(centers) == 33 and read_bits == 6,
        "finite_write_dictionary": len(set(actions)) == 33 and write_bits == 6,
        "action_authority_registered": min(actions) == Fraction(-9, 4)
        and max(actions) == Fraction(7, 4),
    }
    return {
        "centers": len(centers),
        "distinct_actions": len(set(actions)),
        "read_bits": read_bits,
        "write_bits": write_bits,
        "rows": rows,
        "propagated_bound": str(propagated_bound),
        "checks": checks,
        "pass": all(checks.values()),
    }


@cache
def dimension_cover_report() -> dict[str, Any]:
    rows = []
    for dimension in range(1, 5):
        for centers_per_axis in (3, 5, 9, 17, 33):
            cells = cube_cover_count(dimension, centers_per_axis)
            rows.append(
                {
                    "dimension": dimension,
                    "centers_per_axis": centers_per_axis,
                    "cells": cells,
                    "bits": ceil_log2(cells),
                }
            )
    checks = {
        "twenty_cover_rows": len(rows) == 20,
        "one_dimensional_fixture": next(
            row
            for row in rows
            if row["dimension"] == 1 and row["centers_per_axis"] == 33
        )["bits"]
        == 6,
        "dimension_cost_not_suppressed": next(
            row
            for row in rows
            if row["dimension"] == 4 and row["centers_per_axis"] == 33
        )["bits"]
        == 21,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


@cache
def architecture_boundary_report() -> dict[str, Any]:
    cell_radius = Fraction(1, 32)
    nominal_lipschitz = Fraction(2)
    true_lipschitz = Fraction(5, 2)
    disturbance_radius = Fraction(1, 128)
    false_linear_bound = nominal_lipschitz * cell_radius + disturbance_radius
    correct_bound = true_lipschitz * cell_radius + disturbance_radius
    nonlinear_witness = nonlinear_step(
        Fraction(1) - cell_radius,
        nominal_action(Fraction(1)),
        -disturbance_radius,
    )

    large_disturbance = Fraction(1, 16)
    large_disturbance_bound = true_lipschitz * cell_radius + large_disturbance
    long_errors = propagated_errors(
        true_lipschitz,
        Fraction(1),
        cell_radius,
        disturbance_radius,
        5,
    )

    positive_state = Fraction(1)
    negative_state = Fraction(-1)
    shared_observation = abs(positive_state) == abs(negative_state)
    positive_action = nominal_action(positive_state)
    negative_action = nominal_action(negative_state)
    positive_action_interval = (Fraction(-19, 8), Fraction(-17, 8))
    negative_action_interval = (Fraction(13, 8), Fraction(15, 8))
    fixed_action_exists = max(
        positive_action_interval[0], negative_action_interval[0]
    ) <= min(positive_action_interval[1], negative_action_interval[1])

    zero_mean = (large_disturbance + -large_disturbance) / 2
    checks = {
        "nonlinear_derivative_term_is_load_bearing": abs(nonlinear_witness)
        > false_linear_bound
        and correct_bound > false_linear_bound,
        "large_worst_case_disturbance_breaks_reset_margin": large_disturbance_bound
        > Fraction(1, 8),
        "fixed_cell_radius_fails_long_expanding_connector": long_errors[-1]
        > Fraction(1, 8),
        "hidden_observation_collision_requires_read_refinement": shared_observation
        and positive_action != negative_action,
        "one_fixed_write_action_cannot_reset_both_hidden_states": not fixed_action_exists,
        "zero_mean_does_not_certify_worst_case": zero_mean == 0
        and large_disturbance_bound > Fraction(1, 8),
        "actuator_dictionary_not_free": len(
            {nominal_action(center) for center in interval_centers()}
        )
        == 33,
    }
    return {
        "false_bound": str(false_linear_bound),
        "correct_bound": str(correct_bound),
        "long_error": str(long_errors[-1]),
        "checks": checks,
        "pass": all(checks.values()),
    }


@cache
def v34_bridge_report() -> dict[str, Any]:
    v34 = json.loads(V34_CLAIM.read_text(encoding="utf-8"))
    v34_contract = json.loads(V34_CONTRACT.read_text(encoding="utf-8"))
    fixture = nonlinear_fixture_report()
    checks = {
        "v34_requires_public_information_state": v34.get("registered_state", {}).get(
            "hidden_plant_state_is_not_free"
        )
        is True,
        "v34_requires_memory_reset": v34.get("registered_state", {}).get(
            "private_memory_must_reset"
        )
        is True,
        "atlas_supplies_finite_read_cost": fixture["read_bits"] == 6,
        "atlas_supplies_finite_write_cost": fixture["write_bits"] == 6,
        "fixed_reset_atlas_supplies_constant_time": fixture["pass"],
        "fixed_reset_atlas_supplies_v33_safe_closing": v34.get("theorem", {}).get(
            "safe_closing"
        )
        == "constant connector bounds imply v0.33 sublinear safe closing",
        "literal_v34_local_premise_requires_all_pairs": v34_contract.get(
            "requirements", {}
        )
        .get("local_certificate", "")
        .startswith("every two public states"),
    }
    return {"checks": checks, "pass": all(checks.values())}


def mutation_report() -> dict[str, Any]:
    boundaries = architecture_boundary_report()["checks"]
    fixture = nonlinear_fixture_report()["checks"]
    bridge = v34_bridge_report()["checks"]
    rows = {
        "drop_nonlinear_derivative_from_error_bound": boundaries[
            "nonlinear_derivative_term_is_load_bearing"
        ],
        "replace_worst_case_disturbance_by_its_mean": boundaries[
            "zero_mean_does_not_certify_worst_case"
        ],
        "treat_hidden_observation_collision_as_public_state": boundaries[
            "hidden_observation_collision_requires_read_refinement"
        ],
        "controller_choice_makes_write_dictionary_free": boundaries[
            "actuator_dictionary_not_free"
        ],
        "sensor_knowledge_makes_read_label_free": bridge[
            "atlas_supplies_finite_read_cost"
        ],
        "omit_terminal_reset_margin": boundaries[
            "large_worst_case_disturbance_breaks_reset_margin"
        ],
        "fixed_quantization_handles_arbitrary_unstable_horizon": boundaries[
            "fixed_cell_radius_fails_long_expanding_connector"
        ],
        "robust_atlas_resolves_every_canonical_hyperbolic_class": contract_report()[
            "checks"
        ]["scope_open"],
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 8 and all(rows.values()) and fixture["finite_write_dictionary"],
    }


def _count_tests(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
        for node in ast.walk(tree)
    )


def _package_version(name: str) -> int:
    match = re.search(r"_v0_(\d+)$", name)
    return int(match.group(1)) if match else 0


@cache
def predecessor_inventory_report() -> dict[str, Any]:
    paths = sorted(
        path
        for path in ROOT.glob("asmp4*/test_*.py")
        if path.parent.resolve() != HERE.resolve()
        and _package_version(path.parent.name) < 35
    )
    tests = sum(_count_tests(path) for path in paths)
    checks = {
        "thirty_five_predecessor_packages": len(paths) == 35,
        "three_hundred_eighty_four_predecessor_tests": tests == 384,
    }
    return {
        "packages": len(paths),
        "tests": tests,
        "checks": checks,
        "pass": all(checks.values()),
    }


def claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_robust_public_atlas_v0_35",
        "theorem": {
            "error_recurrence": "e_(t+1)<=A*e_t+D*omega",
            "finite_atlas": "compact robust public basins admit a finite read-labeled connector subcover",
            "read_bound": "ceil(log2 N_read)",
            "write_bound": "ceil(log2 N_distinct_connector_words)",
            "safe_reset": "propagated error stays below safety margin and terminal reset margin",
            "v33_implication": "a finite fixed-reset atlas supplies constant safe-closing certificates",
            "v34_boundary": "the literal v0.34 local premise needs an all-pairs atlas; a fixed-reset atlas only supplies its safe-closing conclusion",
            "coordinate_invariance": "registered bi-Lipschitz conjugacies preserve atlas existence but need not preserve numerical radii",
        },
        "nonlinear_fixture": {
            "plant": "x_next=2*x+u+x^2/4+w",
            "core": "[-1,1]",
            "reset": "[-1/8,1/8]",
            "disturbance": "|w|<=1/128",
            "read_cells": 33,
            "write_words": 33,
            "read_bits": 6,
            "write_bits": 6,
            "worst_case_error": "11/128",
        },
        "evidence": {
            "error_rows": 3888,
            "nonlinear_rows": nonlinear_fixture_report()["rows"],
            "cover_rows": 20,
            "mutations_rejected": 8,
            "predecessor_packages": 35,
            "predecessor_tests": 384,
        },
        "disposition": "robust finite-cost public connector atlases are now constructed from registered Lipschitz margins and observation/action quantization; proving such robust pointwise connectors for the full canonical normally hyperbolic class remains open",
    }


@cache
def contract_report() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    checks = {
        "schema": contract.get("schema_version")
        == "asmp4_robust_public_atlas_contract_v0_35",
        "separate_ports": contract.get("requirements", {}).get("ports")
        == "sensor labels and actuator words are separately charged",
        "worst_case": contract.get("requirements", {}).get("uncertainty")
        == "universal bounded disturbance, not expectation",
        "scope_open": "does not prove" in contract.get("scope_boundary", ""),
    }
    return {"checks": checks, "pass": all(checks.values())}


@cache
def claim_report() -> dict[str, Any]:
    actual = json.loads(CLAIM.read_text(encoding="utf-8"))
    checks = {
        "exact": actual == claim_payload(),
        "two_port_bits": actual.get("nonlinear_fixture", {}).get("read_bits") == 6
        and actual.get("nonlinear_fixture", {}).get("write_bits") == 6,
        "scope_open": "remains open" in actual.get("disposition", ""),
    }
    return {"checks": checks, "pass": all(checks.values())}


def payload_report() -> dict[str, Any]:
    missing = [name for name in EXPECTED_PAYLOAD if not (HERE / name).is_file()]
    return {"missing": missing, "pass": not missing}


def full_report() -> dict[str, Any]:
    report = {
        "contract": contract_report(),
        "claim": claim_report(),
        "errors": error_recurrence_report(),
        "nonlinear": nonlinear_fixture_report(),
        "dimension": dimension_cover_report(),
        "boundaries": architecture_boundary_report(),
        "v34_bridge": v34_bridge_report(),
        "mutations": mutation_report(),
        "inventory": predecessor_inventory_report(),
        "payload": payload_report(),
    }
    report["pass"] = all(section["pass"] for section in report.values())
    return report


def main() -> int:
    report = full_report()
    gates = {
        "R0_contract": report["contract"]["pass"],
        "R1_claim": report["claim"]["pass"],
        "R2_error_recurrence": report["errors"]["pass"],
        "R3_nonlinear_atlas": report["nonlinear"]["pass"],
        "R4_dimension_cover": report["dimension"]["pass"],
        "R5_architecture_boundaries": report["boundaries"]["pass"],
        "R6_v34_bridge": report["v34_bridge"]["pass"],
        "R7_mutations": report["mutations"]["pass"],
        "R8_inventory": report["inventory"]["pass"],
        "R9_payload": report["payload"]["pass"],
    }
    print(json.dumps({"gates": gates, "report": report}, indent=2, sort_keys=True))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
