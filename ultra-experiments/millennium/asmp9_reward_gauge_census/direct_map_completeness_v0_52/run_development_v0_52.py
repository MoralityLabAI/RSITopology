"""Run the non-claim-eligible ASMP-9 v0.52 development census."""

from __future__ import annotations

from fractions import Fraction as Q
import json
from pathlib import Path
import time

from direct_map_completeness import (
    all_direct_maps,
    compare_global_optima,
    consistent_orders,
    direct_map_valid,
    dominance_certificate,
    minimal_controls,
    monotone_tables,
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
    levels = (Q(0), Q(1), Q(2))
    weights = (
        (Q(1, 3), Q(1, 3), Q(1, 3)),
        (Q(1, 2), Q(1, 3), Q(1, 6)),
        (Q(1, 6), Q(1, 3), Q(1, 2)),
        (Q(1, 6), Q(1, 2), Q(1, 3)),
    )
    tables = monotone_tables(3, 3)
    valid_count = 0
    invalid_count = 0
    tie_checks = 0
    strict_count = 0
    dominance_failures = 0
    validity_failures = 0
    valid_counts = []

    for table in tables:
        table_valid = 0
        for reports in all_direct_maps(3, levels):
            if not direct_map_valid(table, reports, levels):
                invalid_count += 1
                continue
            valid_count += 1
            table_valid += 1
            for order in consistent_orders(reports):
                certificate = dominance_certificate(
                    table, reports, levels, order
                )
                tie_checks += 1
                strict_count += bool(certificate.strict_coordinates)
                dominance_failures += (
                    not certificate.pointwise_dominates
                )
                validity_failures += not certificate.buehler_valid
        valid_counts.append(table_valid)

    optimum_checks = 0
    optimum_mismatches = 0
    for table in tables:
        for reference in weights:
            comparison = compare_global_optima(
                table, levels, levels, reference
            )
            optimum_checks += 1
            optimum_mismatches += (
                comparison.direct_value != comparison.buehler_value
            )

    controls = minimal_controls()
    output = {
        "schema": "asmp9-v0.52-development-census-v1",
        "claim_eligible": False,
        "table_count": len(tables),
        "direct_candidate_count": len(tables) * 27,
        "valid_direct_map_count": valid_count,
        "invalid_direct_map_count": invalid_count,
        "minimum_valid_maps_per_table": min(valid_counts),
        "maximum_valid_maps_per_table": max(valid_counts),
        "tie_refinement_check_count": tie_checks,
        "strict_dominance_certificate_count": strict_count,
        "dominance_failure_count": dominance_failures,
        "buehler_validity_failure_count": validity_failures,
        "global_optimum_check_count": optimum_checks,
        "global_optimum_mismatch_count": optimum_mismatches,
        "controls": {
            "equality_input": [
                qstr(value)
                for value in controls["equality"].reports
            ],
            "equality_output": [
                qstr(value)
                for value in controls["equality"].buehler_reports
            ],
            "strict_input": [
                qstr(value) for value in controls["strict"].reports
            ],
            "strict_output": [
                qstr(value)
                for value in controls["strict"].buehler_reports
            ],
        },
        "elapsed_seconds_descriptive": time.perf_counter() - started,
    }
    path = HERE / "DEVELOPMENT_CENSUS_v0_52.json"
    path.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
