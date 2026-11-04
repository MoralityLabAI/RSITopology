"""Fresh-cell helpers for the ASMP-9 v0.10 verification."""

from __future__ import annotations

import random
from collections import Counter
from fractions import Fraction
from itertools import combinations
from typing import Any, Iterable

from mdp_access import (
    TransitionKernel,
    action_difference_matrix,
    baseline_pair_intersection_dimension,
    cyclic_action_kernel,
    deterministic_kernels,
    deterministic_policy_witness,
    matrix_rank,
    residual_reward_ambiguity_dimension,
    self_loop_kernel,
    shaping_matrix,
    successor_difference_components,
    trajectory_ambiguity_dimension,
)


def rational_stochastic_kernel(
    state_count: int,
    action_count: int,
    rng: random.Random,
    maximum_weight: int,
) -> TransitionKernel:
    states = []
    for _state in range(state_count):
        actions = []
        for _action in range(action_count):
            weights = [
                rng.randint(1, maximum_weight) for _ in range(state_count)
            ]
            total = sum(weights)
            actions.append(tuple(Fraction(value, total) for value in weights))
        states.append(tuple(actions))
    return tuple(states)


def run_stochastic_cells(spec: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(int(spec["seed"]))
    discounts = tuple(Fraction(value) for value in spec["discounts"])
    shaping_rank_mismatch_count = 0
    intersection_mismatch_count = 0
    ambiguity_distribution: Counter[int] = Counter()
    state_distribution: Counter[int] = Counter()
    action_distribution: Counter[int] = Counter()
    discount_distribution: Counter[str] = Counter()
    total = 0
    for _ in range(int(spec["count"])):
        state_count = rng.randint(
            int(spec["minimum_states"]), int(spec["maximum_states"])
        )
        action_count = rng.randint(
            int(spec["minimum_actions"]), int(spec["maximum_actions"])
        )
        discount = discounts[rng.randrange(len(discounts))]
        kernel = rational_stochastic_kernel(
            state_count,
            action_count,
            rng,
            int(spec["maximum_weight"]),
        )
        shaping_rank_mismatch_count += int(
            matrix_rank(shaping_matrix(kernel, discount)) != state_count
        )
        observed = baseline_pair_intersection_dimension(kernel, discount)
        expected = state_count - matrix_rank(
            action_difference_matrix(kernel)
        )
        intersection_mismatch_count += int(observed != expected)
        ambiguity_distribution[observed] += 1
        state_distribution[state_count] += 1
        action_distribution[action_count] += 1
        discount_distribution[str(discount)] += 1
        total += 1
    return {
        **spec,
        "discounts": [str(value) for value in discounts],
        "actual_count": total,
        "shaping_rank_mismatch_count": shaping_rank_mismatch_count,
        "intersection_mismatch_count": intersection_mismatch_count,
        "ambiguity_distribution": dict(
            sorted(ambiguity_distribution.items())
        ),
        "state_distribution": dict(sorted(state_distribution.items())),
        "action_distribution": dict(sorted(action_distribution.items())),
        "discount_distribution": dict(
            sorted(discount_distribution.items())
        ),
    }


def run_deterministic_census(spec: dict[str, Any]) -> dict[str, Any]:
    state_count = int(spec["state_count"])
    action_count = int(spec["action_count"])
    discount = Fraction(spec["discount"])
    component_distribution: Counter[int] = Counter()
    rank_mismatch_count = 0
    intersection_mismatch_count = 0
    total = 0
    for kernel in deterministic_kernels(state_count, action_count):
        components = successor_difference_components(kernel)
        rank_dimension = state_count - matrix_rank(
            action_difference_matrix(kernel)
        )
        intersection = baseline_pair_intersection_dimension(kernel, discount)
        rank_mismatch_count += int(rank_dimension != components)
        intersection_mismatch_count += int(intersection != components)
        component_distribution[components] += 1
        total += 1
    return {
        **spec,
        "discount": str(discount),
        "count": total,
        "component_distribution": dict(
            sorted(component_distribution.items())
        ),
        "connected_count": component_distribution[1],
        "rank_mismatch_count": rank_mismatch_count,
        "intersection_mismatch_count": intersection_mismatch_count,
    }


def run_structured_cells(spec: dict[str, Any]) -> dict[str, Any]:
    transition_discount = Fraction(spec["transition_discount"])
    gamma_left = Fraction(spec["discount_pair"][0])
    gamma_right = Fraction(spec["discount_pair"][1])
    rows = []
    mismatch_count = 0
    for state_count in map(int, spec["state_counts"]):
        cyclic = cyclic_action_kernel(state_count, 2)
        baseline = self_loop_kernel(state_count, 2)
        single = residual_reward_ambiguity_dimension(
            ((cyclic, gamma_left),)
        )
        transition_pair = residual_reward_ambiguity_dimension(
            (
                (baseline, transition_discount),
                (cyclic, transition_discount),
            )
        )
        same_discount = residual_reward_ambiguity_dimension(
            (
                (cyclic, gamma_left),
                (cyclic, gamma_left),
            )
        )
        distinct_discount = residual_reward_ambiguity_dimension(
            (
                (cyclic, gamma_left),
                (cyclic, gamma_right),
            )
        )
        witness = deterministic_policy_witness(
            state_count, transition_discount
        )
        passed = (
            single == state_count
            and transition_pair == 1
            and same_discount == state_count
            and distinct_discount == 1
            and witness["same_strict_policy"]
            and witness["common_gauge_dimension"] == 1
            and not witness["difference_is_common_constant"]
        )
        mismatch_count += int(not passed)
        rows.append(
            {
                "state_count": state_count,
                "single_environment_ambiguity": single,
                "transition_pair_ambiguity": transition_pair,
                "same_discount_pair_ambiguity": same_discount,
                "distinct_discount_pair_ambiguity": distinct_discount,
                "deterministic_witness_passed": bool(
                    witness["same_strict_policy"]
                    and witness["common_gauge_dimension"] == 1
                    and not witness["difference_is_common_constant"]
                ),
                "deterministic_base_gap": str(
                    witness["base_minimum_gap"]
                ),
                "deterministic_perturbed_gap": str(
                    witness["perturbed_minimum_gap"]
                ),
            }
        )
    return {
        **spec,
        "transition_discount": str(transition_discount),
        "discount_pair": [str(gamma_left), str(gamma_right)],
        "rows": rows,
        "mismatch_count": mismatch_count,
    }


def graph_component_count(
    vertex_count: int, edges: Iterable[tuple[int, int]]
) -> int:
    adjacency = [set() for _ in range(vertex_count)]
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    unseen = set(range(vertex_count))
    count = 0
    while unseen:
        count += 1
        stack = [unseen.pop()]
        while stack:
            vertex = stack.pop()
            for neighbor in adjacency[vertex] & unseen:
                unseen.remove(neighbor)
                stack.append(neighbor)
    return count


def run_trajectory_census(spec: dict[str, Any]) -> dict[str, Any]:
    coordinate_count = int(spec["coordinate_count"])
    universe = tuple(combinations(range(coordinate_count), 2))
    if len(universe) > 20:
        raise ValueError("registered exhaustive mask universe is too large")
    ambiguity_distribution: Counter[int] = Counter()
    connected_by_query_count: Counter[int] = Counter()
    mismatch_count = 0
    for mask in range(1 << len(universe)):
        edges = tuple(
            edge
            for index, edge in enumerate(universe)
            if mask & (1 << index)
        )
        components = graph_component_count(coordinate_count, edges)
        ambiguity = trajectory_ambiguity_dimension(
            coordinate_count, edges
        )
        mismatch_count += int(components != ambiguity)
        ambiguity_distribution[ambiguity] += 1
        if components == 1:
            connected_by_query_count[len(edges)] += 1
    minimum_connected_queries = min(connected_by_query_count, default=None)
    return {
        **spec,
        "query_edge_universe_size": len(universe),
        "graph_count": 1 << len(universe),
        "ambiguity_distribution": dict(
            sorted(ambiguity_distribution.items())
        ),
        "connected_by_query_count": dict(
            sorted(connected_by_query_count.items())
        ),
        "minimum_connected_queries": minimum_connected_queries,
        "component_mismatch_count": mismatch_count,
    }
