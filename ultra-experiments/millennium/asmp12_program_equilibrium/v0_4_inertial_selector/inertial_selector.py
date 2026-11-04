"""Exact finite inertial best-response selector for ASMP-12 v0.4."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import re
import shutil
import stat
import subprocess
import time
import tracemalloc
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Sequence


HERE = Path(os.path.abspath(__file__)).parent
FROZEN_PROTOCOL_ID = "ASMP12-INERTIAL-SELECTOR-v0.4"
FROZEN_SCHEMA = "asmp12_inertial_selector_manifest_v0_4"
FROZEN_MANIFEST_CANONICAL_SHA256 = (
    "acd64f90bf96063eeeaf88592869c65af1d2bcdb1e9ec91fc7c25eee70a26f67"
)
FROZEN_SOURCE_FILES = (
    "PROTOCOL_v0_4.md",
    "README.md",
    "SOURCE_FREEZE.md",
    "inertial_selector.py",
    "manifest_v0_4.json",
    "run.py",
    "test_inertial_selector.py",
    "verify_independent.py",
)
FROZEN_FAMILIES = {
    "chicken_threshold": {
        "R": Fraction(3),
        "S": Fraction(1),
        "P": Fraction(0),
    },
    "pd_threshold": {
        "R": Fraction(3),
        "S": Fraction(0),
        "P": Fraction(1),
    },
}
FROZEN_TEMPTATIONS = (Fraction(299, 100), Fraction(3), Fraction(301, 100))
FROZEN_BUDGETS = (2, 3)
FROZEN_SCHEDULES = ("row_first", "column_first")
FROZEN_COSTS = (1, 2, 3)
FROZEN_START = (1, 1)
CANONICAL_CATALOG = ((0, 0, 0), (0, 1, 1), (0, 0, 0))
REPAIRED_CATALOG = ((0, 0, 0), (0, 1, 0), (0, 0, 0))
SOURCE_BLIND_CATALOG = ((0, 0, 0), (1, 1, 1), (0, 0, 0))
CYCLE_FIXTURE_CATALOG = ((1, 1, 0), (0, 1, 1), (1, 0, 1))
CATALOGS = {
    "canonical": CANONICAL_CATALOG,
    "repaired": REPAIRED_CATALOG,
    "source_blind": SOURCE_BLIND_CATALOG,
}
FROZEN_PRIMARY_GATES = (
    "G0_manifest_source_and_predecessor_bindings",
    "G1_complete_12_graph_registry",
    "G2_complete_24_initialized_trajectories",
    "G3_exact_20_cooperative_4_noncooperative",
    "G4_initialized_rows_bind_to_graph_attractors",
    "G5_selected_profiles_are_pure_equilibria",
    "G6_controls_and_scope_breakers",
    "G7_five_metric_probe_families",
    "G8_exact_arithmetic_and_resources",
)
FROZEN_PROBE_IDS = (
    "P1_encoding_invariance",
    "P2_threshold_sensitivity",
    "P3_registered_monotonicity",
    "P4_anti_gaming",
    "P5_clean_controls",
)
FROZEN_CONTROL_IDS = (
    "repaired_duplicate_extensional",
    "source_blind_early_vulnerability",
    "additive_cost_padding",
    "six_semantic_relabelings",
    "inertia_and_cycle_fixtures",
    "max_cost_and_simultaneous_scope_breakers",
)
FROZEN_PREVERIFICATION_LAYERS = {
    "metric_robustness": "five_probe_families_computed_awaiting_independent_replay",
    "task_result": "finite_initialized_inertial_selector_threshold_computed",
    "measurement_reliability": "awaiting_import_independent_verification",
    "claim_support": "pending_independent_verification",
    "operational_decision": "no_deployment_authorization_await_independent_verification",
}
FROZEN_RESULT_FIELDS = {
    "schema_version",
    "protocol_id",
    "manifest_sha256",
    "source_binding",
    "predecessor_binding",
    "status",
    "stop_reason",
    "resource_observations",
    "graph_cells",
    "primary_rows",
    "fair_schedule_aggregates",
    "controls",
    "metric_robustness",
    "gates",
    "conclusion_layers",
    "claim_boundary",
}
GIT_EXECUTABLE = shutil.which("git")


class ResourceStop(RuntimeError):
    """A frozen cooperative resource check stopped the run."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def exact_fraction(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("inexact scalar")
    if isinstance(value, Fraction):
        return value
    if type(value) is int:
        return Fraction(value)
    if isinstance(value, str) and re.fullmatch(r"-?(0|[1-9][0-9]*)/[1-9][0-9]*", value):
        parsed = Fraction(value)
        if fraction_text(parsed) != value:
            raise ValueError("noncanonical fraction")
        return parsed
    raise TypeError("not an exact scalar")


def contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(key) or contains_float(item) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(contains_float(item) for item in value)
    return False


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def _reject_float(value: str) -> Any:
    raise ValueError(f"floating point forbidden: {value}")


def load_json_bytes_strict(payload: bytes) -> Any:
    return json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=_strict_object,
        parse_float=_reject_float,
        parse_constant=_reject_float,
    )


def load_json_strict(path: Path) -> Any:
    return load_json_bytes_strict(path.read_bytes())


def manifest_binding_checks(manifest: dict[str, Any]) -> dict[str, bool]:
    registry = manifest.get("registry", {})
    source = manifest.get("source_freeze", {})
    budget = manifest.get("budget", {})
    return {
        "canonical_manifest_hash_is_frozen": canonical_sha256(manifest)
        == FROZEN_MANIFEST_CANONICAL_SHA256,
        "identity_is_frozen": manifest.get("schema") == "alife.experiment.v1"
        and manifest.get("schema_version") == FROZEN_SCHEMA
        and manifest.get("protocol_id") == FROZEN_PROTOCOL_ID,
        "source_inventory_is_exact": tuple(source.get("files", ()))
        == FROZEN_SOURCE_FILES
        and source.get("artifact_execution_before_commit") == "forbidden",
        "registry_is_exact": registry.get("canonical_catalog")
        == ["DDD", "DCC", "DDD"]
        and tuple(registry.get("family_order", ())) == tuple(FROZEN_FAMILIES)
        and registry.get("graph_loop_order")
        == ["family", "temptation", "budget"]
        and registry.get("primary_loop_order")
        == ["family", "temptation", "budget", "schedule"]
        and tuple(registry.get("catalog_costs", ())) == FROZEN_COSTS
        and tuple(registry.get("budgets", ())) == FROZEN_BUDGETS
        and tuple(registry.get("schedules", ())) == FROZEN_SCHEDULES
        and tuple(exact_fraction(value) for value in registry.get("temptations", ()))
        == FROZEN_TEMPTATIONS
        and registry.get("initial_profile") == list(FROZEN_START)
        and registry.get("graph_cell_count") == 12
        and registry.get("graph_state_count") == 156
        and registry.get("primary_trajectory_count") == 24,
        "resource_contract_is_exact": budget.get("max_wall_seconds") == 15
        and budget.get("max_traced_python_mib") == 64
        and budget.get("max_artifact_bytes") == 1048576
        and budget.get("max_cells_per_world") == 18
        and budget.get("max_episodes") == 24
        and budget.get("max_graph_cells") == 12
        and budget.get("max_primary_trajectories") == 24
        and budget.get("max_scheduled_updates_per_trajectory") == 19
        and budget.get("max_steps_per_episode") == 19,
        "claim_boundary_is_frozen": manifest.get("claim_scope") == "model_only"
        and isinstance(manifest.get("claim_boundary"), list)
        and len(manifest["claim_boundary"]) == 7,
    }


def validate_manifest_binding(manifest: dict[str, Any]) -> dict[str, bool]:
    checks = manifest_binding_checks(manifest)
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"manifest binding failed: {failed}")
    return checks


def actions(
    catalog: Sequence[Sequence[int]], row_program: int, column_program: int
) -> tuple[int, int]:
    return catalog[row_program][column_program], catalog[column_program][row_program]


def utilities(
    family: str, temptation: Fraction, action_pair: tuple[int, int]
) -> tuple[Fraction, Fraction]:
    values = FROZEN_FAMILIES[family]
    if action_pair == (1, 1):
        return values["R"], values["R"]
    if action_pair == (1, 0):
        return values["S"], temptation
    if action_pair == (0, 1):
        return temptation, values["S"]
    return values["P"], values["P"]


def payoff(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    profile: tuple[int, int],
) -> tuple[Fraction, Fraction]:
    return utilities(family, temptation, actions(catalog, *profile))


def admitted(costs: Sequence[int], budget: int) -> tuple[int, ...]:
    return tuple(program for program, cost in enumerate(costs) if cost <= budget)


def best_response_decision(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    programs: Sequence[int],
    costs: Sequence[int],
    profile: tuple[int, int],
    player: int,
    *,
    tie_mode: str = "min_cost",
    inertia: bool = True,
) -> dict[str, Any]:
    if player not in (0, 1) or tie_mode not in {"min_cost", "max_cost"}:
        raise ValueError("unregistered player or tie mode")
    candidates = []
    for program in programs:
        candidate = (program, profile[1]) if player == 0 else (profile[0], program)
        candidates.append((program, payoff(catalog, family, temptation, candidate)[player]))
    best_value = max(value for _, value in candidates)
    best = tuple(program for program, value in candidates if value == best_value)
    incumbent = profile[player]
    incumbent_best = incumbent in best
    if inertia and incumbent_best:
        chosen = incumbent
        reason = "incumbent_best_response_inertia"
    else:
        target = min(costs[program] for program in best)
        if tie_mode == "max_cost":
            target = max(costs[program] for program in best)
        winners = [program for program in best if costs[program] == target]
        if len(winners) != 1:
            raise ValueError("attached-cost tie-break is not unique")
        chosen = winners[0]
        reason = f"{tie_mode}_best_response"
    after = (chosen, profile[1]) if player == 0 else (profile[0], chosen)
    return {
        "player": player,
        "candidate_payoffs": [
            {"program": program, "payoff": fraction_text(value)}
            for program, value in candidates
        ],
        "best_responses": list(best),
        "best_payoff": fraction_text(best_value),
        "incumbent_is_best_response": incumbent_best,
        "chosen_program": chosen,
        "reason": reason,
        "after_profile": list(after),
        "changed": chosen != incumbent,
    }


def augmented_states(programs: Sequence[int]) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        (row, column, player)
        for row in programs
        for column in programs
        for player in (0, 1)
    )


def augmented_step(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    programs: Sequence[int],
    costs: Sequence[int],
    state: tuple[int, int, int],
    *,
    tie_mode: str = "min_cost",
    inertia: bool = True,
) -> tuple[tuple[int, int, int], dict[str, Any]]:
    profile = state[:2]
    player = state[2]
    decision = best_response_decision(
        catalog,
        family,
        temptation,
        programs,
        costs,
        profile,
        player,
        tie_mode=tie_mode,
        inertia=inertia,
    )
    after = tuple(decision["after_profile"])
    return (after[0], after[1], 1 - player), decision


def _canonical_cycle(
    cycle: Sequence[tuple[int, int, int]],
) -> tuple[tuple[int, int, int], ...]:
    rotations = [tuple(cycle[index:]) + tuple(cycle[:index]) for index in range(len(cycle))]
    return min(rotations)


def _cycle_from_state(
    start: tuple[int, int, int],
    successors: dict[tuple[int, int, int], tuple[int, int, int]],
) -> tuple[tuple[int, int, int], ...]:
    path: list[tuple[int, int, int]] = []
    positions: dict[tuple[int, int, int], int] = {}
    state = start
    while state not in positions:
        positions[state] = len(path)
        path.append(state)
        state = successors[state]
    return _canonical_cycle(path[positions[state] :])


def pure_equilibria(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    programs: Sequence[int],
) -> tuple[tuple[int, int], ...]:
    output = []
    for row in programs:
        for column in programs:
            profile = (row, column)
            current = payoff(catalog, family, temptation, profile)
            row_best = max(
                payoff(catalog, family, temptation, (alternative, column))[0]
                for alternative in programs
            )
            column_best = max(
                payoff(catalog, family, temptation, (row, alternative))[1]
                for alternative in programs
            )
            if current == (row_best, column_best):
                output.append(profile)
    return tuple(output)


def complete_augmented_graph(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    costs: Sequence[int],
    budget: int,
    *,
    tie_mode: str = "min_cost",
    inertia: bool = True,
) -> dict[str, Any]:
    programs = admitted(costs, budget)
    states = augmented_states(programs)
    successors: dict[tuple[int, int, int], tuple[int, int, int]] = {}
    decisions: dict[tuple[int, int, int], dict[str, Any]] = {}
    for state in states:
        successor, decision = augmented_step(
            catalog,
            family,
            temptation,
            programs,
            costs,
            state,
            tie_mode=tie_mode,
            inertia=inertia,
        )
        successors[state] = successor
        decisions[state] = decision
    cycles = sorted({_cycle_from_state(state, successors) for state in states})
    cycle_ids = {cycle: f"A{index}" for index, cycle in enumerate(cycles)}
    assignments = {state: _cycle_from_state(state, successors) for state in states}
    basins = Counter(assignments.values())
    equilibria = set(pure_equilibria(catalog, family, temptation, programs))
    attractors = []
    for cycle in cycles:
        profiles = {state[:2] for state in cycle}
        fixed_profile = len(cycle) == 2 and len(profiles) == 1
        profile = next(iter(profiles)) if fixed_profile else None
        attractors.append(
            {
                "id": cycle_ids[cycle],
                "cycle": [list(state) for state in cycle],
                "cycle_length": len(cycle),
                "kind": "fixed_pure_profile" if fixed_profile else "dynamic_cycle",
                "fixed_profile": list(profile) if profile is not None else None,
                "fixed_profile_is_pure_equilibrium": bool(
                    profile is not None and profile in equilibria
                ),
                "basin_size": basins[cycle],
                "basin_fraction": fraction_text(Fraction(basins[cycle], len(states))),
            }
        )
    edges = []
    for state in states:
        edges.append(
            {
                "from": list(state),
                "to": list(successors[state]),
                "decision": decisions[state],
                "attractor_id": cycle_ids[assignments[state]],
            }
        )
    return {
        "family": family,
        "temptation": fraction_text(temptation),
        "budget": budget,
        "programs": list(programs),
        "state_count": len(states),
        "edge_count": len(edges),
        "edges": edges,
        "attractors": attractors,
        "checks": {
            "complete_functional_graph": len(states) == len(edges) == 2 * len(programs) ** 2,
            "basins_partition_states": sum(item["basin_size"] for item in attractors)
            == len(states),
            "fixed_attractors_are_pure_equilibria": all(
                item["fixed_profile_is_pure_equilibrium"]
                for item in attractors
                if item["kind"] == "fixed_pure_profile"
            ),
        },
    }


def _edge_lookup(graph: dict[str, Any]) -> dict[tuple[int, int, int], dict[str, Any]]:
    return {tuple(edge["from"]): edge for edge in graph["edges"]}


def trace_selector(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    costs: Sequence[int],
    budget: int,
    initial_profile: tuple[int, int],
    schedule: str,
    *,
    tie_mode: str = "min_cost",
    inertia: bool = True,
    graph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if schedule not in FROZEN_SCHEDULES:
        raise ValueError("unregistered schedule")
    programs = admitted(costs, budget)
    if any(program not in programs for program in initial_profile):
        raise ValueError("initial profile is not admitted")
    player = 0 if schedule == "row_first" else 1
    state = (initial_profile[0], initial_profile[1], player)
    seen = {state: 0}
    visited = [list(state)]
    transitions = []
    consecutive_no_change = 0
    limit = 2 * len(programs) ** 2 + 1
    termination = "update_limit"
    cycle_start: int | None = None
    for _ in range(limit):
        successor, decision = augmented_step(
            catalog,
            family,
            temptation,
            programs,
            costs,
            state,
            tie_mode=tie_mode,
            inertia=inertia,
        )
        transitions.append({"from": list(state), "to": list(successor), "decision": decision})
        visited.append(list(successor))
        consecutive_no_change = 0 if decision["changed"] else consecutive_no_change + 1
        if consecutive_no_change >= 2:
            termination = "fixed_profile"
            state = successor
            break
        if successor in seen:
            termination = "augmented_state_cycle"
            cycle_start = seen[successor]
            state = successor
            break
        seen[successor] = len(transitions)
        state = successor
    if termination == "update_limit":
        raise AssertionError("finite augmented-state bound was exceeded")
    terminal_profile = state[:2] if termination == "fixed_profile" else None
    if terminal_profile is not None:
        observed_cycle = _canonical_cycle(
            (
                (terminal_profile[0], terminal_profile[1], 0),
                (terminal_profile[0], terminal_profile[1], 1),
            )
        )
    else:
        if cycle_start is None:
            raise AssertionError("cycle termination lacks a repeated-state index")
        observed_cycle = _canonical_cycle(
            tuple(tuple(item) for item in visited[cycle_start:-1])
        )
    graph = graph or complete_augmented_graph(
        catalog,
        family,
        temptation,
        costs,
        budget,
        tie_mode=tie_mode,
        inertia=inertia,
    )
    start_edge = _edge_lookup(graph)[tuple(visited[0])]
    attractor_id = start_edge["attractor_id"]
    attractor = next(item for item in graph["attractors"] if item["id"] == attractor_id)
    return {
        "initial_augmented_state": visited[0],
        "visited_augmented_states": visited,
        "transitions": transitions,
        "termination": termination,
        "cycle_start_transition": cycle_start,
        "terminal_profile": list(terminal_profile) if terminal_profile is not None else None,
        "scheduled_updates": len(transitions),
        "changed_moves": sum(item["decision"]["changed"] for item in transitions),
        "attractor_id": attractor_id,
        "attractor_cycle": attractor["cycle"],
        "observed_attractor_cycle": [list(item) for item in observed_cycle],
        "reported_attractor_matches_observed": attractor["cycle"]
        == [list(item) for item in observed_cycle],
    }


def expected_primary_endpoint(
    family: str, temptation: Fraction, budget: int, schedule: str
) -> tuple[int, int]:
    if budget == 2 or temptation <= 3:
        return FROZEN_START
    if family == "pd_threshold":
        return (2, 0) if schedule == "row_first" else (0, 2)
    return (2, 1) if schedule == "row_first" else (1, 2)


def primary_row(
    family: str,
    temptation: Fraction,
    budget: int,
    schedule: str,
    graph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    graph = graph or complete_augmented_graph(
        CANONICAL_CATALOG, family, temptation, FROZEN_COSTS, budget
    )
    trace = trace_selector(
        CANONICAL_CATALOG,
        family,
        temptation,
        FROZEN_COSTS,
        budget,
        FROZEN_START,
        schedule,
        graph=graph,
    )
    terminal = tuple(trace["terminal_profile"] or ())
    selected_actions = actions(CANONICAL_CATALOG, *terminal)
    selected_payoff = payoff(CANONICAL_CATALOG, family, temptation, terminal)
    equilibria = pure_equilibria(
        CANONICAL_CATALOG, family, temptation, admitted(FROZEN_COSTS, budget)
    )
    expected = expected_primary_endpoint(family, temptation, budget, schedule)
    cooperative = selected_actions == (1, 1)
    return {
        "family": family,
        "temptation": fraction_text(temptation),
        "budget": budget,
        "schedule": schedule,
        "initial_profile": list(FROZEN_START),
        "trace": trace,
        "terminal_profile": list(terminal),
        "terminal_actions": list(selected_actions),
        "terminal_payoffs": [fraction_text(value) for value in selected_payoff],
        "cooperative_selected": cooperative,
        "available_pure_equilibria": [list(profile) for profile in equilibria],
        "checks": {
            "expected_endpoint": terminal == expected,
            "expected_cooperation": cooperative == (budget == 2 or temptation <= 3),
            "fixed_profile": trace["termination"] == "fixed_profile",
            "selected_profile_is_pure_equilibrium": terminal in equilibria,
            "initialized_state_binds_to_graph_attractor": trace[
                "reported_attractor_matches_observed"
            ]
            and trace["attractor_cycle"]
            == next(
                item["cycle"]
                for item in graph["attractors"]
                if item["id"] == trace["attractor_id"]
            ),
        },
    }


def primary_registry_keys() -> tuple[tuple[str, Fraction, int, str], ...]:
    return tuple(
        (family, temptation, budget, schedule)
        for family in FROZEN_FAMILIES
        for temptation in FROZEN_TEMPTATIONS
        for budget in FROZEN_BUDGETS
        for schedule in FROZEN_SCHEDULES
    )


def graph_registry_keys() -> tuple[tuple[str, Fraction, int], ...]:
    return tuple(
        (family, temptation, budget)
        for family in FROZEN_FAMILIES
        for temptation in FROZEN_TEMPTATIONS
        for budget in FROZEN_BUDGETS
    )


def fair_schedule_aggregate(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) != 2 or {row["schedule"] for row in rows} != set(FROZEN_SCHEDULES):
        raise ValueError("fair aggregate requires exactly both schedules")
    atoms: Counter[tuple[Any, ...]] = Counter()
    for row in rows:
        atoms[
            (
                tuple(row["terminal_profile"]),
                tuple(row["terminal_actions"]),
                tuple(row["terminal_payoffs"]),
                row["cooperative_selected"],
            )
        ] += 1
    ordered_atoms = []
    for key, count in sorted(atoms.items()):
        profile, action_pair, payoffs, cooperative = key
        ordered_atoms.append(
            {
                "terminal_profile": list(profile),
                "terminal_actions": list(action_pair),
                "terminal_payoffs": list(payoffs),
                "cooperative_selected": cooperative,
                "weight": fraction_text(Fraction(count, 2)),
            }
        )
    first = rows[0]
    return {
        "family": first["family"],
        "temptation": first["temptation"],
        "budget": first["budget"],
        "schedule_weights": {"row_first": "1/2", "column_first": "1/2"},
        "outcome_atoms": ordered_atoms,
        "cooperation_distribution": [
            {
                "cooperative_selected": first["cooperative_selected"],
                "weight": "1/1",
            }
        ],
        "point_mass_cooperation": rows[0]["cooperative_selected"]
        == rows[1]["cooperative_selected"],
        "distinct_terminal_profiles": len(atoms),
    }


def relabel_catalog(
    catalog: Sequence[Sequence[int]],
    costs: Sequence[int],
    permutation: Sequence[int],
) -> tuple[tuple[tuple[int, ...], ...], tuple[int, ...]]:
    if tuple(sorted(permutation)) != (0, 1, 2):
        raise ValueError("not a program permutation")
    transformed = [[0] * 3 for _ in range(3)]
    transformed_costs = [0] * 3
    for old_program in range(3):
        new_program = permutation[old_program]
        transformed_costs[new_program] = costs[old_program]
        for old_opponent in range(3):
            transformed[new_program][permutation[old_opponent]] = catalog[old_program][
                old_opponent
            ]
    return tuple(tuple(row) for row in transformed), tuple(transformed_costs)


def _map_state_back(state: Sequence[int], inverse: Sequence[int]) -> list[int]:
    return [inverse[state[0]], inverse[state[1]], state[2]]


def _map_profile_back(profile: Sequence[int], inverse: Sequence[int]) -> list[int]:
    return [inverse[profile[0]], inverse[profile[1]]]


def _normalized_cycle_back(
    cycle: Sequence[Sequence[int]], inverse: Sequence[int]
) -> list[list[int]]:
    mapped = tuple(tuple(_map_state_back(state, inverse)) for state in cycle)
    return [list(state) for state in _canonical_cycle(mapped)]


def _decision_signature_back(
    decision: dict[str, Any], inverse: Sequence[int]
) -> dict[str, Any]:
    candidates = sorted(
        (
            {"program": inverse[item["program"]], "payoff": item["payoff"]}
            for item in decision["candidate_payoffs"]
        ),
        key=lambda item: item["program"],
    )
    return {
        "player": decision["player"],
        "candidate_payoffs": candidates,
        "best_responses": sorted(inverse[item] for item in decision["best_responses"]),
        "best_payoff": decision["best_payoff"],
        "incumbent_is_best_response": decision["incumbent_is_best_response"],
        "chosen_program": inverse[decision["chosen_program"]],
        "reason": decision["reason"],
        "after_profile": _map_profile_back(decision["after_profile"], inverse),
        "changed": decision["changed"],
    }


def _semantic_trace_signature(
    trace: dict[str, Any], inverse: Sequence[int] = (0, 1, 2)
) -> dict[str, Any]:
    terminal = trace["terminal_profile"]
    return {
        "initial_augmented_state": _map_state_back(
            trace["initial_augmented_state"], inverse
        ),
        "visited_augmented_states": [
            _map_state_back(state, inverse)
            for state in trace["visited_augmented_states"]
        ],
        "transitions": [
            {
                "from": _map_state_back(item["from"], inverse),
                "to": _map_state_back(item["to"], inverse),
                "decision": _decision_signature_back(item["decision"], inverse),
            }
            for item in trace["transitions"]
        ],
        "termination": trace["termination"],
        "cycle_start_transition": trace["cycle_start_transition"],
        "terminal_profile": (
            _map_profile_back(terminal, inverse) if terminal is not None else None
        ),
        "scheduled_updates": trace["scheduled_updates"],
        "changed_moves": trace["changed_moves"],
        "attractor_cycle": _normalized_cycle_back(trace["attractor_cycle"], inverse),
        "observed_attractor_cycle": _normalized_cycle_back(
            trace["observed_attractor_cycle"], inverse
        ),
        "reported_attractor_matches_observed": trace[
            "reported_attractor_matches_observed"
        ],
    }


def relabel_trace_signature_back(
    trace: dict[str, Any], permutation: Sequence[int]
) -> dict[str, Any]:
    inverse = [0] * 3
    for old, new in enumerate(permutation):
        inverse[new] = old
    return _semantic_trace_signature(trace, inverse)


def _semantic_graph_signature(
    graph: dict[str, Any], inverse: Sequence[int] = (0, 1, 2)
) -> dict[str, Any]:
    attractor_cycles = {
        item["id"]: _normalized_cycle_back(item["cycle"], inverse)
        for item in graph["attractors"]
    }
    edges = [
        {
            "from": _map_state_back(edge["from"], inverse),
            "to": _map_state_back(edge["to"], inverse),
            "decision": _decision_signature_back(edge["decision"], inverse),
            "attractor_cycle": attractor_cycles[edge["attractor_id"]],
        }
        for edge in graph["edges"]
    ]
    edges.sort(key=lambda edge: tuple(edge["from"]))
    attractors = []
    for item in graph["attractors"]:
        fixed_profile = item["fixed_profile"]
        attractors.append(
            {
                "cycle": attractor_cycles[item["id"]],
                "cycle_length": item["cycle_length"],
                "kind": item["kind"],
                "fixed_profile": (
                    _map_profile_back(fixed_profile, inverse)
                    if fixed_profile is not None
                    else None
                ),
                "fixed_profile_is_pure_equilibrium": item[
                    "fixed_profile_is_pure_equilibrium"
                ],
                "basin_size": item["basin_size"],
                "basin_fraction": item["basin_fraction"],
            }
        )
    attractors.sort(key=lambda item: tuple(tuple(state) for state in item["cycle"]))
    return {
        "family": graph["family"],
        "temptation": graph["temptation"],
        "programs": sorted(inverse[program] for program in graph["programs"]),
        "state_count": graph["state_count"],
        "edge_count": graph["edge_count"],
        "edges": edges,
        "attractors": attractors,
        "checks": graph["checks"],
    }


def _selection_distribution_signature(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    schedule_traces: Sequence[tuple[str, dict[str, Any]]],
    inverse: Sequence[int] = (0, 1, 2),
) -> dict[str, Any]:
    outcomes = []
    atoms: Counter[tuple[Any, ...]] = Counter()
    for schedule, trace in schedule_traces:
        terminal = tuple(trace["terminal_profile"] or ())
        mapped_terminal = tuple(_map_profile_back(terminal, inverse))
        action_pair = actions(catalog, *terminal)
        payoffs = tuple(
            fraction_text(value) for value in payoff(catalog, family, temptation, terminal)
        )
        cooperative = action_pair == (1, 1)
        outcome = {
            "schedule": schedule,
            "terminal_profile": list(mapped_terminal),
            "terminal_actions": list(action_pair),
            "terminal_payoffs": list(payoffs),
            "cooperative_selected": cooperative,
        }
        outcomes.append(outcome)
        atoms[(mapped_terminal, action_pair, payoffs, cooperative)] += 1
    atom_rows = []
    for key, count in sorted(atoms.items()):
        terminal, action_pair, payoffs, cooperative = key
        atom_rows.append(
            {
                "terminal_profile": list(terminal),
                "terminal_actions": list(action_pair),
                "terminal_payoffs": list(payoffs),
                "cooperative_selected": cooperative,
                "weight": fraction_text(Fraction(count, len(schedule_traces))),
            }
        )
    return {
        "schedule_weights": {schedule: "1/2" for schedule in FROZEN_SCHEDULES},
        "schedule_outcomes": outcomes,
        "outcome_atoms": atom_rows,
    }


def _base_control_rows(
    catalog: Sequence[Sequence[int]], costs: Sequence[int] = FROZEN_COSTS
) -> list[dict[str, Any]]:
    rows = []
    graphs: dict[tuple[str, Fraction, int], dict[str, Any]] = {}
    for family, temptation, budget, schedule in primary_registry_keys():
        graph_key = (family, temptation, budget)
        if graph_key not in graphs:
            graphs[graph_key] = complete_augmented_graph(
                catalog, family, temptation, costs, budget
            )
        trace = trace_selector(
            catalog,
            family,
            temptation,
            costs,
            budget,
            FROZEN_START,
            schedule,
            graph=graphs[graph_key],
        )
        terminal = tuple(trace["terminal_profile"] or ())
        rows.append(
            {
                "family": family,
                "temptation": temptation,
                "budget": budget,
                "schedule": schedule,
                "graph": graphs[graph_key],
                "trace": trace,
                "terminal": terminal,
                "cooperative": actions(catalog, *terminal) == (1, 1),
            }
        )
    return rows


def simultaneous_trace(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    costs: Sequence[int],
    budget: int,
    initial_profile: tuple[int, int],
) -> dict[str, Any]:
    programs = admitted(costs, budget)
    profile = initial_profile
    seen = {profile: 0}
    visited = [list(profile)]
    for _ in range(len(programs) ** 2 + 1):
        row = best_response_decision(
            catalog, family, temptation, programs, costs, profile, 0
        )["chosen_program"]
        column = best_response_decision(
            catalog, family, temptation, programs, costs, profile, 1
        )["chosen_program"]
        after = (row, column)
        visited.append(list(after))
        if after == profile:
            return {"termination": "fixed_profile", "visited_profiles": visited}
        if after in seen:
            return {
                "termination": "profile_cycle",
                "visited_profiles": visited,
                "cycle": visited[seen[after] : -1],
            }
        seen[after] = len(visited) - 1
        profile = after
    raise AssertionError("simultaneous state bound exceeded")


def cycle_detection_fixture() -> dict[str, Any]:
    trace = trace_selector(
        CYCLE_FIXTURE_CATALOG,
        "pd_threshold",
        Fraction(301, 100),
        FROZEN_COSTS,
        3,
        (0, 0),
        "row_first",
    )
    return {
        "catalog": ["CCD", "DCC", "CDC"],
        "termination": trace["termination"],
        "cycle_start_transition": trace["cycle_start_transition"],
        "observed_attractor_cycle": trace["observed_attractor_cycle"],
        "reported_attractor_cycle": trace["attractor_cycle"],
        "pass": trace["termination"] == "augmented_state_cycle"
        and len(trace["observed_attractor_cycle"]) == 6
        and trace["reported_attractor_matches_observed"],
    }


def build_controls(primary_rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    canonical_rows = _base_control_rows(CANONICAL_CATALOG)
    repaired_rows = _base_control_rows(REPAIRED_CATALOG)
    source_blind_rows = _base_control_rows(SOURCE_BLIND_CATALOG)
    semantic_rows = {
        "canonical": canonical_rows,
        "repaired": repaired_rows,
        "source_blind": source_blind_rows,
    }

    padding_trace_comparisons = 0
    padding_graph_comparisons = 0
    padding_distribution_comparisons = 0
    padding_traces_exact = True
    padding_graphs_exact = True
    padding_distributions_exact = True
    relabel_trace_comparisons = 0
    relabel_graph_comparisons = 0
    relabel_distribution_comparisons = 0
    relabel_traces_exact = True
    relabel_graphs_exact = True
    relabel_distributions_exact = True
    for catalog_id, rows in semantic_rows.items():
        catalog = CATALOGS[catalog_id]
        padded_costs = tuple(cost + 2 for cost in FROZEN_COSTS)
        for family, temptation, budget in graph_registry_keys():
            matched = [
                row
                for row in rows
                if (row["family"], row["temptation"], row["budget"])
                == (family, temptation, budget)
            ]
            base_schedule_traces = [
                (row["schedule"], row["trace"]) for row in matched
            ]
            base_graph = matched[0]["graph"]
            padded_graph = complete_augmented_graph(
                catalog, family, temptation, padded_costs, budget + 2
            )
            padding_graph_comparisons += 1
            padding_graphs_exact = padding_graphs_exact and (
                _semantic_graph_signature(base_graph)
                == _semantic_graph_signature(padded_graph)
            )
            padded_schedule_traces = []
            for row in matched:
                padded_trace = trace_selector(
                    catalog,
                    family,
                    temptation,
                    padded_costs,
                    budget + 2,
                    FROZEN_START,
                    row["schedule"],
                    graph=padded_graph,
                )
                padded_schedule_traces.append((row["schedule"], padded_trace))
                padding_trace_comparisons += 1
                padding_traces_exact = padding_traces_exact and (
                    _semantic_trace_signature(row["trace"])
                    == _semantic_trace_signature(padded_trace)
                )
            padding_distribution_comparisons += 1
            padding_distributions_exact = padding_distributions_exact and (
                _selection_distribution_signature(
                    catalog, family, temptation, base_schedule_traces
                )
                == _selection_distribution_signature(
                    catalog, family, temptation, padded_schedule_traces
                )
            )
            for permutation in itertools.permutations(range(3)):
                transformed, transformed_costs = relabel_catalog(
                    catalog, FROZEN_COSTS, permutation
                )
                inverse = [0] * 3
                for old, new in enumerate(permutation):
                    inverse[new] = old
                transformed_start = (
                    permutation[FROZEN_START[0]],
                    permutation[FROZEN_START[1]],
                )
                transformed_graph = complete_augmented_graph(
                    transformed,
                    family,
                    temptation,
                    transformed_costs,
                    budget,
                )
                relabel_graph_comparisons += 1
                relabel_graphs_exact = relabel_graphs_exact and (
                    _semantic_graph_signature(base_graph)
                    == _semantic_graph_signature(transformed_graph, inverse)
                )
                transformed_schedule_traces = []
                for row in matched:
                    transformed_trace = trace_selector(
                        transformed,
                        family,
                        temptation,
                        transformed_costs,
                        budget,
                        transformed_start,
                        row["schedule"],
                        graph=transformed_graph,
                    )
                    transformed_schedule_traces.append(
                        (row["schedule"], transformed_trace)
                    )
                    relabel_trace_comparisons += 1
                    relabel_traces_exact = relabel_traces_exact and (
                        _semantic_trace_signature(row["trace"])
                        == relabel_trace_signature_back(
                            transformed_trace, permutation
                        )
                    )
                relabel_distribution_comparisons += 1
                relabel_distributions_exact = relabel_distributions_exact and (
                    _selection_distribution_signature(
                        catalog, family, temptation, base_schedule_traces
                    )
                    == _selection_distribution_signature(
                        transformed,
                        family,
                        temptation,
                        transformed_schedule_traces,
                        inverse,
                    )
                )

    source_blind_no_budget_effect = True
    for family in FROZEN_FAMILIES:
        for temptation in FROZEN_TEMPTATIONS:
            for schedule in FROZEN_SCHEDULES:
                matches = [
                    row
                    for row in source_blind_rows
                    if (row["family"], row["temptation"], row["schedule"])
                    == (family, temptation, schedule)
                ]
                source_blind_no_budget_effect = source_blind_no_budget_effect and len(matches) == 2
                source_blind_no_budget_effect = source_blind_no_budget_effect and (
                    matches[0]["terminal"] == matches[1]["terminal"]
                    and matches[0]["cooperative"] == matches[1]["cooperative"]
                )

    inertia_main = trace_selector(
        CANONICAL_CATALOG,
        "pd_threshold",
        Fraction(301, 100),
        FROZEN_COSTS,
        3,
        (2, 0),
        "row_first",
    )
    inertia_mutation = trace_selector(
        CANONICAL_CATALOG,
        "pd_threshold",
        Fraction(301, 100),
        FROZEN_COSTS,
        3,
        (2, 0),
        "row_first",
        inertia=False,
    )
    max_cost_rows = []
    simultaneous = []
    for family in FROZEN_FAMILIES:
        for schedule in FROZEN_SCHEDULES:
            max_cost_rows.append(
                {
                    "family": family,
                    "schedule": schedule,
                    "trace": trace_selector(
                        CANONICAL_CATALOG,
                        family,
                        Fraction(301, 100),
                        FROZEN_COSTS,
                        3,
                        FROZEN_START,
                        schedule,
                        tie_mode="max_cost",
                    ),
                }
            )
        simultaneous.append(
            {
                "family": family,
                "trace": simultaneous_trace(
                    CANONICAL_CATALOG,
                    family,
                    Fraction(301, 100),
                    FROZEN_COSTS,
                    3,
                    FROZEN_START,
                ),
            }
        )

    distinct_condition_keys = [
        (family, temptation, budget)
        for family, temptation, budget in graph_registry_keys()
        if fair_schedule_aggregate(
            [
                row
                for row in primary_rows
                if (row["family"], row["temptation"], row["budget"])
                == (family, fraction_text(temptation), budget)
            ]
        )["distinct_terminal_profiles"]
        == 2
    ]
    expected_distinct_keys = [
        (family, Fraction(301, 100), 3) for family in FROZEN_FAMILIES
    ]
    selected_pure = all(
        row["checks"]["selected_profile_is_pure_equilibrium"] for row in primary_rows
    )
    repaired_pass = all(row["cooperative"] for row in repaired_rows)
    blind_early = all(
        not row["cooperative"]
        for row in source_blind_rows
        if row["temptation"] > 3
    )
    inertia_distinguishes = (
        inertia_main["terminal_profile"] != inertia_mutation["terminal_profile"]
    )
    cycle_fixture = cycle_detection_fixture()
    max_cost_pd_changes = all(
        row["trace"]["terminal_profile"] == [2, 2]
        for row in max_cost_rows
        if row["family"] == "pd_threshold"
    )
    simultaneous_pd_p2_p2 = next(
        row for row in simultaneous if row["family"] == "pd_threshold"
    )["trace"] == {
        "termination": "fixed_profile",
        "visited_profiles": [[1, 1], [2, 2], [2, 2]],
    }
    simultaneous_chicken_cycle = (
        next(row for row in simultaneous if row["family"] == "chicken_threshold")[
            "trace"
        ]["termination"]
        == "profile_cycle"
    )
    distinct_exact = distinct_condition_keys == expected_distinct_keys
    return {
        "repaired_duplicate_extensional": {
            "trajectory_count": len(repaired_rows),
            "cooperative_count": sum(row["cooperative"] for row in repaired_rows),
            "all_initialized_cooperation_retained": repaired_pass,
            "pass": repaired_pass,
        },
        "source_blind_early_vulnerability": {
            "trajectory_count": len(source_blind_rows),
            "cooperative_count": sum(row["cooperative"] for row in source_blind_rows),
            "no_budget_induced_change": source_blind_no_budget_effect,
            "above_threshold_is_already_vulnerable_at_budget_two": all(
                not row["cooperative"]
                for row in source_blind_rows
                if row["temptation"] > 3
            ),
            "pass": source_blind_no_budget_effect and blind_early,
        },
        "additive_cost_padding": {
            "trace_comparison_count": padding_trace_comparisons,
            "graph_relation_comparison_count": padding_graph_comparisons,
            "distribution_comparison_count": padding_distribution_comparisons,
            "all_traces_exact": padding_traces_exact,
            "all_graph_relations_exact": padding_graphs_exact,
            "all_selected_distributions_exact": padding_distributions_exact,
            "pass": padding_traces_exact
            and padding_graphs_exact
            and padding_distributions_exact,
        },
        "six_semantic_relabelings": {
            "permutation_count": math.factorial(3),
            "trace_comparison_count": relabel_trace_comparisons,
            "graph_relation_comparison_count": relabel_graph_comparisons,
            "distribution_comparison_count": relabel_distribution_comparisons,
            "all_mapped_traces_exact": relabel_traces_exact,
            "all_mapped_graph_relations_exact": relabel_graphs_exact,
            "all_mapped_selected_distributions_exact": relabel_distributions_exact,
            "pass": relabel_traces_exact
            and relabel_graphs_exact
            and relabel_distributions_exact
            and relabel_trace_comparisons == 432
            and relabel_graph_comparisons == 216
            and relabel_distribution_comparisons == 216,
        },
        "inertia_and_cycle_fixtures": {
            "main_terminal_profile": inertia_main["terminal_profile"],
            "noninertial_terminal_profile": inertia_mutation["terminal_profile"],
            "distinguishes_inertia_rule": inertia_distinguishes,
            "cycle_fixture": cycle_fixture,
            "pass": inertia_distinguishes and cycle_fixture["pass"],
        },
        "max_cost_and_simultaneous_scope_breakers": {
            "max_cost_rows": max_cost_rows,
            "simultaneous_rows": simultaneous,
            "max_cost_pd_profile_changes": max_cost_pd_changes,
            "simultaneous_pd_selects_p2_p2": simultaneous_pd_p2_p2,
            "simultaneous_chicken_cycles": simultaneous_chicken_cycle,
            "selection_validity": {
                "all_initialized_terminal_profiles_are_pure_equilibria": selected_pure,
                "distinct_schedule_equilibrium_conditions": len(
                    distinct_condition_keys
                ),
                "distinct_condition_keys": [
                    [family, fraction_text(temptation), budget]
                    for family, temptation, budget in distinct_condition_keys
                ],
                "distinct_only_in_two_b3_above_threshold_conditions": distinct_exact,
            },
            "pass": max_cost_pd_changes
            and simultaneous_pd_p2_p2
            and simultaneous_chicken_cycle
            and selected_pure
            and distinct_exact,
        },
    }


def build_metric_robustness(
    rows: Sequence[dict[str, Any]], controls: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    b3_by_family_schedule: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for family in FROZEN_FAMILIES:
        for schedule in FROZEN_SCHEDULES:
            b3_by_family_schedule[(family, schedule)] = [
                row
                for row in rows
                if row["family"] == family
                and row["schedule"] == schedule
                and row["budget"] == 3
            ]
    monotone = all(
        [row["cooperative_selected"] for row in selected] == [True, True, False]
        for selected in b3_by_family_schedule.values()
    )
    return {
        "P1_encoding_invariance": {
            "family": "invariance",
            "pass": controls["additive_cost_padding"]["pass"]
            and controls["six_semantic_relabelings"]["pass"],
        },
        "P2_threshold_sensitivity": {
            "family": "sensitivity",
            "pass": sum(row["cooperative_selected"] for row in rows) == 20,
        },
        "P3_registered_monotonicity": {
            "family": "monotonicity",
            "pass": monotone,
        },
        "P4_anti_gaming": {
            "family": "anti_gaming",
            "pass": controls["inertia_and_cycle_fixtures"][
                "distinguishes_inertia_rule"
            ]
            and controls["inertia_and_cycle_fixtures"]["cycle_fixture"]["pass"]
            and controls["max_cost_and_simultaneous_scope_breakers"][
                "max_cost_pd_profile_changes"
            ]
            and controls["max_cost_and_simultaneous_scope_breakers"][
                "simultaneous_chicken_cycles"
            ],
        },
        "P5_clean_controls": {
            "family": "clean_control",
            "pass": controls["repaired_duplicate_extensional"][
                "all_initialized_cooperation_retained"
            ]
            and controls["source_blind_early_vulnerability"]["no_budget_induced_change"]
            and controls["max_cost_and_simultaneous_scope_breakers"][
                "selection_validity"
            ]["all_initialized_terminal_profiles_are_pure_equilibria"],
        },
    }


def _git_environment() -> dict[str, str]:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    return environment


def _git(args: list[str], *, text: bool, cwd: Path | None = None) -> str | bytes:
    if GIT_EXECUTABLE is None:
        raise RuntimeError("trusted Git executable is unavailable")
    completed = subprocess.run(
        [GIT_EXECUTABLE, *args],
        cwd=cwd or HERE,
        env=_git_environment(),
        check=True,
        capture_output=True,
        text=text,
    )
    return completed.stdout.strip() if text else completed.stdout


def repo_root() -> Path:
    return Path(os.path.abspath(str(_git(["rev-parse", "--show-toplevel"], text=True))))


def validate_git_view(root: Path) -> None:
    git_directory = Path(
        os.path.abspath(str(_git(["rev-parse", "--absolute-git-dir"], text=True, cwd=root)))
    )
    grafts = git_directory / "info" / "grafts"
    if grafts.exists() and grafts.stat().st_size:
        raise ValueError("legacy Git grafts are forbidden")
    if str(
        _git(
            ["for-each-ref", "--format=%(refname)", "refs/replace"],
            text=True,
            cwd=root,
        )
    ):
        raise ValueError("Git replacement refs are forbidden")
    if str(_git(["rev-parse", "--is-shallow-repository"], text=True, cwd=root)) != "false":
        raise ValueError("shallow repository is forbidden")


def validate_predecessor_bindings(manifest: dict[str, Any]) -> dict[str, Any]:
    root = repo_root()
    validate_git_view(root)
    binding = manifest["predecessor_binding"]
    evidence_commit = binding["evidence_commit"]
    source_checkpoint = binding["source_checkpoint"]
    commits = (source_checkpoint, evidence_commit)
    for commit in commits:
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ValueError("predecessor commit is not full lowercase hex")
        if str(_git(["cat-file", "-t", commit], text=True, cwd=root)) != "commit":
            raise ValueError("predecessor object is not a commit")
        if subprocess.run(
            [GIT_EXECUTABLE, "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=root,
            env=_git_environment(),
        ).returncode:
            raise ValueError("predecessor commit is not an ancestor")
    files = []
    for item in binding["files"]:
        payload = bytes(
            _git(
                ["show", f"{evidence_commit}:{item['path']}"],
                text=False,
                cwd=root,
            )
        )
        digest = sha256_bytes(payload)
        if digest != item["sha256"]:
            raise ValueError(f"predecessor hash mismatch: {item['path']}")
        files.append(
            {"commit": evidence_commit, "path": item["path"], "role": item["role"], "sha256": digest}
        )
    return {
        "source_checkpoint": source_checkpoint,
        "evidence_commit": evidence_commit,
        "files": files,
        "all_hashes_match": True,
    }


def _resource_check(
    start_ns: int,
    wall_limit_ns: int,
    traced_limit_bytes: int,
    clock_ns: Callable[[], int],
) -> None:
    if clock_ns() - start_ns > wall_limit_ns:
        raise ResourceStop("wall_limit_after_completed_stage")
    if tracemalloc.get_traced_memory()[1] > traced_limit_bytes:
        raise ResourceStop("traced_python_memory_limit_after_completed_stage")


def compile_result(
    manifest: dict[str, Any],
    source_binding: dict[str, Any],
    *,
    clock_ns: Callable[[], int] = time.monotonic_ns,
) -> dict[str, Any]:
    manifest_checks = validate_manifest_binding(manifest)
    predecessor = validate_predecessor_bindings(manifest)
    wall_limit_ns = manifest["budget"]["max_wall_seconds"] * 1_000_000_000
    traced_limit_bytes = manifest["budget"]["max_traced_python_mib"] * 1024 * 1024
    start_ns = clock_ns()
    owned_trace = not tracemalloc.is_tracing()
    if owned_trace:
        tracemalloc.start()
    tracemalloc.reset_peak()
    graph_cells: list[dict[str, Any]] = []
    primary_rows: list[dict[str, Any]] = []
    aggregates: list[dict[str, Any]] = []
    controls: dict[str, Any] = {}
    probes: dict[str, Any] = {}
    status = "complete"
    stop_reason = "registered_contract_complete"
    try:
        graph_map = {}
        for key in graph_registry_keys():
            _resource_check(start_ns, wall_limit_ns, traced_limit_bytes, clock_ns)
            graph = complete_augmented_graph(
                CANONICAL_CATALOG, key[0], key[1], FROZEN_COSTS, key[2]
            )
            graph_cells.append(graph)
            graph_map[key] = graph
        for family, temptation, budget, schedule in primary_registry_keys():
            _resource_check(start_ns, wall_limit_ns, traced_limit_bytes, clock_ns)
            primary_rows.append(
                primary_row(
                    family, temptation, budget, schedule, graph_map[(family, temptation, budget)]
                )
            )
        for family, temptation, budget in graph_registry_keys():
            rows = [
                row
                for row in primary_rows
                if (row["family"], row["temptation"], row["budget"])
                == (family, fraction_text(temptation), budget)
            ]
            aggregates.append(fair_schedule_aggregate(rows))
        controls = build_controls(primary_rows)
        probes = build_metric_robustness(primary_rows, controls)
        _resource_check(start_ns, wall_limit_ns, traced_limit_bytes, clock_ns)
    except ResourceStop as error:
        status = "stopped_resource"
        stop_reason = str(error)
    elapsed_ns = clock_ns() - start_ns
    peak_bytes = tracemalloc.get_traced_memory()[1]
    if owned_trace:
        tracemalloc.stop()
    source_valid = bool(
        source_binding.get("source_commit_type") == "commit"
        and source_binding.get("source_commit_is_ancestor_of_head") is True
        and tuple(source_binding.get("source_files", {})) == FROZEN_SOURCE_FILES
    )
    graph_valid = bool(
        len(graph_cells) == 12
        and sum(cell["state_count"] for cell in graph_cells) == 156
        and all(all(cell["checks"].values()) for cell in graph_cells)
    )
    rows_valid = bool(
        len(primary_rows) == 24
        and all(all(row["checks"].values()) for row in primary_rows)
    )
    counts_valid = (
        sum(row["cooperative_selected"] for row in primary_rows) == 20
        and sum(not row["cooperative_selected"] for row in primary_rows) == 4
    )
    controls_valid = tuple(controls) == FROZEN_CONTROL_IDS and all(
        record["pass"] is True for record in controls.values()
    )
    gates = {
        "G0_manifest_source_and_predecessor_bindings": all(manifest_checks.values())
        and source_valid
        and predecessor["all_hashes_match"],
        "G1_complete_12_graph_registry": status == "complete" and graph_valid,
        "G2_complete_24_initialized_trajectories": status == "complete" and rows_valid,
        "G3_exact_20_cooperative_4_noncooperative": status == "complete" and counts_valid,
        "G4_initialized_rows_bind_to_graph_attractors": status == "complete"
        and all(
            row["checks"]["initialized_state_binds_to_graph_attractor"]
            for row in primary_rows
        ),
        "G5_selected_profiles_are_pure_equilibria": status == "complete"
        and all(row["checks"]["selected_profile_is_pure_equilibrium"] for row in primary_rows),
        "G6_controls_and_scope_breakers": status == "complete" and controls_valid,
        "G7_five_metric_probe_families": status == "complete"
        and tuple(probes) == FROZEN_PROBE_IDS
        and all(record["pass"] for record in probes.values()),
        "G8_exact_arithmetic_and_resources": status == "complete"
        and elapsed_ns <= wall_limit_ns
        and peak_bytes <= traced_limit_bytes
        and not contains_float(
            {"graphs": graph_cells, "rows": primary_rows, "controls": controls}
        ),
    }
    passed = status == "complete" and all(gates.values())
    layers = (
        dict(FROZEN_PREVERIFICATION_LAYERS)
        if passed
        else {
            "metric_robustness": "not_established",
            "task_result": "not_established",
            "measurement_reliability": "failed",
            "claim_support": "none",
            "operational_decision": "no_deployment_authorization_repair",
        }
    )
    result = {
        "schema_version": "asmp12_inertial_selector_result_v0_4",
        "protocol_id": FROZEN_PROTOCOL_ID,
        "manifest_sha256": FROZEN_MANIFEST_CANONICAL_SHA256,
        "source_binding": source_binding,
        "predecessor_binding": predecessor,
        "status": status,
        "stop_reason": stop_reason,
        "resource_observations": {
            "canonical_result_bytes": 0,
            "completed_graph_cells": len(graph_cells),
            "completed_primary_trajectories": len(primary_rows),
            "elapsed_wall_ns": elapsed_ns,
            "wall_limit_ns": wall_limit_ns,
            "traced_python_peak_bytes": peak_bytes,
            "traced_python_limit_bytes": traced_limit_bytes,
            "memory_measurement": "tracemalloc_peak_python_allocation_only",
            "process_rss_and_native_memory_measured": False,
        },
        "graph_cells": graph_cells,
        "primary_rows": primary_rows,
        "fair_schedule_aggregates": aggregates,
        "controls": controls,
        "metric_robustness": probes,
        "gates": gates,
        "conclusion_layers": layers,
        "claim_boundary": list(manifest["claim_boundary"]),
    }
    if set(result) != FROZEN_RESULT_FIELDS or tuple(gates) != FROZEN_PRIMARY_GATES:
        raise AssertionError("result or gate universe changed")
    for _ in range(10):
        size = len(canonical_json(result).encode("utf-8"))
        if result["resource_observations"]["canonical_result_bytes"] == size:
            break
        result["resource_observations"]["canonical_result_bytes"] = size
    else:
        raise AssertionError("result byte-count fixed point failed")
    return result


def _is_reparse_point(path: Path) -> bool:
    metadata = path.lstat()
    attributes = getattr(metadata, "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return path.is_symlink() or bool(attributes & flag)


def live_source_inventory_checks(directory: Path = HERE) -> dict[str, Any]:
    expected = set(FROZEN_SOURCE_FILES)
    try:
        entries = {entry.name: entry for entry in directory.iterdir()}
        directory_reparse = _is_reparse_point(directory)
    except OSError as error:
        return {
            "pass": False,
            "error": type(error).__name__,
            "missing": sorted(expected),
            "unexpected": [],
            "invalid": [],
        }
    invalid = []
    for name in sorted(expected & set(entries)):
        try:
            if _is_reparse_point(entries[name]) or not entries[name].is_file():
                invalid.append(name)
        except OSError:
            invalid.append(name)
    return {
        "pass": not (
            directory_reparse
            or expected - set(entries)
            or set(entries) - expected
            or invalid
        ),
        "error": "",
        "missing": sorted(expected - set(entries)),
        "unexpected": sorted(set(entries) - expected),
        "invalid": invalid,
    }


def validate_live_source_inventory(directory: Path = HERE) -> dict[str, Any]:
    checks = live_source_inventory_checks(directory)
    if not checks["pass"]:
        raise ValueError(f"live source inventory failed: {checks}")
    return checks


def _absolute_without_reparse_resolution(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _destination_chain(destination: Path) -> tuple[Path, ...]:
    chain = [destination]
    while chain[-1].parent != chain[-1]:
        chain.append(chain[-1].parent)
    chain.reverse()
    return tuple(chain)


def _prepare_write_once_destination(path: Path) -> Path:
    destination = _absolute_without_reparse_resolution(path)
    chain = _destination_chain(destination)
    for component in chain[:-1]:
        try:
            metadata = component.lstat()
        except FileNotFoundError:
            component.mkdir()
            metadata = component.lstat()
        if _is_reparse_point(component) or not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"unsafe artifact ancestor: {component}")
    try:
        destination.lstat()
    except FileNotFoundError:
        pass
    else:
        raise FileExistsError(f"artifact destination already exists: {destination}")
    for component in chain[:-1]:
        metadata = component.lstat()
        if _is_reparse_point(component) or not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"unsafe artifact ancestor: {component}")
    return destination


def write_once_json(path: Path, value: Any, max_bytes: int = 1048576) -> None:
    payload = canonical_json(value).encode("utf-8")
    if len(payload) > max_bytes:
        raise ResourceStop("artifact_byte_ceiling")
    destination = _prepare_write_once_destination(path)
    with destination.open("xb") as stream:
        stream.write(payload)
