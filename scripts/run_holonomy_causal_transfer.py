#!/usr/bin/env python
"""Execute and seal the CPU-synthetic holonomy causal-transfer protocol."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys
import time
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import scipy
import sklearn

from rsi_topology.holonomy_causal import evaluate_causal_transfer


def _hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")


def _write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to overwrite different artifact: {path}")
        return
    path.write_bytes(payload)


def _environment() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "scikit_learn": sklearn.__version__,
        "execution": "CPU-only; no model weights, CUDA, training, or mutation",
    }


def _markdown(summary: dict[str, Any], manifest_hash: str) -> str:
    metrics = summary["metrics"]
    prediction = summary["prediction"]
    null = summary["permuted_holonomy_prediction"]
    gates = "\n".join(
        f"- `{name}`: **{'pass' if passed else 'fail'}**"
        for name, passed in summary["gates"].items()
    )
    return f"""# Holonomy causal path-transfer falsification v0.1

## Outcome

Registered decision: **`{summary['decision']}`**. All gates pass:
`{str(summary['all_gates_pass']).lower()}`.

The canonical CPU fixture transports one rank-four signed coordinate to the
same target by two paths. One direct-sum block is either flat or curved while a
second block remains flat, providing exposed and low-exposure directions in one
bundle. The downstream map is `tanh(Jz)`, so its registered Lipschitz bound is
known exactly within the edit space.

## Primary results

- Rows: `{metrics['row_count']}` across `{metrics['loop_count']}` loops.
- Maximum two-path/loop identity error:
  `{metrics['maximum_path_identity_error']:.3e}`.
- Maximum causal-bound excess: `{metrics['maximum_bound_excess']:.3e}`.
- Maximum flat displacement: `{metrics['maximum_flat_displacement']:.3e}`.
- Maximum curved exposed displacement:
  `{metrics['maximum_curved_exposed_displacement']:.6f}`.
- Maximum curved exposed response disagreement:
  `{metrics['maximum_curved_exposed_response_disagreement']:.6f}`.
- Bound-authorized coverage: `{metrics['authorization_coverage']:.3%}` with
  `{metrics['false_authorization_count']}` false authorizations.
- Grouped held-out relative SSE reduction from the frozen holonomy features:
  `{prediction['relative_sse_reduction']:.6f}`, grouped-bootstrap 90% interval
  `[{prediction['grouped_bootstrap_90_interval'][0]:.6f},
  {prediction['grouped_bootstrap_90_interval'][1]:.6f}]`.
- Seeded permuted-holonomy relative SSE reduction:
  `{null['relative_sse_reduction']:.6f}` (descriptive leakage null).

## Gates

{gates}

## Interpretation

This establishes that the proposed measurement and analysis recover a planted
causal path-dependence signal that local lineage and Jacobian visibility do not
fully encode. It also calibrates a conservative signed-control bound. It does
not show that a transformer contains the measured bundle. The real-model entry
condition remains a target-blind, lineage-connected, noise-valid loop universe
with a third untouched causal split.

Manifest SHA-256: `{manifest_hash}`.

## Claim boundary

{summary['claim_boundary']}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path("protocols/holonomy_causal_transfer_falsification_v0_1.json"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/holonomy_causal_transfer_v0_1"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("reports/holonomy_causal_transfer_v0_1.md"),
    )
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if protocol.get("protocol_id") != "holonomy_causal_transfer_falsification_v0_1":
        raise ValueError("unexpected protocol_id")
    if protocol.get("status") != "registered_before_canonical_run":
        raise ValueError("protocol is not frozen for the canonical run")
    population = protocol["canonical_population"]
    started = datetime.now(timezone.utc)
    started_clock = time.perf_counter()
    result = evaluate_causal_transfer(
        step_sizes=tuple(population["step_sizes"]),
        steps_per_side=int(population["steps_per_side"]),
        causal_map_replicates=int(population["causal_map_replicates"]),
        causal_output_dimension=int(population["causal_output_dimension"]),
        edit_norms=tuple(population["edit_norms"]),
        seed=int(population["seed"]),
        bootstrap_draws=int(population["bootstrap_draws"]),
        control_error_budget=float(population["control_error_budget"]),
    )
    ended = datetime.now(timezone.utc)
    duration = time.perf_counter() - started_clock
    rows = result.pop("rows")
    loops = result.pop("loop_receipts")
    result["protocol_sha256"] = _hash(protocol_path)
    result["source_sha256"] = {
        "holonomy_causal.py": _hash(
            Path("rsi_topology/holonomy_causal.py").resolve()
        ),
        "holonomy.py": _hash(Path("rsi_topology/holonomy.py").resolve()),
        "risk_gate.py": _hash(Path("rsi_topology/risk_gate.py").resolve()),
        "runner": _hash(Path(__file__).resolve()),
    }
    result["run"] = {
        "started_utc": started.isoformat(),
        "ended_utc": ended.isoformat(),
        "elapsed_seconds": duration,
        "status": "completed" if result["all_gates_pass"] else "completed_with_gate_failure",
    }
    output_dir = args.output_dir.resolve()
    environment_path = output_dir / "environment_lock.json"
    rows_path = output_dir / "causal_rows.jsonl"
    loops_path = output_dir / "loop_receipts.jsonl"
    summary_path = output_dir / "canonical_summary.json"
    _write_once(environment_path, _canonical_json(_environment()))
    _write_once(
        rows_path,
        b"".join(_canonical_json(row).replace(b"\n", b"") + b"\n" for row in rows),
    )
    _write_once(
        loops_path,
        b"".join(_canonical_json(row).replace(b"\n", b"") + b"\n" for row in loops),
    )
    _write_once(summary_path, _canonical_json(result))
    artifacts = {
        path.name: {"sha256": _hash(path), "bytes": path.stat().st_size}
        for path in (environment_path, rows_path, loops_path, summary_path)
    }
    manifest = {
        "schema_version": "1.0.0",
        "protocol_id": result["protocol_id"],
        "protocol_sha256": result["protocol_sha256"],
        "artifacts": artifacts,
    }
    manifest_path = output_dir / "release_manifest.json"
    _write_once(manifest_path, _canonical_json(manifest))
    manifest_hash = _hash(manifest_path)
    _write_once(args.report.resolve(), _markdown(result, manifest_hash).encode("utf-8"))
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "all_gates_pass": result["all_gates_pass"],
                "summary": str(summary_path),
                "manifest": str(manifest_path),
                "manifest_sha256": manifest_hash,
                "report": str(args.report.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
