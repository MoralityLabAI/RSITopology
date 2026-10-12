from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

try:
    from .asmp9_native_fixture import native_laws_and_answers
    from .decision_information import (
        characteristic_design,
        fixed_confidence_lower_bound,
    )
    from .finite_upper_bound import (
        conservative_start,
        decimal_text,
        fraction_digest,
        optimize_midpoint_grid,
    )
except ImportError:
    from asmp9_native_fixture import (  # type: ignore[no-redef]
        native_laws_and_answers,
    )
    from decision_information import (  # type: ignore[no-redef]
        characteristic_design,
        fixed_confidence_lower_bound,
    )
    from finite_upper_bound import (  # type: ignore[no-redef]
        conservative_start,
        decimal_text,
        fraction_digest,
        optimize_midpoint_grid,
    )


def error_record(value: Fraction, delta: Fraction) -> dict[str, object]:
    return {
        "decimal": decimal_text(value),
        "exact_fraction_sha256": fraction_digest(value),
        "numerator_digits": len(str(value.numerator)),
        "denominator_digits": len(str(value.denominator)),
        "strictly_below_delta": value < delta,
    }


def build_report() -> dict[str, object]:
    delta = Fraction(1, 20)
    laws, answers, sources = native_laws_and_answers()
    information_design = characteristic_design(laws, answers, "base")
    lower_bound = fixed_confidence_lower_bound(
        information_design,
        float(delta),
    )
    conservative = conservative_start(delta)
    fixed = optimize_midpoint_grid(delta)
    return {
        "claim_status": "development_only_unregistered",
        "source_hashes": sources.source_hashes,
        "registry": {
            "answers": answers,
            "delta": "1/20",
            "independent_channel_samples": True,
            "known_channel_laws": True,
        },
        "decision_rule": [
            "if mixture successes >= mixture threshold: not_certified",
            "else if return or mechanics successes >= its threshold: policy_0",
            "else: policy_1",
        ],
        "midpoint_aligned_grid": {
            "return_and_mechanics_sample_multiple": 2,
            "mixture_sample_multiple": 68,
            "thresholds_frozen_at_exact_probability_midpoints": True,
            "threshold_optimization_permitted": False,
        },
        "conservative_delta_over_three_start": {
            "return_samples": conservative.return_channel.samples,
            "mechanics_samples": conservative.mechanics.samples,
            "mixture_samples": conservative.mixture.samples,
            "total_queries": conservative.total_queries,
        },
        "constructive_upper_certificate": {
            "return_samples": fixed.return_channel.samples,
            "return_threshold": fixed.return_channel.threshold,
            "mechanics_samples": fixed.mechanics.samples,
            "mechanics_threshold": fixed.mechanics.threshold,
            "mixture_samples": fixed.mixture.samples,
            "mixture_threshold": fixed.mixture.threshold,
            "total_queries": fixed.total_queries,
            "errors": {
                "base": error_record(fixed.errors.base, delta),
                "gauge_alias": error_record(
                    fixed.errors.gauge_alias,
                    delta,
                ),
                "mechanics_flip": error_record(
                    fixed.errors.mechanics_flip,
                    delta,
                ),
                "mixture_invalid": error_record(
                    fixed.errors.mixture_invalid,
                    delta,
                ),
                "reward_flip": error_record(
                    fixed.errors.reward_flip,
                    delta,
                ),
            },
            "uniform_delta_correct_on_registered_registry": (
                fixed.errors.worst < delta
            ),
            "grid_minimal_by_exhaustive_exact_search": True,
        },
        "lower_upper_comparison_at_base": {
            "change_of_measure_expected_query_lower_bound": lower_bound,
            "fixed_query_constructive_upper_bound": fixed.total_queries,
            "upper_to_lower_ratio": fixed.total_queries / lower_bound,
            "comparison_scope": (
                "equal unit query costs; lower bound is expected queries "
                "at base; upper procedure has a fixed query count"
            ),
        },
        "claim_boundary": {
            "globally_minimal_fixed_design_proved": False,
            "adaptive_upper_bound_proved": False,
            "unknown_or_misspecified_laws_supported": False,
            "registered_or_claim_eligible": False,
            "resolves_asmp9": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the exact finite-sample v0.33 upper certificate."
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    encoded = json.dumps(build_report(), indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        output = args.output.resolve()
        if output.exists():
            raise FileExistsError(f"refusing to overwrite {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8", newline="\n")
        print(f"wrote {output}")
        print(f"sha256 {hashlib.sha256(output.read_bytes()).hexdigest()}")
    print(encoded, end="")


if __name__ == "__main__":
    main()
