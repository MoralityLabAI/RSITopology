from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "balanced_design_v0_16"

spec = importlib.util.spec_from_file_location(
    "asmp9_balanced_v016_verifier", BASE / "verify_result.py"
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
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    start = json.loads(args.start.read_text(encoding="utf-8"))
    progress = json.loads(args.progress.read_text(encoding="utf-8"))
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
