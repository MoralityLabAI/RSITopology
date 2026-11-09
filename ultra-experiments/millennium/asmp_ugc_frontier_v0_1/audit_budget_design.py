"""BM-05: exactly costed Bayesian holonomy monitoring with restoration attestations.

This is a second, deliberately distinct component of BM-05. Each cycle episode
uses one chosen known shift x in F2^s. x=0 is passive; x!=0 incurs explicit
shift and externally attested restoration charges. The attestor is assumed
sound by this finite design and is NOT inferred from the monitoring channel.

The decision maker can stop at any time, must obey a worst-case pathwise
integer resource budget, and maximizes correct-identification probability
minus a known nonnegative price per spent resource unit. The posterior
state has unnormalized weights, so the Bellman equation is exact over Q.
No money/real-model cost calibration is implied by the integer units.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

try:
    from .finite_sample_monitor import noisy_failure_count_law
except ImportError:
    from finite_sample_monitor import noisy_failure_count_law


@dataclass(frozen=True)
class AuditResourceModel:
    observation_units: int = 1
    shift_bit_units: int = 1
    restoration_audit_units: int = 1
    utility_price_per_unit: Fraction = Fraction(1, 100)

    def __post_init__(self):
        if (self.observation_units < 1 or self.shift_bit_units < 0
            or self.restoration_audit_units < 1):
            raise ValueError("observations and restoration audits must be charged")
        price = Fraction(self.utility_price_per_unit)
        if price < 0:
            raise ValueError("utility price must be nonnegative")

    def action_cost(self, shift: int) -> int:
        if shift < 0:
            raise ValueError("shift must be nonnegative")
        return (self.observation_units
                + self.shift_bit_units * shift.bit_count()
                + (self.restoration_audit_units if shift else 0))


@dataclass(frozen=True)
class AuditDecision:
    net_utility: Fraction
    correct_identification: Fraction
    expected_units: Fraction
    expected_episodes: Fraction
    first_shift: int | None


def optimal_costed_monitor(
    q: int, length: int, episodes: int, max_resource_units: int,
    *,
    model: AuditResourceModel = AuditResourceModel(),
    readout_flip: Fraction = Fraction(0),
) -> AuditDecision:
    """Exact uniform-prior optimal stopping / action DP with hard budget.

    V(w,n,b)=max{ max_h w_h, max_{x:cost(x)<=b} [
      sum_k V((w_h p(k|h,x))_h,n-1,b-cost(x))
      - price*cost(x)*sum_h w_h ] }.

    Returned success, cost and episode expectations are under a uniform prior
    on the hidden holonomy and the optimal deterministic policy.
    """
    if q not in (2, 4) or not 1 <= length <= 4:
        raise ValueError("seed supports q=2 or 4 and length 1..4")
    if not 0 <= episodes <= 4 or not 0 <= max_resource_units <= 20:
        raise ValueError("seed supports <=4 episodes and <=20 resource units")
    eta = Fraction(readout_flip)
    if not 0 <= eta <= 1:
        raise ValueError("readout_flip must lie in [0,1]")
    price = Fraction(model.utility_price_per_unit)
    flat = noisy_failure_count_law(length, q, flat=True, flip_probability=eta)
    nonflat = noisy_failure_count_law(length, q, flat=False, flip_probability=eta)

    @lru_cache(maxsize=None)
    def value(
        weights: tuple[Fraction, ...], remaining: int, budget: int
    ) -> tuple[Fraction, Fraction, Fraction, Fraction, int | None]:
        # Tuple is net value, correct mass, cost mass, episode mass, first x.
        best = (max(weights), max(weights), Fraction(0), Fraction(0), None)
        if remaining == 0:
            return best
        weight_sum = sum(weights, Fraction(0))
        for shift in range(q):
            units = model.action_cost(shift)
            if units > budget:
                continue
            net = -price * weight_sum * units
            accuracy = Fraction(0)
            charge = weight_sum * units
            calls = weight_sum
            for k in range(length + 1):
                next_weights = tuple(
                    w * (flat[k] if h == shift else nonflat[k])
                    for h, w in enumerate(weights)
                )
                if sum(next_weights):
                    outcome = value(next_weights, remaining - 1, budget - units)
                    net += outcome[0]
                    accuracy += outcome[1]
                    charge += outcome[2]
                    calls += outcome[3]
            if net > best[0]:
                best = (net, accuracy, charge, calls, shift)
        return best

    val, success, charge, calls, action = value(
        (Fraction(1),) * q, episodes, max_resource_units
    )
    result = AuditDecision(
        net_utility=val / q,
        correct_identification=success / q,
        expected_units=charge / q,
        expected_episodes=calls / q,
        first_shift=action,
    )
    if result.net_utility != (
        result.correct_identification
        - price * result.expected_units
    ):
        raise AssertionError("resource utility accounting fails")
    if result.expected_units > max_resource_units:
        raise AssertionError("expected resources exceed hard pathwise budget")
    return result
