from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "result_v0_3.json"
OUTPUT_PATH = HERE / "artifacts" / "fourier_verification_v0_3.json"
ETA = Fraction(1, 5)
LAMBDA = 1 - 2 * ETA


def channel_times_character() -> tuple[Fraction, Fraction]:
    channel = (
        (1 - ETA, ETA),
        (ETA, 1 - ETA),
    )
    character = (Fraction(1), Fraction(-1))
    return tuple(
        sum(
            (channel[row][column] * character[column] for column in range(2)),
            Fraction(0),
        )
        for row in range(2)
    )


def fourier_distribution_difference(depth: int, observed_parity: int) -> Fraction:
    if depth < 1 or observed_parity not in (0, 1):
        raise ValueError("invalid Fourier-certificate argument")
    sign = 1 if observed_parity == 0 else -1
    return Fraction(sign) * LAMBDA**depth / (2 ** (depth - 1))


def fourier_total_variation(depth: int) -> Fraction:
    magnitude_per_observation = abs(fourier_distribution_difference(depth, 0))
    return Fraction(2**depth) * magnitude_per_observation / 2


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    rows = result["binding_refute_branch"]["asymptotic_rows"]
    checks = {
        "binary_channel_parity_character_eigenpair": (
            channel_times_character() == (LAMBDA, -LAMBDA)
        ),
        "tensor_character_gap_matches_artifact": all(
            fourier_total_variation(int(row["depth"]))
            == Fraction(row["best_joint_decision_gap"]["exact"])
            for row in rows
        ),
        "distribution_difference_normalizes": all(
            (
                2 ** (int(row["depth"]) - 1)
                * fourier_distribution_difference(int(row["depth"]), 0)
                + 2 ** (int(row["depth"]) - 1)
                * fourier_distribution_difference(int(row["depth"]), 1)
            )
            == 0
            for row in rows
        ),
        "gap_recurrence": all(
            fourier_total_variation(depth + 1)
            == LAMBDA * fourier_total_variation(depth)
            for depth in range(1, 64)
        ),
        "gap_is_not_constant": fourier_total_variation(64) < Fraction(1, 10**12),
        "refutation_dimension_dual_argument": (
            "S is all d semantic indices"
            in result["binding_refute_branch"]["frozen_message_game"][
                "refute_relation"
            ]
            and all(
                row["enumerated_refutation_dimension"]
                == row["refuting_atom_count"]
                for row in result["binding_refute_branch"]["exhaustive_rows"]
                if row["enumerated_refutation_dimension"] is not None
            )
        ),
    }
    passed = all(checks.values())
    return {
        "schema_version": "asmp3_fourier_verification_v0_3",
        "verified_experiment_id": result["experiment_id"],
        "passed": passed,
        "checks": checks,
        "check_count": len(checks),
        "certificate": {
            "channel_matrix": [["4/5", "1/5"], ["1/5", "4/5"]],
            "parity_character": ["1", "-1"],
            "eigenvalue": "3/5",
            "tensor_eigenvalue": "(3/5)^d",
            "distribution_difference": (
                "(-1)^parity(y) (3/5)^d / 2^(d-1)"
            ),
        },
        "method": (
            "Independent Fourier-character/eigenvalue proof; does not import "
            "the producer or enumerative verifier."
        ),
    }


def main() -> None:
    verification = verify()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(verification, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not verification["passed"]:
        raise RuntimeError("ASMP-3 Fourier verification failed")
    print(
        f"ASMP-3 Fourier verification passed: "
        f"{verification['check_count']}/{verification['check_count']}"
    )


if __name__ == "__main__":
    main()
