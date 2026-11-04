"""Registered runner for the ASMP-5A finite bounded-tiling seed."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Iterable

import psutil

from tiling import canonical_json, run_census


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
REGISTRATION = HERE / "registration_v0_1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, check=True, capture_output=True, text=True)


def write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def verify_registration() -> dict[str, Any]:
    if not REGISTRATION.is_file():
        raise FileNotFoundError("registration_v0_1.json must be committed before running")
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    if registration["schema_version"] != "asmp5a_bounded_tiling_registration_v0_1":
        raise ValueError("unexpected registration schema")
    for relative, expected in registration["source_hashes"].items():
        path = REPO_ROOT / relative
        if sha256(path) != expected:
            raise RuntimeError(f"registration mismatch: {relative}")
        if git("status", "--porcelain", "--", relative).stdout.strip():
            raise RuntimeError(f"registered source dirty: {relative}")
    if git("diff", "--quiet", "HEAD").returncode != 0:
        raise RuntimeError("tracked worktree diff must be empty")
    return {**registration, "run_commit": git("rev-parse", "HEAD").stdout.strip()}


class PeakRSS:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.peak = self.process.memory_info().rss
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._loop, daemon=True)

    def _loop(self):
        while not self.stop.wait(0.005):
            self.peak = max(self.peak, self.process.memory_info().rss)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_args):
        self.stop.set()
        self.thread.join()
        self.peak = max(self.peak, self.process.memory_info().rss)


def parse_args(argv: Iterable[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=HERE / "artifacts_v0_1")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    registration = verify_registration()
    protocol_path = HERE / "protocol_v0_1.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    output = args.output_dir.resolve()
    result_path, receipt_path = output / "result_v0_1.json", output / "receipt_v0_1.json"
    if result_path.exists() or receipt_path.exists():
        raise FileExistsError("registered outputs already exist")
    started = time.perf_counter()
    with PeakRSS() as memory:
        result = run_census(protocol)
    elapsed = time.perf_counter() - started
    ceiling = protocol["resource_ceiling"]
    resource_pass = elapsed <= ceiling["wall_seconds"] and memory.peak <= ceiling["process_peak_rss_bytes"]
    result["resource_receipt"] = {
        "elapsed_seconds": elapsed,
        "process_peak_rss_bytes": memory.peak,
        "wall_ceiling_seconds": ceiling["wall_seconds"],
        "process_peak_rss_ceiling_bytes": ceiling["process_peak_rss_bytes"],
        "pass": resource_pass,
    }
    if not resource_pass:
        result["instrument_status"] = "unavailable"
        result["verdict"] = "unavailable_resource_cap"
    result["registration_sha256"] = sha256(REGISTRATION)
    result["protocol_sha256"] = sha256(protocol_path)
    payload = canonical_json(result).encode()
    write_once(result_path, payload)
    receipt = {
        "schema_version": "asmp5a_bounded_tiling_receipt_v0_1",
        "source_commit": registration["run_commit"],
        "registration_sha256": sha256(REGISTRATION),
        "protocol_sha256": sha256(protocol_path),
        "result_sha256": hashlib.sha256(payload).hexdigest(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "psutil": psutil.__version__,
            "cpu_count": os.cpu_count(),
        },
    }
    write_once(receipt_path, canonical_json(receipt).encode())
    print(canonical_json({"verdict": result["verdict"], "elapsed_seconds": elapsed, "peak_rss_bytes": memory.peak}), end="")
    return 0 if result["instrument_status"] == "valid" and resource_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
