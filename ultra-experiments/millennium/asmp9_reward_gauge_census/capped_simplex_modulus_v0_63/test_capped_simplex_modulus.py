from fractions import Fraction

import pytest

from capped_simplex_modulus import (
    CAPS,
    FLOOR,
    all_support_bounds,
    binary_probabilities_from_weights,
    common_huber_observation,
    common_recording_observation,
    delta_modulus,
    full_from_ranking_weights,
    huber_threshold,
    in_floor_class,
    is_rum,
    lambda_modulus,
    possible_violation_supports,
    primal_pair,
    ranking_weights,
    rum_projection,
    support_bound,
    symmetric_ratio,
    tv,
    violation_mass,
    violation_support,
)


Q = Fraction
GAMMAS = (Q(1, 4096), Q(3, 1600), Q(1, 200), Q(1, 50))


def grid_laws(denominator: int = 40):
    floor_count = denominator // 10
    for a_count in range(floor_count, denominator - 2 * floor_count + 1):
        for b_count in range(
            floor_count,
            denominator - a_count - floor_count + 1,
        ):
            c_count = denominator - a_count - b_count
            if c_count >= floor_count:
                yield (
                    Q(a_count, denominator),
                    Q(b_count, denominator),
                    Q(c_count, denominator),
                )


def test_rum_polytope_has_unique_ranking_reconstruction():
    for full in grid_laws():
        weights = ranking_weights(full)
        assert sum(weights, Q(0)) == 1
        assert (min(weights) >= 0) == is_rum(full)
        if is_rum(full):
            assert full_from_ranking_weights(weights) == full
            assert binary_probabilities_from_weights(weights) == (
                Q(2, 5),
                Q(3, 5),
                Q(3, 5),
            )


def test_cap_violation_mass_is_exact_tv_projection_distance():
    for full in grid_laws():
        projected = rum_projection(full)
        assert is_rum(projected)
        assert in_floor_class(projected)
        assert tv(full, projected) == violation_mass(full)
        for candidate in grid_laws():
            if is_rum(candidate):
                assert tv(full, candidate) >= violation_mass(full)


def test_supports_and_lower_bounds_are_exhaustive():
    assert possible_violation_supports() == (
        (0,),
        (1,),
        (2,),
        (0, 2),
    )
    for gamma in GAMMAS:
        bounds = all_support_bounds(gamma)
        assert bounds[(0,)] == 1 + Q(5, 2) * gamma
        assert bounds[(2,)] == bounds[(0,)]
        assert bounds[(1,)] == Q(2, 5) / (Q(2, 5) - gamma)
        assert bounds[(0, 2)] == Q(1, 5) / (Q(1, 5) - gamma)
        assert min(bounds.values()) == lambda_modulus(gamma)


def test_primal_pair_attains_both_exact_moduli():
    for gamma in GAMMAS:
        rum, nonrum = primal_pair(gamma)
        assert is_rum(rum)
        assert not is_rum(nonrum)
        assert in_floor_class(rum)
        assert in_floor_class(nonrum)
        assert violation_support(nonrum) == (0,)
        assert violation_mass(nonrum) == gamma
        assert tv(rum, nonrum) == delta_modulus(gamma)
        assert symmetric_ratio(rum, nonrum) == lambda_modulus(gamma)


def test_every_rational_grid_cross_tier_pair_obeys_duals():
    gamma = Q(1, 50)
    rum_laws = [law for law in grid_laws(20) if is_rum(law)]
    nonrum_laws = [
        law
        for law in grid_laws(20)
        if violation_mass(law) >= gamma
    ]
    assert rum_laws
    assert nonrum_laws
    for rum in rum_laws:
        for nonrum in nonrum_laws:
            assert tv(rum, nonrum) >= delta_modulus(gamma)
            support = violation_support(nonrum)
            assert (
                symmetric_ratio(rum, nonrum)
                >= support_bound(gamma, support)
                >= lambda_modulus(gamma)
            )


def test_huber_boundary_has_common_observation_and_contaminants():
    for gamma in GAMMAS:
        left, right = primal_pair(gamma)
        observed = common_huber_observation(gamma)
        epsilon = huber_threshold(gamma)
        for clean in (left, right):
            contaminant = tuple(
                (
                    observed[index] - (1 - epsilon) * clean[index]
                )
                / epsilon
                for index in range(3)
            )
            assert min(contaminant) >= 0
            assert sum(contaminant, Q(0)) == 1


def test_recording_boundary_has_common_joint_law():
    for gamma in GAMMAS:
        left, right = primal_pair(gamma)
        joint, left_recording, right_recording = (
            common_recording_observation(gamma)
        )
        for index in range(3):
            assert left[index] * left_recording[index] == joint[index]
            assert right[index] * right_recording[index] == joint[index]
        assert sum(joint, Q(0)) <= 1


def test_invalid_parameters_fail_closed():
    with pytest.raises(ValueError):
        delta_modulus(Q(0))
    with pytest.raises(ValueError):
        lambda_modulus(Q(1, 49))
    with pytest.raises(ValueError):
        support_bound(Q(1, 100), ())
    with pytest.raises(ValueError):
        ranking_weights((Q(1, 2), Q(1, 2), Q(1, 10)))
    assert sum(CAPS, Q(0)) == Q(7, 5)
    assert FLOOR == Q(1, 10)

