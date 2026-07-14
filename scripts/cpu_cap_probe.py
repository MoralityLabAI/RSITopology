from __future__ import annotations

import argparse
import math
import time


def main() -> int:
    parser = argparse.ArgumentParser(description="Busy-loop CPU quota probe.")
    parser.add_argument("--seconds", type=float, default=8.0)
    args = parser.parse_args()
    deadline = time.monotonic() + args.seconds
    value = 0.0
    while time.monotonic() < deadline:
        value += math.sin(value + 0.1) ** 2
    print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
