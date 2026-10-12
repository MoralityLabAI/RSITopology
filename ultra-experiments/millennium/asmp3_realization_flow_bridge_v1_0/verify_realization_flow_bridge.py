from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "realization_flow_bridge_v1_0.json"
OUTPUT_PATH = (
    HERE / "artifacts" / "realization_flow_bridge_verification_v1_0.json"
)


def q(value: str | int) -> Fraction:
    return Fraction(value)


def check_reconstruction_record(
    record: dict[str, object],
    state_count: int,
    low_probability: Fraction,
    high_probability: Fraction,
    high_action_probability: Fraction,
) -> bool:
    expected_low_flow = (1 - high_action_probability) / state_count
    expected_high_flow = high_action_probability / state_count
    occupancy = record["occupancy"]
    if len(occupancy) != 2 * state_count:
        return False
    for index in range(state_count):
        if q(occupancy[f"s{index}|low"]) != expected_low_flow:
            return False
        if q(occupancy[f"s{index}|high"]) != expected_high_flow:
            return False
    expected_zero = (
        (1 - high_action_probability) * low_probability
        + high_action_probability * high_probability
    )
    terminal = record["terminal_law"]
    if q(terminal["zero"]) != expected_zero or q(terminal["one"]) != 1 - expected_zero:
        return False
    flow_rows = record["flow_audit"]["flow_rows"]
    return (
        len(flow_rows) == state_count
        and all(
            q(row["outgoing"]) == q(row["initial_plus_incoming"]) == Fraction(1, state_count)
            and row["holds"] is True
            for row in flow_rows
        )
        and record["flow_audit"]["valid"] is True
        and record["reconstruction_exact"] is True
    )


def check_band_row(row: dict[str, object]) -> bool:
    state_count = int(row["state_count"])
    enumerated = state_count <= 8
    if (
        int(row["pure_policy_count_per_class"]) != 1 << state_count
        or int(row["flow_variable_count_per_class"]) != 2 * state_count
        or int(row["flow_equality_count_per_class"]) != state_count
        or row["honest_zero_probability_interval"] != ["4/5", "9/10"]
        or row["false_zero_probability_interval"] != ["1/10", "1/5"]
        or row["exact_gap"] != "3/5"
        or row["pure_policies_enumerated"] is not enumerated
    ):
        return False
    if enumerated:
        if row["enumerated_honest_extrema"] != ["4/5", "9/10"]:
            return False
        if row["enumerated_false_extrema"] != ["1/10", "1/5"]:
            return False
    elif (
        row["enumerated_honest_extrema"] is not None
        or row["enumerated_false_extrema"] is not None
    ):
        return False
    return (
        check_reconstruction_record(
            row["closest_honest"], state_count, q("4/5"), q("9/10"), q("0")
        )
        and check_reconstruction_record(
            row["closest_false"], state_count, q("1/10"), q("1/5"), q("1")
        )
        and check_reconstruction_record(
            row["honest_interior_reconstruction"],
            state_count,
            q("4/5"),
            q("9/10"),
            q("2/5"),
        )
        and check_reconstruction_record(
            row["false_interior_reconstruction"],
            state_count,
            q("1/10"),
            q("1/5"),
            q("3/5"),
        )
        and row["certified"] is True
    )


def parse_adaptive_graph(value: dict[str, object]) -> dict[str, object]:
    states = tuple(value["states"])
    terminals = tuple(value["terminals"])
    actions = {state: tuple(registered) for state, registered in value["actions"].items()}
    initial = {state: q(probability) for state, probability in value["initial"].items()}
    transitions = {}
    for key, channel in value["transitions"].items():
        state, action = key.split("|", 1)
        transitions[(state, action)] = {
            destination: q(probability) for destination, probability in channel.items()
        }
    return {
        "states": states,
        "terminals": terminals,
        "actions": actions,
        "initial": initial,
        "transitions": transitions,
    }


def simulate(
    graph: dict[str, object], policy: dict[str, dict[str, Fraction]]
) -> tuple[dict[tuple[str, str], Fraction], dict[str, Fraction]]:
    arrival = {state: graph["initial"].get(state, Fraction(0)) for state in graph["states"]}
    occupancy = {}
    terminal = {name: Fraction(0) for name in graph["terminals"]}
    for state in graph["states"]:
        for action in graph["actions"][state]:
            mass = arrival[state] * policy[state][action]
            occupancy[(state, action)] = mass
            for destination, probability in graph["transitions"][(state, action)].items():
                if destination in terminal:
                    terminal[destination] += mass * probability
                else:
                    arrival[destination] += mass * probability
    return occupancy, terminal


def check_adaptive_row(row: dict[str, object]) -> bool:
    graph = parse_adaptive_graph(row["graph"])
    policy = {
        state: {action: q(value) for action, value in distribution.items()}
        for state, distribution in row["registered_policy"].items()
    }
    occupancy, terminal = simulate(graph, policy)
    recorded = row["audit"]
    recorded_occupancy = {
        tuple(key.split("|", 1)): q(value)
        for key, value in recorded["occupancy"].items()
    }
    recorded_terminal = {
        name: q(value) for name, value in recorded["terminal_law"].items()
    }

    pure_laws = set()
    for choices in product(*(graph["actions"][state] for state in graph["states"])):
        pure_policy = {
            state: {
                action: Fraction(1) if action == selected else Fraction(0)
                for action in graph["actions"][state]
            }
            for state, selected in zip(graph["states"], choices)
        }
        _, law = simulate(graph, pure_policy)
        pure_laws.add(tuple(law[name] for name in graph["terminals"]))
    recorded_pure_laws = {
        tuple(q(value) for value in law) for law in row["pure_terminal_laws"]
    }
    return (
        occupancy == recorded_occupancy
        and terminal == recorded_terminal
        and sum(terminal.values(), Fraction(0)) == 1
        and int(row["pure_policy_count"]) == 8
        and int(row["distinct_pure_terminal_law_count"]) == len(pure_laws)
        and recorded_pure_laws == pure_laws
        and recorded["flow_audit"]["valid"] is True
        and recorded["reconstruction_exact"] is True
        and row["certified"] is True
    )


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    bands = result.get("band_rows", [])
    adaptive = result.get("adaptive_row", {})
    checks = {
        "V0_schema_parent_status_and_boundary": (
            result.get("schema_version") == "asmp3_realization_flow_bridge_v1_0"
            and result.get("status") == "exact_acyclic_single_controller_bridge"
            and result.get("parent_result") == "ASMP-3-POLYHEDRAL-TV-FRONTIER-v0.9"
            and result.get("certified") is True
            and "Multiple independently strategic roles"
            in result.get("claim_boundary", "")
        ),
        "V1_band_registry_complete": (
            [row["state_count"] for row in bands] == list(range(1, 13))
        ),
        "V2_all_band_flows_reconstructed": (
            len(bands) == 12 and all(check_band_row(row) for row in bands)
        ),
        "V3_exponential_policy_linear_flow_counts": all(
            row["pure_policy_count_per_class"] == 2 ** row["state_count"]
            and row["flow_variable_count_per_class"] == 2 * row["state_count"]
            for row in bands
        ),
        "V4_band_gap_uniformly_three_fifths": all(
            row["exact_gap"] == "3/5" for row in bands
        ),
        "V5_adaptive_graph_reconstructed": check_adaptive_row(adaptive),
        "V6_producer_gates_all_true": (
            bool(result.get("gates")) and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_realization_flow_bridge_verification_v1_0",
        "checker": "clean_room_flow_and_policy_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker reconstructs registered acyclic controlled graphs; "
            "it does not extend the result to multi-controller games."
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
        raise SystemExit(f"realization-flow verification failed: {failed}")
    print(
        "ASMP-3 realization-flow independent verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
