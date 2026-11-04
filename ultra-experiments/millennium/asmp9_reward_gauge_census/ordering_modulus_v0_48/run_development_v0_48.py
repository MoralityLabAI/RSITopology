"""Run the burned ASMP-9 v0.48 evidence-ordering search."""

from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V47 = HERE.parent / "sharp_atom_modulus_v0_47"
for path in (HERE, V47):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ordering_modulus import (  # noqa: E402
    buehler_subset_bounds,
    exhaustive_ordering_census,
    exhaustive_cross_audit,
    experiment_rows,
    prefix_probability_tables,
    qstr,
    uniform_parameter_mixture,
)
from sharp_atom_modulus import (  # noqa: E402
    classification_risks,
    parameter_grid,
)


ALLOCATION = (1, 1, 1)
SEARCH = (
    ((Q(0), Q(1, 5), Q(2, 5)), Q(1, 20)),
    ((Q(0), Q(1, 5), Q(2, 5)), Q(1, 10)),
    ((Q(0), Q(1, 5), Q(2, 5)), Q(1, 5)),
    ((Q(0), Q(1, 5), Q(2, 5)), Q(3, 10)),
    ((Q(0), Q(1, 10), Q(3, 10)), Q(1, 20)),
    ((Q(0), Q(1, 10), Q(3, 10)), Q(1, 10)),
    ((Q(0), Q(1, 10), Q(3, 10)), Q(1, 5)),
    ((Q(0), Q(1, 10), Q(3, 10)), Q(3, 10)),
    ((Q(0), Q(1, 10), Q(1, 5), Q(2, 5)), Q(1, 10)),
    ((Q(0), Q(1, 10), Q(1, 5), Q(2, 5)), Q(1, 5)),
)


def canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def run_fixture(
    levels: tuple[Q, ...],
    alpha: Q,
    all_risks: dict,
) -> dict:
    parameters = parameter_grid(levels)
    risks = {
        parameter: all_risks[parameter] for parameter in parameters
    }
    root_risks = {
        parameter: parameter[0] for parameter in parameters
    }
    outcomes, probabilities = experiment_rows(
        parameters, ALLOCATION
    )
    reference = uniform_parameter_mixture(probabilities)
    subsets = prefix_probability_tables(probabilities)
    class_bounds = buehler_subset_bounds(risks, subsets, alpha)
    root_bounds = buehler_subset_bounds(root_risks, subsets, alpha)
    class_census = exhaustive_ordering_census(
        class_bounds, reference, keep_optimizers=8
    )
    root_census = exhaustive_ordering_census(
        root_bounds, reference, keep_optimizers=8
    )
    audit = exhaustive_cross_audit(
        class_census.optimum,
        class_bounds,
        root_census.optimum,
        root_bounds,
        reference,
    )
    return {
        "levels": [qstr(value) for value in levels],
        "alpha": qstr(alpha),
        "parameters": len(parameters),
        "outcomes": [list(outcome) for outcome in outcomes],
        "reference_weights": [qstr(value) for value in reference],
        "classification_risk_range": [
            qstr(min(risks.values())),
            qstr(max(risks.values())),
        ],
        "root_risk_range": [
            qstr(min(root_risks.values())),
            qstr(max(root_risks.values())),
        ],
        "classification_bound_values": sorted(
            {qstr(value) for value in class_bounds}
        ),
        "root_bound_values": sorted(
            {qstr(value) for value in root_bounds}
        ),
        "classification": class_census.jsonable(outcomes),
        "root_group": root_census.jsonable(outcomes),
        "cross_audit": audit,
        "live": (
            len(set(class_bounds)) > 1
            and len(set(root_bounds)) > 1
            and audit["common_optimizer_count"] == 0
            and Q(audit["first_cross_regret"]) > 0
            and Q(audit["second_cross_regret"]) > 0
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "DEVELOPMENT_RESULT_v0_48.json",
    )
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError("workers must be positive")
    started = time.perf_counter()
    master_levels = tuple(
        sorted(
            {
                value
                for levels, _ in SEARCH
                for value in levels
            }
        )
    )
    all_risks = classification_risks(
        parameter_grid(master_levels), workers=args.workers
    )
    rows = [
        run_fixture(levels, alpha, all_risks)
        for levels, alpha in SEARCH
    ]
    live_indices = [
        index for index, row in enumerate(rows) if row["live"]
    ]
    payload = {
        "schema": "asmp9-v0.48-ordering-development-v1",
        "claim_eligible": False,
        "allocation": list(ALLOCATION),
        "search_cells": len(rows),
        "master_levels": [
            qstr(value) for value in master_levels
        ],
        "classification_risk_points": len(all_risks),
        "live_indices": live_indices,
        "first_live_index": live_indices[0] if live_indices else None,
        "status": (
            "decision_dependent_ordering_live"
            if live_indices
            else "decision_dependent_ordering_not_found"
        ),
        "rows": rows,
        "elapsed_seconds": time.perf_counter() - started,
        "workers": args.workers,
    }
    encoded = canonical_json_bytes(payload)
    output = args.output.resolve()
    if output.exists() and output.read_bytes() != encoded:
        raise RuntimeError("development output mismatch")
    output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "output": output.relative_to(REPO).as_posix(),
                "sha256": hashlib.sha256(encoded).hexdigest(),
                "status": payload["status"],
                "live_indices": live_indices,
                "elapsed_seconds": payload["elapsed_seconds"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
