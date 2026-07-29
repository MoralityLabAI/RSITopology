"""Exact finite dynamic-response diagnostics for ASMP-9 v0.66."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Sequence


Belief = tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class Transducer:
    """A deterministic query/response/update system.

    ``outputs[state][query]`` is emitted before the corresponding
    ``transitions[state][query]`` becomes the current state.  A write-before-
    read system must encode its post-update response directly in ``outputs``;
    the chronology is therefore part of the registered transducer.
    """

    outputs: tuple[tuple[int, ...], ...]
    transitions: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        if len(self.outputs) < 2:
            raise ValueError("at least two latent states are required")
        if len(self.outputs) != len(self.transitions):
            raise ValueError("output and transition state counts differ")
        query_count = len(self.outputs[0])
        if query_count < 1:
            raise ValueError("at least one query is required")
        if any(len(row) != query_count for row in self.outputs):
            raise ValueError("output rows must have equal query count")
        if any(len(row) != query_count for row in self.transitions):
            raise ValueError("transition rows must have equal query count")
        state_count = len(self.outputs)
        if any(
            target < 0 or target >= state_count
            for row in self.transitions
            for target in row
        ):
            raise ValueError("transition target outside state universe")

    @property
    def state_count(self) -> int:
        return len(self.outputs)

    @property
    def query_count(self) -> int:
        return len(self.outputs[0])


@dataclass(frozen=True)
class SolveResult:
    initial_belief: Belief
    winning: bool
    minimum_depth: int | None
    reachable_belief_count: int
    winning_belief_count: int
    first_query: int | None


def make_transducer(
    outputs: Sequence[Sequence[int]],
    transitions: Sequence[Sequence[int]],
) -> Transducer:
    return Transducer(
        outputs=tuple(
            tuple(int(value) for value in row)
            for row in outputs
        ),
        transitions=tuple(
            tuple(int(value) for value in row)
            for row in transitions
        ),
    )


def initial_belief(
    state_count: int,
    initial_states: Iterable[int] | None = None,
) -> Belief:
    if state_count < 2:
        raise ValueError("at least two latent states are required")
    if initial_states is None:
        initial_states = range(state_count)
    states = tuple(sorted(int(state) for state in initial_states))
    if not states:
        raise ValueError("initial-state set must be nonempty")
    if len(set(states)) != len(states):
        raise ValueError("initial-state set contains duplicates")
    if any(state < 0 or state >= state_count for state in states):
        raise ValueError("initial state outside state universe")
    return tuple((state, state) for state in states)


def validate_belief(machine: Transducer, belief: Belief) -> Belief:
    belief = tuple(
        sorted((int(initial), int(current)) for initial, current in belief)
    )
    if not belief:
        raise ValueError("belief must be nonempty")
    initial_labels = tuple(initial for initial, _ in belief)
    if len(set(initial_labels)) != len(initial_labels):
        raise ValueError("initial labels must be unique")
    if any(
        initial < 0
        or initial >= machine.state_count
        or current < 0
        or current >= machine.state_count
        for initial, current in belief
    ):
        raise ValueError("belief state outside machine universe")
    return belief


def branch_map(
    machine: Transducer,
    belief: Belief,
    query: int,
) -> dict[int, Belief]:
    belief = validate_belief(machine, belief)
    query = int(query)
    if query < 0 or query >= machine.query_count:
        raise ValueError("query outside query universe")
    branches: dict[int, list[tuple[int, int]]] = {}
    for initial, current in belief:
        output = machine.outputs[current][query]
        successor = machine.transitions[current][query]
        branches.setdefault(output, []).append((initial, successor))
    return {
        output: tuple(sorted(items))
        for output, items in sorted(branches.items())
    }


def has_irrecoverable_merge(belief: Belief) -> bool:
    currents = tuple(current for _, current in belief)
    return len(set(currents)) != len(currents)


def reachable_beliefs(
    machine: Transducer,
    start: Belief,
) -> tuple[Belief, ...]:
    start = validate_belief(machine, start)
    seen = {start}
    frontier = [start]
    while frontier:
        belief = frontier.pop()
        for query in range(machine.query_count):
            for branch in branch_map(machine, belief, query).values():
                if branch not in seen:
                    seen.add(branch)
                    frontier.append(branch)
    return tuple(sorted(seen, key=lambda item: (len(item), item)))


def validate_distortion(
    machine: Transducer,
    distortion: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    distortion = tuple(
        tuple(int(value) for value in row)
        for row in distortion
    )
    n = machine.state_count
    if len(distortion) != n or any(len(row) != n for row in distortion):
        raise ValueError("distortion must be a square state matrix")
    if any(value < 0 for row in distortion for value in row):
        raise ValueError("distortion must be nonnegative")
    return distortion


def solve_with_budget(
    machine: Transducer,
    distortion: Sequence[Sequence[int]],
    budget: int,
    initial_states: Iterable[int] | None = None,
) -> SolveResult:
    """Solve finite adaptive identify-and-terminate by least fixed point."""

    distortion = validate_distortion(machine, distortion)
    budget = int(budget)
    if budget < 0:
        raise ValueError("budget must be nonnegative")
    start = initial_belief(machine.state_count, initial_states)
    reachable = reachable_beliefs(machine, start)

    depth: dict[Belief, int] = {}
    choice: dict[Belief, int] = {}
    for belief in reachable:
        if len(belief) == 1:
            initial, current = belief[0]
            if distortion[initial][current] <= budget:
                depth[belief] = 0

    while True:
        additions: dict[Belief, tuple[int, int]] = {}
        for belief in reachable:
            if belief in depth or has_irrecoverable_merge(belief):
                continue
            candidates: list[tuple[int, int]] = []
            for query in range(machine.query_count):
                branches = tuple(
                    branch_map(machine, belief, query).values()
                )
                if all(branch in depth for branch in branches):
                    candidates.append(
                        (
                            1 + max(depth[branch] for branch in branches),
                            query,
                        )
                    )
            if candidates:
                additions[belief] = min(candidates)
        if not additions:
            break
        for belief, (candidate_depth, query) in additions.items():
            depth[belief] = candidate_depth
            choice[belief] = query

    return SolveResult(
        initial_belief=start,
        winning=start in depth,
        minimum_depth=depth.get(start),
        reachable_belief_count=len(reachable),
        winning_belief_count=len(depth),
        first_query=choice.get(start),
    )


def unconstrained_distortion(machine: Transducer) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(0 for _ in range(machine.state_count))
        for _ in range(machine.state_count)
    )


def identity_distortion(machine: Transducer) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(
            0 if initial == current else 1
            for current in range(machine.state_count)
        )
        for initial in range(machine.state_count)
    )


def identifies_initial_state(
    machine: Transducer,
    initial_states: Iterable[int] | None = None,
) -> SolveResult:
    return solve_with_budget(
        machine,
        unconstrained_distortion(machine),
        0,
        initial_states,
    )


def identifies_and_restores(
    machine: Transducer,
    initial_states: Iterable[int] | None = None,
) -> SolveResult:
    return solve_with_budget(
        machine,
        identity_distortion(machine),
        0,
        initial_states,
    )


def minimum_worst_disturbance(
    machine: Transducer,
    distortion: Sequence[Sequence[int]],
    initial_states: Iterable[int] | None = None,
) -> tuple[int | None, SolveResult | None]:
    distortion = validate_distortion(machine, distortion)
    for budget in sorted({value for row in distortion for value in row}):
        result = solve_with_budget(
            machine,
            distortion,
            budget,
            initial_states,
        )
        if result.winning:
            return budget, result
    return None, None


def maximum_identifiable_subset(machine: Transducer) -> int:
    states = tuple(range(machine.state_count))
    for size in range(machine.state_count, 0, -1):
        for subset in combinations(states, size):
            if identifies_initial_state(machine, subset).winning:
                return size
    raise AssertionError("a singleton initial state is always identified")


def classify(machine: Transducer) -> str:
    if not identifies_initial_state(machine).winning:
        return "unidentifiable"
    if identifies_and_restores(machine).winning:
        return "identify_and_restore"
    return "identify_only_altering"


def transition_is_permutation(machine: Transducer, query: int) -> bool:
    return {
        machine.transitions[state][query]
        for state in range(machine.state_count)
    } == set(range(machine.state_count))


def read_only_fixture(state_count: int = 3) -> Transducer:
    return make_transducer(
        outputs=((state,) for state in range(state_count)),
        transitions=((state,) for state in range(state_count)),
    )


def read_then_reset_fixture(state_count: int = 3) -> Transducer:
    return make_transducer(
        outputs=((state,) for state in range(state_count)),
        transitions=((0,) for _ in range(state_count)),
    )


def reset_then_read_fixture(state_count: int = 3) -> Transducer:
    return make_transducer(
        outputs=((0,) for _ in range(state_count)),
        transitions=((0,) for _ in range(state_count)),
    )


def reversible_flip_fixture() -> Transducer:
    return make_transducer(
        outputs=((0,), (1,)),
        transitions=((1,), (0,)),
    )


def pairwise_but_not_global_fixture() -> Transducer:
    """Every state pair separates immediately, but no global ADS exists."""

    return make_transducer(
        outputs=(
            (0, 0),
            (1, 0),
            (1, 1),
        ),
        transitions=(
            (0, 0),
            (1, 0),
            (1, 2),
        ),
    )
