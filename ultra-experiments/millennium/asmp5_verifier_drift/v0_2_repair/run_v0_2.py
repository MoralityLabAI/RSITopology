"""Registered ASMP-5 verifier-drift v0.2 runner."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Iterable

import psutil

from verifier_drift import canonical_json, run_registered


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
REGISTRATION = HERE / "registration_v0_2.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to overwrite non-identical artifact: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def git(*args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, check=True, capture_output=True, text=text)


def verify_registration() -> dict[str, Any]:
    if not REGISTRATION.is_file():
        raise FileNotFoundError("registration_v0_2.json must be committed before the claim run")
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    if registration.get("schema_version") != "asmp5_verifier_drift_registration_v0_2":
        raise ValueError("unexpected registration schema")
    commit = git("rev-parse", "HEAD").stdout.strip()
    for relative, expected in registration["source_hashes"].items():
        path = REPO_ROOT / relative
        if sha256(path) != expected:
            raise RuntimeError(f"registration hash mismatch: {relative}")
        if git("status", "--porcelain", "--", relative).stdout.strip():
            raise RuntimeError(f"registered source is dirty: {relative}")
    if git("diff", "--quiet", "HEAD").returncode != 0:
        raise RuntimeError("tracked worktree diff must be empty at run start")
    return {**registration, "run_commit": commit}


class PeakRSS:
    def __init__(self) -> None:
        self.process = psutil.Process(os.getpid())
        self.peak = self.process.memory_info().rss
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._sample, daemon=True)

    def _sample(self) -> None:
        while not self.stop.wait(0.005):
            self.peak = max(self.peak, self.process.memory_info().rss)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_args):
        self.stop.set()
        self.thread.join()
        self.peak = max(self.peak, self.process.memory_info().rss)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=HERE / "artifacts_v0_2")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    registration = verify_registration()
    protocol_path = HERE / "protocol_v0_2.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    output_dir = args.output_dir.resolve()
    if output_dir == HERE or HERE in output_dir.parents and output_dir.name != "artifacts_v0_2":
        raise ValueError("output must be the dedicated artifacts_v0_2 directory or an external path")
    result_path = output_dir / "result_v0_2.json"
    receipt_path = output_dir / "receipt_v0_2.json"
    if result_path.exists() or receipt_path.exists():
        raise FileExistsError("registered outputs already exist")

    started = time.perf_counter()
    with PeakRSS() as memory:
        result = run_registered(protocol)
    elapsed = time.perf_counter() - started
    resource = protocol["resource_ceiling"]
    resource_pass = elapsed <= resource["wall_seconds"] and memory.peak <= resource["process_peak_rss_bytes"]
    result["resource_receipt"] = {
        "elapsed_seconds": elapsed,
        "process_peak_rss_bytes": memory.peak,
        "wall_ceiling_seconds": resource["wall_seconds"],
        "process_peak_rss_ceiling_bytes": resource["process_peak_rss_bytes"],
        "pass": resource_pass,
    }
    if not resource_pass:
        result["instrument_status"] = "unavailable"
        result["runner_gate_pass"] = False
        result["stage_decision"] = resource["on_exceed"]
    result["registration_sha256"] = sha256(REGISTRATION)
    result["protocol_sha256"] = sha256(protocol_path)
    result_payload = canonical_json(result).encode()
    write_once(result_path, result_payload)
    receipt = {
        "schema_version": "asmp5_verifier_drift_receipt_v0_2",
        "registration_sha256": sha256(REGISTRATION),
        "protocol_sha256": sha256(protocol_path),
        "result_sha256": hashlib.sha256(result_payload).hexdigest(),
        "source_commit": registration["run_commit"],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "psutil": psutil.__version__,
            "cpu_count": os.cpu_count(),
        },
    }
    write_once(receipt_path, canonical_json(receipt).encode())
    print(
        canonical_json(
            {
                "instrument_status": result["instrument_status"],
                "runner_gate_pass": result["runner_gate_pass"],
                "stage_decision": result["stage_decision"],
                "elapsed_seconds": elapsed,
                "peak_rss_bytes": memory.peak,
                "result": str(result_path),
            }
        ),
        end="",
    )
    return 0 if result["runner_gate_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
