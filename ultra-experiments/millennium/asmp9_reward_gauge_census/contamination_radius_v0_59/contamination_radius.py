"""Development mathematics for the ASMP-9 contamination radius v0.59."""

from __future__ import annotations

from fractions import Fraction
from math import atanh, comb, exp, floor, log, tanh
from typing import Iterable, Sequence, Tuple


Distribution = Tuple[Fraction, ...]
Kernel = Tuple[Distribution, ...]


def _as_distribution(values: Iterable[Fraction]) -> Distribution:
    distribution = tuple(Fraction(value) for value in values)
    if not distribution:
        raise ValueError("distribution must be nonempty")
    if any(value < 0 for value in distribution):
        raise ValueError("distribution has negative mass")
    if sum(distribution, Fraction(0)) != 1:
        raise ValueError("distribution must sum to one")
    return distribution


def total_variation(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
) -> Fraction:
    left = _as_distribution(left)
    right = _as_distribution(right)
    if len(left) != len(right):
        raise ValueError("distribution dimensions differ")
    return sum(
        (abs(a - b) for a, b in zip(left, right)),
        Fraction(0),
    ) / 2


def minimum_huber_contamination_for_overlap(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
) -> Fraction:
    """Smallest epsilon whose additive-contamination neighborhoods intersect."""

    distance = total_variation(left, right)
    return distance / (1 + distance)


def kernel_tv_distance(
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
) -> Fraction:
    """Maximum menuwise TV distance on one registered menu family."""

    left_kernel = tuple(_as_distribution(menu) for menu in left)
    right_kernel = tuple(_as_distribution(menu) for menu in right)
    if not left_kernel:
        raise ValueError("kernel must contain at least one menu")
    if len(left_kernel) != len(right_kernel):
        raise ValueError("kernels have different menu counts")
    return max(
        total_variation(left_menu, right_menu)
        for left_menu, right_menu in zip(left_kernel, right_kernel)
    )


def minimum_huber_contamination_for_kernel_overlap(
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
) -> Fraction:
    """Exact radius for independently contaminated registered menus."""

    distance = kernel_tv_distance(left, right)
    return distance / (1 + distance)


def huber_neighborhoods_overlap(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
    epsilon: Fraction,
) -> bool:
    """Exact overlap decision for equal-radius Huber neighborhoods."""

    epsilon = Fraction(epsilon)
    if not 0 <= epsilon < 1:
        raise ValueError("epsilon must lie in [0,1)")
    distance = total_variation(left, right)
    return (1 - epsilon) * distance <= epsilon


def kernel_huber_neighborhoods_overlap(
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
    epsilon: Fraction,
) -> bool:
    """Overlap decision when each menu has its own fixed contaminant."""

    epsilon = Fraction(epsilon)
    if not 0 <= epsilon < 1:
        raise ValueError("epsilon must lie in [0,1)")
    return (1 - epsilon) * kernel_tv_distance(left, right) <= epsilon


def common_huber_observation(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
    epsilon: Fraction,
) -> Tuple[Distribution, Distribution, Distribution]:
    """Construct a common observation and one contaminant for each center."""

    left = _as_distribution(left)
    right = _as_distribution(right)
    if len(left) != len(right):
        raise ValueError("distribution dimensions differ")
    epsilon = Fraction(epsilon)
    if not huber_neighborhoods_overlap(left, right, epsilon):
        raise ValueError("Huber neighborhoods do not overlap")
    if epsilon == 0:
        return left, left, right

    common = [
        (1 - epsilon) * max(a, b)
        for a, b in zip(left, right)
    ]
    remainder = 1 - sum(common, Fraction(0))
    if remainder < 0:
        raise AssertionError("overlap arithmetic produced negative remainder")
    common[0] += remainder
    common_distribution = _as_distribution(common)
    left_contaminant = _as_distribution(
        (observed - (1 - epsilon) * clean) / epsilon
        for observed, clean in zip(common_distribution, left)
    )
    right_contaminant = _as_distribution(
        (observed - (1 - epsilon) * clean) / epsilon
        for observed, clean in zip(common_distribution, right)
    )
    return common_distribution, left_contaminant, right_contaminant


def rum_nonrum_full_menu_pair(gamma: Fraction) -> Tuple[Distribution, Distribution]:
    """The v0.58 margin-promised RUM/non-RUM full-menu pair."""

    gamma = Fraction(gamma)
    if not 0 < gamma <= Fraction(1, 125):
        raise ValueError("gamma must lie in (0,1/125]")
    boundary = (Fraction(2, 5), Fraction(2, 5), Fraction(1, 5))
    nonrum = (
        Fraction(2, 5) + 2 * gamma,
        Fraction(2, 5) - 2 * gamma,
        Fraction(1, 5),
    )
    return boundary, nonrum


def rum_nonrum_witness_contamination_threshold(gamma: Fraction) -> Fraction:
    boundary, nonrum = rum_nonrum_full_menu_pair(gamma)
    return minimum_huber_contamination_for_overlap(boundary, nonrum)


def interpolation_norm(context_size: int, degree: int) -> int:
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if context_size <= degree:
        return 1
    return sum(
        comb(context_size, observed_size)
        * comb(context_size - observed_size - 1, degree - observed_size)
        for observed_size in range(degree + 1)
    )


def maximum_interpolation_norm(n: int, degree: int) -> int:
    if not 0 <= degree <= n - 2:
        raise ValueError("requires 0 <= degree <= n-2")
    return max(interpolation_norm(size, degree) for size in range(n - 1))


def observed_coordinate_count(n: int, degree: int) -> int:
    return sum(
        menu_size * comb(n, menu_size)
        for menu_size in range(2, min(n, degree + 2) + 1)
    )


def observed_tv_modulus_lower_bound(
    probability_floor: float,
    gamma: float,
    interpolation_condition: int,
) -> float:
    """Certified lower bound on cross-tier observed-menu TV separation."""

    if not 0 < probability_floor <= 1:
        raise ValueError("probability floor must lie in (0,1]")
    if not 0 < gamma < 2:
        raise ValueError("gamma must lie in (0,2)")
    if interpolation_condition < 1:
        raise ValueError("interpolation condition must be positive")
    return probability_floor * (
        1 - exp(-atanh(gamma / 2) / interpolation_condition)
    )


def contamination_ceiling_from_observed_gap(observed_tv_gap: float) -> float:
    """Largest boundary epsilon: epsilon/(1-epsilon)=observed_tv_gap."""

    if not 0 <= observed_tv_gap <= 1:
        raise ValueError("observed TV gap must lie in [0,1]")
    return observed_tv_gap / (1 + observed_tv_gap)


def clean_coordinate_tolerance(
    probability_floor: float,
    gamma: float,
    interpolation_condition: int,
) -> float:
    """The v0.58 coordinate tolerance needed for gamma/3 full-kernel error."""

    if not 0 < probability_floor <= 1:
        raise ValueError("probability floor must lie in (0,1]")
    if not 0 < gamma <= 2:
        raise ValueError("gamma must lie in (0,2]")
    if interpolation_condition < 1:
        raise ValueError("interpolation condition must be positive")
    return probability_floor * (
        1 - exp(-atanh(gamma / 6) / interpolation_condition)
    )


def sampling_tolerance_after_contamination(
    probability_floor: float,
    gamma: float,
    interpolation_condition: int,
    epsilon: float,
) -> float:
    """Sampling error still available after worst-case coordinate bias."""

    if not 0 <= epsilon < 1:
        raise ValueError("epsilon must lie in [0,1)")
    return (
        clean_coordinate_tolerance(
            probability_floor,
            gamma,
            interpolation_condition,
        )
        - epsilon
    )


def robust_sample_count_per_menu(
    n: int,
    degree: int,
    probability_floor: float,
    gamma: float,
    epsilon: float,
    delta: float,
) -> int | None:
    """Strict sufficient count; None means contamination exhausts the margin."""

    if not 0 < delta < 1:
        raise ValueError("delta must lie in (0,1)")
    condition = maximum_interpolation_norm(n, degree)
    tolerance = sampling_tolerance_after_contamination(
        probability_floor,
        gamma,
        condition,
        epsilon,
    )
    if tolerance <= 0:
        return None
    coordinates = observed_coordinate_count(n, degree)
    real_bound = log(2 * coordinates / delta) / (2 * tolerance * tolerance)
    return floor(real_bound) + 1


def reconstruction_l1_bound_under_contamination(
    epsilon: float,
    sampling_coordinate_error: float,
    probability_floor: float,
    interpolation_condition: int,
) -> float:
    """Full-kernel L1 error after treating the contaminated law as clean."""

    total_error = epsilon + sampling_coordinate_error
    if not 0 <= total_error < probability_floor:
        raise ValueError("total coordinate error must lie below the clean floor")
    log_score_error = (
        -2
        * interpolation_condition
        * log(1 - total_error / probability_floor)
    )
    return 2 * tanh(log_score_error / 2)


def population_identifiability_status(
    observed_tv_gap: Fraction,
    epsilon: Fraction,
) -> str:
    """Frozen exact status at a class-wide observed-TV gap."""

    observed_tv_gap = Fraction(observed_tv_gap)
    epsilon = Fraction(epsilon)
    if not 0 <= observed_tv_gap <= 1:
        raise ValueError("observed TV gap must lie in [0,1]")
    if not 0 <= epsilon < 1:
        raise ValueError("epsilon must lie in [0,1)")
    radius = epsilon / (1 - epsilon)
    if radius < observed_tv_gap:
        return "identifiable"
    if radius == observed_tv_gap:
        return "boundary_inconclusive"
    return "ambiguous"
