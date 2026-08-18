from fractions import Fraction

from experiment import run_registry
from run_verification import (
    evaluate_scientific_gates,
    render_report,
    summarize_records,
)


def test_burned_summary_separates_null_and_collapse() -> None:
    spec = {
        "alpha": "1/20",
        "cycle_lengths": [3],
        "trials_per_edge": [2],
        "odds_ratios": ["1/1", "2/1"],
        "nuisance_ratios": ["1/1", "256/1"],
    }
    registry = run_registry(spec)
    summary = summarize_records(
        registry["records"],
        alpha=Fraction(1, 20),
        balanced_nuisance="1/1",
        extreme_nuisance="256/1",
        interior_nuisance="1/1",
        interior_epsilon=Fraction(1, 4),
        ratio_ceiling=Fraction(1, 1000),
    )
    assert summary["null_control_mismatch_count"] == 0
    assert summary["nonpositive_excess_count"] == 0
    assert summary["nonpositive_interior_bound_count"] == 0
    assert summary["fixed_interior_mismatch_count"] == 0
    assert summary["endpoint_collapse_mismatch_count"] == 0


def test_burned_scientific_gate_evaluator_is_total() -> None:
    protocol = {
        "fresh_registry": {
            "alpha": "1/20",
            "cycle_lengths": [3],
            "trials_per_edge": [2],
            "odds_ratios": ["1/1", "2/1"],
            "nuisance_ratios": ["1/1", "256/1"],
        },
        "balanced_nuisance_ratio": "1/1",
        "extreme_nuisance_ratio": "256/1",
        "maximum_extreme_to_balanced_excess_ratio": "1/1000",
        "interior_nuisance_ratio": "1/1",
        "interior_probability_floor": "1/4",
    }
    registry = run_registry(protocol["fresh_registry"])
    summary = summarize_records(
        registry["records"],
        alpha=Fraction(1, 20),
        balanced_nuisance="1/1",
        extreme_nuisance="256/1",
        interior_nuisance="1/1",
        interior_epsilon=Fraction(1, 4),
        ratio_ceiling=Fraction(1, 1000),
    )
    gates = evaluate_scientific_gates(registry, summary, protocol)
    assert set(gates) == {
        "G1_fiber_partition_and_mass",
        "G2_availability_formula",
        "G3_exact_conditional_size",
        "G4_excess_factorization",
        "G5_no_go_upper_bound",
        "G6_interior_sufficiency",
        "G7_null_control",
        "G8_extreme_nuisance_collapse",
    }
    assert all(gates.values())


def test_report_preserves_conditional_unconditional_distinction() -> None:
    result = {
        "verdict": "ok",
        "gates": {"G0": True},
        "registry": {
            "cell_count": 2,
            "availability_formula_mismatch_count": 0,
            "mass_normalization_mismatch_count": 0,
            "excess_decomposition_mismatch_count": 0,
            "interior_lower_bound_mismatch_count": 0,
            "records": [
                {
                    "odds_ratio": "2/1",
                    "unconditional_power_all": {"decimal": 0.06},
                }
            ],
        },
        "summary": {
            "null_cell_count": 1,
            "positive_cell_count": 1,
            "interior_control_count": 1,
            "fixed_interior_mismatch_count": 0,
            "maximum_endpoint_ratio": 0.001,
        },
        "claim_boundary": "conditional is not unconditional",
    }
    report = render_report(result)
    assert "entirely an unconditional availability effect" in report
    assert "conditional is not unconditional" in report
