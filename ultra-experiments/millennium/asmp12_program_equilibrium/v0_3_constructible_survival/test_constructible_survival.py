from fractions import Fraction

import pytest

import build_artifacts as artifacts
import constructible_survival as primary
import run_constructible_survival as runner
import verify_constructible_survival as independent


@pytest.fixture(scope="module")
def surface():
    return primary.build_surface()


@pytest.fixture(scope="module")
def report():
    return runner.build_report()


def test_profitable_deviation_graph_and_signed_margin_are_exact():
    catalog = primary.V2.V1.canonical_catalog()
    graph_at = primary.build_graph(catalog, "pd_order", Fraction(3), primary.COSTS, 3)
    graph_above = primary.build_graph(
        catalog, "pd_order", Fraction(301, 100), primary.COSTS, 3
    )
    assert primary.graph_is_typed(graph_at)
    assert primary.graph_margin_status_valid(graph_at)
    assert graph_at["margins"][(1, 1)] == 0
    assert (1, 1) in graph_at["cooperative_sinks"]
    assert graph_above["margins"][(1, 1)] == Fraction(-1, 100)
    assert (1, 1) not in graph_above["sinks"]
    assert any(edge[:2] == (1, 1) for edge in graph_above["edges"])


def test_every_registered_cell_has_a_typed_graph(surface):
    assert independent.load_manifest() == independent.expected_manifest()
    assert len(surface["catalogs"]) == 512
    assert len(surface["graphs"]) == 512 * 2 * 8 * 3
    assert all(primary.graph_is_typed(graph) for graph in surface["graphs"].values())
    assert all(
        primary.graph_margin_status_valid(graph) for graph in surface["graphs"].values()
    )


def test_budget_inclusions_are_claimed_only_after_exact_verification(surface):
    records = surface["graph_maps"]["budget_inclusions"]
    assert len(records) == 512 * 2 * 8 * 2
    assert all(record["verified"] for record in records)
    assert all(record["old_edge_gains_preserved"] for record in records)


def test_adjacent_temptation_unions_form_typed_zigzags(surface):
    records = surface["graph_maps"]["temptation_adjacent_union_zigzags"]
    assert len(records) == 512 * 2 * 7 * 3
    assert all(record["verified"] for record in records)
    nonmonotone = [
        record
        for record in records
        if record["relation"] in {"right_strict_subgraph_of_left", "incomparable_edge_sets"}
    ]
    assert nonmonotone
    assert all(
        record["verified_direct_inclusion"] is None
        for record in records
        if record["relation"] == "incomparable_edge_sets"
    )
    assert all(record["arrows"] == ("left_to_union", "right_to_union") for record in records)


def test_cooperative_sink_events_are_separate_and_have_exact_certificates(surface):
    assert "cooperative_sink_events" in surface
    assert "cooperative_sink_events" not in surface["graph_maps"]
    events = surface["cooperative_sink_events"]
    assert events
    assert all(primary.event_certificate_valid(event) for event in events)
    canonical = runner.canonical_certificates(surface)
    assert set(canonical) == {"budget_death_at_T4", "temptation_death_T3_to_T4"}
    assert canonical["budget_death_at_T4"]["left_margin"] == "2"
    assert canonical["budget_death_at_T4"]["right_margin"] == "-1"
    assert canonical["temptation_death_T3_to_T4"]["left_margin"] == "0"
    assert canonical["temptation_death_T3_to_T4"]["right_margin"] == "-1"


def test_independent_verifier_reconstructs_graphs_maps_zigzags_and_events(surface):
    verification = independent.verify_surface(surface)
    assert verification["rebuilt_graph_count"] == 512 * 2 * 8 * 3
    assert verification["reconstructed_budget_map_count"] == 512 * 2 * 8 * 2
    assert verification["reconstructed_temptation_zigzag_count"] == 512 * 2 * 7 * 3
    assert all(verification["checks"].values())
    assert verification["verified"]


def test_frozen_registry_and_exact_records_reject_stale_green_mutations(surface):
    mutated_config = dict(surface)
    mutated_config["config"] = dict(surface["config"])
    mutated_config["config"]["temptations"] = tuple(
        Fraction(99) if value == 5 else value for value in surface["config"]["temptations"]
    )
    config_check = independent.verify_surface(mutated_config)
    assert not config_check["checks"]["frozen_config_matches"]
    assert not config_check["verified"]

    mutated_catalogs = dict(surface)
    catalogs = list(surface["catalogs"])
    catalogs[0] = catalogs[1]
    mutated_catalogs["catalogs"] = tuple(catalogs)
    catalog_check = independent.verify_surface(mutated_catalogs)
    assert not catalog_check["checks"]["frozen_catalog_sequence_matches"]
    assert not catalog_check["verified"]

    mutated_adjacency = dict(surface)
    mutated_adjacency["graph_maps"] = dict(surface["graph_maps"])
    zigzags = list(surface["graph_maps"]["temptation_adjacent_union_zigzags"])
    zigzags[0] = zigzags[1]
    mutated_adjacency["graph_maps"]["temptation_adjacent_union_zigzags"] = tuple(zigzags)
    adjacency_check = independent.verify_surface(mutated_adjacency)
    assert not adjacency_check["checks"]["complete_temptation_adjacency_registry"]
    assert not adjacency_check["verified"]

    mutated_payload = dict(surface)
    mutated_payload["graph_maps"] = dict(surface["graph_maps"])
    zigzags = list(surface["graph_maps"]["temptation_adjacent_union_zigzags"])
    zigzags[0] = dict(zigzags[0], relation="left_strict_subgraph_of_right")
    mutated_payload["graph_maps"]["temptation_adjacent_union_zigzags"] = tuple(zigzags)
    events = list(surface["cooperative_sink_events"])
    events[0] = dict(events[0], right_margin=Fraction(-999))
    mutated_payload["cooperative_sink_events"] = tuple(events)
    payload_check = independent.verify_surface(mutated_payload)
    assert not payload_check["checks"][
        "all_adjacent_unions_relations_and_decorations_reverified"
    ]
    assert not payload_check["checks"][
        "all_cooperative_sink_event_records_reverified_exactly"
    ]
    assert not payload_check["verified"]

    failed_report = runner.build_report_from_surface(mutated_payload)
    assert failed_report["task_result"]["status"] == "instrument_failed"
    assert failed_report["claim_support"]["status"] == "not_established_due_to_gate_failure"
    assert not failed_report["claim_support"]["supported"]
    assert not failed_report["reliability"]["gates"]["Z0_adjacent_union_zigzags_typed"]
    assert not failed_report["reliability"]["gates"][
        "S0_cooperative_sink_events_separate_and_certified"
    ]


def test_five_robustness_probes_pass(surface):
    probes = primary.five_robustness_probes(surface)
    assert set(probes) == {
        "cost_padding_replay",
        "program_label_equivariance",
        "source_blind_column_permutation_null",
        "exact_boundary_microgrid",
        "positive_margin_payoff_perturbation",
    }
    assert all(probe["passed"] for probe in probes.values())


def test_evidence_root_binds_registries_maps_events_and_probes(surface, report):
    roots = artifacts.evidence_roots(surface, report)
    assert set(roots) == {
        "manifest",
        "catalog_sequence",
        "graph_key_registry",
        "cell_graphs",
        "budget_maps",
        "temptation_zigzags",
        "cooperative_sink_events",
        "robustness_probes",
        "root_of_roots",
    }
    assert all(len(value) == 64 for value in roots.values())
    zigzags = list(surface["graph_maps"]["temptation_adjacent_union_zigzags"])
    zigzags[0] = dict(zigzags[0], relation="left_strict_subgraph_of_right")
    assert artifacts.digest_value(tuple(zigzags)) != roots["temptation_zigzags"]


def test_report_has_four_distinct_conclusion_layers(report):
    assert set(report) == {
        "schema_version",
        "task_result",
        "reliability",
        "claim_support",
        "operation",
    }
    assert report["task_result"]["status"] == (
        "finite_constructible_survival_correspondence_built"
    )
    assert all(report["reliability"]["gates"].values())
    assert report["claim_support"]["status"] == (
        "supports_only_the_registered_finite_constructible_correspondence"
    )
    assert report["operation"]["gpu_used"] is False
    assert report["operation"]["network_used"] is False
    assert report["operation"]["repository_writes"] is False
