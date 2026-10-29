from __future__ import annotations

import json
from pathlib import Path

from expected_weighted_noise import build_result


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts" / "expected_weighted_noise_v1_7.json"


def main() -> None:
    result = build_result()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not result["certified"]:
        failed = [name for name, passed in result["gates"].items() if not passed]
        raise SystemExit(f"expected-weighted-noise gates failed: {failed}")
    print(
        "ASMP-3 expected-weighted-noise TV phase certified: "
        f"{len(result['gates'])}/{len(result['gates'])} gates, "
        f"{len(result['expected_rows'])} rows"
    )


if __name__ == "__main__":
    main()
