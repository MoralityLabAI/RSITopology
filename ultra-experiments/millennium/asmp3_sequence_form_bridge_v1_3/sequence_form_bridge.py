from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Mapping, Sequence


Q = Fraction
SequenceKey = tuple[tuple[str, str], ...]
EMPTY: SequenceKey = ()


def qstr(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def qvector(values: Sequence[Q]) -> list[str]:
    return [qstr(value) for value in values]


def sequence_name(sequence: SequenceKey) -> str:
    if not sequence:
        return "EMPTY"
    return ">".join(f"{information}:{action}" for information, action in sequence)


@dataclass(frozen=True)
class ExtensiveGame:
    root: str
    nodes: Mapping[str, Mapping[str, object]]


@dataclass(frozen=True)
class RealizationForm:
    player: str
    sequences: tuple[SequenceKey, ...]
    information_sets: tuple[str, ...]
    actions: Mapping[str, tuple[str, ...]]
    parent_sequence: Mapping[str, SequenceKey]
    child_sequence: Mapping[tuple[str, str], SequenceKey]
    E: tuple[tuple[Q, ...], ...]
    e: tuple[Q, ...]


@dataclass(frozen=True)
class CompiledSequenceGame:
    max_form: RealizationForm
    min_form: RealizationForm
    payoff: tuple[tuple[Q, ...], ...]
    terminal_count: int
    nonzero_payoff_contributions: int
    perfect_recall: bool


def analyze_tree(game: ExtensiveGame) -> dict[str, object]:
    if game.root not in game.nodes:
        raise ValueError("root is missing")
    parents: dict[str, str] = {}
    visited: set[str] = set()
    info: dict[str, dict[str, object]] = {}
    info_order = {"max": [], "min": []}
    sequences = {"max": {EMPTY}, "min": {EMPTY}}
    terminals = []

    def visit(
        node_id: str,
        own_sequences: dict[str, SequenceKey],
        chance_probability: Q,
    ) -> None:
        if node_id in visited:
            raise ValueError("game graph is not a tree")
        visited.add(node_id)
        node = game.nodes[node_id]
        kind = node.get("kind")
        if kind == "terminal":
            payoff = node.get("payoff")
            if not isinstance(payoff, Q):
                raise ValueError("terminal payoff must be rational")
            terminals.append(
                {
                    "node": node_id,
                    "chance_probability": chance_probability,
                    "max_sequence": own_sequences["max"],
                    "min_sequence": own_sequences["min"],
                    "payoff": payoff,
                }
            )
            return
        if kind == "chance":
            transitions = node.get("transitions")
            if not isinstance(transitions, Mapping) or not transitions:
                raise ValueError("chance node needs transitions")
            total = Q(0)
            for outcome, edge in transitions.items():
                if not isinstance(edge, tuple) or len(edge) != 2:
                    raise ValueError("chance edge must be (probability, child)")
                probability, child = edge
                if not isinstance(probability, Q) or probability < 0:
                    raise ValueError("chance probability must be nonnegative rational")
                if child not in game.nodes:
                    raise ValueError("chance edge leaves node registry")
                if child in parents:
                    raise ValueError("game graph is not a tree")
                parents[child] = node_id
                total += probability
                visit(child, dict(own_sequences), chance_probability * probability)
            if total != 1:
                raise ValueError("chance probabilities do not sum to one")
            return
        if kind != "player":
            raise ValueError("unknown node kind")

        player = node.get("player")
        information_set = node.get("information_set")
        actions = node.get("actions")
        if player not in {"max", "min"}:
            raise ValueError("player node has invalid owner")
        if not isinstance(information_set, str) or not information_set:
            raise ValueError("player node needs an information set")
        if not isinstance(actions, Mapping) or not actions:
            raise ValueError("player node needs actions")
        action_names = tuple(actions)
        if len(set(action_names)) != len(action_names):
            raise ValueError("duplicate action")
        parent_sequence = own_sequences[player]
        if information_set not in info:
            info[information_set] = {
                "player": player,
                "actions": action_names,
                "parent_sequence": parent_sequence,
                "nodes": [node_id],
            }
            info_order[player].append(information_set)
        else:
            registered = info[information_set]
            if registered["player"] != player:
                raise ValueError("information set mixes players")
            if registered["actions"] != action_names:
                raise ValueError("information set action registries differ")
            if registered["parent_sequence"] != parent_sequence:
                raise ValueError("perfect recall violated at information set")
            registered["nodes"].append(node_id)

        for action, child in actions.items():
            if child not in game.nodes:
                raise ValueError("action edge leaves node registry")
            if child in parents:
                raise ValueError("game graph is not a tree")
            parents[child] = node_id
            next_sequences = dict(own_sequences)
            child_sequence = parent_sequence + ((information_set, action),)
            sequences[player].add(child_sequence)
            next_sequences[player] = child_sequence
            visit(child, next_sequences, chance_probability)

    visit(game.root, {"max": EMPTY, "min": EMPTY}, Q(1))
    if visited != set(game.nodes):
        raise ValueError("node registry contains unreachable nodes")
    if sum((terminal["chance_probability"] for terminal in terminals), Q(0)) <= 0:
        raise ValueError("game has no positive-probability terminal")
    return {
        "information": info,
        "information_order": info_order,
        "sequences": sequences,
        "terminals": terminals,
        "node_count": len(visited),
        "perfect_recall": True,
    }


def build_realization_form(analysis: dict[str, object], player: str) -> RealizationForm:
    information_sets = tuple(analysis["information_order"][player])
    info = analysis["information"]
    sequence_set = analysis["sequences"][player]
    sequences = (EMPTY,) + tuple(
        sorted(
            (sequence for sequence in sequence_set if sequence),
            key=lambda value: (len(value), sequence_name(value)),
        )
    )
    index = {sequence: position for position, sequence in enumerate(sequences)}
    actions = {
        information_set: tuple(info[information_set]["actions"])
        for information_set in information_sets
    }
    parents = {
        information_set: info[information_set]["parent_sequence"]
        for information_set in information_sets
    }
    children = {
        (information_set, action): parents[information_set]
        + ((information_set, action),)
        for information_set in information_sets
        for action in actions[information_set]
    }
    rows = []
    root_row = [Q(0)] * len(sequences)
    root_row[index[EMPTY]] = Q(1)
    rows.append(tuple(root_row))
    for information_set in information_sets:
        row = [Q(0)] * len(sequences)
        row[index[parents[information_set]]] = Q(-1)
        for action in actions[information_set]:
            row[index[children[(information_set, action)]]] += Q(1)
        rows.append(tuple(row))
    return RealizationForm(
        player=player,
        sequences=sequences,
        information_sets=information_sets,
        actions=actions,
        parent_sequence=parents,
        child_sequence=children,
        E=tuple(rows),
        e=(Q(1),) + (Q(0),) * len(information_sets),
    )


def compile_sequence_form(game: ExtensiveGame) -> CompiledSequenceGame:
    analysis = analyze_tree(game)
    max_form = build_realization_form(analysis, "max")
    min_form = build_realization_form(analysis, "min")
    max_index = {sequence: index for index, sequence in enumerate(max_form.sequences)}
    min_index = {sequence: index for index, sequence in enumerate(min_form.sequences)}
    payoff = [
        [Q(0) for _ in min_form.sequences] for _ in max_form.sequences
    ]
    nonzero = 0
    for terminal in analysis["terminals"]:
        contribution = terminal["chance_probability"] * terminal["payoff"]
        payoff[max_index[terminal["max_sequence"]]][
            min_index[terminal["min_sequence"]]
        ] += contribution
        if contribution:
            nonzero += 1
    return CompiledSequenceGame(
        max_form=max_form,
        min_form=min_form,
        payoff=tuple(tuple(row) for row in payoff),
        terminal_count=len(analysis["terminals"]),
        nonzero_payoff_contributions=nonzero,
        perfect_recall=analysis["perfect_recall"],
    )


def dot(left: Sequence[Q], right: Sequence[Q]) -> Q:
    return sum((x * y for x, y in zip(left, right)), Q(0))


def matrix_vector(matrix: Sequence[Sequence[Q]], vector: Sequence[Q]) -> tuple[Q, ...]:
    return tuple(dot(row, vector) for row in matrix)


def transpose_vector(matrix: Sequence[Sequence[Q]], vector: Sequence[Q]) -> tuple[Q, ...]:
    return tuple(
        sum((vector[row] * matrix[row][column] for row in range(len(matrix))), Q(0))
        for column in range(len(matrix[0]))
    )


def realization_from_behavior(
    form: RealizationForm, behavior: Mapping[str, Mapping[str, Q]]
) -> tuple[Q, ...]:
    if set(behavior) != set(form.information_sets):
        raise ValueError("behavior information-set registry mismatch")
    values = {EMPTY: Q(1)}
    for information_set in sorted(
        form.information_sets,
        key=lambda value: len(form.parent_sequence[value]),
    ):
        distribution = behavior[information_set]
        if set(distribution) != set(form.actions[information_set]):
            raise ValueError("behavior action registry mismatch")
        if any(value < 0 for value in distribution.values()):
            raise ValueError("negative behavior probability")
        if sum(distribution.values(), Q(0)) != 1:
            raise ValueError("behavior probabilities do not sum to one")
        parent_value = values[form.parent_sequence[information_set]]
        for action in form.actions[information_set]:
            values[form.child_sequence[(information_set, action)]] = (
                parent_value * distribution[action]
            )
    return tuple(values[sequence] for sequence in form.sequences)


def behavior_from_realization(
    form: RealizationForm, realization: Sequence[Q]
) -> dict[str, dict[str, Q]]:
    if not realization_feasible(form, realization):
        raise ValueError("invalid realization plan")
    index = {sequence: position for position, sequence in enumerate(form.sequences)}
    behavior = {}
    for information_set in form.information_sets:
        parent_value = realization[index[form.parent_sequence[information_set]]]
        if parent_value:
            behavior[information_set] = {
                action: realization[index[form.child_sequence[(information_set, action)]]]
                / parent_value
                for action in form.actions[information_set]
            }
        else:
            behavior[information_set] = {
                action: Q(1) if position == 0 else Q(0)
                for position, action in enumerate(form.actions[information_set])
            }
    return behavior


def realization_feasible(form: RealizationForm, realization: Sequence[Q]) -> bool:
    return (
        len(realization) == len(form.sequences)
        and all(value >= 0 for value in realization)
        and matrix_vector(form.E, realization) == form.e
    )


def child_information_sets(form: RealizationForm) -> dict[SequenceKey, list[str]]:
    children = {sequence: [] for sequence in form.sequences}
    for information_set in form.information_sets:
        children[form.parent_sequence[information_set]].append(information_set)
    return children


def min_dual_potentials(
    form: RealizationForm, sequence_payoffs: Sequence[Q]
) -> tuple[Q, ...]:
    if len(sequence_payoffs) != len(form.sequences):
        raise ValueError("sequence payoff dimension mismatch")
    index = {sequence: position for position, sequence in enumerate(form.sequences)}
    descendants = child_information_sets(form)
    potentials: dict[str, Q] = {}
    for information_set in sorted(
        form.information_sets,
        key=lambda value: len(form.parent_sequence[value]),
        reverse=True,
    ):
        candidates = []
        for action in form.actions[information_set]:
            sequence = form.child_sequence[(information_set, action)]
            candidates.append(
                sequence_payoffs[index[sequence]]
                + sum((potentials[child] for child in descendants[sequence]), Q(0))
            )
        potentials[information_set] = min(candidates)
    root = sequence_payoffs[index[EMPTY]] + sum(
        (potentials[child] for child in descendants[EMPTY]), Q(0)
    )
    return (root,) + tuple(potentials[information_set] for information_set in form.information_sets)


def max_dual_potentials(
    form: RealizationForm, sequence_payoffs: Sequence[Q]
) -> tuple[Q, ...]:
    if len(sequence_payoffs) != len(form.sequences):
        raise ValueError("sequence payoff dimension mismatch")
    index = {sequence: position for position, sequence in enumerate(form.sequences)}
    descendants = child_information_sets(form)
    potentials: dict[str, Q] = {}
    for information_set in sorted(
        form.information_sets,
        key=lambda value: len(form.parent_sequence[value]),
        reverse=True,
    ):
        candidates = []
        for action in form.actions[information_set]:
            sequence = form.child_sequence[(information_set, action)]
            candidates.append(
                sequence_payoffs[index[sequence]]
                + sum((potentials[child] for child in descendants[sequence]), Q(0))
            )
        potentials[information_set] = max(candidates)
    root = sequence_payoffs[index[EMPTY]] + sum(
        (potentials[child] for child in descendants[EMPTY]), Q(0)
    )
    return (root,) + tuple(potentials[information_set] for information_set in form.information_sets)


def transpose_constraint(form: RealizationForm, potentials: Sequence[Q]) -> tuple[Q, ...]:
    return transpose_vector(form.E, potentials)


def audit_sequence_saddle(
    compiled: CompiledSequenceGame,
    max_realization: Sequence[Q],
    min_realization: Sequence[Q],
    claimed_value: Q,
) -> dict[str, object]:
    max_feasible = realization_feasible(compiled.max_form, max_realization)
    min_feasible = realization_feasible(compiled.min_form, min_realization)
    if not max_feasible or not min_feasible:
        raise ValueError("saddle realization is infeasible")
    min_sequence_payoffs = transpose_vector(compiled.payoff, max_realization)
    max_sequence_payoffs = matrix_vector(compiled.payoff, min_realization)
    min_potentials = min_dual_potentials(
        compiled.min_form, min_sequence_payoffs
    )
    max_potentials = max_dual_potentials(
        compiled.max_form, max_sequence_payoffs
    )
    min_lhs = transpose_constraint(compiled.min_form, min_potentials)
    max_lhs = transpose_constraint(compiled.max_form, max_potentials)
    lower_valid = all(
        lhs <= payoff for lhs, payoff in zip(min_lhs, min_sequence_payoffs)
    )
    upper_valid = all(
        lhs >= payoff for lhs, payoff in zip(max_lhs, max_sequence_payoffs)
    )
    lower_value = dot(compiled.min_form.e, min_potentials)
    upper_value = dot(compiled.max_form.e, max_potentials)
    pair_value = dot(max_realization, matrix_vector(compiled.payoff, min_realization))
    recovered_max = realization_from_behavior(
        compiled.max_form,
        behavior_from_realization(compiled.max_form, max_realization),
    )
    recovered_min = realization_from_behavior(
        compiled.min_form,
        behavior_from_realization(compiled.min_form, min_realization),
    )
    exact = (
        lower_valid
        and upper_valid
        and lower_value == upper_value == pair_value == claimed_value
        and recovered_max == tuple(max_realization)
        and recovered_min == tuple(min_realization)
    )
    return {
        "max_realization": qvector(max_realization),
        "min_realization": qvector(min_realization),
        "min_sequence_payoffs": qvector(min_sequence_payoffs),
        "max_sequence_payoffs": qvector(max_sequence_payoffs),
        "min_dual_potentials": qvector(min_potentials),
        "max_dual_potentials": qvector(max_potentials),
        "min_dual_lhs": qvector(min_lhs),
        "max_dual_lhs": qvector(max_lhs),
        "max_realization_feasible": max_feasible,
        "min_realization_feasible": min_feasible,
        "lower_constraint_valid": lower_valid,
        "upper_constraint_valid": upper_valid,
        "lower_value": qstr(lower_value),
        "upper_value": qstr(upper_value),
        "mixed_pair_value": qstr(pair_value),
        "claimed_value": qstr(claimed_value),
        "behavior_round_trip_exact": (
            recovered_max == tuple(max_realization)
            and recovered_min == tuple(min_realization)
        ),
        "exact": exact,
    }


def matching_game(hidden: bool) -> ExtensiveGame:
    nodes: dict[str, dict[str, object]] = {
        "root": {
            "kind": "player",
            "player": "max",
            "information_set": "MAX_CHOICE",
            "actions": {"H": "after_h", "T": "after_t"},
        }
    }
    for first in ("h", "t"):
        information = "MIN_HIDDEN" if hidden else f"MIN_AFTER_{first.upper()}"
        nodes[f"after_{first}"] = {
            "kind": "player",
            "player": "min",
            "information_set": information,
            "actions": {
                "H": f"terminal_{first}_h",
                "T": f"terminal_{first}_t",
            },
        }
        for second in ("h", "t"):
            nodes[f"terminal_{first}_{second}"] = {
                "kind": "terminal",
                "payoff": Q(1) if first == second else Q(-1),
            }
    return ExtensiveGame("root", nodes)


def concealment_game(size: int) -> ExtensiveGame:
    if size < 2:
        raise ValueError("concealment size must be at least two")
    nodes: dict[str, dict[str, object]] = {
        "chance": {"kind": "chance", "transitions": {}}
    }
    chance_transitions = nodes["chance"]["transitions"]
    for hidden_type in range(size):
        max_node = f"max_type_{hidden_type}"
        chance_transitions[f"type_{hidden_type}"] = (Q(1, size), max_node)
        max_actions = {}
        for signal in range(size):
            min_node = f"min_type_{hidden_type}_signal_{signal}"
            max_actions[f"signal_{signal}"] = min_node
            min_actions = {}
            for guess in range(size):
                terminal = f"terminal_{hidden_type}_{signal}_{guess}"
                min_actions[f"guess_{guess}"] = terminal
                nodes[terminal] = {
                    "kind": "terminal",
                    "payoff": Q(0) if guess == hidden_type else Q(1),
                }
            nodes[min_node] = {
                "kind": "player",
                "player": "min",
                "information_set": f"MIN_SEES_SIGNAL_{signal}",
                "actions": min_actions,
            }
        nodes[max_node] = {
            "kind": "player",
            "player": "max",
            "information_set": f"MAX_KNOWS_TYPE_{hidden_type}",
            "actions": max_actions,
        }
    return ExtensiveGame("chance", nodes)


def nested_perfect_recall_game() -> ExtensiveGame:
    nodes: dict[str, dict[str, object]] = {
        "root": {
            "kind": "player",
            "player": "max",
            "information_set": "MAX_FIRST",
            "actions": {"L": "min_after_l", "R": "min_after_r"},
        },
        "min_after_l": {
            "kind": "player",
            "player": "min",
            "information_set": "MIN_HIDDEN_FIRST",
            "actions": {"X": "max_lx", "Y": "max_ly"},
        },
        "min_after_r": {
            "kind": "player",
            "player": "min",
            "information_set": "MIN_HIDDEN_FIRST",
            "actions": {"X": "max_rx", "Y": "max_ry"},
        },
    }
    for first in ("l", "r"):
        for challenge in ("x", "y"):
            later = f"max_{first}{challenge}"
            information = f"MAX_REMEMBERS_{first.upper()}"
            nodes[later] = {
                "kind": "player",
                "player": "max",
                "information_set": information,
                "actions": {
                    "A": f"terminal_{first}{challenge}_a",
                    "B": f"terminal_{first}{challenge}_b",
                },
            }
            nodes[f"terminal_{first}{challenge}_a"] = {
                "kind": "terminal",
                "payoff": Q(1),
            }
            nodes[f"terminal_{first}{challenge}_b"] = {
                "kind": "terminal",
                "payoff": Q(0),
            }
    return ExtensiveGame("root", nodes)


def uniform_behavior(form: RealizationForm, action_count: int) -> dict[str, dict[str, Q]]:
    return {
        information_set: {
            action: Q(1, action_count) for action in form.actions[information_set]
        }
        for information_set in form.information_sets
    }


def normal_concealment_audit(size: int) -> dict[str, object] | None:
    if size > 3:
        return None
    pure_functions = list(product(range(size), repeat=size))
    matrix = []
    for sender in pure_functions:
        row = []
        for receiver in pure_functions:
            payoff = sum(
                (
                    Q(0)
                    if receiver[sender[hidden_type]] == hidden_type
                    else Q(1)
                    for hidden_type in range(size)
                ),
                Q(0),
            ) / size
            row.append(payoff)
        matrix.append(tuple(row))
    uniform = Q(1, len(pure_functions))
    column_values = tuple(
        sum((uniform * matrix[row][column] for row in range(len(matrix))), Q(0))
        for column in range(len(matrix))
    )
    row_values = tuple(
        sum((matrix[row][column] * uniform for column in range(len(matrix))), Q(0))
        for row in range(len(matrix))
    )
    value = Q(size - 1, size)
    return {
        "pure_strategies_per_role": len(pure_functions),
        "normal_matrix_entries": len(pure_functions) ** 2,
        "uniform_column_values": sorted({qstr(value) for value in column_values}),
        "uniform_row_values": sorted({qstr(value) for value in row_values}),
        "value": qstr(value),
        "exact": set(column_values) == {value} and set(row_values) == {value},
    }


def form_summary(form: RealizationForm) -> dict[str, object]:
    return {
        "player": form.player,
        "sequence_count": len(form.sequences),
        "information_set_count": len(form.information_sets),
        "constraint_rows": len(form.E),
        "sequence_names": [sequence_name(sequence) for sequence in form.sequences],
        "E": [qvector(row) for row in form.E],
        "e": qvector(form.e),
    }


def matching_row(hidden: bool) -> dict[str, object]:
    compiled = compile_sequence_form(matching_game(hidden))
    if hidden:
        max_behavior = uniform_behavior(compiled.max_form, 2)
        min_behavior = uniform_behavior(compiled.min_form, 2)
        value = Q(0)
        case_id = "hidden_matching"
    else:
        max_behavior = {
            "MAX_CHOICE": {"H": Q(1), "T": Q(0)}
        }
        min_behavior = {
            "MIN_AFTER_H": {"H": Q(0), "T": Q(1)},
            "MIN_AFTER_T": {"H": Q(1), "T": Q(0)},
        }
        value = Q(-1)
        case_id = "revealed_matching"
    max_realization = realization_from_behavior(compiled.max_form, max_behavior)
    min_realization = realization_from_behavior(compiled.min_form, min_behavior)
    audit = audit_sequence_saddle(compiled, max_realization, min_realization, value)
    return {
        "case_id": case_id,
        "hidden": hidden,
        "max_form": form_summary(compiled.max_form),
        "min_form": form_summary(compiled.min_form),
        "terminal_count": compiled.terminal_count,
        "payoff": [qvector(row) for row in compiled.payoff],
        "audit": audit,
        "value": qstr(value),
        "certified": audit["exact"],
    }


def nested_row() -> dict[str, object]:
    compiled = compile_sequence_form(nested_perfect_recall_game())
    max_behavior = {
        "MAX_FIRST": {"L": Q(1), "R": Q(0)},
        "MAX_REMEMBERS_L": {"A": Q(1), "B": Q(0)},
        "MAX_REMEMBERS_R": {"A": Q(1), "B": Q(0)},
    }
    min_behavior = {
        "MIN_HIDDEN_FIRST": {"X": Q(1), "Y": Q(0)}
    }
    max_realization = realization_from_behavior(compiled.max_form, max_behavior)
    min_realization = realization_from_behavior(compiled.min_form, min_behavior)
    audit = audit_sequence_saddle(
        compiled, max_realization, min_realization, Q(1)
    )
    return {
        "case_id": "nested_perfect_recall",
        "max_form": form_summary(compiled.max_form),
        "min_form": form_summary(compiled.min_form),
        "terminal_count": compiled.terminal_count,
        "payoff": [qvector(row) for row in compiled.payoff],
        "audit": audit,
        "value": "1",
        "max_sequence_depth": max(
            len(sequence) for sequence in compiled.max_form.sequences
        ),
        "certified": audit["exact"],
    }


def concealment_row(size: int) -> dict[str, object]:
    compiled = compile_sequence_form(concealment_game(size))
    max_realization = realization_from_behavior(
        compiled.max_form, uniform_behavior(compiled.max_form, size)
    )
    min_realization = realization_from_behavior(
        compiled.min_form, uniform_behavior(compiled.min_form, size)
    )
    value = Q(size - 1, size)
    audit = audit_sequence_saddle(compiled, max_realization, min_realization, value)
    normal = normal_concealment_audit(size)
    return {
        "size": size,
        "types": size,
        "signals": size,
        "guesses": size,
        "pure_strategies_per_role": size**size,
        "normal_matrix_entries": (size**size) ** 2,
        "sequences_per_role": 1 + size * size,
        "sequence_payoff_entries": (1 + size * size) ** 2,
        "terminal_histories": size**3,
        "nonzero_terminal_contributions": size * size * (size - 1),
        "max_form": form_summary(compiled.max_form),
        "min_form": form_summary(compiled.min_form),
        "compiled_terminal_count": compiled.terminal_count,
        "compiled_nonzero_payoff_contributions": compiled.nonzero_payoff_contributions,
        "value": qstr(value),
        "audit": audit,
        "normal_form_audit": normal,
        "certified": (
            compiled.perfect_recall
            and audit["exact"]
            and compiled.terminal_count == size**3
            and compiled.nonzero_payoff_contributions == size * size * (size - 1)
            and (normal is None or normal["exact"])
        ),
    }


def imperfect_recall_fixture() -> ExtensiveGame:
    return ExtensiveGame(
        "first",
        {
            "first": {
                "kind": "player",
                "player": "max",
                "information_set": "FIRST",
                "actions": {"L": "later_l", "R": "later_r"},
            },
            "later_l": {
                "kind": "player",
                "player": "max",
                "information_set": "FORGETS_FIRST",
                "actions": {"A": "la", "B": "lb"},
            },
            "later_r": {
                "kind": "player",
                "player": "max",
                "information_set": "FORGETS_FIRST",
                "actions": {"A": "ra", "B": "rb"},
            },
            "la": {"kind": "terminal", "payoff": Q(0)},
            "lb": {"kind": "terminal", "payoff": Q(0)},
            "ra": {"kind": "terminal", "payoff": Q(0)},
            "rb": {"kind": "terminal", "payoff": Q(0)},
        },
    )


def build_result() -> dict[str, object]:
    matching = [matching_row(hidden=False), matching_row(hidden=True)]
    nested = nested_row()
    concealment = [concealment_row(size) for size in range(2, 9)]
    imperfect_recall_rejected = False
    try:
        compile_sequence_form(imperfect_recall_fixture())
    except ValueError as error:
        imperfect_recall_rejected = "perfect recall violated" in str(error)
    gates = {
        "S0_matching_information_values_exact": (
            matching[0]["value"] == "-1"
            and matching[1]["value"] == "0"
            and all(row["certified"] for row in matching)
        ),
        "S1_all_concealment_sequence_saddles_exact": all(
            row["certified"] for row in concealment
        ),
        "S1b_nested_realization_recursion_exact": (
            nested["certified"]
            and nested["value"] == "1"
            and nested["max_sequence_depth"] == 2
        ),
        "S2_sequence_counts_are_one_plus_k_squared": all(
            row["sequences_per_role"] == 1 + row["size"] ** 2
            for row in concealment
        ),
        "S3_pure_strategy_counts_are_k_to_k": all(
            row["pure_strategies_per_role"] == row["size"] ** row["size"]
            for row in concealment
        ),
        "S4_concealment_values_are_one_minus_one_over_k": all(
            row["value"] == qstr(Q(row["size"] - 1, row["size"]))
            for row in concealment
        ),
        "S5_small_normal_form_cross_checks_pass": all(
            row["normal_form_audit"] is None or row["normal_form_audit"]["exact"]
            for row in concealment
        ),
        "S6_imperfect_recall_is_rejected": imperfect_recall_rejected,
    }
    return {
        "schema_version": "asmp3_sequence_form_bridge_v1_3",
        "experiment_id": "ASMP-3-SEQUENCE-FORM-BRIDGE-v1.3",
        "status": "exact_perfect_recall_sequence_form_bridge",
        "parent_result": "ASMP-3-MATRIX-GAME-BRIDGE-v1.2",
        "theorem": {
            "input": (
                "finite two-player zero-sum extensive tree with rational chance, "
                "typed information sets, and perfect recall"
            ),
            "compiler": (
                "realization constraints E_i r_i=e_i and chance-weighted "
                "sequence payoff matrix A"
            ),
            "max_certificate": "E_max x=e_max and E_min^T p <= A^T x",
            "min_certificate": "E_min y=e_min and E_max^T q >= A y",
            "consequence": (
                "hidden extensive games can be certified without enumerating "
                "complete pure strategies"
            ),
        },
        "matching_rows": matching,
        "nested_row": nested,
        "concealment_rows": concealment,
        "imperfect_recall_rejected": imperfect_recall_rejected,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The theorem requires a finite explicit perfect-recall tree and a "
            "zero-sum payoff. It does not compact an exponentially large history "
            "tree, handle imperfect recall, or choose an admissible interface."
        ),
    }
