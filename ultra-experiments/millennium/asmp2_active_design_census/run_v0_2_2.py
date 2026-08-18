"""Resource-measurement repair for the ASMP-2 active-design census."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import threading
import time
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import psutil
import sympy as sp

import run as scientific
import run_v0_2_1 as performance


HERE = Path(__file__).resolve().parent


class RSSMonitor:
    def __init__(self, interval_seconds: float = 0.01):
        self.interval_seconds = interval_seconds
        self.process = psutil.Process()
        self.peak = self.process.memory_info().rss
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._sample, name="rss-monitor", daemon=True)

    def _sample(self) -> None:
        while not self.stop_event.wait(self.interval_seconds):
            self.peak = max(self.peak, self.process.memory_info().rss)

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> int:
        self.peak = max(self.peak, self.process.memory_info().rss)
        self.stop_event.set()
        self.thread.join(timeout=1)
        return self.peak


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--amendment", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    operational_started = time.perf_counter()
    monitor = RSSMonitor()
    monitor.start()
    args = parse_args(argv)
    amendment_path = args.amendment.resolve()
    amendment = json.loads(amendment_path.read_text(encoding="utf-8"))
    if amendment.get("schema_version") != "asmp2_active_design_amendment_v0_2_2":
        raise ValueError("unexpected amendment schema")
    scientific_protocol_path = HERE / amendment["scientific_parent_protocol"]
    performance_protocol_path = HERE / amendment["performance_parent_amendment"]
    if scientific.sha256_file(scientific_protocol_path) != amendment["scientific_parent_sha256"]:
        raise ValueError("scientific parent hash mismatch")
    if scientific.sha256_file(performance_protocol_path) != amendment["performance_parent_sha256"]:
        raise ValueError("performance parent hash mismatch")
    protocol = json.loads(scientific_protocol_path.read_text(encoding="utf-8"))
    performance_amendment = json.loads(performance_protocol_path.read_text(encoding="utf-8"))
    sealed = (
        amendment_path, scientific_protocol_path, performance_protocol_path,
        HERE / "CLAIM_PACKET.md", HERE / "CLAIM_PACKET_v0_2_1.md", HERE / "CLAIM_PACKET_v0_2_2.md",
        HERE / "README.md", HERE / "README_v0_2_1.md", HERE / "README_v0_2_2.md",
        HERE / "run.py", HERE / "run_v0_2_1.py", Path(__file__).resolve(),
        HERE / "verify_result.py", HERE / "verify_result_v0_2_1.py", HERE / "verify_result_v0_2_2.py",
        HERE / "test_active_design.py", HERE / "test_active_design_v0_2_1.py", HERE / "test_active_design_v0_2_2.py",
    )
    output_dir = args.output_dir.resolve()
    if any(output_dir == path or output_dir in path.parents for path in sealed):
        raise ValueError("output directory aliases a sealed input")
    result_path = output_dir / "result_v0_2_2.json"
    receipt_path = output_dir / "receipt_v0_2_2.json"
    if result_path.exists() or receipt_path.exists():
        raise FileExistsError("registered v0.2.2 output already exists")
    registration = scientific.bind_committed_inputs(sealed)
    original_census = scientific.exhaustive_census
    scientific.exhaustive_census = lambda _protocol: performance.fast_census(_protocol, performance_amendment)
    try:
        result = scientific.run_registered(protocol)
    finally:
        scientific.exhaustive_census = original_census
    result["schema_version"] = "asmp2_active_design_result_v0_2_2"
    result["protocol_id"] = amendment["protocol_id"]
    result["amendment"] = {
        "scope": amendment["amendment_scope"],
        "scientific_contract_changes": amendment["scientific_contract_changes"],
        "scientific_parent_sha256": amendment["scientific_parent_sha256"],
        "performance_parent_sha256": amendment["performance_parent_sha256"],
    }
    result["registration"] = registration
    result["protocol_sha256"] = scientific.sha256_file(scientific_protocol_path)
    result["amendment_sha256"] = scientific.sha256_file(amendment_path)
    operational_elapsed = time.perf_counter() - operational_started
    peak_rss = monitor.stop()
    limits = amendment["resource_measurement"]
    resource_pass = operational_elapsed <= limits["operational_wall_ceiling_seconds"] and peak_rss <= limits["process_peak_rss_bytes"]
    result["resource_receipt"] = {
        "operational_elapsed_seconds": operational_elapsed,
        "operational_wall_ceiling_seconds": limits["operational_wall_ceiling_seconds"],
        "external_total_wall_ceiling_seconds": limits["external_total_wall_ceiling_seconds"],
        "process_peak_rss_bytes": peak_rss,
        "process_peak_rss_ceiling_bytes": limits["process_peak_rss_bytes"],
        "sampling_interval_seconds": 0.01,
        "pass": resource_pass,
    }
    if not resource_pass:
        result["instrument_status"] = "unavailable"
        result["evidence_label"] = "unavailable_resource_cap"
        result["runner_gate_pass"] = False
        result["stage_decision"] = limits["on_exceed"]
    payload = scientific.canonical_json(result).encode()
    scientific.write_once(result_path, payload)
    receipt = {
        "schema_version": "asmp2_active_design_receipt_v0_2_2",
        "git_commit_at_run": registration["commit"],
        "git_tracked_diff_sha256_at_run": registration["tracked_diff_sha256"],
        "scientific_parent_sha256": scientific.sha256_file(scientific_protocol_path),
        "performance_parent_sha256": scientific.sha256_file(performance_protocol_path),
        "amendment_sha256": scientific.sha256_file(amendment_path),
        "claim_packet_sha256": scientific.sha256_file(HERE / "CLAIM_PACKET_v0_2_2.md"),
        "runner_sha256": scientific.sha256_file(Path(__file__).resolve()),
        "verifier_sha256": scientific.sha256_file(HERE / "verify_result_v0_2_2.py"),
        "tests_sha256": scientific.sha256_file(HERE / "test_active_design_v0_2_2.py"),
        "result_sha256": hashlib.sha256(payload).hexdigest(),
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "sympy": sp.__version__, "psutil": psutil.__version__, "platform": platform.platform()},
    }
    scientific.write_once(receipt_path, scientific.canonical_json(receipt).encode())
    print(scientific.canonical_json({"instrument_status": result["instrument_status"], "evidence_label": result["evidence_label"], "stage_decision": result["stage_decision"], "operational_elapsed_seconds": operational_elapsed, "process_peak_rss_bytes": peak_rss, "result": str(result_path)}), end="")
    return 0 if result["runner_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
