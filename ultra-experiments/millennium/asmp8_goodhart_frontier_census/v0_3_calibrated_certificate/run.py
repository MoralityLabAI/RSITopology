"""Registered CPU runner for ASMP-8 v0.3a."""

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

from calibration import canonical_json, rows_csv, run_experiment


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
PROTOCOL = HERE / "protocol_v0_3.json"
REGISTRATION = HERE / "registration_v0_3.json"


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
        raise FileNotFoundError("registration_v0_3.json must be committed before execution")
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    if registration.get("schema_version") != "asmp8_calibrated_certificate_registration_v0_3":
        raise ValueError("unexpected registration schema")
    for relative, expected in registration["source_hashes"].items():
        path = REPO_ROOT / relative
        if sha256(path) != expected:
            raise RuntimeError(f"registration hash mismatch: {relative}")
        if git("status", "--porcelain", "--", relative).stdout.strip():
            raise RuntimeError(f"registered source is dirty: {relative}")
    registration_relative = str(REGISTRATION.relative_to(REPO_ROOT))
    if git("status", "--porcelain", "--", registration_relative).stdout.strip():
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
    gates = result["gates"]
    lines = [
        "# ASMP-8 v0.3a registered calibrated-certificate result",
        "",
        f"**Verdict:** `{result['verdict']}`",
        "",
        "## Result",
        "",
        f"The run evaluated {result['policy_count']} proxy-only policies from "
        f"{result['policy_family_count']} optimizer families against three hidden "
        f"reward-error populations. Each of the nine calibration conditions used "
        f"{result['replicates_per_condition']:,} target-blind audit replicates.",
        "",
        f"- Maximum one-sided 95% binomial upper bound on simultaneous radius failure: "
        f"{gates['G1_calibration_coverage']['maximum_cp_upper']:.6f}.",
        f"- False-safe registered certificates conditional on valid radii: "
        f"{gates['G2_certificate_soundness']['conditional_false_safe_count']}.",
        f"- Diffuse-error, m=512 registered non-vacuity: "
        f"{gates['G3_nonvacuity']['registered_fraction']:.3%}.",
        f"- Corresponding Pinsker non-vacuity: "
        f"{gates['G4_stronger_than_pinsker']['pinsker_fraction']:.3%}.",
        f"- Proxy-only rare-tail false-safe cells: "
        f"{gates['G6_rare_tail_liveness']['proxy_only_false_safe_cells']:,}.",
        f"- RMSE-only rare-tail false-safe cells: "
        f"{gates['G6_rare_tail_liveness']['rmse_only_false_safe_cells']:,}.",
        "",
        "## Calibration conditions",
        "",
        "| error family | m | radius failures | CP upper | registered coverage |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in conditions:
        lines.append(
            f"| {row['error_family']} | {row['sample_size']} | "
            f"{row['simultaneous_radius_failures']}/{row['replicates']} | "
            f"{row['failure_rate_cp_upper_95']:.6f} | "
            f"{row['mean_registered_coverage']:.3%} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The v0.2 dual bound remains mechanically sound after replacing a known "
            "error radius with target-blind audit bounds. The primary operational "
            "question is non-vacuity: a valid certificate is useful only where its "
            "lower bound clears zero. The rare-tail arm tests the complementary "
            "failure mode in which scalar proxy accuracy looks adequate while "
            "optimization concentrates on the bad tail.",
            "",
            "## Claim boundary",
            "",
            result["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def risk_svg(risk_rows: list[dict[str, Any]]) -> bytes:
    aggregated: dict[tuple[str, int, float], list[tuple[float, float]]] = {}
    for row in risk_rows:
        key = (row["error_family"], row["sample_size"], row["threshold"])
        aggregated.setdefault(key, []).append((row["coverage"], row["false_safe_rate"]))
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), constrained_layout=True)
    families = [
        "diffuse_low_error",
        "heteroskedastic_proxy_coupled",
        "rare_top_tail",
    ]
    colors = {32: "#9ecae1", 128: "#4292c6", 512: "#084594"}
    for axis, family in zip(axes, families):
        for sample_size in (32, 128, 512):
            points = []
            for key, values in aggregated.items():
                if key[0] == family and key[1] == sample_size:
                    points.append(
                        (
                            key[2],
                            float(sum(value[0] for value in values) / len(values)),
                            float(sum(value[1] for value in values) / len(values)),
                        )
                    )
            points.sort()
            axis.plot(
                [point[1] for point in points],
                [point[2] for point in points],
                marker="o",
                color=colors[sample_size],
                label=f"m={sample_size}",
            )
        axis.set_title(family.replace("_", " "))
        axis.set_xlabel("coverage")
        axis.set_ylabel("false-safe rate")
        axis.grid(alpha=0.25)
    axes[0].legend(frameon=False)
    fig.suptitle("ASMP-8 v0.3a registered risk–coverage curves")
    stream = __import__("io").BytesIO()
    fig.savefig(stream, format="svg", metadata={"Date": None})
    plt.close(fig)
    return stream.getvalue()


def parse_args(argv: Iterable[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=HERE / "artifacts_v0_3")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    registration = verify_registration()
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    output = args.output_dir.resolve()
    paths = {
        "result": output / "result_v0_3.json",
        "conditions": output / "condition_summary_v0_3.csv",
        "policies": output / "policy_summary_v0_3.csv",
        "risks": output / "risk_coverage_v0_3.csv",
        "figure": output / "risk_coverage_v0_3.svg",
        "report": output / "RESULT_v0_3.md",
        "receipt": output / "receipt_v0_3.json",
    }
    if any(path.exists() for path in paths.values()):
        raise FileExistsError("registered output already exists")

    started = time.perf_counter()
    with PeakRSS() as memory:
        result, conditions, policy_rows, risk_rows = run_experiment(protocol)
    elapsed = time.perf_counter() - started
    ceiling = protocol["resource_ceiling"]
    resource_pass = (
        elapsed <= float(ceiling["wall_seconds"])
        and memory.peak <= int(ceiling["process_peak_rss_bytes"])
    )
    result["gates"] = {
        "G0_registration_binding": {
            "pass": True,
            "registration_sha256": sha256(REGISTRATION),
        },
        **result["gates"],
        "G8_resources_and_receipts": {
            "pass": resource_pass,
            "elapsed_seconds": elapsed,
            "process_peak_rss_bytes": memory.peak,
        },
    }
    all_pass = len(result["gates"]) == 9 and all(gate["pass"] for gate in result["gates"].values())
    essential = ("G0_registration_binding", "G1_calibration_coverage", "G2_certificate_soundness",
                 "G6_rare_tail_liveness", "G7_sample_size_ordering", "G8_resources_and_receipts")
    essential_pass = all(result["gates"][key]["pass"] for key in essential)
    if all_pass:
        verdict = "calibrated_certificate_validated_nonvacuous"
    elif essential_pass:
        verdict = "calibrated_certificate_valid_but_vacuous"
    elif result["gates"]["G0_registration_binding"]["pass"] and result["gates"]["G8_resources_and_receipts"]["pass"]:
        verdict = "not_established"
    else:
        verdict = "invalid_stop"
    result.update(
        {
            "instrument_status": "valid" if essential_pass else "not_established",
            "verdict": verdict,
            "registration_sha256": sha256(REGISTRATION),
            "protocol_sha256": sha256(PROTOCOL),
            "source_commit": registration["run_commit"],
        }
    )

    condition_fields = [
        "error_family", "sample_size", "replicates", "seed", "actual_l1", "actual_l2",
        "simultaneous_radius_failures", "failure_rate", "failure_rate_cp_upper_95",
        "mean_registered_coverage",
    ]
    policy_fields = [
        "error_family", "sample_size", "policy_id", "optimizer_family", "proxy_gain",
        "true_gain", "movement_l1", "movement_l2", "movement_linf", "kl_pi_p0",
        "registered_certified_fraction", "registered_false_safe_count",
        "conditional_false_safe_count", "pinsker_certified_fraction",
        "rmse_only_certified_fraction", "proxy_only_certified_fraction",
        "rmse_only_false_safe_count", "proxy_only_false_safe_count",
    ]
    risk_fields = [
        "error_family", "sample_size", "policy_id", "threshold", "coverage", "false_safe_rate"
    ]
    write_once(paths["result"], canonical_json(result).encode("utf-8"))
    write_once(paths["conditions"], rows_csv(conditions, condition_fields).encode("utf-8"))
    write_once(paths["policies"], rows_csv(policy_rows, policy_fields).encode("utf-8"))
    write_once(paths["risks"], rows_csv(risk_rows, risk_fields).encode("utf-8"))
    write_once(paths["figure"], risk_svg(risk_rows))
    write_once(paths["report"], report_markdown(result, conditions).encode("utf-8"))
    receipt = {
        "schema_version": "asmp8_calibrated_certificate_receipt_v0_3",
        "source_commit": registration["run_commit"],
        "registration_sha256": sha256(REGISTRATION),
        "protocol_sha256": sha256(PROTOCOL),
        "artifacts": {
            name: {"path": path.name, "sha256": sha256(path)}
            for name, path in paths.items()
            if name != "receipt"
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "resource": result["gates"]["G8_resources_and_receipts"],
    }
    write_once(paths["receipt"], canonical_json(receipt).encode("utf-8"))
    print(canonical_json({"verdict": verdict, "output_dir": str(output)}), end="")
    return 0 if essential_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
