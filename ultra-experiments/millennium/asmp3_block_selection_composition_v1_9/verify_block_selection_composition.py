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
RESULT_PATH = HERE / "artifacts" / "block_selection_composition_v1_9.json"
OUTPUT_PATH = (
    HERE / "artifacts" / "block_selection_composition_verification_v1_9.json"
)
PARENT_PATH = (
    HERE.parent
    / "asmp3_independent_noise_amplification_v1_8"
    / "artifacts"
    / "independent_noise_amplification_v1_8.json"
)
ETAS = (Q(1, 10), Q(1, 5), Q(1, 3), Q(2, 5))
ATOMS = (1, 2, 4, 8, 16, 32)

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(100_000)


def text(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


@cache
def majority_error(depth: int, eta: Q) -> Q:
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


def reconstruct_row(row: dict[str, object]) -> bool:
    atoms = int(row["atoms"])
    depth = int(row["replications_per_atom"])
    eta = Q(row["eta"])
    error = majority_error(depth, eta)
    independent = 1 - (1 - error) ** atoms
    union = min(Q(1), atoms * error)
    per_atom_persistent = 1 - (1 - eta) ** atoms
    return (
        int(row["total_semantic_queries"]) == atoms * depth
        and Q(row["single_atom_majority_error"]) == error
        and Q(row["independent_block_any_error"]) == independent
        and Q(row["or_all_zero_refutation_error"]) == independent
        and Q(row["truth_aware_failure_selector_risk"]) == independent
        and Q(row["union_bound"]) == union
        and Q(row["marginal_only_extremal_union_risk"]) == union
        and Q(row["selector_inflation_over_one_atom"]) == independent - error
        and Q(row["marginal_only_gap_over_block_independence"])
        == union - independent
        and Q(row["independent_per_atom_persistent_risk"])
        == per_atom_persistent
        and Q(row["one_global_persistent_risk"]) == eta
        and Q(row["block_independence_improvement_over_per_atom_persistence"])
        == per_atom_persistent - independent
        and row["certified"] is True
    )


def enumerate_case(atoms: int, depth: int, eta: Q) -> tuple[int, Q]:
    risk = Q(0)
    count = 0
    for bits in product((0, 1), repeat=atoms * depth):
        failed = any(
            sum(bits[atom * depth : (atom + 1) * depth]) > depth // 2
            for atom in range(atoms)
        )
        errors = sum(bits)
        mass = eta**errors * (1 - eta) ** (atoms * depth - errors)
        if failed:
            risk += mass
        count += 1
    return count, risk


def search_depth(atoms: int, eta: Q, target: Q, union_safe: bool) -> int:
    for depth in (1, *range(3, 2048, 2)):
        error = majority_error(depth, eta)
        risk = min(Q(1), atoms * error) if union_safe else 1 - (1 - error) ** atoms
        if risk <= target:
            return depth
    raise RuntimeError("clean-room depth search exceeded limit")


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_PATH.read_text(encoding="utf-8"))
    rows = result.get("composition_rows", [])
    expected_keys = [
        (text(eta), atoms, depth)
        for eta in ETAS
        for atoms in ATOMS
        for depth in range(1, 32)
    ]

    small = result.get("small_response_enumeration", [])
    small_match = len(small) == 12
    for row in small:
        atoms = int(row["atoms"])
        depth = int(row["replications_per_atom"])
        eta = Q(row["eta"])
        count, risk = enumerate_case(atoms, depth, eta)
        formula = 1 - (1 - majority_error(depth, eta)) ** atoms
        small_match = small_match and (
            int(row["response_profiles_enumerated"]) == count
            and Q(row["enumerated_or_error"]) == risk
            and Q(row["independent_block_formula"]) == formula
            and row["matches"] is (risk == formula)
        )

    requirements = result.get("depth_requirement_rows", [])
    requirement_match = len(requirements) == 24
    for row in requirements:
        atoms = int(row["atoms"])
        eta = Q(row["eta"])
        target = Q(row["target_joint_risk"])
        exact_depth = search_depth(atoms, eta, target, False)
        safe_depth = search_depth(atoms, eta, target, True)
        exact_risk = 1 - (1 - majority_error(exact_depth, eta)) ** atoms
        safe_bound = min(Q(1), atoms * majority_error(safe_depth, eta))
        previous_exact = (
            1 - (1 - majority_error(exact_depth - 2, eta)) ** atoms
            if exact_depth > 1
            else None
        )
        previous_safe = (
            min(Q(1), atoms * majority_error(safe_depth - 2, eta))
            if safe_depth > 1
            else None
        )
        requirement_match = requirement_match and (
            int(row["minimal_exact_odd_depth"]) == exact_depth
            and int(row["exact_total_queries"]) == atoms * exact_depth
            and Q(row["exact_risk_at_depth"]) == exact_risk
            and (
                row["exact_previous_odd_risk"] is None
                if previous_exact is None
                else Q(row["exact_previous_odd_risk"]) == previous_exact
            )
            and int(row["minimal_union_safe_odd_depth"]) == safe_depth
            and int(row["union_safe_total_queries"]) == atoms * safe_depth
            and Q(row["union_bound_at_safe_depth"]) == safe_bound
            and (
                row["union_previous_odd_bound"] is None
                if previous_safe is None
                else Q(row["union_previous_odd_bound"]) == previous_safe
            )
            and row["exact_minimality_certified"] is True
            and row["union_minimality_certified"] is True
        )

    selection = result.get("selection_inflation_witness", {})
    marginal = result.get("marginal_class_witness", {})
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version") == "asmp3_block_selection_composition_v1_9"
            and result.get("status")
            == "exact_finite_block_composition_and_selection_risk"
            and result.get("parent_result")
            == "ASMP-3-INDEPENDENT-NOISE-AMPLIFICATION-v1.8"
            and result.get("certified") is True
            and "not the value of every" in result.get("claim_boundary", "")
        ),
        "V1_complete_744_row_registry_reconstructed": (
            len(rows) == 744
            and [
                (row["eta"], row["atoms"], row["replications_per_atom"])
                for row in rows
            ]
            == expected_keys
        ),
        "V2_all_composition_and_correlation_fields_reconstructed": all(
            reconstruct_row(row) for row in rows
        ),
        "V3_small_multi_block_spaces_replayed": small_match,
        "V4_all_depth_requirements_independently_minimized": requirement_match,
        "V5_selection_and_marginal_witnesses_exact": (
            selection.get("atoms") == 32
            and selection.get("replications_per_atom") == 9
            and Q(selection.get("selector_inflation_over_one_atom")) > 0
            and marginal.get("atoms") == 16
            and marginal.get("replications_per_atom") == 5
            and Q(marginal.get("marginal_only_gap_over_block_independence")) > 0
        ),
        "V6_parent_single_atom_profile_contract_matches": (
            parent["theorem"]["value"] == "1-2*bayes_error(d,eta)"
            and all(
                Q(row["single_atom_majority_error"])
                == Q(row["independent_block_any_error"])
                for row in rows
                if row["atoms"] == 1
            )
        ),
        "V7_producer_gates_all_true": (
            len(result.get("gates", {})) == 9 and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_block_selection_composition_verification_v1_9",
        "checker": "clean_room_block_union_selection_and_depth_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker validates disjoint independent blocks with fixed "
            "majority decoders and the declared OR/failure-selector interface. "
            "It is not a global adaptive-protocol optimizer."
        ),
    }


def main() -> None:
    result = verify()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not result["passed"]:
        failed = [name for name, passed in result["checks"].items() if not passed]
        raise SystemExit(f"block-composition verification failed: {failed}")
    print(
        "ASMP-3 block-composition verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
