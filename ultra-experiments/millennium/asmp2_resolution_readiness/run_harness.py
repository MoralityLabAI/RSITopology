"""Run the deterministic ASMP-2 resolution-readiness harness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from resolution_harness import build_result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = build_result()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"decision={result['decision']}")
    print(f"stop_is_supported={str(result['stop_is_supported']).lower()}")
    print(f"output={args.output}")
    return 0 if result["stop_is_supported"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
