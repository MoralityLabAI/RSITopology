#!/usr/bin/env python3
"""Import-independent exact verifier for the ASMP-12 v0.3 registry.

The verifier owns a second encoding of the frozen registry. It reconstructs
the ordered catalog universe, every graph key, both adjacency registries, all
cell graphs, every union relation/decorated edge, and every complete sink-event
record. It never treats a supplied count or primary ``verified`` flag as a
substitute for registry membership or exact replay.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
from typing import Sequence


EXPECTED_COSTS = (1, 2, 3)
EXPECTED_BUDGETS = (1, 2, 3)
EXPECTED_TEMPTATIONS = tuple(
    Fraction(value) for value in (0, Fraction(1, 2), 1, 2, 3, 4, 5, 6)
)
EXPECTED_FAMILIES = {
    "pd_order": {"R": Fraction(3), "S": Fraction(0), "P": Fraction(1)},
    "chicken_order": {"R": Fraction(3), "S": Fraction(1), "P": Fraction(0)},
}
HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "protocol_v0_3_1.json"


def expected_manifest() -> dict[str, object]:
    return {
        "schema_version": "asmp12_constructible_survival_protocol_v0_3_1",
        "protocol_id": "ASMP12-CONSTRUCTIBLE-SURVIVAL-v0.3.1",
        "catalogs": {
            "alphabet": [0, 1],
            "shape": [3, 3],
            "order": "lexicographic_row_major_product",
            "count": 512,
            "canonical_sha256": "8b3e2a44c4cddca770554dada7b89ebdd41f835a6a59c85b8647a458c61358c1",
        },
        "costs": [1, 2, 3],
        "budgets": [1, 2, 3],
        "temptations": ["0", "1/2", "1", "2", "3", "4", "5", "6"],
        "families": {
            "pd_order": {"R": "3", "S": "0", "P": "1"},
            "chicken_order": {"R": "3", "S": "1", "P": "0"},
        },
        "expected_counts": {
            "graphs": 24576,
            "budget_adjacencies": 16384,
            "temptation_adjacencies": 21504,
        },
        "claim_boundary": "finite_exact_pure_strategy_graph_correspondence_only",
    }


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def frozen_catalogs() -> tuple[tuple[tuple[int, ...], ...], ...]:
    """Return the exact ordered universe of all binary 3x3 source tables."""

    return tuple(
        tuple(tuple(bits[3 * row + column] for column in range(3)) for row in range(3))
        for bits in product((0, 1), repeat=9)
    )


def expected_graph_keys() -> tuple[tuple[int, str, Fraction, int], ...]:
    return tuple(
        (catalog_index, family, temptation, budget)
        for catalog_index in range(512)
        for family in EXPECTED_FAMILIES
        for temptation in EXPECTED_TEMPTATIONS
        for budget in EXPECTED_BUDGETS
    )


def expected_budget_pairs() -> tuple[
    tuple[tuple[int, str, Fraction, int], tuple[int, str, Fraction, int]], ...
]:
    return tuple(
        (
            (catalog_index, family, temptation, left_budget),
            (catalog_index, family, temptation, right_budget),
        )
        for catalog_index in range(512)
        for family in EXPECTED_FAMILIES
        for temptation in EXPECTED_TEMPTATIONS
        for left_budget, right_budget in zip(EXPECTED_BUDGETS, EXPECTED_BUDGETS[1:])
    )


def expected_temptation_pairs() -> tuple[
    tuple[tuple[int, str, Fraction, int], tuple[int, str, Fraction, int]], ...
]:
    return tuple(
        (
            (catalog_index, family, left_temptation, budget),
            (catalog_index, family, right_temptation, budget),
        )
        for catalog_index in range(512)
        for family in EXPECTED_FAMILIES
        for budget in EXPECTED_BUDGETS
        for left_temptation, right_temptation in zip(
            EXPECTED_TEMPTATIONS, EXPECTED_TEMPTATIONS[1:]
        )
    )


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
        vertex for vertex in vertices if not any(edge[:2] == vertex for edge in edges)
    )
    cooperative_sinks = frozenset(
        vertex for vertex in sinks if _actions(catalog, *vertex) == (1, 1)
    )
    return {
        "programs": programs,
        "vertices": vertices,
        "edges": frozenset(edges),
        "gains": gains,
        "margins": margins,
        "sinks": sinks,
        "cooperative_sinks": cooperative_sinks,
    }


def _matches(primary: dict[str, object], rebuilt: dict[str, object]) -> bool:
    fields = (
        "programs",
        "vertices",
        "edges",
        "gains",
        "margins",
        "sinks",
        "cooperative_sinks",
    )
    return all(primary.get(field) == rebuilt[field] for field in fields)


def _budget_record(
    left_key: tuple[int, str, Fraction, int],
    right_key: tuple[int, str, Fraction, int],
    left: dict[str, object],
    right: dict[str, object],
) -> dict[str, object]:
    vertices_included = left["vertices"] <= right["vertices"]
    edges_included = left["edges"] <= right["edges"]
    gains_preserved = edges_included and all(
        left["gains"][edge] == right["gains"][edge] for edge in left["edges"]
    )
    same_fiber = left_key[:3] == right_key[:3] and right_key[3] == left_key[3] + 1
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


def _zigzag_record(
    left_key: tuple[int, str, Fraction, int],
    right_key: tuple[int, str, Fraction, int],
    left: dict[str, object],
    right: dict[str, object],
) -> dict[str, object]:
    union_vertices = frozenset(left["vertices"] | right["vertices"])
    union_edges = frozenset(left["edges"] | right["edges"])
    decorations = {
        edge: (left["gains"].get(edge), right["gains"].get(edge))
        for edge in union_edges
    }
    typed_union = all(
        (edge[0], edge[1]) in union_vertices and (edge[2], edge[3]) in union_vertices
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
    same_fiber = (
        left_key[0] == right_key[0]
        and left_key[1] == right_key[1]
        and left_key[3] == right_key[3]
        and (left_key[2], right_key[2])
        in set(zip(EXPECTED_TEMPTATIONS, EXPECTED_TEMPTATIONS[1:]))
    )
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


def _outgoing(graph: dict[str, object], profile: tuple[int, int]):
    return tuple(sorted(edge for edge in graph["edges"] if edge[:2] == profile))


def _event_record(
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
    left_outgoing = _outgoing(left, profile) if left_exists else ()
    right_outgoing = _outgoing(right, profile) if right_exists else ()
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
        "left_profitable_edges": tuple((edge, left["gains"][edge]) for edge in left_outgoing),
        "right_profitable_edges": tuple(
            (edge, right["gains"][edge]) for edge in right_outgoing
        ),
    }


def _pair_events(
    axis: str,
    left_key: tuple[int, str, Fraction, int],
    right_key: tuple[int, str, Fraction, int],
    graphs: dict[tuple[int, str, Fraction, int], dict[str, object]],
) -> tuple[dict[str, object], ...]:
    left = graphs[left_key]
    right = graphs[right_key]
    events = []
    for profile in sorted(left["cooperative_sinks"] - right["cooperative_sinks"]):
        events.append(
            _event_record(
                axis, "cooperative_sink_death", profile, left_key, right_key, left, right
            )
        )
    for profile in sorted(right["cooperative_sinks"] - left["cooperative_sinks"]):
        events.append(
            _event_record(
                axis, "cooperative_sink_birth", profile, left_key, right_key, left, right
            )
        )
    return tuple(events)


def _expected_events(
    graphs: dict[tuple[int, str, Fraction, int], dict[str, object]],
) -> tuple[dict[str, object], ...]:
    events = []
    budget_pairs = iter(expected_budget_pairs())
    temptation_pairs = iter(expected_temptation_pairs())
    for _catalog_index in range(512):
        for _family in EXPECTED_FAMILIES:
            for _temptation in EXPECTED_TEMPTATIONS:
                for _ in range(len(EXPECTED_BUDGETS) - 1):
                    left_key, right_key = next(budget_pairs)
                    events.extend(_pair_events("budget", left_key, right_key, graphs))
            for _budget in EXPECTED_BUDGETS:
                for _ in range(len(EXPECTED_TEMPTATIONS) - 1):
                    left_key, right_key = next(temptation_pairs)
                    events.extend(_pair_events("temptation", left_key, right_key, graphs))
    return tuple(events)


def verify_surface(surface: dict[str, object]) -> dict[str, object]:
    expected_catalog_sequence = frozen_catalogs()
    expected_keys = expected_graph_keys()
    expected_key_set = set(expected_keys)
    config = surface.get("config", {})
    catalogs = surface.get("catalogs", ())
    primary_graphs = surface.get("graphs", {})
    graph_maps = surface.get("graph_maps", {})
    budget_maps = tuple(graph_maps.get("budget_inclusions", ()))
    zigzags = tuple(graph_maps.get("temptation_adjacent_union_zigzags", ()))

    config_ok = config == {
        "costs": EXPECTED_COSTS,
        "budgets": EXPECTED_BUDGETS,
        "temptations": EXPECTED_TEMPTATIONS,
        "families": EXPECTED_FAMILIES,
    }
    catalogs_ok = catalogs == expected_catalog_sequence
    key_registry_ok = set(primary_graphs) == expected_key_set and len(primary_graphs) == len(
        expected_keys
    )

    rebuilt_graphs = {
        key: rebuild_graph(
            expected_catalog_sequence[key[0]],
            EXPECTED_FAMILIES[key[1]],
            key[2],
            EXPECTED_COSTS,
            key[3],
        )
        for key in expected_keys
    }
    graph_agreement = key_registry_ok and all(
        _matches(primary_graphs[key], rebuilt_graphs[key]) for key in expected_keys
    )

    budget_pairs = expected_budget_pairs()
    reported_budget_pairs = tuple((row.get("left_key"), row.get("right_key")) for row in budget_maps)
    budget_registry_ok = reported_budget_pairs == budget_pairs
    budget_exact = budget_registry_ok and all(
        record == _budget_record(left_key, right_key, rebuilt_graphs[left_key], rebuilt_graphs[right_key])
        for record, (left_key, right_key) in zip(budget_maps, budget_pairs)
    )

    temptation_pairs = expected_temptation_pairs()
    reported_temptation_pairs = tuple(
        (row.get("left_key"), row.get("right_key")) for row in zigzags
    )
    temptation_registry_ok = reported_temptation_pairs == temptation_pairs
    zigzag_exact = temptation_registry_ok and all(
        record == _zigzag_record(
            left_key, right_key, rebuilt_graphs[left_key], rebuilt_graphs[right_key]
        )
        for record, (left_key, right_key) in zip(zigzags, temptation_pairs)
    )

    expected_events = _expected_events(rebuilt_graphs)
    reported_events = tuple(surface.get("cooperative_sink_events", ()))
    events_exact = reported_events == expected_events

    checks = {
        "frozen_manifest_matches": load_manifest() == expected_manifest(),
        "frozen_config_matches": config_ok,
        "frozen_catalog_sequence_matches": catalogs_ok,
        "complete_graph_key_registry": key_registry_ok,
        "all_cell_graphs_reconstructed_exactly": graph_agreement,
        "complete_budget_adjacency_registry": budget_registry_ok,
        "all_budget_inclusions_reverified_exactly": budget_exact,
        "complete_temptation_adjacency_registry": temptation_registry_ok,
        "all_adjacent_unions_relations_and_decorations_reverified": zigzag_exact,
        "all_cooperative_sink_event_records_reverified_exactly": events_exact,
    }
    return {
        "checks": checks,
        "verified": all(checks.values()),
        "rebuilt_graph_count": len(rebuilt_graphs),
        "reconstructed_budget_map_count": len(budget_pairs),
        "reconstructed_temptation_zigzag_count": len(temptation_pairs),
        "reconstructed_event_count": len(expected_events),
    }
