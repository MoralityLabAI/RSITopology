"""Owned child used only to validate the Qwen Job Object wrapper."""

from __future__ import annotations

import argparse
from pathlib import Path
import time


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("success", "memory", "cpu", "io", "timeout"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Give the parent time to assign this process to its Job Object.
    time.sleep(0.75)
    if args.mode == "success":
        args.output.write_text("success\n", encoding="utf-8")
        return
    if args.mode == "memory":
        blocks = []
        while True:
            blocks.append(bytearray(16 * 1024 * 1024))
            for offset in range(0, len(blocks[-1]), 4096):
                blocks[-1][offset] = 1
            time.sleep(0.02)
    if args.mode == "cpu":
        deadline = time.monotonic() + 8.0
        value = 1
        while time.monotonic() < deadline:
            value = (value * 1664525 + 1013904223) & 0xFFFFFFFF
        args.output.write_text(f"{value}\n", encoding="utf-8")
        return
    if args.mode == "io":
        payload = b"x" * (8 * 1024 * 1024)
        with args.output.open("wb", buffering=0) as handle:
            while True:
                handle.write(payload)
                handle.flush()
                time.sleep(0.05)
    time.sleep(30.0)


if __name__ == "__main__":
    main()
