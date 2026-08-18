import sys

from run_boundary_frontier_v0_2_1 import configure_exact_serialization


def test_large_exact_integer_decimal_serialization_is_enabled() -> None:
    configure_exact_serialization()
    value = 10**5000 + 7
    rendered = str(value)
    assert len(rendered) == 5001
    assert rendered.endswith("007")
    getter = getattr(sys, "get_int_max_str_digits", None)
    if getter is not None:
        assert getter() == 0

