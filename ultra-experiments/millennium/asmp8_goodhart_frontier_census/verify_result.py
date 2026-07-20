"""Independent artifact and headline verifier for the ASMP-8 finite census."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.artifact_dir.resolve()
    receipt = json.loads((root / "receipt_v0_1.json").read_text(encoding="utf-8"))
    result = json.loads((root / "result_v0_1.json").read_text(encoding="utf-8"))
    for name, record in receipt["outputs"].items():
        target = root / name
        assert target.is_file(), name
        assert sha256(target) == record["sha256"], name
        assert target.stat().st_size == record["bytes"], name
    assert receipt["verdict"] == result["verdict"]
    assert result["census"]["reward_vector_count"] == 15620
    assert result["gates"]["G1_numerical_calibration"]["pass"]
    assert result["gates"]["G2_supnorm_positive_control"]["pass"]
    assert result["gates"]["G3_reference_l2_negative_control"]["pass"]
    assert result["gates"]["G6_complete_census"]["pass"]
    g4 = result["gates"]["G4_optimizer_independence_falsification"]
    if g4["pass"]:
        witness = g4["strongest_witness"]
        assert witness["gibbs_gain"] * witness["top_spike_gain"] < 0
        assert witness["gain_difference"] >= 0.20
    print("ASMP-8 artifact verification passed")
    print(f"verdict={result['verdict']} outputs={len(receipt['outputs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
