"""Exact balanced-cover extremal calculation for ASMP-6 v0.2."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


FROZEN_COVER_LAW = "uniform"
FROZEN_MESSAGE_COUNT = 2
FROZEN_MESSAGE_PRIOR = (Fraction(1, 2), Fraction(1, 2))
FROZEN_ALPHABET_RANGE = (2, 31)
FROZEN_ENUMERATION_MAXIMUM = 9
FROZEN_PROTOCOL_ID = "ASMP6-BALANCED-COVER-v0.2"
FROZEN_PROTOCOL_SCHEMA = "asmp6_balanced_cover_protocol_v0_2"
FROZEN_PROTOCOL_FIELDS = {
    "alphabet_sizes",
    "claim_boundary",
    "cover_law",
    "independent_extremal_enumeration_maximum",
    "message_count",
    "message_prior",
    "protocol_id",
    "schema_version",
}
FROZEN_CLAIM_BOUNDARY = (
    "one-shot opaque-symbol laws only",
    "exactly two equiprobable messages only",
    "uniform benign cover law only",
    "exact message-averaged cover and exact per-message control only",
    "no learned or linguistic encoder",
    "no multiletter or ASMP-6 resolution claim",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def total_variation(left: Iterable[Fraction], right: Iterable[Fraction]) -> Fraction:
    return sum((abs(a - b) for a, b in zip(left, right)), Fraction()) / 2


def bayes_error(left: list[Fraction], right: list[Fraction]) -> Fraction:
    """Equal-prior Bayes error for the frozen two-message protocol."""

    return (1 - total_variation(left, right)) / 2


def protocol_binding_checks(protocol: dict[str, Any]) -> dict[str, bool]:
    """Bind executable semantics to the frozen uniform/equal-prior protocol."""

    try:
        prior = tuple(Fraction(value) for value in protocol["message_prior"])
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        prior = ()
    limits = protocol.get("alphabet_sizes", {})
    minimum = limits.get("minimum") if isinstance(limits, dict) else None
    maximum = limits.get("maximum") if isinstance(limits, dict) else None
    boundary = protocol.get("claim_boundary")
    return {
        "protocol_fields_are_exact": set(protocol) == FROZEN_PROTOCOL_FIELDS,
        "protocol_id_is_frozen": protocol.get("protocol_id") == FROZEN_PROTOCOL_ID,
        "protocol_schema_is_frozen": (
            protocol.get("schema_version") == FROZEN_PROTOCOL_SCHEMA
        ),
        "cover_law_is_uniform": protocol.get("cover_law") == FROZEN_COVER_LAW,
        "message_count_is_two": (
            type(protocol.get("message_count")) is int
            and protocol.get("message_count") == FROZEN_MESSAGE_COUNT
        ),
        "message_prior_is_equal_half": prior == FROZEN_MESSAGE_PRIOR,
        "registered_alphabet_range_is_2_through_31": (
            type(minimum) is int
            and type(maximum) is int
            and (minimum, maximum) == FROZEN_ALPHABET_RANGE
        ),
        "enumeration_maximum_is_nine": (
            type(protocol.get("independent_extremal_enumeration_maximum")) is int
            and protocol.get("independent_extremal_enumeration_maximum")
            == FROZEN_ENUMERATION_MAXIMUM
        ),
        "claim_boundary_is_frozen": (
            isinstance(boundary, list) and tuple(boundary) == FROZEN_CLAIM_BOUNDARY
        ),
    }


def validate_protocol_binding(protocol: dict[str, Any]) -> dict[str, bool]:
    checks = protocol_binding_checks(protocol)
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"protocol binding failed: {failed}")
    return checks


def optimal_balanced_laws(alphabet_size: int) -> tuple[list[Fraction], list[Fraction]]:
    """Construct an optimizer under exact averaged uniform cover."""

    if alphabet_size < 2:
        raise ValueError("alphabet_size must be at least two")
    radius = Fraction(1, alphabet_size)
    pairs = alphabet_size // 2
    deviations = [radius] * pairs + [-radius] * pairs
    if alphabet_size % 2:
        deviations.append(Fraction())
    p0 = [radius + value for value in deviations]
    p1 = [radius - value for value in deviations]
    return p0, p1


def sign_count_tv_upper_bound(alphabet_size: int) -> Fraction:
    """Dual/sign-count bound on TV(P0,P1) under averaged uniform cover.

    If `a` deviations are positive and `b` are negative, their common total
    mass is at most `min(a,b)/m`.  Hence L1(d) is at most
    `2*floor(m/2)/m`, which equals TV(P0,P1).
    """

    if alphabet_size < 2:
        raise ValueError("alphabet_size must be at least two")
    return Fraction(2 * (alphabet_size // 2), alphabet_size)


def theorem_cell(alphabet_size: int) -> dict[str, Any]:
    p0, p1 = optimal_balanced_laws(alphabet_size)
    cover = [Fraction(1, alphabet_size)] * alphabet_size
    average = [(left + right) / 2 for left, right in zip(p0, p1)]
    tv = total_variation(p0, p1)
    bound = sign_count_tv_upper_bound(alphabet_size)
    error = bayes_error(p0, p1)
    messagewise_error = bayes_error(cover, cover)
    return {
        "alphabet_size": alphabet_size,
        "parity": "even" if alphabet_size % 2 == 0 else "odd",
        "averaged_cover_exact": average == cover,
        "p0": [fraction_text(value) for value in p0],
        "p1": [fraction_text(value) for value in p1],
        "total_variation": fraction_text(tv),
        "dual_tv_upper_bound": fraction_text(bound),
        "bayes_error": fraction_text(error),
        "messagewise_bayes_error": fraction_text(messagewise_error),
        "perfect_decoding": error == 0,
        "optimality_gap": fraction_text(bound - tv),
    }


def robustness_probes() -> dict[str, dict[str, Any]]:
    p0, p1 = optimal_balanced_laws(7)
    permutation = (3, 0, 6, 2, 5, 1, 4)
    permuted_error = bayes_error([p0[i] for i in permutation], [p1[i] for i in permutation])
    original_error = bayes_error(p0, p1)
    return {
        "invariance": {
            "pass": permuted_error == original_error,
            "probe": "symbol_label_permutation",
        },
        "sensitivity": {
            "pass": theorem_cell(3)["perfect_decoding"] is False
            and theorem_cell(4)["perfect_decoding"] is True,
            "probe": "odd_to_even_divisibility_boundary",
        },
        "monotonicity": {
            "pass": all(
                Fraction(theorem_cell(m)["bayes_error"])
                <= Fraction(theorem_cell(m)["messagewise_bayes_error"])
                for m in range(2, 16)
            ),
            "probe": "relax_messagewise_cover_to_averaged_cover",
        },
        "anti_gaming": {
            "pass": all(theorem_cell(m)["optimality_gap"] == "0/1" for m in range(2, 16)),
            "probe": "witness_matches_sign_count_dual_bound",
        },
        "clean_control": {
            "pass": all(theorem_cell(m)["messagewise_bayes_error"] == "1/2" for m in range(2, 16)),
            "probe": "identical_message_laws_are_chance",
        },
    }


def compile_result(protocol: dict[str, Any]) -> dict[str, Any]:
    binding = validate_protocol_binding(protocol)
    limits = protocol["alphabet_sizes"]
    cells = [theorem_cell(size) for size in range(limits["minimum"], limits["maximum"] + 1)]
    probes = robustness_probes()
    gates = {
        "G0_frozen_protocol_binding": all(binding.values()),
        "G1_probability_feasibility": all(
            cell["averaged_cover_exact"]
            and all(Fraction(value) >= 0 for value in cell["p0"] + cell["p1"])
            and sum((Fraction(value) for value in cell["p0"]), Fraction()) == 1
            and sum((Fraction(value) for value in cell["p1"]), Fraction()) == 1
            for cell in cells
        ),
        "G2_exact_optimality": all(cell["optimality_gap"] == "0/1" for cell in cells),
        "G3_parity_boundary": all(
            cell["perfect_decoding"] == (cell["alphabet_size"] % 2 == 0) for cell in cells
        ),
        "G4_odd_error_formula": all(
            Fraction(cell["bayes_error"]) == Fraction(1, 2 * cell["alphabet_size"])
            for cell in cells
            if cell["alphabet_size"] % 2
        ),
        "G5_messagewise_control": all(cell["messagewise_bayes_error"] == "1/2" for cell in cells),
        "G6_metric_robustness": all(record["pass"] for record in probes.values()),
    }
    passed = all(gates.values())
    return {
        "schema_version": "asmp6_balanced_cover_result_v0_2",
        "protocol_id": protocol["protocol_id"],
        "protocol_binding": binding,
        "metric_robustness": probes,
        "task_result": "sharp_uniform_alphabet_parity_frontier" if passed else "not_established",
        "measurement_reliability": "awaiting_independent_verification" if passed else "failed",
        "claim_support": (
            "one_shot_two_equiprobable_messages_uniform_exact_average_cover"
            if passed
            else "none"
        ),
        "operational_decision": "await_independent_verification" if passed else "repair",
        "gates": gates,
        "cells": cells,
        "claim_boundary": protocol["claim_boundary"],
    }


def load_protocol(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
