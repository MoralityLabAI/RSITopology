"""BM-05: conditional robust monitoring-and-restoration certificate gate.

Binary holonomy (K=F2); every full-cycle pattern is corrected for its known
shift before majority aggregation. A trusted, externally established
restoration attestation bounds conditional false accepts rho_i and false
rejects kappa_i for at most B nonzero-shift interventions. No audit outcomes
are inferred by the tested monitor itself.

The gate combines exact robust parity minimax risk with a union bound for
failed restoration, plus an explicit non-inert authorization floor, and an
integer worst-case resource budget. It is sufficient, not generally optimal.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

try:
    from .correlated_minimax import (
        conditional_minimax_error, conditional_false_restoration_union_bound,
    )
except ImportError:
    from correlated_minimax import (
        conditional_minimax_error, conditional_false_restoration_union_bound,
    )


@dataclass(frozen=True)
class RobustCertification:
    parity_error_bound: Fraction
    authorized_wrong_bound: Fraction
    correct_authorization_lower_bound: Fraction
    worst_case_resource_units: int
    passes: bool


def robust_monitor_certificate(
    length: int,
    per_bit_conditional_error_cap: Fraction,
    samples: int,
    *,
    false_restoration_accept_caps: tuple[Fraction, ...] = (),
    genuine_restoration_reject_caps: tuple[Fraction, ...] = (),
    observation_units: int = 1,
    shift_bit_units: int = 1,
    restoration_audit_units: int = 1,
    max_path_units: int = 64,
    maximum_false_authorization: Fraction = Fraction(1, 5),
    minimum_correct_authorization: Fraction = Fraction(4, 5),
) -> RobustCertification:
    """A two-sided, finite source-conditional certificate.

    Both audit cap vectors have one entry per *potential* nonzero shift and
    each bound holds conditional on the preceding observed/audited history.
    For nonzero actions the root attestor is assumed to run and must approve
    to authorize. The shift is externally known and correctly applied.

    The parity signal under good restorations has two symmetric labels.
    If either hypothesis is true, authorized wrong output is <= parity
    majority error + sum(false-accept caps).
    When genuine restoration always succeeds, correct authorization is
    >= 1 - majority error - sum(false-reject caps).

    Nature may correlate readout bits within an episode and adapt their
    distribution based on history, subject to the per-bit conditional cap,
    independently of the current fresh uniform vertex labeling.
    """
    fa = tuple(Fraction(x) for x in false_restoration_accept_caps)
    fr = tuple(Fraction(x) for x in genuine_restoration_reject_caps)
    if len(fa) != len(fr) or len(fa) > samples or samples < 1:
        raise ValueError("audit lengths must match and fit within sample count")
    if any(not 0 <= x <= 1 for x in fa + fr):
        raise ValueError("attestation error caps must lie in [0,1]")
    if (observation_units < 1 or shift_bit_units < 0
        or restoration_audit_units < 1 or max_path_units < 0):
        raise ValueError("registered audit and observation costs are required")
    alpha = Fraction(maximum_false_authorization)
    utility_floor = Fraction(minimum_correct_authorization)
    if not 0 <= alpha <= 1 or not 0 <= utility_floor <= 1:
        raise ValueError("certificate thresholds must lie in [0,1]")
    parity_risk = conditional_minimax_error(
        length, Fraction(per_bit_conditional_error_cap), samples
    )
    false_budget = conditional_false_restoration_union_bound(fa)
    reject_budget = conditional_false_restoration_union_bound(fr)
    bound_wrong = min(Fraction(1), parity_risk + false_budget)
    bound_right = max(Fraction(0), 1 - parity_risk - reject_budget)
    worst_units = (samples * observation_units
                   + len(fa) * (shift_bit_units + restoration_audit_units))
    return RobustCertification(
        parity_error_bound=parity_risk,
        authorized_wrong_bound=bound_wrong,
        correct_authorization_lower_bound=bound_right,
        worst_case_resource_units=worst_units,
        passes=(bound_wrong <= alpha
                and bound_right >= utility_floor
                and worst_units <= max_path_units),
    )
