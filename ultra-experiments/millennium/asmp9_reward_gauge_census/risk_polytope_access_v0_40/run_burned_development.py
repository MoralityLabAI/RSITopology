"""Record the complete burned v0.40 multi-loss access table."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import time

import psutil

from risk_polytope_access import run_burned_development


BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "DEVELOPMENT_RESULTS_v0_40.json"


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite {OUTPUT}")
    start = time.perf_counter()
    payload = run_burned_development()
    elapsed = time.perf_counter() - start
    scientific_hash = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    payload["elapsed_seconds"] = elapsed
    payload["working_set_bytes_at_completion"] = psutil.Process(
        os.getpid()
    ).memory_info().rss
    payload["scientific_content_sha256"] = scientific_hash
    OUTPUT.write_bytes(canonical_bytes(payload))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
