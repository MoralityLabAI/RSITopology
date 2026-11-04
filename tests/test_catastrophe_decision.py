"""Synthetic comparisons are conditional statements, never live risk estimates."""
from dataclasses import replace
import hashlib
import json
import math

import pytest

from rsi_topology.catastrophe_decision import (
    CausalDeltas, Governance, Interval, LossModel, audit_comparison,
    evidence_grade, expected_loss_bounds, finite_frc_tail_audit,
)


GOOD = Governance(True, True, True, True)
LOSS = LossModel(10.0, 15.0, Interval(0.01, 0.02))
BENEFIT = CausalDeltas(Interval(-0.08, -0.06), Interval(0.005, 0.01),
                      ("independent:A", "independent:B"), "synthetic-study",
                      "assessed")


def test_robust_benefit_is_conditional_and_hash_stable():
    output = audit_comparison(BENEFIT, GOOD, LOSS, asserted="benefit")
    assert output["interval_sign"] == "benefit"
    assert output["delta_expected_loss"]["upper"] == pytest.approx(-0.43)
    assert output["claim_supported_in_stated_scope"]
    assert not output["empirical_validity_verified"]
    assert output["decision"] == "eligible_for_independent_review"
    assert output == audit_comparison(BENEFIT, GOOD, LOSS, asserted="benefit")
    digest = output.pop("sha256")
    assert digest == hashlib.sha256(json.dumps(output, sort_keys=True,
                        separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def test_interval_uncertainty_blocks_strong_net_effect_claim():
    unclear = replace(BENEFIT, nuclear=Interval(-0.08, -0.01),
                      ai_control=Interval(0.005, 0.08))
    claim = audit_comparison(unclear, GOOD, LOSS, asserted="harm")
    assert claim["delta_expected_loss"]["lower"] < 0
    assert claim["delta_expected_loss"]["upper"] > 0
    assert claim["interval_sign"] == "unresolved"
    assert not claim["claim_supported_in_stated_scope"]
    assert claim["decision"] == "review_uncertainty"


def test_harm_finds_signed_evidence_without_governance_approval():
    harmful = replace(BENEFIT, nuclear=Interval(-0.01, 0),
                      ai_control=Interval(0.05, 0.09))
    result = audit_comparison(harmful, GOOD, LOSS, asserted="harm")
    assert result["interval_sign"] == "harm"
    assert result["decision"] == "reject_predicted_harm"


@pytest.mark.parametrize("field", ("authorized", "independently_audited",
                                      "human_recall", "transparent_protocol"))
def test_unapproved_paths_are_blocked_regardless_of_loss_claim(field):
    result = audit_comparison(BENEFIT, replace(GOOD, **{field: False}),
                              LOSS, asserted="benefit")
    assert result["decision"] == "blocked_governance"
    assert result["governance_violations"] == [field]


def test_missing_or_assumed_or_echoed_sources_have_distinct_receipts():
    assert evidence_grade(replace(BENEFIT, nuclear=None)) == "missing_deltas"
    assert evidence_grade(replace(BENEFIT, identification="assumed")) == "assumption_only"
    echo = replace(BENEFIT, independent_roots=("A", "A"))
    assert evidence_grade(echo) == "provenance_gap"
    assert audit_comparison(echo, GOOD, LOSS, asserted="benefit")["decision"] == "request_evidence"
    external = replace(BENEFIT, scope="external")
    assert evidence_grade(external) == "external_assessment_unverified"
    assert not audit_comparison(external, GOOD, LOSS)["empirical_validity_verified"]


def test_probability_delta_and_input_validation_fail_closed():
    for pair in ((0, float("nan")), (0, float("inf")), (.3, .2)):
        with pytest.raises(ValueError):
            Interval(*pair)
    with pytest.raises(ValueError):
        CausalDeltas(Interval(-1.1, 0), Interval(0, 0))
    with pytest.raises(ValueError):
        LossModel(float("nan"), 1, Interval(0, 1))
    with pytest.raises(ValueError):
        LossModel(1, 1, Interval(-1, 0))
    with pytest.raises(ValueError):
        Governance("true", True, True, True)
    with pytest.raises(ValueError):
        audit_comparison(BENEFIT, GOOD, LOSS, asserted="surely")


def test_zero_boundary_is_indeterminate_and_weights_scale_homogeneously():
    zero = CausalDeltas(Interval(0, 0), Interval(0, 0),
                        ("A", "B"), "s", "assessed")
    model = LossModel(1, 1, Interval(0, 0))
    assert audit_comparison(zero, GOOD, model)["interval_sign"] == "unresolved"
    x = expected_loss_bounds(BENEFIT, LOSS)
    y = expected_loss_bounds(BENEFIT, LossModel(20, 30, Interval(.02, .04)))
    assert y.lower == pytest.approx(2 * x.lower)
    assert y.upper == pytest.approx(2 * x.upper)


def test_frc_finite_tail_prevents_infinite_horizon_overclaim():
    summary = finite_frc_tail_audit([1.0, 0.7, 0.8, 0.9])
    assert summary["observed_suffix_infima"] == [0.7, 0.7, 0.8, 0.9]
    assert not summary["infinite_liminf_certified"]
    with pytest.raises(ValueError):
        finite_frc_tail_audit([])
    with pytest.raises(ValueError):
        finite_frc_tail_audit([1, math.nan])
