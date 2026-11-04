"""Confidence-valid finite-sample access bounds for ASMP-9 v0.42.

The module is deliberately independent of one optimizer.  It takes a point
estimate of directed risk deficiency plus simultaneous channel-TV radii and
returns a theorem-backed interval and a total three-state decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import math
from typing import Mapping, Sequence


def _up(value: float) -> float:
    """Round a computed upper bound outward by one binary float."""

    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError("outward-rounded bounds must be finite and nonnegative")
    if value == 0.0:
        return 0.0
    return math.nextafter(value, math.inf)


def _down_nonnegative(value: float) -> float:
    """Round a nonnegative lower endpoint outward toward zero."""

    value = float(value)
    if not math.isfinite(value):
        raise ValueError("outward-rounded bounds must be finite")
    if value <= 0.0:
        return 0.0
    return math.nextafter(value, -math.inf)


def _decimal_probability(value: object) -> Decimal:
    result = Decimal(str(value))
    if not Decimal(0) < result < Decimal(1):
        raise ValueError("probability must lie strictly between zero and one")
    return result


def _float_upper(decimal_bound: Decimal) -> float:
    """Convert a positive Decimal bound to binary float from above."""

    result = float(decimal_bound)
    if Decimal.from_float(result) < decimal_bound:
        result = math.nextafter(result, math.inf)
    return result


def _sqrt_log_ratio_upper(
    log_numerator: Decimal,
    log_denominator: Decimal,
    scale_denominator: int,
) -> float:
    """Conservative high-precision ``sqrt(log(a/b)/c)`` evaluation."""

    if (
        log_numerator <= 0
        or log_denominator <= 0
        or scale_denominator <= 0
    ):
        raise ValueError("radius inputs must be positive")
    with localcontext() as context:
        context.prec = 80
        ratio = log_numerator / log_denominator
        log_value = context.next_plus(ratio.ln())
        squared_radius = context.next_plus(
            log_value / Decimal(scale_denominator)
        )
        radius = context.next_plus(squared_radius.sqrt())
    return _float_upper(radius)


def weissman_tv_radius(
    outcome_count: int,
    samples: int,
    alpha_cell: float,
) -> float:
    """A distribution-free TV radius for one multinomial empirical law.

    Uses ``P(||P_hat-P||_1 >= eps) <=
    (2**K-2) exp(-n eps**2/2)`` and TV = L1/2.
    """

    if outcome_count < 1:
        raise ValueError("outcome_count must be positive")
    if samples < 1:
        raise ValueError("samples must be positive")
    alpha_decimal = _decimal_probability(alpha_cell)
    if outcome_count == 1:
        return 0.0
    prefactor = 2**outcome_count - 2
    radius = _sqrt_log_ratio_upper(
        Decimal(prefactor),
        alpha_decimal,
        2 * samples,
    )
    return min(1.0, radius)


def simultaneous_weissman_radii(
    outcome_counts: Mapping[str, int],
    sample_counts: Mapping[str, int],
    alpha: float,
) -> dict[str, float]:
    """Bonferroni-simultaneous TV radii for a frozen cell universe."""

    if set(outcome_counts) != set(sample_counts):
        raise ValueError("outcome and sample cell universes differ")
    if not outcome_counts:
        raise ValueError("at least one channel cell is required")
    alpha_decimal = _decimal_probability(alpha)
    with localcontext() as context:
        context.prec = 80
        cell_count = Decimal(len(outcome_counts))
        alpha_cell = alpha_decimal / cell_count
        if alpha_cell * cell_count > alpha_decimal:
            alpha_cell = context.next_minus(alpha_cell)
    return {
        cell: weissman_tv_radius(
            outcome_counts[cell],
            sample_counts[cell],
            alpha_cell,
        )
        for cell in sorted(outcome_counts)
    }


def shared_binary_flip_radius(
    query_count: int,
    targets: int,
    samples_per_target: int,
    alpha: float,
) -> float:
    """Simultaneous Hoeffding/Weissman radius for shared flip parameters.

    Each query has one registered symmetric flip probability shared across
    targets.  Balanced sampling yields ``targets*samples_per_target`` iid
    Bernoulli error indicators per query.  Bonferroni is over queries.
    """

    if query_count < 1 or targets < 1 or samples_per_target < 1:
        raise ValueError("counts must be positive")
    alpha_decimal = _decimal_probability(alpha)
    pooled = targets * samples_per_target
    radius = _sqrt_log_ratio_upper(
        Decimal(2 * query_count),
        alpha_decimal,
        2 * pooled,
    )
    return min(1.0, radius)


def loss_spans(losses: Sequence[Sequence[Q]]) -> tuple[Q, ...]:
    if not losses or not losses[0]:
        raise ValueError("loss matrix cannot be empty")
    width = len(losses[0])
    spans = []
    for row in losses:
        if len(row) != width:
            raise ValueError("loss rows must have one action count")
        if any(value < 0 for value in row):
            raise ValueError("losses must be nonnegative")
        spans.append(max(row) - min(row))
    return tuple(spans)


def policy_risk_radii(
    losses: Sequence[Sequence[Q]],
    horizon: int,
    query_names: Sequence[str],
    tv_radii: Mapping[tuple[int, str], float],
) -> tuple[float, ...]:
    """Uniform target-wise risk radii over every adaptive policy tree."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    names = tuple(query_names)
    if horizon and not names:
        raise ValueError("positive horizon requires accessible queries")
    spans = loss_spans(losses)
    result = []
    for target, span in enumerate(spans):
        missing = [
            name for name in names if (target, name) not in tv_radii
        ]
        if missing:
            raise ValueError(
                f"missing target-query TV radii: target={target}, {missing}"
            )
        step_radius = max(
            (tv_radii[(target, name)] for name in names),
            default=0.0,
        )
        history_radius = min(1.0, horizon * step_radius)
        result.append(_up(float(span) * history_radius))
    return tuple(result)


@dataclass(frozen=True)
class DeficiencyInterval:
    point: float
    lower: float
    upper: float
    half_width: float
    confidence: float

    def jsonable(self) -> dict:
        return {
            "point": self.point,
            "lower": self.lower,
            "upper": self.upper,
            "half_width": self.half_width,
            "confidence": self.confidence,
        }


def deficiency_interval(
    point_deficiency: float,
    source_risk_radii: Sequence[float],
    reference_risk_radii: Sequence[float],
    alpha: float,
    maximum_deficiency: float = 1.0,
) -> DeficiencyInterval:
    """Propagate source/reference risk-set radii to deficiency."""

    if not 0 <= point_deficiency <= maximum_deficiency:
        raise ValueError("point deficiency is outside its declared range")
    if len(source_risk_radii) != len(reference_risk_radii):
        raise ValueError("source and reference target counts differ")
    if not source_risk_radii:
        raise ValueError("at least one target radius is required")
    if any(value < 0 for value in source_risk_radii):
        raise ValueError("source radii must be nonnegative")
    if any(value < 0 for value in reference_risk_radii):
        raise ValueError("reference radii must be nonnegative")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between zero and one")
    half_width = _up(
        max(
            source + reference
            for source, reference in zip(
                source_risk_radii, reference_risk_radii
            )
        )
    )
    return DeficiencyInterval(
        point=float(point_deficiency),
        lower=_down_nonnegative(
            float(point_deficiency) - half_width
        ),
        upper=min(
            float(maximum_deficiency),
            _up(float(point_deficiency) + half_width),
        ),
        half_width=half_width,
        confidence=1.0 - alpha,
    )


def access_decision(
    interval: DeficiencyInterval,
    tolerance: float,
    practical_margin: float = 0.0,
) -> str:
    """Total strict-boundary decision: pass, fail, or inconclusive."""

    if not 0 <= tolerance <= 1:
        raise ValueError("tolerance must lie in [0,1]")
    if practical_margin < 0:
        raise ValueError("practical margin must be nonnegative")
    if interval.upper < tolerance - practical_margin:
        return "pass"
    if interval.lower > tolerance + practical_margin:
        return "fail"
    return "inconclusive"


def required_samples_per_target_shared_binary(
    gap: float,
    horizon: int,
    query_count: int,
    targets: int,
    alpha: float,
    loss_span: float = 1.0,
    estimated_sides: int = 1,
) -> int:
    """Smallest integer ``n`` whose analytic radius is strictly below gap.

    ``query_count`` is the number of queries on each estimated side.  When
    both source and reference are estimated, the specialized helper assumes
    disjoint query-cell families: Bonferroni therefore covers
    ``estimated_sides * query_count`` shared flip parameters, and both sides'
    policy-risk radii enter the deficiency width.
    """

    if gap <= 0:
        raise ValueError("gap must be positive")
    if horizon < 1 or query_count < 1 or targets < 1:
        raise ValueError("horizon and counts must be positive")
    if loss_span <= 0:
        raise ValueError("loss_span must be positive")
    if estimated_sides not in (1, 2):
        raise ValueError("estimated_sides must be one or two")
    numerator = (
        (estimated_sides * horizon * loss_span) ** 2
        * math.log(
            (2.0 * estimated_sides * query_count) / alpha
        )
    )
    denominator = 2.0 * targets * gap**2
    floor = int(math.floor(numerator / denominator)) + 1
    floor = max(1, floor)

    def clears(candidate: int) -> bool:
        radius = shared_binary_flip_radius(
            estimated_sides * query_count,
            targets,
            candidate,
            alpha,
        )
        return (
            estimated_sides * horizon * loss_span * radius < gap
        )

    while not clears(floor):
        floor += 1
    while floor > 1 and clears(floor - 1):
        floor -= 1
    return floor


TRUE_ADAPTIVE = Q(61, 135)
TRUE_OPEN_LOOP = Q(13, 25)
TOLERANCE = Q(1, 2)


def burned_centered_calibration() -> dict:
    rows = []
    for samples in (480, 4800, 48000):
        radius = shared_binary_flip_radius(
            query_count=3,
            targets=4,
            samples_per_target=samples,
            alpha=0.05,
        )
        risk_radii = tuple([_up(2.0 * radius)] * 4)
        reference = (0.0, 0.0, 0.0, 0.0)
        arms = {}
        for name, point in (
            ("adaptive", TRUE_ADAPTIVE),
            ("open_loop", TRUE_OPEN_LOOP),
        ):
            interval = deficiency_interval(
                float(point),
                risk_radii,
                reference,
                alpha=0.05,
            )
            arms[name] = {
                "interval": interval.jsonable(),
                "decision": access_decision(
                    interval, float(TOLERANCE)
                ),
            }
        rows.append(
            {
                "samples_per_target_query": samples,
                "pooled_samples_per_query": 4 * samples,
                "simultaneous_query_tv_radius": radius,
                "arms": arms,
            }
        )
    adaptive_gap = float(TOLERANCE - TRUE_ADAPTIVE)
    open_gap = float(TRUE_OPEN_LOOP - TOLERANCE)
    return {
        "phase": "burned_centered_calibration",
        "alpha": 0.05,
        "tolerance": "1/2",
        "horizon": 2,
        "query_count": 3,
        "targets": 4,
        "true_deficiencies": {
            "adaptive": "61/135",
            "open_loop": "13/25",
        },
        "analytic_sample_floors_per_target_query": {
            "adaptive_pass": required_samples_per_target_shared_binary(
                adaptive_gap, 2, 3, 4, 0.05
            ),
            "open_loop_fail": required_samples_per_target_shared_binary(
                open_gap, 2, 3, 4, 0.05
            ),
        },
        "rows": rows,
    }
