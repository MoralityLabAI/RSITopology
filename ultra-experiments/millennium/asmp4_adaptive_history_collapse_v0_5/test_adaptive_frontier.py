from fractions import Fraction

from adaptive_frontier import (
    adaptive_action_universe,
    adaptive_bellman_report,
    action_universe_report,
    causal_signatures,
    competing_cycle_mean_payoff_report,
    deadline_codebook_sets,
    exhaustive_two_block_strategy_report,
    finite_iid_alphabet_report,
    full_binary_length_profiles,
    general_probability_phase_report,
    labelled_deadline_codebooks,
    logarithmic_slack_report,
    markov_common_history_guard_report,
    reveal_signature,
    stationary_predictor_rectangle_report,
    stationary_renewal_source_report,
    threshold_policy_exact,
    two_block_adaptive_witness_report,
    variable_support_mean_payoff_report,
    vanishing_maximum_guard_report,
    verification_payload,
)


def test_complete_deadline_codebook_universe_counts():
    assert len(deadline_codebook_sets()) == 207
    assert len(labelled_deadline_codebooks()) == 4968


def test_causal_partition_factorization_accepts_identity_and_rejects_mixed_shapes():
    huffman = ("0", "10", "110", "111")
    balanced = ("00", "01", "10", "11")
    h_signature = reveal_signature(huffman)
    b_signature = reveal_signature(balanced)
    assert causal_signatures(h_signature, h_signature)
    assert causal_signatures(b_signature, b_signature)
    assert not causal_signatures(h_signature, b_signature)
    assert not causal_signatures(b_signature, h_signature)


def test_all_250_actions_reduce_to_the_exact_thirteen_minimal_signatures():
    universe = adaptive_action_universe()
    assert len(universe["action_signatures"]) == 250
    assert universe["causal_partition_pairs"] == 72
    assert universe["coordinatewise_minima"] == (
        (Fraction(7, 4), (1, 2, 3, 3)),
        (Fraction(15, 8), (1, 3, 2, 3)),
        (Fraction(15, 8), (1, 3, 3, 2)),
        (Fraction(2), (2, 1, 3, 3)),
        (Fraction(2), (2, 2, 2, 2)),
        (Fraction(9, 4), (2, 3, 1, 3)),
        (Fraction(9, 4), (2, 3, 3, 1)),
        (Fraction(19, 8), (3, 1, 2, 3)),
        (Fraction(19, 8), (3, 1, 3, 2)),
        (Fraction(5, 2), (3, 2, 1, 3)),
        (Fraction(5, 2), (3, 2, 3, 1)),
        (Fraction(21, 8), (3, 3, 1, 2)),
        (Fraction(21, 8), (3, 3, 2, 1)),
    )
    assert action_universe_report()["pass"]


def test_exact_bellman_frontier_starts_with_the_registered_values():
    report = adaptive_bellman_report(max_blocks=4)
    values = [
        [
            point["minimum_expected_read"]["exact"]
            for point in horizon["frontier_points"]
        ]
        for horizon in report["horizons"]
    ]
    assert values == [
        ["2", "7/4"],
        ["4", "57/16", "7/2"],
        ["6", "345/64", "337/64", "21/4"],
        ["8", "1851/256", "901/128", "1793/256", "7"],
    ]
    assert all(
        horizon["guard_is_optimal_at_every_budget"] for horizon in report["horizons"]
    )
    assert report["pass"]


def test_two_block_adaptation_strictly_beats_every_fixed_schedule_at_write_five():
    report = two_block_adaptive_witness_report()
    assert report["pass"]
    assert report["histories_replayed"] == 16
    assert report["expected_read_total"]["exact"] == "57/16"
    assert report["worst_write_total"] == 5
    assert report["strict_read_gain"]["exact"] == "3/16"


def test_every_two_block_minimal_action_tree_reproduces_the_bellman_frontier():
    report = exhaustive_two_block_strategy_report()
    assert report["pass"]
    assert report["strategy_trees"] == 371293
    assert report["aggregate_cost_points"] == 188
    assert [
        (row["expected_read_total"]["exact"], row["worst_write_total"])
        for row in report["pareto_minima"]
    ] == [("7/2", 6), ("57/16", 5), ("4", 4)]


def test_threshold_policy_obeys_the_pathwise_budget_and_martingale_bound():
    report = threshold_policy_exact(blocks=16, slack=4)
    assert report["worst_write_total"] == 36
    assert report["hitting_probability"]["exact"] == "179050151/4294967296"
    assert report["doob_hitting_bound"]["exact"] == "1/16"
    assert report["bounds_hold"]


def test_logarithmic_slack_certifies_the_asymptotic_lower_corner():
    report = logarithmic_slack_report()
    assert report["pass"]
    assert report["martingale_factor"] == "1"
    assert report["read_rate_limit_per_tick"] == "7/12"
    assert report["write_rate_limit_per_tick"] == "2/3"
    assert [row["slack"] for row in report["rows"]] == [1, 2, 3, 4, 5, 6]


def test_every_ordered_four_plan_phase_has_an_adaptive_rectangle():
    report = general_probability_phase_report()
    assert report["pass"]
    assert (
        report["laws"],
        report["skew_laws"],
        report["boundary_laws"],
        report["balanced_laws"],
    ) == (34, 27, 2, 5)
    assert all(
        row["martingale_factor"] == "1" and Fraction(row["exponential_multiplier"]) > 1
        for row in report["rows"]
        if row["phase"] == "skew"
    )


def test_general_finite_iid_alphabets_have_the_predicted_rectangle():
    assert [len(full_binary_length_profiles(plans)) for plans in range(2, 7)] == [
        1,
        1,
        2,
        3,
        5,
    ]
    report = finite_iid_alphabet_report()
    assert report["pass"]
    assert report["laws"] == 57
    assert report["construction_counts"] == {
        "fixed_equal": 10,
        "direct": 21,
        "guard": 26,
    }
    assert all(
        Fraction(row["supermartingale_factor"]) < 1
        for row in report["rows"]
        if row["construction"] == "guard"
    )


def test_correlated_markov_source_satisfies_the_conditional_mgf_guard():
    report = markov_common_history_guard_report()
    assert report["pass"]
    assert report["correlation_witness"] == {
        "P_next_0_given_0": "1/2",
        "P_next_0_given_1": "1/8",
    }
    assert report["matches_iid_length_process"]
    assert all(
        row["conditional_factor"] == "1" for row in report["conditional_mgf_rows"]
    )


def test_negative_drift_guard_works_without_a_uniform_one_step_mgf():
    report = vanishing_maximum_guard_report()
    assert report["pass"]
    assert not report["uniform_one_step_mgf_hypothesis_holds"]
    assert report["strong_law_surplus_rate"] == "-1/8"
    assert report["fast_read_rate_limit"] == "15/8"
    assert report["write_rate_limit"] == "2"
    assert [row["blocks"] for row in report["rows"]] == [16, 32, 64, 128]
    assert [row["slack"] for row in report["rows"]] == [4, 6, 8, 12]
    assert all(
        Fraction(value) > 1 for value in report["sampled_weak_factors_at_lambda_2"]
    )


def test_stationary_ergodic_source_separates_negative_drift_from_uniform_mgf():
    report = stationary_renewal_source_report()
    assert report["pass"]
    assert report["uniform_reset_probability_lower_bound"] == "3/8"
    assert report["positive_recurrent"]
    assert report["aperiodic"]
    assert report["irreducible"]
    assert report["conditional_huffman_optimal"]
    assert not report["uniform_one_step_mgf_hypothesis_holds"]
    read_interval = report["stationary_read_rate_interval"]
    assert 1.81618644 < read_interval["lower"]["float"]
    assert read_interval["upper"]["float"] < 1.81618645
    assert report["write_rate_limit"] == "2"


def test_stationary_ergodic_public_predictors_have_the_general_rectangle():
    report = stationary_predictor_rectangle_report()
    assert report["pass"]
    assert report["profile_counts"] == {
        2: 1,
        3: 1,
        4: 2,
        5: 3,
        6: 5,
        7: 9,
        8: 16,
    }
    assert report["closed_region"] == ("[h_H,infinity) x [ceil(log2 m),infinity)")
    assert {fixture["mode"] for fixture in report["fixtures"]} == {
        "negative_drift_guard",
        "uniform_mgf_guard",
        "vanishing_maximum_guard",
        "fixed_equal",
    }


def test_variable_support_predictor_has_the_mean_payoff_rectangle():
    report = variable_support_mean_payoff_report()
    assert report["pass"]
    assert report["write_policy_count"] == 13
    assert report["write_value_counts"] == {"3/2": 1, "2": 12}
    assert report["optimal_write_policy"]["state_a_lengths"] == (2, 2, 2, 2)
    assert report["read_threshold"] == "11/8"
    assert report["write_threshold"] == "3/2"
    assert report["closed_region"] == "[11/8,infinity) x [3/2,infinity)"
    assert report["guard_replay"]["matches_iid_active_round_guard"]


def test_competing_cycles_require_distinct_read_and_write_optimal_codes():
    report = competing_cycle_mean_payoff_report()
    assert report["pass"]
    assert report["write_value_counts"] == {"5/3": 3, "2": 4, "3": 6}
    assert report["fast_huffman_lengths"] == (2, 1, 3, 3)
    assert report["selected_worst_optimal_lengths"] == (1, 2, 3, 3)
    assert report["read_threshold"] == "13/10"
    assert report["write_threshold"] == "5/3"
    assert report["closed_region"] == "[13/10,infinity) x [5/3,infinity)"
    assert report["conditional_mgf_factor_at_lambda_2"] == "1"
    assert report["guard_replay"]["finite_transient_excess"]["exact"] == "4/3"


def test_competing_cycle_bellman_potential_certifies_arbitrary_history_value():
    certificate = competing_cycle_mean_payoff_report()["bellman_certificate"]
    assert certificate["pass"]
    assert certificate["rho"] == "5/3"
    assert certificate["potential"] == ["0", "-4/3", "-2/3"]
    assert certificate["state_targets"] == ["5/3", "1/3", "1"]
    assert certificate["shapley_values"] == certificate["state_targets"]
    assert certificate["action_score_counts"] == {"5/3": 3, "2": 4, "3": 6}
    assert certificate["baseline_edge_values"] == {
        "A": ["1", "2/3", "5/3", "5/3"],
        "B": ["1/3"],
        "C": ["1"],
    }
    assert certificate["upper_policy_certificate"]
    assert certificate["arbitrary_history_lower_certificate"]
    assert certificate["potential_span"] == "4/3"


def test_every_adaptive_verification_gate_passes():
    payload = verification_payload()
    assert payload["pass"]
    assert all(payload["gates"].values())
