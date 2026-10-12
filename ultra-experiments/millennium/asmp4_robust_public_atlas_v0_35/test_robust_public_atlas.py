from fractions import Fraction

import pytest

from robust_public_atlas import (
    architecture_boundary_report,
    atlas_bits,
    ceil_log2,
    claim_payload,
    closed_form_error,
    cube_cover_count,
    dimension_cover_report,
    error_recurrence_report,
    full_report,
    mutation_report,
    nonlinear_fixture_report,
    predecessor_inventory_report,
    propagated_errors,
    robust_word_certificate,
    v34_bridge_report,
)


def test_error_recurrence_matches_closed_form_on_full_census() -> None:
    report = error_recurrence_report()
    assert report["pass"]
    assert report["rows"] == 3888
    assert propagated_errors(Fraction(1), Fraction(2), Fraction(1, 8), Fraction(1, 16), 3) == (
        Fraction(1, 8),
        Fraction(1, 4),
        Fraction(3, 8),
        Fraction(1, 2),
    )
    assert closed_form_error(Fraction(1), Fraction(2), Fraction(1, 8), Fraction(1, 16), 3) == Fraction(1, 2)


def test_error_parameter_guards_reject_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        propagated_errors(Fraction(-1), Fraction(1), Fraction(0), Fraction(0), 1)
    with pytest.raises(ValueError):
        closed_form_error(Fraction(2), Fraction(1), Fraction(0), Fraction(0), -1)
    with pytest.raises(ValueError):
        robust_word_certificate(Fraction(2), Fraction(1), Fraction(0), Fraction(0), (), Fraction(1))


def test_strict_margin_certificate_accepts_and_rejects_exactly() -> None:
    accepted = robust_word_certificate(
        Fraction(5, 2),
        Fraction(1),
        Fraction(1, 32),
        Fraction(1, 128),
        (Fraction(1),),
        Fraction(1, 8),
    )
    rejected = robust_word_certificate(
        Fraction(5, 2),
        Fraction(1),
        Fraction(1, 32),
        Fraction(1, 16),
        (Fraction(1),),
        Fraction(1, 8),
    )
    assert accepted["pass"] and accepted["errors"][-1] == Fraction(11, 128)
    assert not rejected["pass"] and not rejected["reset"]


def test_two_port_atlas_and_dimension_costs_are_separate() -> None:
    assert atlas_bits(33, 33) == (6, 6)
    assert atlas_bits(1, 17) == (0, 5)
    assert ceil_log2(1) == 0
    assert cube_cover_count(4, 33) == 1_185_921
    with pytest.raises(ValueError):
        ceil_log2(0)
    with pytest.raises(ValueError):
        cube_cover_count(0, 3)


def test_nonlinear_fixture_is_robust_and_charges_both_ports() -> None:
    report = nonlinear_fixture_report()
    assert report["pass"]
    assert report["rows"] == 3171
    assert report["centers"] == report["distinct_actions"] == 33
    assert report["read_bits"] == report["write_bits"] == 6
    assert report["propagated_bound"] == "11/128"


def test_architecture_boundaries_reject_all_shortcuts() -> None:
    report = architecture_boundary_report()
    assert report["pass"]
    assert report["false_bound"] == "9/128"
    assert report["correct_bound"] == "11/128"
    assert all(report["checks"].values())


def test_dimension_cover_report_exposes_growth() -> None:
    report = dimension_cover_report()
    assert report["pass"]
    assert len(report["rows"]) == 20
    assert report["rows"][-1] == {
        "dimension": 4,
        "centers_per_axis": 33,
        "cells": 1_185_921,
        "bits": 21,
    }


def test_fixed_reset_bridge_does_not_claim_all_pairs_premise() -> None:
    report = v34_bridge_report()
    assert report["pass"]
    assert report["checks"]["fixed_reset_atlas_supplies_v33_safe_closing"]
    assert report["checks"]["literal_v34_local_premise_requires_all_pairs"]


def test_mutations_and_predecessor_inventory_are_frozen() -> None:
    mutations = mutation_report()
    inventory = predecessor_inventory_report()
    assert mutations["pass"] and mutations["cases"] == mutations["rejected"] == 8
    assert inventory["pass"]
    assert (inventory["packages"], inventory["tests"]) == (35, 384)


def test_exact_claim_and_complete_payload_pass() -> None:
    report = full_report()
    assert report["pass"]
    assert report["claim"]["pass"]
    assert report["payload"]["missing"] == []
    assert claim_payload()["evidence"]["nonlinear_rows"] == 3171
