"""Targeted burned liveness check for the ASMP-9 v0.47 atom modulus."""

from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

from sharp_atom_modulus import (
    boundary_parameters,
    classification_risks,
    mandatory_atom_region,
    parameter_grid,
    qstr,
    root_group_risk_table,
    sharp_atom_modulus,
)


HERE = Path(__file__).resolve().parent
V46_RESULT = (
    HERE.parent
    / "coupled_uncertainty_v0_46"
    / "artifacts_v0_46"
    / "result_v0_46.json"
)
LEVELS = tuple(
    Q(value, 100) for value in (0, 2, 4, 5, 6, 8, 10, 12, 13, 14, 15)
)
ALPHA = Q(1, 20)
CLASSIFICATION_ALLOCATIONS = ((28, 19, 19), (22, 22, 22))
ROOT_ALLOCATIONS = ((64, 1, 1), (22, 22, 22))


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    started = time.perf_counter()
    universe = parameter_grid(LEVELS)
    classification_required = set()
    for allocation in CLASSIFICATION_ALLOCATIONS:
        classification_required.update(
            mandatory_atom_region(universe, allocation, ALPHA)
        )
    classification = classification_risks(
        classification_required,
        workers=args.workers,
    )
    root = root_group_risk_table(LEVELS)
    class_results = {
        ",".join(map(str, allocation)): sharp_atom_modulus(
            classification,
            allocation,
            ALPHA,
            parameter_universe=universe,
        ).jsonable()
        for allocation in CLASSIFICATION_ALLOCATIONS
    }
    root_results = {
        ",".join(map(str, allocation)): sharp_atom_modulus(
            root,
            allocation,
            ALPHA,
            parameter_universe=universe,
        ).jsonable()
        for allocation in ROOT_ALLOCATIONS
    }
    boundaries = {
        ",".join(map(str, allocation)): len(
            boundary_parameters(universe, allocation, ALPHA)
        )
        for allocation in (
            *CLASSIFICATION_ALLOCATIONS,
            ROOT_ALLOCATIONS[0],
        )
    }
    v46 = json.loads(V46_RESULT.read_text(encoding="utf-8"))
    v46_class = v46["scientific"]["coupled"]["branch_classification"]
    v46_root = v46["scientific"]["coupled"]["root_group"]
    comparisons = {
        "classification_optimum": {
            "allocation": [28, 19, 19],
            "sharp_atom": class_results["28,19,19"]["upper"],
            "v0_46_method_of_types_upper": v46_class["optimum_interval"][1],
        },
        "classification_uniform": {
            "allocation": [22, 22, 22],
            "sharp_atom": class_results["22,22,22"]["upper"],
            "v0_46_method_of_types_upper": v46_class["uniform_interval"][1],
        },
        "root_optimum": {
            "allocation": [64, 1, 1],
            "sharp_atom": root_results["64,1,1"]["upper"],
            "v0_46_method_of_types_upper": v46_root["optimum_interval"][1],
        },
        "root_uniform": {
            "allocation": [22, 22, 22],
            "sharp_atom": root_results["22,22,22"]["upper"],
            "v0_46_method_of_types_upper": v46_root["uniform_interval"][1],
        },
    }
    liveness = {
        "all_moduli_nonzero": all(
            Q(result["upper"]) > 0
            for result in (*class_results.values(), *root_results.values())
        ),
        "all_lower_upper_matched": all(
            result["matched"]
            for result in (*class_results.values(), *root_results.values())
        ),
        "no_boundary_equalities": all(
            count == 0 for count in boundaries.values()
        ),
        "method_of_types_strictly_above_sharp_atom": all(
            Q(row["v0_46_method_of_types_upper"])
            > Q(row["sharp_atom"])
            for row in comparisons.values()
        ),
    }
    payload = {
        "schema": "asmp9-v0.47-targeted-development-v1",
        "development_only": True,
        "claim_eligible": False,
        "levels": [qstr(value) for value in LEVELS],
        "parameter_universe": len(universe),
        "classification_risk_points": len(classification),
        "alpha": qstr(ALPHA),
        "classification": class_results,
        "root_group": root_results,
        "boundary_equalities": boundaries,
        "comparisons": comparisons,
        "liveness": liveness,
        "elapsed_seconds": time.perf_counter() - started,
    }
    encoded = canonical_bytes(payload)
    output = HERE / "DEVELOPMENT_TARGETED_RESULT_v0_47.json"
    output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "path": output.name,
                "sha256": hashlib.sha256(encoded).hexdigest(),
                "elapsed_seconds": payload["elapsed_seconds"],
                "classification_risk_points": len(classification),
                "comparisons": comparisons,
                "liveness": liveness,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
