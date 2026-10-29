from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
V03 = HERE.parent / "width_theorem_v0_3"
sys.path.insert(0, str(V03))

from run_verification import (  # noqa: E402
    canonical_json,
    load_json,
    repo_root,
    sha256_file,
    validate_registration,
    verify_full_cell,
    verify_random_cell,
)
from width_theorem import (  # noqa: E402
    any_separator_below_sharp_width,
    dot,
    lower_witness,
    sharp_width,
    vector_gcd,
)


def possible_signs(score: int, delta: Fraction) -> set[int]:
    low = Fraction(score) - delta
    high = Fraction(score) + delta
    values = set()
    if low < 0:
        values.add(-1)
    if low <= 0 <= high:
        values.add(0)
    if high > 0:
        values.add(1)
    return values


def endpoint_control(bound: int) -> dict[str, object]:
    first, second = lower_witness(2, bound)
    query = (0, 1) if bound == 1 else (bound - 2, -(bound - 1))
    scores = (dot(query, first), dot(query, second))
    exact_separates = possible_signs(
        scores[0], Fraction(0)
    ).isdisjoint(possible_signs(scores[1], Fraction(0)))
    positive_separates = possible_signs(
        scores[0], Fraction(1, 2)
    ).isdisjoint(possible_signs(scores[1], Fraction(1, 2)))
    return {
        "bound": bound,
        "query": query,
        "scores": scores,
        "query_width": max(map(abs, query)),
        "sharp_positive_delta_width": sharp_width(bound),
        "exact_delta_zero_separates": exact_separates,
        "positive_delta_half_separates": positive_separates,
    }


def render_report(result: dict[str, object]) -> str:
    gates = "\n".join(
        f"- **{name}:** {'PASS' if passed else 'FAIL'}"
        for name, passed in result["gates"].items()
    )
    rows = "\n".join(
        f"| {row['dimension']} | {row['bound']} | {row['ray_count']} | "
        f"{row['pair_count']} | {row['sharp_width']} | "
        f"{row['maximum_constructed_width']} | {row['failure_count']} |"
        for row in result["full_pair_cells"]
    )
    return f"""# Corrected ASMP-9 sharp-width verification v0.3.1

**Verdict:** `{result['verdict']}`

## Gates

{gates}

## Fresh full-pair cells

| dimension | bound | rays | pairs | theorem width | maximum used | failures |
|---:|---:|---:|---:|---:|---:|---:|
{rows}

The corrected theorem applies only to `0<delta<1`. Endpoint controls confirm
that a narrower tie-producing query separates the lower witness at `delta=0`
but ceases to separate it at `delta=1/2`.

## Claim boundary

This verifies the implementation and fresh witnesses for the corrected
finite-lattice theorem. The written proof carries the theorem. It neither
establishes novelty nor resolves the behavioral, discounted, finite-sample, or
inconsistent-demonstrator parts of ASMP-9.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    registration_path = args.registration.resolve()
    registration = validate_registration(registration_path)
    protocol = load_json(repo_root() / registration["protocol_path"])
    if protocol["delta_domain"] != "0 < delta < 1":
        raise RuntimeError("corrected protocol must exclude delta=0")
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError(f"refusing to overwrite nonempty {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()

    full_cells = [
        verify_full_cell(int(dimension), int(bound))
        for dimension, bound in protocol["full_pair_cells"]
    ]
    lower_config = protocol["lower_witness_bounds"]
    lower_rows = []
    for bound in range(
        int(lower_config["minimum_bound"]),
        int(lower_config["maximum_bound"]) + 1,
    ):
        first, second = lower_witness(int(lower_config["dimension"]), bound)
        lower_rows.append(
            {
                "bound": bound,
                "primitive": vector_gcd(first) == vector_gcd(second) == 1,
                "narrower_strict_separator_exists": (
                    any_separator_below_sharp_width(
                        int(lower_config["dimension"]), bound
                    )
                ),
            }
        )
    random_rows = [
        verify_random_cell(
            int(dimension),
            int(bound),
            int(seed),
            int(protocol["random_pairs_per_cell"]),
        )
        for dimension, bound, seed in protocol["random_cells"]
    ]
    endpoint_rows = [
        endpoint_control(int(bound))
        for bound in protocol["endpoint_control_bounds"]
    ]
    gates = {
        "G0_registration_binding": True,
        "G1_strict_opposite_scores": all(
            row["failure_count"] == 0 for row in full_cells + random_rows
        ),
        "G2_constructed_width_bound": all(
            row["maximum_constructed_width"] <= row["sharp_width"]
            for row in full_cells + random_rows
        ),
        "G3_lower_witness_validity": all(
            row["primitive"] for row in lower_rows
        ),
        "G4_lower_witness_sharpness": all(
            not row["narrower_strict_separator_exists"] for row in lower_rows
        ),
        "G5_fresh_grid_complete": all(
            row["pair_count"]
            == row["ray_count"] * (row["ray_count"] - 1) // 2
            for row in full_cells
        ),
        "G6_zero_endpoint_discontinuity": all(
            row["query_width"] < row["sharp_positive_delta_width"]
            and row["exact_delta_zero_separates"]
            and not row["positive_delta_half_separates"]
            for row in endpoint_rows
        ),
    }
    verdict = (
        "corrected_sharp_query_width_theorem_implementation_verified"
        if all(gates.values())
        else "corrected_theorem_verification_failed"
    )
    current_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root(),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    result = {
        "protocol_id": protocol["protocol_id"],
        "registration_sha256": sha256_file(registration_path),
        "registration_commit": current_commit,
        "verdict": verdict,
        "gates": gates,
        "full_pair_cells": full_cells,
        "lower_witness_cells": lower_rows,
        "random_cells": random_rows,
        "endpoint_controls": endpoint_rows,
        "elapsed_seconds": time.perf_counter() - started,
    }
    result_path = output_dir / "result_v0_3_1.json"
    report_path = output_dir / "RESULT_v0_3_1.md"
    result_path.write_text(canonical_json(result), encoding="utf-8")
    report_path.write_text(render_report(result), encoding="utf-8")
    receipt = {
        "protocol_id": protocol["protocol_id"],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "registration_sha256": sha256_file(registration_path),
        "registration_commit": current_commit,
        "implementation_commit": registration["implementation_commit"],
        "output_hashes": {
            result_path.name: sha256_file(result_path),
            report_path.name: sha256_file(report_path),
        },
        "elapsed_seconds": result["elapsed_seconds"],
    }
    (output_dir / "receipt_v0_3_1.json").write_text(
        canonical_json(receipt), encoding="utf-8"
    )
    print(canonical_json({"verdict": verdict, "gates": gates}))
    return 0 if all(gates.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())

