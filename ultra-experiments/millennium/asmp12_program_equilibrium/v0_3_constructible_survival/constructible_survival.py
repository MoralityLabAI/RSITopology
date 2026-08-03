#!/usr/bin/env python3
"""Exact constructible graph correspondence for ASMP-12 v0.3.

Every registered budget-by-temptation cell receives a finite directed graph of
strictly profitable unilateral deviations.  Budget maps are asserted only
after exact inclusion and gain-preservation checks.  Adjacent temptation cells
are connected through explicit underlying-graph unions; their rational gain
decorations remain attached to the endpoint cells.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parent
V2_PATH = ROOT.parent / "v0_2_survival" / "run_survival.py"
SPEC = importlib.util.spec_from_file_location("asmp12_survival_v0_2_bound", V2_PATH)
V2 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(V2)

COSTS = (1, 2, 3)
BUDGETS = (1, 2, 3)
TEMPTATIONS = tuple(V2.TEMPTATIONS)
FAMILIES = {
    name: {key: Fraction(value) for key, value in values.items()}
    for name, values in V2.FAMILIES.items()
}

# Edge identity is (source row, source column, target row, target column,
# deviating player).  Positive rational gains are stored separately so that
# temptation zigzags are rigorously typed in the underlying graph category.


def fraction_text(value: Fraction | None) -> str | None:
    if value is None:
        return None
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def catalogs() -> tuple[tuple[tuple[int, ...], ...], ...]:
    return tuple(tuple(tuple(row) for row in catalog) for catalog in V2.V1.catalogs())


def utilities(
    family: str,
    temptation: Fraction,
    actions: tuple[int, int],
) -> tuple[Fraction, Fraction]:
    values = FAMILIES[family]
    if actions == (1, 1):
        return values["R"], values["R"]
    if actions == (1, 0):
        return values["S"], temptation
    if actions == (0, 1):
        return temptation, values["S"]
    return values["P"], values["P"]


def actions(
    catalog: Sequence[Sequence[int]],
    row_program: int,
    column_program: int,
) -> tuple[int, int]:
    return catalog[row_program][column_program], catalog[column_program][row_program]


def payoff(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    profile: tuple[int, int],
) -> tuple[Fraction, Fraction]:
    return utilities(family, temptation, actions(catalog, *profile))


def admitted(costs: Sequence[int], budget: int) -> tuple[int, ...]:
    return tuple(program for program, cost in enumerate(costs) if cost <= budget)


def unilateral_comparisons(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    programs: Sequence[int],
    profile: tuple[int, int],
) -> tuple[tuple[tuple[int, int, int, int, int], Fraction], ...]:
    """Return every unilateral edge identity and signed deviation gain."""

    row, column = profile
    current = payoff(catalog, family, temptation, profile)
    comparisons: list[tuple[tuple[int, int, int, int, int], Fraction]] = []
    for alternative in programs:
        if alternative != row:
            target = (alternative, column)
            gain = payoff(catalog, family, temptation, target)[0] - current[0]
            comparisons.append(((row, column, alternative, column, 0), gain))
        if alternative != column:
            target = (row, alternative)
            gain = payoff(catalog, family, temptation, target)[1] - current[1]
            comparisons.append(((row, column, row, alternative, 1), gain))
    return tuple(comparisons)


def build_graph(
    catalog: Sequence[Sequence[int]],
    family: str,
    temptation: Fraction,
    costs: Sequence[int],
    budget: int,
) -> dict[str, object]:
    """Build one exact weighted profitable-deviation cell graph."""

    programs = admitted(costs, budget)
    vertices = frozenset((row, column) for row in programs for column in programs)
    edges: set[tuple[int, int, int, int, int]] = set()
    gains: dict[tuple[int, int, int, int, int], Fraction] = {}
    margins: dict[tuple[int, int], Fraction | None] = {}
    outgoing: dict[tuple[int, int], set[tuple[int, int, int, int, int]]] = {
        vertex: set() for vertex in vertices
    }
    for profile in vertices:
        comparisons = unilateral_comparisons(
            catalog, family, temptation, programs, profile
        )
        margins[profile] = (
            min((-gain for _, gain in comparisons), default=None)
            if comparisons
            else None
        )
        for edge, gain in comparisons:
            if gain <= 0:
                continue
            edges.add(edge)
            gains[edge] = gain
            outgoing[profile].add(edge)
    sinks = frozenset(vertex for vertex in vertices if not outgoing[vertex])
    cooperative_sinks = frozenset(
        vertex for vertex in sinks if actions(catalog, *vertex) == (1, 1)
    )
    graph = {
        "programs": programs,
        "vertices": vertices,
        "edges": frozenset(edges),
        "gains": gains,
        "margins": margins,
        "sinks": sinks,
        "cooperative_sinks": cooperative_sinks,
    }
    if not graph_is_typed(graph):
        raise AssertionError("constructed graph failed its incidence typing")
    return graph


def graph_is_typed(graph: dict[str, object]) -> bool:
    vertices = graph["vertices"]
    edges = graph["edges"]
    gains = graph["gains"]
    if not isinstance(vertices, frozenset) or not isinstance(edges, frozenset):
        return False
    if not isinstance(gains, dict) or set(gains) != set(edges):
        return False
    for edge in edges:
        source = (edge[0], edge[1])
        target = (edge[2], edge[3])
        player = edge[4]
        if source not in vertices or target not in vertices or gains[edge] <= 0:
            return False
        if player == 0:
            if source[1] != target[1] or source[0] == target[0]:
                return False
        elif player == 1:
            if source[0] != target[0] or source[1] == target[1]:
                return False
        else:
            return False
    return True


def graph_equal(left: dict[str, object], right: dict[str, object]) -> bool:
    return bool(
        left["vertices"] == right["vertices"]
        and left["edges"] == right["edges"]
        and left["gains"] == right["gains"]
        and left["margins"] == right["margins"]
        and left["sinks"] == right["sinks"]
        and left["cooperative_sinks"] == right["cooperative_sinks"]
    )


def graph_digest(graph: dict[str, object]) -> str:
    payload = {
        "vertices": [list(vertex) for vertex in sorted(graph["vertices"])],
        "edges": [
            {"edge": list(edge), "gain": fraction_text(graph["gains"][edge])}
            for edge in sorted(graph["edges"])
        ],
        "margins": [
            {"profile": list(profile), "margin": fraction_text(graph["margins"][profile])}
            for profile in sorted(graph["vertices"])
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def budget_inclusion(
    left_key: tuple[int, str, Fraction, int],
    right_key: tuple[int, str, Fraction, int],
    left: dict[str, object],
    right: dict[str, object],
) -> dict[str, object]:
    same_fiber = left_key[:3] == right_key[:3] and right_key[3] == left_key[3] + 1
    vertices_included = left["vertices"] <= right["vertices"]
    edges_included = left["edges"] <= right["edges"]
    gains_preserved = edges_included and all(
        left["gains"][edge] == right["gains"][edge] for edge in left["edges"]
    )
    return {
        "left_key": left_key,
        "right_key": right_key,
        "map_type": "weighted_directed_graph_inclusion",
        "same_parameter_fiber": same_fiber,
        "vertices_included": vertices_included,
        "edges_included": edges_included,
        "old_edge_gains_preserved": gains_preserved,
        "verified": same_fiber and vertices_included and edges_included and gains_preserved,
    }


def adjacent_union_zigzag(
    left_key: tuple[int, str, Fraction, int],
    right_key: tuple[int, str, Fraction, int],
    left: dict[str, object],
    right: dict[str, object],
) -> dict[str, object]:
    """Construct ``G_t -> G_t union G_t' <- G_t'`` on underlying graphs."""

    same_fiber = (
        left_key[0] == right_key[0]
        and left_key[1] == right_key[1]
        and left_key[3] == right_key[3]
    )
    union_vertices = frozenset(left["vertices"] | right["vertices"])
    union_edges = frozenset(left["edges"] | right["edges"])
    decorations = {
        edge: (left["gains"].get(edge), right["gains"].get(edge))
        for edge in union_edges
    }
    typed_union = all(
        (edge[0], edge[1]) in union_vertices
        and (edge[2], edge[3]) in union_vertices
        for edge in union_edges
    )
    left_map = left["vertices"] <= union_vertices and left["edges"] <= union_edges
    right_map = right["vertices"] <= union_vertices and right["edges"] <= union_edges
    if left["edges"] == right["edges"]:
        relation = "equal_underlying_graphs"
        direct_inclusion = "identity_both_directions"
    elif left["edges"] < right["edges"]:
        relation = "left_strict_subgraph_of_right"
        direct_inclusion = "left_to_right_verified"
    elif right["edges"] < left["edges"]:
        relation = "right_strict_subgraph_of_left"
        direct_inclusion = "right_to_left_verified"
    else:
        relation = "incomparable_edge_sets"
        direct_inclusion = None
    return {
        "left_key": left_key,
        "right_key": right_key,
        "object_type": "adjacent_union_zigzag_in_underlying_finite_directed_graphs",
        "arrows": ("left_to_union", "right_to_union"),
        "union_vertices": union_vertices,
        "union_edges": union_edges,
        "endpoint_gain_decorations": decorations,
        "relation": relation,
        "verified_direct_inclusion": direct_inclusion,
        "same_parameter_fiber": same_fiber,
        "left_map_verified": left_map,
        "right_map_verified": right_map,
        "typed_union": typed_union,
        "verified": same_fiber and left_map and right_map and typed_union,
    }


def outgoing_edges(
    graph: dict[str, object],
    profile: tuple[int, int],
) -> tuple[tuple[int, int, int, int, int], ...]:
    return tuple(
        sorted(edge for edge in graph["edges"] if edge[:2] == profile)
    )


def sink_event(
    axis: str,
    kind: str,
    profile: tuple[int, int],
    left_key: tuple[int, str, Fraction, int],
    right_key: tuple[int, str, Fraction, int],
    left: dict[str, object],
    right: dict[str, object],
) -> dict[str, object]:
    left_exists = profile in left["vertices"]
    right_exists = profile in right["vertices"]
    left_outgoing = outgoing_edges(left, profile) if left_exists else ()
    right_outgoing = outgoing_edges(right, profile) if right_exists else ()
    return {
        "axis": axis,
        "kind": kind,
        "profile": profile,
        "left_key": left_key,
        "right_key": right_key,
        "left_exists": left_exists,
        "right_exists": right_exists,
        "left_is_cooperative_sink": profile in left["cooperative_sinks"],
        "right_is_cooperative_sink": profile in right["cooperative_sinks"],
        "left_margin": left["margins"].get(profile),
        "right_margin": right["margins"].get(profile),
        "left_profitable_edges": tuple(
            (edge, left["gains"][edge]) for edge in left_outgoing
        ),
        "right_profitable_edges": tuple(
            (edge, right["gains"][edge]) for edge in right_outgoing
        ),
    }


def adjacent_sink_events(
    axis: str,
    left_key: tuple[int, str, Fraction, int],
    right_key: tuple[int, str, Fraction, int],
    left: dict[str, object],
    right: dict[str, object],
) -> tuple[dict[str, object], ...]:
    events: list[dict[str, object]] = []
    left_sinks = left["cooperative_sinks"]
    right_sinks = right["cooperative_sinks"]
    for profile in sorted(left_sinks - right_sinks):
        events.append(sink_event(axis, "cooperative_sink_death", profile, left_key, right_key, left, right))
    for profile in sorted(right_sinks - left_sinks):
        events.append(sink_event(axis, "cooperative_sink_birth", profile, left_key, right_key, left, right))
    return tuple(events)


def event_certificate_valid(event: dict[str, object]) -> bool:
    if event["kind"] == "cooperative_sink_death":
        return bool(
            event["left_is_cooperative_sink"]
            and not event["right_is_cooperative_sink"]
            and event["right_exists"]
            and event["right_margin"] is not None
            and event["right_margin"] < 0
            and event["right_profitable_edges"]
        )
    if event["kind"] == "cooperative_sink_birth":
        if not event["right_is_cooperative_sink"] or event["left_is_cooperative_sink"]:
            return False
        if not event["left_exists"]:
            return True
        return bool(
            event["left_margin"] is not None
            and event["left_margin"] < 0
            and event["left_profitable_edges"]
        )
    return False


def graph_margin_status_valid(graph: dict[str, object]) -> bool:
    for vertex in graph["vertices"]:
        margin = graph["margins"][vertex]
        is_sink = vertex in graph["sinks"]
        if margin is None:
            if not is_sink:
                return False
        elif is_sink != (margin >= 0):
            return False
    return True


@lru_cache(maxsize=1)
def build_surface() -> dict[str, object]:
    catalog_universe = catalogs()
    graphs: dict[tuple[int, str, Fraction, int], dict[str, object]] = {}
    for catalog_index, catalog in enumerate(catalog_universe):
        for family in FAMILIES:
            for temptation in TEMPTATIONS:
                for budget in BUDGETS:
                    key = (catalog_index, family, temptation, budget)
                    graphs[key] = build_graph(catalog, family, temptation, COSTS, budget)

    budget_maps: list[dict[str, object]] = []
    temptation_zigzags: list[dict[str, object]] = []
    cooperative_sink_events: list[dict[str, object]] = []
    for catalog_index, _catalog in enumerate(catalog_universe):
        for family in FAMILIES:
            for temptation in TEMPTATIONS:
                for left_budget, right_budget in zip(BUDGETS, BUDGETS[1:]):
                    left_key = (catalog_index, family, temptation, left_budget)
                    right_key = (catalog_index, family, temptation, right_budget)
                    left = graphs[left_key]
                    right = graphs[right_key]
                    budget_maps.append(budget_inclusion(left_key, right_key, left, right))
                    cooperative_sink_events.extend(
                        adjacent_sink_events("budget", left_key, right_key, left, right)
                    )
            for budget in BUDGETS:
                for left_temptation, right_temptation in zip(TEMPTATIONS, TEMPTATIONS[1:]):
                    left_key = (catalog_index, family, left_temptation, budget)
                    right_key = (catalog_index, family, right_temptation, budget)
                    left = graphs[left_key]
                    right = graphs[right_key]
                    temptation_zigzags.append(
                        adjacent_union_zigzag(left_key, right_key, left, right)
                    )
                    cooperative_sink_events.extend(
                        adjacent_sink_events("temptation", left_key, right_key, left, right)
                    )

    return {
        "config": {
            "costs": COSTS,
            "budgets": BUDGETS,
            "temptations": TEMPTATIONS,
            "families": FAMILIES,
        },
        "catalogs": catalog_universe,
        "graphs": graphs,
        "graph_maps": {
            "budget_inclusions": tuple(budget_maps),
            "temptation_adjacent_union_zigzags": tuple(temptation_zigzags),
        },
        # Sink events are intentionally not encoded as graph maps.
        "cooperative_sink_events": tuple(cooperative_sink_events),
    }


def relabel_catalog(
    catalog: Sequence[Sequence[int]],
    permutation: Sequence[int],
) -> tuple[tuple[int, ...], ...]:
    size = len(catalog)
    output = [[0] * size for _ in range(size)]
    for old_row in range(size):
        for old_column in range(size):
            output[permutation[old_row]][permutation[old_column]] = catalog[old_row][old_column]
    return tuple(tuple(row) for row in output)


def relabel_costs(costs: Sequence[int], permutation: Sequence[int]) -> tuple[int, ...]:
    output = [0] * len(costs)
    for old, new in enumerate(permutation):
        output[new] = costs[old]
    return tuple(output)


def relabel_graph(graph: dict[str, object], permutation: Sequence[int]) -> dict[str, object]:
    def vertex_map(vertex: tuple[int, int]) -> tuple[int, int]:
        return permutation[vertex[0]], permutation[vertex[1]]

    def edge_map(edge: tuple[int, int, int, int, int]) -> tuple[int, int, int, int, int]:
        return (
            permutation[edge[0]],
            permutation[edge[1]],
            permutation[edge[2]],
            permutation[edge[3]],
            edge[4],
        )

    mapped_edges = {edge_map(edge): graph["gains"][edge] for edge in graph["edges"]}
    return {
        "vertices": frozenset(vertex_map(vertex) for vertex in graph["vertices"]),
        "edges": frozenset(mapped_edges),
        "gains": mapped_edges,
        "margins": {vertex_map(vertex): margin for vertex, margin in graph["margins"].items()},
        "sinks": frozenset(vertex_map(vertex) for vertex in graph["sinks"]),
        "cooperative_sinks": frozenset(
            vertex_map(vertex) for vertex in graph["cooperative_sinks"]
        ),
    }


def five_robustness_probes(surface: dict[str, object]) -> dict[str, dict[str, object]]:
    catalog_universe = surface["catalogs"]
    graphs = surface["graphs"]

    padding_ok = True
    padding_checks = 0
    for key, graph in graphs.items():
        catalog_index, family, temptation, budget = key
        replay = build_graph(
            catalog_universe[catalog_index],
            family,
            temptation,
            tuple(cost + 2 for cost in COSTS),
            budget + 2,
        )
        padding_checks += 1
        padding_ok = padding_ok and graph_equal(graph, replay)

    permutation = (2, 0, 1)
    equivariance_ok = True
    equivariance_checks = 0
    permuted_costs = relabel_costs(COSTS, permutation)
    for key, graph in graphs.items():
        catalog_index, family, temptation, budget = key
        transformed_catalog = relabel_catalog(catalog_universe[catalog_index], permutation)
        transformed = build_graph(
            transformed_catalog, family, temptation, permuted_costs, budget
        )
        equivariance_checks += 1
        equivariance_ok = equivariance_ok and graph_equal(
            relabel_graph(graph, permutation), transformed
        )

    source_blind_ok = True
    source_blind_checks = 0
    column_permutation = (2, 1, 0)
    for catalog_index, catalog in enumerate(catalog_universe):
        if not V2.V1.source_blind(catalog):
            continue
        column_permuted = tuple(
            tuple(row[old] for old in column_permutation) for row in catalog
        )
        for family in FAMILIES:
            for temptation in TEMPTATIONS:
                for budget in BUDGETS:
                    source_blind_checks += 1
                    original = graphs[(catalog_index, family, temptation, budget)]
                    replay = build_graph(column_permuted, family, temptation, COSTS, budget)
                    source_blind_ok = source_blind_ok and graph_equal(original, replay)

    canonical = V2.V1.canonical_catalog()
    profile = (1, 1)
    boundary_rows: list[dict[str, object]] = []
    for label, temptation in (
        ("below", Fraction(299, 100)),
        ("at", Fraction(3)),
        ("above", Fraction(301, 100)),
    ):
        graph = build_graph(canonical, "pd_order", temptation, COSTS, 3)
        boundary_rows.append(
            {
                "label": label,
                "temptation": temptation,
                "margin": graph["margins"][profile],
                "is_cooperative_sink": profile in graph["cooperative_sinks"],
            }
        )
    boundary_ok = (
        boundary_rows[0]["margin"] == Fraction(1, 100)
        and boundary_rows[0]["is_cooperative_sink"]
        and boundary_rows[1]["margin"] == 0
        and boundary_rows[1]["is_cooperative_sink"]
        and boundary_rows[2]["margin"] == Fraction(-1, 100)
        and not boundary_rows[2]["is_cooperative_sink"]
    )

    positive_margins = 0
    zero_margins = 0
    margin_ok = True
    for graph in graphs.values():
        for profile in graph["cooperative_sinks"]:
            margin = graph["margins"][profile]
            if margin is None:
                continue
            if margin == 0:
                zero_margins += 1
            elif margin > 0:
                positive_margins += 1
                epsilon = margin / 4
                margin_ok = margin_ok and margin - 2 * epsilon > 0
            else:
                margin_ok = False
    margin_ok = margin_ok and positive_margins > 0 and zero_margins > 0

    return {
        "cost_padding_replay": {
            "passed": padding_ok,
            "checks": padding_checks,
        },
        "program_label_equivariance": {
            "passed": equivariance_ok,
            "checks": equivariance_checks,
            "permutation_old_to_new": permutation,
        },
        "source_blind_column_permutation_null": {
            "passed": source_blind_ok and source_blind_checks > 0,
            "checks": source_blind_checks,
        },
        "exact_boundary_microgrid": {
            "passed": boundary_ok,
            "rows": tuple(boundary_rows),
        },
        "positive_margin_payoff_perturbation": {
            "passed": margin_ok,
            "positive_margin_certificates": positive_margins,
            "zero_margin_controls": zero_margins,
            "epsilon_rule": "epsilon=margin/4; residual=margin-2*epsilon",
        },
    }
