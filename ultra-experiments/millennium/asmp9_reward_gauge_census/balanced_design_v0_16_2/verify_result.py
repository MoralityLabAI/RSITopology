from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "balanced_design_v0_16"
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

spec = importlib.util.spec_from_file_location(
    "asmp9_balanced_v016_verifier_for_v0162",
    BASE / "verify_result.py",
)
if spec is None or spec.loader is None:
    raise ImportError("unable to load v0.16 independent verifier")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--start", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    verification = base.verify(
        args.registration.resolve(),
        args.result.resolve(),
        args.report.resolve(),
        args.receipt.resolve(),
    )
    result = json.loads(args.result.read_text(encoding="utf-8"))
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    start = json.loads(args.start.read_text(encoding="utf-8"))
    progress = json.loads(args.progress.read_text(encoding="utf-8"))

    threshold_trace_ok = True
    for row in result["threshold_records"]:
        points = row["evaluated_points"]
        parsed = [
            (
                point["total"],
                base.parse(point["value"]["fraction"]),
                point["passes"],
            )
            for point in points
        ]
        exact_values = [
            (
                total,
                base.compact_value(
                    total,
                    row["cycle_length"],
                    base.parse(row["epsilon"]["fraction"]),
                ),
                passes,
            )
            for total, _, passes in parsed
        ]
        target = base.parse(row["target"]["fraction"])
        threshold_trace_ok = threshold_trace_ok and (
            len(points) == row["exact_evaluation_count"]
            and row["exact_evaluation_count"]
            <= row["logarithmic_evaluation_bound"]
            and row["within_evaluation_bound"]
            and row["traversed_values_monotone"]
            and all(
                reported == replayed
                and passes == (replayed >= target)
                for (
                    (_, reported, passes),
                    (_, replayed, _),
                ) in zip(parsed, exact_values, strict=True)
            )
            and all(
                left[1] <= right[1]
                for left, right in zip(
                    exact_values, exact_values[1:], strict=False
                )
            )
        )

    caps = start["resource_caps"]
    extra = {
        "receipt_start_hash": (
            receipt["output_hashes"][args.start.name]
            == base.sha256(args.start)
        ),
        "receipt_progress_hash": (
            receipt["output_hashes"][args.progress.name]
            == base.sha256(args.progress)
        ),
        "start_status": start["status"] == "started",
        "progress_completed": (
            progress["status"] == "completed"
            and progress["stage"] == "completed"
        ),
        "protocol_chain": (
            start["protocol_id"]
            == progress["protocol_id"]
            == receipt["protocol_id"]
        ),
        "full_runner_resource_cap": (
            progress["elapsed_seconds"] <= caps["wall_seconds"]
            and progress["peak_resident_bytes"]
            <= caps["peak_resident_bytes"]
            and receipt["resources"]["elapsed_seconds"]
            <= caps["wall_seconds"]
            and receipt["resources"]["peak_resident_bytes"]
            <= caps["peak_resident_bytes"]
            and receipt["resources"]["gpu_used"] is False
        ),
        "independent_logarithmic_threshold_trace": threshold_trace_ok,
    }
    verification["checks"].update(extra)
    verification["check_count"] = len(verification["checks"])
    verification["failed_checks"] = [
        name
        for name, passed in verification["checks"].items()
        if not passed
    ]
    verification["status"] = (
        "pass" if not verification["failed_checks"] else "fail"
    )

    rendered = json.dumps(verification, indent=2, sort_keys=True) + "\n"
    if args.output:
        if args.output.exists():
            raise FileExistsError(
                f"refusing to overwrite output: {args.output}"
            )
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    raise SystemExit(0 if verification["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
