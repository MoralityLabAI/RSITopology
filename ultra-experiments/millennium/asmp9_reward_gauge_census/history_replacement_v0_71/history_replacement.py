"""Finite path-valuation factorization and replacement tools for ASMP-9 v0.71."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Mapping, Sequence

import sympy as sp


Path = tuple[str, ...]


@dataclass(frozen=True)
class Edge:
    edge_id: str
    source: str
    target: str


@dataclass(frozen=True)
class PathSystem:
    edges: tuple[Edge, ...]
    start: str
    horizon: int
    values: Mapping[Path, Fraction]

    def edge_map(self) -> dict[str, Edge]:
        return {edge.edge_id: edge for edge in self.edges}

    def histories(self) -> tuple[Path, ...]:
        return enumerate_histories(self.edges, self.start, self.horizon)

    def validate(self) -> None:
        if self.horizon < 0:
            raise ValueError("horizon must be nonnegative")
        edge_map = self.edge_map()
        if len(edge_map) != len(self.edges):
            raise ValueError("edge identifiers must be unique")
        histories = self.histories()
        if set(histories) != set(self.values):
            missing = set(histories) - set(self.values)
            extra = set(self.values) - set(histories)
            raise ValueError(f"value domain mismatch: missing={missing}, extra={extra}")
        for path, value in self.values.items():
            Fraction(value)
            current = self.start
            for edge_id in path:
                edge = edge_map[edge_id]
                if edge.source != current:
                    raise ValueError(f"noncomposable path: {path}")
                current = edge.target


def enumerate_histories(
    edges: Sequence[Edge], start: str, horizon: int
) -> tuple[Path, ...]:
    outgoing: dict[str, list[Edge]] = {}
    for edge in edges:
        outgoing.setdefault(edge.source, []).append(edge)
    for values in outgoing.values():
        values.sort(key=lambda edge: edge.edge_id)

    result: list[Path] = [tuple()]
    frontier: list[tuple[str, Path]] = [(start, tuple())]
    for _ in range(horizon):
        next_frontier: list[tuple[str, Path]] = []
        for vertex, path in frontier:
            for edge in outgoing.get(vertex, []):
                extended = path + (edge.edge_id,)
                result.append(extended)
                next_frontier.append((edge.target, extended))
        frontier = next_frontier
    return tuple(result)


def path_endpoint(system: PathSystem, path: Path) -> str:
    current = system.start
    edge_map = system.edge_map()
    for edge_id in path:
        current = edge_map[edge_id].target
    return current


def path_incidence(system: PathSystem) -> tuple[sp.Matrix, sp.Matrix]:
    system.validate()
    histories = system.histories()
    edge_index = {edge.edge_id: index for index, edge in enumerate(system.edges)}
    rows: list[list[int]] = []
    values: list[sp.Rational] = []
    empty_value = sp.Rational(system.values[tuple()])
    for path in histories:
        row = [0] * len(system.edges)
        for edge_id in path:
            row[edge_index[edge_id]] += 1
        rows.append(row)
        values.append(sp.Rational(system.values[path]) - empty_value)
    return sp.Matrix(rows), sp.Matrix(values)


@dataclass(frozen=True)
class MarkovFactorization:
    factorizes: bool
    edge_rewards: Mapping[str, str] | None
    obstruction_coefficients: Mapping[Path, str] | None
    obstruction_value: str | None
    path_count: int
    edge_count: int
    incidence_rank: int

    def to_jsonable(self) -> dict[str, object]:
        def encode_path(path: Path) -> str:
            return "/".join(path) if path else "<empty>"

        return {
            "factorizes": self.factorizes,
            "edge_rewards": self.edge_rewards,
            "obstruction_coefficients": (
                None
                if self.obstruction_coefficients is None
                else {
                    encode_path(path): value
                    for path, value in self.obstruction_coefficients.items()
                }
            ),
            "obstruction_value": self.obstruction_value,
            "path_count": self.path_count,
            "edge_count": self.edge_count,
            "incidence_rank": self.incidence_rank,
        }


def factor_markov_reward(system: PathSystem) -> MarkovFactorization:
    incidence, values = path_incidence(system)
    histories = system.histories()
    augmented_rank = incidence.row_join(values).rank()
    if augmented_rank == incidence.rank():
        solution = next(iter(sp.linsolve((incidence, values))))
        free_symbols = sorted(
            set().union(*(term.free_symbols for term in solution)),
            key=str,
        )
        substitutions = {symbol: 0 for symbol in free_symbols}
        selected = [sp.simplify(term.subs(substitutions)) for term in solution]
        return MarkovFactorization(
            factorizes=True,
            edge_rewards={
                edge.edge_id: str(selected[index])
                for index, edge in enumerate(system.edges)
            },
            obstruction_coefficients=None,
            obstruction_value=None,
            path_count=len(histories),
            edge_count=len(system.edges),
            incidence_rank=incidence.rank(),
        )

    for certificate in incidence.T.nullspace():
        residual = sp.simplify((certificate.T * values)[0])
        if residual != 0:
            coefficients = {
                path: str(certificate[index])
                for index, path in enumerate(histories)
                if certificate[index] != 0
            }
            return MarkovFactorization(
                factorizes=False,
                edge_rewards=None,
                obstruction_coefficients=coefficients,
                obstruction_value=str(residual),
                path_count=len(histories),
                edge_count=len(system.edges),
                incidence_rank=incidence.rank(),
            )
    raise AssertionError("inconsistent system lacked a left-kernel witness")


def _suffixes(system: PathSystem, vertex: str, budget: int) -> tuple[Path, ...]:
    return enumerate_histories(system.edges, vertex, budget)


@dataclass(frozen=True)
class HistoryReplacement:
    class_count: int
    state_time_count: int
    history_to_class: Mapping[Path, int]
    transitions: tuple[dict[str, object], ...]
    needs_history_augmentation: bool

    def to_jsonable(self) -> dict[str, object]:
        def encode_path(path: Path) -> str:
            return "/".join(path) if path else "<empty>"

        return {
            "class_count": self.class_count,
            "state_time_count": self.state_time_count,
            "history_to_class": {
                encode_path(path): class_id
                for path, class_id in self.history_to_class.items()
            },
            "transitions": list(self.transitions),
            "needs_history_augmentation": self.needs_history_augmentation,
        }


def canonical_history_replacement(system: PathSystem) -> HistoryReplacement:
    """Build the endpoint/time-respecting future-increment quotient."""

    system.validate()
    histories = system.histories()
    edge_map = system.edge_map()
    outgoing: dict[str, list[str]] = {}
    for edge in system.edges:
        outgoing.setdefault(edge.source, []).append(edge.edge_id)
    for edge_ids in outgoing.values():
        edge_ids.sort()

    signatures: dict[Path, tuple[object, ...]] = {}
    for history in histories:
        endpoint = path_endpoint(system, history)
        remaining = system.horizon - len(history)
        continuation = []
        for suffix in _suffixes(system, endpoint, remaining):
            increment = Fraction(system.values[history + suffix]) - Fraction(
                system.values[history]
            )
            continuation.append((suffix, increment))
        signatures[history] = (
            endpoint,
            remaining,
            tuple(continuation),
        )

    unique_signatures = {
        signature: index
        for index, signature in enumerate(
            sorted(set(signatures.values()), key=repr)
        )
    }
    history_to_class = {
        history: unique_signatures[signature]
        for history, signature in signatures.items()
    }

    transitions_by_key: dict[tuple[int, str], tuple[int, Fraction]] = {}
    for history in histories:
        if len(history) == system.horizon:
            continue
        endpoint = path_endpoint(system, history)
        for edge_id in outgoing.get(endpoint, []):
            extended = history + (edge_id,)
            key = (history_to_class[history], edge_id)
            value = (
                history_to_class[extended],
                Fraction(system.values[extended])
                - Fraction(system.values[history]),
            )
            if key in transitions_by_key and transitions_by_key[key] != value:
                raise AssertionError("future-equivalent histories had inconsistent transitions")
            transitions_by_key[key] = value

    transitions = tuple(
        {
            "source_class": source,
            "edge_id": edge_id,
            "target_class": target,
            "reward": str(reward),
        }
        for (source, edge_id), (target, reward) in sorted(
            transitions_by_key.items()
        )
    )
    state_time = {
        (
            path_endpoint(system, history),
            system.horizon - len(history),
        )
        for history in histories
    }
    return HistoryReplacement(
        class_count=len(unique_signatures),
        state_time_count=len(state_time),
        history_to_class=history_to_class,
        transitions=transitions,
        needs_history_augmentation=len(unique_signatures) > len(state_time),
    )


def replay_replacement(system: PathSystem, replacement: HistoryReplacement) -> bool:
    """Check telescoping reconstruction on every registered history."""

    transition_map = {
        (int(row["source_class"]), str(row["edge_id"])): (
            int(row["target_class"]),
            Fraction(str(row["reward"])),
        )
        for row in replacement.transitions
    }
    base = Fraction(system.values[tuple()])
    for path in system.histories():
        class_id = replacement.history_to_class[tuple()]
        total = base
        prefix: Path = tuple()
        for edge_id in path:
            target, reward = transition_map[(class_id, edge_id)]
            total += reward
            prefix += (edge_id,)
            class_id = target
            if class_id != replacement.history_to_class[prefix]:
                return False
        if total != Fraction(system.values[path]):
            return False
    return True


def canonical_fixtures() -> dict[str, PathSystem]:
    edges = (
        Edge("a", "s", "m"),
        Edge("b", "s", "m"),
        Edge("z", "m", "t"),
    )
    histories = enumerate_histories(edges, "s", 2)

    markov_rewards = {"a": Fraction(1), "b": Fraction(2), "z": Fraction(3)}
    markov_values = {
        path: sum((markov_rewards[edge] for edge in path), Fraction(0))
        for path in histories
    }

    interaction_values = {path: Fraction(0) for path in histories}
    interaction_values[("a", "z")] = Fraction(1)

    return {
        "markov_additive": PathSystem(
            edges=edges,
            start="s",
            horizon=2,
            values=markov_values,
        ),
        "history_interaction": PathSystem(
            edges=edges,
            start="s",
            horizon=2,
            values=interaction_values,
        ),
    }


def binary_valuation_census() -> dict[str, int]:
    """Exhaust all binary valuations on the four nonempty fixture histories."""

    base = canonical_fixtures()["markov_additive"]
    histories = base.histories()
    factorizing = 0
    nonfactorizing = 0
    history_augmented = 0
    replay_failures = 0
    for bits in product((0, 1), repeat=len(histories) - 1):
        values = {tuple(): Fraction(0)}
        values.update(
            {
                path: Fraction(bit)
                for path, bit in zip(histories[1:], bits, strict=True)
            }
        )
        system = PathSystem(
            edges=base.edges,
            start=base.start,
            horizon=base.horizon,
            values=values,
        )
        factorization = factor_markov_reward(system)
        replacement = canonical_history_replacement(system)
        if factorization.factorizes:
            factorizing += 1
        else:
            nonfactorizing += 1
        if replacement.needs_history_augmentation:
            history_augmented += 1
        if not replay_replacement(system, replacement):
            replay_failures += 1
    return {
        "total": 2 ** (len(histories) - 1),
        "factorizing": factorizing,
        "nonfactorizing": nonfactorizing,
        "history_augmented": history_augmented,
        "replay_failures": replay_failures,
    }
