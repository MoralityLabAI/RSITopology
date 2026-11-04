"""Independent structural and exact-arithmetic verifier for ASMP-4 v0.2."""

from __future__ import annotations

import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def minimum_one_step_actions(
    transitions: tuple[str, ...], partial_observation: bool
) -> int | None:
    """Independent set-cover calculation for the tiny transition census."""

    states = ("L", "R")
    actions = ("l", "r")
    transition = dict(zip(itertools.product(states, actions), transitions, strict=True))
    groups = (states,) if partial_observation else (("L",), ("R",))
    valid_by_group: list[tuple[str, ...]] = []
    for group in groups:
        valid = tuple(
            action
            for action in actions
            if all(transition[(state, action)] in states for state in group)
        )
        if not valid:
            return None
        valid_by_group.append(valid)
    return min(len(set(selection)) for selection in itertools.product(*valid_by_group))


def independent_census() -> dict[str, object]:
    histogram = {"1": 0, "2": 0, "infeasible": 0}
    budget_cells = 0
    predicted_feasible = 0
    for transitions in itertools.product(("L", "R", "BAD"), repeat=4):
        for partial in (False, True):
            minimum = minimum_one_step_actions(transitions, partial)
            histogram["infeasible" if minimum is None else str(minimum)] += 1
            for read_cap, write_cap in itertools.product((1, 2), repeat=2):
                budget_cells += 1
                predicted_feasible += int(
                    minimum is not None and read_cap >= minimum and write_cap >= minimum
                )
    return {
        "plant_observation_pairs": sum(histogram.values()),
        "budget_cells": budget_cells,
        "predicted_feasible_budget_cells": predicted_feasible,
        "minimum_transcript_histogram": histogram,
    }


def ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def independent_formula_checks() -> dict[str, object]:
    scalar = [max(1, ceil_fraction(Fraction(2**horizon, 4))) for horizon in range(1, 7)]
    shear = [max(1, ceil_fraction(Fraction(horizon, 2))) for horizon in range(1, 101)]
    diagonal = []
    for horizon in range(1, 5):
        first = max(1, ceil_fraction(Fraction(2**horizon, 4)))
        second = max(1, ceil_fraction(Fraction(3**horizon, 9)))
        third = max(1, ceil_fraction(Fraction(1, 2**horizon)))
        diagonal.append(first * second * third)
    return {
        "scalar_counts": scalar,
        "shear_first_four": shear[:4],
        "shear_horizon_100": shear[-1],
        "shear_rate_horizon_100": math.log2(shear[-1]) / 100,
        "diagonal_counts": diagonal,
    }


def independent_delay_relay_check() -> dict[str, object]:
    rows = []
    for delay in range(4):
        for horizon in range(6):
            words: set[tuple[int, ...]] = set()
            for emissions in itertools.product((0, 1), repeat=max(0, horizon - delay)):
                parity = 0
                word = []
                for event in range(horizon):
                    if event >= delay:
                        parity ^= emissions[event - delay]
                    word.append(parity)
                words.add(tuple(word))
            rows.append(
                {
                    "delay": delay,
                    "horizon": horizon,
                    "count": len(words),
                    "expected": 2 ** max(0, horizon - delay),
                }
            )
    return {"rows": rows, "pass": all(row["count"] == row["expected"] for row in rows)}


def theorem_sentinels() -> dict[str, bool]:
    theorem = (HERE / "THEOREM.md").read_text(encoding="utf-8")
    audit = (HERE / "RESOLUTION_AUDIT.md").read_text(encoding="utf-8")
    return {
        "causal_data_processing": "|M_w^C(T)| <= |M_r^C(T)|" in theorem,
        "relay_language_identity": (
            "|M_r^(C^=)(T)| = |M_w^(C^=)(T)| = |M_w^C(T)|" in theorem
            and "warm-up prefix" in theorem
        ),
        "finite_full_region": (
            "B_r >= log2 nu_T(K_0,K)" in theorem
            and "B_w >= log2 nu_T(K_0,K)" in theorem
        ),
        "control_tree_variational_formula": (
            "nu_T(K_0,K) = min_(pi in Pi_T^safe) |L_T(pi)|" in theorem
        ),
        "asymptotic_full_region": (
            "[h_perp(K_0,K),infinity) x [h_perp(K_0,K),infinity)" in theorem
        ),
        "arbitrary_initial_set": (
            "allows an arbitrary nonempty `K_0` contained in `K`" in theorem
        ),
        "regenerative_finite_block_corollary": (
            "h_perp^reg(K) =" in theorem
            and "inf_(T>=1)        (1/T) log2 nu_T^reg(K)" in theorem
        ),
        "coordinate_invariance": "control congruence" in theorem,
        "finite_margin": ("nu_T([-delta,delta],[-L,L]) = ceil(a^T delta/L)" in theorem),
        "authority_boundary": "### Actuator authority" in theorem,
        "all_positive_obligations": audit.count("| Satisfied |") == 6,
        "negative_obligations": ("Both requirements are therefore satisfied." in audit),
        "empirical_firewall": (
            "The resolution remains valid or invalid with the proof" in audit
        ),
    }


def registry_obligation_check() -> dict[str, object]:
    registry = json.loads(
        (HERE.parent / "problem_set_v0_1.json").read_text(encoding="utf-8")
    )
    claim = json.loads(
        (HERE / "resolution_claim_v0_2.json").read_text(encoding="utf-8")
    )
    problem = next(
        item for item in registry["problems"] if item["id"] == claim["problem_id"]
    )
    positive_expected = set(problem["positive_resolution_requires"])
    negative_expected = set(problem["negative_resolution_requires"])
    positive_actual = set(claim["positive_obligation_evidence"])
    negative_actual = set(claim["negative_obligation_evidence"])
    return {
        "problem_id": claim["problem_id"],
        "positive_expected": sorted(positive_expected),
        "positive_actual": sorted(positive_actual),
        "negative_expected": sorted(negative_expected),
        "negative_actual": sorted(negative_actual),
        "positive_exact": positive_actual == positive_expected,
        "negative_exact": negative_actual == negative_expected,
        "negative_resolution_allowed": problem["negative_resolution_allowed"],
        "empirical_resolution_forbidden": not problem["empirical_resolution_allowed"],
        "claim_is_nonempirical": not claim["empirical_resolution"],
    }


def verify() -> dict[str, object]:
    census = independent_census()
    formulas = independent_formula_checks()
    delay_relay = independent_delay_relay_check()
    sentinels = theorem_sentinels()
    obligations = registry_obligation_check()
    checks = {
        "V0_independent_census_universe": (
            census["plant_observation_pairs"] == 162 and census["budget_cells"] == 648
        ),
        "V1_independent_census_histogram": (
            census["minimum_transcript_histogram"]
            == {"1": 112, "2": 8, "infeasible": 42}
        ),
        "V2_scalar_exact_counts": formulas["scalar_counts"] == [1, 1, 2, 4, 8, 16],
        "V3_diagonal_exact_counts": formulas["diagonal_counts"] == [1, 1, 6, 36],
        "V4_shear_polynomial_counts": (
            formulas["shear_first_four"] == [1, 1, 2, 2]
            and formulas["shear_horizon_100"] == 50
            and formulas["shear_rate_horizon_100"] < 0.06
        ),
        "V5_fixed_fifo_delay_relay_counts": delay_relay["pass"]
        and len(delay_relay["rows"]) == 24,
        "V6_theorem_obligation_sentinels": all(sentinels.values()),
        "V7_registry_obligations_exact": (
            obligations["positive_exact"]
            and obligations["negative_exact"]
            and obligations["negative_resolution_allowed"]
            and obligations["empirical_resolution_forbidden"]
            and obligations["claim_is_nonempirical"]
        ),
    }
    return {
        "schema_version": "asmp4_serial_collapse_independent_verification_v0_2",
        "census": census,
        "formulas": formulas,
        "fixed_fifo_delay_relay": delay_relay,
        "theorem_sentinels": sentinels,
        "registry_obligations": obligations,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    payload = verify()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
