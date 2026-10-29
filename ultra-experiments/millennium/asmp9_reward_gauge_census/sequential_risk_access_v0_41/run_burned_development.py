"""Run the explicitly burned v0.41 adaptivity-gap development fixture."""

from __future__ import annotations

import json
from pathlib import Path

from sequential_access import burned_adaptivity_gap


BASE = Path(__file__).resolve().parent


def main() -> None:
    output = BASE / "DEVELOPMENT_RESULT_v0_41.json"
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    output.write_text(
        json.dumps(
            burned_adaptivity_gap(),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
