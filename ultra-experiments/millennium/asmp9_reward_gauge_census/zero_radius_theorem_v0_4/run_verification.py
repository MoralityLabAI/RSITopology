from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from zero_radius_width import (
    construct_exact_separator,
    dot,
    lower_witness,
    narrower_exact_separator_exists,
    primitive,
    primitive_rays,
    sharp_zero_width,
    sign,
    vector_gcd,
)


HERE = Path(__file__).resolve().parent


def repo_root() -> Path:
    for candidate in [HERE, *HERE.parents]:
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_registration(path: Path) -> dict[str, Any]:
    registration = load_json(path)
    mismatches = []
    for relative, expected in registration["sealed_files"].items():
        target = repo_root() / relative
        actual = sha256_file(target) if target.exists() else None
        if actual != expected:
            mismatches.append((relative, expected, actual))
    if mismatches:
        raise RuntimeError(f"sealed-file mismatch: {mismatches}")
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=repo_root(),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if status:
        raise RuntimeError(f"worktree must be clean before run: {status}")
    return registration


def full_cell(dimension: int, bound: int) -> dict[str, Any]:
    started = time.perf_counter()
    rays = primitive_rays(dimension, bound)
    pair_count = 0
    maximum_width = 0
    failures = 0
    for first, second in itertools.combinations(rays, 2):
        query = construct_exact_separator(first, second, bound)
        pair_count += 1
        maximum_width = max(maximum_width, max(map(abs, query)))
        if (
            sign(dot(query, first)) == sign(dot(query, second))
            or max(map(abs, query)) > sharp_zero_width(bound)
            or vector_gcd(query) != 1
        ):
            failures += 1
            break
    return {
        "dimension": dimension,
        "bound": bound,
        "ray_count": len(rays),
        "pair_count": pair_count,
        "theorem_width": sharp_zero_width(bound),
        "maximum_constructed_width": maximum_width,
        "failure_count": failures,
        "elapsed_seconds": time.perf_counter() - started,
    }


def random_primitive(
    rng: random.Random, dimension: int, bound: int
) -> tuple[int, ...]:
    while True:
        raw = tuple(rng.randint(-bound, bound) for _ in range(dimension))
        if any(raw):
            return primitive(raw)


def random_cell(
    dimension: int, bound: int, seed: int, target: int
) -> dict[str, Any]:
    rng = random.Random(seed)
    pairs = set()
    failures = 0
    maximum_width = 0
    while len(pairs) < target:
        first = random_primitive(rng, dimension, bound)
        second = random_primitive(rng, dimension, bound)
        if first == second:
            continue
        key = (first, second) if first < second else (second, first)
        if key in pairs:
            continue
        pairs.add(key)
        query = construct_exact_separator(first, second, bound)
        maximum_width = max(maximum_width, max(map(abs, query)))
        if sign(dot(query, first)) == sign(dot(query, second)):
            failures += 1
            break
    return {
        "dimension": dimension,
        "bound": bound,
        "seed": seed,
        "pair_count": len(pairs),
        "theorem_width": sharp_zero_width(bound),
        "maximum_constructed_width": maximum_width,
        "failure_count": failures,
    }


def render_report(result: dict[str, Any]) -> str:
    gates = "\n".join(
        f"- **{name}:** {'PASS' if passed else 'FAIL'}"
        for name, passed in result["gates"].items()
    )
    rows = "\n".join(
        f"| {row['dimension']} | {row['bound']} | {row['ray_count']} | "
        f"{row['pair_count']} | {row['theorem_width']} | "
        f"{row['maximum_constructed_width']} | {row['failure_count']} |"
        for row in result["full_pair_cells"]
    )
    return f"""# ASMP-9 exact-tie width theorem verification v0.4

**Verdict:** `{result['verdict']}`

## Gates

{gates}

## Fresh full-pair cells

| dimension | bound | rays | pairs | theorem width | maximum used | failures |
|---:|---:|---:|---:|---:|---:|---:|
{rows}

## Interpretation

Exact ties reduce the sharp width from `2B-1` under any positive sub-unit
threshold ambiguity to `B-1` for `B>=3`. The proof is a Farey-sequence
corollary; this run checks the constructor and lower witnesses.

## Claim boundary

This verifies a finite cycle-coordinate theorem. It is not finite-sample
preference learning, behavioral IRL, discounted shaping, or a novelty claim.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    registration_path = args.registration.resolve()
    registration = validate_registration(registration_path)
    protocol = load_json(repo_root() / registration["protocol_path"])
    if protocol["delta"] != "0":
        raise RuntimeError("exact-tie protocol must fix delta=0")
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError(f"refusing to overwrite nonempty {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()

    full_rows = [
        full_cell(int(dimension), int(bound))
        for dimension, bound in protocol["full_pair_cells"]
    ]
    lower = protocol["lower_witness_bounds"]
    lower_rows = []
    for bound in range(
        int(lower["minimum_bound"]), int(lower["maximum_bound"]) + 1
    ):
        first, second = lower_witness(int(lower["dimension"]), bound)
        lower_rows.append(
            {
                "bound": bound,
                "primitive": vector_gcd(first) == vector_gcd(second) == 1,
                "bounded": max(map(abs, first + second)) <= bound,
                "narrower_separator_exists": narrower_exact_separator_exists(
                    int(lower["dimension"]), bound
                ),
            }
        )
    random_rows = [
        random_cell(
            int(dimension),
            int(bound),
            int(seed),
            int(protocol["random_pairs_per_cell"]),
        )
        for dimension, bound, seed in protocol["random_cells"]
    ]
    gates = {
        "G0_registration_binding": True,
        "G1_distinct_exact_signs": all(
            row["failure_count"] == 0 for row in full_rows + random_rows
        ),
        "G2_constructed_width_bound": all(
            row["maximum_constructed_width"] <= row["theorem_width"]
            for row in full_rows + random_rows
        ),
        "G3_lower_witness_validity": all(
            row["primitive"] and row["bounded"] for row in lower_rows
        ),
        "G4_lower_witness_sharpness": all(
            not row["narrower_separator_exists"] for row in lower_rows
        ),
        "G5_fresh_grid_complete": all(
            row["pair_count"]
            == row["ray_count"] * (row["ray_count"] - 1) // 2
            for row in full_rows
        ),
    }
    verdict = (
        "sharp_exact_tie_width_theorem_implementation_verified"
        if all(gates.values())
        else "exact_tie_width_verification_failed"
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
        "full_pair_cells": full_rows,
        "lower_witness_cells": lower_rows,
        "random_cells": random_rows,
        "elapsed_seconds": time.perf_counter() - started,
    }
    result_path = output_dir / "result_v0_4.json"
    report_path = output_dir / "RESULT_v0_4.md"
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
    (output_dir / "receipt_v0_4.json").write_text(
        canonical_json(receipt), encoding="utf-8"
    )
    print(canonical_json({"verdict": verdict, "gates": gates}))
    return 0 if all(gates.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())

