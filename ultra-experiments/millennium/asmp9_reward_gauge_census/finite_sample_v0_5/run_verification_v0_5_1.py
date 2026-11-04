"""Execution-only path correction for registered ASMP-9 v0.5.1."""

from __future__ import annotations

import run_verification as v0_5


v0_5.REPO = v0_5.HERE.parents[3]


if __name__ == "__main__":
    v0_5.main()
