"""Run and record the explicitly burned ASMP-9 v0.39 development grid."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import time

import psutil

from gauge_leakage import run_burned_development


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "DEVELOPMENT_RESULTS_v0_39.json"


def canonical_bytes(payload: dict) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def main() -> None:
    started = time.perf_counter()
    payload = run_burned_development()
    payload["elapsed_seconds"] = time.perf_counter() - started
    payload["working_set_bytes_at_completion"] = psutil.Process(
        os.getpid()
    ).memory_info().rss
    scientific = {
        key: value
        for key, value in payload.items()
        if key not in {"elapsed_seconds", "working_set_bytes_at_completion"}
    }
    payload["scientific_content_sha256"] = hashlib.sha256(
        canonical_bytes(scientific)
    ).hexdigest()
    OUTPUT.write_bytes(canonical_bytes(payload))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
