from __future__ import annotations

import sys


def configure_exact_serialization() -> None:
    """Allow trusted exact certificates to exceed CPython's decimal limit."""
    setter = getattr(sys, "set_int_max_str_digits", None)
    if setter is not None:
        setter(0)


def main() -> None:
    configure_exact_serialization()
    from run_boundary_frontier import main as run_v0_2

    run_v0_2()


if __name__ == "__main__":
    main()

