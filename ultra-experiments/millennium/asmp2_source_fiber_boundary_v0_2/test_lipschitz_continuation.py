from fractions import Fraction

import pytest

from lipschitz_continuation import (
    fill_distance,
    frozen_continuation_report,
    lower_envelope,
    upper_envelope,
)


def test_mcshane_whitney_envelopes_interpolate_sources() -> None:
    sources = (Fraction(-1), Fraction(0), Fraction(1))
    values = (Fraction(1, 4), Fraction(3, 8), Fraction(1, 2))
    lipschitz = Fraction(1, 4)
    for source, value in zip(sources, values):
        assert upper_envelope(source, sources, values, lipschitz) == value
        assert lower_envelope(source, sources, values, lipschitz) == value


def test_every_admissible_value_lies_between_exact_envelopes() -> None:
    sources = (Fraction(-1), Fraction(1))
    values = (Fraction(7, 16), Fraction(7, 16))
    lipschitz = Fraction(1, 4)
    x = Fraction(0)
    assert lower_envelope(x, sources, values, lipschitz) == Fraction(3, 16)
    assert upper_envelope(x, sources, values, lipschitz) == Fraction(11, 16)


def test_fill_distance_on_interval_is_exact() -> None:
    assert fill_distance(
        Fraction(-1), Fraction(1), (Fraction(-1), Fraction(1))
    ) == Fraction(1)
    assert fill_distance(
        Fraction(-1),
        Fraction(1),
        (Fraction(-1), Fraction(0), Fraction(1)),
    ) == Fraction(1, 2)


def test_midpoint_active_addition_closes_frozen_margin() -> None:
    report = frozen_continuation_report()
    assert report["endpoint_design_fails"]
    assert report["midpoint_addition_certifies"]
    assert report["exact_margin_cover_identity"]
    assert report["endpoint_worst_upper_envelope"] == "11/16"
    assert report["covered_worst_upper_envelope"] == "9/16"


def test_inconsistent_source_values_are_rejected() -> None:
    with pytest.raises(ValueError, match="violate"):
        upper_envelope(
            Fraction(0),
            (Fraction(-1), Fraction(1)),
            (Fraction(0), Fraction(1)),
            Fraction(1, 4),
        )
