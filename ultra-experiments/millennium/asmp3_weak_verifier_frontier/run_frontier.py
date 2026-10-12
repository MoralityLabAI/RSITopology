from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from frontier import RHO_GRID, QUERY_GRID, compute_rows, evaluate_gates, family_grid


HERE = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_registration(registration: dict[str, object]) -> None:
    expected = registration["sealed_files"]
    for relative, expected_hash in expected.items():
        actual = sha256_file(HERE / relative)
        if actual != expected_hash:
            raise RuntimeError(f"sealed hash mismatch for {relative}: {actual} != {expected_hash}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, default=HERE / "registration_v0_1.json")
    parser.add_argument("--output-dir", type=Path, default=HERE / "artifacts_v0_1")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    registration = json.loads(args.registration.read_text(encoding="utf-8"))
    validate_registration(registration)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.output_dir / "result.json"
    receipt_path = args.output_dir / "receipt.json"
    if (result_path.exists() or receipt_path.exists()) and not args.force:
        raise RuntimeError("output exists; use --force for an explicit replay")

    rows = compute_rows()
    gates = evaluate_gates(rows)
    all_pass = all(record["pass"] for record in gates.values())

    frontiers: list[dict[str, object]] = []
    for q in QUERY_GRID:
        for families in family_grid(q):
            cells = [r for r in rows if r["q"] == q and r["families"] == families]
            passing = [r for r in cells if r["admissible"]]
            frontiers.append(
                {
                    "q": q,
                    "families": families,
                    "max_passing_rho_on_grid": passing[-1]["rho"] if passing else None,
                    "first_failing_rho_on_grid": next(
                        (r["rho"] for r in cells if not r["admissible"]), None
                    ),
                }
            )

    result = {
        "experiment_id": registration["experiment_id"],
        "verdict": (
            "exact_finite_correlation_diversity_frontier_established"
            if all_pass
            else "registered_gate_failure"
        ),
        "evidence_class": "exact_finite_rational",
        "gates": gates,
        "frontiers": frontiers,
        "rows": rows,
        "claim_boundary": (
            "Exact only for the registered symmetric beta-binomial semantic-bit game. "
            "No claim about real judges, refutation search, superhuman work, or ASMP-3 resolution."
        ),
    }
    write_json(result_path, result)

    receipt = {
        "experiment_id": registration["experiment_id"],
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "registration_sha256": sha256_file(args.registration),
        "result_sha256": sha256_file(result_path),
        "sealed_files": registration["sealed_files"],
        "python": "stdlib-only exact Fraction arithmetic",
    }
    write_json(receipt_path, receipt)
    print(json.dumps({"verdict": result["verdict"], "gates": gates}, indent=2))


if __name__ == "__main__":
    main()

