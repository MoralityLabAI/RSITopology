from __future__ import annotations

import argparse
import hashlib
import json
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

from experiment import (
    exact_allocation_optima,
    exhaustive_vertex_minimum_equal,
    fraction_record,
    minimal_equal_trials,
    one_sided_drift_availability,
    parse_fraction,
    sharp_min_availability,
    v014_crude_lower_bound,
)


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.receipt.exists():
        raise FileExistsError("refusing to overwrite development output")
    started = time.perf_counter()

    theorem_cells = []
    for k in range(3, 11):
        for n in range(1, 9):
            for epsilon in (
                Fraction(1, 20),
                Fraction(1, 10),
                Fraction(1, 5),
                Fraction(1, 4),
                Fraction(2, 5),
            ):
                formula = sharp_min_availability(k, n, epsilon)
                exhaustive, witnesses = exhaustive_vertex_minimum_equal(
                    k, n, epsilon
                )
                crude = v014_crude_lower_bound(k, n, epsilon)
                drift = one_sided_drift_availability(k, n, epsilon)
                theorem_cells.append(
                    {
                        "cycle_length": k,
                        "trials_per_edge": n,
                        "epsilon": fraction_record(epsilon),
                        "sharp_minimum": fraction_record(formula),
                        "exhaustive_vertex_minimum": fraction_record(
                            exhaustive
                        ),
                        "minimizing_low_edge_counts": witnesses,
                        "formula_matches": formula == exhaustive,
                        "expected_witnesses": sorted(
                            {k // 2, k - k // 2}
                        ),
                        "witnesses_match": witnesses
                        == sorted({k // 2, k - k // 2}),
                        "v014_crude_bound": fraction_record(crude),
                        "sharp_dominates_crude": formula >= crude,
                        "one_sided_drift": fraction_record(drift),
                        "balanced_split_no_larger_than_drift": (
                            formula <= drift
                        ),
                        "balanced_split_strictly_below_drift": (
                            k < 4 or formula < drift
                        ),
                    }
                )

    threshold_cells = []
    for k in (3, 4, 6, 8, 12):
        for epsilon in (
            Fraction(1, 20),
            Fraction(1, 10),
            Fraction(1, 5),
            Fraction(1, 4),
        ):
            for delta in (
                Fraction(1, 5),
                Fraction(1, 10),
                Fraction(1, 20),
                Fraction(1, 100),
            ):
                target = 1 - delta
                threshold = minimal_equal_trials(k, epsilon, target)
                if threshold is None:
                    raise AssertionError("positive interior has no threshold")
                at_threshold = sharp_min_availability(
                    k, threshold, epsilon
                )
                predecessor = (
                    Fraction(0)
                    if threshold == 1
                    else sharp_min_availability(
                        k, threshold - 1, epsilon
                    )
                )
                threshold_cells.append(
                    {
                        "cycle_length": k,
                        "epsilon": fraction_record(epsilon),
                        "delta": fraction_record(delta),
                        "target": fraction_record(target),
                        "minimum_trials_per_edge": threshold,
                        "predecessor_availability": fraction_record(
                            predecessor
                        ),
                        "threshold_availability": fraction_record(
                            at_threshold
                        ),
                        "sharp_threshold_holds": (
                            predecessor < target <= at_threshold
                        ),
                    }
                )

    zero_interior_cells = []
    for k in (3, 4, 6, 8):
        for n in (1, 3, 10, 30):
            value = sharp_min_availability(k, n, Fraction(0))
            zero_interior_cells.append(
                {
                    "cycle_length": k,
                    "trials_per_edge": n,
                    "minimum_availability": fraction_record(value),
                    "no_positive_uniform_guarantee": value == 0,
                }
            )

    allocation_cells = []
    for k in (3, 4, 5):
        for epsilon in (
            Fraction(1, 10),
            Fraction(1, 5),
            Fraction(1, 4),
        ):
            for extra in range(0, 9):
                allocation_cells.append(
                    exact_allocation_optima(k + extra, k, epsilon)
                )

    result = {
        "status": "burned_development_only",
        "theorem_cells": theorem_cells,
        "threshold_cells": threshold_cells,
        "zero_interior_cells": zero_interior_cells,
        "allocation_cells": allocation_cells,
        "summary": {
            "theorem_cell_count": len(theorem_cells),
            "formula_mismatch_count": sum(
                not row["formula_matches"] for row in theorem_cells
            ),
            "witness_mismatch_count": sum(
                not row["witnesses_match"] for row in theorem_cells
            ),
            "crude_bound_mismatch_count": sum(
                not row["sharp_dominates_crude"]
                for row in theorem_cells
            ),
            "drift_control_mismatch_count": sum(
                not row["balanced_split_no_larger_than_drift"]
                or not row["balanced_split_strictly_below_drift"]
                for row in theorem_cells
            ),
            "threshold_cell_count": len(threshold_cells),
            "threshold_mismatch_count": sum(
                not row["sharp_threshold_holds"]
                for row in threshold_cells
            ),
            "zero_interior_cell_count": len(zero_interior_cells),
            "zero_interior_mismatch_count": sum(
                not row["no_positive_uniform_guarantee"]
                for row in zero_interior_cells
            ),
            "allocation_cell_count": len(allocation_cells),
            "balanced_allocation_failure_count": sum(
                not row["balanced_is_optimal"]
                for row in allocation_cells
            ),
        },
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": (
            "Unregistered exact development evidence for a sharp "
            "equal-count interior-availability theorem and a bounded "
            "integer-allocation conjecture; not a registered result, "
            "general Bradley-Terry optimal design, or ASMP-9 resolution."
        ),
    }
    write_json(args.output, result)
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    write_json(
        args.receipt,
        {
            "artifact": args.output.name,
            "sha256": digest,
            "status": "burned_development_only",
        },
    )
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
