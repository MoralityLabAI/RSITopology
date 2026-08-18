from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "polyhedral_tv_frontier_v0_9.json"
OUTPUT_PATH = (
    HERE / "artifacts" / "polyhedral_tv_frontier_verification_v0_9.json"
)


def q(value: str | int) -> Fraction:
    return Fraction(value)


def vector(values: Sequence[str | int]) -> tuple[Fraction, ...]:
    return tuple(q(value) for value in values)


def scalar(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return sum((x * y for x, y in zip(left, right)), Fraction(0))


def parse_polytope(value: dict[str, object]) -> dict[str, object]:
    dimension = int(value["dimension"])
    polytope = {
        "dimension": dimension,
        "A": tuple(vector(row) for row in value["A"]),
        "b": vector(value["b"]),
        "E": tuple(vector(row) for row in value["E"]),
        "e": vector(value["e"]),
    }
    if len(polytope["A"]) != len(polytope["b"]):
        raise ValueError("inequality shape mismatch")
    if len(polytope["E"]) != len(polytope["e"]):
        raise ValueError("equality shape mismatch")
    if any(
        len(row) != dimension for row in (*polytope["A"], *polytope["E"])
    ):
        raise ValueError("constraint dimension mismatch")
    return polytope


def contains(polytope: dict[str, object], point: Sequence[Fraction]) -> bool:
    return (
        len(point) == polytope["dimension"]
        and all(
            scalar(row, point) <= bound
            for row, bound in zip(polytope["A"], polytope["b"])
        )
        and all(
            scalar(row, point) == target
            for row, target in zip(polytope["E"], polytope["e"])
        )
    )


def check_dual(
    polytope: dict[str, object],
    coefficients: Sequence[Fraction],
    y: Sequence[Fraction],
    z: Sequence[Fraction],
    bound: Fraction,
) -> bool:
    if len(y) != len(polytope["A"]) or len(z) != len(polytope["E"]):
        return False
    if any(value < 0 for value in y):
        return False
    reconstructed = tuple(
        sum(
            (weight * row[column] for weight, row in zip(y, polytope["A"])),
            Fraction(0),
        )
        + sum(
            (weight * row[column] for weight, row in zip(z, polytope["E"])),
            Fraction(0),
        )
        for column in range(polytope["dimension"])
    )
    objective = scalar(y, polytope["b"]) + scalar(z, polytope["e"])
    return reconstructed == tuple(coefficients) and objective <= bound


def tv(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return sum((abs(x - y) for x, y in zip(left, right)), Fraction(0)) / 2


def check_row(row: dict[str, object]) -> bool:
    honest = parse_polytope(row["honest_polytope"])
    false = parse_polytope(row["false_polytope"])
    certificate = row["certificate"]
    acceptance = vector(certificate["acceptance"])
    honest_lower = q(certificate["honest_lower"])
    false_upper = q(certificate["false_upper"])
    gap = q(certificate["claimed_gap"])
    closest_honest = vector(certificate["closest_honest"])
    closest_false = vector(certificate["closest_false"])
    if (
        honest["dimension"] != false["dimension"]
        or honest["dimension"] != len(acceptance)
    ):
        return False
    if any(value < 0 or value > 1 for value in acceptance):
        return False

    honest_dual = check_dual(
        honest,
        tuple(-value for value in acceptance),
        vector(certificate["honest_dual_y"]),
        vector(certificate["honest_dual_z"]),
        -honest_lower,
    )
    false_dual = check_dual(
        false,
        acceptance,
        vector(certificate["false_dual_y"]),
        vector(certificate["false_dual_z"]),
        false_upper,
    )
    return (
        honest_dual
        and false_dual
        and contains(honest, closest_honest)
        and contains(false, closest_false)
        and honest_lower - false_upper == gap
        and tv(closest_honest, closest_false) == gap
        and row["audit"]["exact"] is True
    )


def check_joint_marginal_witness(row: dict[str, object]) -> bool:
    honest = parse_polytope(row["honest_polytope"])
    false = parse_polytope(row["false_polytope"])
    witness = row["equal_marginal_witness"]
    honest_law = vector(witness["honest"])
    false_law = vector(witness["false"])
    marginal_indices = ((2, 3), (1, 3))
    return (
        contains(honest, honest_law)
        and contains(false, false_law)
        and all(
            sum((honest_law[index] for index in indices), Fraction(0))
            == sum((false_law[index] for index in indices), Fraction(0))
            == Fraction(1, 2)
            for indices in marginal_indices
        )
    )


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    rows = result.get("case_rows", [])
    by_id = {row["case_id"]: row for row in rows}
    checks = {
        "V0_schema_parent_status_and_boundary": (
            result.get("schema_version") == "asmp3_polyhedral_tv_frontier_v0_9"
            and result.get("status") == "exact_rational_polyhedral_subtheorem"
            and result.get("parent_result") == "ASMP-3-FINITE-TV-FRONTIER-v0.8"
            and result.get("certified") is True
            and "does not prove that arbitrary interactive"
            in result.get("claim_boundary", "")
        ),
        "V1_case_registry_exact": (
            set(by_id)
            == {
                "interval_noise_bands",
                "polyhedral_hull_collision",
                "joint_event_robust_bands",
            }
        ),
        "V2_all_farkas_and_tv_certificates_reconstructed": (
            len(rows) == 3 and all(check_row(row) for row in rows)
        ),
        "V3_interval_gap_exact": (
            q(by_id["interval_noise_bands"]["certificate"]["claimed_gap"])
            == Fraction(3, 5)
        ),
        "V4_collision_gap_zero": (
            q(by_id["polyhedral_hull_collision"]["certificate"]["claimed_gap"])
            == 0
        ),
        "V5_joint_event_gap_exact": (
            q(by_id["joint_event_robust_bands"]["certificate"]["claimed_gap"])
            == Fraction(3, 5)
        ),
        "V6_joint_equal_marginal_witness_feasible": check_joint_marginal_witness(
            by_id["joint_event_robust_bands"]
        ),
        "V7_all_producer_gates_pass": (
            bool(result.get("gates")) and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_polyhedral_tv_frontier_verification_v0_9",
        "checker": "clean_room_farkas_and_tv_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker validates the exact rational certificates; it is "
            "not an external review of the polyhedral theorem's scope."
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
        raise SystemExit(f"polyhedral TV verification failed: {failed}")
    print(
        "ASMP-3 polyhedral TV independent verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
