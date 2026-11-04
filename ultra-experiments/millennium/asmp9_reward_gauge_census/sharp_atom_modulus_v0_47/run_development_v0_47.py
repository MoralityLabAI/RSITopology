"""Run the burned ASMP-9 v0.47 finite-grid development census."""

from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

from sharp_atom_modulus import (
    allocation_modulus_census,
    classification_risk_table,
    qstr,
    root_group_risk_table,
)


HERE = Path(__file__).resolve().parent
LEVELS = (Q(0), Q(1, 10), Q(1, 5), Q(3, 10), Q(2, 5), Q(1, 2))
ALPHA = Q(1, 20)


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def summarize_census(census: dict) -> dict:
    rows = [row.jsonable() for row in census["rows"]]
    encoded_rows = canonical_bytes(rows)
    return {
        "total_budget": census["total_budget"],
        "allocation_count": census["allocation_count"],
        "optimum": qstr(census["optimum"]),
        "optimizers": [list(row) for row in census["optimizers"]],
        "unique": census["unique"],
        "uniform": census["uniform"].jsonable(),
        "boundary_equalities": sum(
            row.modulus.boundary_count for row in census["rows"]
        ),
        "rows": rows,
        "rows_sha256": hashlib.sha256(encoded_rows).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--total-budget", type=int, default=66)
    args = parser.parse_args()
    started = time.perf_counter()
    classification = classification_risk_table(
        LEVELS, workers=args.workers
    )
    root = root_group_risk_table(LEVELS)
    classification_rows = [
        {
            "parameter": [qstr(value) for value in parameter],
            "risk": qstr(risk),
        }
        for parameter, risk in sorted(classification.items())
    ]
    risk_hash = hashlib.sha256(
        canonical_bytes(classification_rows)
    ).hexdigest()
    classification_census = summarize_census(
        allocation_modulus_census(
            classification, args.total_budget, ALPHA
        )
    )
    root_census = summarize_census(
        allocation_modulus_census(root, args.total_budget, ALPHA)
    )
    payload = {
        "schema": "asmp9-v0.47-sharp-atom-development-v1",
        "development_only": True,
        "claim_eligible": False,
        "levels": [qstr(value) for value in LEVELS],
        "parameter_count": len(classification),
        "alpha": qstr(ALPHA),
        "total_budget": args.total_budget,
        "workers": args.workers,
        "elapsed_seconds": time.perf_counter() - started,
        "classification_risks": classification_rows,
        "classification_risks_sha256": risk_hash,
        "classification": classification_census,
        "root_group": root_census,
        "liveness": {
            "classification_nonzero": (
                Q(classification_census["optimum"]) > 0
            ),
            "root_group_nonzero": Q(root_census["optimum"]) > 0,
            "decision_optima_differ": (
                classification_census["optimizers"]
                != root_census["optimizers"]
            ),
            "no_boundary_equalities": (
                classification_census["boundary_equalities"] == 0
                and root_census["boundary_equalities"] == 0
            ),
        },
    }
    encoded = canonical_bytes(payload)
    output = HERE / "DEVELOPMENT_RESULT_v0_47.json"
    output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "path": output.name,
                "sha256": hashlib.sha256(encoded).hexdigest(),
                "elapsed_seconds": payload["elapsed_seconds"],
                "classification_optimum": (
                    classification_census["optimum"]
                ),
                "classification_allocations": (
                    classification_census["optimizers"]
                ),
                "root_group_optimum": root_census["optimum"],
                "root_group_allocations": root_census["optimizers"],
                "liveness": payload["liveness"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
