from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

from experiment import (
    allocation_census,
    balanced_allocation,
    balanced_worst_closed,
    minimal_total_trials,
    pair_constants,
    smoothing_certificate,
    worst_endpoint_availability,
)


def write_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.receipt.exists():
        raise FileExistsError("refusing to overwrite development output")

    started = time.perf_counter()
    epsilons = (
        Fraction(1, 100),
        Fraction(1, 20),
        Fraction(1, 8),
        Fraction(1, 5),
        Fraction(1, 3),
        Fraction(1, 2),
    )

    local_records = []
    other_count_sets = (
        (1,),
        (2,),
        (5,),
        (1, 3),
        (2, 5),
        (1, 2, 4),
    )
    for epsilon in epsilons:
        for a in range(1, 7):
            for difference in range(2, 8):
                b = a + difference
                for other_counts in other_count_sets:
                    for labels in itertools.product(
                        (0, 1), repeat=len(other_counts)
                    ):
                        U, V, W = pair_constants(
                            other_counts, epsilon, labels
                        )
                        local_records.append(
                            smoothing_certificate(
                                a, b, epsilon, U, V, W
                            )
                        )

    allocation_records = []
    for k in range(3, 8):
        for epsilon in (
            Fraction(1, 50),
            Fraction(1, 12),
            Fraction(1, 6),
            Fraction(3, 10),
            Fraction(9, 20),
        ):
            for extra in range(0, 11):
                allocation_records.append(
                    allocation_census(k + extra, k, epsilon)
                )

    closed_value_records = []
    for k in range(3, 11):
        for epsilon in (
            Fraction(1, 40),
            Fraction(1, 9),
            Fraction(2, 9),
            Fraction(7, 20),
        ):
            for extra in range(0, 13):
                total = k + extra
                closed, witnesses = balanced_worst_closed(
                    total, k, epsilon
                )
                exhaustive, _ = worst_endpoint_availability(
                    balanced_allocation(total, k), epsilon
                )
                closed_value_records.append(
                    {
                        "cycle_length": k,
                        "total_trials": total,
                        "epsilon": (
                            f"{epsilon.numerator}/{epsilon.denominator}"
                        ),
                        "closed": (
                            f"{closed.numerator}/{closed.denominator}"
                        ),
                        "exhaustive": (
                            f"{exhaustive.numerator}/"
                            f"{exhaustive.denominator}"
                        ),
                        "witnesses": [
                            list(witness) for witness in witnesses
                        ],
                        "matches": closed == exhaustive,
                    }
                )

    threshold_records = []
    for k in (3, 5, 8, 11):
        for epsilon in (
            Fraction(1, 20),
            Fraction(1, 8),
            Fraction(1, 4),
            Fraction(2, 5),
        ):
            for delta in (
                Fraction(1, 5),
                Fraction(1, 20),
                Fraction(1, 100),
            ):
                target = 1 - delta
                threshold = minimal_total_trials(k, epsilon, target)
                if threshold is None:
                    raise AssertionError("positive interior has no threshold")
                current, _ = balanced_worst_closed(
                    threshold, k, epsilon
                )
                predecessor = (
                    Fraction(0)
                    if threshold == k
                    else balanced_worst_closed(
                        threshold - 1, k, epsilon
                    )[0]
                )
                threshold_records.append(
                    {
                        "cycle_length": k,
                        "epsilon": (
                            f"{epsilon.numerator}/{epsilon.denominator}"
                        ),
                        "delta": (
                            f"{delta.numerator}/{delta.denominator}"
                        ),
                        "minimum_total_trials": threshold,
                        "predecessor": (
                            f"{predecessor.numerator}/"
                            f"{predecessor.denominator}"
                        ),
                        "current": (
                            f"{current.numerator}/{current.denominator}"
                        ),
                        "straddles": predecessor < target <= current,
                    }
                )

    zero_boundary_records = []
    for counts in (
        (1, 1, 8),
        (1, 2, 3, 9),
        (2, 2, 2, 10),
        (1, 1, 1, 1, 20),
    ):
        value, _ = worst_endpoint_availability(counts, Fraction(0))
        zero_boundary_records.append(
            {
                "allocation": list(counts),
                "worst_availability_fraction": (
                    f"{value.numerator}/{value.denominator}"
                ),
                "is_zero": value == 0,
            }
        )

    k_two_records = []
    for total in range(4, 13):
        record = allocation_census(total, 2, Fraction(1, 5))
        k_two_records.append(
            {
                "total_trials": total,
                "optimizer_count": len(record["optimizers"]),
                "all_allocations_optimal": (
                    len(record["optimizers"])
                    == record["allocation_count"]
                ),
            }
        )

    summary = {
        "local_cell_count": len(local_records),
        "local_formula_mismatch_count": sum(
            not row["branch_formula_matches_direct"]
            or not row["same_decomposition_holds"]
            or not row["opposite_decomposition_holds"]
            for row in local_records
        ),
        "local_smoothing_failure_count": sum(
            not row["same_strictly_improves"]
            or not row["opposite_strictly_improves"]
            or not row["minimum_strictly_improves"]
            for row in local_records
        ),
        "local_identity_failure_count": sum(
            not row["D_is_invariant"]
            or not row["E_is_nondecreasing"]
            or not row["pair_products_nondecrease"]
            for row in local_records
        ),
        "allocation_cell_count": len(allocation_records),
        "balanced_optimum_failure_count": sum(
            not row["balanced_is_unique_modulo_permutation"]
            for row in allocation_records
        ),
        "global_smoothing_failure_count": sum(
            not row["all_smoothing_steps_strict"]
            for row in allocation_records
        ),
        "closed_value_cell_count": len(closed_value_records),
        "closed_value_mismatch_count": sum(
            not row["matches"] for row in closed_value_records
        ),
        "threshold_cell_count": len(threshold_records),
        "threshold_mismatch_count": sum(
            not row["straddles"] for row in threshold_records
        ),
        "zero_boundary_cell_count": len(zero_boundary_records),
        "zero_boundary_failure_count": sum(
            not row["is_zero"] for row in zero_boundary_records
        ),
        "k_two_cell_count": len(k_two_records),
        "k_two_boundary_failure_count": sum(
            not row["all_allocations_optimal"] for row in k_two_records
        ),
    }
    result = {
        "status": "burned_development_only",
        "summary": summary,
        "local_records": local_records,
        "allocation_records": allocation_records,
        "closed_value_records": closed_value_records,
        "threshold_records": threshold_records,
        "zero_boundary_records": zero_boundary_records,
        "k_two_records": k_two_records,
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": (
            "Unregistered exact development verification of a pairwise "
            "balancing proof and its epsilon=0 and k=2 boundaries; not a "
            "prospective result, general Bradley-Terry design theorem, "
            "adaptive rollout result, or ASMP-9 resolution."
        ),
    }
    write_json(args.output, result)
    write_json(
        args.receipt,
        {
            "artifact": args.output.name,
            "sha256": sha256(args.output),
            "status": "burned_development_only",
        },
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
