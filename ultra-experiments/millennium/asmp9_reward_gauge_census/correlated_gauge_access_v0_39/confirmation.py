"""Prospective disjoint confirmation for ASMP-9 v0.39.

Do not call :func:`run_confirmation` until the registration and every sealed
input have been committed and pushed.
"""

from __future__ import annotations

from fractions import Fraction as Q

from gauge_leakage import (
    certify_access_alignment,
    certify_gauge_leakage,
    intervene_on_gauge,
    qstr,
)


CONFIRMATION_STRENGTHS = (
    (Q(6, 7), Q(1, 7)),
    (Q(7, 10), Q(3, 10)),
    (Q(11, 16), Q(5, 16)),
    (Q(9, 14), Q(5, 14)),
)

LEAKAGE_VECTORS = (
    ("spread_a", (Q(7, 9), Q(2, 9), Q(4, 9))),
    ("spread_b", (Q(1, 6), Q(5, 6), Q(1, 2))),
    ("flat_control", (Q(4, 11),) * 3),
)

INTERVENTION_PROBABILITIES = (Q(2, 7), Q(5, 9))
ALIGNMENTS = ("q0", "q0_complement", "q1", "q2", "constant")


def _leakage_row(name: str, probabilities: tuple[Q, ...]) -> dict:
    certificate = certify_gauge_leakage(probabilities)
    row = certificate.jsonable()
    row["vector_id"] = name
    row["gate_exact_half_range"] = (
        certificate.decision_relative_radius
        == certificate.analytic_radius
        == certificate.ordinary_radius
        and certificate.reverse_decision_relative == 0
        and certificate.reverse_ordinary == 0
    )
    return row


def _intervention_row(probability: Q) -> dict:
    observational = LEAKAGE_VECTORS[0][1]
    intervened = intervene_on_gauge(observational, probability)
    certificate = certify_gauge_leakage(intervened)
    return {
        "intervention_probability": qstr(probability),
        "postintervention_probabilities": [
            qstr(value) for value in intervened
        ],
        "decision_relative_radius": qstr(
            certificate.decision_relative_radius
        ),
        "ordinary_radius": qstr(certificate.ordinary_radius),
        "gate_erasure": (
            certificate.analytic_radius == 0
            and certificate.decision_relative_radius == 0
            and certificate.ordinary_radius == 0
        ),
    }


def _alignment_row(high: Q, low: Q, assignment: str) -> dict:
    certificate = certify_access_alignment(high, low, assignment)
    row = certificate.jsonable()
    gap = high - low
    half_gap = gap / 2
    expected = {
        "q0": Q(0),
        "q0_complement": Q(0),
        "q1": half_gap,
        "q2": high * low * gap,
        "constant": half_gap,
    }[assignment]
    row["gap"] = qstr(gap)
    row["half_gap"] = qstr(half_gap)
    row["registered_expected_deficiency"] = qstr(expected)
    row["gate_expected_value"] = (
        certificate.relative_substitution_deficiency == expected
        and certificate.ordinary_substitution_deficiency == expected
    )
    return row


def run_confirmation() -> dict:
    leakage_rows = [
        _leakage_row(name, probabilities)
        for name, probabilities in LEAKAGE_VECTORS
    ]
    intervention_rows = [
        _intervention_row(probability)
        for probability in INTERVENTION_PROBABILITIES
    ]
    alignment_rows = [
        _alignment_row(high, low, assignment)
        for high, low in CONFIRMATION_STRENGTHS
        for assignment in ALIGNMENTS
    ]

    same_radius_distinct_value = True
    for high, low in CONFIRMATION_STRENGTHS:
        block = {
            row["gauge_assignment"]: row
            for row in alignment_rows
            if row["high"] == qstr(high) and row["low"] == qstr(low)
        }
        radii = {
            block[name]["leakage_radius"]
            for name in ("q0", "q1", "q2")
        }
        values = {
            block[name]["relative_substitution_deficiency"]
            for name in ("q0", "q1", "q2")
        }
        same_radius_distinct_value &= len(radii) == 1 and len(values) == 3

    gates = {
        "L0_exact_leakage_radius": all(
            row["gate_exact_half_range"] for row in leakage_rows
        ),
        "I0_intervention_erasure": all(
            row["gate_erasure"] for row in intervention_rows
        ),
        "A0_aligned_substitution": all(
            row["gate_expected_value"]
            for row in alignment_rows
            if row["gauge_assignment"] in {"q0", "q0_complement"}
        ),
        "Q0_missing_query_threshold": all(
            row["gate_expected_value"]
            for row in alignment_rows
            if row["gauge_assignment"] in {"q1", "constant"}
        ),
        "T0_transverse_formula": all(
            row["gate_expected_value"]
            for row in alignment_rows
            if row["gauge_assignment"] == "q2"
        ),
        "U0_radius_value_separation": same_radius_distinct_value,
    }
    return {
        "status": (
            "correlated_gauge_access_alignment_established"
            if all(gates.values())
            else "registered_gate_failed"
        ),
        "gates": gates,
        "leakage_rows": leakage_rows,
        "intervention_rows": intervention_rows,
        "alignment_rows": alignment_rows,
        "row_counts": {
            "leakage": len(leakage_rows),
            "intervention": len(intervention_rows),
            "alignment": len(alignment_rows),
        },
    }
