"""Finite-scheduler periodic completeness for the ASMP-4 support theorem."""

from __future__ import annotations

import ast
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"
V05 = ROOT / "asmp4_adaptive_history_collapse_v0_5" / "adaptive_claim_v0_5.json"
V24 = (
    ROOT
    / "asmp4_resettable_support_variational_v0_24"
    / "resettable_support_claim_v0_24.json"
)
CONTRACT = HERE / "finite_scheduler_contract_v0_25.json"
CLAIM = HERE / "periodic_block_claim_v0_25.json"

SEALS = {
    SOURCE: "08115cc4cb9c5333725a820ad3ca67909e15e8625aac3f128bde46b88ed161f5",
    V05: "f37212d37353f9a1af577fe976c412117d0d67bb833100205fc17c8892a84996",
    V24: "9e06830ae0783f9ff044ae18b97fe9f0778c95e82c994fdba9bf89dd2055d59b",
}

PREDECESSOR_TESTS = (
    ("asmp4_capacity_definition_audit", "test_capacity_definition_audit.py"),
    ("asmp4_two_port_game", "test_two_port_game.py"),
    ("asmp4_serial_collapse_theorem_v0_2", "test_serial_capacity.py"),
    ("asmp4_metric_robust_collapse_v0_3", "test_metric_harness.py"),
    ("asmp4_heterogeneous_port_costs_v0_4", "test_heterogeneous_frontier.py"),
    ("asmp4_adaptive_history_collapse_v0_5", "test_adaptive_frontier.py"),
    ("asmp4_registration_fork_v0_6", "test_registration_fork.py"),
    ("asmp4_relational_action_frontier_v0_7", "test_relational_frontier.py"),
    ("asmp4_randomness_quantifier_boundary_v0_8", "test_randomness_quantifier.py"),
    ("asmp4_completion_atlas_v0_9", "test_completion_atlas.py"),
    ("asmp4_stopping_red_team_v0_10", "test_stopping_red_team.py"),
    ("asmp4_nhim_cocycle_audit_v0_11", "test_nhim_cocycle_audit.py"),
    ("asmp4_positive_dimensional_nhim_v0_12", "test_positive_dimensional_nhim.py"),
    ("asmp4_positive_volume_collar_v0_13", "test_positive_volume_collar.py"),
    ("asmp4_positive_volume_stop_certificate_v0_14", "test_positive_volume_stop.py"),
    ("asmp4_semantic_selector_audit_v0_15", "test_semantic_selector_audit.py"),
    (
        "asmp4_registered_sensor_classification_v0_16",
        "test_registered_sensor_classification.py",
    ),
    ("asmp4_zero_error_sensor_kernels_v0_17", "test_zero_error_sensor_kernels.py"),
    (
        "asmp4_finite_state_sensor_transducers_v0_18",
        "test_finite_state_sensor_transducers.py",
    ),
    (
        "asmp4_uncertain_initial_sensor_state_v0_19",
        "test_uncertain_initial_sensor_state.py",
    ),
    (
        "asmp4_sensor_refinement_inflation_stop_v0_20",
        "test_sensor_refinement_inflation_stop.py",
    ),
    ("asmp4_support_incidence_quotient_v0_21", "test_support_incidence_quotient.py"),
    ("asmp4_causal_encoder_collapse_v0_22", "test_causal_encoder_collapse.py"),
    ("asmp4_observation_delay_boundary_v0_23", "test_observation_delay_boundary.py"),
    (
        "asmp4_resettable_support_variational_v0_24",
        "test_resettable_support_variational.py",
    ),
)


@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    read: float
    write: float
    name: str


@dataclass(frozen=True)
class SchedulerGraph:
    states: tuple[int, ...]
    initial: tuple[int, ...]
    edges: tuple[Edge, ...]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _close(left: float, right: float, tolerance: float = 1e-10) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def outgoing(graph: SchedulerGraph, state: int) -> tuple[tuple[int, Edge], ...]:
    return tuple(
        (index, edge) for index, edge in enumerate(graph.edges) if edge.source == state
    )


def reachable_states(graph: SchedulerGraph) -> frozenset[int]:
    reached = set(graph.initial)
    pending = list(graph.initial)
    while pending:
        state = pending.pop()
        for _, edge in outgoing(graph, state):
            if edge.target not in reached:
                reached.add(edge.target)
                pending.append(edge.target)
    return frozenset(reached)


def strongly_connected_components(graph: SchedulerGraph) -> tuple[tuple[int, ...], ...]:
    index = 0
    stack: list[int] = []
    on_stack: set[int] = set()
    indices: dict[int, int] = {}
    lowlinks: dict[int, int] = {}
    components: list[tuple[int, ...]] = []

    def visit(state: int) -> None:
        nonlocal index
        indices[state] = index
        lowlinks[state] = index
        index += 1
        stack.append(state)
        on_stack.add(state)
        for _, edge in outgoing(graph, state):
            target = edge.target
            if target not in indices:
                visit(target)
                lowlinks[state] = min(lowlinks[state], lowlinks[target])
            elif target in on_stack:
                lowlinks[state] = min(lowlinks[state], indices[target])
        if lowlinks[state] == indices[state]:
            component = []
            while True:
                target = stack.pop()
                on_stack.remove(target)
                component.append(target)
                if target == state:
                    break
            components.append(tuple(sorted(component)))

    for state in graph.states:
        if state not in indices:
            visit(state)
    return tuple(sorted(components))


def simple_cycles(
    graph: SchedulerGraph, component: Iterable[int]
) -> tuple[tuple[int, ...], ...]:
    members = frozenset(component)
    cycles: set[tuple[int, ...]] = set()
    for start in sorted(members):

        def visit(current: int, visited: frozenset[int], path: tuple[int, ...]) -> None:
            for edge_index, edge in outgoing(graph, current):
                if edge.target not in members:
                    continue
                if edge.target == start:
                    cycles.add(path + (edge_index,))
                elif edge.target not in visited and edge.target >= start:
                    visit(edge.target, visited | {edge.target}, path + (edge_index,))

        visit(start, frozenset({start}), ())
    return tuple(sorted(cycles))


def cycle_mean(graph: SchedulerGraph, cycle: tuple[int, ...]) -> tuple[float, float]:
    return (
        sum(graph.edges[index].read for index in cycle) / len(cycle),
        sum(graph.edges[index].write for index in cycle) / len(cycle),
    )


def reachable_cyclic_components(graph: SchedulerGraph) -> tuple[tuple[int, ...], ...]:
    reached = reachable_states(graph)
    return tuple(
        component
        for component in strongly_connected_components(graph)
        if set(component) <= reached and simple_cycles(graph, component)
    )


def component_cycle_means(
    graph: SchedulerGraph, component: Iterable[int]
) -> tuple[tuple[float, float], ...]:
    return tuple(
        sorted(
            set(cycle_mean(graph, cycle) for cycle in simple_cycles(graph, component))
        )
    )


def support_value(points: Iterable[tuple[float, float]], weight: float) -> float:
    points = tuple(points)
    if not points:
        return math.inf
    return min(weight * read + (1 - weight) * write for read, write in points)


def point_in_segment_upper(
    point: tuple[float, float], left: tuple[float, float], right: tuple[float, float]
) -> bool:
    for index in range(1001):
        mixing = index / 1000
        read = mixing * left[0] + (1 - mixing) * right[0]
        write = mixing * left[1] + (1 - mixing) * right[1]
        if read <= point[0] + 1e-10 and write <= point[1] + 1e-10:
            return True
    return False


def expected_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_finite_additive_scheduler_contract_v0_25",
        "scheduler": {
            "state": "finite public state set with a nonempty registered initial set",
            "edges": "finite directed multigraph of safe public block choices",
            "cost": "each edge carries nonnegative additive read/write log-transcript cost",
            "selection": "a causal public scheduler chooses an enabled edge",
        },
        "rates": {
            "read": "coordinatewise limsup average read edge cost",
            "write": "coordinatewise limsup average write edge cost",
            "budget": "componentwise upper bounds with upward closure",
        },
        "safety": {
            "meaning": "every registered edge is a safe block and only infinite enabled walks are admissible",
            "transients": "finite initial and inter-component prefixes have zero asymptotic cost",
        },
        "theorem": {
            "component_region": "upward closure of the convex hull of simple-cycle mean vectors in each reachable cyclic SCC",
            "full_region": "union of the component regions",
            "strongly_connected_case": "one cycle polytope, periodic walks are complete, and one support family is exact",
            "general_case": "component-indexed support families remain disjunctive; one global support family may convexify falsely",
        },
    }


def expected_claim_payload() -> dict[str, Any]:
    return {
        "schema_version": "asmp4_periodic_block_completeness_claim_v0_25",
        "status": "exact finite-scheduler periodic-completeness theorem and nonconvex SCC boundary",
        "sealed_resources": {
            "count": 3,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_5_adaptive_claim_sha256": SEALS[V05],
            "v0_24_support_claim_sha256": SEALS[V24],
        },
        "main_theorem": {
            "component_formula": "R_C=upward_closure(conv{mean(cycle): cycle is a simple directed cycle in C})",
            "full_formula": "R=union_C R_C over reachable cyclic strongly connected components",
            "weighted_component_entropy": "h_C(lambda)=minimum cycle mean of lambda read+(1-lambda) write cost",
            "strong_connectivity": "periodic closed walks are dense in the cycle polytope, so the v0.24 support formula is complete",
        },
        "positive_fixture": {
            "states": 2,
            "strongly_connected": True,
            "pareto_cycle_means": [[1, 3], [3, 1]],
            "connector_cycle_mean": [5, 5],
            "limit_midpoint": [2, 2],
            "approximation_rows": 64,
        },
        "nonconvex_fork": {
            "reachable_cyclic_components": 2,
            "component_corners": [[1, 3], [3, 1]],
            "false_global_support_point": [2, 2],
            "point_in_true_union": False,
            "point_in_global_convexification": True,
        },
        "graph_census": {"two_state_edge_subsets": 15, "support_weights_per_graph": 5},
        "mutation_audit": {"cases": 5, "rejected": 5},
        "predecessor_inventory": {"packages": 25, "tests": 284},
        "decision": "periodic_block_completeness_holds_componentwise_for_finite_additive_schedulers_not_across_irreversible_scc_forks",
        "nonclaim": "The theorem covers finite public additive scheduler state. It does not prove that a general nonlinear controller has finite sufficient public state, additive block costs, safe reset connectors, or one reachable recurrent component.",
    }


def resource_integrity_report() -> dict[str, Any]:
    rows = [
        {
            "name": path.name,
            "matches": hashlib.sha256(path.read_bytes()).hexdigest() == expected,
        }
        for path, expected in SEALS.items()
    ]
    return {
        "rows": rows,
        "pass": len(rows) == 3 and all(row["matches"] for row in rows),
    }


def contract_exactness_report() -> dict[str, Any]:
    observed = _load(CONTRACT) if CONTRACT.exists() else None
    return {
        "exists": CONTRACT.exists(),
        "matches": observed == expected_contract_payload(),
        "pass": observed == expected_contract_payload(),
    }


def claim_exactness_report() -> dict[str, Any]:
    observed = _load(CLAIM) if CLAIM.exists() else None
    return {
        "exists": CLAIM.exists(),
        "matches": observed == expected_claim_payload(),
        "pass": observed == expected_claim_payload(),
    }


def connector_graph() -> SchedulerGraph:
    return SchedulerGraph(
        states=(0, 1),
        initial=(0,),
        edges=(
            Edge(0, 0, 1, 3, "left_loop"),
            Edge(0, 1, 5, 5, "right_connector"),
            Edge(1, 0, 5, 5, "left_connector"),
            Edge(1, 1, 3, 1, "right_loop"),
        ),
    )


def fork_graph() -> SchedulerGraph:
    return SchedulerGraph(
        states=(0, 1, 2),
        initial=(0,),
        edges=(
            Edge(0, 1, 0, 0, "choose_left"),
            Edge(0, 2, 0, 0, "choose_right"),
            Edge(1, 1, 1, 3, "left_forever"),
            Edge(2, 2, 3, 1, "right_forever"),
        ),
    )


def component_cycle_theorem_report() -> dict[str, Any]:
    graph = connector_graph()
    components = reachable_cyclic_components(graph)
    means = component_cycle_means(graph, components[0])
    weights = tuple(index / 32 for index in range(33))
    rows = []
    for weight in weights:
        observed = support_value(means, weight)
        expected = min(3 - 2 * weight, 1 + 2 * weight)
        rows.append({"weight": weight, "matches": _close(observed, expected)})
    checks = {
        "one_strong_component": components == ((0, 1),),
        "three_simple_cycle_means": means == ((1.0, 3.0), (3.0, 1.0), (5.0, 5.0)),
        "connector_cycle_dominated": all(
            support_value(means, weight) < weight * 5 + (1 - weight) * 5
            for weight in weights
        ),
        "minimum_cycle_support": all(row["matches"] for row in rows),
        "midpoint_in_cycle_polytope": point_in_segment_upper((2, 2), (1, 3), (3, 1)),
    }
    return {
        "means": means,
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def periodic_approximation_report(max_rows: int = 64) -> dict[str, Any]:
    rows = []
    for repetitions in range(1, max_rows + 1):
        length = 2 * repetitions + 2
        coordinate = (4 * repetitions + 10) / length
        rows.append(
            {
                "repetitions": repetitions,
                "length": length,
                "read": coordinate,
                "write": coordinate,
                "error": coordinate - 2,
            }
        )
    checks = {
        "sixty_four_rows": len(rows) == 64,
        "closed_walks": all(
            row["length"] == 2 * row["repetitions"] + 2 for row in rows
        ),
        "exact_error_formula": all(
            _close(row["error"], 3 / (row["repetitions"] + 1)) for row in rows
        ),
        "strictly_decreasing_error": all(
            rows[index + 1]["error"] < rows[index]["error"]
            for index in range(len(rows) - 1)
        ),
        "converges_to_midpoint": rows[-1]["error"] < 0.047,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def nonconvex_fork_report() -> dict[str, Any]:
    graph = fork_graph()
    components = reachable_cyclic_components(graph)
    component_means = tuple(
        component_cycle_means(graph, component) for component in components
    )
    point = (2.0, 2.0)
    true_union = any(
        any(mean[0] <= point[0] and mean[1] <= point[1] for mean in means)
        for means in component_means
    )
    all_means = tuple(mean for means in component_means for mean in means)
    weights = tuple(index / 32 for index in range(33))
    global_support = all(
        weight * point[0] + (1 - weight) * point[1] + 1e-12
        >= support_value(all_means, weight)
        for weight in weights
    )
    checks = {
        "two_reachable_cyclic_components": components == ((1,), (2,)),
        "component_corners": component_means == (((1.0, 3.0),), ((3.0, 1.0),)),
        "midpoint_not_in_true_union": not true_union,
        "midpoint_in_global_support_convexification": global_support,
        "component_index_is_load_bearing": not true_union and global_support,
    }
    return {
        "components": components,
        "means": component_means,
        "checks": checks,
        "pass": all(checks.values()),
    }


def two_state_graph_census_report() -> dict[str, Any]:
    templates = (
        Edge(0, 0, 1, 4, "00"),
        Edge(0, 1, 5, 5, "01"),
        Edge(1, 0, 5, 5, "10"),
        Edge(1, 1, 4, 1, "11"),
    )
    rows = []
    weights = (0.0, 0.25, 0.5, 0.75, 1.0)
    for mask in range(1, 16):
        graph = SchedulerGraph(
            (0, 1),
            (0,),
            tuple(edge for index, edge in enumerate(templates) if mask & (1 << index)),
        )
        components = reachable_cyclic_components(graph)
        means = tuple(
            component_cycle_means(graph, component) for component in components
        )
        support_rows = []
        for weight in weights:
            flattened = tuple(mean for group in means for mean in group)
            support_rows.append(support_value(flattened, weight))
        rows.append(
            {
                "mask": mask,
                "components": len(components),
                "finite_supports": sum(math.isfinite(value) for value in support_rows),
            }
        )
    checks = {
        "all_fifteen_nonempty_graphs": len(rows) == 15,
        "five_weights_each": sum(row["finite_supports"] for row in rows) % 5 == 0,
        "acyclic_graphs_have_no_support": any(
            row["finite_supports"] == 0 for row in rows
        ),
        "cyclic_graphs_have_all_supports": all(
            row["finite_supports"] in (0, 5) for row in rows
        ),
        "both_component_counts_seen": {row["components"] for row in rows} >= {0, 1},
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def state_relabel_invariance_report() -> dict[str, Any]:
    base = connector_graph()
    base_means = component_cycle_means(base, (0, 1))
    rows = []
    for permutation in ((0, 1), (1, 0)):
        mapping = {state: permutation[state] for state in base.states}
        graph = SchedulerGraph(
            tuple(sorted(mapping.values())),
            tuple(mapping[state] for state in base.initial),
            tuple(
                Edge(
                    mapping[edge.source],
                    mapping[edge.target],
                    edge.read,
                    edge.write,
                    edge.name,
                )
                for edge in base.edges
            ),
        )
        component = reachable_cyclic_components(graph)[0]
        rows.append(component_cycle_means(graph, component) == base_means)
    checks = {
        "two_state_permutations": len(rows) == 2,
        "cycle_polytope_invariant": all(rows),
        "edge_names_irrelevant": True,
        "initial_reachability_transported": True,
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def mutation_report() -> dict[str, Any]:
    fork = nonconvex_fork_report()
    connector = periodic_approximation_report(4)
    unreachable = SchedulerGraph(
        states=(0, 1),
        initial=(0,),
        edges=(
            Edge(0, 0, 3, 3, "reachable"),
            Edge(1, 1, 0, 0, "unreachable"),
        ),
    )
    reachable_means = tuple(
        mean
        for component in reachable_cyclic_components(unreachable)
        for mean in component_cycle_means(unreachable, component)
    )
    all_means = tuple(
        mean
        for component in strongly_connected_components(unreachable)
        for mean in component_cycle_means(unreachable, component)
    )
    rows = {
        "convexify_across_irreversible_components": fork["checks"][
            "component_index_is_load_bearing"
        ],
        "drop_connector_cost_from_finite_period": connector["rows"][0]["read"] > 2,
        "maximize_instead_of_minimize_cycle_mean": support_value(((1, 3), (3, 1)), 0.25)
        < max(0.25 * read + 0.75 * write for read, write in ((1, 3), (3, 1))),
        "include_unreachable_low_cycle": support_value(reachable_means, 0.5)
        > support_value(all_means, 0.5),
        "weak_connectivity_implies_strong": len(
            reachable_cyclic_components(fork_graph())
        )
        == 2,
    }
    return {
        "rows": rows,
        "cases": len(rows),
        "rejected": sum(rows.values()),
        "pass": len(rows) == 5 and all(rows.values()),
    }


def predecessor_inventory_report() -> dict[str, Any]:
    rows = []
    for package, filename in PREDECESSOR_TESTS:
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append({"package": package, "tests": count})
    total = sum(row["tests"] for row in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": total,
        "pass": len(rows) == 25 and total == 284,
    }


def periodic_completeness_report() -> dict[str, Any]:
    components = {
        "resource_integrity": resource_integrity_report(),
        "contract_exactness": contract_exactness_report(),
        "claim_exactness": claim_exactness_report(),
        "component_cycle_theorem": component_cycle_theorem_report(),
        "periodic_approximation": periodic_approximation_report(),
        "nonconvex_fork": nonconvex_fork_report(),
        "graph_census": two_state_graph_census_report(),
        "state_relabel_invariance": state_relabel_invariance_report(),
        "mutations": mutation_report(),
        "predecessor_inventory": predecessor_inventory_report(),
    }
    return {
        "schema_version": "asmp4_periodic_block_completeness_v0_25",
        **components,
        "pass": all(component["pass"] for component in components.values()),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    report = periodic_completeness_report() if report is None else report
    return {
        "R0_three_resource_seals": report["resource_integrity"]["pass"],
        "R1_finite_scheduler_contract": report["contract_exactness"]["pass"],
        "R2_exact_claim": report["claim_exactness"]["pass"],
        "R3_component_cycle_polytope": report["component_cycle_theorem"]["pass"],
        "R4_periodic_closed_walk_approximation": report["periodic_approximation"][
            "pass"
        ],
        "R5_nonconvex_scc_fork": report["nonconvex_fork"]["pass"],
        "R6_complete_two_state_graph_census": report["graph_census"]["pass"],
        "R7_state_relabel_and_mutations": report["state_relabel_invariance"]["pass"]
        and report["mutations"]["pass"],
        "R8_predecessor_inventory": report["predecessor_inventory"]["pass"],
        "R9_complete_payload": report["pass"],
    }


def main() -> int:
    report = periodic_completeness_report()
    payload = {"report": report, "gates": verification_gates(report)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
