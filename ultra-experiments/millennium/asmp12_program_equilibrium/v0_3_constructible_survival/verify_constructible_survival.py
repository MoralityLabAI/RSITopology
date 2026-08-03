#!/usr/bin/env python3
"""Independent exact verifier for the ASMP-12 v0.3 graph correspondence.

This module does not import the primary implementation.  It reconstructs cell
graphs from the passed finite catalogs and payoff parameters, then verifies
budget inclusions, adjacent unions, and the derived sink-event signatures.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence


def _actions(
    catalog: Sequence[Sequence[int]], row: int, column: int
) -> tuple[int, int]:
    return catalog[row][column], catalog[column][row]


def _utilities(
    family_values: dict[str, Fraction],
    temptation: Fraction,
    action_pair: tuple[int, int],
) -> tuple[Fraction, Fraction]:
    if action_pair == (1, 1):
        return family_values["R"], family_values["R"]
    if action_pair == (1, 0):
        return family_values["S"], temptation
    if action_pair == (0, 1):
        return temptation, family_values["S"]
    return family_values["P"], family_values["P"]


def _payoff(
    catalog: Sequence[Sequence[int]],
    family_values: dict[str, Fraction],
    temptation: Fraction,
    profile: tuple[int, int],
) -> tuple[Fraction, Fraction]:
    return _utilities(family_values, temptation, _actions(catalog, *profile))


def rebuild_graph(
    catalog: Sequence[Sequence[int]],
    family_values: dict[str, Fraction],
    temptation: Fraction,
    costs: Sequence[int],
    budget: int,
) -> dict[str, object]:
    programs = tuple(index for index, cost in enumerate(costs) if cost <= budget)
    vertices = frozenset((row, column) for row in programs for column in programs)
    edges: set[tuple[int, int, int, int, int]] = set()
    gains: dict[tuple[int, int, int, int, int], Fraction] = {}
    margins: dict[tuple[int, int], Fraction | None] = {}
    for row, column in vertices:
        current = _payoff(catalog, family_values, temptation, (row, column))
        comparison_gains: list[Fraction] = []
        for alternative in programs:
            if alternative != row:
                target = (alternative, column)
                gain = _payoff(catalog, family_values, temptation, target)[0] - current[0]
                comparison_gains.append(gain)
                if gain > 0:
                    edge = (row, column, alternative, column, 0)
                    edges.add(edge)
                    gains[edge] = gain
            if alternative != column:
                target = (row, alternative)
                gain = _payoff(catalog, family_values, temptation, target)[1] - current[1]
                comparison_gains.append(gain)
                if gain > 0:
                    edge = (row, column, row, alternative, 1)
                    edges.add(edge)
                    gains[edge] = gain
        margins[(row, column)] = (
            min((-gain for gain in comparison_gains), default=None)
            if comparison_gains
            else None
        )
    sinks = frozenset(
        vertex
        for vertex in vertices
        if not any(edge[:2] == vertex for edge in edges)
    )
    cooperative_sinks = frozenset(
        vertex for vertex in sinks if _actions(catalog, *vertex) == (1, 1)
    )
    return {
        "vertices": vertices,
        "edges": frozenset(edges),
        "gains": gains,
        "margins": margins,
        "sinks": sinks,
        "cooperative_sinks": cooperative_sinks,
    }


def _matches(primary: dict[str, object], rebuilt: dict[str, object]) -> bool:
    return all(primary[field] == rebuilt[field] for field in (
        "vertices", "edges", "gains", "margins", "sinks", "cooperative_sinks"
    ))


def _event_signatures_from_pairs(
    pairs: Sequence[tuple[str, tuple[int, str, Fraction, int], tuple[int, str, Fraction, int]]],
    graphs: dict[tuple[int, str, Fraction, int], dict[str, object]],
) -> set[tuple[object, ...]]:
    signatures: set[tuple[object, ...]] = set()
    for axis, left_key, right_key in pairs:
        left = graphs[left_key]["cooperative_sinks"]
        right = graphs[right_key]["cooperative_sinks"]
        for profile in left - right:
            signatures.add((axis, "cooperative_sink_death", left_key, right_key, profile))
        for profile in right - left:
            signatures.add((axis, "cooperative_sink_birth", left_key, right_key, profile))
    return signatures


def verify_surface(surface: dict[str, object]) -> dict[str, object]:
    config = surface["config"]
    catalogs = surface["catalogs"]
    primary_graphs = surface["graphs"]
    rebuilt_graphs: dict[tuple[int, str, Fraction, int], dict[str, object]] = {}
    graph_agreement = True
    for key, primary in primary_graphs.items():
        catalog_index, family, temptation, budget = key
        rebuilt = rebuild_graph(
            catalogs[catalog_index],
            config["families"][family],
            temptation,
            config["costs"],
            budget,
        )
        rebuilt_graphs[key] = rebuilt
        graph_agreement = graph_agreement and _matches(primary, rebuilt)

    budget_maps = surface["graph_maps"]["budget_inclusions"]
    budget_ok = True
    pair_specs: list[
        tuple[str, tuple[int, str, Fraction, int], tuple[int, str, Fraction, int]]
    ] = []
    for record in budget_maps:
        left_key = record["left_key"]
        right_key = record["right_key"]
        left = rebuilt_graphs[left_key]
        right = rebuilt_graphs[right_key]
        expected = (
            left["vertices"] <= right["vertices"]
            and left["edges"] <= right["edges"]
            and all(left["gains"][edge] == right["gains"][edge] for edge in left["edges"])
        )
        budget_ok = budget_ok and expected and record["verified"]
        pair_specs.append(("budget", left_key, right_key))

    zigzags = surface["graph_maps"]["temptation_adjacent_union_zigzags"]
    zigzag_ok = True
    for record in zigzags:
        left_key = record["left_key"]
        right_key = record["right_key"]
        left = rebuilt_graphs[left_key]
        right = rebuilt_graphs[right_key]
        union_edges = left["edges"] | right["edges"]
        union_vertices = left["vertices"] | right["vertices"]
        expected_decorations = {
            edge: (left["gains"].get(edge), right["gains"].get(edge))
            for edge in union_edges
        }
        zigzag_ok = zigzag_ok and bool(
            record["verified"]
            and record["union_edges"] == union_edges
            and record["union_vertices"] == union_vertices
            and record["endpoint_gain_decorations"] == expected_decorations
        )
        pair_specs.append(("temptation", left_key, right_key))

    expected_events = _event_signatures_from_pairs(pair_specs, rebuilt_graphs)
    reported_events = {
        (
            event["axis"],
            event["kind"],
            event["left_key"],
            event["right_key"],
            event["profile"],
        )
        for event in surface["cooperative_sink_events"]
    }
    events_ok = expected_events == reported_events

    checks = {
        "all_cell_graphs_reconstructed_exactly": graph_agreement,
        "all_budget_inclusions_reverified": budget_ok,
        "all_adjacent_unions_reverified": zigzag_ok,
        "all_cooperative_sink_event_signatures_reverified": events_ok,
        "registered_graph_count_reproduced": len(rebuilt_graphs) == 512 * 2 * 8 * 3,
    }
    return {
        "checks": checks,
        "verified": all(checks.values()),
        "rebuilt_graph_count": len(rebuilt_graphs),
        "reconstructed_event_count": len(expected_events),
    }
