from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import os
import platform
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CONDITIONAL = HERE.parent / "conditional_fiber_v0_13"
sys.path.insert(0, str(HERE))
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
    connected_component_count,
    full_quotient_availability,
    full_quotient_available,
    graph_cycle_rank,
    minimal_bad_boundary_supports,
    positive_allocations,
    residual_cycle_edge_mask,
    theta_worst_endpoint_availability,
)


Edge = tuple[int, int]


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


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
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
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


def parse_fraction(text: str) -> Fraction:
    numerator, denominator = text.split("/")
    return Fraction(int(numerator), int(denominator))


def fraction_record(value: Fraction) -> dict[str, Any]:
    return {
        "fraction": f"{value.numerator}/{value.denominator}",
        "decimal": float(value),
    }


def graph_spec(
    protocol: dict[str, Any], name: str
) -> tuple[int, tuple[Edge, ...], int]:
    raw = protocol["graphs"][name]
    return (
        int(raw["node_count"]),
        tuple(tuple(edge) for edge in raw["edges"]),
        int(raw["expected_beta1"]),
    )


def status_vector(
    counts: Sequence[int], capacities: Sequence[int]
) -> tuple[int, ...]:
    return tuple(
        ZERO if count == 0 else FULL if count == capacity else INTERIOR
        for count, capacity in zip(counts, capacities, strict=True)
    )


def selected_cycle_rank(
    node_count: int,
    edges: Sequence[Edge],
    statuses: Sequence[int],
) -> int:
    mask = residual_cycle_edge_mask(node_count, edges, statuses)
    selected = tuple(
        edge for edge, keep in zip(edges, mask, strict=True) if keep
    )
    return (
        len(selected)
        - node_count
        + connected_component_count(node_count, selected)
    )


def canonical_graph_signature(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, int], ...]:
    best: tuple[tuple[int, int], ...] | None = None
    for permutation in itertools.permutations(range(node_count)):
        candidate = tuple(
            sorted(
                tuple(sorted((permutation[source], permutation[target])))
                for source, target in edges
            )
        )
        if best is None or candidate < best:
            best = candidate
    if best is None:
        raise AssertionError("empty graph signature")
    return best


def validate_registration(
    path: Path, registration: dict[str, Any]
) -> tuple[str, dict[str, bool]]:
    relative = path.resolve().relative_to(REPO).as_posix()
    registration_commit = git("log", "-1", "--format=%H", "--", relative)
    checks = {
        "head_is_registration_commit": (
            git("rev-parse", "HEAD") == registration_commit
        ),
        "tracked_tree_clean": not git(
            "status", "--porcelain", "--untracked-files=no"
        ),
        "implementation_is_ancestor": subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                registration["implementation_commit"],
                registration_commit,
            ],
            cwd=REPO,
            check=False,
        ).returncode
        == 0,
    }
    for relative_path, expected in registration["sealed_files"].items():
        checks[f"hash:{relative_path}"] = (
            sha256(REPO / relative_path) == expected
        )
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"registration validation failed: {failed!r}")
    return registration_commit, checks


def registry_record(protocol: dict[str, Any]) -> dict[str, Any]:
    residual_keys = [
        (row["graph"], tuple(capacities))
        for row in protocol["residual_rank_registry"]
        for capacities in row["capacity_vectors"]
    ]
    availability_keys = [
        (
            row["graph"],
            tuple(row["counts"]),
            tuple(row["probabilities"]),
        )
        for row in protocol["availability_registry"]
    ]
    support_keys = list(protocol["bad_support_certificates"])

    fresh_signatures = {}
    for name, raw in protocol["graphs"].items():
        fresh_signatures[name] = canonical_graph_signature(
            raw["node_count"], tuple(tuple(edge) for edge in raw["edges"])
        )
    burned_signatures = {}
    for name, raw in protocol["burned_graph_registry"].items():
        burned_signatures[name] = canonical_graph_signature(
            raw["node_count"], tuple(tuple(edge) for edge in raw["edges"])
        )
    collisions = sorted(
        (fresh, burned)
        for fresh, fresh_signature in fresh_signatures.items()
        for burned, burned_signature in burned_signatures.items()
        if fresh_signature == burned_signature
    )
    return {
        "residual_cell_count": len(residual_keys),
        "residual_unique_count": len(set(residual_keys)),
        "availability_cell_count": len(availability_keys),
        "availability_unique_count": len(set(availability_keys)),
        "bad_support_cell_count": len(support_keys),
        "bad_support_unique_count": len(set(support_keys)),
        "fresh_graph_count": len(fresh_signatures),
        "burned_graph_count": len(burned_signatures),
        "isomorphic_fresh_burned_collisions": collisions,
        "finite_counterexample_count": int(
            bool(protocol.get("finite_counterexample"))
        ),
    }


def residual_rank_records(
    protocol: dict[str, Any]
) -> list[dict[str, Any]]:
    records = []
    for row in protocol["residual_rank_registry"]:
        node_count, edges, beta1 = graph_spec(protocol, row["graph"])
        rows = incidence_rows(node_count, edges)
        for capacities_raw in row["capacity_vectors"]:
            capacities = tuple(int(value) for value in capacities_raw)
            fibers = enumerate_fibers(capacities, rows)
            mismatch_count = 0
            representative_failure_count = 0
            state_count = 0
            rank_histogram: Counter[int] = Counter()
            mismatch_examples = []
            for balance, fiber in sorted(fibers.items()):
                direct_rank = fiber_affine_rank(fiber)
                rank_histogram[direct_rank] += 1
                predicted_ranks = set()
                for counts in fiber:
                    statuses = status_vector(counts, capacities)
                    predicted = selected_cycle_rank(
                        node_count, edges, statuses
                    )
                    predicted_ranks.add(predicted)
                    state_count += 1
                    if predicted != direct_rank:
                        mismatch_count += 1
                        if len(mismatch_examples) < 5:
                            mismatch_examples.append(
                                {
                                    "balance": list(balance),
                                    "counts": list(counts),
                                    "direct_rank": direct_rank,
                                    "residual_rank": predicted,
                                }
                            )
                representative_failure_count += int(
                    predicted_ranks != {direct_rank}
                )
            records.append(
                {
                    "graph": row["graph"],
                    "capacities": list(capacities),
                    "graph_beta1": beta1,
                    "fiber_count": len(fibers),
                    "state_count": state_count,
                    "rank_histogram": {
                        str(rank): count
                        for rank, count in sorted(rank_histogram.items())
                    },
                    "mismatch_count": mismatch_count,
                    "representative_invariance_failure_count": (
                        representative_failure_count
                    ),
                    "mismatch_examples": mismatch_examples,
                }
            )
    return records


def count_probability(
    counts: Sequence[int],
    capacities: Sequence[int],
    probabilities: Sequence[Fraction],
) -> Fraction:
    mass = Fraction(1)
    for count, capacity, probability in zip(
        counts, capacities, probabilities, strict=True
    ):
        mass *= (
            comb(capacity, count)
            * probability**count
            * (1 - probability) ** (capacity - count)
        )
    return mass


def availability_records(
    protocol: dict[str, Any]
) -> list[dict[str, Any]]:
    records = []
    for row in protocol["availability_registry"]:
        node_count, edges, beta1 = graph_spec(protocol, row["graph"])
        capacities = tuple(int(value) for value in row["counts"])
        probabilities = tuple(
            parse_fraction(value) for value in row["probabilities"]
        )
        rows = incidence_rows(node_count, edges)
        fibers = enumerate_fibers(capacities, rows)
        raw = Fraction(0)
        raw_state_count = 0
        for fiber in fibers.values():
            direct_rank = fiber_affine_rank(fiber)
            for counts in fiber:
                raw_state_count += 1
                if direct_rank == beta1:
                    raw += count_probability(
                        counts, capacities, probabilities
                    )
        compressed = full_quotient_availability(
            node_count, edges, capacities, probabilities
        )
        records.append(
            {
                "graph": row["graph"],
                "counts": list(capacities),
                "probabilities": [
                    fraction_record(value) for value in probabilities
                ],
                "raw_state_count": raw_state_count,
                "raw_full_rank_probability": fraction_record(raw),
                "ternary_full_rank_probability": fraction_record(
                    compressed
                ),
                "exact_match": raw == compressed,
            }
        )
    return records


def endpoint_monotonicity_records(
    protocol: dict[str, Any]
) -> list[dict[str, Any]]:
    records = []
    for name in sorted(protocol["graphs"]):
        node_count, edges, _ = graph_spec(protocol, name)
        checked = 0
        violation_count = 0
        violations = []
        for selected_edge in range(len(edges)):
            other_edges = [
                edge for edge in range(len(edges)) if edge != selected_edge
            ]
            for other_statuses in itertools.product(
                (ZERO, INTERIOR, FULL), repeat=len(other_edges)
            ):
                template = [INTERIOR] * len(edges)
                for edge, status in zip(
                    other_edges, other_statuses, strict=True
                ):
                    template[edge] = status
                values = {}
                for status in (ZERO, INTERIOR, FULL):
                    candidate = list(template)
                    candidate[selected_edge] = status
                    values[status] = full_quotient_available(
                        node_count, edges, candidate
                    )
                checked += 2
                if (
                    (values[ZERO] and not values[INTERIOR])
                    or (values[FULL] and not values[INTERIOR])
                ):
                    violation_count += 1
                    if len(violations) < 5:
                        violations.append(
                            {
                                "edge": selected_edge,
                                "other_statuses": list(other_statuses),
                                "values": {
                                    str(key): value
                                    for key, value in values.items()
                                },
                            }
                        )
        records.append(
            {
                "graph": name,
                "comparison_count": checked,
                "violation_count": violation_count,
                "violation_examples": violations,
                "coefficients_nonnegative": violation_count == 0,
            }
        )
    return records


def support_minimality(
    node_count: int,
    edges: Sequence[Edge],
    support: Sequence[int],
) -> dict[str, Any]:
    bad_orientations = []
    for orientation in itertools.product((ZERO, FULL), repeat=len(support)):
        statuses = [INTERIOR] * len(edges)
        for edge, status in zip(support, orientation, strict=True):
            statuses[edge] = status
        if not full_quotient_available(node_count, edges, statuses):
            bad_orientations.append(list(orientation))

    proper_bad = []
    for size in range(len(support)):
        for subset in itertools.combinations(support, size):
            for orientation in itertools.product(
                (ZERO, FULL), repeat=len(subset)
            ):
                statuses = [INTERIOR] * len(edges)
                for edge, status in zip(
                    subset, orientation, strict=True
                ):
                    statuses[edge] = status
                if not full_quotient_available(
                    node_count, edges, statuses
                ):
                    proper_bad.append(
                        {
                            "subset": list(subset),
                            "orientation": list(orientation),
                        }
                    )
    return {
        "support": list(support),
        "bad_orientation_count": len(bad_orientations),
        "first_bad_orientation": (
            bad_orientations[0] if bad_orientations else None
        ),
        "proper_subset_bad_count": len(proper_bad),
    }


def bad_support_records(
    protocol: dict[str, Any]
) -> list[dict[str, Any]]:
    records = []
    for name, certificate in protocol[
        "bad_support_certificates"
    ].items():
        node_count, edges, _ = graph_spec(protocol, name)
        actual = minimal_bad_boundary_supports(node_count, edges)
        expected = tuple(
            tuple(support)
            for support in certificate["expected_supports"]
        )
        minimality = [
            support_minimality(node_count, edges, support)
            for support in actual
        ]
        records.append(
            {
                "graph": name,
                "actual_supports": [list(value) for value in actual],
                "expected_supports": [
                    list(value) for value in expected
                ],
                "support_count": len(actual),
                "exact_support_match": actual == expected,
                "all_have_bad_orientation": all(
                    row["bad_orientation_count"] > 0
                    for row in minimality
                ),
                "all_proper_subsets_live": all(
                    row["proper_subset_bad_count"] == 0
                    for row in minimality
                ),
                "minimality_records": minimality,
            }
        )
    return records


def exponent_certificate_records(
    protocol: dict[str, Any]
) -> list[dict[str, Any]]:
    records = []
    for name, certificate in protocol[
        "bad_support_certificates"
    ].items():
        _, edges, _ = graph_spec(protocol, name)
        supports = tuple(
            tuple(value) for value in certificate["expected_supports"]
        )
        threshold = parse_fraction(certificate["threshold"])
        primal = tuple(
            parse_fraction(value)
            for value in certificate["primal_weights"]
        )
        dual_rows = [
            (
                tuple(row["support"]),
                parse_fraction(row["mass"]),
            )
            for row in certificate["dual_distribution"]
        ]
        primal_support_sums = tuple(
            sum((primal[edge] for edge in support), Fraction(0))
            for support in supports
        )
        dual_edge_loads = tuple(
            sum(
                (
                    mass
                    for support, mass in dual_rows
                    if edge in support
                ),
                Fraction(0),
            )
            for edge in range(len(edges))
        )
        records.append(
            {
                "graph": name,
                "threshold": fraction_record(threshold),
                "primal_weights": [
                    fraction_record(value) for value in primal
                ],
                "primal_support_sums": [
                    fraction_record(value)
                    for value in primal_support_sums
                ],
                "dual_distribution": [
                    {
                        "support": list(support),
                        "mass": fraction_record(mass),
                    }
                    for support, mass in dual_rows
                ],
                "dual_edge_loads": [
                    fraction_record(value) for value in dual_edge_loads
                ],
                "primal_feasible": (
                    len(primal) == len(edges)
                    and all(value >= 0 for value in primal)
                    and sum(primal, Fraction(0)) == 1
                    and min(primal_support_sums) >= threshold
                ),
                "dual_feasible": (
                    all(mass >= 0 for _, mass in dual_rows)
                    and sum(
                        (mass for _, mass in dual_rows), Fraction(0)
                    )
                    == 1
                    and set(support for support, _ in dual_rows)
                    <= set(supports)
                    and max(dual_edge_loads) <= threshold
                ),
                "matching_value": (
                    min(primal_support_sums)
                    == max(dual_edge_loads)
                    == threshold
                ),
            }
        )
    return records


def finite_counterexample_record(
    protocol: dict[str, Any]
) -> dict[str, Any]:
    registered = protocol["finite_counterexample"]
    paths = tuple(tuple(path) for path in registered["paths"])
    total = int(registered["total_trials"])
    epsilon = parse_fraction(registered["epsilon"])
    uniform = tuple(registered["uniform_allocation"])

    digest = hashlib.sha256()
    allocation_count = 0
    optimum: Fraction | None = None
    optimizers: list[tuple[int, ...]] = []
    for counts in positive_allocations(total, len(uniform)):
        value, witnesses = theta_worst_endpoint_availability(
            paths, counts, epsilon
        )
        allocation_count += 1
        line = (
            ",".join(str(value) for value in counts)
            + f"|{value.numerator}/{value.denominator}|"
            + ";".join("".join(map(str, witness)) for witness in witnesses)
            + "\n"
        )
        digest.update(line.encode("ascii"))
        if optimum is None or value > optimum:
            optimum = value
            optimizers = [counts]
        elif value == optimum:
            optimizers.append(counts)
    if optimum is None:
        raise AssertionError("empty allocation universe")
    uniform_value, uniform_witnesses = (
        theta_worst_endpoint_availability(paths, uniform, epsilon)
    )
    return {
        "graph": registered["graph"],
        "paths": [list(path) for path in paths],
        "total_trials": total,
        "epsilon": fraction_record(epsilon),
        "allocation_count": allocation_count,
        "allocation_value_digest_sha256": digest.hexdigest(),
        "uniform_allocation": list(uniform),
        "uniform_value": fraction_record(uniform_value),
        "uniform_witness_count": len(uniform_witnesses),
        "optimum": fraction_record(optimum),
        "optimizers": [list(value) for value in optimizers],
        "optimizer_count": len(optimizers),
        "balanced_optimizer_count": sum(
            max(value) - min(value) <= 1 for value in optimizers
        ),
        "strictly_beats_uniform": optimum > uniform_value,
    }


def evaluate_gates(
    *,
    protocol: dict[str, Any],
    binding: dict[str, bool],
    registry: dict[str, Any],
    residual: list[dict[str, Any]],
    availability: list[dict[str, Any]],
    endpoint: list[dict[str, Any]],
    supports: list[dict[str, Any]],
    exponents: list[dict[str, Any]],
    finite: dict[str, Any],
    elapsed_seconds: float,
    peak_bytes: int,
) -> dict[str, bool]:
    caps = protocol["resource_caps"]
    gates = {
        "G0_registration_binding": all(binding.values()),
        "G1_registry_completeness": (
            registry["residual_cell_count"]
            == registry["residual_unique_count"]
            == 6
            and registry["availability_cell_count"]
            == registry["availability_unique_count"]
            == 3
            and registry["bad_support_cell_count"]
            == registry["bad_support_unique_count"]
            == 3
            and registry["finite_counterexample_count"] == 1
            and not registry["isomorphic_fresh_burned_collisions"]
        ),
        "G2_residual_rank_identity": (
            len(residual) == 6
            and all(row["mismatch_count"] == 0 for row in residual)
        ),
        "G3_representative_invariance": (
            len(residual) == 6
            and all(
                row["representative_invariance_failure_count"] == 0
                for row in residual
            )
        ),
        "G4_three_state_exactness": (
            len(availability) == 3
            and all(row["exact_match"] for row in availability)
        ),
        "G5_endpoint_reduction": (
            len(endpoint) == len(protocol["graphs"])
            and all(
                row["violation_count"] == 0
                and row["coefficients_nonnegative"]
                for row in endpoint
            )
        ),
        "G6_bad_support_completeness": (
            len(supports) == 3
            and all(
                row["exact_support_match"]
                and row["all_have_bad_orientation"]
                and row["all_proper_subsets_live"]
                for row in supports
            )
        ),
        "G7_primal_dual_exponent_certificates": (
            len(exponents) == 3
            and all(
                row["primal_feasible"]
                and row["dual_feasible"]
                and row["matching_value"]
                for row in exponents
            )
        ),
        "G8_finite_nonuniform_counterexample": (
            finite["allocation_count"] == 1716
            and finite["strictly_beats_uniform"]
            and finite["balanced_optimizer_count"] == 0
        ),
        "G9_resource_and_scope": (
            not caps["gpu_allowed"]
            and elapsed_seconds <= caps["wall_seconds"]
            and peak_bytes <= caps["peak_resident_bytes"]
            and bool(protocol["claim_boundary"])
        ),
    }
    if list(gates) != protocol["gate_ids"]:
        raise RuntimeError("runtime gate universe differs from protocol")
    return gates


def render_report(result: dict[str, Any]) -> str:
    gate_rows = "\n".join(
        f"- `{name}`: **{'PASS' if passed else 'FAIL'}**"
        for name, passed in result["gates"].items()
    )
    availability_rows = "\n".join(
        "| {graph} | {raw} | {compressed} | {match} |".format(
            graph=row["graph"],
            raw=row["raw_full_rank_probability"]["fraction"],
            compressed=row["ternary_full_rank_probability"]["fraction"],
            match="yes" if row["exact_match"] else "no",
        )
        for row in result["availability_records"]
    )
    exponent_rows = "\n".join(
        "| {graph} | {threshold} | {primal} | {dual} |".format(
            graph=row["graph"],
            threshold=row["threshold"]["fraction"],
            primal="yes" if row["primal_feasible"] else "no",
            dual="yes" if row["dual_feasible"] else "no",
        )
        for row in result["exponent_certificate_records"]
    )
    finite = result["finite_counterexample"]
    return f"""# ASMP-9 general comparison-graph allocation v0.17 result

## Verdict

`{result["verdict"]}`

## Gates

{gate_rows}

## Residual-cycle theorem checks

- fresh capacity cells: {len(result["residual_rank_records"])}
- realized count representatives: {result["summary"]["residual_state_count"]}
- conditional fibers: {result["summary"]["residual_fiber_count"]}
- residual-rank mismatches: {result["summary"]["residual_mismatch_count"]}
- representative-invariance failures: {result["summary"]["representative_failure_count"]}

## Exact ternary compression

| graph | raw binomial enumeration | ternary status polynomial | exact |
| --- | ---: | ---: | :---: |
{availability_rows}

## Bad-support exponent certificates

| graph | `tau_G*` | primal feasible | dual feasible |
| --- | ---: | :---: | :---: |
{exponent_rows}

## Prospective finite counterexample

- graph: theta `(1,3,3)`
- total trials: {finite["total_trials"]}
- positive labelled allocations: {finite["allocation_count"]}
- uniform value: `{finite["uniform_value"]["fraction"]}`
- exact optimum: `{finite["optimum"]["fraction"]}`
- optimizer count: {finite["optimizer_count"]}
- balanced optimizer count: {finite["balanced_optimizer_count"]}
- complete allocation/value digest: `{finite["allocation_value_digest_sha256"]}`

## Interpretation

The result tests whether the one-cycle balancing theorem transfers to graphs
with several cycle directions. The large-deviation allocation is certified
by a finite hypergraph game over minimal bad boundary supports; the finite
theta census is a separately registered stress test. A pass or failure is
about this exact independent Bernoulli comparison model only.

## Resources

- elapsed seconds: {result["resources"]["elapsed_seconds"]:.6f}
- peak resident bytes: {result["resources"]["peak_resident_bytes"]}
- GPU used: false

## Claim boundary

{result["claim_boundary"]}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(
            f"refusing to overwrite output directory: {args.output_dir}"
        )

    started = time.perf_counter()
    registration_path = args.registration.resolve()
    registration = json.loads(
        registration_path.read_text(encoding="utf-8")
    )
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )

    args.output_dir.mkdir(parents=True, exist_ok=False)
    start_path = args.output_dir / "start_v0_17.json"
    progress_path = args.output_dir / "progress_v0_17.json"
    abort_path = args.output_dir / "abort_v0_17.json"
    write_json(
        start_path,
        {
            "protocol_id": protocol["protocol_id"],
            "registration_sha256": sha256(registration_path),
            "started_at_utc": utc_now(),
            "status": "started",
            "resource_caps": protocol["resource_caps"],
        },
    )
    completed_stages: list[str] = []

    def write_progress(stage: str, status: str = "running") -> None:
        write_json(
            progress_path,
            {
                "protocol_id": protocol["protocol_id"],
                "status": status,
                "stage": stage,
                "completed_stages": completed_stages,
                "elapsed_seconds": time.perf_counter() - started,
                "peak_resident_bytes": peak_resident_bytes(),
            },
        )

    def finish_stage(stage: str) -> None:
        completed_stages.append(stage)
        write_progress(stage)
        caps = protocol["resource_caps"]
        elapsed = time.perf_counter() - started
        peak = peak_resident_bytes()
        if (
            elapsed > caps["wall_seconds"]
            or peak > caps["peak_resident_bytes"]
        ):
            raise RuntimeError(
                f"resource cap exceeded after {stage}: "
                f"elapsed={elapsed}, peak={peak}"
            )

    registration_commit = ""
    try:
        write_progress("registration_binding")
        registration_commit, binding = validate_registration(
            registration_path, registration
        )
        finish_stage("registration_binding")

        registry = registry_record(protocol)
        finish_stage("registry_completeness")

        residual = residual_rank_records(protocol)
        finish_stage("residual_rank")

        availability = availability_records(protocol)
        finish_stage("three_state_compression")

        endpoint = endpoint_monotonicity_records(protocol)
        finish_stage("endpoint_reduction")

        supports = bad_support_records(protocol)
        finish_stage("bad_supports")

        exponents = exponent_certificate_records(protocol)
        finish_stage("exponent_certificates")

        finite = finite_counterexample_record(protocol)
        finish_stage("finite_counterexample")

        elapsed = time.perf_counter() - started
        peak = peak_resident_bytes()
        gates = evaluate_gates(
            protocol=protocol,
            binding=binding,
            registry=registry,
            residual=residual,
            availability=availability,
            endpoint=endpoint,
            supports=supports,
            exponents=exponents,
            finite=finite,
            elapsed_seconds=elapsed,
            peak_bytes=peak,
        )
        verdict = (
            "registered_exact_result_passed"
            if all(gates.values())
            else "registered_exact_result_failed"
        )
        result = {
            "protocol_id": protocol["protocol_id"],
            "registration_commit": registration_commit,
            "registration_sha256": sha256(registration_path),
            "implementation_commit": registration[
                "implementation_commit"
            ],
            "verdict": verdict,
            "gates": gates,
            "binding_checks": binding,
            "registry_record": registry,
            "residual_rank_records": residual,
            "availability_records": availability,
            "endpoint_monotonicity_records": endpoint,
            "bad_support_records": supports,
            "exponent_certificate_records": exponents,
            "finite_counterexample": finite,
            "summary": {
                "residual_state_count": sum(
                    row["state_count"] for row in residual
                ),
                "residual_fiber_count": sum(
                    row["fiber_count"] for row in residual
                ),
                "residual_mismatch_count": sum(
                    row["mismatch_count"] for row in residual
                ),
                "representative_failure_count": sum(
                    row["representative_invariance_failure_count"]
                    for row in residual
                ),
                "endpoint_comparison_count": sum(
                    row["comparison_count"] for row in endpoint
                ),
                "bad_support_count": sum(
                    row["support_count"] for row in supports
                ),
            },
            "resources": {
                "elapsed_seconds": elapsed,
                "peak_resident_bytes": peak,
                "gpu_used": False,
            },
            "claim_boundary": protocol["claim_boundary"],
        }
        result_path = args.output_dir / "result_v0_17.json"
        report_path = args.output_dir / "RESULT_v0_17.md"
        write_json(result_path, result)
        write_text(report_path, render_report(result))
        finish_stage("result_and_report")
        write_progress("completed", status="completed")

        final_elapsed = time.perf_counter() - started
        final_peak = peak_resident_bytes()
        caps = protocol["resource_caps"]
        if (
            final_elapsed > caps["wall_seconds"]
            or final_peak > caps["peak_resident_bytes"]
        ):
            raise RuntimeError(
                "resource cap exceeded before receipt: "
                f"elapsed={final_elapsed}, peak={final_peak}"
            )
        receipt = {
            "protocol_id": protocol["protocol_id"],
            "registration_commit": registration_commit,
            "registration_sha256": sha256(registration_path),
            "implementation_commit": registration[
                "implementation_commit"
            ],
            "verdict": verdict,
            "output_hashes": {
                result_path.name: sha256(result_path),
                report_path.name: sha256(report_path),
                start_path.name: sha256(start_path),
                progress_path.name: sha256(progress_path),
            },
            "resources": {
                "elapsed_seconds": final_elapsed,
                "peak_resident_bytes": final_peak,
                "gpu_used": False,
            },
        }
        write_json(args.output_dir / "receipt_v0_17.json", receipt)
        print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
        raise SystemExit(0 if all(gates.values()) else 1)
    except SystemExit:
        raise
    except BaseException as error:
        write_json(
            abort_path,
            {
                "protocol_id": protocol["protocol_id"],
                "registration_commit": registration_commit or None,
                "status": "aborted",
                "error_type": type(error).__name__,
                "error": str(error),
                "completed_stages": completed_stages,
                "elapsed_seconds": time.perf_counter() - started,
                "peak_resident_bytes": peak_resident_bytes(),
            },
        )
        write_progress("aborted", status="aborted")
        raise


if __name__ == "__main__":
    main()
