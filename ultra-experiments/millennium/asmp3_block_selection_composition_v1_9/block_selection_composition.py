from __future__ import annotations

import json
import sys
from fractions import Fraction
from functools import cache
from itertools import product
from math import comb
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
PARENT_ARTIFACT = (
    HERE.parent
    / "asmp3_independent_noise_amplification_v1_8"
    / "artifacts"
    / "independent_noise_amplification_v1_8.json"
)
ETA_REGISTRY = (Q(1, 10), Q(1, 5), Q(1, 3), Q(2, 5))
ATOM_REGISTRY = (1, 2, 4, 8, 16, 32)

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(100_000)


def qstr(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def validate(atoms: int, depth: int, eta: Q) -> None:
    if not isinstance(atoms, int) or atoms < 1:
        raise ValueError("atom count must be positive")
    if not isinstance(depth, int) or depth < 1:
        raise ValueError("replication depth must be positive")
    if eta < 0 or eta >= Q(1, 2):
        raise ValueError("eta must lie in [0,1/2)")


@cache
def atom_error(depth: int, eta: Q) -> Q:
    if depth < 1 or eta < 0 or eta >= Q(1, 2):
        raise ValueError("invalid atom-error parameters")
    result = sum(
        (
            Q(comb(depth, errors))
            * eta**errors
            * (1 - eta) ** (depth - errors)
            for errors in range(depth // 2 + 1, depth + 1)
        ),
        Q(0),
    )
    if depth % 2 == 0:
        result += (
            Q(comb(depth, depth // 2))
            * eta ** (depth // 2)
            * (1 - eta) ** (depth // 2)
            / 2
        )
    return result


def composition_row(atoms: int, depth: int, eta: Q | int) -> dict[str, object]:
    eta = Q(eta)
    validate(atoms, depth, eta)
    error = atom_error(depth, eta)
    independent = Q(1) - (Q(1) - error) ** atoms
    union = min(Q(1), atoms * error)
    per_atom_persistent = Q(1) - (Q(1) - eta) ** atoms
    global_persistent = eta
    return {
        "atoms": atoms,
        "replications_per_atom": depth,
        "eta": qstr(eta),
        "total_semantic_queries": atoms * depth,
        "single_atom_majority_error": qstr(error),
        "independent_block_any_error": qstr(independent),
        "or_all_zero_refutation_error": qstr(independent),
        "truth_aware_failure_selector_risk": qstr(independent),
        "union_bound": qstr(union),
        "marginal_only_extremal_union_risk": qstr(union),
        "selector_inflation_over_one_atom": qstr(independent - error),
        "marginal_only_gap_over_block_independence": qstr(union - independent),
        "independent_per_atom_persistent_risk": qstr(per_atom_persistent),
        "one_global_persistent_risk": qstr(global_persistent),
        "block_independence_improvement_over_per_atom_persistence": qstr(
            per_atom_persistent - independent
        ),
        "certified": (
            error <= independent <= union
            and independent <= per_atom_persistent
            and independent == Q(1) - (Q(1) - error) ** atoms
            and union == min(Q(1), atoms * error)
        ),
    }


def enumerate_small_case(atoms: int, depth: int, eta: Q) -> dict[str, object]:
    if depth % 2 == 0:
        raise ValueError("small enumeration uses odd depths to avoid tie coins")
    validate(atoms, depth, eta)
    risk = Q(0)
    profiles = 0
    for bits in product((0, 1), repeat=atoms * depth):
        block_failures = []
        for atom in range(atoms):
            block = bits[atom * depth : (atom + 1) * depth]
            block_failures.append(sum(block) > depth // 2)
        errors = sum(bits)
        probability = eta**errors * (1 - eta) ** (atoms * depth - errors)
        if any(block_failures):
            risk += probability
        profiles += 1
    formula = Q(1) - (Q(1) - atom_error(depth, eta)) ** atoms
    return {
        "atoms": atoms,
        "replications_per_atom": depth,
        "eta": qstr(eta),
        "response_profiles_enumerated": profiles,
        "enumerated_or_error": qstr(risk),
        "independent_block_formula": qstr(formula),
        "matches": risk == formula,
    }


def minimal_depth(
    atoms: int, eta: Q, target: Q, *, union_safe: bool
) -> int:
    if atoms < 1 or eta <= 0 or eta >= Q(1, 2) or target <= 0 or target >= 1:
        raise ValueError("invalid depth-search parameters")
    candidates = (1, *range(3, 2048, 2))
    for depth in candidates:
        error = atom_error(depth, eta)
        risk = min(Q(1), atoms * error) if union_safe else Q(1) - (1 - error) ** atoms
        if risk <= target:
            return depth
    raise RuntimeError("depth search exceeded registered limit")


def depth_requirement_rows() -> list[dict[str, object]]:
    rows = []
    for eta in (Q(1, 5), Q(1, 3), Q(2, 5)):
        for atoms in (1, 4, 16, 64):
            for target in (Q(1, 10), Q(1, 100)):
                exact_depth = minimal_depth(atoms, eta, target, union_safe=False)
                safe_depth = minimal_depth(atoms, eta, target, union_safe=True)
                exact_row = composition_row(atoms, exact_depth, eta)
                safe_row = composition_row(atoms, safe_depth, eta)
                previous_exact = (
                    composition_row(atoms, exact_depth - 2, eta)
                    if exact_depth > 1
                    else None
                )
                previous_safe = (
                    composition_row(atoms, safe_depth - 2, eta)
                    if safe_depth > 1
                    else None
                )
                rows.append(
                    {
                        "atoms": atoms,
                        "eta": qstr(eta),
                        "target_joint_risk": qstr(target),
                        "minimal_exact_odd_depth": exact_depth,
                        "exact_total_queries": atoms * exact_depth,
                        "exact_risk_at_depth": exact_row["independent_block_any_error"],
                        "exact_previous_odd_risk": (
                            previous_exact["independent_block_any_error"]
                            if previous_exact
                            else None
                        ),
                        "minimal_union_safe_odd_depth": safe_depth,
                        "union_safe_total_queries": atoms * safe_depth,
                        "union_bound_at_safe_depth": safe_row["union_bound"],
                        "union_previous_odd_bound": (
                            previous_safe["union_bound"] if previous_safe else None
                        ),
                        "exact_minimality_certified": (
                            Q(exact_row["independent_block_any_error"]) <= target
                            and (
                                previous_exact is None
                                or Q(previous_exact["independent_block_any_error"])
                                > target
                            )
                        ),
                        "union_minimality_certified": (
                            Q(safe_row["union_bound"]) <= target
                            and (
                                previous_safe is None
                                or Q(previous_safe["union_bound"]) > target
                            )
                        ),
                    }
                )
    return rows


def build_result() -> dict[str, object]:
    parent = json.loads(PARENT_ARTIFACT.read_text(encoding="utf-8"))
    rows = [
        composition_row(atoms, depth, eta)
        for eta in ETA_REGISTRY
        for atoms in ATOM_REGISTRY
        for depth in range(1, 32)
    ]
    enumeration = [
        enumerate_small_case(atoms, depth, eta)
        for eta in (Q(1, 5), Q(1, 3))
        for atoms in (1, 2, 3)
        for depth in (1, 3)
    ]
    requirements = depth_requirement_rows()
    selection_witness = composition_row(32, 9, Q(1, 5))
    marginal_witness = composition_row(16, 5, Q(1, 3))
    gates = {
        "C0_registry_complete": (
            len(rows) == len(ETA_REGISTRY) * len(ATOM_REGISTRY) * 31
            and [(row["eta"], row["atoms"], row["replications_per_atom"]) for row in rows]
            == [
                (qstr(eta), atoms, depth)
                for eta in ETA_REGISTRY
                for atoms in ATOM_REGISTRY
                for depth in range(1, 32)
            ]
        ),
        "C1_all_composition_rows_certified": all(row["certified"] for row in rows),
        "C2_small_response_spaces_enumerated_exactly": (
            len(enumeration) == 12 and all(row["matches"] for row in enumeration)
        ),
        "C3_or_and_failure_selection_risks_coincide": all(
            row["independent_block_any_error"]
            == row["or_all_zero_refutation_error"]
            == row["truth_aware_failure_selector_risk"]
            for row in rows
        ),
        "C4_marginal_extremum_and_union_bound_exact": all(
            row["marginal_only_extremal_union_risk"] == row["union_bound"]
            and Q(row["independent_block_any_error"]) <= Q(row["union_bound"])
            for row in rows
        ),
        "C5_replication_depth_requirements_minimal": (
            len(requirements) == 24
            and all(
                row["exact_minimality_certified"]
                and row["union_minimality_certified"]
                and row["minimal_exact_odd_depth"] <= row["minimal_union_safe_odd_depth"]
                for row in requirements
            )
        ),
        "C6_query_costs_are_charged": all(
            row["total_semantic_queries"]
            == row["atoms"] * row["replications_per_atom"]
            for row in rows
        ),
        "C7_correlation_class_separations_witnessed": (
            Q(marginal_witness["marginal_only_gap_over_block_independence"]) > 0
            and Q(selection_witness["selector_inflation_over_one_atom"]) > 0
            and Q(selection_witness["block_independence_improvement_over_per_atom_persistence"])
            > 0
        ),
        "C8_parent_single_atom_profile_matches": (
            parent["theorem"]["value"] == "1-2*bayes_error(d,eta)"
            and all(
                composition_row(1, depth, eta)["single_atom_majority_error"]
                == composition_row(1, depth, eta)["independent_block_any_error"]
                for eta in ETA_REGISTRY
                for depth in range(1, 32)
            )
        ),
    }
    return {
        "schema_version": "asmp3_block_selection_composition_v1_9",
        "experiment_id": "ASMP-3-BLOCK-SELECTION-COMPOSITION-v1.9",
        "status": "exact_finite_block_composition_and_selection_risk",
        "parent_result": "ASMP-3-INDEPENDENT-NOISE-AMPLIFICATION-v1.8",
        "theorem": {
            "single_atom_error": "e_d(eta) from v1.8",
            "independent_M_atom_risk": "1-(1-e_d)^M",
            "marginal_only_extremal_risk": "min(1,M e_d)",
            "tight_predicate": "OR on an all-zero truth vector",
            "tight_selector": "choose a failed decoded block whenever one exists",
            "query_cost": "M*d semantic queries",
        },
        "registry_parameters": {
            "etas": [qstr(eta) for eta in ETA_REGISTRY],
            "atoms": list(ATOM_REGISTRY),
            "depths": [1, 31],
            "row_count": len(rows),
        },
        "composition_rows": rows,
        "small_response_enumeration": enumeration,
        "depth_requirement_rows": requirements,
        "selection_inflation_witness": selection_witness,
        "marginal_class_witness": marginal_witness,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The exact joint formula requires disjoint conditionally independent "
            "replication blocks and fixed majority decoders. The OR/selector "
            "witnesses establish tight composition risk for this interface, not "
            "the value of every globally optimized adaptive protocol."
        ),
    }
