"""Sharp finite-horizon rate calculations for ASMP-9 v0.43.

The v0.42 certificate first bounded every one-step channel in total
variation and then used an ``h * TV`` union bound.  This module isolates a
binary sentinel experiment for which the exact decision-relative deficiency
is available in closed form.  It also records:

* the policy-uniform chain-rule/Pinsker upper modulus under a per-step KL
  bound;
* an exact two-point chi-square certificate giving an
  ``Omega(h / gap**2)`` sample lower bound; and
* a block estimator attaining ``O(h log(1/alpha) / gap**2)`` on the same
  sentinel family.

All theorem witnesses use ``fractions.Fraction``.  Floating point is used
only for logarithms/square roots in confidence-radius reporting.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import math


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def _validate_probability(value: Q, name: str) -> None:
    if not Q(0) <= value <= Q(1):
        raise ValueError(f"{name} must lie in [0,1]")


def sentinel_deficiency(horizon: int, success_probability: Q) -> Q:
    """Exact deficiency to perfect revelation for the sentinel experiment.

    There are two targets and zero-one terminal loss.  Under target zero the
    repeated binary query always emits zero.  Under target one it emits one
    with probability ``p`` independently on each of ``h`` uses.

    The only ambiguous transcript is the all-zero transcript, whose
    probability under target one is ``a=(1-p)**h``.  Randomizing on that
    transcript equalizes the two target-wise errors at ``a/(1+a)``.
    """

    if horizon < 1:
        raise ValueError("horizon must be positive")
    p = q(success_probability)
    _validate_probability(p, "success_probability")
    all_zero = (Q(1) - p) ** horizon
    return all_zero / (Q(1) + all_zero)


def sentinel_derivative_magnitude(
    horizon: int, success_probability: Q
) -> Q:
    """Magnitude of the derivative of the exact deficiency in ``p``."""

    if horizon < 1:
        raise ValueError("horizon must be positive")
    p = q(success_probability)
    _validate_probability(p, "success_probability")
    base = Q(1) - p
    all_zero = base**horizon
    return (
        Q(horizon) * base ** (horizon - 1)
        / (Q(1) + all_zero) ** 2
    )


def bernoulli_chi_square(p: Q, reference_q: Q) -> Q:
    """Exact ``chi^2(Ber(p) || Ber(q))`` for an interior reference."""

    p = q(p)
    reference_q = q(reference_q)
    _validate_probability(p, "p")
    if not Q(0) < reference_q < Q(1):
        raise ValueError("reference_q must lie strictly inside (0,1)")
    return (p - reference_q) ** 2 / (
        reference_q * (Q(1) - reference_q)
    )


@dataclass(frozen=True)
class TwoPointCertificate:
    horizon: int
    epsilon: Q
    p0: Q
    p1: Q
    deficiency0: Q
    deficiency1: Q
    deficiency_gap: Q
    chi_square_upper_on_kl: Q
    le_cam_sample_floor: int

    def jsonable(self) -> dict:
        return {
            "horizon": self.horizon,
            "epsilon": qstr(self.epsilon),
            "p0": qstr(self.p0),
            "p1": qstr(self.p1),
            "deficiency0": qstr(self.deficiency0),
            "deficiency1": qstr(self.deficiency1),
            "deficiency_gap": qstr(self.deficiency_gap),
            "chi_square_upper_on_kl": qstr(
                self.chi_square_upper_on_kl
            ),
            "le_cam_sample_floor": self.le_cam_sample_floor,
            "normalized_floor_gap_squared_over_h": float(
                Q(self.le_cam_sample_floor)
                * self.deficiency_gap**2
                / self.horizon
            ),
        }


def two_point_certificate(
    horizon: int, epsilon: Q
) -> TwoPointCertificate:
    """Build the exact local lower-bound witness.

    ``p0=1/(2h)`` and ``p1=(1/2+epsilon)/h``.  For ``h>=2`` and
    ``0<epsilon<=1/4``:

    * the deficiency gap lies in ``[epsilon/16, epsilon]``;
    * ``KL(Ber(p0)||Ber(p1)) <= chi2 <= 4 epsilon**2 / h``; and
    * any test with both pointwise errors at most 1/4 needs at least
      ``ceil(1/(2 chi2))`` iid channel samples.
    """

    if horizon < 2:
        raise ValueError("horizon must be at least two")
    epsilon = q(epsilon)
    if not Q(0) < epsilon <= Q(1, 4):
        raise ValueError("epsilon must lie in (0,1/4]")
    p0 = Q(1, 2 * horizon)
    p1 = (Q(1, 2) + epsilon) / horizon
    d0 = sentinel_deficiency(horizon, p0)
    d1 = sentinel_deficiency(horizon, p1)
    gap = d0 - d1
    chi_square = bernoulli_chi_square(p0, p1)

    if not epsilon / 16 <= gap <= epsilon:
        raise AssertionError("registered deficiency-gap bounds failed")
    if chi_square > 4 * epsilon**2 / horizon:
        raise AssertionError("registered chi-square bound failed")

    reciprocal = Q(1, 2) / chi_square
    sample_floor = (
        reciprocal.numerator + reciprocal.denominator - 1
    ) // reciprocal.denominator
    return TwoPointCertificate(
        horizon=horizon,
        epsilon=epsilon,
        p0=p0,
        p1=p1,
        deficiency0=d0,
        deficiency1=d1,
        deficiency_gap=gap,
        chi_square_upper_on_kl=chi_square,
        le_cam_sample_floor=sample_floor,
    )


def adaptive_kl_risk_radius(
    horizon: int,
    per_step_kl: float,
    loss_span: float = 1.0,
) -> float:
    """Policy-uniform risk radius from KL chain rule and Pinsker.

    If every target/query cell obeys the directed conditional bound
    ``KL(P(.|theta,q) || P_hat(.|theta,q)) <= kappa``, then the transcript
    law under any history-adaptive policy obeys ``KL <= h*kappa``.
    Pinsker and bounded loss give this radius.
    """

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    if not math.isfinite(per_step_kl) or per_step_kl < 0:
        raise ValueError("per_step_kl must be finite and nonnegative")
    if not math.isfinite(loss_span) or loss_span < 0:
        raise ValueError("loss_span must be finite and nonnegative")
    return loss_span * min(
        1.0, math.sqrt(horizon * per_step_kl / 2.0)
    )


def no_linear_horizon_witness_ratio(
    horizon: int,
    kl_quadratic_constant: float,
) -> float:
    """Upper bound on ``risk_gap/(h*delta)`` under ``KL<=C delta^2``.

    The value is ``sqrt(C/(2h))`` for unit-span losses.  It tends to zero,
    ruling out a uniform ``Omega(h*delta)`` risk gap in any KL-regular
    two-point family.
    """

    if horizon < 1:
        raise ValueError("horizon must be positive")
    if (
        not math.isfinite(kl_quadratic_constant)
        or kl_quadratic_constant < 0
    ):
        raise ValueError(
            "kl_quadratic_constant must be finite and nonnegative"
        )
    return math.sqrt(kl_quadratic_constant / (2.0 * horizon))


def _log_upper(value: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = 80
        return context.next_plus(value.ln())


def block_hoeffding_radius(block_count: int, alpha: float) -> float:
    """Two-sided Hoeffding radius for all-zero block indicators."""

    if block_count < 1:
        raise ValueError("block_count must be positive")
    alpha_decimal = Decimal(str(alpha))
    if not Decimal(0) < alpha_decimal < Decimal(1):
        raise ValueError("alpha must lie strictly between zero and one")
    with localcontext() as context:
        context.prec = 80
        squared = context.next_plus(
            _log_upper(Decimal(2) / alpha_decimal)
            / (Decimal(2) * Decimal(block_count))
        )
        radius_decimal = context.next_plus(squared.sqrt())
    radius = float(radius_decimal)
    if Decimal.from_float(radius) < radius_decimal:
        radius = math.nextafter(radius, math.inf)
    return min(1.0, radius)


def required_block_samples(
    horizon: int, gap: float, alpha: float
) -> dict:
    """Sufficient raw channel samples for a strict width below ``gap``."""

    if horizon < 1:
        raise ValueError("horizon must be positive")
    if not math.isfinite(gap) or not 0 < gap < 1:
        raise ValueError("gap must lie strictly inside (0,1)")
    alpha_decimal = Decimal(str(alpha))
    if not Decimal(0) < alpha_decimal < Decimal(1):
        raise ValueError("alpha must lie strictly between zero and one")
    with localcontext() as context:
        context.prec = 80
        threshold = (
            _log_upper(Decimal(2) / alpha_decimal)
            / (Decimal(2) * Decimal(str(gap)) ** 2)
        )
        blocks = int(threshold.to_integral_value(rounding="ROUND_FLOOR")) + 1
    while block_hoeffding_radius(blocks, alpha) >= gap:
        blocks += 1
    while (
        blocks > 1
        and block_hoeffding_radius(blocks - 1, alpha) < gap
    ):
        blocks -= 1
    raw_samples = horizon * blocks
    return {
        "horizon": horizon,
        "gap": gap,
        "alpha": alpha,
        "blocks": blocks,
        "raw_samples": raw_samples,
        "radius": block_hoeffding_radius(blocks, alpha),
        "normalized_samples_gap_squared_over_h": (
            raw_samples * gap**2 / horizon
        ),
    }


def block_deficiency_interval(
    all_zero_blocks: int, block_count: int, alpha: float
) -> dict:
    """Confidence interval for the sentinel deficiency from block data."""

    if block_count < 1:
        raise ValueError("block_count must be positive")
    if not 0 <= all_zero_blocks <= block_count:
        raise ValueError("all_zero_blocks must lie in [0, block_count]")
    a_hat = all_zero_blocks / block_count
    point = a_hat / (1.0 + a_hat)
    radius = block_hoeffding_radius(block_count, alpha)
    a_lower = max(0.0, a_hat - radius)
    a_upper = min(1.0, a_hat + radius)
    return {
        "point": point,
        "lower": a_lower / (1.0 + a_lower),
        "upper": a_upper / (1.0 + a_upper),
        "all_zero_probability_point": a_hat,
        "all_zero_probability_radius": radius,
        "confidence": 1.0 - alpha,
    }
