from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "finite_tv_frontier_v0_8.json"
OUTPUT_PATH = (
    HERE / "artifacts" / "finite_tv_frontier_verification_v0_8.json"
)


def q(value: str | int) -> Fraction:
    return Fraction(value)


def qvector(values: Sequence[str | int]) -> tuple[Fraction, ...]:
    return tuple(q(value) for value in values)


def scalar(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return sum((x * y for x, y in zip(left, right)), Fraction(0))


def load_result() -> dict[str, object]:
    value = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("frontier result must be a JSON object")
    return value


def check_explicit_certificate(row: dict[str, object]) -> bool:
    honest = tuple(qvector(law) for law in row["honest_laws"])
    false = tuple(qvector(law) for law in row["false_laws"])
    acceptance = qvector(row["acceptance_certificate"])
    weights = qvector(row["joint_dual_weights"])
    positive = qvector(row["dual_positive_part"])
    gap = q(row["claimed_gap"])

    if not honest or not false or len(weights) != len(honest) * len(false):
        return False
    width = len(acceptance)
    laws = (*honest, *false)
    if any(len(law) != width for law in laws):
        return False
    if any(sum(law, Fraction(0)) != 1 for law in laws):
        return False
    if any(value < 0 for law in laws for value in law):
        return False
    if any(value < 0 or value > 1 for value in acceptance):
        return False
    if any(value < 0 for value in (*weights, *positive)):
        return False
    if sum(weights, Fraction(0)) != 1 or len(positive) != width:
        return False

    differences = [
        tuple(p_value - q_value for p_value, q_value in zip(p_law, q_law))
        for p_law in honest
        for q_law in false
    ]
    if min(scalar(difference, acceptance) for difference in differences) < gap:
        return False
    mixture = tuple(
        sum(
            (weight * difference[index] for weight, difference in zip(weights, differences)),
            Fraction(0),
        )
        for index in range(width)
    )
    return (
        all(bound >= value for bound, value in zip(positive, mixture))
        and sum(positive, Fraction(0)) == gap
        and row["certificate_audit"]["exact"] is True
        and q(row["vertex_solver_gap"]) == gap
    )


def bsc_probability(source: int, observed: int, depth: int) -> Fraction:
    distance = (source ^ observed).bit_count()
    return Fraction(1, 5) ** distance * Fraction(4, 5) ** (depth - distance)


def check_parity_row(row: dict[str, object]) -> bool:
    depth = int(row["depth"])
    worlds = range(1 << depth)
    honest = [word for word in worlds if word.bit_count() % 2 == 0]
    false = [word for word in worlds if word.bit_count() % 2 == 1]
    gap = Fraction(3, 5) ** depth
    honest_acceptance = Fraction(1, 2) * (1 + gap)
    false_acceptance = Fraction(1, 2) * (1 - gap)
    per_even = gap / (1 << (depth - 1))

    for source in worlds:
        observed_even_probability = sum(
            (
                bsc_probability(source, observed, depth)
                for observed in worlds
                if observed.bit_count() % 2 == 0
            ),
            Fraction(0),
        )
        expected = (
            honest_acceptance
            if source.bit_count() % 2 == 0
            else false_acceptance
        )
        if observed_even_probability != expected:
            return False

    for observed in worlds:
        honest_mixture = sum(
            (bsc_probability(source, observed, depth) for source in honest),
            Fraction(0),
        ) / len(honest)
        false_mixture = sum(
            (bsc_probability(source, observed, depth) for source in false),
            Fraction(0),
        ) / len(false)
        expected_difference = (
            per_even if observed.bit_count() % 2 == 0 else -per_even
        )
        if honest_mixture - false_mixture != expected_difference:
            return False

    return (
        row["error"] == "1/5"
        and q(row["contraction"]) == Fraction(3, 5)
        and q(row["honest_acceptance"]) == honest_acceptance
        and q(row["false_acceptance"]) == false_acceptance
        and set(row["all_pair_gaps"]) == {str(gap)}
        and q(row["dual_positive_value_per_even_outcome"]) == per_even
        and q(row["dual_positive_sum"]) == gap
        and q(row["closed_form_gap"]) == gap
        and row["mixture_formula_matches"] is True
        and row["certificate_exact"] is True
    )


def check_alias_row(row: dict[str, object]) -> bool:
    aliases = int(row["alias_count_per_semantic_outcome"])
    positive_mass = aliases * Fraction(3, 5 * aliases)
    return (
        aliases >= 1
        and int(row["raw_outcome_count"]) == 2 * aliases
        and int(row["quotient_outcome_count"]) == 2
        and q(row["gap"]) == Fraction(3, 5)
        and q(row["dual_upper_bound"]) == positive_mass == Fraction(3, 5)
        and row["certificate_exact"] is True
    )


def check_special_cases(rows: Sequence[dict[str, object]]) -> tuple[bool, bool]:
    by_id = {row["case_id"]: row for row in rows}
    collision = by_id["convex_hull_collision"]
    collision_honest = [qvector(law) for law in collision["honest_laws"]]
    collision_false = qvector(collision["false_laws"][0])
    collision_midpoint = tuple(
        (left + right) / 2
        for left, right in zip(collision_honest[0], collision_honest[1])
    )

    joint = by_id["joint_correlation_signal"]
    honest_joint = qvector(joint["honest_laws"][0])
    false_joint = qvector(joint["false_laws"][0])
    marginal_indices = ((2, 3), (1, 3))
    same_marginals = all(
        sum((honest_joint[index] for index in indices), Fraction(0))
        == sum((false_joint[index] for index in indices), Fraction(0))
        == Fraction(1, 2)
        for indices in marginal_indices
    )
    disjoint_support = all(
        not (honest_value and false_value)
        for honest_value, false_value in zip(honest_joint, false_joint)
    )
    return collision_midpoint == collision_false, same_marginals and disjoint_support


def verify() -> dict[str, object]:
    result = load_result()
    explicit = result.get("explicit_cases", [])
    parity = result.get("parity_bsc_rows", [])
    aliases = result.get("alias_refinement_rows", [])
    collision_exact, joint_exact = check_special_cases(explicit)

    checks = {
        "V0_schema_status_and_boundary": (
            result.get("schema_version") == "asmp3_finite_tv_frontier_v0_8"
            and result.get("status") == "exact_finite_typed_subtheorem"
            and result.get("certified") is True
            and "does not choose the v0.1 interface quantifier"
            in result.get("claim_boundary", "")
        ),
        "V1_explicit_primal_dual_certificates": (
            len(explicit) == 3
            and all(check_explicit_certificate(row) for row in explicit)
        ),
        "V2_convex_hull_collision_reconstructed": collision_exact,
        "V3_joint_marginal_counterexample_reconstructed": joint_exact,
        "V4_parity_depth_registry_complete": (
            [row["depth"] for row in parity] == list(range(1, 9))
        ),
        "V5_parity_bsc_mixtures_reconstructed": (
            all(check_parity_row(row) for row in parity)
        ),
        "V6_alias_registry_complete": (
            [row["alias_count_per_semantic_outcome"] for row in aliases]
            == list(range(1, 9))
        ),
        "V7_alias_invariance_reconstructed": (
            all(check_alias_row(row) for row in aliases)
        ),
        "V8_producer_gates_all_true": (
            bool(result.get("gates")) and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_finite_tv_frontier_verification_v0_8",
        "checker": "clean_room_standard_library_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker verifies the finite rational certificates and "
            "parametric BSC rows. It is not an external mathematical review."
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
        raise SystemExit(f"finite TV independent verification failed: {failed}")
    print(
        "ASMP-3 finite TV independent verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
