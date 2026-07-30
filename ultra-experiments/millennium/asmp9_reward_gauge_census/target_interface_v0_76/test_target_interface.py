from __future__ import annotations

import pytest

from target_interface import classify_target_interface


TARGET = ("left", "left", "right", "right")


def test_exact_partition_match() -> None:
    result = classify_target_interface(TARGET, ("a", "a", "b", "b"))
    assert result.status == "exact_target_interface"
    assert result.target_recoverable
    assert result.representative_insensitive
    assert result.exact_partition_match
    assert result.target_decoder == (("a", "left"), ("b", "right"))
    assert result.representative_insensitive_encoder == (
        ("left", "a"),
        ("right", "b"),
    )


def test_finer_observation_recovers_target_but_leaks_representative() -> None:
    result = classify_target_interface(TARGET, ("a", "b", "c", "d"))
    assert result.status == "recoverable_with_representative_leakage"
    assert result.target_recoverable
    assert not result.representative_insensitive
    assert not result.exact_partition_match
    assert result.underidentification_witnesses == ()
    assert result.representative_leakage_witnesses == ((0, 1), (2, 3))
    assert result.target_decoder is not None
    assert result.representative_insensitive_encoder is None


def test_coarser_observation_is_underidentified_but_invariant() -> None:
    result = classify_target_interface(TARGET, ("a", "a", "a", "a"))
    assert result.status == "underidentified"
    assert not result.target_recoverable
    assert result.representative_insensitive
    assert result.target_decoder is None
    assert result.representative_insensitive_encoder is not None
    assert result.underidentification_witnesses == (
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
    )


def test_cross_cut_partition_has_both_failures() -> None:
    result = classify_target_interface(TARGET, ("a", "b", "a", "b"))
    assert result.status == "cross_cut_misspecified_interface"
    assert not result.target_recoverable
    assert not result.representative_insensitive
    assert result.target_decoder is None
    assert result.representative_insensitive_encoder is None
    assert result.representative_leakage_witnesses == ((0, 1), (2, 3))
    assert result.underidentification_witnesses == ((0, 2), (1, 3))


def test_singleton_observation_can_decode_constant_target_with_leakage() -> None:
    result = classify_target_interface(
        ("same", "same", "same"),
        ("x", "y", "z"),
    )
    assert result.status == "recoverable_with_representative_leakage"
    assert result.target_recoverable


@pytest.mark.parametrize(
    ("target", "observation"),
    [
        ((), ()),
        (("a",), ("x", "y")),
    ],
)
def test_invalid_universes_are_rejected(target, observation) -> None:
    with pytest.raises(ValueError):
        classify_target_interface(target, observation)
