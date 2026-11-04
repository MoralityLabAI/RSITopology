"""Run the sealed v0.34 analyzer against the additive Prime schema."""

from __future__ import annotations

import analyze_burned_pilot as sealed_analyzer
import run_burned_pilot as sealed_runner


PRIME_REGISTRATION_SCHEMA = (
    "asmp9_physical_acquisition_burned_pilot_registration_v0_34_3"
)


def main() -> None:
    """Adapt only the registered schema identifier, then call sealed analysis."""
    sealed_runner.REGISTRATION_SCHEMA = PRIME_REGISTRATION_SCHEMA
    sealed_analyzer.REGISTRATION_SCHEMA = PRIME_REGISTRATION_SCHEMA
    sealed_analyzer.run(sealed_analyzer.parse_args())


if __name__ == "__main__":
    main()
