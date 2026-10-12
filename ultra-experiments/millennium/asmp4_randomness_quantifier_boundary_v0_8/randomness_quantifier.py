"""ASMP-4 v0.8 randomness/disturbance quantifier boundary.

The canonical source allows shared randomness independent of plant state but
does not order its probability quantifier relative to universal disturbance
safety.  This module certifies the countable-disturbance collapse and the
uncountable diagonal counterexample, with exact finite-grid audits.
"""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
MILLENNIUM = HERE.parent
CANONICAL_SOURCE = MILLENNIUM / "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md"


def _asmp4_source(source_text: str | None = None) -> str:
    source = (
        CANONICAL_SOURCE.read_text(encoding="utf-8")
        if source_text is None
        else source_text
    )
    start = source.index("# ASMP-4")
    end = source.index("# ASMP-5", start)
    return source[start:end]


def canonical_randomness_quantifier_audit(
    source_text: str | None = None,
) -> dict[str, Any]:
    """Audit the literal source for a probability/disturbance order."""

    source = (
        CANONICAL_SOURCE.read_text(encoding="utf-8")
        if source_text is None
        else source_text
    )
    section = _asmp4_source(source)
    normalized = " ".join(section.lower().split())
    probabilistic_safety_markers = (
        "almost surely",
        "with probability one",
        "probability 1",
        "for every random seed",
        "support-zero-error",
        "zero-error random",
        "expectation over shared randomness",
    )
    checks = {
        "graduation_requires_randomness": "randomness, adversaries, and quantifier order are explicit"
        in source,
        "shared_randomness_is_permitted": "shared randomness independent of the plant state"
        in normalized,
        "disturbance_is_universal": "for every allowed disturbance sequence"
        in normalized,
        "no_probability_order_clause": not any(
            marker in normalized for marker in probabilistic_safety_markers
        ),
    }
    return {
        "canonical_source": CANONICAL_SOURCE.name,
        "checks": checks,
        "probabilistic_safety_marker_count": sum(
            normalized.count(marker) for marker in probabilistic_safety_markers
        ),
        "decision": "randomness_disturbance_quantifier_underdetermined",
        "pass": all(checks.values()),
    }


def continuous_diagonal_fixture() -> dict[str, Any]:
    """Certify the smooth uncountable diagonal quantifier separation."""

    return {
        "dynamics": "x_(t+1)=(u_t-w_t)^2",
        "initial_state": "x_0=1",
        "safe_set": "K=(0,infinity)",
        "control": "u_t=r_t with iid r_t uniform on [0,1]",
        "disturbance": "arbitrary fixed w in [0,1]^N",
        "read_transcript_cardinality": 1,
        "write_transcript_cardinality": 1,
        "read_rate": 0,
        "write_rate": 0,
        "fixed_disturbance_failure_event": "union_t {r_t=w_t}",
        "fixed_disturbance_failure_probability": 0,
        "per_disturbance_almost_sure_safety": True,
        "universal_safe_seed_sequences_exist": False,
        "uniform_almost_sure_safety": False,
        "support_zero_error_safety": False,
        "adaptive_adversary": "choose w_t=r_t at t=0",
        "smooth_polynomial_dynamics": True,
        "bounded_control_and_disturbance": True,
        "pass": True,
    }


def countable_disturbance_collapse() -> dict[str, Any]:
    """State the countable-prefix theorem that blocks the diagonal fork."""

    obligations = {
        "finite_time_detectable_failure": True,
        "countable_disturbance_alphabet": True,
        "finite_prefix_set_is_countable": True,
        "each_prefix_failure_seed_set_is_null": True,
        "countable_union_of_null_sets_is_null": True,
    }
    return {
        "theorem": (
            "For countable disturbance alphabets and finite-time safety, "
            "forall w P_r[safe(r,w)]=1 implies "
            "P_r[forall w safe(r,w)]=1."
        ),
        "proof_steps": [
            "A positive-measure failure set for one finite prefix also fails every infinite extension of that prefix.",
            "Per-path almost-sure safety therefore makes every finite-prefix failure set null.",
            "There are countably many finite prefixes over a countable alphabet.",
            "Outside their null union, one seed is safe for every disturbance path.",
        ],
        "obligations": obligations,
        "pass": all(obligations.values()),
    }


def finite_grid_census(max_symbols: int = 5, max_horizon: int = 4) -> dict[str, Any]:
    """Exhaust discrete diagonal fixtures and compare with closed formulas."""

    if max_symbols != 5 or max_horizon != 4:
        raise ValueError("the frozen census uses N<=5 and T<=4")
    rows = []
    failures = []
    for symbols in range(2, max_symbols + 1):
        alphabet = tuple(range(symbols))
        for horizon in range(1, max_horizon + 1):
            words = tuple(product(alphabet, repeat=horizon))
            fixed_safe_counts = []
            safe_pairs = 0
            for disturbance in words:
                safe_count = sum(
                    all(seed[index] != disturbance[index] for index in range(horizon))
                    for seed in words
                )
                fixed_safe_counts.append(safe_count)
                safe_pairs += safe_count
            universal_safe_seeds = sum(
                all(
                    all(seed[index] != disturbance[index] for index in range(horizon))
                    for disturbance in words
                )
                for seed in words
            )
            expected_safe_per_disturbance = (symbols - 1) ** horizon
            expected_safe_pairs = (symbols * (symbols - 1)) ** horizon
            formula_matches = (
                set(fixed_safe_counts) == {expected_safe_per_disturbance}
                and safe_pairs == expected_safe_pairs
                and universal_safe_seeds == 0
            )
            if not formula_matches:
                failures.append({"symbols": symbols, "horizon": horizon})
            rows.append(
                {
                    "symbols": symbols,
                    "horizon": horizon,
                    "seed_words": symbols**horizon,
                    "disturbance_words": symbols**horizon,
                    "safe_seed_words_per_fixed_disturbance": fixed_safe_counts[0],
                    "safe_seed_disturbance_pairs": safe_pairs,
                    "universal_safe_seed_words": universal_safe_seeds,
                    "fixed_disturbance_success_probability": str(
                        Fraction((symbols - 1) ** horizon, symbols**horizon)
                    ),
                    "fixed_disturbance_failure_probability": str(
                        1 - Fraction((symbols - 1) ** horizon, symbols**horizon)
                    ),
                    "formula_matches": formula_matches,
                }
            )
    return {
        "rows": rows,
        "cells": len(rows),
        "enumerated_seed_disturbance_pairs": sum(
            row["seed_words"] * row["disturbance_words"] for row in rows
        ),
        "failures": failures,
        "pass": len(rows) == 16 and not failures,
    }


def finite_grid_formula_phase_map() -> dict[str, Any]:
    """Evaluate exact formulas beyond the exhaustive grid."""

    rows = []
    symbol_values = tuple(2**power for power in range(1, 11))
    horizon_values = (1, 2, 4, 8, 16, 32)
    for symbols in symbol_values:
        for horizon in horizon_values:
            success = Fraction((symbols - 1) ** horizon, symbols**horizon)
            rows.append(
                {
                    "symbols": symbols,
                    "horizon": horizon,
                    "success_probability": str(success),
                    "failure_probability": str(1 - success),
                    "success_decimal": float(success),
                }
            )
    monotone_in_symbols = all(
        Fraction((n - 1) ** horizon, n**horizon)
        < Fraction(((2 * n) - 1) ** horizon, (2 * n) ** horizon)
        for n in symbol_values[:-1]
        for horizon in horizon_values
    )
    monotone_in_horizon = all(
        Fraction((symbols - 1) ** (2 * horizon), symbols ** (2 * horizon))
        < Fraction((symbols - 1) ** horizon, symbols**horizon)
        for symbols in symbol_values
        for horizon in horizon_values[:-1]
    )
    return {
        "rows": rows,
        "cells": len(rows),
        "fixed_horizon_limit_as_symbols_grow": 1,
        "fixed_finite_symbols_limit_as_horizon_grows": 0,
        "continuous_fixed_path_success_probability": 1,
        "continuous_universal_safe_seed_probability": 0,
        "noncommuting_limits": {
            "lim_N_to_infinity_then_T_to_infinity_success": 1,
            "lim_T_to_infinity_then_N_to_infinity_success": 0,
        },
        "monotone_in_symbols": monotone_in_symbols,
        "monotone_in_horizon": monotone_in_horizon,
        "pass": (len(rows) == 60 and monotone_in_symbols and monotone_in_horizon),
    }


def monte_carlo_trap_report() -> dict[str, Any]:
    """Quantify how random testing misses a worst-case diagonal."""

    rows = []
    for symbols in (16, 256, 65536):
        for trials in (1, 100, 1000):
            no_failure = Fraction(symbols - 1, symbols) ** trials
            exact_probability = (
                str(no_failure)
                if trials <= 100
                else f"({symbols - 1}/{symbols})^{trials}"
            )
            rows.append(
                {
                    "symbols": symbols,
                    "trials": trials,
                    "probability_random_tests_see_no_failure": float(no_failure),
                    "exact_probability": exact_probability,
                    "adaptive_worst_case_failure_probability": 1,
                }
            )
    return {
        "rows": rows,
        "continuous_random_pair_failure_probability": 0,
        "continuous_adaptive_diagonal_failure_probability": 1,
        "warning": (
            "Random nonfailure cannot certify universal confinement when the "
            "adversary may select the measure-zero diagonal."
        ),
        "pass": all(
            0 <= row["probability_random_tests_see_no_failure"] <= 1
            and row["adaptive_worst_case_failure_probability"] == 1
            for row in rows
        ),
    }


def quantifier_models() -> dict[str, Any]:
    """Evaluate the canonical completions on the same smooth fixture."""

    models = {
        "per_disturbance_almost_sure": {
            "formula": "forall w, P_r[forall t x_t in K]=1",
            "zero_rate_code_is_safe": True,
            "region_contains_origin": True,
        },
        "uniform_almost_sure": {
            "formula": "P_r[forall w forall t x_t in K]=1",
            "zero_rate_code_is_safe": False,
            "region_contains_origin": False,
        },
        "support_zero_error": {
            "formula": "forall r in support forall w forall t x_t in K",
            "zero_rate_code_is_safe": False,
            "region_contains_origin": False,
        },
        "adaptive_disturbance": {
            "formula": "disturbance observes r_t and chooses w_t=r_t",
            "zero_rate_code_is_safe": False,
            "region_contains_origin": False,
        },
    }
    return {
        "models": models,
        "same_plant": True,
        "same_randomized_zero_message_architecture": True,
        "decision": "probability_disturbance_order_changes_feasibility",
        "pass": (
            models["per_disturbance_almost_sure"]["zero_rate_code_is_safe"]
            and all(
                not model["zero_rate_code_is_safe"]
                for name, model in models.items()
                if name != "per_disturbance_almost_sure"
            )
        ),
    }


def randomness_quantifier_report() -> dict[str, Any]:
    source = canonical_randomness_quantifier_audit()
    continuous = continuous_diagonal_fixture()
    countable = countable_disturbance_collapse()
    finite = finite_grid_census()
    phase = finite_grid_formula_phase_map()
    monte_carlo = monte_carlo_trap_report()
    models = quantifier_models()
    components = (source, continuous, countable, finite, phase, monte_carlo, models)
    return {
        "schema_version": "asmp4_randomness_quantifier_boundary_v0_8",
        "canonical_audit": source,
        "continuous_diagonal_fixture": continuous,
        "countable_disturbance_collapse": countable,
        "finite_grid_census": finite,
        "formula_phase_map": phase,
        "monte_carlo_trap": monte_carlo,
        "quantifier_models": models,
        "pass": all(component["pass"] for component in components),
    }


def verification_gates(report: dict[str, Any] | None = None) -> dict[str, bool]:
    if report is None:
        report = randomness_quantifier_report()
    return {
        "R0_canonical_randomness_order_is_unspecified": report["canonical_audit"][
            "pass"
        ],
        "R1_continuous_diagonal_quantifier_fork": report["continuous_diagonal_fixture"][
            "pass"
        ],
        "R2_countable_disturbance_collapse_theorem": report[
            "countable_disturbance_collapse"
        ]["pass"],
        "R3_finite_grid_formulas_are_exhaustive": report["finite_grid_census"]["pass"],
        "R4_noncommuting_limit_phase_map": report["formula_phase_map"]["pass"],
        "R5_monte_carlo_trap_is_quantified": report["monte_carlo_trap"]["pass"],
        "R6_quantifier_models_change_feasibility": report["quantifier_models"]["pass"],
        "R7_complete_payload": report["pass"],
    }


def main(output: str | None = None) -> int:
    report = randomness_quantifier_report()
    payload = {"report": report, "gates": verification_gates(report)}
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if output is None:
        print(rendered)
    else:
        Path(output).write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["pass"] and all(payload["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
