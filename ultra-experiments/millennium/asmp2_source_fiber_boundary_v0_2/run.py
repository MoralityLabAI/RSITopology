"""Run the exact ASMP-2 source-fiber witness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from source_fiber import build_result


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
    print(f"all_gates_passed={str(result['all_gates_passed']).lower()}")
    print(
        "randomized_uniform_success="
        f"{result['fiber_certificate']['randomized_uniform_success']}"
    )
    print(f"output={args.output}")
    return 0 if result["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
