from __future__ import annotations

import hashlib
from collections import Counter
from fractions import Fraction
from math import comb
from typing import Any, Sequence

from conditional_fiber import (
    conditional_weights,
    enumerate_fibers,
    exact_randomized_upper_test,
    fiber_affine_rank,
    flat_null_state_mass,
    gauge_transform_odds,
    graph_cycle_rank,
    incidence_rows,
)


def parse_fraction(text: str) -> Fraction:
    numerator, denominator = text.split("/")
    return Fraction(int(numerator), int(denominator))


def _integer_bytes(value: int) -> bytes:
    magnitude = abs(value)
    payload = magnitude.to_bytes(
        max(1, (magnitude.bit_length() + 7) // 8), "big"
    )
    return (b"-" if value < 0 else b"+") + payload


def fraction_certificate(value: Fraction) -> dict[str, object]:
    numerator = value.numerator
    denominator = value.denominator
    result: dict[str, object] = {
        "decimal": float(value),
        "numerator_bit_length": abs(numerator).bit_length(),
        "denominator_bit_length": denominator.bit_length(),
        "numerator_sha256": hashlib.sha256(
            _integer_bytes(numerator)
        ).hexdigest(),
        "denominator_sha256": hashlib.sha256(
            _integer_bytes(denominator)
        ).hexdigest(),
    }
    if max(abs(numerator).bit_length(), denominator.bit_length()) <= 512:
        result["fraction"] = f"{numerator}/{denominator}"
    return result


def _gauge_factor(
    counts: Sequence[int],
    edges: Sequence[tuple[int, int]],
    scales: Sequence[Fraction],
) -> Fraction:
    value = Fraction(1, 1)
    for exponent, (source, target) in zip(counts, edges, strict=True):
        value *= (scales[target] / scales[source]) ** exponent
    return value


def run_fresh_liveness(specs: Sequence[dict[str, Any]]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    graph_arithmetic_mismatch_count = 0
    mass_mismatch_count = 0
    gauge_factor_mismatch_count = 0
    normalized_law_mismatch_count = 0
    rank_upper_mismatch_count = 0
    missing_full_rank_graph_count = 0
    missing_deficient_graph_count = 0
    zero_full_mass_graph_count = 0
    zero_deficient_mass_graph_count = 0

    for graph_spec in specs:
        node_count = int(graph_spec["node_count"])
        edges = [tuple(edge) for edge in graph_spec["edges"]]
        rows = incidence_rows(node_count, edges)
        beta1 = graph_cycle_rank(node_count, edges)
        expected_beta1 = int(graph_spec["expected_beta1"])
        graph_arithmetic_mismatch_count += int(beta1 != expected_beta1)
        graph_has_full = False
        graph_has_deficient = False
        graph_full_mass_positive = False
        graph_deficient_mass_positive = False

        for n in graph_spec["trials_per_edge"]:
            trials = [int(n)] * len(edges)
            fibers = enumerate_fibers(trials, rows)
            mass = flat_null_state_mass(fibers, trials)
            mass_mismatch_count += int(
                sum(mass.values(), Fraction(0, 1)) != 1
            )
            rank_counts: Counter[int] = Counter()
            for fiber in fibers.values():
                rank = fiber_affine_rank(fiber)
                rank_counts[rank] += 1
                rank_upper_mismatch_count += int(rank > beta1)
                graph_has_full |= rank == beta1
                graph_has_deficient |= rank < beta1

                scales = tuple(
                    Fraction(value)
                    for value in (2, 3, 5, 7, 11, 13, 17)[:node_count]
                )
                factors = {
                    _gauge_factor(counts, edges, scales)
                    for counts in fiber
                }
                gauge_factor_mismatch_count += int(len(factors) != 1)

            full_mass = mass.get(beta1, Fraction(0, 1))
            deficient_mass = 1 - full_mass
            graph_full_mass_positive |= full_mass > 0
            graph_deficient_mass_positive |= deficient_mass > 0

            selected = next(
                (fiber for fiber in fibers.values() if len(fiber) > 1),
                None,
            )
            if selected is not None:
                odds = tuple(
                    Fraction(index + 2, index + 1)
                    for index in range(len(edges))
                )
                transformed = gauge_transform_odds(
                    odds, edges, scales
                )
                normalized_law_mismatch_count += int(
                    conditional_weights(selected, trials, odds)
                    != conditional_weights(selected, trials, transformed)
                )

            records.append(
                {
                    "graph": graph_spec["name"],
                    "node_count": node_count,
                    "edge_count": len(edges),
                    "beta1": beta1,
                    "trials_per_edge": int(n),
                    "fiber_count": len(fibers),
                    "fiber_rank_counts": dict(sorted(rank_counts.items())),
                    "flat_null_rank_mass": {
                        str(rank): fraction_certificate(value)
                        for rank, value in mass.items()
                    },
                    "full_quotient_mass": fraction_certificate(full_mass),
                    "deficient_mass": fraction_certificate(deficient_mass),
                }
            )

        missing_full_rank_graph_count += int(not graph_has_full)
        missing_deficient_graph_count += int(not graph_has_deficient)
        zero_full_mass_graph_count += int(not graph_full_mass_positive)
        zero_deficient_mass_graph_count += int(
            not graph_deficient_mass_positive
        )

    return {
        "records": records,
        "graph_count": len(specs),
        "cell_count": len(records),
        "graph_arithmetic_mismatch_count": (
            graph_arithmetic_mismatch_count
        ),
        "mass_mismatch_count": mass_mismatch_count,
        "gauge_factor_mismatch_count": gauge_factor_mismatch_count,
        "normalized_law_mismatch_count": normalized_law_mismatch_count,
        "rank_upper_mismatch_count": rank_upper_mismatch_count,
        "missing_full_rank_graph_count": missing_full_rank_graph_count,
        "missing_deficient_graph_count": missing_deficient_graph_count,
        "zero_full_mass_graph_count": zero_full_mass_graph_count,
        "zero_deficient_mass_graph_count": zero_deficient_mass_graph_count,
    }


def _closed_cycle_weights(
    cycle_length: int, trials: int, ratio: Fraction
) -> dict[tuple[int, ...], Fraction]:
    raw = {
        (z,) * cycle_length: Fraction(comb(trials, z) ** cycle_length)
        * ratio**z
        for z in range(trials + 1)
    }
    total = sum(raw.values(), Fraction(0, 1))
    return {counts: value / total for counts, value in raw.items()}


def run_power_calibration(spec: dict[str, Any]) -> dict[str, Any]:
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

        exact = exact_randomized_upper_test(k, n, ratio, alpha)
        size_mismatch_count += int(exact["size"] != alpha)
        nonpositive_power_gain_count += int(exact["power"] <= alpha)
        power_band_mismatch_count += int(
            not lower <= exact["power"] <= upper
        )
        records.append(
            {
                **cell,
                "exact_size": fraction_certificate(exact["size"]),
                "exact_power": fraction_certificate(exact["power"]),
                "randomization": fraction_certificate(
                    exact["randomization"]
                ),
                "boundary": exact["boundary"],
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
    }
