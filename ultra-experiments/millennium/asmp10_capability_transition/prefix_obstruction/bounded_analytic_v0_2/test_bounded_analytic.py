from fractions import Fraction

import pytest

import bounded_analytic as solver
import run_bounded_analytic as runner
import verify_bounded_analytic as independent


def test_zero_nullity_control_and_first_kernel_dimension():
    for n_nodes, jet_order in runner.REGISTERED_CASES:
        control = solver.identified_control(n_nodes, jet_order)
        assert control["rank"] == n_nodes * (jet_order + 1)
        assert control["nullity"] == 0

        result = solver.solve_first_kernel(n_nodes, jet_order, 1)
        assert result["rank"] == result["observations"]
        assert result["nullity"] == 1


def test_exact_kernel_matches_independent_closed_form_product():
    for n_nodes, jet_order in runner.REGISTERED_CASES:
        result = solver.solve_first_kernel(n_nodes, jet_order, 1)
        expected = independent.closed_form_kernel(n_nodes, jet_order)
        assert result["kernel_direction"] == expected
        assert result["kernel_direction"] == solver.explicit_kernel_product(n_nodes, jet_order)
        assert all(value == 0 for value in result["plus_prefix"])
        assert all(value == 0 for value in result["minus_prefix"])


def test_budget_homogeneity_and_monotonicity_are_exact():
    budgets = runner.REGISTERED_BUDGETS
    for n_nodes, jet_order in runner.REGISTERED_CASES:
        for metric_name in runner.REGISTERED_METRICS:
            values = [
                solver.solve_first_kernel(n_nodes, jet_order, budget, metric_name)[
                    "optimum_separation"
                ]
                for budget in budgets
            ]
            unit = solver.solve_first_kernel(n_nodes, jet_order, 1, metric_name)[
                "optimum_separation"
            ]
            assert values == [budget * unit for budget in budgets]
            assert all(left <= right for left, right in zip(values, values[1:]))


def test_basis_is_bound_and_material_to_the_norm():
    with pytest.raises(ValueError, match="basis must be exactly"):
        solver.solve_first_kernel(2, 1, 1, basis_id="shifted_monomials")

    result = solver.solve_first_kernel(2, 1, 1)
    coefficients = result["kernel_direction"]
    shifted = solver.shifted_monomial_coefficients(coefficients, Fraction(1, 2))
    assert result["basis_id"] == solver.BASIS_ID
    assert result["norm_id"] == solver.NORM_ID
    assert solver.coefficient_l1(coefficients) == result["kernel_l1"]
    assert solver.coefficient_l1(shifted) != result["kernel_l1"]


def test_fraction_witnesses_are_feasible_and_attain_the_formula():
    for n_nodes, jet_order in runner.REGISTERED_CASES:
        for metric_name in runner.REGISTERED_METRICS:
            for budget in runner.REGISTERED_BUDGETS:
                result = solver.solve_first_kernel(n_nodes, jet_order, budget, metric_name)
                assert solver.witness_is_feasible(result)
                assert solver.coefficient_l1(result["plus_coefficients"]) <= budget
                assert solver.coefficient_l1(result["minus_coefficients"]) <= budget
                expected = (
                    2
                    * budget
                    * abs(result["metric_on_kernel"])
                    / result["kernel_l1"]
                )
                assert result["witness_separation"] == expected
                assert result["optimum_separation"] == expected


def test_independent_determinant_and_dual_certificate_prove_optimality():
    for n_nodes, jet_order in runner.REGISTERED_CASES:
        for metric_name in runner.REGISTERED_METRICS:
            result = solver.solve_first_kernel(n_nodes, jet_order, Fraction(7, 5), metric_name)
            verification = independent.verify_solver_result(result)
            certificate = verification["certificate"]
            assert verification["verified"]
            assert certificate["identified_determinant"] != 0
            assert certificate["checks"]["dual_linf_feasible"]
            assert certificate["checks"]["dual_saturates_l1"]
            assert result["optimum_separation"] == certificate["optimum_separation"]


def test_exactly_five_metric_robustness_probes_pass():
    assert runner.REGISTERED_METRICS == (
        "future_gradient_at_n",
        "future_value_at_n",
        "future_value_at_n_plus_1",
        "future_gradient_at_n_plus_1",
        "future_secant_n_to_n_plus_1",
    )
    report = runner.build_report()
    metric_status = report["reliability"]["metric_probe_status"]
    assert len(metric_status) == 5
    assert all(metric_status.values())
    assert report["reliability"]["gates"]["R0_five_metric_robustness_probes"]


def test_report_separates_result_reliability_claim_support_and_operation():
    report = runner.build_report()
    assert set(report) == {
        "schema_version",
        "task_result",
        "reliability",
        "claim_support",
        "operation",
    }
    assert report["task_result"]["status"] == (
        "exact_codimension_one_norm_bounded_envelope_established"
    )
    assert all(report["reliability"]["gates"].values())
    assert report["claim_support"]["status"] == (
        "supports_only_the_frozen_exact_prefix_codimension_one_slice"
    )
    assert report["operation"]["gpu_used"] is False
    assert report["operation"]["network_used"] is False
    assert report["operation"]["repository_writes"] is False
