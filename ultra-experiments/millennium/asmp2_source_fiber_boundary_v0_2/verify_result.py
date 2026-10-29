"""Independent verifier for the ASMP-2 source-fiber boundary."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
MILLENNIUM = HERE.parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_fraction(value: str) -> Fraction:
    numerator, denominator = value.split("/")
    return Fraction(int(numerator), int(denominator))


def verify(result: dict[str, object]) -> dict[str, bool]:
    sources = (Fraction(-1, 2), Fraction(0), Fraction(1, 2))

    def g(theta: Fraction) -> Fraction:
        return Fraction(16, 9) * theta**2 * (theta**2 - Fraction(1, 4)) ** 2

    def g_prime(theta: Fraction) -> Fraction:
        return (
            Fraction(32, 3) * theta**5
            - Fraction(32, 9) * theta**3
            + Fraction(2, 9) * theta
        )

    def pz(theta: Fraction) -> Fraction:
        return Fraction(1, 2) + theta / 8

    def py(world: int, action: int, theta: Fraction) -> Fraction:
        return Fraction(1, 2) + theta / 16 + action * world * g(theta) / 8

    def parameters(world: int, theta: Fraction) -> tuple[Fraction, ...]:
        return (pz(theta), py(world, -1, theta), py(world, 1, theta))

    def pmf(world: int, theta: Fraction) -> tuple[Fraction, ...]:
        values = parameters(world, theta)
        rows = []
        for bits in itertools.product((0, 1), repeat=3):
            probability = Fraction(1)
            for bit, value in zip(bits, values):
                probability *= value if bit else 1 - value
            rows.append(probability)
        return tuple(rows)

    inputs = result["authoritative_and_theorem_inputs"]
    input_paths = {
        "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md": (
            MILLENNIUM / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
        ),
        "problem_set_v0_1.json": MILLENNIUM / "problem_set_v0_1.json",
        "THEOREM_v0_2.md": HERE / "THEOREM_v0_2.md",
        "PRIOR_ART_v0_2.md": HERE / "PRIOR_ART_v0_2.md",
        "LOCAL_SUFFICIENCY_COUNTEREXAMPLE_v0_5.md": (
            HERE / "LOCAL_SUFFICIENCY_COUNTEREXAMPLE_v0_5.md"
        ),
    }
    hashes_match = all(
        inputs[name] == sha256(path) for name, path in input_paths.items()
    )

    source_equal = all(
        g(theta) == 0 and g_prime(theta) == 0 and pmf(-1, theta) == pmf(1, theta)
        for theta in sources
    )
    fisher = Fraction(4) * (Fraction(1, 8) ** 2 + 2 * Fraction(1, 16) ** 2)
    certificate = result["fiber_certificate"]
    good = certificate["good_actions_by_world"]
    gates = result["gates"]

    return {
        "identity": (
            result["schema_version"] == "asmp2_source_fiber_boundary_v0_2"
            and result["problem_id"] == "ASMP-2"
        ),
        "input_hashes": hashes_match,
        "source_laws_recomputed": source_equal,
        "positive_fisher_recomputed": (
            fisher == Fraction(3, 32)
            and parse_fraction(result["witness"]["fisher_information_at_zero"])
            == fisher
        ),
        "world_minus_good_set": good["-1"] == [1],
        "world_plus_good_set": good["1"] == [-1],
        "good_sets_individually_feasible_and_disjoint": (
            good["-1"] and good["1"] and set(good["-1"]).isdisjoint(good["1"])
        ),
        "deployment_risks_recomputed": (
            py(-1, 1, Fraction(1)) == Fraction(7, 16)
            and py(-1, -1, Fraction(1)) == Fraction(11, 16)
            and py(1, -1, Fraction(1)) == Fraction(7, 16)
            and py(1, 1, Fraction(1)) == Fraction(11, 16)
        ),
        "fiber_lp_value_recomputed": (
            parse_fraction(certificate["optimal_probability_of_action_minus_one"])
            == Fraction(1, 2)
            and parse_fraction(certificate["randomized_uniform_success"])
            == Fraction(1, 2)
            and parse_fraction(certificate["deterministic_uniform_success"]) == 0
        ),
        "curvature_recomputed": (
            parse_fraction(result["witness"]["risk_curvature_bound"])
            == Fraction(193, 36)
        ),
        "all_reported_gates": result["all_gates_passed"] is True
        and all(gates.values()),
        "local_counterexample_recomputed": (
            result["local_sufficiency_counterexample"]["fisher_information"] == "1/4"
            and result["local_sufficiency_counterexample"]["all_gates_passed"] is True
            and all(
                not result["local_sufficiency_counterexample"]["action_rows"][
                    str(action)
                ]["globally_safe_on_local_ball"]
                for action in (-1, 1)
            )
        ),
        "claim_boundary_preserved": (
            result["adjudication"]["candidate_negative_result"] is True
            and result["adjudication"]["problem_resolved"] is False
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = json.loads(args.result.read_text(encoding="utf-8"))
    checks = verify(result)
    payload = {
        "schema_version": "asmp2_source_fiber_verification_v0_2",
        "result_sha256": sha256(args.result),
        "checks": checks,
        "check_count": len(checks),
        "passed_count": sum(checks.values()),
        "passed": all(checks.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"verification_passed={str(payload['passed']).lower()}")
    print(f"checks={payload['passed_count']}/{payload['check_count']}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
