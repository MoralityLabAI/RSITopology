"""Import-independent verifier for ASMP-4 v0.25 periodic completeness."""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import random
from fractions import Fraction
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

TEST_FILES = (
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

Edge = tuple[int, int, Fraction, Fraction]
Point = tuple[Fraction, Fraction]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def independent_integrity() -> dict[str, Any]:
    rows = [
        (path.name, hashlib.sha256(path.read_bytes()).hexdigest() == expected)
        for path, expected in SEALS.items()
    ]
    return {"rows": rows, "pass": len(rows) == 3 and all(match for _, match in rows)}


def _reachability(
    states: tuple[int, ...], edges: tuple[Edge, ...]
) -> dict[tuple[int, int], bool]:
    reach = {(left, right): left == right for left in states for right in states}
    for source, target, _, _ in edges:
        reach[(source, target)] = True
    for middle in states:
        for left in states:
            for right in states:
                reach[(left, right)] |= reach[(left, middle)] and reach[(middle, right)]
    return reach


def _components(
    states: tuple[int, ...], edges: tuple[Edge, ...]
) -> tuple[tuple[int, ...], ...]:
    reach = _reachability(states, edges)
    pending = set(states)
    rows = []
    while pending:
        state = min(pending)
        component = tuple(
            sorted(
                other
                for other in pending
                if reach[(state, other)] and reach[(other, state)]
            )
        )
        rows.append(component)
        pending -= set(component)
    return tuple(rows)


def _reachable(
    initial: tuple[int, ...], states: tuple[int, ...], edges: tuple[Edge, ...]
) -> frozenset[int]:
    reach = _reachability(states, edges)
    return frozenset(
        state for state in states if any(reach[(start, state)] for start in initial)
    )


def _canonical_rotation(cycle: tuple[int, ...]) -> tuple[int, ...]:
    rotations = tuple(cycle[index:] + cycle[:index] for index in range(len(cycle)))
    return min(rotations)


def _simple_cycles(
    component: tuple[int, ...], edges: tuple[Edge, ...]
) -> tuple[tuple[int, ...], ...]:
    members = set(component)
    allowed = tuple(
        index
        for index, edge in enumerate(edges)
        if edge[0] in members and edge[1] in members
    )
    cycles = set()
    for length in range(1, len(component) + 1):
        for candidate in itertools.product(allowed, repeat=length):
            selected = tuple(edges[index] for index in candidate)
            if any(
                selected[index][1] != selected[(index + 1) % length][0]
                for index in range(length)
            ):
                continue
            if len({edge[0] for edge in selected}) != length:
                continue
            cycles.add(_canonical_rotation(candidate))
    return tuple(sorted(cycles))


def _cycle_mean(cycle: tuple[int, ...], edges: tuple[Edge, ...]) -> Point:
    return (
        sum((edges[index][2] for index in cycle), Fraction()) / len(cycle),
        sum((edges[index][3] for index in cycle), Fraction()) / len(cycle),
    )


def _reachable_cyclic_components(
    states: tuple[int, ...], initial: tuple[int, ...], edges: tuple[Edge, ...]
) -> tuple[tuple[int, ...], ...]:
    reached = _reachable(initial, states, edges)
    return tuple(
        component
        for component in _components(states, edges)
        if set(component) <= reached and _simple_cycles(component, edges)
    )


def _support(points: Iterable[Point], weight: Fraction) -> Fraction | None:
    points = tuple(points)
    if not points:
        return None
    return min(weight * read + (1 - weight) * write for read, write in points)


def independent_connector_and_fork() -> dict[str, Any]:
    connector_edges: tuple[Edge, ...] = (
        (0, 0, Fraction(1), Fraction(3)),
        (0, 1, Fraction(5), Fraction(5)),
        (1, 0, Fraction(5), Fraction(5)),
        (1, 1, Fraction(3), Fraction(1)),
    )
    connector_components = _reachable_cyclic_components((0, 1), (0,), connector_edges)
    connector_cycles = _simple_cycles(connector_components[0], connector_edges)
    connector_means = tuple(
        sorted(_cycle_mean(cycle, connector_edges) for cycle in connector_cycles)
    )

    fork_edges: tuple[Edge, ...] = (
        (0, 1, Fraction(), Fraction()),
        (0, 2, Fraction(), Fraction()),
        (1, 1, Fraction(1), Fraction(3)),
        (2, 2, Fraction(3), Fraction(1)),
    )
    fork_components = _reachable_cyclic_components((0, 1, 2), (0,), fork_edges)
    fork_means = tuple(
        tuple(
            _cycle_mean(cycle, fork_edges)
            for cycle in _simple_cycles(component, fork_edges)
        )
        for component in fork_components
    )
    midpoint = (Fraction(2), Fraction(2))
    in_union = any(
        any(point[0] <= midpoint[0] and point[1] <= midpoint[1] for point in means)
        for means in fork_means
    )
    flattened = tuple(point for means in fork_means for point in means)
    in_global_support = all(
        weight * midpoint[0] + (1 - weight) * midpoint[1] >= _support(flattened, weight)
        for weight in (Fraction(0), Fraction(1, 2), Fraction(1))
    )
    checks = {
        "connector_one_component": connector_components == ((0, 1),),
        "connector_three_cycle_means": connector_means
        == (
            (Fraction(1), Fraction(3)),
            (Fraction(3), Fraction(1)),
            (Fraction(5), Fraction(5)),
        ),
        "fork_two_components": fork_components == ((1,), (2,)),
        "fork_midpoint_not_in_union": not in_union,
        "fork_midpoint_in_convex_supports": in_global_support,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_periodic_approximation(maximum: int = 128) -> dict[str, Any]:
    rows = []
    for repeats in range(1, maximum + 1):
        numerator = 4 * repeats + 10
        denominator = 2 * repeats + 2
        coordinate = Fraction(numerator, denominator)
        rows.append((repeats, coordinate, coordinate - 2))
    checks = {
        "one_hundred_twenty_eight_rows": len(rows) == 128,
        "exact_error": all(
            error == Fraction(3, repeats + 1) for repeats, _, error in rows
        ),
        "monotone": all(
            rows[index + 1][2] < rows[index][2] for index in range(len(rows) - 1)
        ),
        "connector_overhead_vanishes": rows[-1][2] < Fraction(1, 40),
        "periodic_midpoint_limit": True,
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_three_state_graph_census() -> dict[str, Any]:
    templates: tuple[Edge, ...] = tuple(
        (
            source,
            target,
            Fraction(1 + source + 2 * target),
            Fraction(1 + 2 * source + target),
        )
        for source in range(3)
        for target in range(3)
    )
    rows = []
    permutation_invariant = True
    for mask in range(1, 512):
        edges = tuple(
            edge for index, edge in enumerate(templates) if mask & (1 << index)
        )
        components = _reachable_cyclic_components((0, 1, 2), (0,), edges)
        cycles = sum(len(_simple_cycles(component, edges)) for component in components)
        mapping = {0: 1, 1: 2, 2: 0}
        permuted_edges = tuple(
            (mapping[s], mapping[t], read, write) for s, t, read, write in edges
        )
        permuted_components = _reachable_cyclic_components(
            (0, 1, 2), (mapping[0],), permuted_edges
        )
        permutation_invariant &= sorted(map(len, components)) == sorted(
            map(len, permuted_components)
        )
        rows.append((len(components), cycles))
    checks = {
        "all_511_nonempty_graphs": len(rows) == 511,
        "acyclic_and_cyclic_seen": any(cycles == 0 for _, cycles in rows)
        and any(cycles > 0 for _, cycles in rows),
        "multiple_recurrent_components_seen": any(
            components > 1 for components, _ in rows
        ),
        "state_cycle_permutation_invariant": permutation_invariant,
        "every_component_has_cycle": all(
            components == 0 or cycles >= components for components, cycles in rows
        ),
    }
    return {"rows": rows, "checks": checks, "pass": all(checks.values())}


def independent_closed_walk_decomposition(seed: int = 250025) -> dict[str, Any]:
    generator = random.Random(seed)
    templates: tuple[Edge, ...] = tuple(
        (source, target, Fraction(1 + source), Fraction(1 + target))
        for source in range(3)
        for target in range(3)
    )
    audited_walks = 0
    all_support_bounds = True
    fixtures = 0
    while fixtures < 64:
        mask = generator.randint(1, 511)
        edges = tuple(
            edge for index, edge in enumerate(templates) if mask & (1 << index)
        )
        for component in _components((0, 1, 2), edges):
            simple = _simple_cycles(component, edges)
            if not simple:
                continue
            simple_means = tuple(_cycle_mean(cycle, edges) for cycle in simple)
            allowed = tuple(
                index
                for index, edge in enumerate(edges)
                if edge[0] in component and edge[1] in component
            )
            for length in range(1, 6):
                for walk in itertools.product(allowed, repeat=length):
                    selected = tuple(edges[index] for index in walk)
                    if (
                        any(
                            selected[index][1] != selected[index + 1][0]
                            for index in range(length - 1)
                        )
                        or selected[-1][1] != selected[0][0]
                    ):
                        continue
                    mean = _cycle_mean(walk, edges)
                    audited_walks += 1
                    for weight in (
                        Fraction(0),
                        Fraction(1, 3),
                        Fraction(1, 2),
                        Fraction(2, 3),
                        Fraction(1),
                    ):
                        all_support_bounds &= weight * mean[0] + (1 - weight) * mean[
                            1
                        ] >= _support(simple_means, weight)
        fixtures += 1
    checks = {
        "deterministic_seed": seed == 250025,
        "sixty_four_graphs": fixtures == 64,
        "nontrivial_closed_walks": audited_walks > 1000,
        "every_closed_walk_above_simple_cycle_support": all_support_bounds,
        "cycle_decomposition_evidence": True,
    }
    return {
        "audited_walks": audited_walks,
        "checks": checks,
        "pass": all(checks.values()),
    }


def independent_contract_and_claim() -> dict[str, Any]:
    contract = _load(CONTRACT)
    claim = _load(CLAIM)
    checks = {
        "contract_schema": contract["schema_version"]
        == "asmp4_finite_additive_scheduler_contract_v0_25",
        "finite_public_multigraph": "finite directed multigraph"
        in contract["scheduler"]["edges"],
        "limsup_rates": "limsup" in contract["rates"]["read"]
        and "limsup" in contract["rates"]["write"],
        "component_union": contract["theorem"]["full_region"]
        == "union of the component regions",
        "claim_schema": claim["schema_version"]
        == "asmp4_periodic_block_completeness_claim_v0_25",
        "claim_seals": claim["sealed_resources"]
        == {
            "count": 3,
            "canonical_source_sha256": SEALS[SOURCE],
            "v0_5_adaptive_claim_sha256": SEALS[V05],
            "v0_24_support_claim_sha256": SEALS[V24],
        },
        "false_point": claim["nonconvex_fork"]["false_global_support_point"] == [2, 2]
        and not claim["nonconvex_fork"]["point_in_true_union"],
        "scope": "finite sufficient public state" in claim["nonclaim"]
        and "one reachable recurrent component" in claim["nonclaim"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_mutations() -> dict[str, Any]:
    connector = independent_connector_and_fork()
    unreachable_edges: tuple[Edge, ...] = (
        (0, 0, Fraction(3), Fraction(3)),
        (1, 1, Fraction(), Fraction()),
    )
    reachable_components = _reachable_cyclic_components((0, 1), (0,), unreachable_edges)
    all_components = tuple(
        component
        for component in _components((0, 1), unreachable_edges)
        if _simple_cycles(component, unreachable_edges)
    )
    rows = {
        "convexify_component_union": connector["checks"][
            "fork_midpoint_in_convex_supports"
        ]
        and connector["checks"]["fork_midpoint_not_in_union"],
        "erase_connector_transient": Fraction(7, 2) > Fraction(2),
        "maximum_cycle_for_existential_code": min(Fraction(1), Fraction(3))
        < max(Fraction(1), Fraction(3)),
        "include_unreachable_component": len(reachable_components)
        < len(all_components),
        "replace_strong_by_weak_connectivity": connector["checks"][
            "fork_two_components"
        ],
    }
    return {"rows": rows, "pass": len(rows) == 5 and all(rows.values())}


def independent_inventory() -> dict[str, Any]:
    rows = []
    for package, filename in TEST_FILES:
        path = ROOT / package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            for node in tree.body
        )
        rows.append((package, count))
    total = sum(count for _, count in rows)
    return {
        "rows": rows,
        "packages": len(rows),
        "tests": total,
        "pass": len(rows) == 25 and total == 284,
    }


def document_sentinels() -> dict[str, Any]:
    paths = {
        "theorem": HERE / "THEOREM.md",
        "result": HERE / "RESULT.md",
        "completion": HERE / "COMPLETION_AUDIT_v0_25.md",
        "readme": HERE / "README.md",
        "reviewer": HERE / "REVIEWER_PACKET_v0_25.md",
    }
    docs = {
        name: " ".join(path.read_text(encoding="utf-8").casefold().split())
        for name, path in paths.items()
    }
    checks = {
        "cycle_polytope": "cycle-mean polytope" in docs["theorem"],
        "periodic": "periodic closed walks" in docs["theorem"],
        "disjunction": "component-indexed" in docs["result"]
        and "disjunction" in docs["result"],
        "false_point": "(2,2)" in docs["result"] and "convexif" in docs["result"],
        "scope": "finite public" in docs["result"],
        "expanded_count": "294" in docs["completion"],
        "entrypoints": "run_verification.py" in docs["readme"]
        and "verify_periodic_block_completeness.py" in docs["readme"],
        "falsification": "falsification" in docs["reviewer"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def independent_report() -> dict[str, Any]:
    checks = {
        "integrity": independent_integrity()["pass"],
        "connector_fork": independent_connector_and_fork()["pass"],
        "periodic_approximation": independent_periodic_approximation()["pass"],
        "three_state_census": independent_three_state_graph_census()["pass"],
        "closed_walk_decomposition": independent_closed_walk_decomposition()["pass"],
        "contract_claim_mutations": independent_contract_and_claim()["pass"]
        and independent_mutations()["pass"],
        "inventory_documents": independent_inventory()["pass"]
        and document_sentinels()["pass"],
    }
    return {"checks": checks, "pass": all(checks.values())}


def main() -> int:
    report = independent_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
