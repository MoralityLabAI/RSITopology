from __future__ import annotations

import itertools
import math
import random

import pytest

from finite_sample import (
    binary_entropy,
    bounded_unit_ratios,
    channel_capacity,
    farey_sequence,
    fano_fixed_budget_lower_bound,
    full_signature,
    identify_ray,
    logical_query_bound,
    nonadaptive_farey_lower_bound,
    primitive_ray_count,
    primitive_rays,
    repetitions_required,
    theorem_width,
)


@pytest.mark.parametrize("dimension,bound", [(2, 1), (2, 5), (3, 3)])
def test_primitive_count_matches_enumeration(dimension: int, bound: int) -> None:
    assert primitive_ray_count(dimension, bound) == len(
        primitive_rays(dimension, bound)
    )


@pytest.mark.parametrize("bound", range(1, 13))
def test_farey_cells_contain_at_most_one_bounded_ratio(bound: int) -> None:
    farey = farey_sequence(max(1, bound - 1))
    ratios = bounded_unit_ratios(bound)
    for left, right in itertools.pairwise(farey):
        assert sum(left < value < right for value in ratios) <= 1


@pytest.mark.parametrize(
    "bound,expected", [(1, 1), (2, 1), (3, 2), (4, 3), (9, 8)]
)
def test_width_formula(bound: int, expected: int) -> None:
    assert theorem_width(bound) == expected


@pytest.mark.parametrize(
    "dimension,bound", [(2, 1), (2, 2), (2, 5), (3, 3)]
)
def test_population_constructor_recovers_every_small_ray(
    dimension: int, bound: int
) -> None:
    for index, vector in enumerate(primitive_rays(dimension, bound)):
        estimate, samples, width = identify_ray(
            vector,
            bound,
            eta=0.0,
            force_repetitions=4096,
            seed=100_000 * dimension + 1000 * bound + index,
        )
        assert estimate == vector
        assert samples <= logical_query_bound(
            dimension, bound
        ) * 4096
        assert width <= theorem_width(bound)


@pytest.mark.parametrize("bound", range(3, 10))
def test_lower_witness_is_indistinguishable_below_width(bound: int) -> None:
    left = (bound, bound - 1)
    right = (bound - 1, bound - 2)
    assert full_signature(left, bound - 2) == full_signature(
        right, bound - 2
    )
    assert full_signature(left, bound - 1) != full_signature(
        right, bound - 1
    )


def test_noisy_constructor_on_seeded_sample() -> None:
    rng = random.Random(90500)
    rays = primitive_rays(3, 4)
    selected = rng.sample(rays, 64)
    for index, vector in enumerate(selected):
        estimate, samples, width = identify_ray(
            vector,
            4,
            eta=0.1,
            alpha=1e-6,
            seed=90501 + index,
        )
        assert estimate == vector
        assert samples <= logical_query_bound(3, 4) * repetitions_required(
            0.1, 1e-6, logical_query_bound(3, 4)
        )
        assert width <= theorem_width(4)


@pytest.mark.parametrize("eta", [0.0, 0.1, 0.25, 0.49])
def test_tie_input_cannot_raise_channel_capacity(eta: float) -> None:
    capacity = channel_capacity(eta)
    entropy_strict = binary_entropy(eta)
    # Grid all input mixtures over {-1,0,+1}. The analytic proof is
    # I=H(Y)-[(p_-+p_+)h2(eta)+p_0], so I<=1-h2(eta).
    for minus in range(21):
        for tie in range(21 - minus):
            plus = 20 - minus - tie
            weights = [minus / 20, tie / 20, plus / 20]
            output_one = (
                weights[0] * eta
                + weights[1] * 0.5
                + weights[2] * (1.0 - eta)
            )
            mutual_information = binary_entropy(output_one) - (
                (weights[0] + weights[2]) * entropy_strict + weights[1]
            )
            assert mutual_information <= capacity + 1e-12


def test_fano_bound_diverges_at_fair_channel() -> None:
    assert math.isinf(fano_fixed_budget_lower_bound(3, 4, 0.5, 0.05))


def test_repetition_bound_worsens_monotonically() -> None:
    values = [repetitions_required(eta, 0.05, 20) for eta in (0, 0.1, 0.2, 0.3, 0.4)]
    assert values == sorted(values)


def test_nonadaptive_lower_bound_has_quadratic_farey_growth() -> None:
    # |F_B| is asymptotically quadratic. The finite ratio need not equal four,
    # but the B=128 bound must materially outgrow the B=16 bound after
    # normalizing confidence and channel.
    small = nonadaptive_farey_lower_bound(16, 0.1, 0.05)
    large = nonadaptive_farey_lower_bound(128, 0.1, 0.05)
    assert large / small > 40


@pytest.mark.parametrize(
    "args",
    [
        (-0.1, 0.05, 10),
        (0.5, 0.05, 10),
        (0.1, 0.0, 10),
        (0.1, 0.5, 10),
        (0.1, 0.05, 0),
    ],
)
def test_invalid_repetition_inputs_raise(args: tuple[float, float, int]) -> None:
    with pytest.raises(ValueError):
        repetitions_required(*args)
