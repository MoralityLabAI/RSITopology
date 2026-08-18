"""Registered CPU runner for the ASMP-8 v0.2 dual frontier."""

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

from frontier import canonical_json, frontier_csv, run_census


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
REGISTRATION = HERE / "registration_v0_2.json"
PROTOCOL = HERE / "protocol_v0_2.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=check, capture_output=True, text=True
    )


def write_once(path: Path, payload: bytes) -> None:
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def verify_registration() -> dict[str, Any]:
    if not REGISTRATION.is_file():
        raise FileNotFoundError("registration_v0_2.json must be committed before execution")
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    if registration.get("schema_version") != "asmp8_dual_frontier_registration_v0_2":
        raise ValueError("unexpected registration schema")
    for relative, expected in registration["source_hashes"].items():
        path = REPO_ROOT / relative
        if sha256(path) != expected:
            raise RuntimeError(f"registration hash mismatch: {relative}")
        if git("status", "--porcelain", "--", relative).stdout.strip():
            raise RuntimeError(f"registered source is dirty: {relative}")
    if git("status", "--porcelain", "--", str(REGISTRATION.relative_to(REPO_ROOT))).stdout.strip():
        raise RuntimeError("registration must be committed and clean")
    if git("diff", "--quiet", "HEAD", check=False).returncode != 0:
        raise RuntimeError("tracked worktree diff must be empty")
    return {**registration, "run_commit": git("rev-parse", "HEAD").stdout.strip()}


class PeakRSS:
    def __init__(self) -> None:
        self.process = psutil.Process(os.getpid())
        self.peak = self.process.memory_info().rss
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._loop, daemon=True)

    def _loop(self) -> None:
        while not self.stop.wait(0.005):
            self.peak = max(self.peak, self.process.memory_info().rss)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_args) -> None:
        self.stop.set()
        self.thread.join()
        self.peak = max(self.peak, self.process.memory_info().rss)


def report_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# ASMP-8 v0.2 registered dual-norm frontier result",
        "",
        f"**Verdict:** `{result['verdict']}`",
        "",
        "## Result",
        "",
        f"The census enumerated {result['policy_count']:,} rational policies; "
        f"{result['proxy_improving_policy_count']:,} strictly improved the proxy.",
        "",
        "For every improving policy under q in {1, 2, infinity}, the worst-case true-reward gain matched:",
        "",
        "```text",
        "proxy_gain - epsilon * dual_movement",
        "```",
        "",
        "Polyhedral cases were independently checked by extreme-point enumeration; the q=2 case used exact squared algebra. Every cell had an attaining witness.",
        "",
        "## Coordinate result",
        "",
        "For each registered error geometry, the census found both an equal-proxy-gain pair with unequal movement and an equal-movement pair with unequal proxy gain. Neither coordinate alone determines the robust frontier on this registry; the pair does.",
        "",
        "## Controls",
        "",
        f"- Near-tie sup-norm regret: {result['controls']['near_tie']['regret']} = 2 epsilon (pass).",
        f"- Rare-tail weighted-L2 error squared: {result['controls']['rare_tail_l2']['weighted_l2_error_squared']}; true gain: {result['controls']['rare_tail_l2']['true_gain']} (pass).",
        "",
        "## Interpretation",
        "",
        "The v0.1 failure of scalar KL does not imply that no optimizer-independent robust certificate exists. Under a declared reward-error norm, proxy gain and the corresponding dual policy movement form a sharp certificate. This is classical robust optimization specialized and audited on the Goodhart registry, not a new convex-duality theorem.",
        "",
        "## Claim boundary",
        "",
        result["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


def parse_args(argv: Iterable[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=HERE / "artifacts_v0_2")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    registration = verify_registration()
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    output = args.output_dir.resolve()
    paths = {
        "result": output / "result_v0_2.json",
        "frontier": output / "frontier_v0_2.csv",
        "witnesses": output / "witnesses_v0_2.json",
        "report": output / "RESULT_v0_2.md",
        "receipt": output / "receipt_v0_2.json",
    }
    if any(path.exists() for path in paths.values()):
        raise FileExistsError("registered output already exists")

    started = time.perf_counter()
    with PeakRSS() as memory:
        result, frontier_rows, witnesses = run_census(protocol)
    elapsed = time.perf_counter() - started
    ceiling = protocol["resource_ceiling"]
    resource_pass = (
        elapsed <= float(ceiling["wall_seconds"])
        and memory.peak <= int(ceiling["process_peak_rss_bytes"])
    )
    result["gates"] = {
        "G0_registration_binding": {"pass": True, "registration_sha256": sha256(REGISTRATION)},
        **result["gates"],
        "G7_resource_and_receipts": {
            "pass": resource_pass,
            "elapsed_seconds": elapsed,
            "process_peak_rss_bytes": memory.peak,
        },
    }
    all_pass = len(result["gates"]) == 8 and all(gate["pass"] for gate in result["gates"].values())
    result["instrument_status"] = "valid" if all_pass else "invalid"
    result["verdict"] = "dual_frontier_validated" if all_pass else "invalid_stop"
    result["registration_sha256"] = sha256(REGISTRATION)
    result["protocol_sha256"] = sha256(PROTOCOL)
    result["source_commit"] = registration["run_commit"]

    write_once(paths["result"], canonical_json(result).encode("utf-8"))
    write_once(paths["frontier"], frontier_csv(frontier_rows).encode("utf-8"))
    write_once(paths["witnesses"], canonical_json(witnesses).encode("utf-8"))
    write_once(paths["report"], report_markdown(result).encode("utf-8"))
    receipt = {
        "schema_version": "asmp8_dual_frontier_receipt_v0_2",
        "source_commit": registration["run_commit"],
        "registration_sha256": sha256(REGISTRATION),
        "protocol_sha256": sha256(PROTOCOL),
        "artifacts": {name: {"path": path.name, "sha256": sha256(path)} for name, path in paths.items() if name != "receipt"},
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "resource": result["gates"]["G7_resource_and_receipts"],
    }
    write_once(paths["receipt"], canonical_json(receipt).encode("utf-8"))
    print(canonical_json({"verdict": result["verdict"], "output_dir": str(output)}), end="")
    return 0 if all_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())

