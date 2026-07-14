"""Report readiness or seal a complete proposal-recursion run registration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.run_preparation_v2 import (
    readiness_report,
    seal_run_pre_anchor,
    write_once_or_equal,
    canonical_json_bytes,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--seal", action="store_true")
    args = parser.parse_args()
    registration_path = args.registration.resolve()
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    report = readiness_report(registration)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_once_or_equal(
        args.out_dir / "readiness_report.json", canonical_json_bytes(report)
    )
    if args.seal:
        seal = seal_run_pre_anchor(
            registration,
            registration_path=registration_path,
            output_dir=args.out_dir.resolve(),
        )
        print(json.dumps(seal, indent=2, sort_keys=True))
    else:
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
