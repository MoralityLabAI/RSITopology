"""Prime execution shim for the sealed ASMP-9 v0.34 measurement runner.

The measurement implementation remains in ``run_burned_pilot.py``. This
additive shim changes only the accepted registration schema so a Linux runtime
can bind its own server binary, hard-cap wrapper, cleanup script, and paths
without modifying the immutable local v0.34.2 registration.
"""

from __future__ import annotations

from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_burned_pilot as sealed_runner  # noqa: E402


PRIME_REGISTRATION_SCHEMA = (
    "asmp9_physical_acquisition_burned_pilot_registration_v0_34_3"
)


def main() -> None:
    sealed_runner.REGISTRATION_SCHEMA = PRIME_REGISTRATION_SCHEMA
    sealed_runner.main()


if __name__ == "__main__":
    main()

