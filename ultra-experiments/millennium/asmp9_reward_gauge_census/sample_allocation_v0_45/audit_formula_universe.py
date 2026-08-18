"""Exhaustive exact-LP audit of the ASMP-9 v0.45 closed forms."""

from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
V41 = HERE.parent / "sequential_risk_access_v0_41"
for path in (HERE, V41):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from allocation_design import (  # noqa: E402
    enumerate_policy_occupancies,
    exact_upper_for_allocation,
    positive_allocations,
    qstr,
    registered_constructive_upper,
)
from sequential_access import (  # noqa: E402
    ADAPTIVITY_GAP_QUERIES,
    binary_group_problem,
    classification_problem,
)


_WORKER_MODE: str | None = None
_WORKER_ENVELOPES = ()
_WORKER_PROBLEM = None
_WORKER_REFERENCE = ()


def canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _initialize_worker(mode: str) -> None:
    global _WORKER_MODE
    global _WORKER_ENVELOPES
    global _WORKER_PROBLEM
    global _WORKER_REFERENCE
    if mode == "branch_classification":
        problem = classification_problem(4)
    elif mode == "root_group":
        problem = binary_group_problem(
            "root_group",
            (0, 0, 1, 1),
            false_positive_cost=Q(1),
        )
    else:
        raise ValueError("unknown formula-audit mode")
    _WORKER_MODE = mode
    _WORKER_PROBLEM = problem
    _WORKER_ENVELOPES = enumerate_policy_occupancies(
        ADAPTIVITY_GAP_QUERIES, problem, 2
    )
    _WORKER_REFERENCE = (
        tuple([Q(0)] * problem.target_count),
    )


def _audit_one(allocation: tuple[int, ...]) -> dict:
    if _WORKER_MODE is None or _WORKER_PROBLEM is None:
        raise RuntimeError("worker was not initialized")
    exact = exact_upper_for_allocation(
        _WORKER_ENVELOPES,
        _WORKER_PROBLEM,
        allocation,
        3,
        _WORKER_REFERENCE,
    )
    formula = registered_constructive_upper(
        allocation, _WORKER_MODE
    )
    return {
        "allocation": list(allocation),
        "exact_upper": qstr(exact),
        "formula_upper": qstr(formula),
        "match": exact == formula,
    }


def audit_mode(
    mode: str,
    total_budget: int,
    workers: int,
) -> dict:
    allocations = positive_allocations(total_budget, 3)
    started = time.perf_counter()
    if workers == 1:
        _initialize_worker(mode)
        rows = [_audit_one(row) for row in allocations]
    else:
        context = mp.get_context("spawn")
        with context.Pool(
            processes=workers,
            initializer=_initialize_worker,
            initargs=(mode,),
        ) as pool:
            rows = list(
                pool.imap_unordered(
                    _audit_one, allocations, chunksize=4
                )
            )
    rows.sort(key=lambda row: row["allocation"])
    encoded = canonical_json_bytes(rows)
    mismatches = [row for row in rows if not row["match"]]
    exact_values = [
        (Q(row["exact_upper"]), tuple(row["allocation"]))
        for row in rows
    ]
    formula_values = [
        (Q(row["formula_upper"]), tuple(row["allocation"]))
        for row in rows
    ]
    exact_best = min(value for value, _ in exact_values)
    formula_best = min(value for value, _ in formula_values)
    quotient, remainder = divmod(total_budget, 3)
    uniform = tuple(
        quotient + int(index < remainder) for index in range(3)
    )
    exact_uniform = next(
        value
        for value, allocation in exact_values
        if allocation == uniform
    )
    formula_uniform = next(
        value
        for value, allocation in formula_values
        if allocation == uniform
    )
    exact_optima = [
        list(allocation)
        for value, allocation in exact_values
        if value == exact_best
    ]
    formula_optima = [
        list(allocation)
        for value, allocation in formula_values
        if value == formula_best
    ]
    maximum_formula_excess = max(
        Q(row["formula_upper"]) - Q(row["exact_upper"])
        for row in rows
    )
    underbound_count = sum(
        Q(row["formula_upper"]) < Q(row["exact_upper"])
        for row in rows
    )
    return {
        "mode": mode,
        "total_budget": total_budget,
        "allocations": len(rows),
        "workers": workers,
        "mismatch_count": len(mismatches),
        "first_mismatches": mismatches[:10],
        "exact_best_upper": qstr(exact_best),
        "exact_optima": exact_optima,
        "uniform_allocation": list(uniform),
        "exact_uniform_upper": qstr(exact_uniform),
        "formula_best_upper": qstr(formula_best),
        "formula_optima": formula_optima,
        "formula_uniform_upper": qstr(formula_uniform),
        "maximum_formula_excess": qstr(maximum_formula_excess),
        "constructive_underbound_count": underbound_count,
        "rows_sha256": hashlib.sha256(encoded).hexdigest(),
        "elapsed_seconds": time.perf_counter() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--total-budget", type=int, default=54)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError("workers must be positive")
    result = {
        "schema": "asmp9-v0.45-formula-universe-audit-v1",
        "results": [
            audit_mode(
                mode, args.total_budget, args.workers
            )
            for mode in (
                "branch_classification",
                "root_group",
            )
        ],
    }
    encoded = canonical_json_bytes(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    sys.stdout.buffer.write(encoded)


if __name__ == "__main__":
    mp.freeze_support()
    main()
