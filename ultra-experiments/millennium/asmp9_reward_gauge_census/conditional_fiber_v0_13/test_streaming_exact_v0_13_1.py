from fractions import Fraction

from conditional_fiber import exact_randomized_upper_test
from streaming_exact_v0_13_1 import exact_randomized_upper_test_streaming


def test_streaming_matches_literal_exact_small_registry() -> None:
    for k in (3, 4, 6):
        for n in (1, 2, 5, 9):
            for ratio in (Fraction(3, 2), Fraction(2), Fraction(5, 2)):
                literal = exact_randomized_upper_test(
                    k, n, ratio, Fraction(1, 20)
                )
                streaming = exact_randomized_upper_test_streaming(
                    k, n, ratio, Fraction(1, 20)
                )
                assert streaming.boundary == literal["boundary"]
                assert (
                    streaming.randomization_fraction()
                    == literal["randomization"]
                )
                assert streaming.power_fraction() == literal["power"]


def test_streaming_certificate_uses_exact_cross_multiplication() -> None:
    result = exact_randomized_upper_test_streaming(
        4, 207, Fraction(2), Fraction(1, 20)
    )
    certificate = result.certificate(
        alpha=Fraction(1, 20),
        lower_power=Fraction(39, 50),
        upper_power=Fraction(41, 50),
    )
    assert certificate["exact_size"]["construction_verified"]
    assert certificate["power_above_size"]
    assert certificate["power_in_registered_band"]
