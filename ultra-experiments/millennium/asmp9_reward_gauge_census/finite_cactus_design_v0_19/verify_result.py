"""Independent exact replay for the ASMP-9 v0.19 result."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_hash(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def prod(values: Iterable[Fraction]) -> Fraction:
    answer = Fraction(1)
    for value in values:
        answer *= value
    return answer


def xyz(n: int, epsilon: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    return (
        1 - (1 - epsilon) ** n,
        1 - epsilon**n,
        1 - (1 - epsilon) ** n - epsilon**n,
    )


def cycle_value(
    counts: Sequence[int],
    epsilon: Fraction,
    labels: Sequence[int],
) -> Fraction:
    first: list[Fraction] = []
    second: list[Fraction] = []
    interior: list[Fraction] = []
    for n, label in zip(counts, labels, strict=True):
        x_value, y_value, z_value = xyz(n, epsilon)
        first.append(x_value if label == 0 else y_value)
        second.append(y_value if label == 0 else x_value)
        interior.append(z_value)
    return prod(first) + prod(second) - prod(interior)


def cycle_worst(counts: Sequence[int], epsilon: Fraction) -> Fraction:
    return min(
        cycle_value(counts, epsilon, labels)
        for labels in product((0, 1), repeat=len(counts))
    )


def balanced(k: int, total: int) -> tuple[int, ...]:
    quotient, remainder = divmod(total, k)
    return (quotient,) * (k - remainder) + (quotient + 1,) * remainder


def f_value(k: int, total: int, epsilon: Fraction) -> Fraction:
    return cycle_worst(balanced(k, total), epsilon)


def bounded_compositions(
    total: int, floors: Sequence[int]
) -> Iterator[tuple[int, ...]]:
    floors = tuple(floors)
    slack = total - sum(floors)
    if slack < 0:
        return

    def visit(index: int, left: int, prefix: tuple[int, ...]):
        if index == len(floors) - 1:
            yield prefix + (floors[index] + left,)
            return
        for value in range(left + 1):
            yield from visit(
                index + 1,
                left - value,
                prefix + (floors[index] + value,),
            )

    yield from visit(0, slack, ())


def exact_totals(
    lengths: Sequence[int],
    budget: int,
    bridges: int,
    epsilon: Fraction,
) -> tuple[Fraction, tuple[tuple[int, ...], ...]]:
    rows = [
        (
            prod(
                f_value(length, total, epsilon)
                for length, total in zip(lengths, totals, strict=True)
            ),
            totals,
        )
        for totals in bounded_compositions(budget - bridges, lengths)
    ]
    maximum = max(value for value, _ in rows)
    return maximum, tuple(
        totals for value, totals in rows if value == maximum
    )


def bellman(
    lengths: Sequence[int],
    budget: int,
    bridges: int,
    epsilon: Fraction,
) -> tuple[Fraction, tuple[tuple[int, ...], ...]]:
    cycle_budget = budget - bridges
    states: dict[int, tuple[Fraction, set[tuple[int, ...]]]] = {
        0: (Fraction(1), {()})
    }
    for position, length in enumerate(lengths):
        remainder_floor = sum(lengths[position + 1 :])
        new: dict[int, tuple[Fraction, set[tuple[int, ...]]]] = {}
        for used, (prefix_value, prefixes) in states.items():
            for assigned in range(
                length, cycle_budget - used - remainder_floor + 1
            ):
                candidate = prefix_value * f_value(
                    length, assigned, epsilon
                )
                target = used + assigned
                extended = {
                    prefix + (assigned,) for prefix in prefixes
                }
                if target not in new or candidate > new[target][0]:
                    new[target] = (candidate, extended)
                elif candidate == new[target][0]:
                    new[target][1].update(extended)
        states = new
    value, totals = states[cycle_budget]
    return value, tuple(sorted(totals))


def bouquet(
    lengths: Sequence[int], bridges: int
) -> tuple[
    tuple[tuple[int, int], ...],
    tuple[tuple[int, ...], ...],
    tuple[int, ...],
]:
    edges: list[tuple[int, int]] = []
    blocks: list[tuple[int, ...]] = []
    next_vertex = 1
    for length in lengths:
        vertices = (0,) + tuple(range(next_vertex, next_vertex + length - 1))
        next_vertex += length - 1
        block = []
        for offset in range(length):
            block.append(len(edges))
            edges.append(
                (vertices[offset], vertices[(offset + 1) % length])
            )
        blocks.append(tuple(block))
    bridge_indices = []
    previous = 0
    for _ in range(bridges):
        bridge_indices.append(len(edges))
        edges.append((previous, next_vertex))
        previous = next_vertex
        next_vertex += 1
    return tuple(edges), tuple(blocks), tuple(bridge_indices)


def components(
    vertices: Sequence[int], arcs: Sequence[tuple[int, int]]
) -> dict[int, int]:
    adjacency = {vertex: [] for vertex in vertices}
    reverse = {vertex: [] for vertex in vertices}
    for source, target in arcs:
        adjacency[source].append(target)
        reverse[target].append(source)
    seen: set[int] = set()
    order: list[int] = []

    def forward(vertex: int) -> None:
        seen.add(vertex)
        for target in adjacency[vertex]:
            if target not in seen:
                forward(target)
        order.append(vertex)

    for vertex in vertices:
        if vertex not in seen:
            forward(vertex)
    labels: dict[int, int] = {}

    def backward(vertex: int, label: int) -> None:
        labels[vertex] = label
        for target in reverse[vertex]:
            if target not in labels:
                backward(target, label)

    label = 0
    for vertex in reversed(order):
        if vertex not in labels:
            backward(vertex, label)
            label += 1
    return labels


def live(
    edges: Sequence[tuple[int, int]],
    blocks: Sequence[Sequence[int]],
    statuses: Sequence[str],
) -> bool:
    arcs = []
    for (source, target), status in zip(edges, statuses, strict=True):
        if status in ("Z", "I"):
            arcs.append((source, target))
        if status in ("F", "I"):
            arcs.append((target, source))
    vertices = sorted({value for edge in edges for value in edge})
    labels = components(vertices, arcs)
    return all(
        labels[edges[index][0]] == labels[edges[index][1]]
        for block in blocks
        for index in block
    )


def status_law(
    n: int, epsilon: Fraction, label: int
) -> dict[str, Fraction]:
    p_value = epsilon if label == 0 else 1 - epsilon
    return {
        "Z": (1 - p_value) ** n,
        "F": p_value**n,
        "I": 1 - (1 - p_value) ** n - p_value**n,
    }


def graph_direct(
    lengths: Sequence[int],
    bridges: int,
    counts: Sequence[int],
    epsilon: Fraction,
    labels: Sequence[int],
) -> Fraction:
    edges, blocks, _ = bouquet(lengths, bridges)
    laws = [
        status_law(n, epsilon, label)
        for n, label in zip(counts, labels, strict=True)
    ]
    answer = Fraction(0)
    for statuses in product(("Z", "I", "F"), repeat=len(edges)):
        if live(edges, blocks, statuses):
            answer += prod(
                laws[index][status]
                for index, status in enumerate(statuses)
            )
    return answer


def graph_factorized(
    lengths: Sequence[int],
    bridges: int,
    counts: Sequence[int],
    epsilon: Fraction,
    labels: Sequence[int],
) -> Fraction:
    _, blocks, _ = bouquet(lengths, bridges)
    return prod(
        cycle_value(
            tuple(counts[index] for index in block),
            epsilon,
            tuple(labels[index] for index in block),
        )
        for block in blocks
    )


def positive_compositions(total: int, parts: int):
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for rest in positive_compositions(total - first, parts - 1):
            yield (first,) + rest


def all_edge_optimum(raw: dict[str, Any]):
    lengths = tuple(raw["cycle_lengths"])
    bridges = int(raw["bridge_count"])
    total = int(raw["total_budget"])
    epsilon = Fraction(raw["epsilon"])
    _, blocks, bridge_indices = bouquet(lengths, bridges)
    edge_count = sum(lengths) + bridges
    rows = []
    for counts in positive_compositions(total, edge_count):
        value = prod(
            cycle_worst(
                tuple(counts[index] for index in block), epsilon
            )
            for block in blocks
        )
        rows.append((value, counts))
    maximum = max(value for value, _ in rows)
    optimizers = tuple(
        counts for value, counts in rows if value == maximum
    )
    induced = {
        tuple(sum(counts[index] for index in block) for block in blocks)
        for counts in optimizers
    }
    bridge_floor = all(
        all(counts[index] == 1 for index in bridge_indices)
        for counts in optimizers
    )
    internally_balanced = all(
        all(
            max(counts[index] for index in block)
            - min(counts[index] for index in block)
            <= 1
            for block in blocks
        )
        for counts in optimizers
    )
    return maximum, optimizers, induced, bridge_floor, internally_balanced


def all_greedy_endpoints(
    lengths: Sequence[int],
    budget: int,
    epsilon: Fraction,
) -> tuple[tuple[int, ...], ...]:
    states = {tuple(lengths)}
    while sum(next(iter(states))) < budget:
        new = set()
        for totals in states:
            ratios = [
                f_value(k, n + 1, epsilon) / f_value(k, n, epsilon)
                for k, n in zip(lengths, totals, strict=True)
            ]
            maximum = max(ratios)
            for index, ratio in enumerate(ratios):
                if ratio == maximum:
                    updated = list(totals)
                    updated[index] += 1
                    new.add(tuple(updated))
        states = new
    return tuple(sorted(states))


def global_totals(
    lengths: Sequence[int], budget: int
) -> tuple[tuple[int, ...], ...]:
    lower, high_count = divmod(budget, sum(lengths))
    output = set()
    for highs in bounded_compositions(high_count, (0,) * len(lengths)):
        if all(h <= k for h, k in zip(highs, lengths, strict=True)):
            output.add(
                tuple(
                    lower * k + h
                    for h, k in zip(highs, lengths, strict=True)
                )
            )
    return tuple(sorted(output))


def allocation(
    lengths: Sequence[int],
    totals: Sequence[int],
    epsilon: Fraction,
) -> Fraction:
    return prod(
        f_value(k, n, epsilon)
        for k, n in zip(lengths, totals, strict=True)
    )


def parse_result_fraction(record: dict[str, Any]) -> Fraction:
    return Fraction(record["fraction"])


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
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    registration = json.loads(
        args.registration.read_text(encoding="utf-8")
    )
    result = json.loads(args.result.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    checks["protocol_hash"] = (
        result["protocol_sha256"] == sha256(args.protocol)
    )
    checks["registration_hash"] = (
        result["registration_sha256"] == sha256(args.registration)
    )
    checks["sealed_files"] = all(
        (REPO / relative).is_file()
        and sha256(REPO / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )

    raw_direct = protocol["factorization_cells"]["fresh_figure_3_4"]
    direct_rows = []
    mismatches = 0
    for labels in product(
        (0, 1), repeat=sum(raw_direct["cycle_lengths"])
    ):
        direct = graph_direct(
            raw_direct["cycle_lengths"],
            raw_direct["bridge_count"],
            raw_direct["counts"],
            Fraction(raw_direct["epsilon"]),
            labels,
        )
        factored = graph_factorized(
            raw_direct["cycle_lengths"],
            raw_direct["bridge_count"],
            raw_direct["counts"],
            Fraction(raw_direct["epsilon"]),
            labels,
        )
        mismatches += direct != factored
        direct_rows.append(
            {
                "labels": "".join(str(value) for value in labels),
                "direct": f"{direct.numerator}/{direct.denominator}",
                "factorized": (
                    f"{factored.numerator}/{factored.denominator}"
                ),
            }
        )
    checks["factorization"] = (
        mismatches == 0
        and result["factorization"]["mismatch_count"] == 0
        and result["factorization"]["row_sha256"]
        == json_hash(direct_rows)
    )

    raw_bridge = protocol["factorization_cells"][
        "fresh_figure_3_5_bridge"
    ]
    bridge_ok = True
    for labels in raw_bridge["label_vectors"]:
        value_a = graph_direct(
            raw_bridge["cycle_lengths"],
            raw_bridge["bridge_count"],
            raw_bridge["counts_a"],
            Fraction(raw_bridge["epsilon"]),
            labels,
        )
        value_b = graph_direct(
            raw_bridge["cycle_lengths"],
            raw_bridge["bridge_count"],
            raw_bridge["counts_b"],
            Fraction(raw_bridge["epsilon"]),
            labels,
        )
        factored = graph_factorized(
            raw_bridge["cycle_lengths"],
            raw_bridge["bridge_count"],
            raw_bridge["counts_a"],
            Fraction(raw_bridge["epsilon"]),
            labels,
        )
        bridge_ok &= value_a == value_b == factored
    checks["bridge"] = bridge_ok and result["bridge"]["pass"]

    dp_ok = True
    result_dp = {row["name"]: row for row in result["dp_cells"]}
    for name, raw in protocol["dp_cells"].items():
        lengths = tuple(raw["cycle_lengths"])
        epsilon = Fraction(raw["epsilon"])
        dynamic = bellman(
            lengths,
            raw["total_budget"],
            raw["bridge_count"],
            epsilon,
        )
        exhaustive = exact_totals(
            lengths,
            raw["total_budget"],
            raw["bridge_count"],
            epsilon,
        )
        reported = result_dp[name]
        dp_ok &= (
            dynamic == exhaustive
            and parse_result_fraction(reported["dynamic"]["value"])
            == dynamic[0]
            and tuple(
                tuple(value)
                for value in reported["dynamic"]["cycle_totals"]
            )
            == dynamic[1]
        )
    checks["dp_cells"] = dp_ok

    direct = all_edge_optimum(protocol["global_edge_census"])
    raw_global = protocol["global_edge_census"]
    dynamic = bellman(
        tuple(raw_global["cycle_lengths"]),
        raw_global["total_budget"],
        raw_global["bridge_count"],
        Fraction(raw_global["epsilon"]),
    )
    reported_global = result["all_edge_census"]
    checks["all_edge"] = (
        direct[0] == dynamic[0]
        and direct[2] == set(dynamic[1])
        and direct[3]
        and direct[4]
        and parse_result_fraction(reported_global["direct_value"])
        == direct[0]
        and reported_global["bridges_at_floor"]
        and reported_global["cycles_balanced"]
    )

    greedy_lengths = (3, 3)
    greedy_epsilon = Fraction(1, 4)
    greedy_endpoints = all_greedy_endpoints(
        greedy_lengths, 10, greedy_epsilon
    )
    greedy_optimum = bellman(greedy_lengths, 10, 0, greedy_epsilon)
    greedy_value = max(
        allocation(greedy_lengths, totals, greedy_epsilon)
        for totals in greedy_endpoints
    )
    uniform_lengths = (3, 4)
    uniform_epsilon = Fraction(1, 10)
    balanced_totals = global_totals(uniform_lengths, 12)
    uniform_optimum = bellman(uniform_lengths, 12, 0, uniform_epsilon)
    balanced_value = max(
        allocation(uniform_lengths, totals, uniform_epsilon)
        for totals in balanced_totals
    )
    checks["regressions"] = (
        greedy_endpoints == ((4, 6), (6, 4))
        and greedy_optimum[1] == ((5, 5),)
        and greedy_optimum[0] - greedy_value
        == Fraction(45, 262144)
        and uniform_optimum[1] == ((3, 9),)
        and uniform_optimum[0] - balanced_value
        == Fraction(26235981, 125000000000)
    )

    comparator_ok = True
    reported_comparators = {
        row["name"]: row for row in result["comparators"]
    }
    for name, raw in protocol["comparator_cells"].items():
        lengths = tuple(raw["cycle_lengths"])
        epsilon = Fraction(raw["epsilon"])
        exact = exact_totals(
            lengths,
            raw["total_budget"],
            raw["bridge_count"],
            epsilon,
        )
        dynamic = bellman(
            lengths,
            raw["total_budget"],
            raw["bridge_count"],
            epsilon,
        )
        reported = reported_comparators[name]
        comparator_ok &= (
            exact == dynamic
            and parse_result_fraction(reported["dynamic"]["value"])
            == dynamic[0]
            and tuple(
                tuple(value)
                for value in reported["dynamic"]["cycle_totals"]
            )
            == dynamic[1]
        )
    checks["comparators"] = comparator_ok
    checks["registered_gates"] = (
        len(result["gates"]) == len(protocol["gate_ids"])
        and all(result["gates"].values())
        and result["verdict"]
        == "finite_budget_cactus_dp_established_in_frozen_model"
    )
    verification = {
        "verification_id": (
            "ASMP-9-FINITE-CACTUS-DESIGN-v0.19-independent"
        ),
        "protocol_sha256": sha256(args.protocol),
        "registration_sha256": sha256(args.registration),
        "result_sha256": sha256(args.result),
        "checks": checks,
        "check_count": len(checks),
        "pass": all(checks.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(verification, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(verification, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
