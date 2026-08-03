from fractions import Fraction

import pytest

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
    assert all(verification["checks"].values())
    assert verification["verified"]


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
