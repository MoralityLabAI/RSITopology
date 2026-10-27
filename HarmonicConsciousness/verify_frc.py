"""Reproducible, source-stamped synthetic FRC/harmonic result receipt."""
from __future__ import annotations

from hashlib import sha256
import argparse
import json
from pathlib import Path

from HarmonicConsciousness.frc_calibration import verify_synthetic

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "HarmonicConsciousness/frc_calibration.py",
    "HarmonicConsciousness/verify_frc.py",
    "HarmonicConsciousness/FRC_CALIBRATION.md",
    "HarmonicConsciousness/protocol_v0_2.json",
    "tests/test_harmonic_frc.py",
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    report = verify_synthetic()
    report["source_sha256"] = {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES}
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
