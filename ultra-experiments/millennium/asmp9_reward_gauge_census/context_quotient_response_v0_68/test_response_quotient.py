from fractions import Fraction

import pytest

from response_quotient import (
    exhaustive_small_audit,
    gauge_shift,
    invariant_linear_estimand,
    same_gauge_orbit,
    shared_effect_intersection,
    within_reference_quotient,
)


def test_quotient_is_invariant_to_context_order_offsets() -> None:
    measurements = ((10, 13, 9), (-7, -1, -8))
    shifted = gauge_shift(measurements, (100, -25))
    assert within_reference_quotient(measurements) == ((3, -1), (6, -1))
    assert within_reference_quotient(shifted) == ((3, -1), (6, -1))
    assert same_gauge_orbit(measurements, shifted)


def test_quotient_is_maximal_not_merely_invariant() -> None:
    left = ((0, 2, 5), (4, 3, 9))
    right = ((10, 12, 15), (-3, -4, 2))
    different = ((10, 12, 14), (-3, -4, 2))
    assert same_gauge_orbit(left, right)
    assert not same_gauge_orbit(left, different)


def test_linear_estimand_criterion() -> None:
    assert invariant_linear_estimand(((1, -1), (2, -2)))
    assert not invariant_linear_estimand(((1, 0), (2, -2)))


def test_shared_effect_gate_distinguishes_local_from_global() -> None:
    compatible = shared_effect_intersection(((0, 2), (1, 3), (1, 2)))
    assert compatible["status"] == "shared_effect_compatible"
    assert compatible["intersection_lower"] == 1
    assert compatible["intersection_upper"] == 2
    assert compatible["intersection_margin"] == 1

    incompatible = shared_effect_intersection(((0, 1), (2, 3)))
    assert incompatible["status"] == "context_conditioning_required"
    assert incompatible["intersection_margin"] == -1


def test_arm_specific_order_interaction_is_not_removed() -> None:
    # The quotient removes a common order shift, but correctly retains an
    # arm-by-order interaction.  This is the successor's falsification control.
    no_interaction = ((0, 2), (10, 12))
    interaction = ((0, 2), (10, 15))
    assert within_reference_quotient(no_interaction) == ((2,), (2,))
    assert within_reference_quotient(interaction) == ((2,), (5,))


def test_exact_audit_counts() -> None:
    audit = exhaustive_small_audit()
    assert audit == {
        "measurement_matrices": 729,
        "offset_vectors": 25,
        "quotient_invariance_checks": 18_225,
        "maximality_checks": 729,
        "linear_estimand_checks": 729,
    }


@pytest.mark.parametrize(
    "bad",
    [
        (),
        ((1,),),
        ((1, 2), (3,)),
    ],
)
def test_malformed_measurements_fail_closed(bad) -> None:
    with pytest.raises(ValueError):
        within_reference_quotient(bad)
