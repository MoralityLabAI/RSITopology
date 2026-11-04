from __future__ import annotations

import hashlib
import json
from pathlib import Path

from path_factorization_test import (
    analyze_geometry,
    canonical_fixture,
    chi_square_test_design,
    df1_power_high_precision,
    exact_distance_squared,
    minimum_equal_repeats,
)


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "DEVELOPMENT_VERIFICATION_v0_72.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    design, mean = canonical_fixture()
    complete = analyze_geometry(design)
    reduced = analyze_geometry(design[:3, :])
    distance_squared = exact_distance_squared(design, mean)
    sample_gate = minimum_equal_repeats(
        distance_squared=float(distance_squared),
        sample_variance=1.0,
        degrees_of_freedom=complete.residual_degrees_of_freedom,
        alpha=0.05,
        target_power=0.80,
    )
    frozen_power = chi_square_test_design(
        complete.residual_degrees_of_freedom,
        0.05,
        float(sample_gate["noncentrality"]),
    )
    high_precision = {
        "digits": 80,
        "power_at_31": df1_power_high_precision(
            alpha="0.05", noncentrality_value="7.75"
        ),
        "power_at_32": df1_power_high_precision(
            alpha="0.05", noncentrality_value="8"
        ),
    }

    payload = {
        "status": "development_only_not_preregistered",
        "complete_geometry": complete.to_jsonable(),
        "one_path_deleted_geometry": reduced.to_jsonable(),
        "interaction_mean": [str(value) for value in mean],
        "exact_distance_squared": str(distance_squared),
        "sample_variance": 1.0,
        "alpha": 0.05,
        "target_power": 0.80,
        "sample_gate": sample_gate,
        "frozen_power": frozen_power,
        "high_precision_df1_audit": high_precision,
        "checks": {
            "complete_design_identifies_reward": (
                complete.reward_coordinates_identified
            ),
            "complete_design_can_falsify_factorization": (
                complete.factorization_test_available
            ),
            "one_path_deleted_still_identifies_reward": (
                reduced.reward_coordinates_identified
            ),
            "one_path_deleted_cannot_falsify_factorization": (
                not reduced.factorization_test_available
            ),
            "primitive_contrast_is_registered_relation": (
                complete.primitive_contrasts == ((1, -1, -1, 1),)
            ),
            "distance_squared_is_one_quarter": str(distance_squared) == "1/4",
            "minimum_repeats_is_32": (
                sample_gate["minimum_repeats_per_path"] == 32
            ),
            "31_repeats_fail_power": sample_gate["previous_power"] < 0.80,
            "32_repeats_pass_power": sample_gate["power"] >= 0.80,
            "high_precision_boundary_agrees": (
                float(high_precision["power_at_31"]) < 0.80
                and float(high_precision["power_at_32"]) > 0.80
            ),
        },
        "claim_boundary": (
            "Classical known-variance Gaussian lack-of-fit specialization on "
            "one complete finite path table. No unknown-variance, missing-data, "
            "adaptive, strategic, physical-value, or ASMP-9 resolution claim."
        ),
        "source_hashes": {
            name: sha256(ROOT / name)
            for name in (
                "path_factorization_test.py",
                "test_path_factorization_test.py",
                "THEOREM_DRAFT_v0_72.md",
                "PRIOR_ART_GATE_v0_72.md",
            )
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload["checks"], sort_keys=True))


if __name__ == "__main__":
    main()
