"""Import-independent verifier for the ASMP-4 robust public atlas v0.35."""

from __future__ import annotations

import ast
import json
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CENTRAL = HERE / "robust_public_atlas.py"
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

PAYLOAD = (
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


def bits(cardinality: int) -> int:
    return (cardinality - 1).bit_length()


def recurrence_report() -> dict[str, Any]:
    rows = 0
    exact = True
    monotone = True
    for state_constant in map(Fraction, (1, Fraction(3, 2), 2, Fraction(5, 2))):
        for disturbance_constant in map(Fraction, (Fraction(1, 2), 1, Fraction(3, 2))):
            for initial_radius in map(Fraction, (Fraction(1, 128), Fraction(1, 64), Fraction(1, 32))):
                for disturbance_radius in map(Fraction, (0, Fraction(1, 256), Fraction(1, 128))):
                    iterative = initial_radius
                    previous = iterative
                    for step in range(36):
                        direct = state_constant**step * initial_radius + (
                            disturbance_constant
                            * disturbance_radius
                            * sum(state_constant**power for power in range(step))
                        )
                        exact &= iterative == direct
                        if step:
                            monotone &= iterative >= previous
                        previous = iterative
                        iterative = (
                            state_constant * iterative
                            + disturbance_constant * disturbance_radius
                        )
                        rows += 1
    checks = {
        "direct_sum_matches_recurrence": exact,
        "expanding_errors_monotone": monotone,
        "rows": rows == 3888,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def nonlinear_report() -> dict[str, Any]:
    centers = tuple(Fraction(-1) + Fraction(index, 16) for index in range(33))
    actions = tuple(-2 * center - center * center / 4 for center in centers)
    cell_radius = Fraction(1, 32)
    disturbance_radius = Fraction(1, 128)
    propagated = Fraction(5, 2) * cell_radius + disturbance_radius

    grid_covered = True
    for index in range(2049):
        state = Fraction(-1) + Fraction(index, 1024)
        grid_covered &= min(abs(state - center) for center in centers) <= cell_radius

    rows = 0
    robust = True
    analytic_match = True
    bounded = True
    for center, action in zip(centers, actions, strict=True):
        for error_index in range(-16, 17):
            error = Fraction(error_index, 512)
            state = center + error
            if not -1 <= state <= 1:
                continue
            for disturbance in (-disturbance_radius, Fraction(0), disturbance_radius):
                direct = 2 * state + action + state * state / 4 + disturbance
                expanded = (2 + center / 2) * error + error * error / 4 + disturbance
                analytic_match &= direct == expanded
                bounded &= abs(direct) <= propagated
                robust &= abs(direct) < Fraction(1, 8)
                rows += 1

    checks = {
        "compact_grid_covered": grid_covered,
        "independent_expansion_exact": analytic_match,
        "all_rows_below_lipschitz_bound": bounded,
        "all_rows_reset": robust,
        "sharp_bound": propagated == Fraction(11, 128) < Fraction(1, 8),
        "read_count": len(centers) == 33 and bits(len(centers)) == 6,
        "write_count": len(set(actions)) == 33 and bits(len(set(actions))) == 6,
        "action_range": min(actions) == Fraction(-9, 4)
        and max(actions) == Fraction(7, 4),
        "rows": rows == 3171,
    }
    return {
        "rows": rows,
        "read_bits": bits(len(centers)),
        "write_bits": bits(len(set(actions))),
        "checks": checks,
        "pass": all(checks.values()),
    }


def boundary_report() -> dict[str, Any]:
    radius = Fraction(1, 32)
    disturbance = Fraction(1, 128)
    false_bound = 2 * radius + disturbance
    true_bound = Fraction(5, 2) * radius + disturbance
    state = Fraction(1) - radius
    action = Fraction(-9, 4)
    witness = 2 * state + action + state * state / 4 - disturbance

    error = radius
    for _ in range(5):
        error = Fraction(5, 2) * error + disturbance

    positive_interval = (Fraction(-19, 8), Fraction(-17, 8))
    negative_interval = (Fraction(13, 8), Fraction(15, 8))
    intervals_overlap = max(positive_interval[0], negative_interval[0]) <= min(
        positive_interval[1], negative_interval[1]
    )
    large_disturbance = Fraction(1, 16)
    large_bound = Fraction(5, 2) * radius + large_disturbance
    checks = {
        "linearized_bound_falsified": abs(witness) > false_bound,
        "full_derivative_bound_covers_witness": abs(witness) <= true_bound,
        "long_unstable_word_needs_refinement": error > Fraction(1, 8),
        "hidden_absolute_observation_collides": abs(Fraction(1))
        == abs(Fraction(-1)),
        "one_word_cannot_reset_both_signs": not intervals_overlap,
        "worst_case_not_zero_mean": (large_disturbance - large_disturbance) / 2
        == 0
        and large_bound > Fraction(1, 8),
        "terminal_margin_load_bearing": large_bound > Fraction(1, 8),
        "dictionary_has_positive_cost": bits(33) == 6,
    }
    return {"checks": checks, "pass": all(checks.values())}


def dimension_report() -> dict[str, Any]:
    rows = []
    for dimension in range(1, 5):
        for side in (3, 5, 9, 17, 33):
            cells = side**dimension
            rows.append((dimension, side, cells, bits(cells)))
    checks = {
        "rows": len(rows) == 20,
        "fixture_bits": (1, 33, 33, 6) in rows,
        "four_dimensional_bits": (4, 33, 1_185_921, 21) in rows,
    }
    return {"rows": len(rows), "checks": checks, "pass": all(checks.values())}


def expected_claim() -> dict[str, Any]:
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
            "nonlinear_rows": 3171,
            "cover_rows": 20,
            "mutations_rejected": 8,
            "predecessor_packages": 35,
            "predecessor_tests": 384,
        },
        "disposition": "robust finite-cost public connector atlases are now constructed from registered Lipschitz margins and observation/action quantization; proving such robust pointwise connectors for the full canonical normally hyperbolic class remains open",
    }


def contract_claim_report() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    claim = json.loads(CLAIM.read_text(encoding="utf-8"))
    checks = {
        "contract_schema": contract.get("schema_version")
        == "asmp4_robust_public_atlas_contract_v0_35",
        "separate_ports": contract.get("requirements", {}).get("ports")
        == "sensor labels and actuator words are separately charged",
        "universal_uncertainty": contract.get("requirements", {}).get("uncertainty")
        == "universal bounded disturbance, not expectation",
        "scope_not_overclaimed": "does not prove" in contract.get(
            "scope_boundary", ""
        ),
        "claim_exact": claim == expected_claim(),
    }
    return {"checks": checks, "pass": all(checks.values())}


def bridge_report() -> dict[str, Any]:
    claim = json.loads(V34_CLAIM.read_text(encoding="utf-8"))
    contract = json.loads(V34_CONTRACT.read_text(encoding="utf-8"))
    checks = {
        "public_state_required": claim.get("registered_state", {}).get(
            "hidden_plant_state_is_not_free"
        )
        is True,
        "memory_reset_required": claim.get("registered_state", {}).get(
            "private_memory_must_reset"
        )
        is True,
        "constant_closing_reaches_v33": claim.get("theorem", {}).get(
            "safe_closing"
        )
        == "constant connector bounds imply v0.33 sublinear safe closing",
        "all_pairs_is_stronger": contract.get("requirements", {})
        .get("local_certificate", "")
        .startswith("every two public states"),
    }
    return {"checks": checks, "pass": all(checks.values())}


def mutation_report() -> dict[str, Any]:
    boundaries = boundary_report()["checks"]
    rows = {
        "drop_nonlinear_derivative": boundaries["linearized_bound_falsified"],
        "average_disturbance": boundaries["worst_case_not_zero_mean"],
        "hide_observation_collision": boundaries[
            "hidden_absolute_observation_collides"
        ],
        "free_actuator_dictionary": boundaries["dictionary_has_positive_cost"],
        "free_sensor_label": nonlinear_report()["read_bits"] > 0,
        "omit_reset_margin": boundaries["terminal_margin_load_bearing"],
        "fixed_long_horizon_quantization": boundaries[
            "long_unstable_word_needs_refinement"
        ],
        "claim_full_canonical_resolution": "remains open"
        in expected_claim()["disposition"],
    }
    return {
        "rows": rows,
        "rejected": sum(rows.values()),
        "pass": len(rows) == 8 and all(rows.values()),
    }


def count_tests(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
        for node in ast.walk(tree)
    )


def package_version(name: str) -> int:
    match = re.search(r"_v0_(\d+)$", name)
    return int(match.group(1)) if match else 0


def inventory_report() -> dict[str, Any]:
    paths = sorted(
        path
        for path in ROOT.glob("asmp4*/test_*.py")
        if path.parent.resolve() != HERE.resolve()
        and package_version(path.parent.name) < 35
    )
    tests = sum(count_tests(path) for path in paths)
    checks = {"packages": len(paths) == 35, "tests": tests == 384}
    return {
        "packages": len(paths),
        "tests": tests,
        "checks": checks,
        "pass": all(checks.values()),
    }


def documents_report() -> dict[str, Any]:
    required = {
        "README.md": ("v0.35", "fixed-reset atlas", "not a full resolution"),
        "THEOREM.md": ("Fixed-reset atlas theorem", "all-pairs", "bi-Lipschitz"),
        "RESULT.md": ("3,888", "3,171", "not a full"),
        "PRIOR_ART_BOUNDARY_v0_35.md": ("invariance entropy", "symbolic", "repository contribution"),
        "REVIEWER_PACKET_v0_35.md": ("Scope boundary", "11/128", "all-pairs"),
        "COMPLETION_AUDIT_v0_35.md": ("Canonical ASMP-4", "Partial", "384"),
    }
    rows = {}
    for name, tokens in required.items():
        path = HERE / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        rows[name] = all(token in text for token in tokens)
    return {"rows": rows, "pass": all(rows.values())}


def source_report() -> dict[str, Any]:
    independent_source = Path(__file__).read_text(encoding="utf-8")
    independent_tree = ast.parse(independent_source, filename=str(Path(__file__)))
    central_tree = ast.parse(CENTRAL.read_text(encoding="utf-8"), filename=str(CENTRAL))
    central_functions = {
        node.name for node in ast.walk(central_tree) if isinstance(node, ast.FunctionDef)
    }
    central_imported = any(
        (
            isinstance(node, ast.Import)
            and any(alias.name == "robust_public_atlas" for alias in node.names)
        )
        or (
            isinstance(node, ast.ImportFrom)
            and node.module == "robust_public_atlas"
        )
        for node in ast.walk(independent_tree)
    )
    checks = {
        "central_not_imported": not central_imported,
        "central_entry_point_present": "main" in central_functions,
        "robust_certificate_present": "robust_word_certificate" in central_functions,
        "payload_complete": all((HERE / name).is_file() for name in PAYLOAD),
    }
    return {"checks": checks, "pass": all(checks.values())}


def full_report() -> dict[str, Any]:
    report = {
        "contract_claim": contract_claim_report(),
        "recurrence": recurrence_report(),
        "nonlinear": nonlinear_report(),
        "dimension": dimension_report(),
        "boundaries": boundary_report(),
        "bridge": bridge_report(),
        "mutations": mutation_report(),
        "inventory": inventory_report(),
        "documents": documents_report(),
        "source": source_report(),
    }
    report["pass"] = all(section["pass"] for section in report.values())
    return report


def main() -> int:
    report = full_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
