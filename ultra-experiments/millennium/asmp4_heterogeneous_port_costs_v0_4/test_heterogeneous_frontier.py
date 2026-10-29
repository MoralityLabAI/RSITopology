from fractions import Fraction

from heterogeneous_frontier import (
    CODEBOOK_SHAPES,
    causal_no_lag,
    complete_prefix_universe_report,
    enumerate_format_matrix,
    exhaustive_safe_replay_report,
    finite_prefix_frontier_report,
    full_binary_shapes,
    is_prefix_free,
    periodic_time_sharing_report,
    minimal_plan_count_report,
    skew_probability_phase_report,
    unit_rescaling_report,
    verification_payload,
)


def test_registered_codebooks_are_prefix_free():
    assert all(is_prefix_free(words) for words in CODEBOOK_SHAPES.values())


def test_identity_formats_have_causal_relays_and_mixed_formats_do_not():
    huffman = CODEBOOK_SHAPES["huffman"]
    balanced = CODEBOOK_SHAPES["balanced"]
    assert causal_no_lag(huffman, huffman)
    assert causal_no_lag(balanced, balanced)
    assert not causal_no_lag(huffman, balanced)
    assert not causal_no_lag(balanced, huffman)


def test_all_plan_labellings_give_the_exact_transducer_matrix():
    rows = {
        (row["input_format"], row["output_format"]): row
        for row in enumerate_format_matrix()["rows"]
    }
    assert rows[("huffman", "huffman")]["feasible_assignments"] == 48
    assert rows[("huffman", "balanced")]["feasible_assignments"] == 0
    assert rows[("balanced", "huffman")]["feasible_assignments"] == 0
    assert rows[("balanced", "balanced")]["feasible_assignments"] == 192


def test_finite_frontier_excludes_the_coordinatewise_infimum():
    report = finite_prefix_frontier_report()
    points = [
        (
            Fraction(
                row["expected_read_length"]["numerator"],
                row["expected_read_length"]["denominator"],
            ),
            row["worst_write_length"],
        )
        for row in report["pareto_minima"]
    ]
    assert points == [(Fraction(7, 4), 3), (Fraction(2), 2)]
    assert not report["coordinatewise_infimum_achievable"]


def test_public_periodic_schedules_lie_on_the_exact_frontier_segment():
    report = periodic_time_sharing_report()
    assert report["schedule_count"] == 90
    assert report["pass"]
    for row in report["rows"]:
        read = Fraction(
            row["expected_read_total"]["numerator"],
            row["expected_read_total"]["denominator"],
        )
        assert 4 * read + row["worst_write_total"] == 10 * row["blocks"]


def test_positive_unit_rescaling_cannot_change_the_base_argmin():
    report = unit_rescaling_report()
    assert report == {"rows_checked": 400, "pass": True}


def test_every_feasible_transducer_replays_every_terminal_control():
    report = exhaustive_safe_replay_report()
    assert report["pass"]
    assert report["feasible_transducers"] == 240
    assert report["plan_replays"] == 960
    assert report["failures"] == []


def test_complete_four_plan_full_binary_prefix_universe():
    assert len(full_binary_shapes(4)) == 5
    report = complete_prefix_universe_report()
    assert report["pass"]
    assert report["labelled_codebooks"] == 120
    assert report["codebook_pairs_checked"] == 14400
    assert report["feasible_pairs"] == 960
    assert report["plan_replays"] == 3840
    assert [
        (
            row["expected_read_length"]["exact"],
            row["worst_write_length"],
        )
        for row in report["pareto_minima"]
    ] == [("7/4", 3), ("2", 2)]


def test_skew_probability_phase_and_minimal_plan_count():
    phase = skew_probability_phase_report()
    assert phase["pass"]
    assert (
        phase["laws"],
        phase["skew_laws"],
        phase["boundary_laws"],
        phase["balanced_laws"],
    ) == (34, 27, 2, 5)
    minimal = minimal_plan_count_report()
    assert minimal["pass"]
    assert [len(row["pareto"]) for row in minimal["rows"]] == [1, 1, 1, 2]


def test_all_verification_gates_pass():
    payload = verification_payload()
    assert payload["pass"]
    assert all(payload["gates"].values())
