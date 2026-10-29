from fractions import Fraction as Q

import pytest

from execute_confirmation_v0_42_1 import (
    parse_registered_fraction,
    seed_from_registration_bytes,
)


def test_literal_registered_margin_parses_through_fraction():
    assert parse_registered_fraction("1/1000") == float(Q(1, 1000))


def test_decimal_margin_remains_accepted():
    assert parse_registered_fraction("0.001") == float(Q(1, 1000))


def test_malformed_and_negative_margins_fail_closed():
    with pytest.raises(ValueError, match="invalid registered rational"):
        parse_registered_fraction("not-a-rational")
    with pytest.raises(ValueError, match="cannot be negative"):
        parse_registered_fraction("-1/1000")


def test_repair_seed_is_content_bound_and_version_separated():
    first = seed_from_registration_bytes(b"registration")
    assert first == seed_from_registration_bytes(b"registration")
    assert first != seed_from_registration_bytes(b"registration-2")
