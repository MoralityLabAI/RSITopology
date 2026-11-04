from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "balanced_design_v0_16"
REPO = HERE.parents[3]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(HERE))
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

runner_spec = importlib.util.spec_from_file_location(
    "asmp9_balanced_v016_runner_for_v0162",
    BASE / "run_verification.py",
)
if runner_spec is None or runner_spec.loader is None:
    raise ImportError("unable to load v0.16 runner library")
base = importlib.util.module_from_spec(runner_spec)
runner_spec.loader.exec_module(base)

from threshold_search import logarithmic_total_threshold  # noqa: E402


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def build_threshold_records(
    protocol: dict[str, Any],
) -> list[dict[str, Any]]:
    registry = protocol["threshold_registry"]
    records = []
    for length in registry["cycle_lengths"]:
        for epsilon_text in registry["epsilon"]:
            epsilon = base.parse_fraction(epsilon_text)
            for delta_text in registry["delta"]:
                delta = base.parse_fraction(delta_text)
                record = logarithmic_total_threshold(
                    length, epsilon, 1 - delta
                )
                if record is None:
                    raise AssertionError(
                        "positive interior has no finite threshold"
                    )
                record["delta"] = base.fraction_record(delta)
                records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(
            f"refusing to overwrite output directory: {args.output_dir}"
        )

    started = time.perf_counter()
    registration_path = args.registration.resolve()
    registration = json.loads(
        registration_path.read_text(encoding="utf-8")
    )
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    args.output_dir.mkdir(parents=True, exist_ok=False)
    start_path = args.output_dir / "start_v0_16_2.json"
    progress_path = args.output_dir / "progress_v0_16_2.json"
    abort_path = args.output_dir / "abort_v0_16_2.json"
    base.write_json(
        start_path,
        {
            "protocol_id": protocol["protocol_id"],
            "registration_sha256": base.sha256(registration_path),
            "started_at_utc": utc_now(),
            "status": "started",
            "resource_caps": protocol["resource_caps"],
        },
    )

    completed_stages: list[str] = []

    def write_progress(stage: str, status: str = "running") -> None:
        base.write_json(
            progress_path,
            {
                "protocol_id": protocol["protocol_id"],
                "status": status,
                "stage": stage,
                "completed_stages": completed_stages,
                "elapsed_seconds": time.perf_counter() - started,
                "peak_resident_bytes": base.peak_resident_bytes(),
            },
        )

    def finish_stage(stage: str) -> None:
        completed_stages.append(stage)
        write_progress(stage)
        elapsed = time.perf_counter() - started
        peak = base.peak_resident_bytes()
        caps = protocol["resource_caps"]
        if (
            elapsed > caps["wall_seconds"]
            or peak > caps["peak_resident_bytes"]
        ):
            raise RuntimeError(
                f"resource cap exceeded after stage {stage}: "
                f"elapsed={elapsed}, peak={peak}"
            )

    try:
        write_progress("registration_binding")
        registration_commit, binding = base.validate_registration(
            registration_path, registration
        )
        finish_stage("registration_binding")

        pairs = base.build_pair_records(protocol)
        finish_stage("pair_registry")

        global_records = base.build_global_records(protocol)
        finish_stage("global_allocation_registry")

        compact = base.build_compact_records(protocol)
        finish_stage("compact_value_registry")

        thresholds = build_threshold_records(protocol)
        finish_stage("threshold_registry")

        boundaries = base.build_boundary_records(protocol)
        finish_stage("negative_boundaries")

        elapsed = time.perf_counter() - started
        peak = base.peak_resident_bytes()
        gates = base.evaluate_gates(
            protocol=protocol,
            binding=binding,
            pairs=pairs,
            global_records=global_records,
            compact=compact,
            thresholds=thresholds,
            boundaries=boundaries,
            elapsed_seconds=elapsed,
            peak_bytes=peak,
        )
        verdict = (
            "registered_exact_result_passed"
            if all(gates.values())
            else "registered_exact_result_failed"
        )
        result = {
            "protocol_id": protocol["protocol_id"],
            "registration_commit": registration_commit,
            "registration_sha256": base.sha256(registration_path),
            "implementation_commit": registration[
                "implementation_commit"
            ],
            "verdict": verdict,
            "gates": gates,
            "binding_checks": binding,
            "pair_records": pairs,
            "global_records": global_records,
            "compact_records": compact,
            "threshold_records": thresholds,
            "boundary_records": boundaries,
            "summary": {
                "pair_cell_count": len(pairs),
                "global_cell_count": len(global_records),
                "compact_cell_count": len(compact),
                "threshold_cell_count": len(thresholds),
                "boundary_cell_count": (
                    len(boundaries["epsilon_zero"])
                    + len(boundaries["k_two"])
                ),
                "threshold_exact_evaluation_count": sum(
                    row["exact_evaluation_count"]
                    for row in thresholds
                ),
                "threshold_maximum_total_trials": max(
                    row["minimum_total_trials"]
                    for row in thresholds
                ),
            },
            "resources": {
                "elapsed_seconds": elapsed,
                "peak_resident_bytes": peak,
                "gpu_used": False,
            },
            "claim_boundary": protocol["claim_boundary"],
            "supersedes_resource_aborts_only": ["v0.16", "v0.16.1"],
        }
        result_path = args.output_dir / "result_v0_16_2.json"
        report_path = args.output_dir / "RESULT_v0_16_2.md"
        base.write_json(result_path, result)
        report = base.render_report(result).replace(
            "v0.16 result", "v0.16.2 result"
        )
        report += (
            "\n## Threshold-search implementation\n\n"
            "The 36 exact thresholds used exponential bracketing plus binary "
            "search, with "
            f"{result['summary']['threshold_exact_evaluation_count']} exact "
            "value evaluations in total. The largest selected total was "
            f"{result['summary']['threshold_maximum_total_trials']}.\n"
        )
        base.write_text(report_path, report)
        finish_stage("result_and_report")
        write_progress("completed", status="completed")

        final_elapsed = time.perf_counter() - started
        final_peak = base.peak_resident_bytes()
        caps = protocol["resource_caps"]
        if (
            final_elapsed > caps["wall_seconds"]
            or final_peak > caps["peak_resident_bytes"]
        ):
            raise RuntimeError(
                "resource cap exceeded before receipt: "
                f"elapsed={final_elapsed}, peak={final_peak}"
            )
        receipt = {
            "protocol_id": protocol["protocol_id"],
            "registration_commit": registration_commit,
            "registration_sha256": base.sha256(registration_path),
            "implementation_commit": registration[
                "implementation_commit"
            ],
            "verdict": verdict,
            "output_hashes": {
                result_path.name: base.sha256(result_path),
                report_path.name: base.sha256(report_path),
                start_path.name: base.sha256(start_path),
                progress_path.name: base.sha256(progress_path),
            },
            "resources": {
                "elapsed_seconds": final_elapsed,
                "peak_resident_bytes": final_peak,
                "gpu_used": False,
            },
        }
        base.write_json(
            args.output_dir / "receipt_v0_16_2.json", receipt
        )
        print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
        raise SystemExit(0 if all(gates.values()) else 1)
    except SystemExit:
        raise
    except BaseException as error:
        base.write_json(
            abort_path,
            {
                "protocol_id": protocol["protocol_id"],
                "status": "aborted",
                "error_type": type(error).__name__,
                "error": str(error),
                "completed_stages": completed_stages,
                "elapsed_seconds": time.perf_counter() - started,
                "peak_resident_bytes": base.peak_resident_bytes(),
            },
        )
        write_progress("aborted", status="aborted")
        raise


if __name__ == "__main__":
    main()
