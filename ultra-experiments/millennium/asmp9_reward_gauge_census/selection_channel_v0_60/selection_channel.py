"""Development mathematics for the ASMP-9 selection-channel boundary v0.60."""

from __future__ import annotations

from fractions import Fraction
from math import atanh, ceil, exp, log
from typing import Iterable, Sequence, Tuple


Distribution = Tuple[Fraction, ...]
Kernel = Tuple[Distribution, ...]
Vector = Tuple[Fraction, ...]
JointKernel = Tuple[Vector, ...]


def as_distribution(values: Iterable[Fraction]) -> Distribution:
    distribution = tuple(Fraction(value) for value in values)
    if not distribution:
        raise ValueError("distribution must be nonempty")
    if any(value < 0 for value in distribution):
        raise ValueError("distribution has negative mass")
    if sum(distribution, Fraction(0)) != 1:
        raise ValueError("distribution must sum to one")
    return distribution


def as_kernel(menus: Sequence[Sequence[Fraction]]) -> Kernel:
    kernel = tuple(as_distribution(menu) for menu in menus)
    if not kernel:
        raise ValueError("kernel must contain at least one menu")
    return kernel


def preselection_joint(
    kernel: Sequence[Sequence[Fraction]],
    selection: Sequence[Fraction],
) -> JointKernel:
    """Joint P(A,x) when the recorded menu is selected before its response."""

    kernel = as_kernel(kernel)
    selection = as_distribution(selection)
    if len(kernel) != len(selection):
        raise ValueError("selection and kernel menu counts differ")
    return tuple(
        tuple(menu_probability * response for response in menu)
        for menu_probability, menu in zip(selection, kernel)
    )


def recover_preselection_joint(
    joint: Sequence[Sequence[Fraction]],
) -> Tuple[Distribution, Tuple[Distribution | None, ...]]:
    """Recover the selection law and every positive-support conditional."""

    joint = tuple(tuple(Fraction(value) for value in menu) for menu in joint)
    if not joint or any(not menu for menu in joint):
        raise ValueError("joint law must contain nonempty menus")
    if any(value < 0 for menu in joint for value in menu):
        raise ValueError("joint law has negative mass")
    if sum((sum(menu) for menu in joint), Fraction(0)) != 1:
        raise ValueError("joint law must sum to one")
    selection = tuple(sum(menu, Fraction(0)) for menu in joint)
    conditionals = tuple(
        None
        if probability == 0
        else as_distribution(value / probability for value in menu)
        for probability, menu in zip(selection, joint)
    )
    return as_distribution(selection), conditionals


def observed_support(selection: Sequence[Fraction]) -> Tuple[int, ...]:
    selection = as_distribution(selection)
    return tuple(index for index, probability in enumerate(selection) if probability > 0)


def incomplete_domain_compatible_tiers(
    *,
    complete_support: bool,
    full_tier: str | None = None,
    has_rum_completion: bool | None = None,
    has_luce_completion: bool | None = None,
) -> Tuple[str, ...]:
    """The v0.56 tier ledger after pre-response selection recovery."""

    if complete_support:
        if full_tier not in {"L", "R", "N"}:
            raise ValueError("complete support requires full_tier in {L,R,N}")
        return (full_tier,)
    if has_rum_completion is None or has_luce_completion is None:
        raise ValueError("proper support requires completion flags")
    if has_luce_completion and not has_rum_completion:
        raise ValueError("Luce completion implies RUM completion")
    if not has_rum_completion:
        return ("N",)
    if has_luce_completion:
        return ("L", "R", "N")
    return ("R", "N")


def categorical_kl(left: Sequence[Fraction], right: Sequence[Fraction]) -> float:
    left = as_distribution(left)
    right = as_distribution(right)
    if len(left) != len(right):
        raise ValueError("distribution dimensions differ")
    divergence = 0.0
    for p_value, q_value in zip(left, right):
        if p_value == 0:
            continue
        if q_value == 0:
            return float("inf")
        divergence += float(p_value) * log(float(p_value / q_value))
    return divergence


def preselection_joint_kl(
    selection: Sequence[Fraction],
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
) -> float:
    """KL factorization when both hypotheses use the same menu selection."""

    selection = as_distribution(selection)
    left = as_kernel(left)
    right = as_kernel(right)
    if not len(selection) == len(left) == len(right):
        raise ValueError("menu counts differ")
    return sum(
        float(menu_probability) * categorical_kl(left_menu, right_menu)
        for menu_probability, left_menu, right_menu in zip(
            selection,
            left,
            right,
        )
    )


def outcome_selected_observation(
    clean: Sequence[Fraction],
    target_selected: Sequence[Fraction],
    record_rate: Fraction,
) -> Tuple[Distribution, Vector, Vector]:
    """Map any positive clean law to a target selected law.

    Returns the selected conditional, the response-dependent recording
    probabilities, and the unconditional recorded response masses.
    """

    clean = as_distribution(clean)
    target_selected = as_distribution(target_selected)
    if len(clean) != len(target_selected):
        raise ValueError("distribution dimensions differ")
    if any(value <= 0 for value in clean) or any(
        value <= 0 for value in target_selected
    ):
        raise ValueError("clean and target distributions must be positive")
    record_rate = Fraction(record_rate)
    if not 0 < record_rate <= 1:
        raise ValueError("record_rate must lie in (0,1]")
    recording = tuple(
        record_rate * target / source
        for source, target in zip(clean, target_selected)
    )
    if any(probability > 1 for probability in recording):
        raise ValueError("record_rate is infeasible for the requested target")
    recorded_joint = tuple(
        source * probability
        for source, probability in zip(clean, recording)
    )
    if sum(recorded_joint, Fraction(0)) != record_rate:
        raise AssertionError("recorded mass does not match record rate")
    selected = as_distribution(value / record_rate for value in recorded_joint)
    return selected, recording, recorded_joint


def common_outcome_selected_observation(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
    target_selected: Sequence[Fraction] | None = None,
) -> Tuple[
    Fraction,
    Distribution,
    Vector,
    Vector,
    Vector,
]:
    """Construct one selected law and record rate shared by two clean laws."""

    left = as_distribution(left)
    right = as_distribution(right)
    if len(left) != len(right):
        raise ValueError("distribution dimensions differ")
    if any(value <= 0 for value in left + right):
        raise ValueError("clean distributions must be positive")
    if target_selected is None:
        target = tuple(Fraction(1, len(left)) for _ in left)
    else:
        target = as_distribution(target_selected)
    if len(target) != len(left) or any(value <= 0 for value in target):
        raise ValueError("target distribution must be positive and dimension matched")
    largest_rate = min(
        tuple(source / target_value for source, target_value in zip(left, target))
        + tuple(source / target_value for source, target_value in zip(right, target))
    )
    record_rate = min(Fraction(1), largest_rate) / 2
    selected_left, recording_left, joint_left = outcome_selected_observation(
        left,
        target,
        record_rate,
    )
    selected_right, recording_right, joint_right = outcome_selected_observation(
        right,
        target,
        record_rate,
    )
    if selected_left != selected_right or joint_left != joint_right:
        raise AssertionError("common selected observation construction failed")
    return (
        record_rate,
        selected_left,
        recording_left,
        recording_right,
        joint_left,
    )


def recording_ratio_required_for_overlap(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
) -> Fraction:
    """Smallest u/ell allowing equal recorded laws under unknown weights."""

    left = as_distribution(left)
    right = as_distribution(right)
    if len(left) != len(right):
        raise ValueError("distribution dimensions differ")
    if any(value <= 0 for value in left + right):
        raise ValueError("clean distributions must be positive")
    return max(
        max(a / b, b / a)
        for a, b in zip(left, right)
    )


def bounded_recording_neighborhoods_overlap(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
    lower: Fraction,
    upper: Fraction,
) -> bool:
    """Exact overlap with each unknown recording weight in [lower, upper]."""

    lower = Fraction(lower)
    upper = Fraction(upper)
    if not 0 < lower <= upper <= 1:
        raise ValueError("recording bounds require 0 < lower <= upper <= 1")
    return recording_ratio_required_for_overlap(left, right) <= upper / lower


def common_bounded_recorded_joint(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
    lower: Fraction,
    upper: Fraction,
) -> Tuple[Vector, Vector, Vector, Fraction]:
    """Construct equal recorded masses under bounded unknown recording."""

    left = as_distribution(left)
    right = as_distribution(right)
    if len(left) != len(right):
        raise ValueError("distribution dimensions differ")
    lower = Fraction(lower)
    upper = Fraction(upper)
    if not bounded_recording_neighborhoods_overlap(
        left,
        right,
        lower,
        upper,
    ):
        raise ValueError("bounded recording neighborhoods do not overlap")
    recorded_joint = tuple(
        max(lower * a, lower * b)
        for a, b in zip(left, right)
    )
    left_recording = tuple(
        mass / clean for mass, clean in zip(recorded_joint, left)
    )
    right_recording = tuple(
        mass / clean for mass, clean in zip(recorded_joint, right)
    )
    if any(
        not lower <= probability <= upper
        for probability in left_recording + right_recording
    ):
        raise AssertionError("bounded overlap construction left its interval")
    record_rate = sum(recorded_joint, Fraction(0))
    if not 0 < record_rate <= 1:
        raise AssertionError("invalid constructed record rate")
    return left_recording, right_recording, recorded_joint, record_rate


def l1_margin_recording_ratio_ceiling(gamma: float) -> float:
    """Sufficient ratio boundary from an L1 tier-separation margin."""

    if not 0 < gamma < 2:
        raise ValueError("gamma must lie in (0,2)")
    return exp(2 * atanh(gamma / 2))


def recover_from_known_recording(
    recorded_joint: Sequence[Fraction],
    recording_probabilities: Sequence[Fraction],
) -> Distribution:
    """Recover a clean response law from known positive recording weights."""

    recorded_joint = tuple(Fraction(value) for value in recorded_joint)
    recording = tuple(Fraction(value) for value in recording_probabilities)
    if len(recorded_joint) != len(recording) or not recorded_joint:
        raise ValueError("recorded masses and recording weights must align")
    if any(value < 0 for value in recorded_joint):
        raise ValueError("recorded mass is negative")
    if any(not 0 < value <= 1 for value in recording):
        raise ValueError("recording probabilities must lie in (0,1]")
    return as_distribution(
        mass / probability
        for mass, probability in zip(recorded_joint, recording)
    )


def total_draws_for_per_menu_count(
    per_menu_count: int,
    menu_count: int,
    selection_floor: float,
    undercount_failure_probability: float,
) -> int:
    """Sufficient iid total draws for every menu to receive a target count."""

    if per_menu_count <= 0 or menu_count <= 0:
        raise ValueError("counts must be positive")
    if not 0 < selection_floor <= 1 / menu_count:
        raise ValueError("selection floor is incompatible with menu count")
    if not 0 < undercount_failure_probability < 1:
        raise ValueError("failure probability must lie in (0,1)")
    count_term = 2 * per_menu_count / selection_floor
    probability_term = (
        8
        / selection_floor
        * log(menu_count / undercount_failure_probability)
    )
    return ceil(max(count_term, probability_term))


def selection_scaled_lecam_lower_bound(
    informative_menu_probability: float,
    informative_menu_kl: float,
    target_maximum_error: float,
) -> float:
    """Necessary total-query budget from KL chain, Pinsker, and Le Cam."""

    if not 0 < informative_menu_probability <= 1:
        raise ValueError("informative menu probability must lie in (0,1]")
    if not informative_menu_kl > 0:
        raise ValueError("informative menu KL must be positive")
    if not 0 < target_maximum_error < 0.5:
        raise ValueError("target error must lie in (0,1/2)")
    return (
        2 * (1 - 2 * target_maximum_error) ** 2
        / (informative_menu_probability * informative_menu_kl)
    )
