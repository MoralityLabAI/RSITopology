"""Development mathematics for ASMP-9 finite-sample tiers v0.58."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, permutations
from math import atanh, ceil, comb, exp, expm1, log, log1p, sqrt, tanh
from typing import Dict, Mapping, Sequence, Tuple


Alternative = str
Menu = Tuple[Alternative, ...]
Event = Tuple[Menu, Alternative]
Kernel = Dict[Event, Fraction]
Ranking = Tuple[Alternative, ...]

LUCE = "L"
RUM_NON_LUCE = "R"
NON_RUM = "N"
INCONCLUSIVE = "inconclusive"


def _menus(universe: Sequence[Alternative]):
    for size in range(2, len(universe) + 1):
        yield from combinations(tuple(universe), size)


def kernel_from_ranking_weights(
    weights: Mapping[Ranking, Fraction],
    universe: Sequence[Alternative] = ("a", "b", "c"),
) -> Kernel:
    universe = tuple(universe)
    rankings = tuple(permutations(universe))
    normalized = {ranking: Fraction(weights.get(ranking, 0)) for ranking in rankings}
    if any(value < 0 for value in normalized.values()):
        raise ValueError("negative ranking weight")
    if sum(normalized.values(), Fraction(0)) != 1:
        raise ValueError("ranking weights must sum to one")
    return {
        (menu, choice): sum(
            (
                value
                for ranking, value in normalized.items()
                if next(item for item in ranking if item in menu) == choice
            ),
            Fraction(0),
        )
        for menu in _menus(universe)
        for choice in menu
    }


def uniform_luce_kernel() -> Kernel:
    universe = ("a", "b", "c")
    return {
        (menu, choice): Fraction(1, len(menu))
        for menu in _menus(universe)
        for choice in menu
    }


def close_luce_rum_kernel(eta: Fraction) -> Kernel:
    """Non-Luce RUM path approaching the uniform Luce kernel."""

    eta = Fraction(eta)
    if not 0 < eta < Fraction(1, 6):
        raise ValueError("eta must lie in (0,1/6)")
    rankings = tuple(permutations(("a", "b", "c")))
    direction = (0, -1, 1, -1, 1, 0)
    weights = {
        ranking: Fraction(1, 6) + eta * shift
        for ranking, shift in zip(rankings, direction)
    }
    return kernel_from_ranking_weights(weights)


def rum_boundary_kernel() -> Kernel:
    """Positive non-Luce RUM kernel on one regularity boundary."""

    rankings = tuple(permutations(("a", "b", "c")))
    numerators = (1, 1, 1, 1, 0, 1)
    return kernel_from_ranking_weights(
        {
            ranking: Fraction(numerator, 5)
            for ranking, numerator in zip(rankings, numerators)
        }
    )


def close_rum_nonrum_kernel(epsilon: Fraction) -> Kernel:
    """Non-RUM path approaching the explicit RUM boundary kernel."""

    epsilon = Fraction(epsilon)
    if not 0 < epsilon < Fraction(2, 5):
        raise ValueError("epsilon must lie in (0,2/5)")
    kernel = dict(rum_boundary_kernel())
    full = ("a", "b", "c")
    kernel[(full, "a")] += epsilon
    kernel[(full, "b")] -= epsilon
    return kernel


def luce_rum_single_draw_kl(eta: float) -> float:
    if not 0 < eta < 1 / 6:
        raise ValueError("eta must lie in (0,1/6)")
    return -log1p(-9 * eta * eta) / 3


def lecam_error_lower_bound(query_budget: int, eta: float) -> float:
    if query_budget < 0:
        raise ValueError("query budget must be nonnegative")
    kl_upper = query_budget * luce_rum_single_draw_kl(eta)
    return max(0.0, (1 - sqrt(kl_upper / 2)) / 2)


def rum_nonrum_margin_single_draw_kl(gamma: float) -> float:
    """KL for q_0 versus q_(2 gamma) on the full ternary menu."""

    if not 0 < gamma < 1 / 5:
        raise ValueError("gamma must lie in (0,1/5)")
    return -2 / 5 * log1p(-25 * gamma * gamma)


def margin_promised_query_lower_bound(
    gamma: float,
    target_error: float,
) -> int:
    """Necessary adaptive query budget from the explicit RUM/non-RUM pair."""

    if not 0 < target_error < 0.5:
        raise ValueError("target error must lie in (0,1/2)")
    divergence = rum_nonrum_margin_single_draw_kl(gamma)
    return ceil(2 * (1 - 2 * target_error) ** 2 / divergence)


def rum_boundary_luce_distance_lower_bound() -> Fraction:
    """Certified metric separation of q_0 from the Luce closure.

    The binary IIA-cycle polynomial differs from zero by 6/125. Each of its
    two triple products is 3-Lipschitz in coordinate L-infinity distance, so
    the difference is 6-Lipschitz. Maximum menuwise L1 dominates coordinate
    L-infinity distance.
    """

    return Fraction(1, 125)


def eta_for_error_target(query_budget: int, target_error: float) -> float:
    """Choose a conservative eta whose Le Cam lower bound exceeds target."""

    if query_budget <= 0:
        return 1 / 12
    if not 0 < target_error < 0.5:
        raise ValueError("target error must lie in (0,1/2)")
    tv_target = 1 - 2 * target_error
    boundary = sqrt(-expm1(-6 * tv_target * tv_target / query_budget)) / 3
    return min(1 / 12, boundary / 2)


def interpolation_norm(context_size: int, degree: int) -> int:
    if not 0 <= degree:
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


def coordinate_tolerance(
    probability_floor: float,
    gamma: float,
    interpolation_condition: int,
) -> float:
    if not 0 < probability_floor <= 1:
        raise ValueError("probability floor must lie in (0,1]")
    if not 0 < gamma <= 2:
        raise ValueError("gamma must lie in (0,2]")
    if interpolation_condition < 1:
        raise ValueError("interpolation condition must be positive")
    return probability_floor * (
        1 - exp(-atanh(gamma / 6) / interpolation_condition)
    )


def sample_count_per_menu(
    n: int,
    degree: int,
    probability_floor: float,
    gamma: float,
    delta: float,
) -> int:
    if not 0 < delta < 1:
        raise ValueError("delta must lie in (0,1)")
    condition = maximum_interpolation_norm(n, degree)
    tolerance = coordinate_tolerance(probability_floor, gamma, condition)
    coordinates = observed_coordinate_count(n, degree)
    return ceil(log(2 * coordinates / delta) / (2 * tolerance * tolerance))


def likelihood_oscillation_l1_bound(log_score_error: float) -> float:
    """Sharp L1 bound when all log-score errors lie in [-E,E]."""

    if log_score_error < 0:
        raise ValueError("log score error must be nonnegative")
    return 2 * tanh(log_score_error / 2)


def reconstruction_l1_bound(
    coordinate_error: float,
    probability_floor: float,
    interpolation_condition: int,
) -> float:
    if not 0 <= coordinate_error < probability_floor:
        raise ValueError("coordinate error must lie in [0, probability_floor)")
    log_score_error = (
        -2
        * interpolation_condition
        * log(1 - coordinate_error / probability_floor)
    )
    return likelihood_oscillation_l1_bound(log_score_error)


def classify_from_distances(
    distance_to_luce: float,
    distance_to_rum: float,
    gamma: float,
    atol: float = 0.0,
) -> str:
    """Total frozen classifier for exact model-set distance oracles."""

    if min(distance_to_luce, distance_to_rum) < 0:
        raise ValueError("distances must be nonnegative")
    threshold = gamma / 2
    if distance_to_rum > threshold + atol:
        return NON_RUM
    if abs(distance_to_rum - threshold) <= atol:
        return INCONCLUSIVE
    if abs(distance_to_luce - threshold) <= atol:
        return INCONCLUSIVE
    if distance_to_luce < threshold:
        return LUCE
    return RUM_NON_LUCE
