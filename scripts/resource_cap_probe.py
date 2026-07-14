from __future__ import annotations

import argparse
import time


def main() -> int:
    parser = argparse.ArgumentParser(description="Deliberately breach a memory cap.")
    parser.add_argument("--allocate-mb", type=int, required=True)
    args = parser.parse_args()
    time.sleep(2.0)  # Allow the wrapper to assign this PID to its Job Object.
    blocks = []
    for _ in range(args.allocate_mb):
        blocks.append(bytearray(1024 * 1024))
        time.sleep(0.005)
    time.sleep(5.0)
    return len(blocks) < 0


if __name__ == "__main__":
    raise SystemExit(main())
