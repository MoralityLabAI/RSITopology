from __future__ import annotations

import math

from audit import (
    PROTOCOL_PATH,
    RESULT_PATH,
    action_dictionary_nesting_violations,
    load_json,
    profile_all_witnesses,
    row_key,
    run_audit,
    time_aware_zero_rate_fixture,
    upward_closure_violations,
    witness_transcript_profile,
    zero_port_audit,
)


def source_inputs():
    return load_json(PROTOCOL_PATH), load_json(RESULT_PATH)


def test_raw_grid_fails_the_capacity_upper_set_axiom_in_six_pairs():
    _, result = source_inputs()
    violations = upward_closure_violations(result["grid"])
    assert len(violations) == 6
    assert {
        (row["feasible_source"][1], row["infeasible_larger_budget"][1])
        for row in violations
    } == {(0, 1), (0, 2)}


def test_write_dictionaries_change_authority_instead_of_nesting_it():
    protocol, _ = source_inputs()
    violations = action_dictionary_nesting_violations(protocol)
    assert len(violations) == 3
    assert {(row["lower_bits"], row["higher_bits"]) for row in violations} == {
        (0, 1),
        (0, 2),
        (1, 2),
    }


def test_zero_port_cuts_must_be_open_loop_but_raw_grid_disagrees():
    protocol, result = source_inputs()
    audit = zero_port_audit(protocol, result["grid"])
    assert audit["context_count"] == 12
    assert audit["raw_zero_port_disagreement_count"] == 3
    assert audit["raw_r0_wmax_open_loop_mismatch_count"] == 3
    assert audit["raw_rmax_w0_open_loop_mismatch_count"] == 0
    assert audit["raw_r0_w0_open_loop_mismatch_count"] == 0


def test_all_reported_witnesses_obey_data_processing_but_not_nominal_rates():
    protocol, result = source_inputs()
    profiles = profile_all_witnesses(protocol, result["grid"])
    assert profiles["feasible_witness_count"] == 77
    assert profiles["data_processing_violation_count"] == 0
    assert profiles["strict_write_collapses_count"] == 34
    assert profiles["nominal_read_rate_overstatement_count"] == 60
    assert profiles["nominal_write_rate_overstatement_count"] == 53


def test_load_bearing_nominal_two_bit_cell_uses_only_three_transcripts():
    protocol, result = source_inputs()
    row = next(
        item for item in result["grid"] if row_key(item) == (2, "1/2", "3/2", 2, 2)
    )
    profile = witness_transcript_profile(protocol, row)
    assert profile["read_transcript_count"] == 3
    assert profile["write_transcript_count"] == 3
    assert (
        profile["achieved_read_bits_per_step"]
        == profile["achieved_write_bits_per_step"]
    )
    assert profile["achieved_read_bits_per_step"] == math.log2(3) / 2


def test_decoder_memory_can_make_a_time_varying_open_loop_code_zero_rate():
    fixture = time_aware_zero_rate_fixture()
    assert fixture["one_symbol_time_aware_pass"] is True
    assert fixture["every_fixed_memoryless_decoder_fails"] is True
    assert fixture["read_transcript_count"] == fixture["write_transcript_count"] == 1


def test_audit_stops_on_definition_repair_not_on_solver_invalidity():
    audit = run_audit()
    assert audit["checks"]["source_exact_run_is_internally_valid"]["pass"] is True
    assert audit["checks"]["raw_grid_is_upward_closed"]["pass"] is False
    assert audit["checks"]["reported_witnesses_obey_data_processing"]["pass"] is True
    assert (
        audit["checks"]["nominal_rates_equal_achieved_transcript_rates"]["pass"]
        is False
    )
    assert audit["decision"]["status"] == "stop_and_repair_problem_definition"
