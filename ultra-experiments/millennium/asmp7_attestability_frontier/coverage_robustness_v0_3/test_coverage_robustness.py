from __future__ import annotations

import ast
import copy
from fractions import Fraction
from pathlib import Path

import pytest

from coverage_robustness import (
    ERROR_LIMIT,
    MODELS,
    brute_force_small_cases,
    build_result,
    cell_record,
    covered_agreement_range,
    observation_pair,
    policy_independent_probability,
    selective_probability,
)
from verify_result import verify_payload


HERE = Path(__file__).resolve().parent


@pytest.fixture(scope="module")
def result() -> dict[str, object]:
    return build_result()


def test_coverage_probability_formulas_are_exact() -> None:
    theta = Fraction(3, 4)
    assert policy_independent_probability(8, theta, 12) == Fraction(1, 2)
    assert policy_independent_probability(14, theta, 12) == Fraction(41, 64)
    assert covered_agreement_range(8, 12) == (4, 8)
    assert covered_agreement_range(14, 12) == (10, 12)
    assert selective_probability(8, theta, 12) == Fraction(9, 16)
    assert selective_probability(10, theta, 12) == Fraction(5, 8)


def test_zero_information_and_selective_common_laws() -> None:
    for model in MODELS:
        for k1 in (14, 16):
            assert observation_pair(model, k1, Fraction(3, 4), 0).common_law
            assert observation_pair(model, k1, Fraction(1, 2), 16).common_law
    for theta in (Fraction(3, 4), Fraction(4, 5), Fraction(1)):
        selective = observation_pair("adversarial_selective", 14, theta, 10)
        independent = observation_pair("policy_independent", 14, theta, 10)
        assert selective.common_law
        assert selective.common_witness["covered_agreements"] == 8
        assert not independent.common_law


def test_full_coverage_reproduces_v021_minima() -> None:
    expected = {
        (14, Fraction(3, 4)): 73,
        (14, Fraction(4, 5)): 50,
        (14, Fraction(1)): 15,
        (16, Fraction(3, 4)): 40,
        (16, Fraction(4, 5)): 26,
        (16, Fraction(1)): 5,
    }
    for model in MODELS:
        for (k1, theta), m_star in expected.items():
            record = cell_record(model, k1, theta, 16)
            assert record["status"] == "feasible_exact"
            assert record["m_star"] == m_star
            assert Fraction(*map(int, record["test"]["fp"].split("/"))) == ERROR_LIMIT
            assert Fraction(*map(int, record["test"]["fn"].split("/"))) <= ERROR_LIMIT
            assert Fraction(*map(int, record["predecessor"]["fn"].split("/"))) > ERROR_LIMIT


def test_bruteforce_small_cases_and_metric_probes(result: dict[str, object]) -> None:
    brute = brute_force_small_cases()
    assert brute["pass"]
    assert not brute["range_failures"]
    assert not brute["invariance_failures"]
    assert not brute["distribution_failures"]
    assert all(probe["pass"] for probe in result["metric_robustness_probes"].values())


def test_gates_and_decision_layers_remain_separate(result: dict[str, object]) -> None:
    assert all(gate["pass"] for gate in result["gates"].values())
    assert result["task_result"]["status"] == "selective_suppression_weakens_registered_attestability"
    assert result["measurement_reliability"]["status"] == "reliable_exact_finite_measurement"
    assert result["claim_support"]["status"] == "registered_finite_claim_supported"
    assert result["operational_decision"]["status"] == "no_deployment_decision_authorized"
    assert set(result).issuperset(
        {"task_result", "measurement_reliability", "claim_support", "operational_decision"}
    )


def test_independent_verifier_recomputes_and_rejects_tampering(result: dict[str, object]) -> None:
    verification = verify_payload(result)
    assert verification["pass"], verification["failures"]
    assert verification["implementation_imported"] is False

    tampered = copy.deepcopy(result)
    row = next(record for record in tampered["records"] if record["status"] == "feasible_exact")
    row["m_star"] += 1
    rejected = verify_payload(tampered)
    assert not rejected["pass"]
    assert any("m_star" in failure for failure in rejected["failures"])


def test_verifier_has_no_implementation_import() -> None:
    tree = ast.parse((HERE / "verify_result.py").read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert "coverage_robustness" not in imported
