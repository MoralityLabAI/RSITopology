from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import os
import platform
import subprocess
import time
from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

from block_factorization import Edge, PreparedGraph


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ZERO = 0
INTERIOR = 1
FULL = 2

_LIVE_CACHE: dict[
    tuple[int, tuple[Edge, ...], str],
    tuple[tuple[int, ...], ...],
] = {}
_WORST_CACHE: dict[
    tuple[
        int,
        tuple[Edge, ...],
        tuple[int, ...],
        int,
        int,
    ],
    tuple[Fraction, tuple[tuple[int, ...], ...]],
] = {}


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def write_json_exclusive(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(
            json.dumps(value, indent=2, sort_keys=True) + "\n"
        )


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


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


def graph_from_raw(raw: dict[str, Any]) -> PreparedGraph:
    return PreparedGraph.build(
        int(raw["node_count"]),
        tuple(tuple(edge) for edge in raw["edges"]),
    )


def component_count(
    node_count: int,
    edges: Sequence[Edge],
    excluded: int | None = None,
) -> int:
    adjacency = [[] for _ in range(node_count)]
    for edge_id, (source, target) in enumerate(edges):
        if edge_id == excluded:
            continue
        adjacency[source].append(target)
        adjacency[target].append(source)
    seen: set[int] = set()
    count = 0
    for root in range(node_count):
        if root in seen:
            continue
        count += 1
        seen.add(root)
        stack = [root]
        while stack:
            node = stack.pop()
            for target in adjacency[node]:
                if target not in seen:
                    seen.add(target)
                    stack.append(target)
    return count


def independent_bridges(
    node_count: int, edges: Sequence[Edge]
) -> frozenset[int]:
    base = component_count(node_count, edges)
    return frozenset(
        edge_id
        for edge_id in range(len(edges))
        if component_count(node_count, edges, edge_id) > base
    )


def brute_cycle_blocks(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    """Independent exponential edge-block oracle for small graphs."""

    parent = list(range(len(edges)))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for mask in range(1 << len(edges)):
        selected = tuple(
            edge_id
            for edge_id in range(len(edges))
            if mask & (1 << edge_id)
        )
        if len(selected) < 3:
            continue
        degrees = [0] * node_count
        adjacency = [[] for _ in range(node_count)]
        for edge_id in selected:
            source, target = edges[edge_id]
            degrees[source] += 1
            degrees[target] += 1
            adjacency[source].append(target)
            adjacency[target].append(source)
        vertices = {
            node for node, degree in enumerate(degrees) if degree
        }
        if (
            len(vertices) != len(selected)
            or any(degrees[node] != 2 for node in vertices)
        ):
            continue
        root = next(iter(vertices))
        seen = {root}
        stack = [root]
        while stack:
            node = stack.pop()
            for target in adjacency[node]:
                if target not in seen:
                    seen.add(target)
                    stack.append(target)
        if seen != vertices:
            continue
        for edge_id in selected[1:]:
            union(selected[0], edge_id)

    groups: dict[int, list[int]] = {}
    for edge_id in range(len(edges)):
        groups.setdefault(find(edge_id), []).append(edge_id)
    return tuple(
        sorted(
            (tuple(sorted(group)) for group in groups.values()),
            key=lambda block: (min(block), block),
        )
    )


def reachability(
    node_count: int,
    edges: Sequence[Edge],
    statuses: Sequence[int],
    edge_ids: Sequence[int] | None = None,
) -> tuple[int, ...]:
    selected: Iterable[int] = (
        range(len(edges)) if edge_ids is None else edge_ids
    )
    reach = [1 << node for node in range(node_count)]
    for edge_id in selected:
        source, target = edges[edge_id]
        status = statuses[edge_id]
        if status in (ZERO, INTERIOR):
            reach[source] |= 1 << target
        if status in (INTERIOR, FULL):
            reach[target] |= 1 << source
    for intermediate in range(node_count):
        flag = 1 << intermediate
        for source in range(node_count):
            if reach[source] & flag:
                reach[source] |= reach[intermediate]
    return tuple(reach)


def independent_direct_available(
    prepared: PreparedGraph, statuses: Sequence[int]
) -> bool:
    bridges = independent_bridges(
        prepared.node_count, prepared.edges
    )
    reach = reachability(
        prepared.node_count, prepared.edges, statuses
    )
    return all(
        edge_id in bridges
        or (
            reach[source] & (1 << target)
            and reach[target] & (1 << source)
        )
        for edge_id, (source, target) in enumerate(prepared.edges)
    )


def independent_block_available(
    prepared: PreparedGraph,
    blocks: Sequence[Sequence[int]],
    statuses: Sequence[int],
) -> bool:
    for block in blocks:
        if len(block) == 1:
            continue
        vertices = {
            vertex
            for edge_id in block
            for vertex in prepared.edges[edge_id]
        }
        reach = reachability(
            prepared.node_count,
            prepared.edges,
            statuses,
            block,
        )
        root = next(iter(vertices))
        if any(
            not (reach[root] & (1 << vertex))
            or not (reach[vertex] & (1 << root))
            for vertex in vertices
        ):
            return False
    return True


def live_states(
    prepared: PreparedGraph, mode: str
) -> tuple[tuple[int, ...], ...]:
    key = (prepared.node_count, prepared.edges, mode)
    if key not in _LIVE_CACHE:
        if mode == "direct":
            predicate = prepared.direct_available
        elif mode == "blockwise":
            predicate = prepared.blockwise_available
        else:
            raise ValueError(f"unknown liveness mode: {mode}")
        _LIVE_CACHE[key] = tuple(
            statuses
            for statuses in itertools.product(
                (ZERO, INTERIOR, FULL),
                repeat=len(prepared.edges),
            )
            if predicate(statuses)
        )
    return _LIVE_CACHE[key]


def status_integer_weights(
    count: int, label: int, epsilon: Fraction
) -> tuple[int, int, int]:
    denominator = epsilon.denominator
    probability = (
        epsilon.numerator
        if label == 0
        else denominator - epsilon.numerator
    )
    zero = (denominator - probability) ** count
    full = probability**count
    return zero, denominator**count - zero - full, full


def exact_availability(
    prepared: PreparedGraph,
    counts: Sequence[int],
    labels: Sequence[int],
    epsilon: Fraction,
    *,
    mode: str = "direct",
) -> Fraction:
    if len(counts) != len(prepared.edges):
        raise ValueError("count vector does not cover every edge")
    if len(labels) != len(prepared.edges):
        raise ValueError("label vector does not cover every edge")
    if any(count < 1 for count in counts):
        raise ValueError("every edge count must be positive")
    weights = tuple(
        status_integer_weights(count, label, epsilon)
        for count, label in zip(counts, labels, strict=True)
    )
    numerator = 0
    for statuses in live_states(prepared, mode):
        mass = 1
        for edge_id, status in enumerate(statuses):
            mass *= weights[edge_id][status]
        numerator += mass
    denominator = epsilon.denominator ** sum(counts)
    return Fraction(numerator, denominator)


def local_prepared(
    prepared: PreparedGraph, block: Sequence[int]
) -> PreparedGraph:
    vertices = sorted(
        {
            vertex
            for edge_id in block
            for vertex in prepared.edges[edge_id]
        }
    )
    local = {vertex: index for index, vertex in enumerate(vertices)}
    edges = tuple(
        (
            local[prepared.edges[edge_id][0]],
            local[prepared.edges[edge_id][1]],
        )
        for edge_id in block
    )
    return PreparedGraph.build(len(vertices), edges)


def product_availability(
    prepared: PreparedGraph,
    counts: Sequence[int],
    labels: Sequence[int],
    epsilon: Fraction,
) -> tuple[Fraction, tuple[dict[str, Any], ...]]:
    product = Fraction(1)
    rows = []
    for block in prepared.cyclic:
        local = local_prepared(prepared, block)
        local_counts = tuple(counts[index] for index in block)
        local_labels = tuple(labels[index] for index in block)
        value = exact_availability(
            local, local_counts, local_labels, epsilon
        )
        product *= value
        rows.append(
            {
                "edge_ids": list(block),
                "value": fraction_text(value),
            }
        )
    return product, tuple(rows)


def worst_endpoint(
    prepared: PreparedGraph,
    counts: Sequence[int],
    epsilon: Fraction,
) -> tuple[Fraction, tuple[tuple[int, ...], ...]]:
    key = (
        prepared.node_count,
        prepared.edges,
        tuple(counts),
        epsilon.numerator,
        epsilon.denominator,
    )
    if key in _WORST_CACHE:
        return _WORST_CACHE[key]
    best: Fraction | None = None
    witnesses: list[tuple[int, ...]] = []
    for labels in itertools.product(
        (0, 1), repeat=len(prepared.edges)
    ):
        value = exact_availability(
            prepared, counts, labels, epsilon
        )
        if best is None or value < best:
            best = value
            witnesses = [labels]
        elif value == best:
            witnesses.append(labels)
    if best is None:
        raise AssertionError("empty endpoint-label universe")
    result = best, tuple(witnesses)
    _WORST_CACHE[key] = result
    return result


def product_worst_endpoint(
    prepared: PreparedGraph,
    counts: Sequence[int],
    epsilon: Fraction,
) -> tuple[Fraction, tuple[dict[str, Any], ...]]:
    product = Fraction(1)
    rows = []
    for block in prepared.cyclic:
        local = local_prepared(prepared, block)
        value, witnesses = worst_endpoint(
            local,
            tuple(counts[index] for index in block),
            epsilon,
        )
        product *= value
        rows.append(
            {
                "edge_ids": list(block),
                "value": fraction_text(value),
                "witness_count": len(witnesses),
                "witnesses": [
                    "".join(str(item) for item in witness)
                    for witness in witnesses
                ],
            }
        )
    return product, tuple(rows)


def positive_compositions(
    total: int, parts: int
) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        if total >= 1:
            yield (total,)
        return
    for first in range(1, total - parts + 2):
        for tail in positive_compositions(
            total - first, parts - 1
        ):
            yield (first, *tail)


def local_design_table(
    prepared: PreparedGraph,
    block: Sequence[int],
    max_total: int,
    epsilon: Fraction,
) -> dict[int, tuple[Fraction, tuple[tuple[int, ...], ...]]]:
    local = local_prepared(prepared, block)
    result = {}
    for total in range(len(block), max_total + 1):
        best: Fraction | None = None
        optimizers: list[tuple[int, ...]] = []
        for counts in positive_compositions(total, len(block)):
            value, _ = worst_endpoint(local, counts, epsilon)
            if best is None or value > best:
                best = value
                optimizers = [counts]
            elif value == best:
                optimizers.append(counts)
        if best is None:
            raise AssertionError("empty local allocation universe")
        result[total] = best, tuple(optimizers)
    return result


def compose_global_counts(
    edge_count: int,
    blocks: Sequence[Sequence[int]],
    local_counts: Sequence[Sequence[int]],
) -> tuple[int, ...]:
    result = [0] * edge_count
    for block, counts in zip(blocks, local_counts, strict=True):
        for edge_id, count in zip(block, counts, strict=True):
            result[edge_id] = count
    if any(count < 1 for count in result):
        raise ValueError("design graph must have no bridge blocks")
    return tuple(result)


def design_comparison(
    prepared: PreparedGraph,
    total_budget: int,
    epsilon: Fraction,
) -> dict[str, Any]:
    if prepared.bridges:
        raise ValueError("registered design cell must be bridgeless")
    blocks = prepared.cyclic
    tables = [
        local_design_table(
            prepared,
            block,
            total_budget
            - sum(len(other) for other in blocks if other != block),
            epsilon,
        )
        for block in blocks
    ]

    states: dict[
        int,
        tuple[
            Fraction,
            tuple[tuple[tuple[int, ...], ...], ...],
        ],
    ] = {0: (Fraction(1), ((),))}
    for table in tables:
        successor: dict[
            int,
            tuple[
                Fraction,
                tuple[tuple[tuple[int, ...], ...], ...],
            ],
        ] = {}
        for used, (prefix_value, prefixes) in states.items():
            for local_total, (
                local_value,
                local_optimizers,
            ) in table.items():
                new_used = used + local_total
                if new_used > total_budget:
                    continue
                value = prefix_value * local_value
                candidates = tuple(
                    prefix + (optimizer,)
                    for prefix in prefixes
                    for optimizer in local_optimizers
                )
                current = successor.get(new_used)
                if current is None or value > current[0]:
                    successor[new_used] = value, candidates
                elif value == current[0]:
                    successor[new_used] = (
                        value,
                        current[1] + candidates,
                    )
        states = successor
    bellman_value, bellman_local = states[total_budget]
    bellman_optimizers = tuple(
        sorted(
            {
                compose_global_counts(
                    len(prepared.edges), blocks, local_counts
                )
                for local_counts in bellman_local
            }
        )
    )

    local_score_cache: dict[
        tuple[tuple[int, ...], tuple[int, ...]], Fraction
    ] = {}

    def local_score(
        block: tuple[int, ...], counts: tuple[int, ...]
    ) -> Fraction:
        key = block, counts
        if key not in local_score_cache:
            local = local_prepared(prepared, block)
            local_score_cache[key] = worst_endpoint(
                local, counts, epsilon
            )[0]
        return local_score_cache[key]

    exhaustive_best: Fraction | None = None
    exhaustive_optimizers: list[tuple[int, ...]] = []
    allocation_count = 0
    for counts in positive_compositions(
        total_budget, len(prepared.edges)
    ):
        allocation_count += 1
        value = Fraction(1)
        for block in blocks:
            value *= local_score(
                block, tuple(counts[index] for index in block)
            )
        if exhaustive_best is None or value > exhaustive_best:
            exhaustive_best = value
            exhaustive_optimizers = [counts]
        elif value == exhaustive_best:
            exhaustive_optimizers.append(counts)
    if exhaustive_best is None:
        raise AssertionError("empty global allocation universe")

    return {
        "total_budget": total_budget,
        "epsilon": fraction_text(epsilon),
        "allocation_count": allocation_count,
        "local_tables": [
            {
                str(total): {
                    "value": fraction_text(value),
                    "optimizers": [list(item) for item in optimizers],
                }
                for total, (value, optimizers) in table.items()
            }
            for table in tables
        ],
        "bellman_value": fraction_text(bellman_value),
        "bellman_optimizers": [
            list(item) for item in bellman_optimizers
        ],
        "exhaustive_value": fraction_text(exhaustive_best),
        "exhaustive_optimizers": [
            list(item) for item in exhaustive_optimizers
        ],
        "exact_match": (
            bellman_value == exhaustive_best
            and set(bellman_optimizers)
            == set(exhaustive_optimizers)
        ),
    }


def validate_registration(
    registration_path: Path,
    expected_hash: str,
) -> tuple[dict[str, Any], bool, list[str]]:
    registration = json.loads(
        registration_path.read_text(encoding="utf-8")
    )
    failures = []
    if sha256(registration_path).lower() != expected_hash.lower():
        failures.append("registration_hash")
    for relative, expected in registration["sealed_files"].items():
        path = REPO / relative
        if not path.is_file() or sha256(path) != expected:
            failures.append(relative)
    return registration, not failures, failures


def fresh_registry_check(
    protocol: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    minimum = int(
        protocol["freshness_rule"][
            "minimum_node_count_for_every_registered_graph"
        ]
    )
    signatures = []
    burned = set(
        protocol["freshness_rule"][
            "burned_full_graph_signatures"
        ].values()
    )
    violations = []
    for name, raw in protocol["graphs"].items():
        node_count = int(raw["node_count"])
        edges = tuple(
            sorted(
                tuple(sorted(edge)) for edge in raw["edges"]
            )
        )
        signature = (node_count, edges)
        digest = hashlib.sha256(
            json.dumps(
                {
                    "node_count": node_count,
                    "edges": [list(edge) for edge in edges],
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if node_count < minimum:
            violations.append(f"{name}:node_count")
        if signature in signatures:
            violations.append(f"{name}:duplicate_signature")
        if digest in burned:
            violations.append(f"{name}:burned_signature")
        signatures.append(signature)
    return not violations, {
        "graph_count": len(signatures),
        "minimum_node_count": min(
            int(raw["node_count"])
            for raw in protocol["graphs"].values()
        ),
        "unique_signature_count": len(set(signatures)),
        "burned_signature_count": len(burned),
        "violations": violations,
    }


def verdict_for_gates(gate_values: dict[str, bool]) -> str:
    return (
        "finite_block_factorization_established_in_frozen_model_v0_20"
        if all(gate_values.values())
        else "finite_block_factorization_not_established_v0_20"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--registration-sha256", required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    registration_path = args.registration.resolve()
    result_path = args.result.resolve()
    receipt_path = args.receipt.resolve()
    if result_path.exists() or receipt_path.exists():
        raise FileExistsError("refusing to overwrite registered output")

    started_utc = utc_now()
    start = time.perf_counter()
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    registration, binding_ok, binding_failures = (
        validate_registration(
            registration_path, args.registration_sha256
        )
    )
    graphs = {
        name: graph_from_raw(raw)
        for name, raw in protocol["graphs"].items()
    }

    fresh_ok, fresh_record = fresh_registry_check(protocol)

    partition_rows = []
    partition_ok = True
    for name, prepared in graphs.items():
        oracle = brute_cycle_blocks(
            prepared.node_count, prepared.edges
        )
        expected = tuple(
            tuple(block)
            for block in protocol["graphs"][name][
                "expected_blocks"
            ]
        )
        match = prepared.blocks == oracle == expected
        partition_ok = partition_ok and match
        partition_rows.append(
            {
                "graph": name,
                "implementation_blocks": [
                    list(block) for block in prepared.blocks
                ],
                "oracle_blocks": [
                    list(block) for block in oracle
                ],
                "expected_blocks": [
                    list(block) for block in expected
                ],
                "match": match,
            }
        )

    status_rows = []
    status_ok = True
    for name in protocol["status_census_graphs"]:
        prepared = graphs[name]
        oracle_blocks = brute_cycle_blocks(
            prepared.node_count, prepared.edges
        )
        mismatch_count = 0
        first_mismatch = None
        status_count = 0
        for statuses in itertools.product(
            (ZERO, INTERIOR, FULL),
            repeat=len(prepared.edges),
        ):
            status_count += 1
            values = (
                prepared.direct_available(statuses),
                prepared.blockwise_available(statuses),
                independent_direct_available(prepared, statuses),
                independent_block_available(
                    prepared, oracle_blocks, statuses
                ),
            )
            if len(set(values)) != 1:
                mismatch_count += 1
                if first_mismatch is None:
                    first_mismatch = {
                        "statuses": list(statuses),
                        "values": list(values),
                    }
        status_ok = status_ok and mismatch_count == 0
        status_rows.append(
            {
                "graph": name,
                "status_vectors_checked": status_count,
                "mismatch_count": mismatch_count,
                "first_mismatch": first_mismatch,
            }
        )

    probability_rows = []
    probability_ok = True
    for raw in protocol["fixed_probability_cells"]:
        prepared = graphs[raw["graph"]]
        counts = tuple(int(value) for value in raw["counts"])
        labels = tuple(int(value) for value in raw["labels"])
        epsilon = Fraction(raw["epsilon"])
        direct = exact_availability(
            prepared, counts, labels, epsilon
        )
        product, factors = product_availability(
            prepared, counts, labels, epsilon
        )
        match = direct == product
        probability_ok = probability_ok and match
        probability_rows.append(
            {
                "graph": raw["graph"],
                "counts": list(counts),
                "labels": raw["labels"],
                "epsilon": raw["epsilon"],
                "direct": fraction_text(direct),
                "product": fraction_text(product),
                "factors": list(factors),
                "match": match,
            }
        )

    worst_raw = protocol["worst_label_cell"]
    worst_prepared = graphs[worst_raw["graph"]]
    worst_counts = tuple(
        int(value) for value in worst_raw["counts"]
    )
    worst_epsilon = Fraction(worst_raw["epsilon"])
    global_worst, global_witnesses = worst_endpoint(
        worst_prepared, worst_counts, worst_epsilon
    )
    product_worst, worst_factors = product_worst_endpoint(
        worst_prepared, worst_counts, worst_epsilon
    )
    worst_record = {
        "graph": worst_raw["graph"],
        "counts": list(worst_counts),
        "epsilon": worst_raw["epsilon"],
        "global_worst": fraction_text(global_worst),
        "global_witness_count": len(global_witnesses),
        "global_witnesses": [
            "".join(str(item) for item in witness)
            for witness in global_witnesses
        ],
        "product_worst": fraction_text(product_worst),
        "factors": list(worst_factors),
        "match": global_worst == product_worst,
    }
    worst_ok = bool(worst_record["match"])

    bridge = graphs["bridge_separated_cycles"]
    epsilon = Fraction(2, 9)
    counts_a = (2, 1, 2, 1, 2, 1, 2, 1, 1)
    counts_b = (2, 1, 2, 7, 2, 1, 2, 1, 5)
    labels_a = (0, 1, 0, 0, 1, 0, 1, 0, 0)
    labels_b = (0, 1, 0, 1, 1, 0, 1, 0, 1)
    value_a = exact_availability(
        bridge, counts_a, labels_a, epsilon
    )
    value_b = exact_availability(
        bridge, counts_b, labels_b, epsilon
    )
    bridge_groups: dict[tuple[int, ...], bool] = {}
    bridge_status_violations = 0
    bridge_indices = tuple(sorted(bridge.bridges))
    nonbridges = tuple(
        edge_id
        for edge_id in range(len(bridge.edges))
        if edge_id not in bridge.bridges
    )
    for statuses in itertools.product(
        (ZERO, INTERIOR, FULL), repeat=len(bridge.edges)
    ):
        key = tuple(statuses[index] for index in nonbridges)
        value = bridge.direct_available(statuses)
        if key in bridge_groups and bridge_groups[key] != value:
            bridge_status_violations += 1
        bridge_groups[key] = value
    bridge_record = {
        "graph": "bridge_separated_cycles",
        "bridge_indices": list(bridge_indices),
        "status_group_count": len(bridge_groups),
        "status_violations": bridge_status_violations,
        "availability_a": fraction_text(value_a),
        "availability_b": fraction_text(value_b),
        "exact_match": value_a == value_b,
    }
    bridge_ok = (
        bridge_indices == (3, 8)
        and bridge_status_violations == 0
        and value_a == value_b
    )

    design_raw = protocol["design_cell"]
    design_record = design_comparison(
        graphs[design_raw["graph"]],
        int(design_raw["total_budget"]),
        Fraction(design_raw["epsilon"]),
    )
    design_record["graph"] = design_raw["graph"]
    design_ok = bool(design_record["exact_match"])

    control_raw = protocol["one_block_negative_control"]
    control = graphs[control_raw["graph"]]
    control_counts = tuple(
        int(value) for value in control_raw["counts"]
    )
    control_labels = tuple(
        int(value) for value in control_raw["labels"]
    )
    control_epsilon = Fraction(control_raw["epsilon"])
    control_direct = exact_availability(
        control, control_counts, control_labels, control_epsilon
    )
    control_product, _ = product_availability(
        control, control_counts, control_labels, control_epsilon
    )
    control_record = {
        "graph": control_raw["graph"],
        "factor_count": len(control.cyclic),
        "direct": fraction_text(control_direct),
        "product": fraction_text(control_product),
        "exact_match": control_direct == control_product,
        "interpretation": control_raw["required_interpretation"],
    }
    control_ok = (
        len(control.cyclic) == 1
        and control_direct == control_product
        and control_record["interpretation"]
        == "factor_count_one_no_within_block_computational_simplification"
    )

    elapsed = time.perf_counter() - start
    peak = peak_resident_bytes()
    caps = protocol["resource_caps"]
    resource_ok = (
        not bool(caps["gpu_allowed"])
        and elapsed <= float(caps["wall_seconds"])
        and peak <= int(caps["peak_resident_bytes"])
    )

    gate_values = {
        "G0_registration_binding": binding_ok,
        "G1_fresh_graph_registry": fresh_ok,
        "G2_block_partition": partition_ok,
        "G3_exhaustive_status_equivalence": status_ok,
        "G4_fixed_label_probability_product": probability_ok,
        "G5_rectangular_worst_label_product": worst_ok,
        "G6_bridge_irrelevance": bridge_ok,
        "G7_bellman_equals_full_edge_census": design_ok,
        "G8_one_block_negative_control": control_ok,
        "G9_resource_and_scope": (
            resource_ok
            and isinstance(protocol["claim_boundary"], str)
            and bool(protocol["claim_boundary"])
        ),
    }
    gate_order = protocol["gate_ids"]
    if set(gate_order) != set(gate_values):
        raise ValueError("protocol gate universe mismatch")
    verdict = verdict_for_gates(gate_values)

    result = {
        "protocol_id": protocol["protocol_id"],
        "version": protocol["version"],
        "claim_boundary": protocol["claim_boundary"],
        "started_at_utc": started_utc,
        "completed_at_utc": utc_now(),
        "implementation_commit": registration[
            "implementation_commit"
        ],
        "execution_commit": git("rev-parse", "HEAD"),
        "protocol_sha256": sha256(protocol_path),
        "registration_sha256": sha256(registration_path),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "gpu_used": False,
        },
        "registration_binding_failures": binding_failures,
        "fresh_registry": fresh_record,
        "block_partitions": partition_rows,
        "status_censuses": status_rows,
        "fixed_probability_products": probability_rows,
        "worst_label_product": worst_record,
        "bridge_irrelevance": bridge_record,
        "design_comparison": design_record,
        "one_block_negative_control": control_record,
        "resources": {
            "elapsed_seconds": elapsed,
            "peak_resident_bytes": peak,
            "wall_cap_seconds": caps["wall_seconds"],
            "peak_resident_cap_bytes": caps[
                "peak_resident_bytes"
            ],
            "gpu_used": False,
        },
        "gates": [
            {"gate_id": gate, "pass": gate_values[gate]}
            for gate in gate_order
        ],
        "gate_pass_count": sum(gate_values.values()),
        "gate_count": len(gate_values),
        "verdict": verdict,
    }
    write_json_exclusive(result_path, result)
    receipt = {
        "protocol_sha256": sha256(protocol_path),
        "registration_sha256": sha256(registration_path),
        "result_sha256": sha256(result_path),
        "result_path": result_path.relative_to(REPO).as_posix(),
        "verdict": verdict,
    }
    write_json_exclusive(receipt_path, receipt)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
