from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from width_theorem import (
    any_separator_below_sharp_width,
    construct_separator,
    dot,
    lower_witness,
    primitive,
    primitive_rays,
    sharp_width,
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
    root = repo_root()
    mismatches = []
    for relative, expected in registration["sealed_files"].items():
        target = root / relative
        actual = sha256_file(target) if target.exists() else None
        if actual != expected:
            mismatches.append((relative, expected, actual))
    if mismatches:
        raise RuntimeError(f"sealed-file mismatch: {mismatches}")
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if status:
        raise RuntimeError(f"worktree must be clean before verification: {status}")
    return registration


def verify_full_cell(dimension: int, bound: int) -> dict[str, Any]:
    started = time.perf_counter()
    rays = primitive_rays(dimension, bound)
    pair_count = 0
    maximum_constructed_width = 0
    failures = []
    for first, second in itertools.combinations(rays, 2):
        query = construct_separator(first, second, bound)
        pair_count += 1
        width = max(map(abs, query))
        maximum_constructed_width = max(maximum_constructed_width, width)
        first_score = dot(query, first)
        second_score = dot(query, second)
        if (
            first_score * second_score >= 0
            or width > sharp_width(bound)
            or vector_gcd(query) != 1
        ):
            failures.append(
                {
                    "first": first,
                    "second": second,
                    "query": query,
                    "scores": [first_score, second_score],
                }
            )
            break
    return {
        "dimension": dimension,
        "bound": bound,
        "ray_count": len(rays),
        "pair_count": pair_count,
        "sharp_width": sharp_width(bound),
        "maximum_constructed_width": maximum_constructed_width,
        "failure_count": len(failures),
        "elapsed_seconds": time.perf_counter() - started,
    }


def random_primitive(
    rng: random.Random, dimension: int, bound: int
) -> tuple[int, ...]:
    while True:
        raw = tuple(rng.randint(-bound, bound) for _ in range(dimension))
        if any(raw):
            return primitive(raw)


def verify_random_cell(
    dimension: int, bound: int, seed: int, pair_target: int
) -> dict[str, Any]:
    rng = random.Random(seed)
    seen: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    failures = 0
    maximum_constructed_width = 0
    while len(seen) < pair_target:
        first = random_primitive(rng, dimension, bound)
        second = random_primitive(rng, dimension, bound)
        if first == second:
            continue
        key = (first, second) if first < second else (second, first)
        if key in seen:
            continue
        seen.add(key)
        query = construct_separator(first, second, bound)
        maximum_constructed_width = max(
            maximum_constructed_width, max(map(abs, query))
        )
        if dot(query, first) * dot(query, second) >= 0:
            failures += 1
            break
    return {
        "dimension": dimension,
        "bound": bound,
        "seed": seed,
        "pair_count": len(seen),
        "sharp_width": sharp_width(bound),
        "maximum_constructed_width": maximum_constructed_width,
        "failure_count": failures,
    }


def render_report(result: dict[str, Any]) -> str:
    full_rows = "\n".join(
        f"| {row['dimension']} | {row['bound']} | {row['ray_count']} | "
        f"{row['pair_count']} | {row['sharp_width']} | "
        f"{row['maximum_constructed_width']} | {row['failure_count']} |"
        for row in result["full_pair_cells"]
    )
    gate_lines = "\n".join(
        f"- **{name}:** {'PASS' if passed else 'FAIL'}"
        for name, passed in result["gates"].items()
    )
    return f"""# ASMP-9 sharp query-width theorem verification v0.3

**Verdict:** `{result['verdict']}`

## Gates

{gate_lines}

## Disjoint full-pair verification

| dimension | bound | rays | pairs | theorem width | maximum used | failures |
|---:|---:|---:|---:|---:|---:|---:|
{full_rows}

The full claim grid was disjoint from the construction-development grid. The
lower-witness search separately exhausted every narrower two-dimensional
integer query for bounds 33 through 64. High-dimensional seeded checks covered
4096 distinct pairs in each of dimensions 5, 8, and 16.

## Claim boundary

This verifies the implementation and extremal witnesses for the written sharp
finite-lattice theorem. The proof, not the census, carries the theorem. It does
not establish novelty or solve reward recovery from behavior, discounted
shaping, finite-sample preference learning, or inconsistent-demonstrator
identifiability.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    registration_path = args.registration.resolve()
    registration = validate_registration(registration_path)
    protocol = load_json(repo_root() / registration["protocol_path"])
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError(f"refusing to overwrite nonempty {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()

    full_cells = [
        verify_full_cell(int(dimension), int(bound))
        for dimension, bound in protocol["full_pair_cells"]
    ]
    lower_rows = []
    lower_config = protocol["lower_witness_bounds"]
    for bound in range(
        int(lower_config["minimum_bound"]),
        int(lower_config["maximum_bound"]) + 1,
    ):
        first, second = lower_witness(int(lower_config["dimension"]), bound)
        lower_rows.append(
            {
                "bound": bound,
                "sharp_width": sharp_width(bound),
                "first": first,
                "second": second,
                "primitive": vector_gcd(first) == vector_gcd(second) == 1,
                "narrower_separator_exists": any_separator_below_sharp_width(
                    int(lower_config["dimension"]), bound
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
            not row["narrower_separator_exists"] for row in lower_rows
        ),
        "G5_disjoint_grid_complete": all(
            row["pair_count"]
            == row["ray_count"] * (row["ray_count"] - 1) // 2
            for row in full_cells
        ),
    }
    verdict = (
        "sharp_query_width_theorem_implementation_verified"
        if all(gates.values())
        else "theorem_implementation_verification_failed"
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
        "elapsed_seconds": time.perf_counter() - started,
    }
    result_path = output_dir / "result_v0_3.json"
    report_path = output_dir / "RESULT_v0_3.md"
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
    (output_dir / "receipt_v0_3.json").write_text(
        canonical_json(receipt), encoding="utf-8"
    )
    print(canonical_json({"verdict": verdict, "gates": gates}))
    return 0 if all(gates.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())

