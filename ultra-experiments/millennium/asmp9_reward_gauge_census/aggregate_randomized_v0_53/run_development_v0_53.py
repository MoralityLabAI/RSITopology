"""Run the non-claim-eligible ASMP-9 v0.53 development census."""

from __future__ import annotations

from fractions import Fraction as Q
import json
from pathlib import Path
import time

from aggregate_randomized import (
    exact_deterministic_optimum,
    exact_randomized_optimum,
    one_outcome_strict_gain,
    subset_bound_table,
    two_experiment_witness,
)


HERE = Path(__file__).resolve().parent


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def main() -> None:
    started = time.perf_counter()
    alpha = Q(1, 2)
    risks = (Q(1),)
    reports = (Q(0), Q(1))
    weights = (Q(1, 2), Q(1, 2))
    rows = []
    formula_mismatches = 0
    table_mismatches = 0
    dual_mismatches = 0
    support_failures = 0
    expected_table = (Q(0), Q(1), Q(0), Q(1))

    for numerator in range(11, 21):
        p = Q(numerator, 20)
        law = (p, 1 - p)
        table = subset_bound_table(risks, (law,), alpha)
        deterministic = exact_deterministic_optimum(
            risks, (law,), reports, alpha, weights
        )
        randomized = exact_randomized_optimum(
            risks, (law,), reports, alpha, weights
        )
        formula = Q(1, 4) / p
        dual_lambda = weights[0] / p
        dual_value = dual_lambda * (1 - alpha)
        table_mismatches += table != expected_table
        formula_mismatches += randomized.value != formula
        dual_mismatches += dual_value != randomized.value
        support_failures += randomized.maximum_positive_support > 3
        rows.append(
            {
                "p": qstr(p),
                "subset_table": [qstr(value) for value in table],
                "deterministic_value": qstr(deterministic[0]),
                "randomized_value": qstr(randomized.value),
                "formula_value": qstr(formula),
                "dual_lambda": qstr(dual_lambda),
                "feasible_vertex_count": (
                    randomized.feasible_vertex_count
                ),
                "maximum_positive_support": (
                    randomized.maximum_positive_support
                ),
            }
        )

    witness = two_experiment_witness()
    control = one_outcome_strict_gain()
    output = {
        "schema": "asmp9-v0.53-development-census-v1",
        "claim_eligible": False,
        "family": rows,
        "family_size": len(rows),
        "common_subset_table": [
            qstr(value) for value in expected_table
        ],
        "distinct_randomized_values": len(
            {row["randomized_value"] for row in rows}
        ),
        "table_mismatch_count": table_mismatches,
        "formula_mismatch_count": formula_mismatches,
        "dual_mismatch_count": dual_mismatches,
        "support_bound_failure_count": support_failures,
        "headline_witness": {
            "first_value": qstr(
                witness["experiments"][0]["randomized_value"]
            ),
            "second_value": qstr(
                witness["experiments"][1]["randomized_value"]
            ),
        },
        "one_outcome_control": {
            "deterministic_value": qstr(
                control["deterministic_value"]
            ),
            "randomized_value": qstr(control["randomized_value"]),
        },
        "elapsed_seconds_descriptive": time.perf_counter() - started,
    }
    path = HERE / "DEVELOPMENT_CENSUS_v0_53.json"
    path.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
