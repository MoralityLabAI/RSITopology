#!/usr/bin/env python3
"""Build the deterministic ASMP-12 v0.3 constructible-survival report."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from functools import lru_cache

import constructible_survival as primary
import verify_constructible_survival as independent


def key_text(key: tuple[object, ...]) -> str:
    return f"catalog={key[0]}|family={key[1]}|T={primary.fraction_text(key[2])}|budget={key[3]}"


def edge_certificate_text(
    entries: tuple[tuple[tuple[int, int, int, int, int], object], ...]
) -> list[dict[str, object]]:
    return [
        {"edge": list(edge), "gain": primary.fraction_text(gain)}
        for edge, gain in entries
    ]


def event_text(event: dict[str, object]) -> dict[str, object]:
    return {
        "axis": event["axis"],
        "kind": event["kind"],
        "profile": list(event["profile"]),
        "left_cell": key_text(event["left_key"]),
        "right_cell": key_text(event["right_key"]),
        "left_margin": primary.fraction_text(event["left_margin"]),
        "right_margin": primary.fraction_text(event["right_margin"]),
        "left_profitable_edges": edge_certificate_text(event["left_profitable_edges"]),
        "right_profitable_edges": edge_certificate_text(event["right_profitable_edges"]),
    }


def canonical_certificates(surface: dict[str, object]) -> dict[str, object]:
    canonical = tuple(tuple(row) for row in primary.V2.V1.canonical_catalog())
    catalog_index = surface["catalogs"].index(canonical)
    events = surface["cooperative_sink_events"]
    selected: dict[str, object] = {}
    for event in events:
        if event["profile"] != (1, 1) or event["left_key"][0] != catalog_index:
            continue
        if (
            event["axis"] == "budget"
            and event["kind"] == "cooperative_sink_death"
            and event["left_key"][1:] == ("pd_order", primary.Fraction(4), 2)
            and event["right_key"][3] == 3
        ):
            selected["budget_death_at_T4"] = event_text(event)
        if (
            event["axis"] == "temptation"
            and event["kind"] == "cooperative_sink_death"
            and event["left_key"][1:] == ("pd_order", primary.Fraction(3), 3)
            and event["right_key"][2] == 4
        ):
            selected["temptation_death_T3_to_T4"] = event_text(event)
    return selected


@lru_cache(maxsize=1)
def build_report() -> dict[str, object]:
    return build_report_from_surface(primary.build_surface())


def _expected_primary_events(
    graphs: dict[tuple[int, str, primary.Fraction, int], dict[str, object]],
) -> tuple[dict[str, object], ...]:
    events: list[dict[str, object]] = []
    for catalog_index in range(512):
        for family in independent.EXPECTED_FAMILIES:
            for temptation in independent.EXPECTED_TEMPTATIONS:
                for left_budget, right_budget in zip(
                    independent.EXPECTED_BUDGETS, independent.EXPECTED_BUDGETS[1:]
                ):
                    left_key = (catalog_index, family, temptation, left_budget)
                    right_key = (catalog_index, family, temptation, right_budget)
                    events.extend(
                        primary.adjacent_sink_events(
                            "budget",
                            left_key,
                            right_key,
                            graphs[left_key],
                            graphs[right_key],
                        )
                    )
            for budget in independent.EXPECTED_BUDGETS:
                for left_temptation, right_temptation in zip(
                    independent.EXPECTED_TEMPTATIONS,
                    independent.EXPECTED_TEMPTATIONS[1:],
                ):
                    left_key = (catalog_index, family, left_temptation, budget)
                    right_key = (catalog_index, family, right_temptation, budget)
                    events.extend(
                        primary.adjacent_sink_events(
                            "temptation",
                            left_key,
                            right_key,
                            graphs[left_key],
                            graphs[right_key],
                        )
                    )
    return tuple(events)


def build_report_from_surface(surface: dict[str, object]) -> dict[str, object]:
    graphs = surface["graphs"]
    budget_maps = surface["graph_maps"]["budget_inclusions"]
    zigzags = surface["graph_maps"]["temptation_adjacent_union_zigzags"]
    events = surface["cooperative_sink_events"]

    expected_keys = independent.expected_graph_keys()
    frozen_registry_gate = bool(
        independent.load_manifest() == independent.expected_manifest()
        and surface["config"]
        == {
            "costs": independent.EXPECTED_COSTS,
            "budgets": independent.EXPECTED_BUDGETS,
            "temptations": independent.EXPECTED_TEMPTATIONS,
            "families": independent.EXPECTED_FAMILIES,
        }
        and surface["catalogs"] == independent.frozen_catalogs()
        and tuple(graphs) == expected_keys
    )
    graph_gate = frozen_registry_gate and all(
        primary.graph_is_typed(graph) and primary.graph_margin_status_valid(graph)
        for graph in graphs.values()
    )
    budget_composition = True
    for catalog_index in range(512):
        for family in primary.FAMILIES:
            for temptation in primary.TEMPTATIONS:
                first = graphs[(catalog_index, family, temptation, 1)]
                last = graphs[(catalog_index, family, temptation, 3)]
                budget_composition = budget_composition and bool(
                    first["vertices"] <= last["vertices"]
                    and first["edges"] <= last["edges"]
                    and all(first["gains"][edge] == last["gains"][edge] for edge in first["edges"])
                )
    expected_budget_pairs = independent.expected_budget_pairs()
    budget_gate = bool(
        tuple((record["left_key"], record["right_key"]) for record in budget_maps)
        == expected_budget_pairs
        and all(
            record
            == primary.budget_inclusion(
                left_key,
                right_key,
                graphs[left_key],
                graphs[right_key],
            )
            for record, (left_key, right_key) in zip(budget_maps, expected_budget_pairs)
        )
        and budget_composition
    )

    relation_counts = Counter(record["relation"] for record in zigzags)
    nonmonotone_count = (
        relation_counts["right_strict_subgraph_of_left"]
        + relation_counts["incomparable_edge_sets"]
    )
    expected_temptation_pairs = independent.expected_temptation_pairs()
    zigzag_gate = bool(
        tuple((record["left_key"], record["right_key"]) for record in zigzags)
        == expected_temptation_pairs
        and all(
            record
            == primary.adjacent_union_zigzag(
                left_key,
                right_key,
                graphs[left_key],
                graphs[right_key],
            )
            for record, (left_key, right_key) in zip(zigzags, expected_temptation_pairs)
        )
        and nonmonotone_count > 0
        and all(
            record["verified_direct_inclusion"] is None
            if record["relation"] == "incomparable_edge_sets"
            else record["verified_direct_inclusion"] is not None
            for record in zigzags
        )
    )

    expected_events = _expected_primary_events(graphs) if frozen_registry_gate else ()
    event_gate = bool(
        events
        and tuple(events) == expected_events
        and all(primary.event_certificate_valid(event) for event in expected_events)
        and {event["axis"] for event in events} == {"budget", "temptation"}
        and {event["kind"] for event in events}
        == {"cooperative_sink_birth", "cooperative_sink_death"}
    )
    independent_result = independent.verify_surface(surface)
    robustness = primary.five_robustness_probes(surface)
    robustness_gate = len(robustness) == 5 and all(
        probe["passed"] for probe in robustness.values()
    )
    gates = {
        "F0_frozen_registry_exact": frozen_registry_gate,
        "U0_every_cell_graph_defined_and_margin_typed": graph_gate,
        "B0_budget_inclusions_and_composition_verified": budget_gate,
        "Z0_adjacent_union_zigzags_typed": zigzag_gate,
        "S0_cooperative_sink_events_separate_and_certified": event_gate,
        "I0_independent_reconstruction": independent_result["verified"],
        "R0_five_robustness_probes": robustness_gate,
    }
    passed = all(gates.values())

    digest = hashlib.sha256()
    for key in sorted(graphs, key=lambda item: (item[0], item[1], item[2], item[3])):
        digest.update(key_text(key).encode("utf-8"))
        digest.update(primary.graph_digest(graphs[key]).encode("ascii"))

    event_counts = Counter((event["axis"], event["kind"]) for event in events)
    return {
        "schema_version": "asmp12_constructible_survival_v0_3_1_report_v1",
        "task_result": {
            "status": (
                "finite_constructible_survival_correspondence_built"
                if passed
                else "instrument_failed"
            ),
            "object_type": (
                "verified budget inclusions plus temptation adjacent-union zigzags "
                "in underlying finite directed graphs"
            ),
            "weighted_cell_graph_count": len(graphs),
            "budget_inclusion_count": len(budget_maps),
            "temptation_zigzag_count": len(zigzags),
            "nonmonotone_temptation_step_count": nonmonotone_count,
            "temptation_relation_counts": dict(sorted(relation_counts.items())),
            "cooperative_sink_event_counts": {
                f"{axis}|{kind}": count
                for (axis, kind), count in sorted(event_counts.items())
            },
            "canonical_event_margin_certificates": (
                canonical_certificates(surface) if event_gate else {}
            ),
            "cell_graph_digest_root": digest.hexdigest(),
        },
        "reliability": {
            "status": "all_registered_gates_passed" if passed else "gate_failure",
            "gates": gates,
            "independent_verifier": independent_result,
            "robustness_probes": {
                name: {
                    key: (
                        primary.fraction_text(value)
                        if isinstance(value, primary.Fraction)
                        else value
                    )
                    for key, value in probe.items()
                    if key != "rows"
                }
                for name, probe in robustness.items()
            },
        },
        "claim_support": {
            "status": (
                "supports_only_the_registered_finite_constructible_correspondence"
                if passed
                else "not_established_due_to_gate_failure"
            ),
            "supported": (
                [
                    "one exact profitable-deviation graph at every registered cell",
                    "verified weighted graph inclusions along the budget axis",
                    "typed adjacent-union zigzags along every temptation step",
                    "separate exact cooperative-sink birth/death and margin certificates",
                ]
                if passed
                else []
            ),
            "not_supported": [
                "an ordinary bifiltration of equilibrium sets",
                "weight-preserving temptation-axis graph maps",
                "homology, barcode, interleaving, or stability-module claims",
                "mixed or unrestricted program equilibria",
                "language-model cooperation or equilibrium selection dynamics",
            ],
        },
        "operation": {
            "status": "deterministic_cpu_exact_report_built",
            "arithmetic": "fractions.Fraction for all payoff, gain, and margin values",
            "gpu_used": False,
            "network_used": False,
            "repository_writes": False,
        },
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["reliability"]["status"] == "all_registered_gates_passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
