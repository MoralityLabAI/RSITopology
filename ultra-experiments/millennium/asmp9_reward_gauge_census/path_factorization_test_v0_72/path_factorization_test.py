"""Known-variance Gaussian lack-of-fit test for ASMP-9 v0.72."""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import Sequence

import numpy as np
import sympy as sp
import mpmath as mp
from scipy.stats import chi2, ncx2


def rational_matrix(rows: Sequence[Sequence[object]]) -> sp.Matrix:
    return sp.Matrix([[sp.Rational(value) for value in row] for row in rows])


def primitive_left_contrasts(design: sp.Matrix) -> tuple[sp.Matrix, ...]:
    contrasts: list[sp.Matrix] = []
    for vector in design.T.nullspace():
        denominators = [sp.denom(value) for value in vector]
        scale = sp.ilcm(*denominators) if denominators else 1
        integers = [int(value * scale) for value in vector]
        common = 0
        for value in integers:
            common = gcd(common, abs(value))
        if common:
            integers = [value // common for value in integers]
        first = next((value for value in integers if value), 1)
        if first < 0:
            integers = [-value for value in integers]
        contrasts.append(sp.Matrix(integers))
    return tuple(contrasts)


def exact_distance_squared(design: sp.Matrix, mean: sp.Matrix) -> sp.Expr:
    if mean.shape != (design.rows, 1):
        raise ValueError("mean must be one column with one value per path")
    residual = (sp.eye(design.rows) - design * design.pinv()) * mean
    return sp.simplify((residual.T * residual)[0])


@dataclass(frozen=True)
class FactorizationGeometry:
    path_count: int
    edge_count: int
    design_rank: int
    residual_degrees_of_freedom: int
    reward_coordinates_identified: bool
    factorization_test_available: bool
    primitive_contrasts: tuple[tuple[int, ...], ...]

    def to_jsonable(self) -> dict[str, object]:
        return {
            "path_count": self.path_count,
            "edge_count": self.edge_count,
            "design_rank": self.design_rank,
            "residual_degrees_of_freedom": self.residual_degrees_of_freedom,
            "reward_coordinates_identified": self.reward_coordinates_identified,
            "factorization_test_available": self.factorization_test_available,
            "primitive_contrasts": [
                list(contrast) for contrast in self.primitive_contrasts
            ],
        }


def analyze_geometry(design: sp.Matrix) -> FactorizationGeometry:
    rank = design.rank()
    contrasts = primitive_left_contrasts(design)
    return FactorizationGeometry(
        path_count=design.rows,
        edge_count=design.cols,
        design_rank=rank,
        residual_degrees_of_freedom=design.rows - rank,
        reward_coordinates_identified=rank == design.cols,
        factorization_test_available=design.rows - rank > 0,
        primitive_contrasts=tuple(
            tuple(int(value) for value in contrast)
            for contrast in contrasts
        ),
    )


def weighted_residual_statistic(
    design: sp.Matrix,
    observed_means: Sequence[float],
    mean_variances: Sequence[float],
) -> dict[str, float | int | bool]:
    if len(observed_means) != design.rows:
        raise ValueError("one observed mean is required per path")
    if len(mean_variances) != design.rows:
        raise ValueError("one mean variance is required per path")
    if any(value <= 0 for value in mean_variances):
        raise ValueError("mean variances must be positive")

    x = np.asarray(design, dtype=float)
    y = np.asarray(observed_means, dtype=float)
    whitening = np.diag(1.0 / np.sqrt(np.asarray(mean_variances, dtype=float)))
    z = whitening @ x
    whitened_y = whitening @ y
    projector = np.eye(design.rows) - z @ np.linalg.pinv(z)
    residual = projector @ whitened_y
    statistic = float(residual @ residual)
    degrees = design.rows - int(np.linalg.matrix_rank(z))
    return {
        "statistic": statistic,
        "degrees_of_freedom": degrees,
        "factorization_test_available": degrees > 0,
    }


def noncentrality(
    design: sp.Matrix,
    true_means: Sequence[float],
    mean_variances: Sequence[float],
) -> float:
    result = weighted_residual_statistic(
        design, true_means, mean_variances
    )
    return float(result["statistic"])


def chi_square_test_design(
    degrees_of_freedom: int,
    alpha: float,
    alternative_noncentrality: float,
) -> dict[str, float | int]:
    if degrees_of_freedom <= 0:
        raise ValueError("positive residual degrees of freedom required")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0,1)")
    if alternative_noncentrality < 0:
        raise ValueError("noncentrality must be nonnegative")
    critical = float(chi2.ppf(1.0 - alpha, degrees_of_freedom))
    power = float(
        ncx2.sf(critical, degrees_of_freedom, alternative_noncentrality)
    )
    return {
        "degrees_of_freedom": degrees_of_freedom,
        "alpha": alpha,
        "critical_value": critical,
        "alternative_noncentrality": alternative_noncentrality,
        "power": power,
    }


def minimum_equal_repeats(
    *,
    distance_squared: float,
    sample_variance: float,
    degrees_of_freedom: int,
    alpha: float,
    target_power: float,
    maximum: int = 1_000_000,
) -> dict[str, float | int]:
    if distance_squared <= 0 or sample_variance <= 0:
        raise ValueError("positive distance and variance required")
    if not 0 < target_power < 1:
        raise ValueError("target power must lie in (0,1)")
    critical = float(chi2.ppf(1.0 - alpha, degrees_of_freedom))
    for repeats in range(1, maximum + 1):
        noncentral = repeats * distance_squared / sample_variance
        power = float(ncx2.sf(critical, degrees_of_freedom, noncentral))
        if power >= target_power:
            previous_power = (
                float(
                    ncx2.sf(
                        critical,
                        degrees_of_freedom,
                        (repeats - 1)
                        * distance_squared
                        / sample_variance,
                    )
                )
                if repeats > 1
                else float(alpha)
            )
            return {
                "minimum_repeats_per_path": repeats,
                "power": power,
                "previous_power": previous_power,
                "critical_value": critical,
                "noncentrality": noncentral,
            }
    raise RuntimeError("target power not reached within maximum")


def df1_power_high_precision(
    *, alpha: str, noncentrality_value: str, digits: int = 80
) -> str:
    """Evaluate the exact df=1 normal representation at high precision."""

    with mp.workdps(digits):
        alpha_mp = mp.mpf(alpha)
        noncentral_mp = mp.mpf(noncentrality_value)
        z_critical = mp.sqrt(2) * mp.erfinv(1 - alpha_mp)
        shift = mp.sqrt(noncentral_mp)

        def normal_cdf(value: mp.mpf) -> mp.mpf:
            return (1 + mp.erf(value / mp.sqrt(2))) / 2

        power = (
            1
            - normal_cdf(z_critical - shift)
            + normal_cdf(-z_critical - shift)
        )
        return mp.nstr(power, n=digits)


def canonical_fixture() -> tuple[sp.Matrix, sp.Matrix]:
    # Nonempty paths ordered as a, b, a/z, b/z over edges a, b, z.
    design = rational_matrix(
        [
            [1, 0, 0],
            [0, 1, 0],
            [1, 0, 1],
            [0, 1, 1],
        ]
    )
    interaction_mean = rational_matrix([[0], [0], [1], [0]])
    return design, interaction_mean
