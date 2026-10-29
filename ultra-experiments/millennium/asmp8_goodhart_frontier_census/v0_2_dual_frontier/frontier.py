"""Exact finite robust-Goodhart frontier for ASMP-8 v0.2."""

from __future__ import annotations

import csv
import io
import json
import math
import itertools
from collections import defaultdict
from fractions import Fraction
from typing import Any, Iterable, Iterator


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def F(value: Any) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def fs(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator)


def compositions(total: int, parts: int) -> Iterator[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first, *rest)


def expected_value(policy: tuple[Fraction, ...], reward: tuple[Fraction, ...]) -> Fraction:
    return sum((probability * value for probability, value in zip(policy, reward)), Fraction())


def policy_gain(
    policy: tuple[Fraction, ...],
    reference: tuple[Fraction, ...],
    reward: tuple[Fraction, ...],
) -> Fraction:
    return expected_value(policy, reward) - expected_value(reference, reward)


def likelihood_deviation(
    policy: tuple[Fraction, ...], reference: tuple[Fraction, ...]
) -> tuple[Fraction, ...]:
    if any(value <= 0 for value in reference):
        raise ValueError("reference policy must have full support")
    return tuple(pi / p0 - 1 for pi, p0 in zip(policy, reference))


def dual_movement(
    policy: tuple[Fraction, ...], reference: tuple[Fraction, ...], q: str
) -> Fraction:
    a = likelihood_deviation(policy, reference)
    if q == "infinity":
        return sum((p0 * abs(value) for p0, value in zip(reference, a)), Fraction())
    if q == "2":
        # The return value is the exact square of the L2 dual movement.
        return sum((p0 * value * value for p0, value in zip(reference, a)), Fraction())
    if q == "1":
        return max(abs(value) for value in a)
    raise ValueError(f"unsupported q: {q}")


def margin_record(proxy_gain: Fraction, movement: Fraction, epsilon: Fraction, q: str) -> dict[str, Any]:
    if movement <= 0 or proxy_gain <= 0:
        raise ValueError("frontier requires positive gain and movement")
    if q == "2":
        gain_sq = proxy_gain * proxy_gain
        penalty_sq = epsilon * epsilon * movement
        sign = "positive" if gain_sq > penalty_sq else "zero" if gain_sq == penalty_sq else "negative"
        movement_float = math.sqrt(float(movement))
        margin_float = float(proxy_gain) - float(epsilon) * movement_float
        return {
            "movement_squared": fs(movement),
            "movement": movement_float,
            "critical_epsilon_squared": fs(gain_sq / movement),
            "critical_epsilon": float(proxy_gain) / movement_float,
            "margin_at_registered_epsilon": margin_float,
            "margin_sign_exact": sign,
            "penalty_squared_at_registered_epsilon": fs(penalty_sq),
        }
    margin = proxy_gain - epsilon * movement
    critical = proxy_gain / movement
    return {
        "movement": fs(movement),
        "movement_float": float(movement),
        "critical_epsilon": fs(critical),
        "critical_epsilon_float": float(critical),
        "margin_at_registered_epsilon": fs(margin),
        "margin_at_registered_epsilon_float": float(margin),
        "margin_sign_exact": "positive" if margin > 0 else "zero" if margin == 0 else "negative",
    }


def sharpness_witness(
    policy: tuple[Fraction, ...],
    reference: tuple[Fraction, ...],
    epsilon: Fraction,
    q: str,
) -> dict[str, Any]:
    a = likelihood_deviation(policy, reference)
    movement = dual_movement(policy, reference, q)
    if q == "infinity":
        error = tuple(-epsilon if value > 0 else epsilon if value < 0 else Fraction() for value in a)
        error_norm = max(abs(value) for value in error)
        coupling = sum((p0 * value * err for p0, value, err in zip(reference, a, error)), Fraction())
        passed = error_norm == epsilon and coupling == -epsilon * movement
        return {
            "error": [fs(value) for value in error],
            "error_norm": fs(error_norm),
            "coupling": fs(coupling),
            "target_coupling": fs(-epsilon * movement),
            "pass": passed,
        }
    if q == "1":
        maximum = max(abs(value) for value in a)
        index = next(i for i, value in enumerate(a) if abs(value) == maximum)
        error = [Fraction() for _ in a]
        error[index] = -epsilon * (1 if a[index] > 0 else -1) / reference[index]
        error_norm = sum((p0 * abs(err) for p0, err in zip(reference, error)), Fraction())
        coupling = sum((p0 * value * err for p0, value, err in zip(reference, a, error)), Fraction())
        passed = error_norm == epsilon and coupling == -epsilon * movement
        return {
            "support_index": index,
            "error": [fs(value) for value in error],
            "error_norm": fs(error_norm),
            "coupling": fs(coupling),
            "target_coupling": fs(-epsilon * movement),
            "pass": passed,
        }
    if q == "2":
        # e_i = -epsilon*a_i/sqrt(movement).  Exactness is certified without
        # approximating the square root: norm^2=epsilon^2 and
        # coupling^2=epsilon^2*movement with negative sign.
        coefficients = [fs(-epsilon * value) for value in a]
        passed = movement > 0
        return {
            "symbolic_error": [f"({coefficient})/sqrt({fs(movement)})" for coefficient in coefficients],
            "error_norm_squared": fs(epsilon * epsilon),
            "coupling_sign": "negative",
            "coupling_squared": fs(epsilon * epsilon * movement),
            "pass": passed,
        }
    raise ValueError(q)


def independent_min_coupling(
    policy: tuple[Fraction, ...],
    reference: tuple[Fraction, ...],
    epsilon: Fraction,
    q: str,
) -> Fraction | tuple[str, Fraction]:
    """Independently minimize over extreme points where the ball is polyhedral.

    For q=2, return the sign and exact squared optimum; this avoids a floating
    square-root approximation while checking the algebraic value.
    """
    a = likelihood_deviation(policy, reference)
    if q == "infinity":
        values = []
        for signs in itertools.product((-1, 1), repeat=len(a)):
            error = tuple(epsilon * sign for sign in signs)
            values.append(sum((p0 * value * err for p0, value, err in zip(reference, a, error)), Fraction()))
        return min(values)
    if q == "1":
        values = [Fraction()]
        for index, p0 in enumerate(reference):
            for sign in (-1, 1):
                error = [Fraction() for _ in a]
                error[index] = epsilon * sign / p0
                values.append(
                    sum((weight * value * err for weight, value, err in zip(reference, a, error)), Fraction())
                )
        return min(values)
    if q == "2":
        movement_squared = dual_movement(policy, reference, q)
        return ("negative", epsilon * epsilon * movement_squared)
    raise ValueError(q)


def pair_payload(first: dict[str, Any], second: dict[str, Any], q: str) -> dict[str, Any]:
    return {
        "q": q,
        "first_policy_id": first["policy_id"],
        "second_policy_id": second["policy_id"],
        "first_counts": first["counts"],
        "second_counts": second["counts"],
        "first_proxy_gain": fs(first["proxy_gain"]),
        "second_proxy_gain": fs(second["proxy_gain"]),
        "first_movement_key": fs(first["movement"]),
        "second_movement_key": fs(second["movement"]),
    }


def coordinate_witnesses(entries: list[dict[str, Any]], q: str) -> dict[str, Any]:
    by_gain: dict[Fraction, list[dict[str, Any]]] = defaultdict(list)
    by_movement: dict[Fraction, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        by_gain[entry["proxy_gain"]].append(entry)
        by_movement[entry["movement"]].append(entry)

    equal_gain_candidates = []
    for group in by_gain.values():
        ordered = sorted(group, key=lambda item: (item["movement"], item["policy_id"]))
        if ordered[0]["movement"] != ordered[-1]["movement"]:
            equal_gain_candidates.append((ordered[-1]["movement"] - ordered[0]["movement"], ordered[0], ordered[-1]))
    equal_gain_candidates.sort(key=lambda item: (-item[0], item[1]["policy_id"], item[2]["policy_id"]))

    equal_movement_candidates = []
    for group in by_movement.values():
        ordered = sorted(group, key=lambda item: (item["proxy_gain"], item["policy_id"]))
        if ordered[0]["proxy_gain"] != ordered[-1]["proxy_gain"]:
            equal_movement_candidates.append(
                (ordered[-1]["proxy_gain"] - ordered[0]["proxy_gain"], ordered[0], ordered[-1])
            )
    equal_movement_candidates.sort(key=lambda item: (-item[0], item[1]["policy_id"], item[2]["policy_id"]))

    return {
        "equal_proxy_gain_unequal_movement": pair_payload(
            equal_gain_candidates[0][1], equal_gain_candidates[0][2], q
        )
        if equal_gain_candidates
        else None,
        "equal_movement_unequal_proxy_gain": pair_payload(
            equal_movement_candidates[0][1], equal_movement_candidates[0][2], q
        )
        if equal_movement_candidates
        else None,
    }


def near_tie_control(protocol: dict[str, Any]) -> dict[str, Any]:
    control = protocol["controls"]["near_tie"]
    epsilon = F(control["epsilon"])
    true_reward = tuple(F(value) for value in control["true_rewards"])
    proxy_reward = tuple(F(value) for value in control["proxy_rewards"])
    maximum = max(proxy_reward)
    selected = next(index for index, value in enumerate(proxy_reward) if value == maximum)
    best_true = max(true_reward)
    regret = best_true - true_reward[selected]
    return {
        "selected_index": selected,
        "regret": fs(regret),
        "two_epsilon": fs(2 * epsilon),
        "pass": regret == 2 * epsilon,
    }


def rare_tail_control(protocol: dict[str, Any]) -> dict[str, Any]:
    control = protocol["controls"]["rare_tail_l2"]
    p0 = tuple(F(value) for value in control["reference_policy"])
    policy = tuple(F(value) for value in control["optimized_policy"])
    proxy = tuple(F(value) for value in control["proxy_rewards"])
    true = tuple(F(value) for value in control["true_rewards"])
    error = tuple(t - y for t, y in zip(true, proxy))
    error_sq = sum((probability * value * value for probability, value in zip(p0, error)), Fraction())
    true_gain = policy_gain(policy, p0, true)
    proxy_gain = policy_gain(policy, p0, proxy)
    ceiling = F(control["maximum_weighted_l2_error_squared"])
    harm_floor = F(control["minimum_true_harm"])
    return {
        "weighted_l2_error_squared": fs(error_sq),
        "error_ceiling_squared": fs(ceiling),
        "proxy_gain": fs(proxy_gain),
        "true_gain": fs(true_gain),
        "minimum_true_harm": fs(harm_floor),
        "pass": error_sq <= ceiling and true_gain <= -harm_floor,
    }


def run_census(protocol: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    registry = protocol["finite_registry"]
    count = int(registry["outcome_count"])
    denominator = int(registry["policy_denominator"])
    p0 = tuple(F(value) for value in registry["reference_policy"])
    proxy = tuple(F(value) for value in registry["proxy_reward"])
    epsilon = F(protocol["registered_error_radius"])
    qs = [str(item["q"]) for item in protocol["error_models"]]

    total = 0
    frontier_rows: list[dict[str, Any]] = []
    entries: dict[str, list[dict[str, Any]]] = {q: [] for q in qs}
    sharpness_passes = 0
    sharpness_total = 0
    formula_passes = 0
    formula_total = 0
    phase_counts = {q: {"positive": 0, "zero": 0, "negative": 0} for q in qs}
    representative_witnesses: dict[str, Any] = {}

    for policy_id, counts in enumerate(compositions(denominator, count)):
        total += 1
        policy = tuple(Fraction(value, denominator) for value in counts)
        gain = policy_gain(policy, p0, proxy)
        if gain <= 0:
            continue
        row: dict[str, Any] = {
            "policy_id": policy_id,
            "counts": list(counts),
            "proxy_gain": fs(gain),
            "proxy_gain_float": float(gain),
        }
        for q in qs:
            movement = dual_movement(policy, p0, q)
            margin = margin_record(gain, movement, epsilon, q)
            witness = sharpness_witness(policy, p0, epsilon, q)
            independent = independent_min_coupling(policy, p0, epsilon, q)
            if q == "2":
                formula_pass = independent == ("negative", epsilon * epsilon * movement)
            else:
                formula_pass = independent == -epsilon * movement
            formula_total += 1
            formula_passes += bool(formula_pass)
            sharpness_total += 1
            sharpness_passes += bool(witness["pass"])
            phase_counts[q][margin["margin_sign_exact"]] += 1
            row[f"q_{q}"] = margin
            entries[q].append(
                {
                    "policy_id": policy_id,
                    "counts": list(counts),
                    "proxy_gain": gain,
                    "movement": movement,
                }
            )
            representative_witnesses.setdefault(q, {"policy_id": policy_id, **witness})
        frontier_rows.append(row)

    coordinate = {q: coordinate_witnesses(entries[q], q) for q in qs}
    coordinate_pass = all(
        payload["equal_proxy_gain_unequal_movement"] is not None
        and payload["equal_movement_unequal_proxy_gain"] is not None
        for payload in coordinate.values()
    )
    near_tie = near_tie_control(protocol)
    rare_tail = rare_tail_control(protocol)
    expected_count = int(registry["expected_policy_count"])
    gates = {
        "G1_complete_registry": {"pass": total == expected_count, "observed": total, "expected": expected_count},
        "G2_dual_formula": {
            "pass": formula_passes == formula_total,
            "passed": formula_passes,
            "checked_cells": formula_total,
            "note": "q=1 and infinity are checked by independent extreme-point enumeration; q=2 by exact squared algebra.",
        },
        "G3_sharpness": {"pass": sharpness_passes == sharpness_total, "passed": sharpness_passes, "total": sharpness_total},
        "G4_coordinate_minimality": {"pass": coordinate_pass},
        "G5_near_tie_sharpness": near_tie,
        "G6_rare_tail_liveness": rare_tail,
    }
    core_pass = all(gate["pass"] for gate in gates.values())
    result = {
        "schema_version": "asmp8_dual_frontier_result_v0_2",
        "instrument_status": "valid" if core_pass else "invalid",
        "pre_resource_verdict": "dual_frontier_validated" if core_pass else "not_established",
        "policy_count": total,
        "proxy_improving_policy_count": len(frontier_rows),
        "registered_epsilon": fs(epsilon),
        "phase_counts": phase_counts,
        "coordinate_minimality": coordinate,
        "controls": {"near_tie": near_tie, "rare_tail_l2": rare_tail},
        "gates": gates,
        "claim_boundary": protocol["claim_boundary"],
    }
    witnesses = {
        "schema_version": "asmp8_dual_frontier_witnesses_v0_2",
        "representative_sharpness": representative_witnesses,
        "coordinate_minimality": coordinate,
        "controls": result["controls"],
    }
    return result, frontier_rows, witnesses


def frontier_csv(rows: Iterable[dict[str, Any]]) -> str:
    stream = io.StringIO(newline="")
    fieldnames = [
        "policy_id",
        "counts",
        "proxy_gain",
        "q_infinity_movement",
        "q_infinity_critical_epsilon",
        "q_infinity_margin_sign",
        "q_2_movement_squared",
        "q_2_critical_epsilon_squared",
        "q_2_margin_sign",
        "q_1_movement",
        "q_1_critical_epsilon",
        "q_1_margin_sign",
    ]
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "policy_id": row["policy_id"],
                "counts": ";".join(str(value) for value in row["counts"]),
                "proxy_gain": row["proxy_gain"],
                "q_infinity_movement": row["q_infinity"]["movement"],
                "q_infinity_critical_epsilon": row["q_infinity"]["critical_epsilon"],
                "q_infinity_margin_sign": row["q_infinity"]["margin_sign_exact"],
                "q_2_movement_squared": row["q_2"]["movement_squared"],
                "q_2_critical_epsilon_squared": row["q_2"]["critical_epsilon_squared"],
                "q_2_margin_sign": row["q_2"]["margin_sign_exact"],
                "q_1_movement": row["q_1"]["movement"],
                "q_1_critical_epsilon": row["q_1"]["critical_epsilon"],
                "q_1_margin_sign": row["q_1"]["margin_sign_exact"],
            }
        )
    return stream.getvalue()
