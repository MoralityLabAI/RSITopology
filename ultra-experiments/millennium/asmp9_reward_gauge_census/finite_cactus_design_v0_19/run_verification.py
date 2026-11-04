from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import platform
import subprocess
import time
from datetime import datetime, timezone
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any, Iterable

from finite_cactus_design import (
    allocation_value,
    balanced_allocation,
    bouquet_cactus,
    cactus_availability_factorized,
    fraction_record,
    globally_balanced_cycle_totals,
    graph_availability_direct,
    marginal_greedy_endpoints,
    optimize_all_edges_exhaustive,
    optimize_cactus_dp,
    optimize_cycle_totals_exhaustive,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_json(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_text(path: Path, value: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def peak_resident_bytes() -> int:
    if os.name == "nt":
        from ctypes import wintypes

        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(ProcessMemoryCounters),
            wintypes.DWORD,
        )
        if not psapi.GetProcessMemoryInfo(
            kernel32.GetCurrentProcess(),
            ctypes.byref(counters),
            counters.cb,
        ):
            raise OSError("GetProcessMemoryInfo failed")
        return int(counters.PeakWorkingSetSize)
    import resource

    maximum = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return maximum if platform.system() == "Darwin" else maximum * 1024


def validate_registration(
    registration_path: Path, protocol_path: Path
) -> tuple[dict[str, Any], str, dict[str, bool]]:
    registration = json.loads(
        registration_path.read_text(encoding="utf-8")
    )
    checks: dict[str, bool] = {}
    for relative, expected in registration["sealed_files"].items():
        path = REPO / relative
        checks[relative] = path.is_file() and sha256(path) == expected
    checks["protocol_path"] = (
        registration["protocol_path"]
        == protocol_path.relative_to(REPO).as_posix()
    )
    checks["implementation_commit_is_ancestor"] = (
        subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                registration["implementation_commit"],
                "HEAD",
            ],
            cwd=REPO,
            check=False,
        ).returncode
        == 0
    )
    return registration, sha256(registration_path), checks


def fresh_registry_checks(protocol: dict[str, Any]) -> dict[str, Any]:
    burned = {
        Fraction(value)
        for value in protocol["development_registry"][
            "burned_epsilon_values"
        ]
    }
    sections = {
        "factorization": protocol["factorization_cells"],
        "dp": protocol["dp_cells"],
        "comparator": protocol["comparator_cells"],
        "global": {"global_edge_census": protocol["global_edge_census"]},
    }
    ids = [
        f"{section}:{name}"
        for section, cells in sections.items()
        for name in cells
    ]
    epsilon_rows = [
        {
            "cell": f"{section}:{name}",
            "epsilon": raw["epsilon"],
            "outside_burned_set": Fraction(raw["epsilon"]) not in burned,
        }
        for section, cells in sections.items()
        for name, raw in cells.items()
    ]
    dimensions: dict[str, bool] = {}
    direct = protocol["factorization_cells"]["fresh_figure_3_4"]
    dimensions["fresh_figure_3_4"] = (
        sum(direct["cycle_lengths"]) + direct["bridge_count"]
        == len(direct["counts"])
        and direct["label_mode"] == "all"
    )
    bridge = protocol["factorization_cells"][
        "fresh_figure_3_5_bridge"
    ]
    bridge_edges = sum(bridge["cycle_lengths"]) + bridge["bridge_count"]
    dimensions["fresh_figure_3_5_bridge"] = (
        len(bridge["counts_a"]) == bridge_edges
        and len(bridge["counts_b"]) == bridge_edges
        and all(
            len(labels) == bridge_edges
            for labels in bridge["label_vectors"]
        )
    )
    for section in ("dp_cells", "comparator_cells"):
        for name, raw in protocol[section].items():
            dimensions[name] = (
                raw["total_budget"]
                >= sum(raw["cycle_lengths"]) + raw["bridge_count"]
            )
    global_raw = protocol["global_edge_census"]
    dimensions["global_edge_census"] = (
        global_raw["total_budget"]
        >= sum(global_raw["cycle_lengths"])
        + global_raw["bridge_count"]
    )
    return {
        "cell_ids": ids,
        "unique_cell_ids": len(ids) == len(set(ids)),
        "epsilon_rows": epsilon_rows,
        "dimensions": dimensions,
        "pass": (
            len(ids) == len(set(ids))
            and all(row["outside_burned_set"] for row in epsilon_rows)
            and all(dimensions.values())
        ),
    }


def factorization_record(
    name: str, raw: dict[str, Any]
) -> dict[str, Any]:
    graph = bouquet_cactus(
        raw["cycle_lengths"], raw["bridge_count"]
    )
    epsilon = Fraction(raw["epsilon"])
    counts = tuple(int(value) for value in raw["counts"])
    labels_iter: Iterable[tuple[int, ...]]
    if raw["label_mode"] != "all":
        raise ValueError("unsupported label mode")
    labels_iter = product((0, 1), repeat=len(graph.edges))
    rows: list[dict[str, Any]] = []
    mismatches = 0
    for labels in labels_iter:
        direct = graph_availability_direct(
            graph, counts, epsilon, labels
        )
        factorized = cactus_availability_factorized(
            graph, counts, epsilon, labels
        )
        if direct != factorized:
            mismatches += 1
        rows.append(
            {
                "labels": "".join(str(value) for value in labels),
                "direct": f"{direct.numerator}/{direct.denominator}",
                "factorized": (
                    f"{factorized.numerator}/{factorized.denominator}"
                ),
            }
        )
    return {
        "name": name,
        "edge_count": len(graph.edges),
        "label_count": len(rows),
        "residual_state_evaluations": len(rows) * 3 ** len(graph.edges),
        "mismatch_count": mismatches,
        "row_sha256": sha256_json(rows),
        "rows": rows,
    }


def bridge_record(name: str, raw: dict[str, Any]) -> dict[str, Any]:
    graph = bouquet_cactus(
        raw["cycle_lengths"], raw["bridge_count"]
    )
    epsilon = Fraction(raw["epsilon"])
    counts_a = tuple(int(value) for value in raw["counts_a"])
    counts_b = tuple(int(value) for value in raw["counts_b"])
    rows: list[dict[str, Any]] = []
    for raw_labels in raw["label_vectors"]:
        labels = tuple(int(value) for value in raw_labels)
        direct_a = graph_availability_direct(
            graph, counts_a, epsilon, labels
        )
        direct_b = graph_availability_direct(
            graph, counts_b, epsilon, labels
        )
        factorized = cactus_availability_factorized(
            graph, counts_a, epsilon, labels
        )
        rows.append(
            {
                "labels": "".join(str(value) for value in labels),
                "direct_a": fraction_record(direct_a),
                "direct_b": fraction_record(direct_b),
                "factorized": fraction_record(factorized),
                "all_equal": direct_a == direct_b == factorized,
            }
        )
    return {
        "name": name,
        "edge_count": len(graph.edges),
        "label_count": len(rows),
        "residual_state_evaluations": (
            2 * len(rows) * 3 ** len(graph.edges)
        ),
        "rows": rows,
        "pass": all(row["all_equal"] for row in rows),
    }


def allocation_result_record(result) -> dict[str, Any]:
    return {
        "value": fraction_record(result.value),
        "cycle_totals": [
            list(totals) for totals in result.cycle_totals
        ],
        "transitions_evaluated": result.transitions_evaluated,
    }


def dp_record(name: str, raw: dict[str, Any]) -> dict[str, Any]:
    lengths = tuple(int(value) for value in raw["cycle_lengths"])
    epsilon = Fraction(raw["epsilon"])
    dynamic = optimize_cactus_dp(
        lengths,
        int(raw["total_budget"]),
        epsilon,
        int(raw["bridge_count"]),
    )
    exhaustive = optimize_cycle_totals_exhaustive(
        lengths,
        int(raw["total_budget"]),
        epsilon,
        int(raw["bridge_count"]),
    )
    return {
        "name": name,
        "cycle_lengths": list(lengths),
        "bridge_count": int(raw["bridge_count"]),
        "total_budget": int(raw["total_budget"]),
        "epsilon": raw["epsilon"],
        "dynamic": allocation_result_record(dynamic),
        "exhaustive": allocation_result_record(exhaustive),
        "value_equal": dynamic.value == exhaustive.value,
        "optimizers_equal": (
            dynamic.cycle_totals == exhaustive.cycle_totals
        ),
    }


def all_edge_record(raw: dict[str, Any]) -> dict[str, Any]:
    lengths = tuple(int(value) for value in raw["cycle_lengths"])
    bridges = int(raw["bridge_count"])
    total = int(raw["total_budget"])
    epsilon = Fraction(raw["epsilon"])
    graph = bouquet_cactus(lengths, bridges)
    direct_value, direct_optimizers = optimize_all_edges_exhaustive(
        graph, total, epsilon
    )
    dynamic = optimize_cactus_dp(lengths, total, epsilon, bridges)
    induced_totals = {
        tuple(
            sum(counts[index] for index in block)
            for block in graph.cycle_blocks
        )
        for counts in direct_optimizers
    }
    bridges_at_floor = all(
        all(counts[index] == 1 for index in graph.bridge_indices)
        for counts in direct_optimizers
    )
    cycles_balanced = all(
        all(
            max(counts[index] for index in block)
            - min(counts[index] for index in block)
            <= 1
            for block in graph.cycle_blocks
        )
        for counts in direct_optimizers
    )
    return {
        "cycle_lengths": list(lengths),
        "bridge_count": bridges,
        "total_budget": total,
        "epsilon": raw["epsilon"],
        "allocation_count": sum(
            1
            for _ in _positive_compositions(total, len(graph.edges))
        ),
        "direct_value": fraction_record(direct_value),
        "dynamic": allocation_result_record(dynamic),
        "direct_optimizer_count": len(direct_optimizers),
        "direct_optimizers": [
            list(counts) for counts in direct_optimizers
        ],
        "induced_cycle_totals": [
            list(totals) for totals in sorted(induced_totals)
        ],
        "bridges_at_floor": bridges_at_floor,
        "cycles_balanced": cycles_balanced,
        "value_equal": direct_value == dynamic.value,
        "totals_equal": induced_totals == set(dynamic.cycle_totals),
    }


def _positive_compositions(
    total: int, parts: int
) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for rest in _positive_compositions(total - first, parts - 1):
            yield (first,) + rest


def comparator_record(
    name: str, raw: dict[str, Any]
) -> dict[str, Any]:
    lengths = tuple(int(value) for value in raw["cycle_lengths"])
    epsilon = Fraction(raw["epsilon"])
    total = int(raw["total_budget"])
    bridges = int(raw["bridge_count"])
    dynamic = optimize_cactus_dp(lengths, total, epsilon, bridges)
    exhaustive = optimize_cycle_totals_exhaustive(
        lengths, total, epsilon, bridges
    )
    if bridges:
        raise ValueError("registered comparator cells have no bridges")
    greedy_totals = marginal_greedy_endpoints(lengths, total, epsilon)
    greedy_rows = [
        {
            "cycle_totals": list(totals),
            "value": fraction_record(
                allocation_value(lengths, totals, epsilon)
            ),
        }
        for totals in greedy_totals
    ]
    global_totals = globally_balanced_cycle_totals(lengths, total)
    global_rows = [
        {
            "cycle_totals": list(totals),
            "value": fraction_record(
                allocation_value(lengths, totals, epsilon)
            ),
        }
        for totals in global_totals
    ]
    best_greedy = max(
        Fraction(row["value"]["fraction"]) for row in greedy_rows
    )
    best_global = max(
        Fraction(row["value"]["fraction"]) for row in global_rows
    )
    return {
        "name": name,
        "cycle_lengths": list(lengths),
        "total_budget": total,
        "epsilon": raw["epsilon"],
        "dynamic": allocation_result_record(dynamic),
        "exhaustive": allocation_result_record(exhaustive),
        "greedy": greedy_rows,
        "globally_balanced": global_rows,
        "greedy_gap": fraction_record(dynamic.value - best_greedy),
        "globally_balanced_gap": fraction_record(
            dynamic.value - best_global
        ),
        "dp_exhaustive_equal": (
            dynamic.value == exhaustive.value
            and dynamic.cycle_totals == exhaustive.cycle_totals
        ),
    }


def regression_certificates() -> dict[str, Any]:
    greedy_lengths = (3, 3)
    greedy_epsilon = Fraction(1, 4)
    greedy_total = 10
    greedy_endpoints = marginal_greedy_endpoints(
        greedy_lengths, greedy_total, greedy_epsilon
    )
    greedy_optimum = optimize_cactus_dp(
        greedy_lengths, greedy_total, greedy_epsilon
    )
    greedy_value = max(
        allocation_value(greedy_lengths, totals, greedy_epsilon)
        for totals in greedy_endpoints
    )

    uniform_lengths = (3, 4)
    uniform_epsilon = Fraction(1, 10)
    uniform_total = 12
    global_totals = globally_balanced_cycle_totals(
        uniform_lengths, uniform_total
    )
    uniform_optimum = optimize_cactus_dp(
        uniform_lengths, uniform_total, uniform_epsilon
    )
    best_global = max(
        allocation_value(uniform_lengths, totals, uniform_epsilon)
        for totals in global_totals
    )
    return {
        "greedy": {
            "endpoints": [list(value) for value in greedy_endpoints],
            "optima": [
                list(value) for value in greedy_optimum.cycle_totals
            ],
            "greedy_value": fraction_record(greedy_value),
            "optimal_value": fraction_record(greedy_optimum.value),
            "gap": fraction_record(greedy_optimum.value - greedy_value),
            "pass": (
                greedy_endpoints == ((4, 6), (6, 4))
                and greedy_optimum.cycle_totals == ((5, 5),)
                and greedy_optimum.value - greedy_value
                == Fraction(45, 262144)
            ),
        },
        "finite_uniform": {
            "globally_balanced_totals": [
                list(value) for value in global_totals
            ],
            "optima": [
                list(value) for value in uniform_optimum.cycle_totals
            ],
            "best_global_value": fraction_record(best_global),
            "optimal_value": fraction_record(uniform_optimum.value),
            "gap": fraction_record(uniform_optimum.value - best_global),
            "pass": (
                uniform_optimum.cycle_totals == ((3, 9),)
                and uniform_optimum.value - best_global
                == Fraction(26235981, 125000000000)
            ),
        },
    }


def render_result(result: dict[str, Any]) -> str:
    gate_lines = "\n".join(
        f"- `{gate}`: **{'PASS' if passed else 'FAIL'}**"
        for gate, passed in result["gates"].items()
    )
    dp_lines = "\n".join(
        (
            f"- `{row['name']}`: value "
            f"`{row['dynamic']['value']['fraction']}`, totals "
            f"`{row['dynamic']['cycle_totals']}`"
        )
        for row in result["dp_cells"]
    )
    comparator_lines = "\n".join(
        (
            f"- `{row['name']}`: greedy gap "
            f"`{row['greedy_gap']['fraction']}`, globally-balanced gap "
            f"`{row['globally_balanced_gap']['fraction']}`"
        )
        for row in result["comparators"]
    )
    return f"""# ASMP-9 v0.19 finite cactus-design result

## Verdict

`{result['verdict']}`

## Gates

{gate_lines}

## Exact finite-budget cells

{dp_lines}

The full positive edge-allocation census evaluated
`{result['all_edge_census']['allocation_count']}` allocations. Its exact value
and optimizer-induced cycle totals match the Bellman recursion, every
optimizer leaves the bridge at its mandatory floor, and every cycle is
internally balanced.

## Fresh comparator classifications

{comparator_lines}

These gap signs were not gate directions. The gate required exact,
independently reproduced classifications.

## Interpretation

On a cactus cyclic core, full conditional quotient availability is a series
product of independent cycle-block availabilities. The finite design problem
therefore separates into balanced within-cycle counts and an exact integer
allocation over cycle totals.

That outer allocation is not licensed for one-step greedy optimization:
`log f_k(N)` lacks discrete concavity. Nor can v0.18's asymptotically uniform
cyclic-edge design be promoted to an every-budget rule. The exact finite
replacement is the registered Bellman recurrence.

Dynamic programming and reliability allocation are classical. The
ASMP-9-specific result is the reduction from conditional comparison-fiber
liveness to that classical object.

## Claim boundary

{result['claim_boundary']}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol", type=Path, default=HERE / "protocol_v0_19.json"
    )
    parser.add_argument(
        "--registration",
        type=Path,
        default=HERE / "registration_v0_19.json",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    started_at = utc_now()
    started = time.perf_counter()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"refusing nonempty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    protocol_path = args.protocol.resolve()
    registration_path = args.registration.resolve()
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    registration, registration_sha, seal_checks = validate_registration(
        registration_path, protocol_path
    )
    freshness = fresh_registry_checks(protocol)
    factorization = factorization_record(
        "fresh_figure_3_4",
        protocol["factorization_cells"]["fresh_figure_3_4"],
    )
    bridge = bridge_record(
        "fresh_figure_3_5_bridge",
        protocol["factorization_cells"]["fresh_figure_3_5_bridge"],
    )
    dp_rows = [
        dp_record(name, raw)
        for name, raw in protocol["dp_cells"].items()
    ]
    all_edge = all_edge_record(protocol["global_edge_census"])
    regressions = regression_certificates()
    comparators = [
        comparator_record(name, raw)
        for name, raw in protocol["comparator_cells"].items()
    ]

    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    gates = {
        "G0_registration_binding": all(seal_checks.values()),
        "G1_fresh_registry": freshness["pass"],
        "G2_exact_cactus_factorization": (
            factorization["mismatch_count"] == 0
            and bridge["pass"]
        ),
        "G3_bridge_irrelevance_and_floor": (
            bridge["pass"] and all_edge["bridges_at_floor"]
        ),
        "G4_dp_equals_independent_exhaustive_totals": all(
            row["value_equal"] and row["optimizers_equal"]
            for row in dp_rows
        ),
        "G5_dp_equals_all_edge_census": (
            all_edge["value_equal"]
            and all_edge["totals_equal"]
            and all_edge["cycles_balanced"]
            and all_edge["bridges_at_floor"]
        ),
        "G6_nonconcavity_and_comparator_certificates": (
            regressions["greedy"]["pass"]
            and regressions["finite_uniform"]["pass"]
        ),
        "G7_fresh_comparator_classification": (
            len(comparators) == len(protocol["comparator_cells"])
            and all(row["dp_exhaustive_equal"] for row in comparators)
        ),
        "G8_resource_and_scope": (
            elapsed <= float(protocol["resource_caps"]["wall_seconds"])
            and peak
            <= int(protocol["resource_caps"]["peak_resident_bytes"])
            and not bool(protocol["resource_caps"]["gpu_allowed"])
        ),
    }
    verdict = (
        "finite_budget_cactus_dp_established_in_frozen_model"
        if all(gates.values())
        else "finite_budget_cactus_dp_not_established"
    )
    result = {
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": sha256(protocol_path),
        "registration_id": registration["registration_id"],
        "registration_sha256": registration_sha,
        "execution_commit": git("rev-parse", "HEAD"),
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "elapsed_seconds": elapsed,
        "peak_resident_bytes": peak,
        "gpu_used": False,
        "freshness": freshness,
        "seal_checks": seal_checks,
        "factorization": factorization,
        "bridge": bridge,
        "dp_cells": dp_rows,
        "all_edge_census": all_edge,
        "regression_certificates": regressions,
        "comparators": comparators,
        "gates": gates,
        "verdict": verdict,
        "claim_boundary": protocol["claim_boundary"],
    }
    result_path = output / "result_v0_19.json"
    report_path = output / "RESULT_v0_19.md"
    write_json(result_path, result)
    write_text(report_path, render_result(result))
    receipt = {
        "protocol_sha256": sha256(protocol_path),
        "registration_sha256": registration_sha,
        "result_sha256": sha256(result_path),
        "report_sha256": sha256(report_path),
        "verdict": verdict,
        "gate_count": len(gates),
        "passed_gate_count": sum(gates.values()),
        "elapsed_seconds": elapsed,
        "peak_resident_bytes": peak,
    }
    write_json(output / "run_receipt_v0_19.json", receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
