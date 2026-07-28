from __future__ import annotations

import hashlib
import itertools
import json
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
CONDITIONAL = HERE.parent / "conditional_fiber_v0_13"
sys.path.insert(0, str(CONDITIONAL))

from conditional_fiber import (  # noqa: E402
    enumerate_fibers,
    fiber_affine_rank,
    incidence_rows,
)
from general_graph import (  # noqa: E402
    FULL,
    INTERIOR,
    ZERO,
    bridge_mask,
    connected_component_count,
    fractional_bad_support_design,
    full_quotient_available,
    graph_cycle_rank,
    minimal_bad_boundary_supports,
    theta_allocation_census,
    theta_worst_endpoint_availability,
)


OUTPUT = HERE / "DEVELOPMENT_CENSUS_v0_17.json"
RECEIPT = HERE / "DEVELOPMENT_RECEIPT_v0_17.json"


def fraction_record(value: Fraction) -> dict[str, Any]:
    return {
        "fraction": f"{value.numerator}/{value.denominator}",
        "decimal": float(value),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return fraction_record(value)
    if isinstance(value, tuple):
        return [jsonable(item) for item in value]
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): jsonable(item) for key, item in value.items()
        }
    return value


def residual_rank_checks() -> dict[str, Any]:
    graphs = {
        "cycle4": (
            4,
            ((0, 1), (1, 2), (2, 3), (3, 0)),
        ),
        "theta122": (
            4,
            ((0, 2), (0, 1), (1, 2), (0, 3), (3, 2)),
        ),
        "bowtie": (
            5,
            ((0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)),
        ),
    }
    records = []
    mismatch_count = 0
    checked_fibers = 0
    checked_states = 0
    for name, (node_count, edges) in graphs.items():
        rows = incidence_rows(node_count, edges)
        beta1 = graph_cycle_rank(node_count, edges)
        for trials_per_edge in (1, 2):
            trials = (trials_per_edge,) * len(edges)
            fibers = enumerate_fibers(trials, rows)
            cell_mismatches = 0
            for fiber in fibers.values():
                expected = fiber_affine_rank(fiber) == beta1
                for representative in fiber:
                    statuses = tuple(
                        ZERO
                        if count == 0
                        else FULL
                        if count == trials_per_edge
                        else INTERIOR
                        for count in representative
                    )
                    observed = full_quotient_available(
                        node_count, edges, statuses
                    )
                    cell_mismatches += int(observed != expected)
                    checked_states += 1
            mismatch_count += cell_mismatches
            checked_fibers += len(fibers)
            records.append(
                {
                    "graph": name,
                    "trials_per_edge": trials_per_edge,
                    "fiber_count": len(fibers),
                    "mismatch_count": cell_mismatches,
                }
            )
    return {
        "records": records,
        "checked_fiber_count": checked_fibers,
        "checked_state_count": checked_states,
        "mismatch_count": mismatch_count,
    }


def small_graph_census() -> dict[str, Any]:
    records = []
    for node_count in (3, 4):
        universe = tuple(itertools.combinations(range(node_count), 2))
        for mask in range(1, 1 << len(universe)):
            edges = tuple(
                universe[index]
                for index in range(len(universe))
                if mask & (1 << index)
            )
            if connected_component_count(node_count, edges) != 1:
                continue
            if graph_cycle_rank(node_count, edges) < 1:
                continue
            if any(bridge_mask(node_count, edges)):
                continue
            supports = minimal_bad_boundary_supports(node_count, edges)
            design = fractional_bad_support_design(
                len(edges), supports
            )
            uniform = min(
                Fraction(len(support), len(edges))
                for support in supports
            )
            records.append(
                {
                    "node_count": node_count,
                    "edges": [list(edge) for edge in edges],
                    "edge_count": len(edges),
                    "cycle_rank": graph_cycle_rank(
                        node_count, edges
                    ),
                    "support_count": len(supports),
                    "uniform_exponent": fraction_record(uniform),
                    "optimal_exponent": fraction_record(
                        design["threshold"]
                    ),
                    "uniform_is_suboptimal": (
                        design["threshold"] > uniform
                    ),
                    "optimal_vertices": jsonable(
                        design["optimal_vertices"]
                    ),
                }
            )
    return {
        "records": records,
        "graph_count": len(records),
        "uniform_suboptimal_count": sum(
            record["uniform_is_suboptimal"] for record in records
        ),
    }


def selected_graphs() -> list[dict[str, Any]]:
    cases = {
        "bowtie": (
            5,
            ((0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)),
        ),
        "theta123": (
            5,
            ((0, 1), (0, 2), (2, 1), (0, 3), (3, 4), (4, 1)),
        ),
        "cycle5_plus_chord": (
            5,
            ((0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)),
        ),
    }
    records = []
    for name, (node_count, edges) in cases.items():
        supports = minimal_bad_boundary_supports(node_count, edges)
        design = fractional_bad_support_design(len(edges), supports)
        uniform = min(
            Fraction(len(support), len(edges)) for support in supports
        )
        records.append(
            {
                "graph": name,
                "node_count": node_count,
                "edges": [list(edge) for edge in edges],
                "cycle_rank": graph_cycle_rank(node_count, edges),
                "minimal_bad_supports": [
                    list(support) for support in supports
                ],
                "uniform_exponent": fraction_record(uniform),
                "optimal_exponent": fraction_record(
                    design["threshold"]
                ),
                "optimal_vertices": jsonable(
                    design["optimal_vertices"]
                ),
            }
        )
    return records


def finite_theta_census() -> dict[str, Any]:
    paths = ((0,), (1, 2), (3, 4))
    epsilon = Fraction(1, 4)
    budget_records = []
    for total in range(5, 13):
        record = theta_allocation_census(paths, total, epsilon)
        budget_records.append(
            {
                "total_trials": total,
                "allocation_count": record["allocation_count"],
                "optimum": fraction_record(record["optimum"]),
                "optimizers": [
                    list(value) for value in record["optimizers"]
                ],
                "balanced_optimizer_count": record[
                    "balanced_optimizer_count"
                ],
            }
        )

    precision_records = []
    uniform_counts = (2, 2, 2, 2, 2)
    for interior in (
        Fraction(1, 8),
        Fraction(1, 4),
        Fraction(3, 8),
        Fraction(1, 2),
    ):
        record = theta_allocation_census(paths, 10, interior)
        uniform, _ = theta_worst_endpoint_availability(
            paths, uniform_counts, interior
        )
        precision_records.append(
            {
                "epsilon": fraction_record(interior),
                "uniform": fraction_record(uniform),
                "optimum": fraction_record(record["optimum"]),
                "gap": fraction_record(record["optimum"] - uniform),
                "optimizers": [
                    list(value) for value in record["optimizers"]
                ],
            }
        )
    return {
        "path_lengths": [1, 2, 2],
        "epsilon_quarter_budget_sweep": budget_records,
        "total_ten_interior_sweep": precision_records,
    }


def main() -> None:
    if OUTPUT.exists() or RECEIPT.exists():
        raise FileExistsError("refusing to overwrite development artifacts")
    started = time.perf_counter()
    result = {
        "status": "development_only",
        "residual_rank_checks": residual_rank_checks(),
        "small_graph_census": small_graph_census(),
        "selected_graphs": selected_graphs(),
        "finite_theta_census": finite_theta_census(),
        "claim_boundary": (
            "Burned exact development evidence for a prospective "
            "general-graph theorem; not registered, claim-eligible, "
            "behavioral evidence, or ASMP-9 resolution."
        ),
    }
    result["elapsed_seconds"] = time.perf_counter() - started
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    receipt = {
        "artifact": OUTPUT.name,
        "sha256": sha256(OUTPUT),
        "elapsed_seconds": result["elapsed_seconds"],
        "status": result["status"],
    }
    with RECEIPT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
