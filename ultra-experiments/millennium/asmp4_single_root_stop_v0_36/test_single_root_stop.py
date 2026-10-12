from single_root_stop import (
    MISSING_SELECTORS,
    claim_payload,
    conditional_chain_report,
    dependency_report,
    full_report,
    material_fork_report,
    mutation_report,
    predecessor_inventory_report,
    registration_field_report,
    resource_integrity_report,
    stop_certificate_report,
    stopping_decision,
    truth_table_report,
    canonical_requirements_report,
)


def test_six_sealed_resources_match_exactly() -> None:
    report = resource_integrity_report()
    assert report["pass"]
    assert report["resources"] == 6
    assert all(row["expected"] == row["observed"] for row in report["rows"])


def test_five_canonical_requirements_are_parsed_in_order() -> None:
    report = canonical_requirements_report()
    assert report["pass"]
    assert len(report["requirements"]) == 5
    assert "entire achievable rate region" in report["requirements"][1]


def test_registration_phrases_do_not_supply_domain_selectors() -> None:
    report = registration_field_report()
    assert report["pass"]
    assert all(report["explicit"].values())
    assert tuple(report["missing"]) == MISSING_SELECTORS
    assert all(report["missing"].values())


def test_two_unselected_semantic_forks_change_the_target() -> None:
    report = material_fork_report()
    assert report["pass"]
    assert report["computed_region"] == "[1,infinity) x [1,infinity)"
    assert report["raw_region"] == "[2,infinity) x [1,infinity)"
    assert report["computed_region"] != report["raw_region"]


def test_conditional_theorem_chain_covers_each_requirement() -> None:
    report = conditional_chain_report()
    assert report["pass"]
    assert len(report["rows"]) == 5
    assert {row["requirement"] for row in report["rows"]} == {1, 2, 3, 4, 5}
    assert len({row["canonical_gap"] for row in report["rows"]}) == 1


def test_dependency_graph_has_one_unresolved_root() -> None:
    report = dependency_report()
    assert report["pass"]
    assert report["unresolved_roots"] == ("formal_normative_registry",)
    assert report["nodes"]["robust_public_reset_atlas"]


def test_stop_predicate_and_full_truth_table_are_exact() -> None:
    assert stopping_decision(True, True, True, False, False)
    assert not stopping_decision(False, True, True, False, False)
    assert not stopping_decision(True, True, True, True, False)
    report = truth_table_report()
    assert report["pass"]
    assert (report["rows"], report["stop_rows"]) == (32, 1)


def test_stop_certificate_has_four_real_reopening_conditions() -> None:
    report = stop_certificate_report()
    assert report["pass"]
    assert report["decision"] == "stop_autonomous_asmp4_work_pending_semantic_input"
    assert len(report["reopening_conditions"]) == 4
    assert "not an impossibility theorem" in report["nonclaim"]


def test_mutations_and_predecessor_inventory_are_frozen() -> None:
    mutations = mutation_report()
    inventory = predecessor_inventory_report()
    assert mutations["pass"] and mutations["cases"] == mutations["rejected"] == 8
    assert inventory["pass"]
    assert (inventory["packages"], inventory["tests"]) == (36, 394)


def test_exact_claim_and_complete_report_pass() -> None:
    report = full_report()
    assert report["pass"]
    assert report["claim"]["pass"]
    assert report["payload"]["missing"] == []
    assert claim_payload()["stopping_logic"] == {
        "truth_table_rows": 32,
        "stop_rows": 1,
        "reopening_conditions": 4,
    }
