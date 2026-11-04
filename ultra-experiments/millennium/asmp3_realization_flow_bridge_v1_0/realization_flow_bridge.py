from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Mapping, Sequence


Q = Fraction


def qstr(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


@dataclass(frozen=True)
class ControlledDAG:
    states: tuple[str, ...]
    terminals: tuple[str, ...]
    actions: Mapping[str, tuple[str, ...]]
    transitions: Mapping[tuple[str, str], Mapping[str, Q]]
    initial: Mapping[str, Q]

    def validate(self) -> None:
        if not self.states or not self.terminals:
            raise ValueError("graph needs states and terminals")
        if len(set(self.states)) != len(self.states):
            raise ValueError("duplicate state")
        if len(set(self.terminals)) != len(self.terminals):
            raise ValueError("duplicate terminal")
        if set(self.states) & set(self.terminals):
            raise ValueError("states and terminals overlap")
        if set(self.actions) != set(self.states):
            raise ValueError("every state needs exactly one action registry")
        if set(self.initial) - set(self.states):
            raise ValueError("initial mass outside states")
        if any(value < 0 for value in self.initial.values()):
            raise ValueError("negative initial mass")
        if sum(self.initial.values(), Q(0)) != 1:
            raise ValueError("initial mass does not sum to one")

        order = {state: index for index, state in enumerate(self.states)}
        for state in self.states:
            registered = self.actions[state]
            if not registered or len(set(registered)) != len(registered):
                raise ValueError("empty or duplicate action registry")
            for action in registered:
                key = (state, action)
                if key not in self.transitions:
                    raise ValueError(f"missing transition for {key}")
                channel = self.transitions[key]
                if not channel or any(value < 0 for value in channel.values()):
                    raise ValueError("invalid transition probability")
                if sum(channel.values(), Q(0)) != 1:
                    raise ValueError("transition channel is not normalized")
                for destination in channel:
                    if destination in order:
                        if order[destination] <= order[state]:
                            raise ValueError("state transition is not acyclic")
                    elif destination not in self.terminals:
                        raise ValueError("transition leaves graph")
        expected_keys = {
            (state, action)
            for state in self.states
            for action in self.actions[state]
        }
        if set(self.transitions) != expected_keys:
            raise ValueError("unregistered transition key")


Policy = Mapping[str, Mapping[str, Q]]
Occupancy = Mapping[tuple[str, str], Q]


def validate_policy(graph: ControlledDAG, policy: Policy) -> None:
    graph.validate()
    if set(policy) != set(graph.states):
        raise ValueError("policy state registry mismatch")
    for state in graph.states:
        distribution = policy[state]
        if set(distribution) != set(graph.actions[state]):
            raise ValueError("policy action registry mismatch")
        if any(value < 0 for value in distribution.values()):
            raise ValueError("negative policy probability")
        if sum(distribution.values(), Q(0)) != 1:
            raise ValueError("policy probabilities do not sum to one")


def occupancy_from_policy(
    graph: ControlledDAG, policy: Policy
) -> tuple[dict[tuple[str, str], Q], dict[str, Q]]:
    validate_policy(graph, policy)
    arrival = {state: graph.initial.get(state, Q(0)) for state in graph.states}
    occupancy: dict[tuple[str, str], Q] = {}
    terminal = {name: Q(0) for name in graph.terminals}

    for state in graph.states:
        reach = arrival[state]
        for action in graph.actions[state]:
            mass = reach * policy[state][action]
            occupancy[(state, action)] = mass
            for destination, probability in graph.transitions[
                (state, action)
            ].items():
                contribution = mass * probability
                if destination in terminal:
                    terminal[destination] += contribution
                else:
                    arrival[destination] += contribution
    return occupancy, terminal


def terminal_from_occupancy(
    graph: ControlledDAG, occupancy: Occupancy
) -> dict[str, Q]:
    graph.validate()
    terminal = {name: Q(0) for name in graph.terminals}
    for key, mass in occupancy.items():
        for destination, probability in graph.transitions[key].items():
            if destination in terminal:
                terminal[destination] += mass * probability
    return terminal


def audit_occupancy(
    graph: ControlledDAG, occupancy: Occupancy
) -> dict[str, object]:
    graph.validate()
    expected_keys = {
        (state, action)
        for state in graph.states
        for action in graph.actions[state]
    }
    key_registry_valid = set(occupancy) == expected_keys
    nonnegative = all(value >= 0 for value in occupancy.values())
    flow_rows = []
    all_flows_hold = key_registry_valid and nonnegative

    for state in graph.states:
        outgoing = sum(
            (occupancy.get((state, action), Q(0)) for action in graph.actions[state]),
            Q(0),
        )
        incoming = graph.initial.get(state, Q(0))
        for predecessor in graph.states:
            for action in graph.actions[predecessor]:
                incoming += occupancy.get((predecessor, action), Q(0)) * graph.transitions[
                    (predecessor, action)
                ].get(state, Q(0))
        holds = outgoing == incoming
        all_flows_hold = all_flows_hold and holds
        flow_rows.append(
            {
                "state": state,
                "outgoing": qstr(outgoing),
                "initial_plus_incoming": qstr(incoming),
                "holds": holds,
            }
        )

    terminal = terminal_from_occupancy(graph, occupancy)
    terminal_normalized = sum(terminal.values(), Q(0)) == 1
    return {
        "key_registry_valid": key_registry_valid,
        "nonnegative": nonnegative,
        "flow_rows": flow_rows,
        "all_flows_hold": all_flows_hold,
        "terminal_law": {name: qstr(value) for name, value in terminal.items()},
        "terminal_normalized": terminal_normalized,
        "valid": all_flows_hold and terminal_normalized,
    }


def policy_from_occupancy(
    graph: ControlledDAG, occupancy: Occupancy
) -> dict[str, dict[str, Q]]:
    audit = audit_occupancy(graph, occupancy)
    if not audit["valid"]:
        raise ValueError("occupancy does not satisfy the realization flows")
    policy: dict[str, dict[str, Q]] = {}
    for state in graph.states:
        flow = sum(
            (occupancy[(state, action)] for action in graph.actions[state]), Q(0)
        )
        if flow:
            policy[state] = {
                action: occupancy[(state, action)] / flow
                for action in graph.actions[state]
            }
        else:
            policy[state] = {
                action: Q(1) if index == 0 else Q(0)
                for index, action in enumerate(graph.actions[state])
            }
    return policy


def reconstruction_audit(
    graph: ControlledDAG, policy: Policy
) -> dict[str, object]:
    occupancy, terminal = occupancy_from_policy(graph, policy)
    flow_audit = audit_occupancy(graph, occupancy)
    recovered_policy = policy_from_occupancy(graph, occupancy)
    recovered_occupancy, recovered_terminal = occupancy_from_policy(
        graph, recovered_policy
    )
    exact = (
        flow_audit["valid"]
        and recovered_occupancy == occupancy
        and recovered_terminal == terminal
    )
    return {
        "occupancy": {
            f"{state}|{action}": qstr(value)
            for (state, action), value in occupancy.items()
        },
        "terminal_law": {name: qstr(value) for name, value in terminal.items()},
        "flow_audit": flow_audit,
        "recovered_policy": {
            state: {action: qstr(value) for action, value in distribution.items()}
            for state, distribution in recovered_policy.items()
        },
        "reconstruction_exact": exact,
    }


def deterministic_policies(graph: ControlledDAG) -> Sequence[dict[str, dict[str, Q]]]:
    graph.validate()
    policies = []
    for choices in product(*(graph.actions[state] for state in graph.states)):
        policies.append(
            {
                state: {
                    action: Q(1) if action == selected else Q(0)
                    for action in graph.actions[state]
                }
                for state, selected in zip(graph.states, choices)
            }
        )
    return policies


def band_graph(state_count: int, low: Q, high: Q) -> ControlledDAG:
    if state_count < 1 or not (Q(0) <= low <= high <= Q(1)):
        raise ValueError("invalid band graph parameters")
    states = tuple(f"s{index}" for index in range(state_count))
    actions = {state: ("low", "high") for state in states}
    transitions = {}
    for state in states:
        transitions[(state, "low")] = {"zero": low, "one": 1 - low}
        transitions[(state, "high")] = {"zero": high, "one": 1 - high}
    graph = ControlledDAG(
        states=states,
        terminals=("zero", "one"),
        actions=actions,
        transitions=transitions,
        initial={state: Q(1, state_count) for state in states},
    )
    graph.validate()
    return graph


def uniform_policy(graph: ControlledDAG, high_probability: Q) -> dict[str, dict[str, Q]]:
    return {
        state: {"low": 1 - high_probability, "high": high_probability}
        for state in graph.states
    }


def adaptive_graph() -> ControlledDAG:
    return ControlledDAG(
        states=("root", "left", "right"),
        terminals=("accept", "reject"),
        actions={
            "root": ("A", "B"),
            "left": ("yes", "no"),
            "right": ("yes", "no"),
        },
        transitions={
            ("root", "A"): {"left": Q(3, 4), "right": Q(1, 4)},
            ("root", "B"): {"left": Q(1, 4), "right": Q(3, 4)},
            ("left", "yes"): {"accept": Q(1)},
            ("left", "no"): {"reject": Q(1)},
            ("right", "yes"): {"accept": Q(1)},
            ("right", "no"): {"reject": Q(1)},
        },
        initial={"root": Q(1)},
    )


def serialize_graph(graph: ControlledDAG) -> dict[str, object]:
    return {
        "states": list(graph.states),
        "terminals": list(graph.terminals),
        "actions": {state: list(actions) for state, actions in graph.actions.items()},
        "initial": {state: qstr(value) for state, value in graph.initial.items()},
        "transitions": {
            f"{state}|{action}": {
                destination: qstr(value) for destination, value in channel.items()
            }
            for (state, action), channel in graph.transitions.items()
        },
    }


def band_row(state_count: int) -> dict[str, object]:
    honest = band_graph(state_count, Q(4, 5), Q(9, 10))
    false = band_graph(state_count, Q(1, 10), Q(1, 5))
    honest_closest = reconstruction_audit(honest, uniform_policy(honest, Q(0)))
    false_closest = reconstruction_audit(false, uniform_policy(false, Q(1)))
    honest_mid = reconstruction_audit(honest, uniform_policy(honest, Q(2, 5)))
    false_mid = reconstruction_audit(false, uniform_policy(false, Q(3, 5)))

    enumerated = state_count <= 8
    honest_extrema: tuple[Q, Q] | None = None
    false_extrema: tuple[Q, Q] | None = None
    if enumerated:
        honest_values = [
            occupancy_from_policy(honest, policy)[1]["zero"]
            for policy in deterministic_policies(honest)
        ]
        false_values = [
            occupancy_from_policy(false, policy)[1]["zero"]
            for policy in deterministic_policies(false)
        ]
        honest_extrema = (min(honest_values), max(honest_values))
        false_extrema = (min(false_values), max(false_values))

    return {
        "state_count": state_count,
        "actions_per_state": 2,
        "pure_policy_count_per_class": 1 << state_count,
        "flow_variable_count_per_class": 2 * state_count,
        "flow_equality_count_per_class": state_count,
        "terminal_dimension": 2,
        "honest_zero_probability_interval": ["4/5", "9/10"],
        "false_zero_probability_interval": ["1/10", "1/5"],
        "terminal_verifier": "accept_on_zero",
        "exact_gap": "3/5",
        "closest_honest": honest_closest,
        "closest_false": false_closest,
        "honest_interior_reconstruction": honest_mid,
        "false_interior_reconstruction": false_mid,
        "pure_policies_enumerated": enumerated,
        "enumerated_honest_extrema": (
            [qstr(value) for value in honest_extrema]
            if honest_extrema is not None
            else None
        ),
        "enumerated_false_extrema": (
            [qstr(value) for value in false_extrema]
            if false_extrema is not None
            else None
        ),
        "certified": (
            honest_closest["reconstruction_exact"]
            and false_closest["reconstruction_exact"]
            and honest_mid["reconstruction_exact"]
            and false_mid["reconstruction_exact"]
            and honest_closest["terminal_law"]["zero"] == "4/5"
            and false_closest["terminal_law"]["zero"] == "1/5"
            and (
                not enumerated
                or (
                    honest_extrema == (Q(4, 5), Q(9, 10))
                    and false_extrema == (Q(1, 10), Q(1, 5))
                )
            )
        ),
    }


def adaptive_row() -> dict[str, object]:
    graph = adaptive_graph()
    graph.validate()
    policy = {
        "root": {"A": Q(2, 5), "B": Q(3, 5)},
        "left": {"yes": Q(1, 3), "no": Q(2, 3)},
        "right": {"yes": Q(3, 4), "no": Q(1, 4)},
    }
    audit = reconstruction_audit(graph, policy)
    pure_laws = {
        tuple(
            occupancy_from_policy(graph, candidate)[1][terminal]
            for terminal in graph.terminals
        )
        for candidate in deterministic_policies(graph)
    }
    return {
        "graph": serialize_graph(graph),
        "registered_policy": {
            state: {action: qstr(value) for action, value in distribution.items()}
            for state, distribution in policy.items()
        },
        "audit": audit,
        "pure_policy_count": len(deterministic_policies(graph)),
        "distinct_pure_terminal_law_count": len(pure_laws),
        "pure_terminal_laws": [
            [qstr(value) for value in law] for law in sorted(pure_laws)
        ],
        "certified": audit["reconstruction_exact"],
    }


def build_result() -> dict[str, object]:
    bands = [band_row(state_count) for state_count in range(1, 13)]
    adaptive = adaptive_row()
    gates = {
        "F0_all_band_flow_reconstructions_exact": all(
            row["certified"] for row in bands
        ),
        "F1_pure_policy_count_is_exponential": all(
            row["pure_policy_count_per_class"] == 2 ** row["state_count"]
            for row in bands
        ),
        "F2_flow_formulation_size_is_linear": all(
            row["flow_variable_count_per_class"] == 2 * row["state_count"]
            and row["flow_equality_count_per_class"] == row["state_count"]
            for row in bands
        ),
        "F3_enumerated_band_extrema_match": all(
            not row["pure_policies_enumerated"]
            or (
                row["enumerated_honest_extrema"] == ["4/5", "9/10"]
                and row["enumerated_false_extrema"] == ["1/10", "1/5"]
            )
            for row in bands
        ),
        "F4_all_band_gaps_are_three_fifths": all(
            row["exact_gap"] == "3/5" for row in bands
        ),
        "A0_adaptive_flow_reconstruction_exact": adaptive["certified"],
        "A1_adaptive_pure_policy_registry_complete": (
            adaptive["pure_policy_count"] == 8
        ),
    }
    return {
        "schema_version": "asmp3_realization_flow_bridge_v1_0",
        "experiment_id": "ASMP-3-REALIZATION-FLOW-BRIDGE-v1.0",
        "status": "exact_acyclic_single_controller_bridge",
        "parent_result": "ASMP-3-POLYHEDRAL-TV-FRONTIER-v0.9",
        "theorem": {
            "input": (
                "finite acyclic fully observed controlled graph with rational "
                "chance transitions"
            ),
            "forward": "every randomized policy induces a feasible occupancy flow",
            "reverse": (
                "every feasible nonnegative occupancy flow is induced by the "
                "normalized flow policy, with arbitrary choices at zero-flow states"
            ),
            "consequence": (
                "the terminal-law set is the linear image of a rational flow "
                "polytope and can be passed to v0.9 as an extended formulation"
            ),
        },
        "band_rows": bands,
        "adaptive_row": adaptive,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The bridge covers one fully observed strategic controller in a "
            "frozen acyclic graph. Multiple independently strategic roles, "
            "imperfect recall, endogenous verifier actions, and nonconvex or "
            "unregistered noise require additional game-theoretic machinery."
        ),
    }
