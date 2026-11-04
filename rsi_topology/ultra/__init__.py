"""Reusable mathematical instruments developed by Ultra Experiments."""

from .transient_amplification import (
    FiniteHorizonGain,
    JordanGainBounds,
    boundary_decision,
    departure_from_normality,
    finite_horizon_gain,
    jordan_chain,
    jordan_exact_gain_bounds,
    classify_jordan_radius,
    metric_norm,
    normal_control,
    reframe_operator,
    sample_metric_unit_directions,
    spectral_radius,
    worst_case_trajectory,
)

__all__ = [
    "FiniteHorizonGain",
    "JordanGainBounds",
    "boundary_decision",
    "departure_from_normality",
    "finite_horizon_gain",
    "jordan_chain",
    "jordan_exact_gain_bounds",
    "classify_jordan_radius",
    "metric_norm",
    "normal_control",
    "reframe_operator",
    "sample_metric_unit_directions",
    "spectral_radius",
    "worst_case_trajectory",
]
