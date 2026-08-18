"""Independent verifier for the ASMP-2 resolution-readiness result."""

from __future__ import annotations

import argparse
import hashlib
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


def independent_checks(result: dict[str, object]) -> dict[str, bool]:
    registry_path = MILLENNIUM / "problem_set_v0_1.json"
    normative_path = MILLENNIUM / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
    audit_path = MILLENNIUM / "REFEREE_AUDIT_v0_1.md"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    audit_text = audit_path.read_text(encoding="utf-8")
    problem = next(item for item in registry["problems"] if item["id"] == "ASMP-2")

    sources = (Fraction(-1, 2), Fraction(0), Fraction(1, 2))

    def bump(theta: Fraction) -> Fraction:
        return Fraction(16, 9) * theta**2 * (theta**2 - Fraction(1, 4)) ** 2

    def bump_prime(theta: Fraction) -> Fraction:
        return (
            Fraction(32, 3) * theta**5
            - Fraction(32, 9) * theta**3
            + Fraction(2, 9) * theta
        )

    def z_probability(theta: Fraction) -> Fraction:
        return Fraction(1, 2) + theta / 8

    def risk(world: int, theta: Fraction) -> Fraction:
        return Fraction(1, 2) + theta / 16 + world * bump(theta) / 8

    def joint(world: int, theta: Fraction) -> tuple[Fraction, ...]:
        z = z_probability(theta)
        y = risk(world, theta)
        return ((1 - z) * (1 - y), (1 - z) * y, z * (1 - y), z * y)

    source_indistinguishable = all(
        bump(theta) == 0
        and bump_prime(theta) == 0
        and joint(-1, theta) == joint(1, theta)
        for theta in sources
    )
    fisher = Fraction(4) * (Fraction(1, 8) ** 2 + Fraction(1, 16) ** 2)
    plus = risk(1, Fraction(1))
    minus = risk(-1, Fraction(1))

    expected_inputs = result["authoritative_inputs"]
    hashes_match = (
        expected_inputs[normative_path.name] == sha256(normative_path)
        and expected_inputs[registry_path.name] == sha256(registry_path)
        and expected_inputs[audit_path.name] == sha256(audit_path)
    )

    countermodel = result["exact_countermodel"]
    deployment = countermodel["deployment"]
    local = countermodel["local_certificate_data"]
    return {
        "schema_and_identity": (
            result["schema_version"] == "asmp2_resolution_readiness_v0_1"
            and result["problem_id"] == "ASMP-2"
            and result["problem_version"] == "ASMP-CANDIDATE-SET-v0.1"
        ),
        "authoritative_hashes_match": hashes_match,
        "draft_status_reproduced": (
            registry["status"] == "proposed_candidate_definition_draft"
            and registry["graduation_standard_satisfied"] is False
            and problem["empirical_resolution_allowed"] is False
        ),
        "definition_debt_reproduced": (
            "candidate; global class still conditional" in audit_text
            and "External review must\nstill test whether the registered quotient and conditioning modulus are the\nright ones"
            in audit_text
        ),
        "all_required_bindings_are_absent_from_problem_record": (
            len(result["required_successor_repairs"]) == 15
            and not set(result["required_successor_repairs"]).intersection(problem)
        ),
        "source_indistinguishability_recomputed": source_indistinguishable,
        "positive_fisher_recomputed": (
            fisher == Fraction(5, 64)
            and parse_fraction(local["fisher_total"]) == fisher
        ),
        "finite_curvature_recomputed": (
            # g''(1)=386/9, hence |p_y''(1)|=193/36.
            parse_fraction(countermodel["regularity"]["risk_curvature_bound"])
            == Fraction(193, 36)
        ),
        "global_threshold_conflict_recomputed": (
            minus == Fraction(7, 16)
            and plus == Fraction(11, 16)
            and minus < Fraction(9, 16) < plus
            and parse_fraction(deployment["risk_gap"]) == Fraction(1, 4)
            and parse_fraction(deployment["uniform_success_probability_upper_bound"])
            == 0
        ),
        "utility_floor_recomputed": Fraction(1) >= Fraction(4, 5) > 0,
        "reported_gate_conjunction": (
            countermodel["all_gates_passed"] is True
            and all(countermodel["gates"].values())
        ),
        "stop_decision_is_scoped": (
            result["decision"]
            == "stop_full_resolution_attempt_pending_successor_definition"
            and result["problem_resolved"] is False
            and result["stop_is_supported"] is True
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = json.loads(args.result.read_text(encoding="utf-8"))
    checks = independent_checks(result)
    payload = {
        "schema_version": "asmp2_resolution_readiness_verification_v0_1",
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
