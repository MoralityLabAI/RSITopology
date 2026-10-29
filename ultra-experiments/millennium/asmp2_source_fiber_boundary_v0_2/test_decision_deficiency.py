from fractions import Fraction

from decision_deficiency import (
    best_environment,
    majority_success,
    safety_deficiency,
    sample_complexity,
)


def test_zero_signal_never_beats_one_half() -> None:
    for sample_size in range(11):
        assert majority_success(sample_size, Fraction(0)) == Fraction(1, 2)
        assert safety_deficiency(sample_size, Fraction(0)) == Fraction(1, 2)
    assert sample_complexity(Fraction(0), Fraction(49, 100)) is None


def test_one_sample_value_is_exact() -> None:
    assert majority_success(1, Fraction(1, 8)) == Fraction(5, 8)
    assert safety_deficiency(1, Fraction(1, 8)) == Fraction(3, 8)


def test_even_tie_randomization_matches_previous_odd_size() -> None:
    signal = Fraction(1, 8)
    assert majority_success(2, signal) == majority_success(1, signal)
    assert majority_success(4, signal) == majority_success(3, signal)


def test_signal_strictly_improves_minimax_value() -> None:
    for sample_size in (1, 3, 5, 9):
        assert majority_success(sample_size, Fraction(1, 4)) > majority_success(
            sample_size, Fraction(1, 8)
        )


def test_sample_complexity_is_minimal() -> None:
    signal = Fraction(1, 4)
    delta = Fraction(1, 10)
    sample_size = sample_complexity(signal, delta, maximum=100)
    assert sample_size is not None
    assert safety_deficiency(sample_size, signal) <= delta
    if sample_size:
        assert safety_deficiency(sample_size - 1, signal) > delta


def test_active_choice_uses_largest_safety_signal() -> None:
    signals = (Fraction(1, 16), Fraction(1, 4), Fraction(1, 8))
    assert best_environment(signals) == 1
    assert best_environment((Fraction(1, 8), Fraction(1, 8))) == 0
