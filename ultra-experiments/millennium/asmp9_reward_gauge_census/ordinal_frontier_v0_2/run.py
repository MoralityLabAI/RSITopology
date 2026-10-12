from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ordinal_frontier import (
    build_coverage,
    collision_witness,
    parse_fraction,
    sha256_file,
    solve_minimum_query_cover,
    vector_text,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def repo_root() -> Path:
    for parent in [SCRIPT_DIR, *SCRIPT_DIR.parents]:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("repository root not found")


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_registration(registration_path: Path) -> dict[str, Any]:
    registration = load_json(registration_path)
    root = repo_root()
    errors = []
    for relative, expected in registration["sealed_files"].items():
        path = root / relative
        actual = sha256_file(path) if path.exists() else None
        if actual != expected:
            errors.append(
                {"path": relative, "expected": expected, "actual": actual}
            )
    if errors:
        raise RuntimeError(f"registration mismatch: {errors}")
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if status:
        raise RuntimeError(f"worktree must be clean before reveal: {status}")
    return registration


def compute_experiment(
    protocol: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, bool], str]:
    cells: list[dict[str, Any]] = []
    thresholds: list[dict[str, Any]] = []
    solver_records: list[dict[str, Any]] = []

    widths = [int(value) for value in protocol["query_widths"]]
    deltas = [parse_fraction(value) for value in protocol["misspecification_deltas"]]
    time_limit = float(protocol["solver"]["time_limit_seconds_per_cell"])

    coverage_by_key = {}
    for dimension, reward_bound in protocol["dimensions_and_bounds"]:
        for delta in deltas:
            for query_width in widths:
                coverage = build_coverage(
                    int(dimension),
                    int(reward_bound),
                    query_width,
                    delta,
                )
                key = (int(dimension), int(reward_bound), str(delta), query_width)
                coverage_by_key[key] = coverage
                witness = collision_witness(coverage)
                cells.append(
                    {
                        "dimension": int(dimension),
                        "reward_bound": int(reward_bound),
                        "delta": str(delta),
                        "query_width": query_width,
                        "candidate_count": len(coverage.candidates),
                        "query_count": len(coverage.queries),
                        "pair_count": len(coverage.pairs),
                        "unresolved_pair_count": len(
                            coverage.unresolved_pair_indices
                        ),
                        "complete": coverage.complete,
                        "first_collision_left": (
                            vector_text(witness["left"]) if witness else ""
                        ),
                        "first_collision_right": (
                            vector_text(witness["right"]) if witness else ""
                        ),
                    }
                )

            complete_widths = [
                width
                for width in widths
                if coverage_by_key[
                    (int(dimension), int(reward_bound), str(delta), width)
                ].complete
            ]
            threshold = min(complete_widths) if complete_widths else None
            set_cover = None
            selected_queries: list[str] = []
            if threshold is not None:
                threshold_coverage = coverage_by_key[
                    (int(dimension), int(reward_bound), str(delta), threshold)
                ]
                set_cover = solve_minimum_query_cover(
                    threshold_coverage,
                    time_limit_seconds=time_limit,
                )
                selected_queries = [
                    vector_text(threshold_coverage.queries[index])
                    for index in set_cover.selected_query_indices
                ]
                solver_records.append(
                    {
                        "dimension": int(dimension),
                        "reward_bound": int(reward_bound),
                        "delta": str(delta),
                        "query_width_threshold": threshold,
                        "status": set_cover.status,
                        "objective": set_cover.objective,
                        "dual_bound": set_cover.dual_bound,
                        "mip_gap": set_cover.mip_gap,
                        "independently_covers_all": (
                            set_cover.independently_covers_all
                        ),
                    }
                )
            thresholds.append(
                {
                    "dimension": int(dimension),
                    "reward_bound": int(reward_bound),
                    "delta": str(delta),
                    "query_width_threshold": threshold,
                    "minimum_query_count": (
                        set_cover.objective if set_cover else None
                    ),
                    "solver_status": (
                        set_cover.status if set_cover else "not_separable_within_cap"
                    ),
                    "selected_queries": selected_queries,
                }
            )

    cell_lookup = {
        (
            row["dimension"],
            row["reward_bound"],
            row["delta"],
            row["query_width"],
        ): row
        for row in cells
    }
    threshold_lookup = {
        (row["dimension"], row["reward_bound"], row["delta"]): row
        for row in thresholds
    }

    h1 = all(
        cell_lookup[(dimension, 1, "0", 1)]["complete"]
        and threshold_lookup[(dimension, 1, "0")]["query_width_threshold"] == 1
        and threshold_lookup[(dimension, 1, "0")]["minimum_query_count"]
        == dimension
        for dimension in (1, 2, 3)
    )
    h2 = any(
        dimension >= 2
        and not cell_lookup[(dimension, bound, "1/2", 1)]["complete"]
        and threshold_lookup[(dimension, bound, "1/2")][
            "query_width_threshold"
        ]
        is not None
        for dimension, bound in protocol["dimensions_and_bounds"]
    )
    h3 = any(
        row["delta"] == "1/2"
        and row["minimum_query_count"] is not None
        and row["minimum_query_count"] > row["dimension"]
        for row in thresholds
    )
    g1 = all(
        row["candidate_count"] > 0
        and row["query_count"] > 0
        and row["pair_count"]
        == row["candidate_count"] * (row["candidate_count"] - 1) // 2
        for row in cells
    )
    g4 = all(
        row["status"] == "optimal"
        and row["objective"] is not None
        and abs(float(row["objective"]) - float(row["dual_bound"])) <= 1e-8
        and abs(float(row["mip_gap"])) <= 1e-12
        and row["independently_covers_all"]
        for row in solver_records
    )
    g5_width = True
    g5_delta = True
    for dimension, bound in protocol["dimensions_and_bounds"]:
        for delta in ("0", "1/2"):
            unresolved = [
                cell_lookup[(dimension, bound, delta, width)][
                    "unresolved_pair_count"
                ]
                for width in widths
            ]
            g5_width = g5_width and all(
                later <= earlier
                for earlier, later in zip(unresolved, unresolved[1:])
            )
        for width in widths:
            g5_delta = g5_delta and (
                cell_lookup[(dimension, bound, "1/2", width)][
                    "unresolved_pair_count"
                ]
                >= cell_lookup[(dimension, bound, "0", width)][
                    "unresolved_pair_count"
                ]
            )
    g7 = all(
        (
            row["complete"]
            and row["unresolved_pair_count"] == 0
            and not row["first_collision_left"]
        )
        or (
            not row["complete"]
            and row["unresolved_pair_count"] > 0
            and bool(row["first_collision_left"])
        )
        for row in cells
    )
    gates = {
        "G0_registration_binding": True,
        "G1_complete_enumeration": g1,
        "G2_exact_anchor": h1,
        "G3_robust_frontier_liveness": h2,
        "G4_solver_validity": g4,
        "G5_monotonicity": g5_width and g5_delta,
        "G6_robust_access_penalty": h3,
        "G7_witness_integrity": g7,
    }
    if not all(gates.values()):
        if not all(
            gates[name]
            for name in (
                "G0_registration_binding",
                "G1_complete_enumeration",
                "G4_solver_validity",
                "G5_monotonicity",
                "G7_witness_integrity",
            )
        ):
            verdict = "invalid_instrument"
        elif not gates["G2_exact_anchor"]:
            verdict = "exact_anchor_failed"
        elif not gates["G3_robust_frontier_liveness"]:
            verdict = "robust_width_transition_not_established"
        else:
            verdict = "robust_query_penalty_not_established"
    else:
        verdict = "finite_ordinal_reward_ray_access_frontier_established"
    return cells, thresholds, gates, verdict


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            serializable = {
                key: (
                    json.dumps(value, separators=(",", ":"))
                    if isinstance(value, list)
                    else value
                )
                for key, value in row.items()
            }
            writer.writerow(serializable)


def render_result(result: dict[str, Any]) -> str:
    threshold_lines = []
    for row in result["thresholds"]:
        threshold_lines.append(
            "| {dimension} | {reward_bound} | `{delta}` | {query_width_threshold} | "
            "{minimum_query_count} | {solver_status} |".format(**row)
        )
    gates = "\n".join(
        f"- **{name}:** {'PASS' if passed else 'FAIL'}"
        for name, passed in result["gates"].items()
    )
    return f"""# ASMP-9 ordinal reward-ray access frontier v0.2

**Verdict:** `{result['verdict']}`

## Gates

{gates}

## Query-width and query-count frontier

| dimension | reward bound | delta | first complete width | minimum queries | solver |
|---:|---:|---:|---:|---:|---|
{os.linesep.join(threshold_lines)}

## Interpretation

The `delta=0` arm is the exact-sign anchor: ternary coordinate comparisons
retain equality information. The `delta=1/2` arm treats a comparison whose
score lies inside a half-unit threshold band as adversarially ambiguous. The
registered width sweep therefore distinguishes a shortage of query count from
a query grammar that cannot robustly place two reward rays on opposite sides
of any admitted comparison hyperplane.

Every reward coordinate is a primitive cycle-return vector modulo positive
scale. Opposite vectors remain distinct. Every query is a primitive difference
between two nonnegative trajectory bundles.

## Claim boundary

This is a finite, nonadaptive, population-oracle comparison census after the
potential-shaping quotient has already been constructed. It is not a theorem
about arbitrary rewards, human preferences, policy observations, adaptive
query complexity, finite-sample learning, or discounted MDPs. The
misspecification arm is one frozen adversarial threshold model. Solver
optimality is backed by HiGHS status, zero reported MIP gap, matching dual
bound, and independent cover replay; it is not a formal proof certificate.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    registration_path = args.registration.resolve()
    registration = validate_registration(registration_path)
    protocol_path = repo_root() / registration["protocol_path"]
    protocol = load_json(protocol_path)
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError(f"refusing to overwrite nonempty {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    cells, thresholds, gates, verdict = compute_experiment(protocol)
    elapsed = time.perf_counter() - started
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
        "thresholds": thresholds,
        "cell_count": len(cells),
        "elapsed_seconds": elapsed,
    }

    cell_path = output_dir / "frontier_cells_v0_2.csv"
    threshold_path = output_dir / "thresholds_v0_2.csv"
    result_path = output_dir / "result_v0_2.json"
    report_path = output_dir / "RESULT_v0_2.md"
    write_csv(cell_path, cells)
    write_csv(threshold_path, thresholds)
    result_path.write_text(canonical_json(result), encoding="utf-8")
    report_path.write_text(render_result(result), encoding="utf-8")

    receipt = {
        "protocol_id": protocol["protocol_id"],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "registration_sha256": sha256_file(registration_path),
        "registration_commit": current_commit,
        "implementation_commit": registration["implementation_commit"],
        "sealed_files": registration["sealed_files"],
        "outputs": {
            path.name: sha256_file(path)
            for path in (cell_path, threshold_path, result_path, report_path)
        },
        "python": sys.version,
        "scipy": __import__("scipy").__version__,
        "elapsed_seconds": elapsed,
    }
    (output_dir / "receipt_v0_2.json").write_text(
        canonical_json(receipt), encoding="utf-8"
    )
    print(canonical_json({"verdict": verdict, "gates": gates, "elapsed": elapsed}))
    return 0 if all(gates.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())

