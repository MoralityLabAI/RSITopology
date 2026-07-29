"""Emit the explicitly burned centered v0.42 calibration."""

from __future__ import annotations

import json
from pathlib import Path

from finite_sample_access import burned_centered_calibration


BASE = Path(__file__).resolve().parent


def main() -> None:
    output = BASE / "DEVELOPMENT_RESULT_v0_42.json"
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    output.write_text(
        json.dumps(
            burned_centered_calibration(),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
