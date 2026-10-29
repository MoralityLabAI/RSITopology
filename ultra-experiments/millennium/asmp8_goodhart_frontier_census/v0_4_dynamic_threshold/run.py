"""Registered runner for the ASMP-8 v0.4 dynamic audit threshold."""

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

from dynamic_threshold import canonical_json, rows_csv, run_dynamic


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
PROTOCOL = HERE / "protocol_v0_4.json"
REGISTRATION = HERE / "registration_v0_4.json"


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
        raise FileNotFoundError("registration_v0_4.json must be committed before execution")
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    if registration.get("schema_version") != "asmp8_dynamic_threshold_registration_v0_4":
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
        "# ASMP-8 v0.4 dynamic audit-threshold result",
        "",
        f"**Verdict:** `{result['verdict']}`",
        "",
        "## Correction",
        "",
        "This run does not ask whether 50% of replicates certify. It reports the "
        "first registered audit checkpoint at which each nested stream's monotone "
        "robust margin becomes positive.",
        "",
        "## Instrument",
        "",
        f"- Nested streams per error family: {result['streams_per_error_family']:,}.",
        f"- Checkpoint range: {result['checkpoints'][0]:,} to {result['checkpoints'][-1]:,} audits.",
        f"- Conditional false crossings: {result['gates']['G3_conditional_soundness']['conditional_false_crossings']}.",
        f"- Margin monotonicity violations: {result['gates']['G2_monotone_dynamics']['violations']}.",
        f"- Post-crossing reversions: {result['gates']['G6_no_reversion']['reversions']}.",
        "",
        "## Diffuse-error top-spike path",
        "",
        "| policy | oracle margin | predicted checkpoint | min | q25 | median | q75 | max | censored |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in focus:
        predicted = row["predicted_crossing_checkpoint"]
        lines.append(
            f"| {row['policy_id']} | {row['oracle_margin']:.6f} | "
            f"{predicted if predicted is not None else 'none'} | "
            f"{row['minimum'] if row['minimum'] is not None else 'none'} | "
            f"{row['q25'] if row['q25'] is not None else 'none'} | "
            f"{row['median'] if row['median'] is not None else 'none'} | "
            f"{row['q75'] if row['q75'] is not None else 'none'} | "
            f"{row['maximum'] if row['maximum'] is not None else 'none'} | "
            f"{row['censored_streams']} |"
        )
    lines.extend(
        [
            "",
            "Crossing fractions and quantiles are descriptive outputs, not decision thresholds.",
            "",
            "## Simultaneous instrument",
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
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            result["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def threshold_svg(cdf_rows: list[dict[str, Any]]) -> bytes:
    rows = [
        row
        for row in cdf_rows
        if row["error_family"] == "diffuse_low_error"
        and row["optimizer_family"] == "top_spike"
    ]
    fig, axis = plt.subplots(figsize=(7.4, 4.4), constrained_layout=True)
    for policy_id in sorted({row["policy_id"] for row in rows}):
        values = [row for row in rows if row["policy_id"] == policy_id]
        values.sort(key=lambda row: row["checkpoint"])
        axis.plot(
            [row["checkpoint"] for row in values],
            [row["crossing_fraction_descriptive"] for row in values],
            marker="o",
            markersize=3,
            label=policy_id.split("=")[-1],
        )
    axis.set_xscale("log", base=2)
    axis.set_ylim(-0.02, 1.02)
    axis.set_xlabel("nested audit count")
    axis.set_ylabel("descriptive fraction crossed")
    axis.set_title("Diffuse top-spike certificate hitting-time CDF")
    axis.grid(alpha=0.25)
    axis.legend(title="alpha", frameon=False, ncol=3)
    stream = __import__("io").BytesIO()
    fig.savefig(stream, format="svg", metadata={"Date": None})
    plt.close(fig)
    return stream.getvalue()


CONDITION_FIELDS = [
    "error_family", "streams", "seed", "actual_l1", "actual_l2",
    "instrument_failure_streams", "failure_rate", "failure_cp_upper_95",
]
POLICY_FIELDS = [
    "error_family", "policy_id", "optimizer_family", "proxy_gain", "true_gain",
    "oracle_margin", "oracle_class", "predicted_crossing_checkpoint",
    "crossed_streams", "censored_streams", "crossing_fraction_descriptive",
    "minimum", "q25", "median", "q75", "maximum", "cap",
]
CDF_FIELDS = [
    "error_family", "policy_id", "optimizer_family", "checkpoint",
    "crossing_fraction_descriptive", "mean_margin",
]


def parse_args(argv: Iterable[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=HERE / "artifacts_v0_4")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    registration = verify_registration()
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    output = args.output_dir.resolve()
    paths = {
        "result": output / "result_v0_4.json",
        "conditions": output / "condition_summary_v0_4.csv",
        "policies": output / "policy_thresholds_v0_4.csv",
        "cdf": output / "crossing_cdf_v0_4.csv",
        "figure": output / "top_spike_threshold_v0_4.svg",
        "report": output / "RESULT_v0_4.md",
        "receipt": output / "receipt_v0_4.json",
    }
    if any(path.exists() for path in paths.values()):
        raise FileExistsError("registered output already exists")
    started = time.perf_counter()
    with PeakRSS() as memory:
        result, conditions, policies, cdf = run_dynamic(protocol)
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
    core_without_liveness = all(
        result["gates"][key]["pass"]
        for key in (
            "G0_registration_binding", "G1_simultaneous_instrument", "G2_monotone_dynamics",
            "G3_conditional_soundness", "G4_oracle_consistency", "G6_no_reversion",
            "G7_resources_and_receipts",
        )
    )
    verdict = (
        "dynamic_threshold_measured"
        if all_pass
        else "threshold_censored"
        if core_without_liveness
        else "not_established"
    )
    result.update(
        {
            "instrument_status": "valid" if core_without_liveness else "not_established",
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
    write_once(paths["figure"], threshold_svg(cdf))
    write_once(paths["report"], report_markdown(result, conditions).encode("utf-8"))
    receipt = {
        "schema_version": "asmp8_dynamic_threshold_receipt_v0_4",
        "source_commit": registration["run_commit"],
        "registration_sha256": sha256(REGISTRATION),
        "protocol_sha256": sha256(PROTOCOL),
        "artifacts": {
            name: {"path": path.name, "sha256": sha256(path)}
            for name, path in paths.items()
            if name != "receipt"
        },
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "resource": result["gates"]["G7_resources_and_receipts"],
    }
    write_once(paths["receipt"], canonical_json(receipt).encode("utf-8"))
    print(canonical_json({"verdict": verdict, "output_dir": str(output)}), end="")
    return 0 if core_without_liveness else 2


if __name__ == "__main__":
    raise SystemExit(main())
