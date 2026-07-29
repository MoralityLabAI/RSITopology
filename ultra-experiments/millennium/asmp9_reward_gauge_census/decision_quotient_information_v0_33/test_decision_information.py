from __future__ import annotations

import json
from math import inf, log
import subprocess
import sys
from pathlib import Path

import pytest

from .decision_information import (
    characteristic_design,
    decision_identifiable,
    fixed_confidence_lower_bound,
    kl_divergence,
    restrict_queries,
    xor_channel_fixture,
)


def test_joint_fixture_has_closed_form_optimum() -> None:
    laws, answers = xor_channel_fixture()
    design = characteristic_design(laws, answers, "h00")
    behavior_divergence = 0.6 * log(4)
    mechanics_divergence = 0.5 * log(3)
    expected_behavior = mechanics_divergence / (
        behavior_divergence + mechanics_divergence
    )
    expected_rate = (
        behavior_divergence
        * mechanics_divergence
        / (behavior_divergence + mechanics_divergence)
    )
    assert design.allocation["behavior"] == pytest.approx(
        expected_behavior,
        abs=1e-10,
    )
    assert design.allocation["mechanics"] == pytest.approx(
        1 - expected_behavior,
        abs=1e-10,
    )
    assert design.rate == pytest.approx(expected_rate, abs=1e-10)


@pytest.mark.parametrize("query", ["behavior", "mechanics"])
def test_each_channel_is_necessary(query: str) -> None:
    laws, answers = xor_channel_fixture()
    restricted = restrict_queries(laws, [query])
    assert not decision_identifiable(restricted, answers)
    assert characteristic_design(restricted, answers, "h00").rate == 0


def test_gauge_alias_blocks_parameter_but_not_decision_identification() -> None:
    laws, answers = xor_channel_fixture(include_gauge_alias=True)
    decision = characteristic_design(laws, answers, "h00")
    full = characteristic_design(
        laws,
        answers,
        "h00",
        distinguish_full_hypothesis=True,
    )
    assert decision.rate > 0
    assert full.rate == 0


def test_fixed_confidence_lower_bound_is_finite_only_when_identifiable() -> None:
    laws, answers = xor_channel_fixture()
    joint = characteristic_design(laws, answers, "h00")
    behavior_only = characteristic_design(
        restrict_queries(laws, ["behavior"]),
        answers,
        "h00",
    )
    assert fixed_confidence_lower_bound(joint, 0.05) > 0
    assert fixed_confidence_lower_bound(behavior_only, 0.05) == inf


def test_kl_and_model_validation() -> None:
    assert kl_divergence((0.5, 0.5), (0.5, 0.5)) == pytest.approx(0)
    with pytest.raises(ValueError):
        kl_divergence((0.4, 0.4), (0.5, 0.5))
    laws, answers = xor_channel_fixture()
    broken = dict(answers)
    broken.pop("h11")
    with pytest.raises(ValueError):
        decision_identifiable(laws, broken)


def test_development_runner_reports_scope_and_ablations() -> None:
    here = Path(__file__).resolve().parent
    completed = subprocess.run(
        [sys.executable, str(here / "run_development.py")],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["claim_status"] == "development_only_unregistered"
    assert result["decision_identifiable"]
    assert result["full_parameter_rate_with_gauge_alias"] == 0
    assert all(
        not row["decision_identifiable"] and row["rate"] == 0
        for row in result["single_channel_ablations"].values()
    )
