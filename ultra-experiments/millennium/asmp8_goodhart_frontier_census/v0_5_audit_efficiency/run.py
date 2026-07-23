"""Registered runner for ASMP-8 v0.5."""

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

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import psutil

from efficiency import canonical_json, rows_csv, run_efficiency
from schemas import CDF_FIELDS, CONDITION_FIELDS, POLICY_FIELDS


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
PROTOCOL = HERE / "protocol_v0_5.json"
REGISTRATION = HERE / "registration_v0_5.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, check=check, capture_output=True, text=True)


def write_once(path: Path, payload: bytes) -> None:
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def verify_registration() -> dict[str, Any]:
    if not REGISTRATION.is_file():
        raise FileNotFoundError("registration_v0_5.json must be committed before execution")
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    if registration.get("schema_version") != "asmp8_audit_efficiency_registration_v0_5":
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


def report_markdown(result: dict[str, Any], conditions: list[dict[str, Any]]) -> str:
    focus = result["focus"]["diffuse_top_spike"]
    lines = [
        "# ASMP-8 v0.5 audit-efficiency result",
        "",
        f"**Verdict:** `{result['verdict']}`",
        "",
        "## Diffuse top-spike first-passage costs",
        "",
        "| policy | partial census | empirical Bernstein min | median | max | Hoeffding min | full census |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in focus:
        lines.append(
            f"| {row['policy_id']} | {row['movement_partial_census']} | "
            f"{row['empirical_bernstein_minimum']} | {row['empirical_bernstein_median']} | "
            f"{row['empirical_bernstein_maximum']} | {row['hoeffding_minimum']} | "
            f"{row['full_census']} |"
        )
    lines.extend(
        [
            "",
            "The partial census is policy-specific and deterministic. Empirical Bernstein and "
            "Hoeffding are shared error-norm calibrators. Full census is an exact finite-universe reference.",
            "",
            "## Soundness",
            "",
            f"- Conditional false crossings: {result['gates']['G2_conditional_soundness']['false_crossings']}.",
            f"- Monotonicity violations: {result['gates']['G3_monotone_dynamics']['monotone_violations']}.",
            f"- Reversions: {result['gates']['G3_monotone_dynamics']['reversions']}.",
            f"- Partial-census endpoint mismatches: {result['gates']['G4_partial_census_exactness']['exactness_failures']}.",
            "",
            "## Empirical-Bernstein instrument",
            "",
            "| error family | invalid streams | CP upper |",
            "|---|---:|---:|",
        ]
    )
    for row in conditions:
        lines.append(
            f"| {row['error_family']} | {row['instrument_failure_streams']}/{row['streams']} | "
            f"{row['failure_cp_upper_95']:.6f} |"
        )
    lines.extend(["", "## Claim boundary", "", result["claim_boundary"], ""])
    return "\n".join(lines)


def efficiency_svg(rows: list[dict[str, Any]]) -> bytes:
    focus = [
        row for row in rows
        if row["error_family"] == "diffuse_low_error" and row["optimizer_family"] == "top_spike"
    ]
    labels = [row["policy_id"].split("=")[-1] for row in focus]
    methods = [
        ("partial census", [row["movement_partial_census"] for row in focus], "#31a354"),
        ("empirical Bernstein", [row["empirical_bernstein_median"] for row in focus], "#3182bd"),
        ("Hoeffding", [row["hoeffding_median"] for row in focus], "#de2d26"),
    ]
    fig, axis = plt.subplots(figsize=(7.6, 4.5), constrained_layout=True)
    width = 0.24
    x = list(range(len(labels)))
    for offset, (name, values, color) in zip((-width, 0, width), methods):
        axis.bar([value + offset for value in x], values, width=width, label=name, color=color)
    axis.set_yscale("log", base=2)
    axis.set_xticks(x, labels)
    axis.set_xlabel("top-spike alpha")
    axis.set_ylabel("audits to first positive certificate")
    axis.set_title("Matched ASMP-8 audit-efficiency frontier")
    axis.grid(axis="y", alpha=0.25)
    axis.legend(frameon=False)
    stream = __import__("io").BytesIO()
    fig.savefig(stream, format="svg", metadata={"Date": None})
    plt.close(fig)
    return stream.getvalue()


def parse_args(argv: Iterable[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=HERE / "artifacts_v0_5")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    registration = verify_registration()
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    output = args.output_dir.resolve()
    paths = {
        "result": output / "result_v0_5.json",
        "conditions": output / "condition_summary_v0_5.csv",
        "policies": output / "policy_efficiency_v0_5.csv",
        "cdf": output / "empirical_bernstein_cdf_v0_5.csv",
        "figure": output / "audit_efficiency_v0_5.svg",
        "report": output / "RESULT_v0_5.md",
        "receipt": output / "receipt_v0_5.json",
    }
    if any(path.exists() for path in paths.values()):
        raise FileExistsError("registered output already exists")
    started = time.perf_counter()
    with PeakRSS() as memory:
        result, conditions, policies, cdf = run_efficiency(protocol)
    elapsed = time.perf_counter() - started
    ceiling = protocol["resource_ceiling"]
    resource_pass = elapsed <= float(ceiling["wall_seconds"]) and memory.peak <= int(
        ceiling["process_peak_rss_bytes"]
    )
    result["gates"] = {
        "G0_registration_binding": {"pass": True, "registration_sha256": sha256(REGISTRATION)},
        **result["gates"],
        "G7_resources_and_receipts": {
            "pass": resource_pass,
            "elapsed_seconds": elapsed,
            "process_peak_rss_bytes": memory.peak,
        },
    }
    all_pass = len(result["gates"]) == 8 and all(gate["pass"] for gate in result["gates"].values())
    core = all(
        result["gates"][key]["pass"]
        for key in (
            "G0_registration_binding", "G1_empirical_bernstein_instrument",
            "G2_conditional_soundness", "G3_monotone_dynamics",
            "G4_partial_census_exactness", "G6_complete_threshold_reporting",
            "G7_resources_and_receipts",
        )
    )
    verdict = "efficiency_frontier_measured" if all_pass else "ordering_not_established" if core else "not_established"
    result.update(
        {
            "instrument_status": "valid" if core else "not_established",
            "verdict": verdict,
            "registration_sha256": sha256(REGISTRATION),
            "protocol_sha256": sha256(PROTOCOL),
            "source_commit": registration["run_commit"],
        }
    )
    write_once(paths["result"], canonical_json(result).encode("utf-8"))
    write_once(paths["conditions"], rows_csv(conditions, CONDITION_FIELDS).encode("utf-8"))
    write_once(paths["policies"], rows_csv(policies, POLICY_FIELDS).encode("utf-8"))
    write_once(paths["cdf"], rows_csv(cdf, CDF_FIELDS).encode("utf-8"))
    write_once(paths["figure"], efficiency_svg(policies))
    write_once(paths["report"], report_markdown(result, conditions).encode("utf-8"))
    receipt = {
        "schema_version": "asmp8_audit_efficiency_receipt_v0_5",
        "source_commit": registration["run_commit"],
        "registration_sha256": sha256(REGISTRATION),
        "protocol_sha256": sha256(PROTOCOL),
        "artifacts": {
            name: {"path": path.name, "sha256": sha256(path)}
            for name, path in paths.items() if name != "receipt"
        },
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "resource": result["gates"]["G7_resources_and_receipts"],
    }
    write_once(paths["receipt"], canonical_json(receipt).encode("utf-8"))
    print(canonical_json({"verdict": verdict, "output_dir": str(output)}), end="")
    return 0 if core else 2


if __name__ == "__main__":
    raise SystemExit(main())
