"""Integer-only Q16.48 arithmetic for the signed-control risk gate.

The public fixed-point format is signed Q16.48. Square roots are rounded down,
which makes ``1 - sqrt(retention)`` conservative. Sine is evaluated on
``[0, pi/2]`` with the degree-19 odd Maclaurin polynomial. Coefficients are
stored in Q72 to keep coefficient and Horner rounding below a Q16.48 ulp.

For ``0 <= x < 8/5``, the analytic truncation error is bounded by
``x**21 / 21! < 0.106566`` Q16.48 ulp. Bounding the rounded ``x**2``
perturbation gives ``< 0.171379`` ulp. Q72 coefficient and Horner rounding is
bounded by ``x * sum((13/5)**k, k=0..9) / 2**24 < 0.000842`` ulp, and final
rounding is at most ``0.5`` ulp. The total absolute evaluation error is below
``0.778787`` Q16.48 ulp. ``sin_q_upper`` adds one ulp and clamps at one, so the
value used by the authorization gate is one-sided conservative.

There are no float literals, float operations, NumPy calls, or platform-sized
integer assumptions in this module. Products fit a signed Rust ``i128`` when
the validated public-domain inputs are used.
"""

from __future__ import annotations


FRACTION_BITS = 48
SCALE = 1 << FRACTION_BITS
ONE = SCALE
TWO = 2 * SCALE
ZERO = 0

# floor(1e-12 * 2**48). The strict float comparison is margin > 1e-12,
# so the fixed comparison is encoded_margin > this constant.
NEGATIVE_CONTROL_EPSILON_Q_FLOOR = 281

COEFFICIENT_FRACTION_BITS = 72
COEFFICIENT_SCALE = 1 << COEFFICIENT_FRACTION_BITS

# ceil(pi * 2**48), generated from the published decimal expansion of pi.
PI_Q_CEIL = 884_279_719_003_556
HALF_PI_Q_CEIL = 442_139_859_501_778
DEGREES_180 = 180 * SCALE
DEGREES_360 = 360 * SCALE

# round(((-1)**k / (2*k+1)!) * 2**72), ties away from zero.
# Powers, in order: x, x**3, ..., x**19.
SIN_COEFFICIENTS_Q72 = (
    4_722_366_482_869_645_213_696,
    -787_061_080_478_274_202_283,
    39_353_054_023_913_710_114,
    -936_977_476_759_850_241,
    13_013_576_066_109_031,
    -118_305_236_964_628,
    758_366_903_619,
    -3_611_270_970,
    13_276_732,
    -38_821,
)


def require_int(value: int, label: str) -> int:
    """Reject booleans and non-integers at the guest-compatible boundary."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a fixed-point integer")
    return value


def div_ceil_nonnegative(numerator: int, denominator: int) -> int:
    """Return ceil(numerator / denominator) for nonnegative integers."""

    if numerator < 0 or denominator <= 0:
        raise ValueError("ceil division requires numerator >= 0 and denominator > 0")
    return (numerator + denominator - 1) // denominator


def div_round_nearest(numerator: int, denominator: int) -> int:
    """Round a signed rational to nearest, with exact ties away from zero."""

    if denominator <= 0:
        raise ValueError("rounding denominator must be positive")
    negative = numerator < 0
    magnitude = -numerator if negative else numerator
    quotient, remainder = divmod(magnitude, denominator)
    if 2 * remainder >= denominator:
        quotient += 1
    return -quotient if negative else quotient


def mul_q_nearest(left: int, right: int) -> int:
    """Multiply two Q16.48 values with nearest, ties-away rounding."""

    return div_round_nearest(left * right, SCALE)


def integer_sqrt_floor(value: int) -> int:
    """Floor square root using Newton iteration and integer division only."""

    if value < 0:
        raise ValueError("square root input must be nonnegative")
    if value < 2:
        return value
    estimate = 1 << ((value.bit_length() + 1) // 2)
    while True:
        following = (estimate + value // estimate) // 2
        if following >= estimate:
            return estimate
        estimate = following


def sqrt_q_floor(value_q: int) -> int:
    """Return floor(sqrt(value_q / SCALE) * SCALE)."""

    value_q = require_int(value_q, "square root input")
    if value_q < 0:
        raise ValueError("square root input must be nonnegative")
    return integer_sqrt_floor(value_q * SCALE)


def degrees_to_half_radians_q_ceil(angle_degrees_q: int) -> int:
    """Convert degrees to half-angle radians, rounding toward larger risk."""

    angle_degrees_q = require_int(angle_degrees_q, "angle")
    if not 0 <= angle_degrees_q <= DEGREES_180:
        raise ValueError("angle must lie in [0,180]")
    numerator = angle_degrees_q * PI_Q_CEIL
    result = div_ceil_nonnegative(numerator, DEGREES_360)
    return min(HALF_PI_Q_CEIL, result)


def sin_q_nearest(angle_radians_q: int) -> int:
    """Evaluate the documented degree-19 odd polynomial in Q16.48."""

    angle_radians_q = require_int(angle_radians_q, "sine input")
    if not 0 <= angle_radians_q <= HALF_PI_Q_CEIL:
        raise ValueError("sine input must lie in [0,pi/2]")
    square_q = div_round_nearest(angle_radians_q * angle_radians_q, SCALE)
    accumulator_q72 = SIN_COEFFICIENTS_Q72[-1]
    for coefficient_q72 in reversed(SIN_COEFFICIENTS_Q72[:-1]):
        accumulator_q72 = coefficient_q72 + div_round_nearest(
            accumulator_q72 * square_q, SCALE
        )
    result_q = div_round_nearest(
        angle_radians_q * accumulator_q72, COEFFICIENT_SCALE
    )
    return max(ZERO, min(ONE, result_q))


def sin_q_upper(angle_radians_q: int) -> int:
    """Return the sine polynomial plus its one-ulp conservative correction."""

    return min(ONE, sin_q_nearest(angle_radians_q) + 1)


def chord_displacement_q_upper(angle_degrees_q: int) -> int:
    """Return an upper-rounded Q16.48 value for ``2*sin(angle/2)``."""

    half_radians_q = degrees_to_half_radians_q_ceil(angle_degrees_q)
    return min(TWO, 2 * sin_q_upper(half_radians_q))
