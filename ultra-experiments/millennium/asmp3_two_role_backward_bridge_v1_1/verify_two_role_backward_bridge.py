from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "two_role_backward_bridge_v1_1.json"
OUTPUT_PATH = (
    HERE / "artifacts" / "two_role_backward_bridge_verification_v1_1.json"
)


def q(value: str | int) -> Fraction:
    return Fraction(value)


def check_family_row(row: dict[str, object]) -> bool:
    count = int(row["test_count"])
    audit = row["audit"]
    action_by_state = {entry["state"]: entry for entry in audit["action_rows"]}
    if set(action_by_state) != {"verifier"} | {
        f"challenge_{index}" for index in range(count)
    }:
        return False

    challenge_values = []
    for index in range(count):
        entry = action_by_state[f"challenge_{index}"]
        if index == count - 1:
            expected = (Fraction(3, 5), Fraction(4, 5))
        else:
            expected = (
                Fraction(index + 1, 10 * count),
                Fraction(index + 2, 10 * count),
            )
        recorded = entry["action_values"]
        if (
            q(recorded["attack_a"]) != expected[0]
            or q(recorded["attack_b"]) != expected[1]
            or entry["selected_action"] != "attack_a"
            or q(entry["state_value"]) != expected[0]
        ):
            return False
        challenge_values.append(expected[0])

    verifier = action_by_state["verifier"]
    if any(
        q(verifier["action_values"][f"test_{index}"]) != challenge_values[index]
        for index in range(count)
    ):
        return False
    exhaustive = count <= 8
    return (
        int(row["max_pure_strategy_count"]) == count
        and int(row["min_pure_strategy_count"]) == 1 << count
        and int(row["state_count"]) == count + 1
        and int(row["backward_action_evaluations"]) == 3 * count
        and q(row["exact_value"]) == Fraction(3, 5)
        and row["selected_test"] == f"test_{count - 1}"
        and row["exhaustive_saddle_audit"] is exhaustive
        and q(audit["backward_value"]) == Fraction(3, 5)
        and q(audit["saddle_pair_value"]) == Fraction(3, 5)
        and audit["backward_pair_matches"] is True
        and audit["certified"] is True
        and row["certified"] is True
        and (
            not exhaustive
            or (
                int(audit["max_strategy_count"]) == count
                and int(audit["min_strategy_count"]) == 1 << count
                and q(audit["minimum_against_backward_max"]) == Fraction(3, 5)
                and q(audit["maximum_against_backward_min"]) == Fraction(3, 5)
                and audit["max_guarantee_holds"] is True
                and audit["min_cap_holds"] is True
            )
        )
    )


def parse_game(value: dict[str, object]) -> dict[str, object]:
    states = tuple(value["states"])
    terminals = tuple(value["terminals"])
    transitions = {}
    for key, channel in value["transitions"].items():
        state, action = key.split("|", 1)
        transitions[(state, action)] = {
            destination: q(probability) for destination, probability in channel.items()
        }
    return {
        "states": states,
        "terminals": terminals,
        "owner": dict(value["owner"]),
        "actions": {state: tuple(actions) for state, actions in value["actions"].items()},
        "initial": {state: q(probability) for state, probability in value["initial"].items()},
        "payoff": {
            terminal: q(payoff) for terminal, payoff in value["terminal_payoff"].items()
        },
        "transitions": transitions,
    }


def backward(game: dict[str, object]) -> tuple[Fraction, dict[str, str], dict[str, str]]:
    values = dict(game["payoff"])
    strategies = {"max": {}, "min": {}}
    for state in reversed(game["states"]):
        action_values = {
            action: sum(
                (
                    probability * values[destination]
                    for destination, probability in game["transitions"][(state, action)].items()
                ),
                Fraction(0),
            )
            for action in game["actions"][state]
        }
        role = game["owner"][state]
        target = max(action_values.values()) if role == "max" else min(action_values.values())
        selected = next(action for action in game["actions"][state] if action_values[action] == target)
        values[state] = target
        strategies[role][state] = selected
    value = sum(
        (probability * values[state] for state, probability in game["initial"].items()),
        Fraction(0),
    )
    return value, strategies["max"], strategies["min"]


def evaluate(
    game: dict[str, object], max_strategy: dict[str, str], min_strategy: dict[str, str]
) -> Fraction:
    mass = {state: game["initial"].get(state, Fraction(0)) for state in game["states"]}
    terminal = {name: Fraction(0) for name in game["terminals"]}
    for state in game["states"]:
        action = max_strategy[state] if game["owner"][state] == "max" else min_strategy[state]
        for destination, probability in game["transitions"][(state, action)].items():
            contribution = mass[state] * probability
            if destination in terminal:
                terminal[destination] += contribution
            else:
                mass[destination] += contribution
    return sum(
        (terminal[name] * game["payoff"][name] for name in game["terminals"]),
        Fraction(0),
    )


def enumerate_role(game: dict[str, object], role: str) -> list[dict[str, str]]:
    states = tuple(state for state in game["states"] if game["owner"][state] == role)
    return [
        {state: action for state, action in zip(states, choices)}
        for choices in product(*(game["actions"][state] for state in states))
    ]


def check_alternating(value: dict[str, object]) -> bool:
    game = parse_game(value["game"])
    expected, max_strategy, min_strategy = backward(game)
    max_strategies = enumerate_role(game, "max")
    min_strategies = enumerate_role(game, "min")
    min_against_max = min(evaluate(game, max_strategy, strategy) for strategy in min_strategies)
    max_against_min = max(evaluate(game, strategy, min_strategy) for strategy in max_strategies)
    audit = value["audit"]
    return (
        expected == Fraction(7, 10)
        and min_against_max == expected
        and max_against_min == expected
        and q(audit["backward_value"]) == expected
        and q(audit["saddle_pair_value"]) == expected
        and audit["max_strategy"] == max_strategy
        and audit["min_strategy"] == min_strategy
        and audit["max_guarantee_holds"] is True
        and audit["min_cap_holds"] is True
        and audit["certified"] is True
    )


def check_matching(row: dict[str, object]) -> bool:
    matrix = tuple(tuple(q(value) for value in values) for values in row["simultaneous_payoff_matrix"])
    pure_maximin = max(min(values) for values in matrix)
    half_columns = tuple((matrix[0][column] + matrix[1][column]) / 2 for column in range(2))
    half_rows = tuple((matrix[index][0] + matrix[index][1]) / 2 for index in range(2))
    return (
        matrix == ((Fraction(1), Fraction(-1)), (Fraction(-1), Fraction(1)))
        and pure_maximin == Fraction(-1)
        and half_columns == (Fraction(0), Fraction(0))
        and q(row["revealed_sequential_value"]) == Fraction(-1)
        and q(row["simultaneous_pure_maximin"]) == pure_maximin
        and tuple(q(value) for value in row["simultaneous_max_half_mix_column_values"]) == half_columns
        and tuple(q(value) for value in row["simultaneous_min_half_mix_row_values"]) == half_rows
        and q(row["simultaneous_mixed_lower"]) == min(half_columns) == 0
        and q(row["simultaneous_mixed_upper"]) == max(half_rows) == 0
        and q(row["simultaneous_mixed_value"]) == 0
        and row["revealed_saddle_audit"]["certified"] is True
        and row["information_structure_changes_strategy_class"] is True
    )


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    family = result.get("family_rows", [])
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version") == "asmp3_two_role_backward_bridge_v1_1"
            and result.get("status") == "exact_perfect_information_two_role_bridge"
            and result.get("parent_result") == "ASMP-3-REALIZATION-FLOW-BRIDGE-v1.0"
            and result.get("certified") is True
            and "Simultaneous or hidden actions" in result.get("claim_boundary", "")
        ),
        "V1_family_registry_complete": (
            [row["test_count"] for row in family] == list(range(1, 13))
        ),
        "V2_all_family_backward_certificates_reconstructed": (
            len(family) == 12 and all(check_family_row(row) for row in family)
        ),
        "V3_exponential_strategy_linear_recursion_counts": all(
            row["min_pure_strategy_count"] == 2 ** row["test_count"]
            and row["backward_action_evaluations"] == 3 * row["test_count"]
            for row in family
        ),
        "V4_alternating_game_saddle_reconstructed": check_alternating(
            result["alternating_game"]
        ),
        "V5_matching_information_boundary_reconstructed": check_matching(
            result["matching_boundary"]
        ),
        "V6_producer_gates_all_true": (
            bool(result.get("gates")) and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_two_role_backward_bridge_verification_v1_1",
        "checker": "clean_room_backward_and_saddle_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker covers the registered perfect-information games; "
            "it does not validate an imperfect-information extension."
        ),
    }


def main() -> None:
    result = verify()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not result["passed"]:
        failed = [name for name, passed in result["checks"].items() if not passed]
        raise SystemExit(f"two-role backward verification failed: {failed}")
    print(
        "ASMP-3 two-role backward independent verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
