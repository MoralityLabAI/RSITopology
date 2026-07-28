from __future__ import annotations

from fractions import Fraction
from typing import Any

from conditional_fiber import conditional_weights, enumerate_fibers, incidence_rows
from experiment import _closed_cycle_weights, parse_fraction
from streaming_exact_v0_13_1 import exact_randomized_upper_test_streaming


def run_power_calibration_streaming(spec: dict[str, Any]) -> dict[str, Any]:
    alpha = parse_fraction(spec["alpha"])
    lower = parse_fraction(spec["lower_power"])
    upper = parse_fraction(spec["upper_power"])
    formula_trials = int(spec["formula_trials_per_edge"])
    records: list[dict[str, Any]] = []
    formula_mismatch_count = 0
    likelihood_ratio_mismatch_count = 0
    size_mismatch_count = 0
    nonpositive_power_gain_count = 0
    power_band_mismatch_count = 0

    for cell in spec["cells"]:
        k = int(cell["cycle_length"])
        ratio = parse_fraction(cell["odds_ratio"])
        n = int(cell["trials_per_edge"])
        edges = [(index, (index + 1) % k) for index in range(k)]
        rows = incidence_rows(k, edges)
        zero_fiber = enumerate_fibers([formula_trials] * k, rows)[
            (0,) * k
        ]
        generic_null = conditional_weights(
            zero_fiber, [formula_trials] * k, (Fraction(1),) * k
        )
        generic_alt = conditional_weights(
            zero_fiber,
            [formula_trials] * k,
            (ratio,) + (Fraction(1),) * (k - 1),
        )
        closed_null = _closed_cycle_weights(
            k, formula_trials, Fraction(1)
        )
        closed_alt = _closed_cycle_weights(k, formula_trials, ratio)
        formula_mismatch_count += int(
            generic_null != closed_null or generic_alt != closed_alt
        )

        likelihood_ratios = [
            generic_alt[(z,) * k] / generic_null[(z,) * k]
            for z in range(formula_trials + 1)
        ]
        likelihood_ratio_mismatch_count += sum(
            likelihood_ratios[z + 1] / likelihood_ratios[z] != ratio
            for z in range(formula_trials)
        )

        exact = exact_randomized_upper_test_streaming(k, n, ratio, alpha)
        certificate = exact.certificate(
            alpha=alpha,
            lower_power=lower,
            upper_power=upper,
        )
        size_mismatch_count += int(
            not certificate["exact_size"]["construction_verified"]
        )
        nonpositive_power_gain_count += int(
            not certificate["power_above_size"]
        )
        power_band_mismatch_count += int(
            not certificate["power_in_registered_band"]
        )
        records.append(
            {
                **cell,
                **certificate,
                "formula_exact": generic_alt == closed_alt,
                "likelihood_ratio_exact": all(
                    likelihood_ratios[z + 1] / likelihood_ratios[z]
                    == ratio
                    for z in range(formula_trials)
                ),
                "scope": "conditional_on_zero_vertex_balance",
            }
        )

    return {
        "records": records,
        "cell_count": len(records),
        "alpha": spec["alpha"],
        "power_band": [spec["lower_power"], spec["upper_power"]],
        "formula_mismatch_count": formula_mismatch_count,
        "likelihood_ratio_mismatch_count": (
            likelihood_ratio_mismatch_count
        ),
        "size_mismatch_count": size_mismatch_count,
        "nonpositive_power_gain_count": nonpositive_power_gain_count,
        "power_band_mismatch_count": power_band_mismatch_count,
        "nonmonotonicity_warning": (
            "Exact-size conditional power need not increase between "
            "adjacent per-edge sample counts; registered n values are "
            "calibration points, not critical thresholds."
        ),
        "exact_representation": (
            "streamed_unreduced_integer_ratios_with_cross_multiplication"
        ),
    }
