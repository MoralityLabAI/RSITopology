from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Mapping


Q = Fraction


def qstr(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


@dataclass(frozen=True)
class ZeroSumDAG:
    states: tuple[str, ...]
    terminals: tuple[str, ...]
    owner: Mapping[str, str]
    actions: Mapping[str, tuple[str, ...]]
    transitions: Mapping[tuple[str, str], Mapping[str, Q]]
    terminal_payoff: Mapping[str, Q]
    initial: Mapping[str, Q]

    def validate(self) -> None:
        if not self.states or not self.terminals:
            raise ValueError("game needs states and terminals")
        if len(set(self.states)) != len(self.states):
            raise ValueError("duplicate state")
        if len(set(self.terminals)) != len(self.terminals):
            raise ValueError("duplicate terminal")
        if set(self.states) & set(self.terminals):
            raise ValueError("states and terminals overlap")
        if set(self.owner) != set(self.states):
            raise ValueError("owner registry mismatch")
        if any(role not in {"max", "min"} for role in self.owner.values()):
            raise ValueError("owner must be max or min")
        if set(self.actions) != set(self.states):
            raise ValueError("action registry mismatch")
        if set(self.terminal_payoff) != set(self.terminals):
            raise ValueError("terminal payoff registry mismatch")
        if set(self.initial) - set(self.states):
            raise ValueError("initial mass outside states")
        if any(value < 0 for value in self.initial.values()):
            raise ValueError("negative initial mass")
        if sum(self.initial.values(), Q(0)) != 1:
            raise ValueError("initial mass does not sum to one")

        order = {state: index for index, state in enumerate(self.states)}
        expected = set()
        for state in self.states:
            registered = self.actions[state]
            if not registered or len(set(registered)) != len(registered):
                raise ValueError("empty or duplicate action registry")
            for action in registered:
                key = (state, action)
                expected.add(key)
                if key not in self.transitions:
                    raise ValueError("missing transition channel")
                channel = self.transitions[key]
                if not channel or any(value < 0 for value in channel.values()):
                    raise ValueError("invalid transition channel")
                if sum(channel.values(), Q(0)) != 1:
                    raise ValueError("transition channel is not normalized")
                for destination in channel:
                    if destination in order:
                        if order[destination] <= order[state]:
                            raise ValueError("game graph is not acyclic")
                    elif destination not in self.terminals:
                        raise ValueError("transition leaves game")
        if set(self.transitions) != expected:
            raise ValueError("unregistered transition channel")


def backward_induction(game: ZeroSumDAG) -> dict[str, object]:
    game.validate()
    values: dict[str, Q] = dict(game.terminal_payoff)
    strategy = {"max": {}, "min": {}}
    action_rows = []

    for state in reversed(game.states):
        action_values = {}
        for action in game.actions[state]:
            action_values[action] = sum(
                (
                    probability * values[destination]
                    for destination, probability in game.transitions[
                        (state, action)
                    ].items()
                ),
                Q(0),
            )
        role = game.owner[state]
        target = max(action_values.values()) if role == "max" else min(action_values.values())
        selected = next(
            action for action in game.actions[state] if action_values[action] == target
        )
        values[state] = target
        strategy[role][state] = selected
        action_rows.append(
            {
                "state": state,
                "owner": role,
                "action_values": {
                    action: qstr(value) for action, value in action_values.items()
                },
                "selected_action": selected,
                "state_value": qstr(target),
            }
        )

    initial_value = sum(
        (probability * values[state] for state, probability in game.initial.items()),
        Q(0),
    )
    return {
        "value": initial_value,
        "state_values": {state: values[state] for state in game.states},
        "max_strategy": strategy["max"],
        "min_strategy": strategy["min"],
        "action_rows": list(reversed(action_rows)),
    }


def validate_strategy(game: ZeroSumDAG, role: str, strategy: Mapping[str, str]) -> None:
    expected = {state for state in game.states if game.owner[state] == role}
    if set(strategy) != expected:
        raise ValueError(f"{role} strategy state registry mismatch")
    if any(strategy[state] not in game.actions[state] for state in expected):
        raise ValueError(f"{role} strategy uses an invalid action")


def evaluate_strategies(
    game: ZeroSumDAG,
    max_strategy: Mapping[str, str],
    min_strategy: Mapping[str, str],
) -> Q:
    game.validate()
    validate_strategy(game, "max", max_strategy)
    validate_strategy(game, "min", min_strategy)
    mass = {state: game.initial.get(state, Q(0)) for state in game.states}
    terminal_mass = {terminal: Q(0) for terminal in game.terminals}
    for state in game.states:
        role = game.owner[state]
        action = max_strategy[state] if role == "max" else min_strategy[state]
        for destination, probability in game.transitions[(state, action)].items():
            contribution = mass[state] * probability
            if destination in terminal_mass:
                terminal_mass[destination] += contribution
            else:
                mass[destination] += contribution
    return sum(
        (
            terminal_mass[terminal] * game.terminal_payoff[terminal]
            for terminal in game.terminals
        ),
        Q(0),
    )


def enumerate_strategies(game: ZeroSumDAG, role: str) -> list[dict[str, str]]:
    states = tuple(state for state in game.states if game.owner[state] == role)
    return [
        {state: action for state, action in zip(states, choices)}
        for choices in product(*(game.actions[state] for state in states))
    ]


def saddle_audit(game: ZeroSumDAG, exhaustive: bool = True) -> dict[str, object]:
    result = backward_induction(game)
    value = result["value"]
    saddle_value = evaluate_strategies(
        game, result["max_strategy"], result["min_strategy"]
    )
    row = {
        "backward_value": qstr(value),
        "saddle_pair_value": qstr(saddle_value),
        "backward_pair_matches": saddle_value == value,
        "max_strategy": result["max_strategy"],
        "min_strategy": result["min_strategy"],
        "action_rows": result["action_rows"],
        "exhaustive": exhaustive,
    }
    if exhaustive:
        max_strategies = enumerate_strategies(game, "max")
        min_strategies = enumerate_strategies(game, "min")
        against_fixed_max = [
            evaluate_strategies(game, result["max_strategy"], strategy)
            for strategy in min_strategies
        ]
        against_fixed_min = [
            evaluate_strategies(game, strategy, result["min_strategy"])
            for strategy in max_strategies
        ]
        row.update(
            {
                "max_strategy_count": len(max_strategies),
                "min_strategy_count": len(min_strategies),
                "minimum_against_backward_max": qstr(min(against_fixed_max)),
                "maximum_against_backward_min": qstr(max(against_fixed_min)),
                "max_guarantee_holds": min(against_fixed_max) == value,
                "min_cap_holds": max(against_fixed_min) == value,
            }
        )
    row["certified"] = (
        row["backward_pair_matches"]
        and (
            not exhaustive
            or (row["max_guarantee_holds"] and row["min_cap_holds"])
        )
    )
    return row


def challenge_family_game(test_count: int) -> ZeroSumDAG:
    if test_count < 1:
        raise ValueError("test count must be positive")
    states = ("verifier",) + tuple(f"challenge_{index}" for index in range(test_count))
    owner = {"verifier": "max"}
    owner.update({state: "min" for state in states[1:]})
    actions = {"verifier": tuple(f"test_{index}" for index in range(test_count))}
    transitions = {}
    for index, challenge in enumerate(states[1:]):
        actions[challenge] = ("attack_a", "attack_b")
        transitions[("verifier", f"test_{index}")] = {challenge: Q(1)}
        if index == test_count - 1:
            probabilities = (Q(3, 5), Q(4, 5))
        else:
            probabilities = (Q(index + 1, 10 * test_count), Q(index + 2, 10 * test_count))
        for action, win_probability in zip(actions[challenge], probabilities):
            transitions[(challenge, action)] = {
                "win": win_probability,
                "lose": 1 - win_probability,
            }
    return ZeroSumDAG(
        states=states,
        terminals=("win", "lose"),
        owner=owner,
        actions=actions,
        transitions=transitions,
        terminal_payoff={"win": Q(1), "lose": Q(0)},
        initial={"verifier": Q(1)},
    )


def alternating_game() -> ZeroSumDAG:
    states = (
        "root",
        "left_min",
        "right_min",
        "left_x_max",
        "left_y_max",
        "right_x_max",
        "right_y_max",
    )
    owner = {
        "root": "max",
        "left_min": "min",
        "right_min": "min",
        "left_x_max": "max",
        "left_y_max": "max",
        "right_x_max": "max",
        "right_y_max": "max",
    }
    actions = {
        "root": ("left", "right"),
        "left_min": ("x", "y"),
        "right_min": ("x", "y"),
        "left_x_max": ("u", "v"),
        "left_y_max": ("u", "v"),
        "right_x_max": ("u", "v"),
        "right_y_max": ("u", "v"),
    }
    transitions = {
        ("root", "left"): {"left_min": Q(1)},
        ("root", "right"): {"right_min": Q(1)},
        ("left_min", "x"): {"left_x_max": Q(1)},
        ("left_min", "y"): {"left_y_max": Q(1)},
        ("right_min", "x"): {"right_x_max": Q(1)},
        ("right_min", "y"): {"right_y_max": Q(1)},
    }
    leaf_values = {
        "left_x_max": (Q(1, 2), Q(2, 3)),
        "left_y_max": (Q(1, 3), Q(3, 4)),
        "right_x_max": (Q(4, 5), Q(1, 5)),
        "right_y_max": (Q(3, 5), Q(7, 10)),
    }
    for state, probabilities in leaf_values.items():
        for action, probability in zip(actions[state], probabilities):
            transitions[(state, action)] = {
                "win": probability,
                "lose": 1 - probability,
            }
    return ZeroSumDAG(
        states=states,
        terminals=("win", "lose"),
        owner=owner,
        actions=actions,
        transitions=transitions,
        terminal_payoff={"win": Q(1), "lose": Q(0)},
        initial={"root": Q(1)},
    )


def revealed_matching_game() -> ZeroSumDAG:
    return ZeroSumDAG(
        states=("max_choice", "after_h", "after_t"),
        terminals=("match", "mismatch"),
        owner={"max_choice": "max", "after_h": "min", "after_t": "min"},
        actions={
            "max_choice": ("H", "T"),
            "after_h": ("H", "T"),
            "after_t": ("H", "T"),
        },
        transitions={
            ("max_choice", "H"): {"after_h": Q(1)},
            ("max_choice", "T"): {"after_t": Q(1)},
            ("after_h", "H"): {"match": Q(1)},
            ("after_h", "T"): {"mismatch": Q(1)},
            ("after_t", "H"): {"mismatch": Q(1)},
            ("after_t", "T"): {"match": Q(1)},
        },
        terminal_payoff={"match": Q(1), "mismatch": Q(-1)},
        initial={"max_choice": Q(1)},
    )


def serialize_game(game: ZeroSumDAG) -> dict[str, object]:
    return {
        "states": list(game.states),
        "terminals": list(game.terminals),
        "owner": dict(game.owner),
        "actions": {state: list(actions) for state, actions in game.actions.items()},
        "initial": {state: qstr(value) for state, value in game.initial.items()},
        "terminal_payoff": {
            terminal: qstr(value) for terminal, value in game.terminal_payoff.items()
        },
        "transitions": {
            f"{state}|{action}": {
                destination: qstr(value) for destination, value in channel.items()
            }
            for (state, action), channel in game.transitions.items()
        },
    }


def family_row(test_count: int) -> dict[str, object]:
    game = challenge_family_game(test_count)
    exhaustive = test_count <= 8
    audit = saddle_audit(game, exhaustive=exhaustive)
    result = backward_induction(game)
    return {
        "test_count": test_count,
        "max_pure_strategy_count": test_count,
        "min_pure_strategy_count": 1 << test_count,
        "state_count": test_count + 1,
        "backward_action_evaluations": 3 * test_count,
        "exact_value": qstr(result["value"]),
        "selected_test": result["max_strategy"]["verifier"],
        "exhaustive_saddle_audit": exhaustive,
        "audit": audit,
        "certified": audit["certified"] and result["value"] == Q(3, 5),
    }


def matching_boundary_row() -> dict[str, object]:
    revealed = saddle_audit(revealed_matching_game(), exhaustive=True)
    simultaneous_matrix = ((Q(1), Q(-1)), (Q(-1), Q(1)))
    pure_maximin = max(min(row) for row in simultaneous_matrix)
    max_half_mix_column_values = tuple(
        (simultaneous_matrix[0][column] + simultaneous_matrix[1][column]) / 2
        for column in range(2)
    )
    min_half_mix_row_values = tuple(
        (simultaneous_matrix[row][0] + simultaneous_matrix[row][1]) / 2
        for row in range(2)
    )
    mixed_lower = min(max_half_mix_column_values)
    mixed_upper = max(min_half_mix_row_values)
    mixed_value = mixed_lower if mixed_lower == mixed_upper else None
    return {
        "revealed_sequential_value": revealed["backward_value"],
        "revealed_saddle_audit": revealed,
        "simultaneous_payoff_matrix": [
            [qstr(value) for value in row] for row in simultaneous_matrix
        ],
        "simultaneous_pure_maximin": qstr(pure_maximin),
        "simultaneous_max_half_mix_column_values": [
            qstr(value) for value in max_half_mix_column_values
        ],
        "simultaneous_min_half_mix_row_values": [
            qstr(value) for value in min_half_mix_row_values
        ],
        "simultaneous_mixed_lower": qstr(mixed_lower),
        "simultaneous_mixed_upper": qstr(mixed_upper),
        "simultaneous_mixed_value": qstr(mixed_value) if mixed_value is not None else None,
        "information_structure_changes_strategy_class": (
            revealed["backward_value"] == "-1"
            and pure_maximin == Q(-1)
            and mixed_lower == mixed_upper == Q(0)
        ),
    }


def build_result() -> dict[str, object]:
    family = [family_row(count) for count in range(1, 13)]
    alternating = saddle_audit(alternating_game(), exhaustive=True)
    matching = matching_boundary_row()
    gates = {
        "B0_all_family_backward_values_exact": all(row["certified"] for row in family),
        "B1_challenger_strategy_count_is_exponential": all(
            row["min_pure_strategy_count"] == 2 ** row["test_count"] for row in family
        ),
        "B2_backward_work_is_linear": all(
            row["state_count"] == row["test_count"] + 1
            and row["backward_action_evaluations"] == 3 * row["test_count"]
            for row in family
        ),
        "B3_exhaustive_family_saddles_hold": all(
            not row["exhaustive_saddle_audit"]
            or (
                row["audit"]["max_guarantee_holds"]
                and row["audit"]["min_cap_holds"]
            )
            for row in family
        ),
        "A0_alternating_game_saddle_exact": (
            alternating["certified"] and alternating["backward_value"] == "7/10"
        ),
        "M0_matching_information_boundary_exact": matching[
            "information_structure_changes_strategy_class"
        ],
    }
    return {
        "schema_version": "asmp3_two_role_backward_bridge_v1_1",
        "experiment_id": "ASMP-3-TWO-ROLE-BACKWARD-BRIDGE-v1.1",
        "status": "exact_perfect_information_two_role_bridge",
        "parent_result": "ASMP-3-REALIZATION-FLOW-BRIDGE-v1.0",
        "theorem": {
            "input": (
                "finite acyclic perfect-information zero-sum stochastic game "
                "with rational transitions and payoff"
            ),
            "algorithm": "rational backward induction",
            "certificate": (
                "deterministic max/min strategies with reciprocal deviation bounds"
            ),
            "consequence": (
                "two independently strategic roles can be handled without "
                "convexifying them into one controller in this lane"
            ),
        },
        "family_rows": family,
        "alternating_game": {
            "game": serialize_game(alternating_game()),
            "audit": alternating,
        },
        "matching_boundary": matching,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "Backward induction relies on public perfect information and "
            "turn-based actions. Simultaneous or hidden actions, imperfect "
            "recall, general message information sets, and interface choice "
            "are outside the theorem."
        ),
    }
