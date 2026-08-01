from __future__ import annotations

from registration_fork import (
    CANONICAL_SOURCE,
    RAW_PARTITION,
    SUFFICIENT_PARTITION,
    adaptive_aperiodic_fixture_report,
    adaptive_grammar_lattice_census,
    adaptive_sensor_grammar_census,
    all_mode_partitions,
    canonical_quantifier_audit,
    canonical_quantifier_sensitivity_audit,
    canonical_registry_model_audit,
    continuous_embedding_report,
    exact_language_rows,
    finite_graph_transducer_census,
    general_sensor_grammar_report,
    general_registry_lattice_formula_report,
    golden_mean_registration_report,
    global_registry_scope_audit,
    partition_census,
    registration_fork_report,
    registry_lattice_census,
    singleton_transient_delay_census,
    verification_payload,
)


def test_all_four_mode_partitions_are_exhausted():
    assert len(all_mode_partitions()) == 15
    census = partition_census()
    assert census["pass"]
    assert census["all_block_count_histogram"] == {1: 1, 2: 7, 3: 6, 4: 1}
    assert census["safe_block_count_histogram"] == {2: 1, 3: 2, 4: 1}
    assert census["safe_encoder_controller_pair_count"] == 4


def test_unique_coarsest_safe_partition_is_the_action_sufficient_statistic():
    census = partition_census()
    assert census["unique_minimum_safe_partition"] == [
        list(block) for block in SUFFICIENT_PARTITION
    ]
    assert [list(block) for block in RAW_PARTITION] in census["safe_partitions"]


def test_every_sensor_partition_registry_obeys_lattice_monotonicity():
    report = registry_lattice_census()
    assert report["pass"]
    assert report["all_registries_including_empty"] == 32768
    assert report["nonempty_registries"] == 32767
    assert report["nonempty_registry_histogram"] == {
        "infeasible": 2047,
        "kappa_2": 16384,
        "kappa_3": 12288,
        "kappa_4": 2048,
    }
    assert report["cover_edges"] == 245760
    assert report["strict_cover_edges"] == 26624
    assert not report["monotonicity_failures"]
    assert report["strict_fork_witness"]["raw_kappa"] == 4
    assert report["strict_fork_witness"]["full_kappa"] == 2


def test_stirling_formula_classifies_every_registry_lattice_through_five_modes():
    report = general_registry_lattice_formula_report()
    assert report["pass"]
    assert report["action_shape_rows"] == 18
    assert report["audited_action_partitions"] == 75
    assert report["fixture_matches_complete_census"]
    assert not report["failures"]
    fixture = next(
        row
        for row in report["rows"]
        if row["modes"] == 4 and row["action_block_sizes"] == [2, 2]
    )
    assert fixture["registry_corner_histogram"] == {
        "kappa_2": 16384,
        "kappa_3": 12288,
        "kappa_4": 2048,
    }
    five_mode = next(
        row
        for row in report["rows"]
        if row["modes"] == 5 and row["action_block_sizes"] == [2, 3]
    )
    assert five_mode["safe_partition_histogram"] == {
        "2": 1,
        "3": 4,
        "4": 4,
        "5": 1,
    }
    assert five_mode["infeasible_nonempty_registries"] == 4398046511103
    assert five_mode["strict_cover_edges"] == 2854332185706496


def test_every_disturbance_path_has_the_claimed_exact_language_counts():
    for row in exact_language_rows():
        horizon = row["horizon"]
        assert row["mode_paths"] == 4**horizon
        assert row["raw_read_words"] == 4**horizon
        assert row["computed_read_words"] == 2**horizon
        assert row["write_words"] == 2**horizon
        assert (row["raw_read_bits"], row["computed_read_bits"], row["write_bits"]) == (
            2 * horizon,
            horizon,
            horizon,
        )


def test_sensor_registration_alone_changes_the_exact_capacity_region():
    report = registration_fork_report()
    assert report["pass"]
    assert all(report["shared_invariants"].values())
    assert (
        report["computed_sensor_class"]["closed_asymptotic_region"]
        == "[1,infinity) x [1,infinity)"
    )
    assert (
        report["forced_raw_sensor_class"]["closed_asymptotic_region"]
        == "[2,infinity) x [1,infinity)"
    )
    assert report["registration_changes_region"]
    assert report["computed_sensor_class"]["upstream_normal_form_closed"]
    assert report["computed_sensor_class"]["downstream_normal_form_closed"]
    assert not report["forced_raw_sensor_class"]["upstream_normal_form_closed"]
    assert report["forced_raw_sensor_class"]["downstream_normal_form_closed"]


def test_fork_has_an_exact_unstable_evaluator_normal_embedding():
    report = continuous_embedding_report()
    assert report["pass"]
    assert report["q_values"] == ["0", "0", "1", "1"]
    assert report["normal_multiplier"] == "3/2"
    assert report["tangent_reset_derivative"] == "0"
    assert report["normal_control_derivative"] == "1"
    assert report["correct_safe_paths"] == 4 ** report["replayed_horizon"]
    assert set(report["wrong_control_normal_successors"]) == {"-1", "1"}


def test_general_sensor_grammar_formula_holds_through_five_modes():
    report = general_sensor_grammar_report()
    assert report["pass"]
    assert [row["partitions"] for row in report["rows"]] == [1, 2, 5, 15, 52]
    assert [row["safe_action_sensor_partition_pairs"] for row in report["rows"]] == [
        1,
        3,
        12,
        60,
        358,
    ]
    assert [row["fixed_partition_infeasible_pairs"] for row in report["rows"]] == [
        0,
        1,
        13,
        165,
        2346,
    ]
    assert report["threshold_row_count"] == 340
    assert all(
        row["kappa"] == max(row["action_blocks"], row["minimum_registered_blocks"])
        for row in report["threshold_rows"]
    )


def test_subset_observer_matches_brute_force_on_every_three_mode_graph_case():
    report = finite_graph_transducer_census()
    assert report["pass"]
    assert [row["graphs"] for row in report["rows"]] == [1, 9, 343]
    assert [row["transducer_action_cases"] for row in report["rows"]] == [
        1,
        108,
        60025,
    ]
    assert report["total_cases"] == 60134
    assert report["language_comparisons"] == 12060
    assert not report["mismatches"]


def test_fixed_transducer_first_failure_depth_is_exhaustive():
    report = singleton_transient_delay_census()
    assert report["pass"]
    assert report["total_cases"] == 60134
    assert report["infinitely_safe_cases"] == 37430
    assert report["transient_or_immediate_failure_cases"] == 22704
    assert report["first_failure_histogram"] == {
        1: 10642,
        2: 8406,
        3: 3110,
        4: 534,
        5: 12,
    }
    assert report["maximum_first_failure_horizon"] == 5
    assert report["maximum_safe_finite_horizon"] == 4
    assert report["maximum_delay_witness"] == {
        "modes": 3,
        "graph": [[1], [2], [0, 1]],
        "initial_modes": [0],
        "sensor_partition": [[0, 1, 2]],
        "action_partition": [[0, 1], [2]],
        "first_infeasible_horizon": 5,
        "safe_horizons": [1, 2, 3, 4],
    }
    assert not report["mismatches"]


def test_golden_mean_graph_separates_raw_and_required_action_entropies():
    report = golden_mean_registration_report()
    assert report["pass"]
    assert report["raw_counts"] == [2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
    assert report["action_counts"] == [1] * 12
    assert 0.6942 < report["raw_read_entropy_bits"] < 0.6943
    assert report["write_entropy_bits"] == 0.0
    assert report["forced_raw_region"] == ("[log2(phi),infinity) x [0,infinity)")


def test_adaptive_sensor_grammar_closes_an_aperiodic_entropy_gap():
    report = adaptive_aperiodic_fixture_report()
    assert report["pass"]
    assert report["strongly_connected"]
    assert report["adaptive_read_counts"][:10] == [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    assert report["adaptive_read_counts"] == report["required_action_counts"]
    assert report["fixed_split_read_counts"] == [2**length for length in range(1, 17)]
    assert report["stationary_choices"] == {"belief_{0,2}": 0, "belief_{0,1}": 1}
    assert report["stationary_at_every_horizon"]
    assert report["viable_belief_count"] == 5
    assert report["initial_belief_viable"]
    assert 0.6942 < report["adaptive_read_entropy_bits"] < 0.6943
    assert report["fixed_best_read_entropy_bits"] == 1.0
    assert report["adaptive_region"] == ("[log2(phi),infinity) x [log2(phi),infinity)")
    assert report["best_fixed_region"] == ("[1,infinity) x [log2(phi),infinity)")


def test_every_three_mode_two_partition_grammar_obeys_the_adaptive_bounds():
    report = adaptive_sensor_grammar_census()
    assert report["pass"]
    assert report["cases"] == 120050
    assert report["adaptive_feasible_cases"] == 99524
    assert report["infinitely_viable_cases"] == 99524
    assert report["finite_horizon_only_feasible_cases"] == 0
    assert report["fixed_feasible_cases"] == 97952
    assert report["adaptive_only_feasible_cases"] == 1572
    assert report["strict_finite_horizon_improvements"] == 4863
    assert report["adaptive_matches_action_language_cases"] == 73223
    assert report["maximum_fixed_to_adaptive_ratio"] == "8"
    assert not report["mismatches"]


def test_complete_adaptive_grammar_lattice_is_monotone():
    report = adaptive_grammar_lattice_census()
    assert report["pass"]
    assert report["base_graph_initial_action_cases"] == 12005
    assert report["nonempty_grammar_cases"] == 372155
    assert report["finite_feasible_cases"] == 320930
    assert report["infinitely_viable_cases"] == 320918
    assert report["finite_horizon_only_cases"] == 12
    assert report["action_language_exact_cases"] == 255869
    assert report["cover_edges"] == 960400
    assert report["feasibility_gain_edges"] == 138546
    assert report["viability_gain_edges"] == 138582
    assert report["strict_finite_value_edges"] == 104556
    assert report["maximum_cover_ratio"] == "81"
    assert not report["mismatches"]
    assert len(report["finite_horizon_only_witnesses"]) == 12
    assert {
        witness["first_infeasible_horizon"]
        for witness in report["finite_horizon_only_witnesses"]
    } == {5}
    assert {
        witness["grammar_mask"] for witness in report["finite_horizon_only_witnesses"]
    } == {1}


def test_canonical_source_does_not_select_one_sensor_closure_completion():
    report = canonical_quantifier_audit()
    assert report["pass"]
    assert all(report["source_clauses"].values())
    assert report["closure_clauses"] == {
        "requires_upstream_computation_closure": False,
        "requires_forced_raw_transduction": False,
    }
    assert report["neither_sensor_closure_is_textually_selected"]
    assert report["registrations_have_distinct_exact_regions"]
    assert report["decision"] == "registration_class_underdetermined"


def test_canonical_quantifier_audit_rejects_decision_reversing_mutations():
    report = canonical_quantifier_sensitivity_audit()
    assert report["pass"]
    assert report["mutation_cases"] == 13
    assert len(report["required_clause_deletions"]) == 8
    assert all(report["required_clause_deletions"].values())
    assert len(report["closure_selector_insertions"]) == 4
    assert all(report["closure_selector_insertions"].values())
    assert report["collapsed_regions_rejected"]


def test_two_registry_models_satisfy_every_canonical_obligation():
    report = canonical_registry_model_audit()
    assert report["pass"]
    assert report["source_obligation_count"] == 13
    assert all(report["source_obligations"].values())
    assert not report["registry_domain_selected"]
    assert report["registry_predicate_is_undefined"]
    assert report["all_models_satisfy_source"]
    assert report["models_have_distinct_exact_regions"]
    assert report["existential_region_depends_on_registry_predicate"]
    assert report["decision"] == "two_source_models_with_distinct_regions"
    assert {
        name: model["closed_asymptotic_region"]
        for name, model in report["models"].items()
    } == {
        "computed_sensor_registry": "[1,infinity) x [1,infinity)",
        "fixed_raw_sensor_registry": "[2,infinity) x [1,infinity)",
    }
    for model in report["models"].values():
        assert model["pass"]
        assert model["safe_code_exists"]
        assert len(model["obligation_satisfaction"]) == 13
        assert all(model["obligation_satisfaction"].values())


def test_no_global_normative_source_defines_the_registered_code_domain():
    report = global_registry_scope_audit()
    assert report["pass"]
    assert report["registered_occurrence_count"] == 31
    assert report["domain_defining_occurrence_count"] == 0
    assert report["no_global_domain_definition"]
    assert report["normative_scope_remains_the_markdown_draft"]
    assert all(report["graduation_fragments"].values())
    assert all(report["index_checks"].values())
    assert report["decision"] == ("global_sources_do_not_select_registered_code_domain")

    source = CANONICAL_SOURCE.read_text(encoding="utf-8")
    mutated = global_registry_scope_audit(
        source_text=f"{source}\n\nAll causal sensor encoders are registered.\n"
    )
    assert not mutated["pass"]
    assert mutated["domain_defining_occurrence_count"] == 1
    assert not mutated["no_global_domain_definition"]


def test_every_registration_fork_gate_passes():
    payload = verification_payload()
    assert payload["pass"]
    assert all(payload["gates"].values())
