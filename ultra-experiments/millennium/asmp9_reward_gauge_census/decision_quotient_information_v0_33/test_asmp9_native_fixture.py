from __future__ import annotations

from fractions import Fraction
from math import log

import pytest
from .asmp9_native_fixture import (
    load_native_sources,
    native_laws_and_answers,
    query_families,
)
from .decision_information import (
    characteristic_design,
    decision_identifiable,
    restrict_queries,
)


def test_sources_are_actual_v029_v031_v032_objects() -> None:
    sources = load_native_sources()
    assert sources.measurement_matrix == (
        (Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0)),
    )
    assert sources.gauge_basis == (
        (Fraction(0), Fraction(0), Fraction(1)),
    )
    assert sources.policies == (
        (Fraction(4), Fraction(0), Fraction(2)),
        (Fraction(0), Fraction(4), Fraction(2)),
    )
    assert sources.valid_mixture_residual == 0
    assert sources.invalid_mixture_residual == Fraction(1, 16)
    assert sources.v031_measurement_rows == 8
    assert sources.v032_semantic_residual_rows == 6
    assert len(sources.source_hashes) == 3


def test_native_answers_exercise_reward_mechanics_and_validity() -> None:
    _, answers, _ = native_laws_and_answers()
    assert answers == {
        "base": "policy_1",
        "gauge_alias": "policy_1",
        "mechanics_flip": "policy_0",
        "mixture_invalid": "not_certified",
        "reward_flip": "policy_0",
    }


def test_gauge_alias_is_observationally_and_decision_equivalent() -> None:
    laws, answers, _ = native_laws_and_answers()
    assert laws["gauge_alias"] == laws["base"]
    assert answers["gauge_alias"] == answers["base"]
    assert characteristic_design(laws, answers, "base").rate > 0
    assert (
        characteristic_design(
            laws,
            answers,
            "base",
            distinguish_full_hypothesis=True,
        ).rate
        == 0
    )


def test_every_native_query_family_is_necessary() -> None:
    laws, answers, _ = native_laws_and_answers()
    all_queries = tuple(next(iter(laws.values())))
    for removed in query_families().values():
        retained = tuple(query for query in all_queries if query not in removed)
        restricted = restrict_queries(laws, retained)
        assert not decision_identifiable(restricted, answers)
        assert characteristic_design(restricted, answers, "base").rate == 0


def test_joint_native_design_uses_every_family() -> None:
    laws, answers, _ = native_laws_and_answers()
    assert decision_identifiable(laws, answers)
    design = characteristic_design(laws, answers, "base")
    for queries in query_families().values():
        assert sum(design.allocation[query] for query in queries) > 0


def test_native_design_matches_three_channel_harmonic_rate() -> None:
    laws, answers, _ = native_laws_and_answers()
    design = characteristic_design(laws, answers, "base")
    reward_information = 0.5 * log(3)
    mechanics_information = 0.5 * log(3)
    mixture_information = 0.5 * log(289 / 288)
    expected_rate = 1 / (
        1 / reward_information
        + 1 / mechanics_information
        + 1 / mixture_information
    )
    assert design.rate == pytest.approx(expected_rate, abs=1e-12)
    expected = {
        "return": expected_rate / reward_information,
        "mechanics": expected_rate / mechanics_information,
        "mixture": expected_rate / mixture_information,
    }
    observed = {
        family: sum(design.allocation[query] for query in queries)
        for family, queries in query_families().items()
    }
    assert observed == pytest.approx(expected, abs=1e-12)
