"""Import-independent exact verifier for the ASMP-12 inertial selector v0.4."""

from __future__ import annotations

import sys as _sys


if __name__ == "__main__" and not (
    _sys.flags.isolated and getattr(_sys.flags, "safe_path", False)
):
    raise SystemExit(
        "refusing unsafe launch before imports; invoke with "
        "`python -I verify_independent.py ...`"
    )
if __name__ == "__main__":
    _sys.dont_write_bytecode = True


import argparse
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
ARTIFACT_DIRECTORY = HERE.parent / "artifacts_v0_4_inertial_selector"
PROTOCOL_ID = "ASMP12-INERTIAL-SELECTOR-v0.4"
MANIFEST_SCHEMA = "asmp12_inertial_selector_manifest_v0_4"
MANIFEST_DIGEST = "acd64f90bf96063eeeaf88592869c65af1d2bcdb1e9ec91fc7c25eee70a26f67"
SOURCE_FILES = (
    "PROTOCOL_v0_4.md",
    "README.md",
    "SOURCE_FREEZE.md",
    "inertial_selector.py",
    "manifest_v0_4.json",
    "run.py",
    "test_inertial_selector.py",
    "verify_independent.py",
)
FAMILIES = {
    "chicken_threshold": {"R": Fraction(3), "S": Fraction(1), "P": Fraction(0)},
    "pd_threshold": {"R": Fraction(3), "S": Fraction(0), "P": Fraction(1)},
}
TEMPTATIONS = (Fraction(299, 100), Fraction(3), Fraction(301, 100))
BUDGETS = (2, 3)
SCHEDULES = ("row_first", "column_first")
COSTS = (1, 2, 3)
START = (1, 1)
CANONICAL = ((0, 0, 0), (0, 1, 1), (0, 0, 0))
REPAIRED = ((0, 0, 0), (0, 1, 0), (0, 0, 0))
SOURCE_BLIND = ((0, 0, 0), (1, 1, 1), (0, 0, 0))
CYCLE_FIXTURE = ((1, 1, 0), (0, 1, 1), (1, 0, 1))
CATALOGS = {
    "canonical": CANONICAL,
    "repaired": REPAIRED,
    "source_blind": SOURCE_BLIND,
}
RESULT_FIELDS = {
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
PRIMARY_GATES = (
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
PROBE_IDS = (
    "P1_encoding_invariance",
    "P2_threshold_sensitivity",
    "P3_registered_monotonicity",
    "P4_anti_gaming",
    "P5_clean_controls",
)
CONTROL_IDS = (
    "repaired_duplicate_extensional",
    "source_blind_early_vulnerability",
    "additive_cost_padding",
    "six_semantic_relabelings",
    "inertia_and_cycle_fixtures",
    "max_cost_and_simultaneous_scope_breakers",
)
PREVERIFICATION_LAYERS = {
    "metric_robustness": "five_probe_families_computed_awaiting_independent_replay",
    "task_result": "finite_initialized_inertial_selector_threshold_computed",
    "measurement_reliability": "awaiting_import_independent_verification",
    "claim_support": "pending_independent_verification",
    "operational_decision": "no_deployment_authorization_await_independent_verification",
}
FINAL_LAYERS = {
    "metric_robustness": "five_probe_families_independently_replayed",
    "task_result": "finite_initialized_inertial_selector_threshold_computed",
    "measurement_reliability": "independent_exact_graph_trace_and_source_replay_passed",
    "claim_support": "finite_registered_selector_claim_supported",
    "operational_decision": "no_deployment_authorization",
}
VERIFICATION_GATES = (
    "V0_frozen_manifest_binding",
    "V1_exact_live_and_source_commit_binding",
    "V2_exact_predecessor_binding",
    "V3_result_identity_and_canonical_json",
    "V4_complete_independent_augmented_graphs",
    "V5_complete_independent_initialized_traces",
    "V6_exact_fair_schedule_distributions",
    "V7_independent_controls_and_scope_breakers",
    "V8_five_metric_probe_families",
    "V9_primary_gates_and_preverification_layers",
    "V10_resource_observations_within_contract",
)
VERIFICATION_FIELDS = {
    "schema_version",
    "pass",
    "protocol_id",
    "manifest_binding",
    "source_binding_error",
    "source_binding_replay",
    "predecessor_binding_error",
    "predecessor_binding_replay",
    "result_semantic_checks",
    "graph_mismatches",
    "primary_row_mismatches",
    "aggregate_mismatches",
    "control_mismatches",
    "metric_mismatches",
    "verification_resource_observations",
    "independent_gates",
    "final_conclusion_layers",
    "claim_boundary",
    "bindings",
    "implementation_imported",
}
GIT_EXECUTABLE = shutil.which("git")


class VerificationResourceStop(RuntimeError):
    """A cooperative verification resource boundary was reached."""


def require_isolated_safe_path() -> None:
    if not (_sys.flags.isolated and getattr(_sys.flags, "safe_path", False)):
        raise SystemExit(
            "refusing unsafe launch before imports; invoke with "
            "`python -I verify_independent.py ...`"
        )
    _sys.dont_write_bytecode = True


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def strict_equal(left: Any, right: Any) -> bool:
    try:
        return canonical_json(left) == canonical_json(right)
    except (TypeError, ValueError):
        return False


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def _reject_number(value: str) -> Any:
    raise ValueError(f"inexact or nonfinite JSON number: {value}")


def load_json_bytes_strict(payload: bytes) -> Any:
    return json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=_strict_object,
        parse_float=_reject_number,
        parse_constant=_reject_number,
    )


def load_json_strict(path: Path) -> Any:
    return load_json_bytes_strict(path.read_bytes())


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def exact_fraction(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("inexact scalar")
    if type(value) is int:
        return Fraction(value)
    if isinstance(value, str) and re.fullmatch(r"-?(0|[1-9][0-9]*)/[1-9][0-9]*", value):
        parsed = Fraction(value)
        if fraction_text(parsed) == value:
            return parsed
    raise TypeError("not a canonical exact scalar")


def contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(key) or contains_float(item) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(contains_float(item) for item in value)
    return False


def manifest_checks(manifest: dict[str, Any]) -> dict[str, bool]:
    registry = manifest.get("registry", {})
    budget = manifest.get("budget", {})
    return {
        "canonical_manifest_hash_is_frozen": canonical_sha256(manifest) == MANIFEST_DIGEST,
        "identity_is_frozen": manifest.get("schema") == "alife.experiment.v1"
        and manifest.get("schema_version") == MANIFEST_SCHEMA
        and manifest.get("protocol_id") == PROTOCOL_ID,
        "source_inventory_is_exact": tuple(
            manifest.get("source_freeze", {}).get("files", ())
        )
        == SOURCE_FILES
        and manifest.get("source_freeze", {}).get("artifact_execution_before_commit")
        == "forbidden",
        "registry_is_exact": registry.get("canonical_catalog")
        == ["DDD", "DCC", "DDD"]
        and tuple(registry.get("family_order", ())) == tuple(FAMILIES)
        and registry.get("graph_loop_order")
        == ["family", "temptation", "budget"]
        and registry.get("primary_loop_order")
        == ["family", "temptation", "budget", "schedule"]
        and tuple(registry.get("catalog_costs", ())) == COSTS
        and tuple(registry.get("budgets", ())) == BUDGETS
        and tuple(registry.get("schedules", ())) == SCHEDULES
        and tuple(exact_fraction(value) for value in registry.get("temptations", ()))
        == TEMPTATIONS
        and registry.get("initial_profile") == list(START)
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


def admitted(costs: Sequence[int], budget: int) -> tuple[int, ...]:
    return tuple(index for index, cost in enumerate(costs) if cost <= budget)


def action_pair(catalog: Sequence[Sequence[int]], profile: tuple[int, int]) -> tuple[int, int]:
    return catalog[profile[0]][profile[1]], catalog[profile[1]][profile[0]]


def utility_pair(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    profile: tuple[int, int],
) -> tuple[Fraction, Fraction]:
    row_action, column_action = action_pair(catalog, profile)
    values = FAMILIES[family]
    if (row_action, column_action) == (1, 1):
        return values["R"], values["R"]
    if (row_action, column_action) == (1, 0):
        return values["S"], temptation
    if (row_action, column_action) == (0, 1):
        return temptation, values["S"]
    return values["P"], values["P"]


def independent_decision(
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
    candidates = []
    for program in programs:
        alternative = (program, profile[1]) if player == 0 else (profile[0], program)
        candidates.append((program, utility_pair(catalog, family, temptation, alternative)[player]))
    best_payoff = max(value for _, value in candidates)
    best = tuple(program for program, value in candidates if value == best_payoff)
    incumbent = profile[player]
    incumbent_best = incumbent in best
    if inertia and incumbent_best:
        chosen = incumbent
        reason = "incumbent_best_response_inertia"
    else:
        attached = [costs[program] for program in best]
        target = min(attached) if tie_mode == "min_cost" else max(attached)
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
        "best_payoff": fraction_text(best_payoff),
        "incumbent_is_best_response": incumbent_best,
        "chosen_program": chosen,
        "reason": reason,
        "after_profile": list(after),
        "changed": chosen != incumbent,
    }


def successor(
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
    decision = independent_decision(
        catalog,
        family,
        temptation,
        programs,
        costs,
        state[:2],
        state[2],
        tie_mode=tie_mode,
        inertia=inertia,
    )
    after = decision["after_profile"]
    return (after[0], after[1], 1 - state[2]), decision


def canonical_cycle(
    cycle: Sequence[tuple[int, int, int]],
) -> tuple[tuple[int, int, int], ...]:
    rotations = [tuple(cycle[index:]) + tuple(cycle[:index]) for index in range(len(cycle))]
    return min(rotations)


def terminal_cycle(
    start: tuple[int, int, int],
    links: dict[tuple[int, int, int], tuple[int, int, int]],
) -> tuple[tuple[int, int, int], ...]:
    positions: dict[tuple[int, int, int], int] = {}
    path = []
    state = start
    while state not in positions:
        positions[state] = len(path)
        path.append(state)
        state = links[state]
    return canonical_cycle(path[positions[state] :])


def independent_equilibria(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    programs: Sequence[int],
) -> tuple[tuple[int, int], ...]:
    equilibria = []
    for row in programs:
        for column in programs:
            profile = (row, column)
            value = utility_pair(catalog, family, temptation, profile)
            row_best = max(
                utility_pair(catalog, family, temptation, (candidate, column))[0]
                for candidate in programs
            )
            column_best = max(
                utility_pair(catalog, family, temptation, (row, candidate))[1]
                for candidate in programs
            )
            if value == (row_best, column_best):
                equilibria.append(profile)
    return tuple(equilibria)


def independent_graph(family: str, temptation: Fraction, budget: int) -> dict[str, Any]:
    programs = admitted(COSTS, budget)
    states = tuple(
        (row, column, player)
        for row in programs
        for column in programs
        for player in (0, 1)
    )
    links = {}
    decisions = {}
    for state in states:
        links[state], decisions[state] = successor(
            CANONICAL, family, temptation, programs, COSTS, state
        )
    assignments = {state: terminal_cycle(state, links) for state in states}
    cycles = sorted(set(assignments.values()))
    identifiers = {cycle: f"A{index}" for index, cycle in enumerate(cycles)}
    basin_counts = Counter(assignments.values())
    equilibria = set(independent_equilibria(CANONICAL, family, temptation, programs))
    attractors = []
    for cycle in cycles:
        profiles = {state[:2] for state in cycle}
        fixed = len(cycle) == 2 and len(profiles) == 1
        profile = next(iter(profiles)) if fixed else None
        attractors.append(
            {
                "id": identifiers[cycle],
                "cycle": [list(state) for state in cycle],
                "cycle_length": len(cycle),
                "kind": "fixed_pure_profile" if fixed else "dynamic_cycle",
                "fixed_profile": list(profile) if profile is not None else None,
                "fixed_profile_is_pure_equilibrium": bool(
                    profile is not None and profile in equilibria
                ),
                "basin_size": basin_counts[cycle],
                "basin_fraction": fraction_text(Fraction(basin_counts[cycle], len(states))),
            }
        )
    edges = [
        {
            "from": list(state),
            "to": list(links[state]),
            "decision": decisions[state],
            "attractor_id": identifiers[assignments[state]],
        }
        for state in states
    ]
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


def independent_trace(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    costs: Sequence[int],
    budget: int,
    start: tuple[int, int],
    schedule: str,
    *,
    tie_mode: str = "min_cost",
    inertia: bool = True,
    graph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    programs = admitted(costs, budget)
    state = (start[0], start[1], 0 if schedule == "row_first" else 1)
    seen = {state: 0}
    visited = [list(state)]
    transitions = []
    no_change = 0
    termination = "update_limit"
    cycle_start = None
    for _ in range(2 * len(programs) ** 2 + 1):
        after, decision = successor(
            catalog,
            family,
            temptation,
            programs,
            costs,
            state,
            tie_mode=tie_mode,
            inertia=inertia,
        )
        transitions.append({"from": list(state), "to": list(after), "decision": decision})
        visited.append(list(after))
        no_change = no_change + 1 if not decision["changed"] else 0
        if no_change >= 2:
            termination = "fixed_profile"
            state = after
            break
        if after in seen:
            termination = "augmented_state_cycle"
            cycle_start = seen[after]
            state = after
            break
        seen[after] = len(transitions)
        state = after
    if termination == "update_limit":
        raise AssertionError("independent finite-state bound exceeded")
    terminal_profile = state[:2] if termination == "fixed_profile" else None
    if terminal_profile is not None:
        observed_cycle = canonical_cycle(
            (
                (terminal_profile[0], terminal_profile[1], 0),
                (terminal_profile[0], terminal_profile[1], 1),
            )
        )
    else:
        if cycle_start is None:
            raise AssertionError("cycle termination lacks repeated-state index")
        observed_cycle = canonical_cycle(
            tuple(tuple(item) for item in visited[cycle_start:-1])
        )
    if graph is None:
        graph = independent_catalog_graph(
            catalog,
            family,
            temptation,
            costs,
            budget,
            tie_mode=tie_mode,
            inertia=inertia,
        )
    edge = next(item for item in graph["edges"] if item["from"] == visited[0])
    attractor = next(
        item for item in graph["attractors"] if item["id"] == edge["attractor_id"]
    )
    return {
        "initial_augmented_state": visited[0],
        "visited_augmented_states": visited,
        "transitions": transitions,
        "termination": termination,
        "cycle_start_transition": cycle_start,
        "terminal_profile": (
            list(terminal_profile) if terminal_profile is not None else None
        ),
        "scheduled_updates": len(transitions),
        "changed_moves": sum(item["decision"]["changed"] for item in transitions),
        "attractor_id": edge["attractor_id"],
        "attractor_cycle": attractor["cycle"],
        "observed_attractor_cycle": [list(item) for item in observed_cycle],
        "reported_attractor_matches_observed": attractor["cycle"]
        == [list(item) for item in observed_cycle],
    }


def independent_catalog_graph(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    costs: Sequence[int],
    budget: int,
    *,
    tie_mode: str = "min_cost",
    inertia: bool = True,
) -> dict[str, Any]:
    """Build the graph used by controls without calling the canonical graph helper."""
    programs = admitted(costs, budget)
    states = tuple(
        (row, column, player)
        for row in programs
        for column in programs
        for player in (0, 1)
    )
    links = {}
    decisions = {}
    for state in states:
        links[state], decisions[state] = successor(
            catalog,
            family,
            temptation,
            programs,
            costs,
            state,
            tie_mode=tie_mode,
            inertia=inertia,
        )
    assignments = {state: terminal_cycle(state, links) for state in states}
    cycles = sorted(set(assignments.values()))
    ids = {cycle: f"A{index}" for index, cycle in enumerate(cycles)}
    basin_counts = Counter(assignments.values())
    equilibria = set(independent_equilibria(catalog, family, temptation, programs))
    edges = [
        {
            "from": list(state),
            "to": list(links[state]),
            "decision": decisions[state],
            "attractor_id": ids[assignments[state]],
        }
        for state in states
    ]
    return {
        "family": family,
        "temptation": fraction_text(temptation),
        "budget": budget,
        "programs": list(programs),
        "state_count": len(states),
        "edge_count": len(edges),
        "edges": edges,
        "attractors": [
            {
                "id": ids[cycle],
                "cycle": [list(state) for state in cycle],
                "cycle_length": len(cycle),
                "kind": (
                    "fixed_pure_profile"
                    if len(cycle) == 2 and len({state[:2] for state in cycle}) == 1
                    else "dynamic_cycle"
                ),
                "fixed_profile": (
                    list(cycle[0][:2])
                    if len(cycle) == 2 and len({state[:2] for state in cycle}) == 1
                    else None
                ),
                "fixed_profile_is_pure_equilibrium": (
                    cycle[0][:2] in equilibria
                    if len(cycle) == 2 and len({state[:2] for state in cycle}) == 1
                    else False
                ),
                "basin_size": basin_counts[cycle],
                "basin_fraction": fraction_text(
                    Fraction(basin_counts[cycle], len(states))
                ),
            }
            for cycle in cycles
        ],
        "checks": {
            "complete_functional_graph": len(states)
            == len(edges)
            == 2 * len(programs) ** 2,
            "basins_partition_states": sum(basin_counts.values()) == len(states),
            "fixed_attractors_are_pure_equilibria": all(
                cycle[0][:2] in equilibria
                for cycle in cycles
                if len(cycle) == 2 and len({state[:2] for state in cycle}) == 1
            ),
        },
    }


def expected_endpoint(
    family: str, temptation: Fraction, budget: int, schedule: str
) -> tuple[int, int]:
    if budget == 2 or temptation <= 3:
        return START
    if family == "pd_threshold":
        return (2, 0) if schedule == "row_first" else (0, 2)
    return (2, 1) if schedule == "row_first" else (1, 2)


def independent_row(
    family: str,
    temptation: Fraction,
    budget: int,
    schedule: str,
    graph: dict[str, Any],
) -> dict[str, Any]:
    trace = independent_trace(
        CANONICAL, family, temptation, COSTS, budget, START, schedule, graph=graph
    )
    terminal = tuple(trace["terminal_profile"] or ())
    actions = action_pair(CANONICAL, terminal)
    payoffs = utility_pair(CANONICAL, family, temptation, terminal)
    equilibria = independent_equilibria(CANONICAL, family, temptation, admitted(COSTS, budget))
    return {
        "family": family,
        "temptation": fraction_text(temptation),
        "budget": budget,
        "schedule": schedule,
        "initial_profile": list(START),
        "trace": trace,
        "terminal_profile": list(terminal),
        "terminal_actions": list(actions),
        "terminal_payoffs": [fraction_text(value) for value in payoffs],
        "cooperative_selected": actions == (1, 1),
        "available_pure_equilibria": [list(profile) for profile in equilibria],
        "checks": {
            "expected_endpoint": terminal
            == expected_endpoint(family, temptation, budget, schedule),
            "expected_cooperation": (actions == (1, 1))
            == (budget == 2 or temptation <= 3),
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


def aggregate(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
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
    outcome_atoms = []
    for key, count in sorted(atoms.items()):
        profile, actions, payoffs, cooperative = key
        outcome_atoms.append(
            {
                "terminal_profile": list(profile),
                "terminal_actions": list(actions),
                "terminal_payoffs": list(payoffs),
                "cooperative_selected": cooperative,
                "weight": fraction_text(Fraction(count, 2)),
            }
        )
    return {
        "family": rows[0]["family"],
        "temptation": rows[0]["temptation"],
        "budget": rows[0]["budget"],
        "schedule_weights": {"row_first": "1/2", "column_first": "1/2"},
        "outcome_atoms": outcome_atoms,
        "cooperation_distribution": [
            {
                "cooperative_selected": rows[0]["cooperative_selected"],
                "weight": "1/1",
            }
        ],
        "point_mass_cooperation": rows[0]["cooperative_selected"]
        == rows[1]["cooperative_selected"],
        "distinct_terminal_profiles": len(atoms),
    }


def registry_graph_keys() -> tuple[tuple[str, Fraction, int], ...]:
    return tuple(
        (family, temptation, budget)
        for family in FAMILIES
        for temptation in TEMPTATIONS
        for budget in BUDGETS
    )


def registry_row_keys() -> tuple[tuple[str, Fraction, int, str], ...]:
    return tuple(
        (*key, schedule) for key in registry_graph_keys() for schedule in SCHEDULES
    )


def independent_primary_universe(
    resource_check: Callable[[], None] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    graphs = []
    for key in registry_graph_keys():
        if resource_check is not None:
            resource_check()
        graphs.append(independent_graph(*key))
    graph_map = {key: graph for key, graph in zip(registry_graph_keys(), graphs)}
    rows = []
    for family, temptation, budget, schedule in registry_row_keys():
        if resource_check is not None:
            resource_check()
        rows.append(
            independent_row(
                family,
                temptation,
                budget,
                schedule,
                graph_map[(family, temptation, budget)],
            )
        )
    aggregates = []
    for family, temptation, budget in registry_graph_keys():
        if resource_check is not None:
            resource_check()
        aggregates.append(
            aggregate(
                [
                    row
                    for row in rows
                    if (row["family"], row["temptation"], row["budget"])
                    == (family, fraction_text(temptation), budget)
                ]
            )
        )
    return graphs, rows, aggregates


def relabel(
    catalog: Sequence[Sequence[int]], costs: Sequence[int], permutation: Sequence[int]
) -> tuple[tuple[tuple[int, ...], ...], tuple[int, ...]]:
    transformed = [[0] * 3 for _ in range(3)]
    transformed_costs = [0] * 3
    for old in range(3):
        new = permutation[old]
        transformed_costs[new] = costs[old]
        for old_opponent in range(3):
            transformed[new][permutation[old_opponent]] = catalog[old][old_opponent]
    return tuple(tuple(row) for row in transformed), tuple(transformed_costs)


def state_back(state: Sequence[int], inverse: Sequence[int]) -> list[int]:
    return [inverse[state[0]], inverse[state[1]], state[2]]


def profile_back(profile: Sequence[int], inverse: Sequence[int]) -> list[int]:
    return [inverse[profile[0]], inverse[profile[1]]]


def cycle_back(cycle: Sequence[Sequence[int]], inverse: Sequence[int]) -> list[list[int]]:
    mapped = tuple(tuple(state_back(state, inverse)) for state in cycle)
    return [list(state) for state in canonical_cycle(mapped)]


def decision_back(decision: dict[str, Any], inverse: Sequence[int]) -> dict[str, Any]:
    candidates = sorted(
        [
            {"program": inverse[item["program"]], "payoff": item["payoff"]}
            for item in decision["candidate_payoffs"]
        ],
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
        "after_profile": profile_back(decision["after_profile"], inverse),
        "changed": decision["changed"],
    }


def trace_signature(
    trace: dict[str, Any], inverse: Sequence[int] = (0, 1, 2)
) -> dict[str, Any]:
    terminal = trace["terminal_profile"]
    return {
        "initial_augmented_state": state_back(trace["initial_augmented_state"], inverse),
        "visited_augmented_states": [
            state_back(state, inverse) for state in trace["visited_augmented_states"]
        ],
        "transitions": [
            {
                "from": state_back(item["from"], inverse),
                "to": state_back(item["to"], inverse),
                "decision": decision_back(item["decision"], inverse),
            }
            for item in trace["transitions"]
        ],
        "termination": trace["termination"],
        "cycle_start_transition": trace["cycle_start_transition"],
        "terminal_profile": (
            profile_back(terminal, inverse) if terminal is not None else None
        ),
        "scheduled_updates": trace["scheduled_updates"],
        "changed_moves": trace["changed_moves"],
        "attractor_cycle": cycle_back(trace["attractor_cycle"], inverse),
        "observed_attractor_cycle": cycle_back(
            trace["observed_attractor_cycle"], inverse
        ),
        "reported_attractor_matches_observed": trace[
            "reported_attractor_matches_observed"
        ],
    }


def map_signature_back(trace: dict[str, Any], permutation: Sequence[int]) -> dict[str, Any]:
    inverse = [0] * 3
    for old, new in enumerate(permutation):
        inverse[new] = old
    return trace_signature(trace, inverse)


def graph_signature(
    graph: dict[str, Any], inverse: Sequence[int] = (0, 1, 2)
) -> dict[str, Any]:
    cycles = {
        item["id"]: cycle_back(item["cycle"], inverse)
        for item in graph["attractors"]
    }
    edges = [
        {
            "from": state_back(edge["from"], inverse),
            "to": state_back(edge["to"], inverse),
            "decision": decision_back(edge["decision"], inverse),
            "attractor_cycle": cycles[edge["attractor_id"]],
        }
        for edge in graph["edges"]
    ]
    edges.sort(key=lambda edge: tuple(edge["from"]))
    attractors = []
    for item in graph["attractors"]:
        fixed = item["fixed_profile"]
        attractors.append(
            {
                "cycle": cycles[item["id"]],
                "cycle_length": item["cycle_length"],
                "kind": item["kind"],
                "fixed_profile": profile_back(fixed, inverse) if fixed is not None else None,
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


def distribution_signature(
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
        mapped = tuple(profile_back(terminal, inverse))
        actions = action_pair(catalog, terminal)
        payoffs = tuple(
            fraction_text(value)
            for value in utility_pair(catalog, family, temptation, terminal)
        )
        cooperative = actions == (1, 1)
        outcomes.append(
            {
                "schedule": schedule,
                "terminal_profile": list(mapped),
                "terminal_actions": list(actions),
                "terminal_payoffs": list(payoffs),
                "cooperative_selected": cooperative,
            }
        )
        atoms[(mapped, actions, payoffs, cooperative)] += 1
    atom_rows = []
    for key, count in sorted(atoms.items()):
        terminal, actions, payoffs, cooperative = key
        atom_rows.append(
            {
                "terminal_profile": list(terminal),
                "terminal_actions": list(actions),
                "terminal_payoffs": list(payoffs),
                "cooperative_selected": cooperative,
                "weight": fraction_text(Fraction(count, len(schedule_traces))),
            }
        )
    return {
        "schedule_weights": {schedule: "1/2" for schedule in SCHEDULES},
        "schedule_outcomes": outcomes,
        "outcome_atoms": atom_rows,
    }


def control_rows(
    catalog: Sequence[Sequence[int]], costs: Sequence[int] = COSTS
) -> list[dict[str, Any]]:
    rows = []
    graphs: dict[tuple[str, Fraction, int], dict[str, Any]] = {}
    for family, temptation, budget, schedule in registry_row_keys():
        key = (family, temptation, budget)
        if key not in graphs:
            graphs[key] = independent_catalog_graph(
                catalog, family, temptation, costs, budget
            )
        trace = independent_trace(
            catalog,
            family,
            temptation,
            costs,
            budget,
            START,
            schedule,
            graph=graphs[key],
        )
        terminal = tuple(trace["terminal_profile"] or ())
        rows.append(
            {
                "family": family,
                "temptation": temptation,
                "budget": budget,
                "schedule": schedule,
                "graph": graphs[key],
                "trace": trace,
                "terminal": terminal,
                "cooperative": action_pair(catalog, terminal) == (1, 1),
            }
        )
    return rows


def simultaneous(family: str) -> dict[str, Any]:
    programs = admitted(COSTS, 3)
    profile = START
    seen = {profile: 0}
    visited = [list(profile)]
    for _ in range(len(programs) ** 2 + 1):
        row = independent_decision(
            CANONICAL, family, Fraction(301, 100), programs, COSTS, profile, 0
        )["chosen_program"]
        column = independent_decision(
            CANONICAL, family, Fraction(301, 100), programs, COSTS, profile, 1
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
    raise AssertionError("independent simultaneous bound exceeded")


def independent_controls(
    primary_rows: Sequence[dict[str, Any]],
    resource_check: Callable[[], None] | None = None,
) -> dict[str, Any]:
    canonical_rows = control_rows(CANONICAL)
    repaired_rows = control_rows(REPAIRED)
    blind_rows = control_rows(SOURCE_BLIND)
    semantic_rows = {
        "canonical": canonical_rows,
        "repaired": repaired_rows,
        "source_blind": blind_rows,
    }
    padding_trace_count = 0
    padding_graph_count = 0
    padding_distribution_count = 0
    padding_traces_exact = True
    padding_graphs_exact = True
    padding_distributions_exact = True
    relabel_trace_count = 0
    relabel_graph_count = 0
    relabel_distribution_count = 0
    relabel_traces_exact = True
    relabel_graphs_exact = True
    relabel_distributions_exact = True
    for catalog_id, rows in semantic_rows.items():
        catalog = CATALOGS[catalog_id]
        padded_costs = tuple(cost + 2 for cost in COSTS)
        for family, temptation, budget in registry_graph_keys():
            if resource_check is not None:
                resource_check()
            matched = [
                row
                for row in rows
                if (row["family"], row["temptation"], row["budget"])
                == (family, temptation, budget)
            ]
            base_traces = [(row["schedule"], row["trace"]) for row in matched]
            base_graph = matched[0]["graph"]
            padded_graph = independent_catalog_graph(
                catalog, family, temptation, padded_costs, budget + 2
            )
            padding_graph_count += 1
            padding_graphs_exact = padding_graphs_exact and (
                graph_signature(base_graph) == graph_signature(padded_graph)
            )
            padded_traces = []
            for row in matched:
                padded = independent_trace(
                    catalog,
                    family,
                    temptation,
                    padded_costs,
                    budget + 2,
                    START,
                    row["schedule"],
                    graph=padded_graph,
                )
                padded_traces.append((row["schedule"], padded))
                padding_trace_count += 1
                padding_traces_exact = padding_traces_exact and (
                    trace_signature(row["trace"]) == trace_signature(padded)
                )
            padding_distribution_count += 1
            padding_distributions_exact = padding_distributions_exact and (
                distribution_signature(catalog, family, temptation, base_traces)
                == distribution_signature(catalog, family, temptation, padded_traces)
            )
            for permutation in itertools.permutations(range(3)):
                if resource_check is not None:
                    resource_check()
                transformed, transformed_costs = relabel(catalog, COSTS, permutation)
                inverse = [0] * 3
                for old, new in enumerate(permutation):
                    inverse[new] = old
                transformed_graph = independent_catalog_graph(
                    transformed,
                    family,
                    temptation,
                    transformed_costs,
                    budget,
                )
                relabel_graph_count += 1
                relabel_graphs_exact = relabel_graphs_exact and (
                    graph_signature(base_graph)
                    == graph_signature(transformed_graph, inverse)
                )
                transformed_traces = []
                for row in matched:
                    transformed_trace = independent_trace(
                        transformed,
                        family,
                        temptation,
                        transformed_costs,
                        budget,
                        (permutation[1], permutation[1]),
                        row["schedule"],
                        graph=transformed_graph,
                    )
                    transformed_traces.append((row["schedule"], transformed_trace))
                    relabel_trace_count += 1
                    relabel_traces_exact = relabel_traces_exact and (
                        trace_signature(row["trace"])
                        == map_signature_back(transformed_trace, permutation)
                    )
                relabel_distribution_count += 1
                relabel_distributions_exact = relabel_distributions_exact and (
                    distribution_signature(catalog, family, temptation, base_traces)
                    == distribution_signature(
                        transformed,
                        family,
                        temptation,
                        transformed_traces,
                        inverse,
                    )
                )
    no_budget_effect = True
    for family in FAMILIES:
        for temptation in TEMPTATIONS:
            for schedule in SCHEDULES:
                pair = [
                    row
                    for row in blind_rows
                    if (row["family"], row["temptation"], row["schedule"])
                    == (family, temptation, schedule)
                ]
                no_budget_effect = no_budget_effect and len(pair) == 2
                no_budget_effect = no_budget_effect and pair[0]["terminal"] == pair[1]["terminal"]
                no_budget_effect = no_budget_effect and pair[0]["cooperative"] == pair[1]["cooperative"]
    inertia_main = independent_trace(
        CANONICAL, "pd_threshold", Fraction(301, 100), COSTS, 3, (2, 0), "row_first"
    )
    inertia_off = independent_trace(
        CANONICAL,
        "pd_threshold",
        Fraction(301, 100),
        COSTS,
        3,
        (2, 0),
        "row_first",
        inertia=False,
    )
    max_rows = [
        {
            "family": family,
            "schedule": schedule,
            "trace": independent_trace(
                CANONICAL,
                family,
                Fraction(301, 100),
                COSTS,
                3,
                START,
                schedule,
                tie_mode="max_cost",
            ),
        }
        for family in FAMILIES
        for schedule in SCHEDULES
    ]
    simultaneous_rows = [
        {"family": family, "trace": simultaneous(family)} for family in FAMILIES
    ]
    distinct_keys = [
        (family, temptation, budget)
        for family, temptation, budget in registry_graph_keys()
        if aggregate(
            [
                row
                for row in primary_rows
                if (row["family"], row["temptation"], row["budget"])
                == (family, fraction_text(temptation), budget)
            ]
        )["distinct_terminal_profiles"]
        == 2
    ]
    expected_distinct = [
        (family, Fraction(301, 100), 3) for family in FAMILIES
    ]
    cycle_trace = independent_trace(
        CYCLE_FIXTURE,
        "pd_threshold",
        Fraction(301, 100),
        COSTS,
        3,
        (0, 0),
        "row_first",
    )
    cycle_fixture = {
        "catalog": ["CCD", "DCC", "CDC"],
        "termination": cycle_trace["termination"],
        "cycle_start_transition": cycle_trace["cycle_start_transition"],
        "observed_attractor_cycle": cycle_trace["observed_attractor_cycle"],
        "reported_attractor_cycle": cycle_trace["attractor_cycle"],
        "pass": cycle_trace["termination"] == "augmented_state_cycle"
        and len(cycle_trace["observed_attractor_cycle"]) == 6
        and cycle_trace["reported_attractor_matches_observed"],
    }
    repaired_pass = all(row["cooperative"] for row in repaired_rows)
    blind_early = all(
        not row["cooperative"] for row in blind_rows if row["temptation"] > 3
    )
    inertia_distinguishes = (
        inertia_main["terminal_profile"] != inertia_off["terminal_profile"]
    )
    max_cost_pd_changes = all(
        row["trace"]["terminal_profile"] == [2, 2]
        for row in max_rows
        if row["family"] == "pd_threshold"
    )
    simultaneous_pd_p2_p2 = next(
        row for row in simultaneous_rows if row["family"] == "pd_threshold"
    )["trace"] == {
        "termination": "fixed_profile",
        "visited_profiles": [[1, 1], [2, 2], [2, 2]],
    }
    simultaneous_chicken_cycle = (
        next(
            row
            for row in simultaneous_rows
            if row["family"] == "chicken_threshold"
        )["trace"]["termination"]
        == "profile_cycle"
    )
    selected_pure = all(
        row["checks"]["selected_profile_is_pure_equilibrium"]
        for row in primary_rows
    )
    distinct_exact = distinct_keys == expected_distinct
    return {
        "repaired_duplicate_extensional": {
            "trajectory_count": len(repaired_rows),
            "cooperative_count": sum(row["cooperative"] for row in repaired_rows),
            "all_initialized_cooperation_retained": repaired_pass,
            "pass": repaired_pass,
        },
        "source_blind_early_vulnerability": {
            "trajectory_count": len(blind_rows),
            "cooperative_count": sum(row["cooperative"] for row in blind_rows),
            "no_budget_induced_change": no_budget_effect,
            "above_threshold_is_already_vulnerable_at_budget_two": all(
                not row["cooperative"] for row in blind_rows if row["temptation"] > 3
            ),
            "pass": no_budget_effect and blind_early,
        },
        "additive_cost_padding": {
            "trace_comparison_count": padding_trace_count,
            "graph_relation_comparison_count": padding_graph_count,
            "distribution_comparison_count": padding_distribution_count,
            "all_traces_exact": padding_traces_exact,
            "all_graph_relations_exact": padding_graphs_exact,
            "all_selected_distributions_exact": padding_distributions_exact,
            "pass": padding_traces_exact
            and padding_graphs_exact
            and padding_distributions_exact,
        },
        "six_semantic_relabelings": {
            "permutation_count": math.factorial(3),
            "trace_comparison_count": relabel_trace_count,
            "graph_relation_comparison_count": relabel_graph_count,
            "distribution_comparison_count": relabel_distribution_count,
            "all_mapped_traces_exact": relabel_traces_exact,
            "all_mapped_graph_relations_exact": relabel_graphs_exact,
            "all_mapped_selected_distributions_exact": relabel_distributions_exact,
            "pass": relabel_traces_exact
            and relabel_graphs_exact
            and relabel_distributions_exact
            and relabel_trace_count == 432
            and relabel_graph_count == 216
            and relabel_distribution_count == 216,
        },
        "inertia_and_cycle_fixtures": {
            "main_terminal_profile": inertia_main["terminal_profile"],
            "noninertial_terminal_profile": inertia_off["terminal_profile"],
            "distinguishes_inertia_rule": inertia_distinguishes,
            "cycle_fixture": cycle_fixture,
            "pass": inertia_distinguishes and cycle_fixture["pass"],
        },
        "max_cost_and_simultaneous_scope_breakers": {
            "max_cost_rows": max_rows,
            "simultaneous_rows": simultaneous_rows,
            "max_cost_pd_profile_changes": max_cost_pd_changes,
            "simultaneous_pd_selects_p2_p2": simultaneous_pd_p2_p2,
            "simultaneous_chicken_cycles": simultaneous_chicken_cycle,
            "selection_validity": {
                "all_initialized_terminal_profiles_are_pure_equilibria": selected_pure,
                "distinct_schedule_equilibrium_conditions": len(distinct_keys),
                "distinct_condition_keys": [
                    [family, fraction_text(temptation), budget]
                    for family, temptation, budget in distinct_keys
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


def independent_metrics(
    rows: Sequence[dict[str, Any]], controls: dict[str, Any]
) -> dict[str, Any]:
    monotone = all(
        [
            row["cooperative_selected"]
            for row in rows
            if row["family"] == family
            and row["schedule"] == schedule
            and row["budget"] == 3
        ]
        == [True, True, False]
        for family in FAMILIES
        for schedule in SCHEDULES
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
        "P3_registered_monotonicity": {"family": "monotonicity", "pass": monotone},
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


def _is_reparse_point(path: Path) -> bool:
    metadata = path.lstat()
    attributes = getattr(metadata, "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return path.is_symlink() or bool(attributes & flag)


def live_source_inventory() -> dict[str, Any]:
    entries = {entry.name: entry for entry in HERE.iterdir()}
    expected = set(SOURCE_FILES)
    invalid = [
        name
        for name in sorted(expected & set(entries))
        if _is_reparse_point(entries[name]) or not entries[name].is_file()
    ]
    return {
        "pass": not (_is_reparse_point(HERE) or set(entries) != expected or invalid),
        "missing": sorted(expected - set(entries)),
        "unexpected": sorted(set(entries) - expected),
        "invalid": invalid,
    }


def validate_live_source_inventory() -> dict[str, Any]:
    checks = live_source_inventory()
    if not checks["pass"]:
        raise ValueError(f"live source inventory failed: {checks}")
    return checks


def git_environment() -> dict[str, str]:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    return environment


def git(args: Sequence[str], root: Path, *, input_bytes: bytes | None = None) -> bytes:
    if GIT_EXECUTABLE is None:
        raise ValueError("trusted Git executable is unavailable")
    return subprocess.run(
        [GIT_EXECUTABLE, *args],
        cwd=root,
        env=git_environment(),
        input=input_bytes,
        check=True,
        capture_output=True,
    ).stdout


def trusted_repo() -> Path:
    root = Path(
        os.path.abspath(git(["rev-parse", "--show-toplevel"], HERE).decode().strip())
    )
    git_dir = Path(
        os.path.abspath(
            git(["rev-parse", "--absolute-git-dir"], root).decode().strip()
        )
    )
    if (git_dir / "info" / "grafts").exists() and (git_dir / "info" / "grafts").stat().st_size:
        raise ValueError("legacy Git grafts are forbidden")
    if git(["for-each-ref", "--format=%(refname)", "refs/replace"], root).strip():
        raise ValueError("Git replacement refs are forbidden")
    if git(["rev-parse", "--is-shallow-repository"], root).strip() != b"false":
        raise ValueError("shallow repository is forbidden")
    cursor = HERE
    while True:
        if _is_reparse_point(cursor):
            raise ValueError(f"source ancestry contains reparse point: {cursor}")
        if cursor == root:
            return root
        if cursor.parent == cursor or root not in cursor.parents:
            raise ValueError("source directory is outside repository root")
        cursor = cursor.parent


def require_commit(root: Path, commit: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("commit is not full lowercase hexadecimal")
    if git(["cat-file", "-t", commit], root).strip() != b"commit":
        raise ValueError("Git object is not a commit")
    ancestry = subprocess.run(
        [GIT_EXECUTABLE, "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=root,
        env=git_environment(),
        capture_output=True,
    )
    if ancestry.returncode:
        raise ValueError("commit is not an ancestor of HEAD")


def replay_source_binding(reported: dict[str, Any]) -> dict[str, Any]:
    root = trusted_repo()
    commit = reported["source_commit"]
    require_commit(root, commit)
    relative = HERE.relative_to(root)
    directory = relative.as_posix()
    listed = git(["ls-tree", "-r", "--name-only", commit, "--", directory], root)
    expected_paths = {(relative / filename).as_posix() for filename in SOURCE_FILES}
    if set(listed.decode().splitlines()) != expected_paths:
        raise ValueError("source commit does not contain exact source inventory")
    files = {}
    for filename in SOURCE_FILES:
        path = (relative / filename).as_posix()
        tree_line = git(["ls-tree", commit, "--", path], root).decode().strip()
        metadata, listed_path = tree_line.split("\t", 1)
        mode, kind, oid = metadata.split()
        committed = git(["show", f"{commit}:{path}"], root)
        live = (HERE / filename).read_bytes()
        live_oid = git(["hash-object", "--stdin"], root, input_bytes=live).decode().strip()
        if listed_path != path or mode != "100644" or kind != "blob":
            raise ValueError(f"source is not an ordinary blob: {filename}")
        if live != committed or oid != live_oid:
            raise ValueError(f"live source differs from source commit: {filename}")
        files[filename] = {"git_blob_oid": live_oid, "sha256": sha256_bytes(live)}
    return {
        "repo_relative_directory": directory,
        "source_commit": commit,
        "source_commit_is_ancestor_of_head": True,
        "source_commit_type": "commit",
        "source_files": files,
    }


def replay_predecessor(manifest: dict[str, Any]) -> dict[str, Any]:
    root = trusted_repo()
    binding = manifest["predecessor_binding"]
    source_checkpoint = binding["source_checkpoint"]
    evidence_commit = binding["evidence_commit"]
    require_commit(root, source_checkpoint)
    require_commit(root, evidence_commit)
    files = []
    for item in binding["files"]:
        payload = git(["show", f"{evidence_commit}:{item['path']}"], root)
        digest = sha256_bytes(payload)
        if digest != item["sha256"]:
            raise ValueError(f"predecessor hash mismatch: {item['path']}")
        files.append(
            {
                "commit": evidence_commit,
                "path": item["path"],
                "role": item["role"],
                "sha256": digest,
            }
        )
    return {
        "source_checkpoint": source_checkpoint,
        "evidence_commit": evidence_commit,
        "files": files,
        "all_hashes_match": True,
    }


def mismatch(label: str, reported: Any, expected: Any) -> list[str]:
    return [] if strict_equal(reported, expected) else [label]


def resource_checks(result: dict[str, Any], raw_bytes: bytes) -> dict[str, bool]:
    observations = result.get("resource_observations", {})
    return {
        "field_universe": set(observations)
        == {
            "canonical_result_bytes",
            "completed_graph_cells",
            "completed_primary_trajectories",
            "elapsed_wall_ns",
            "wall_limit_ns",
            "traced_python_peak_bytes",
            "traced_python_limit_bytes",
            "memory_measurement",
            "process_rss_and_native_memory_measured",
        },
        "byte_count": observations.get("canonical_result_bytes") == len(raw_bytes)
        and len(raw_bytes) <= 1048576,
        "completed_counts": observations.get("completed_graph_cells") == 12
        and observations.get("completed_primary_trajectories") == 24,
        "wall": observations.get("wall_limit_ns") == 15_000_000_000
        and type(observations.get("elapsed_wall_ns")) is int
        and 0 <= observations["elapsed_wall_ns"] <= observations["wall_limit_ns"],
        "memory": observations.get("traced_python_limit_bytes") == 64 * 1024 * 1024
        and type(observations.get("traced_python_peak_bytes")) is int
        and 0
        <= observations["traced_python_peak_bytes"]
        <= observations["traced_python_limit_bytes"]
        and observations.get("memory_measurement")
        == "tracemalloc_peak_python_allocation_only"
        and observations.get("process_rss_and_native_memory_measured") is False,
    }


def verification_resource_check(start_ns: int) -> None:
    if time.monotonic_ns() - start_ns > 15_000_000_000:
        raise VerificationResourceStop("wall_limit_before_next_stage")
    if tracemalloc.get_traced_memory()[1] > 64 * 1024 * 1024:
        raise VerificationResourceStop("traced_python_memory_limit_before_next_stage")


def verify_loaded(
    manifest: dict[str, Any],
    result: dict[str, Any],
    *,
    manifest_bytes: bytes,
    result_bytes: bytes,
) -> dict[str, Any]:
    start_ns = time.monotonic_ns()
    owned_trace = not tracemalloc.is_tracing()
    if owned_trace:
        tracemalloc.start()
    tracemalloc.reset_peak()
    binding = manifest_checks(manifest)
    source_error = ""
    replayed_source: dict[str, Any] = {}
    try:
        replayed_source = replay_source_binding(result.get("source_binding", {}))
    except (KeyError, OSError, subprocess.SubprocessError, TypeError, ValueError) as error:
        source_error = f"{type(error).__name__}: {error}"
    predecessor_error = ""
    replayed_predecessor: dict[str, Any] = {}
    try:
        replayed_predecessor = replay_predecessor(manifest)
    except (KeyError, OSError, subprocess.SubprocessError, TypeError, ValueError) as error:
        predecessor_error = f"{type(error).__name__}: {error}"

    expected_graphs: list[dict[str, Any]] = []
    expected_rows: list[dict[str, Any]] = []
    expected_aggregates: list[dict[str, Any]] = []
    expected_controls: dict[str, Any] = {}
    expected_metrics: dict[str, Any] = {}
    verification_stop_reason = "registered_verification_complete"

    def check() -> None:
        verification_resource_check(start_ns)

    try:
        expected_graphs, expected_rows, expected_aggregates = (
            independent_primary_universe(check)
        )
        check()
        expected_controls = independent_controls(expected_rows, check)
        check()
        expected_metrics = independent_metrics(expected_rows, expected_controls)
        check()
    except VerificationResourceStop as error:
        verification_stop_reason = str(error)
    graph_mismatches = mismatch("graph_cells", result.get("graph_cells"), expected_graphs)
    row_mismatches = mismatch("primary_rows", result.get("primary_rows"), expected_rows)
    aggregate_mismatches = mismatch(
        "fair_schedule_aggregates",
        result.get("fair_schedule_aggregates"),
        expected_aggregates,
    )
    control_mismatches = mismatch("controls", result.get("controls"), expected_controls)
    metric_mismatches = mismatch(
        "metric_robustness", result.get("metric_robustness"), expected_metrics
    )
    resources = resource_checks(result, result_bytes)
    semantic = {
        "result_fields_are_exact": set(result) == RESULT_FIELDS,
        "result_identity_is_exact": result.get("schema_version")
        == "asmp12_inertial_selector_result_v0_4"
        and result.get("protocol_id") == PROTOCOL_ID
        and result.get("manifest_sha256") == MANIFEST_DIGEST
        and result.get("status") == "complete"
        and result.get("stop_reason") == "registered_contract_complete",
        "raw_result_is_canonical_json": result_bytes
        == canonical_json(result).encode("utf-8"),
        "source_binding_matches_replay": not source_error
        and strict_equal(result.get("source_binding"), replayed_source),
        "predecessor_binding_matches_replay": not predecessor_error
        and strict_equal(result.get("predecessor_binding"), replayed_predecessor),
        "primary_gates_are_exact_and_true": set(result.get("gates", {}))
        == set(PRIMARY_GATES)
        and all(result.get("gates", {}).get(gate) is True for gate in PRIMARY_GATES),
        "preverification_layers_are_exact": strict_equal(
            result.get("conclusion_layers"), PREVERIFICATION_LAYERS
        ),
        "claim_boundary_is_exact": strict_equal(
            result.get("claim_boundary"), manifest.get("claim_boundary")
        ),
        "exact_json_firewall": not contains_float(result),
    }
    elapsed_ns = time.monotonic_ns() - start_ns
    peak_bytes = tracemalloc.get_traced_memory()[1]
    if owned_trace:
        tracemalloc.stop()
    verification_resources = {
        "completed_graph_cells": len(expected_graphs),
        "completed_primary_trajectories": len(expected_rows),
        "elapsed_wall_ns": elapsed_ns,
        "wall_limit_ns": 15_000_000_000,
        "traced_python_peak_bytes": peak_bytes,
        "traced_python_limit_bytes": 64 * 1024 * 1024,
        "memory_measurement": "tracemalloc_peak_python_allocation_only",
        "process_rss_and_native_memory_measured": False,
        "stop_reason": verification_stop_reason,
    }
    verifier_resources_valid = (
        verification_stop_reason == "registered_verification_complete"
        and elapsed_ns <= 15_000_000_000
        and peak_bytes <= 64 * 1024 * 1024
    )
    independent_gates = {
        "V0_frozen_manifest_binding": all(binding.values()),
        "V1_exact_live_and_source_commit_binding": semantic[
            "source_binding_matches_replay"
        ],
        "V2_exact_predecessor_binding": semantic[
            "predecessor_binding_matches_replay"
        ],
        "V3_result_identity_and_canonical_json": all(
            semantic[key]
            for key in (
                "result_fields_are_exact",
                "result_identity_is_exact",
                "raw_result_is_canonical_json",
                "claim_boundary_is_exact",
                "exact_json_firewall",
            )
        ),
        "V4_complete_independent_augmented_graphs": not graph_mismatches,
        "V5_complete_independent_initialized_traces": not row_mismatches,
        "V6_exact_fair_schedule_distributions": not aggregate_mismatches,
        "V7_independent_controls_and_scope_breakers": not control_mismatches
        and tuple(expected_controls) == CONTROL_IDS
        and all(record["pass"] is True for record in expected_controls.values()),
        "V8_five_metric_probe_families": not metric_mismatches
        and tuple(expected_metrics) == PROBE_IDS
        and all(item["pass"] for item in expected_metrics.values()),
        "V9_primary_gates_and_preverification_layers": semantic[
            "primary_gates_are_exact_and_true"
        ]
        and semantic["preverification_layers_are_exact"],
        "V10_resource_observations_within_contract": all(resources.values())
        and verifier_resources_valid,
    }
    if tuple(independent_gates) != VERIFICATION_GATES:
        raise AssertionError("independent gate universe changed")
    passed = all(independent_gates.values())
    verification = {
        "schema_version": "asmp12_inertial_selector_verification_v0_4",
        "pass": passed,
        "protocol_id": PROTOCOL_ID,
        "manifest_binding": binding,
        "source_binding_error": source_error,
        "source_binding_replay": replayed_source,
        "predecessor_binding_error": predecessor_error,
        "predecessor_binding_replay": replayed_predecessor,
        "result_semantic_checks": semantic,
        "graph_mismatches": graph_mismatches,
        "primary_row_mismatches": row_mismatches,
        "aggregate_mismatches": aggregate_mismatches,
        "control_mismatches": control_mismatches,
        "metric_mismatches": metric_mismatches,
        "verification_resource_observations": verification_resources,
        "independent_gates": independent_gates,
        "final_conclusion_layers": FINAL_LAYERS
        if passed
        else {
            "metric_robustness": "not_established",
            "task_result": "not_established",
            "measurement_reliability": "failed",
            "claim_support": "none",
            "operational_decision": "no_deployment_authorization_repair",
        },
        "claim_boundary": list(manifest.get("claim_boundary", [])),
        "bindings": {
            "manifest_v0_4.json": {
                "raw_sha256": sha256_bytes(manifest_bytes),
                "canonical_sha256": canonical_sha256(manifest),
            },
            "result_v0_4.json": {
                "raw_sha256": sha256_bytes(result_bytes),
                "canonical_sha256": canonical_sha256(result),
            },
        },
        "implementation_imported": False,
    }
    if set(verification) != VERIFICATION_FIELDS or contains_float(verification):
        raise AssertionError("verification universe or exact-number firewall changed")
    return verification


def verify(manifest_path: Path, result_path: Path) -> dict[str, Any]:
    manifest_bytes = manifest_path.read_bytes()
    result_bytes = result_path.read_bytes()
    manifest = load_json_bytes_strict(manifest_bytes)
    result = load_json_bytes_strict(result_bytes)
    if not isinstance(manifest, dict) or not isinstance(result, dict):
        raise ValueError("manifest and result roots must be objects")
    return verify_loaded(
        manifest,
        result,
        manifest_bytes=manifest_bytes,
        result_bytes=result_bytes,
    )


def _absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def validate_paths(manifest: Path, result: Path, output: Path) -> Path:
    if _absolute(manifest) != _absolute(HERE / "manifest_v0_4.json"):
        raise SystemExit("refusing a manifest outside the frozen source directory")
    artifact_directory = _absolute(ARTIFACT_DIRECTORY)
    if _absolute(result) != artifact_directory / "result_v0_4.json":
        raise SystemExit("refusing a result outside the frozen result artifact path")
    try:
        if _is_reparse_point(_absolute(result)) or not _absolute(result).is_file():
            raise SystemExit("refusing non-regular or reparse-point result input")
    except FileNotFoundError as error:
        raise SystemExit(f"result input is absent: {result}") from error
    destination = _absolute(output)
    if destination != artifact_directory / "verification_v0_4.json":
        raise SystemExit("refusing output outside the frozen verification artifact path")
    try:
        destination.lstat()
    except FileNotFoundError:
        return destination
    raise SystemExit(f"refusing occupied write-once output path: {destination}")


def prepare_destination(path: Path) -> Path:
    destination = _absolute(path)
    chain = [destination]
    while chain[-1].parent != chain[-1]:
        chain.append(chain[-1].parent)
    chain.reverse()
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
        return destination
    raise FileExistsError(f"artifact destination exists: {destination}")


def write_once_json(path: Path, value: Any) -> None:
    payload = canonical_json(value).encode("utf-8")
    if len(payload) > 1048576:
        raise ValueError("verification exceeds frozen artifact byte ceiling")
    with prepare_destination(path).open("xb") as stream:
        stream.write(payload)


def main() -> None:
    require_isolated_safe_path()
    validate_live_source_inventory()
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=HERE / "manifest_v0_4.json")
    parser.add_argument(
        "--result", type=Path, default=ARTIFACT_DIRECTORY / "result_v0_4.json"
    )
    parser.add_argument(
        "--output", type=Path, default=ARTIFACT_DIRECTORY / "verification_v0_4.json"
    )
    args = parser.parse_args()
    output = validate_paths(args.manifest, args.result, args.output)
    verification = verify(args.manifest, args.result)
    write_once_json(output, verification)
    if not verification["pass"]:
        failed = [
            gate
            for gate, passed in verification["independent_gates"].items()
            if not passed
        ]
        raise SystemExit(
            "independent verification failed; downgraded write-once artifact retained: "
            f"{failed}"
        )
    print(output)


if __name__ == "__main__":
    main()
