#!/usr/bin/env python3
"""Build the deterministic bounded-analytic v0.2 verification report."""

from __future__ import annotations

import json
from fractions import Fraction
from typing import Sequence

import bounded_analytic as solver
import verify_bounded_analytic as independent


REGISTERED_CASES = ((1, 1), (2, 1), (3, 1), (2, 2), (3, 2))
REGISTERED_BUDGETS = (Fraction(0), Fraction(1, 3), Fraction(1), Fraction(5, 2))
REGISTERED_METRICS = tuple(solver.METRIC_SPECS)


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def vector_text(values: Sequence[Fraction]) -> list[str]:
    return [fraction_text(value) for value in values]


def envelope_row(result: dict[str, object]) -> dict[str, object]:
    return {
        "n_nodes": result["n_nodes"],
        "jet_order": result["jet_order"],
        "degree": result["degree"],
        "budget": fraction_text(result["budget"]),
        "metric_name": result["metric_name"],
        "kernel_l1": fraction_text(result["kernel_l1"]),
        "metric_on_kernel": fraction_text(result["metric_on_kernel"]),
        "witness_amplitude": fraction_text(result["witness_amplitude"]),
        "optimum_separation": fraction_text(result["optimum_separation"]),
    }


def build_report() -> dict[str, object]:
    solutions: list[dict[str, object]] = []
    independent_checks: list[bool] = []
    witness_checks: list[bool] = []
    metric_checks: dict[str, list[bool]] = {name: [] for name in REGISTERED_METRICS}

    for n_nodes, jet_order in REGISTERED_CASES:
        for metric_name in REGISTERED_METRICS:
            for budget in REGISTERED_BUDGETS:
                result = solver.solve_first_kernel(n_nodes, jet_order, budget, metric_name)
                verification = independent.verify_solver_result(result)
                feasible = solver.witness_is_feasible(result)
                solutions.append(result)
                independent_checks.append(bool(verification["verified"]))
                witness_checks.append(feasible)
                metric_checks[metric_name].append(bool(verification["verified"] and feasible))

    zero_nullity_controls = [
        solver.identified_control(n_nodes, jet_order)
        for n_nodes, jet_order in REGISTERED_CASES
    ]
    zero_nullity_gate = all(control["nullity"] == 0 for control in zero_nullity_controls)

    homogeneity_gate = True
    monotonicity_gate = True
    for n_nodes, jet_order in REGISTERED_CASES:
        for metric_name in REGISTERED_METRICS:
            matching = [
                result
                for result in solutions
                if result["n_nodes"] == n_nodes
                and result["jet_order"] == jet_order
                and result["metric_name"] == metric_name
            ]
            by_budget = {result["budget"]: result["optimum_separation"] for result in matching}
            unit = by_budget[Fraction(1)]
            homogeneity_gate = homogeneity_gate and all(
                by_budget[budget] == budget * unit for budget in REGISTERED_BUDGETS
            )
            ordered = [by_budget[budget] for budget in sorted(REGISTERED_BUDGETS)]
            monotonicity_gate = monotonicity_gate and all(
                left <= right for left, right in zip(ordered, ordered[1:])
            )

    kernel_cases: list[dict[str, object]] = []
    shifted_norms_differ = False
    basis_rows_bound = True
    for n_nodes, jet_order in REGISTERED_CASES:
        result = solver.solve_first_kernel(n_nodes, jet_order, 1)
        direction = result["kernel_direction"]
        explicit = solver.explicit_kernel_product(n_nodes, jet_order)
        center = Fraction(n_nodes - 1, 2)
        shifted = solver.shifted_monomial_coefficients(direction, center)
        monomial_l1 = solver.coefficient_l1(direction)
        shifted_l1 = solver.coefficient_l1(shifted)
        shifted_norms_differ = shifted_norms_differ or monomial_l1 != shifted_l1
        basis_rows_bound = basis_rows_bound and bool(
            result["basis_id"] == solver.BASIS_ID
            and result["norm_id"] == solver.NORM_ID
            and direction == explicit
            and monomial_l1 == result["kernel_l1"]
        )
        kernel_cases.append(
            {
                "n_nodes": n_nodes,
                "jet_order": jet_order,
                "kernel_coefficients": vector_text(direction),
                "monomial_l1": fraction_text(monomial_l1),
                "shift_center": fraction_text(center),
                "shifted_basis_l1_control": fraction_text(shifted_l1),
            }
        )
    basis_binding_gate = basis_rows_bound and shifted_norms_differ

    five_metric_gate = len(metric_checks) == 5 and all(
        checks and all(checks) for checks in metric_checks.values()
    )
    gates = {
        "Z0_zero_nullity_control": zero_nullity_gate,
        "H0_budget_homogeneity": homogeneity_gate,
        "M0_budget_monotonicity": monotonicity_gate,
        "B0_frozen_basis_binding": basis_binding_gate,
        "W0_exact_witness_feasibility": all(witness_checks),
        "O0_independent_closed_form_dual_optimality": all(independent_checks),
        "R0_five_metric_robustness_probes": five_metric_gate,
    }
    passed = all(gates.values())
    verdict = (
        "exact_codimension_one_norm_bounded_envelope_established"
        if passed
        else "instrument_failed"
    )

    return {
        "schema_version": "asmp10_bounded_analytic_v0_2_report_v1",
        "task_result": {
            "status": verdict,
            "formula": "Delta*=2*B*abs(phi(q))/coefficient_l1(q)",
            "basis_id": solver.BASIS_ID,
            "norm_id": solver.NORM_ID,
            "kernel_cases": kernel_cases,
            "envelopes": [envelope_row(result) for result in solutions],
        },
        "reliability": {
            "status": "all_registered_gates_passed" if passed else "gate_failure",
            "gates": gates,
            "arithmetic": "fractions.Fraction only on the mathematical path",
            "independent_verifier": "product + square determinant + L-infinity dual witness",
            "metric_probe_status": {
                name: all(checks) for name, checks in metric_checks.items()
            },
        },
        "claim_support": {
            "status": "supports_only_the_frozen_exact_prefix_codimension_one_slice",
            "supported": [
                "sharp global pairwise envelope at D=n(k+1) and delta=0",
                "zero-nullity identified control at D=n(k+1)-1",
                "linear homogeneity and monotonicity in rational budget B",
            ],
            "not_supported": [
                "conditional envelope for a fixed nonzero observed prefix",
                "noisy prefix jets with delta>0",
                "higher-dimensional kernels D>n(k+1)",
                "basis-invariant or infinite-dimensional analytic norm claims",
                "neural-training transition predictability",
            ],
        },
        "operation": {
            "status": "deterministic_cpu_exact_report_built",
            "registered_case_count": len(REGISTERED_CASES),
            "registered_budget_count": len(REGISTERED_BUDGETS),
            "registered_metric_count": len(REGISTERED_METRICS),
            "envelope_count": len(solutions),
            "gpu_used": False,
            "network_used": False,
            "repository_writes": False,
        },
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["reliability"]["status"] == "all_registered_gates_passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
