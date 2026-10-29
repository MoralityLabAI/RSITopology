from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ZERO = 0
INTERIOR = 1
FULL = 2
Edge = tuple[int, int]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(text: str) -> Fraction:
    numerator, denominator = text.split("/")
    return Fraction(int(numerator), int(denominator))


def components(node_count: int, edges: Sequence[Edge]) -> int:
    adjacency = [set() for _ in range(node_count)]
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen = set()
    count = 0
    for root in range(node_count):
        if root in seen:
            continue
        count += 1
        stack = [root]
        seen.add(root)
        while stack:
            node = stack.pop()
            for other in adjacency[node] - seen:
                seen.add(other)
                stack.append(other)
    return count


def cycle_rank(node_count: int, edges: Sequence[Edge]) -> int:
    return len(edges) - node_count + components(node_count, edges)


def residual_rank(
    node_count: int,
    edges: Sequence[Edge],
    statuses: Sequence[int],
) -> int:
    reach = [[False] * node_count for _ in range(node_count)]
    for node in range(node_count):
        reach[node][node] = True
    for (source, target), status in zip(
        edges, statuses, strict=True
    ):
        if status in (ZERO, INTERIOR):
            reach[source][target] = True
        if status in (INTERIOR, FULL):
            reach[target][source] = True
    for via in range(node_count):
        for source in range(node_count):
            if reach[source][via]:
                for target in range(node_count):
                    reach[source][target] = (
                        reach[source][target]
                        or reach[via][target]
                    )
    retained = tuple(
        edge
        for edge in edges
        if reach[edge[0]][edge[1]] and reach[edge[1]][edge[0]]
    )
    return cycle_rank(node_count, retained)


def statuses(
    counts: Sequence[int], capacities: Sequence[int]
) -> tuple[int, ...]:
    return tuple(
        ZERO if value == 0 else FULL if value == cap else INTERIOR
        for value, cap in zip(counts, capacities, strict=True)
    )


def incidence(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    rows = []
    for source, target in edges:
        row = [0] * node_count
        row[source] = -1
        row[target] = 1
        rows.append(tuple(row))
    return tuple(rows)


def balance(
    counts: Sequence[int], rows: Sequence[Sequence[int]]
) -> tuple[int, ...]:
    return tuple(
        sum(
            counts[edge] * rows[edge][node]
            for edge in range(len(rows))
        )
        for node in range(len(rows[0]))
    )


def rank(matrix: Sequence[Sequence[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    row_count = len(work)
    column_count = len(work[0])
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (
                row
                for row in range(pivot_row, row_count)
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [
            value / scale for value in work[pivot_row]
        ]
        for row in range(pivot_row + 1, row_count):
            factor = work[row][column]
            if factor:
                work[row] = [
                    work[row][entry]
                    - factor * work[pivot_row][entry]
                    for entry in range(column_count)
                ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def enumerate_fibers(
    capacities: Sequence[int], rows: Sequence[Sequence[int]]
) -> dict[tuple[int, ...], list[tuple[int, ...]]]:
    result: dict[tuple[int, ...], list[tuple[int, ...]]] = defaultdict(
        list
    )
    for counts in itertools.product(
        *(range(capacity + 1) for capacity in capacities)
    ):
        result[balance(counts, rows)].append(counts)
    return dict(result)


def affine_rank(fiber: Sequence[Sequence[int]]) -> int:
    if len(fiber) <= 1:
        return 0
    origin = fiber[0]
    return rank(
        [
            [
                value - origin[column]
                for column, value in enumerate(point)
            ]
            for point in fiber[1:]
        ]
    )


def graph(
    protocol: dict[str, Any], name: str
) -> tuple[int, tuple[Edge, ...], int]:
    raw = protocol["graphs"][name]
    return (
        raw["node_count"],
        tuple(tuple(edge) for edge in raw["edges"]),
        raw["expected_beta1"],
    )


def canonical_graph_signature(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, int], ...]:
    best = None
    for permutation in itertools.permutations(range(node_count)):
        candidate = tuple(
            sorted(
                tuple(sorted((permutation[left], permutation[right])))
                for left, right in edges
            )
        )
        if best is None or candidate < best:
            best = candidate
    if best is None:
        raise AssertionError("empty graph signature")
    return best


def independent_residual_summary(
    protocol: dict[str, Any]
) -> dict[tuple[str, tuple[int, ...]], dict[str, Any]]:
    summaries = {}
    for row in protocol["residual_rank_registry"]:
        node_count, edges, _ = graph(protocol, row["graph"])
        rows = incidence(node_count, edges)
        for capacities_raw in row["capacity_vectors"]:
            capacities = tuple(capacities_raw)
            fibers = enumerate_fibers(capacities, rows)
            mismatch = 0
            representative = 0
            state_count = 0
            histogram: Counter[int] = Counter()
            for fiber in fibers.values():
                direct = affine_rank(fiber)
                histogram[direct] += 1
                predicted = set()
                for counts in fiber:
                    value = residual_rank(
                        node_count,
                        edges,
                        statuses(counts, capacities),
                    )
                    predicted.add(value)
                    mismatch += int(value != direct)
                    state_count += 1
                representative += int(predicted != {direct})
            summaries[(row["graph"], capacities)] = {
                "fiber_count": len(fibers),
                "state_count": state_count,
                "rank_histogram": {
                    str(key): value
                    for key, value in sorted(histogram.items())
                },
                "mismatch_count": mismatch,
                "representative_invariance_failure_count": representative,
            }
    return summaries


def status_law(
    capacity: int, probability: Fraction
) -> tuple[Fraction, Fraction, Fraction]:
    zero = (1 - probability) ** capacity
    full = probability**capacity
    return zero, 1 - zero - full, full


def independent_status_availability(
    node_count: int,
    edges: Sequence[Edge],
    capacities: Sequence[int],
    probabilities: Sequence[Fraction],
) -> Fraction:
    laws = [
        status_law(capacity, probability)
        for capacity, probability in zip(
            capacities, probabilities, strict=True
        )
    ]
    beta1 = cycle_rank(node_count, edges)
    total = Fraction(0)
    for state in itertools.product(
        (ZERO, INTERIOR, FULL), repeat=len(edges)
    ):
        if residual_rank(node_count, edges, state) != beta1:
            continue
        mass = Fraction(1)
        for law, value in zip(laws, state, strict=True):
            mass *= law[value]
        total += mass
    return total


def independent_raw_availability(
    node_count: int,
    edges: Sequence[Edge],
    capacities: Sequence[int],
    probabilities: Sequence[Fraction],
) -> Fraction:
    rows = incidence(node_count, edges)
    fibers = enumerate_fibers(capacities, rows)
    beta1 = cycle_rank(node_count, edges)
    total = Fraction(0)
    for fiber in fibers.values():
        if affine_rank(fiber) != beta1:
            continue
        for counts in fiber:
            mass = Fraction(1)
            for value, capacity, probability in zip(
                counts, capacities, probabilities, strict=True
            ):
                mass *= (
                    comb(capacity, value)
                    * probability**value
                    * (1 - probability) ** (capacity - value)
                )
            total += mass
    return total


def independent_bad_supports(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    bad = set()
    for state in itertools.product(
        (ZERO, INTERIOR, FULL), repeat=len(edges)
    ):
        if residual_rank(node_count, edges, state) == cycle_rank(
            node_count, edges
        ):
            continue
        bad.add(
            frozenset(
                edge
                for edge, value in enumerate(state)
                if value != INTERIOR
            )
        )
    minimal = [
        support
        for support in bad
        if not any(other < support for other in bad)
    ]
    return tuple(
        sorted(
            (tuple(sorted(value)) for value in minimal),
            key=lambda value: (len(value), value),
        )
    )


def positive_allocations(
    total: int, width: int
) -> Iterable[tuple[int, ...]]:
    if width == 1:
        if total >= 1:
            yield (total,)
        return
    for first in range(1, total - width + 2):
        for tail in positive_allocations(total - first, width - 1):
            yield (first, *tail)


def theta_availability(
    paths: Sequence[Sequence[int]],
    capacities: Sequence[int],
    probabilities: Sequence[Fraction],
) -> Fraction:
    laws = [
        status_law(capacity, probability)
        for capacity, probability in zip(
            capacities, probabilities, strict=True
        )
    ]
    path_laws = []
    for path in paths:
        forward = Fraction(1)
        backward = Fraction(1)
        bidirectional = Fraction(1)
        for edge in path:
            zero, interior, full = laws[edge]
            forward *= zero + interior
            backward *= full + interior
            bidirectional *= interior
        path_laws.append(
            (
                forward,
                backward,
                bidirectional,
                forward + backward - bidirectional,
            )
        )
    all_usable = Fraction(1)
    all_forward_only = Fraction(1)
    all_backward_only = Fraction(1)
    for forward, backward, bidirectional, usable in path_laws:
        all_usable *= usable
        all_forward_only *= forward - bidirectional
        all_backward_only *= backward - bidirectional
    return all_usable - all_forward_only - all_backward_only


def theta_worst(
    paths: Sequence[Sequence[int]],
    capacities: Sequence[int],
    epsilon: Fraction,
) -> tuple[Fraction, list[tuple[int, ...]]]:
    best = None
    witnesses = []
    for labels in itertools.product((0, 1), repeat=len(capacities)):
        probabilities = tuple(
            epsilon if label == 0 else 1 - epsilon
            for label in labels
        )
        value = theta_availability(paths, capacities, probabilities)
        if best is None or value < best:
            best = value
            witnesses = [labels]
        elif value == best:
            witnesses.append(labels)
    if best is None:
        raise AssertionError("empty endpoint universe")
    return best, witnesses


def independent_finite(
    protocol: dict[str, Any]
) -> dict[str, Any]:
    raw = protocol["finite_counterexample"]
    paths = tuple(tuple(path) for path in raw["paths"])
    total = raw["total_trials"]
    epsilon = parse(raw["epsilon"])
    uniform = tuple(raw["uniform_allocation"])
    digest = hashlib.sha256()
    optimum = None
    optimizers = []
    allocation_count = 0
    for counts in positive_allocations(total, len(uniform)):
        value, witnesses = theta_worst(paths, counts, epsilon)
        allocation_count += 1
        digest.update(
            (
                ",".join(str(item) for item in counts)
                + f"|{value.numerator}/{value.denominator}|"
                + ";".join(
                    "".join(map(str, witness)) for witness in witnesses
                )
                + "\n"
            ).encode("ascii")
        )
        if optimum is None or value > optimum:
            optimum = value
            optimizers = [counts]
        elif value == optimum:
            optimizers.append(counts)
    uniform_value, _ = theta_worst(paths, uniform, epsilon)
    if optimum is None:
        raise AssertionError("empty allocation universe")
    return {
        "allocation_count": allocation_count,
        "digest": digest.hexdigest(),
        "uniform": uniform_value,
        "optimum": optimum,
        "optimizers": optimizers,
        "balanced_optimizer_count": sum(
            max(value) - min(value) <= 1 for value in optimizers
        ),
    }


def verify(
    registration_path: Path,
    result_path: Path,
    report_path: Path,
    receipt_path: Path,
    start_path: Path,
    progress_path: Path,
) -> dict[str, Any]:
    registration = json.loads(
        registration_path.read_text(encoding="utf-8")
    )
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    start = json.loads(start_path.read_text(encoding="utf-8"))
    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    for relative, expected in registration["sealed_files"].items():
        checks[f"sealed:{relative}"] = sha256(REPO / relative) == expected
    for output in (result_path, report_path, start_path, progress_path):
        checks[f"receipt:{output.name}"] = (
            receipt["output_hashes"][output.name] == sha256(output)
        )
    checks["registration_hash"] = (
        result["registration_sha256"]
        == receipt["registration_sha256"]
        == start["registration_sha256"]
        == sha256(registration_path)
    )
    checks["protocol_chain"] = (
        result["protocol_id"]
        == receipt["protocol_id"]
        == start["protocol_id"]
        == progress["protocol_id"]
        == protocol["protocol_id"]
    )
    checks["reported_pass"] = (
        result["verdict"] == receipt["verdict"]
        == "registered_exact_result_passed"
        and all(result["gates"].values())
    )
    checks["gate_universe"] = (
        list(result["gates"]) == protocol["gate_ids"]
    )
    checks["progress_completed"] = (
        start["status"] == "started"
        and progress["status"] == "completed"
        and progress["stage"] == "completed"
    )

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
    fresh_signatures = {
        name: canonical_graph_signature(
            raw["node_count"], tuple(tuple(edge) for edge in raw["edges"])
        )
        for name, raw in protocol["graphs"].items()
    }
    burned_signatures = {
        name: canonical_graph_signature(
            raw["node_count"], tuple(tuple(edge) for edge in raw["edges"])
        )
        for name, raw in protocol["burned_graph_registry"].items()
    }
    checks["independent_registry_and_freshness"] = (
        len(residual_keys) == len(set(residual_keys)) == 6
        and len(availability_keys) == len(set(availability_keys)) == 3
        and len(protocol["bad_support_certificates"]) == 3
        and not any(
            fresh == burned
            for fresh in fresh_signatures.values()
            for burned in burned_signatures.values()
        )
    )

    independent_residual = independent_residual_summary(protocol)
    residual_ok = True
    for row in result["residual_rank_records"]:
        key = (row["graph"], tuple(row["capacities"]))
        expected = independent_residual.get(key)
        residual_ok = residual_ok and expected is not None and all(
            row[field] == expected[field]
            for field in (
                "fiber_count",
                "state_count",
                "rank_histogram",
                "mismatch_count",
                "representative_invariance_failure_count",
            )
        )
    checks["independent_residual_rank_replay"] = (
        residual_ok
        and len(result["residual_rank_records"])
        == len(independent_residual)
    )

    availability_ok = True
    for row in result["availability_records"]:
        node_count, edges, _ = graph(protocol, row["graph"])
        capacities = tuple(row["counts"])
        probabilities = tuple(
            parse(item["fraction"]) for item in row["probabilities"]
        )
        raw = independent_raw_availability(
            node_count, edges, capacities, probabilities
        )
        compressed = independent_status_availability(
            node_count, edges, capacities, probabilities
        )
        availability_ok = availability_ok and (
            raw
            == compressed
            == parse(row["raw_full_rank_probability"]["fraction"])
            == parse(row["ternary_full_rank_probability"]["fraction"])
        )
    checks["independent_three_state_replay"] = availability_ok

    endpoint_ok = True
    endpoint_comparisons = {}
    for name in sorted(protocol["graphs"]):
        node_count, edges, beta1 = graph(protocol, name)
        count = 0
        violations = 0
        for selected in range(len(edges)):
            remaining = [
                edge for edge in range(len(edges)) if edge != selected
            ]
            for other_values in itertools.product(
                (ZERO, INTERIOR, FULL), repeat=len(remaining)
            ):
                state = [INTERIOR] * len(edges)
                for edge, value in zip(
                    remaining, other_values, strict=True
                ):
                    state[edge] = value
                outcomes = {}
                for value in (ZERO, INTERIOR, FULL):
                    candidate = list(state)
                    candidate[selected] = value
                    outcomes[value] = (
                        residual_rank(node_count, edges, candidate) == beta1
                    )
                count += 2
                violations += int(
                    (outcomes[ZERO] and not outcomes[INTERIOR])
                    or (outcomes[FULL] and not outcomes[INTERIOR])
                )
        endpoint_comparisons[name] = (count, violations)
    for row in result["endpoint_monotonicity_records"]:
        count, violations = endpoint_comparisons[row["graph"]]
        endpoint_ok = endpoint_ok and (
            row["comparison_count"] == count
            and row["violation_count"] == violations == 0
        )
    checks["independent_endpoint_reduction"] = endpoint_ok

    support_ok = True
    for row in result["bad_support_records"]:
        node_count, edges, _ = graph(protocol, row["graph"])
        actual = independent_bad_supports(node_count, edges)
        support_ok = support_ok and actual == tuple(
            tuple(value) for value in row["actual_supports"]
        )
    checks["independent_bad_support_replay"] = support_ok

    exponent_ok = True
    for row in result["exponent_certificate_records"]:
        raw = protocol["bad_support_certificates"][row["graph"]]
        supports = tuple(tuple(value) for value in raw["expected_supports"])
        weights = tuple(parse(value) for value in raw["primal_weights"])
        threshold = parse(raw["threshold"])
        primal = min(
            sum((weights[edge] for edge in support), Fraction(0))
            for support in supports
        )
        dual = [
            (tuple(item["support"]), parse(item["mass"]))
            for item in raw["dual_distribution"]
        ]
        edge_count = len(weights)
        loads = [
            sum(
                (
                    mass
                    for support, mass in dual
                    if edge in support
                ),
                Fraction(0),
            )
            for edge in range(edge_count)
        ]
        exponent_ok = exponent_ok and (
            sum(weights, Fraction(0)) == 1
            and sum((mass for _, mass in dual), Fraction(0)) == 1
            and primal == max(loads) == threshold
            and row["primal_feasible"]
            and row["dual_feasible"]
            and row["matching_value"]
        )
    checks["independent_exponent_certificates"] = exponent_ok

    finite = independent_finite(protocol)
    reported = result["finite_counterexample"]
    checks["independent_finite_counterexample"] = (
        finite["allocation_count"] == reported["allocation_count"]
        and finite["digest"]
        == reported["allocation_value_digest_sha256"]
        and finite["uniform"]
        == parse(reported["uniform_value"]["fraction"])
        and finite["optimum"]
        == parse(reported["optimum"]["fraction"])
        and [list(value) for value in finite["optimizers"]]
        == reported["optimizers"]
        and finite["balanced_optimizer_count"]
        == reported["balanced_optimizer_count"]
    )

    caps = protocol["resource_caps"]
    checks["resource_caps"] = (
        result["resources"]["gpu_used"] is False
        and receipt["resources"]["gpu_used"] is False
        and progress["elapsed_seconds"] <= caps["wall_seconds"]
        and progress["peak_resident_bytes"]
        <= caps["peak_resident_bytes"]
        and receipt["resources"]["elapsed_seconds"]
        <= caps["wall_seconds"]
        and receipt["resources"]["peak_resident_bytes"]
        <= caps["peak_resident_bytes"]
    )
    checks["claim_boundary_exact"] = (
        result["claim_boundary"] == protocol["claim_boundary"]
        and protocol["claim_boundary"] in report
    )
    failed = [name for name, passed in checks.items() if not passed]
    return {
        "status": "pass" if not failed else "fail",
        "check_count": len(checks),
        "checks": checks,
        "failed_checks": failed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--start", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    verification = verify(
        args.registration.resolve(),
        args.result.resolve(),
        args.report.resolve(),
        args.receipt.resolve(),
        args.start.resolve(),
        args.progress.resolve(),
    )
    rendered = json.dumps(verification, indent=2, sort_keys=True) + "\n"
    if args.output:
        if args.output.exists():
            raise FileExistsError(
                f"refusing to overwrite output: {args.output}"
            )
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    raise SystemExit(0 if verification["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
