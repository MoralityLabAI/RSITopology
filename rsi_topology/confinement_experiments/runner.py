"""Resumable runner for confinement-width CPU work units."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from .common import (
    WorkUnit,
    canonical_json_bytes,
    checksum_manifest,
    content_sha256,
    environment_receipt,
    implementation_fingerprint,
    load_config,
    write_bytes_compare_or_fail,
    write_csv_compare_or_fail,
    write_json_compare_or_fail,
)
from .suite import (
    aggregate_metrics,
    evaluate_registered_gates,
    evaluate_work_unit,
    generate_work_units,
    markdown_report,
    render_figure,
)


def _unit_receipt(unit: WorkUnit) -> dict[str, Any]:
    result = evaluate_work_unit(unit)
    return {
        "schema_version": "confinement-work-unit-v1",
        "experiment": unit.experiment,
        "unit_id": unit.unit_id,
        "scientific_identity": unit.scientific_identity,
        "payload": unit.payload,
        "seed": unit.seed,
        "implementation_sha256": unit.implementation_sha256,
        "result": result,
    }


def _load_or_evaluate(unit: WorkUnit, directory: Path) -> dict[str, Any]:
    path = directory / f"{unit.unit_id}.json"
    if path.exists():
        import json

        receipt = json.loads(path.read_text(encoding="utf-8"))
        expected = {
            "experiment": unit.experiment,
            "unit_id": unit.unit_id,
            "scientific_identity": unit.scientific_identity,
            "payload": unit.payload,
            "seed": unit.seed,
            "implementation_sha256": unit.implementation_sha256,
        }
        actual = {key: receipt.get(key) for key in expected}
        if canonical_json_bytes(actual) != canonical_json_bytes(expected):
            raise ValueError(f"work-unit receipt conflicts with frozen unit: {path}")
        return receipt
    receipt = _unit_receipt(unit)
    write_json_compare_or_fail(path, receipt)
    return receipt


def run_config(
    config_path: str | Path,
    *,
    output_root: str | Path = "artifacts/confinement",
    workers: int = 1,
) -> dict[str, Any]:
    config_path = Path(config_path)
    config = load_config(config_path)
    if workers < 1:
        raise ValueError("workers must be positive")
    experiment = str(config["experiment"])
    run_id = str(config["run_id"])
    run_dir = Path(output_root) / experiment / run_id
    units_dir = run_dir / "work_units"
    units_dir.mkdir(parents=True, exist_ok=True)
    config_hash = content_sha256(config)
    write_json_compare_or_fail(run_dir / "config.json", config)
    write_json_compare_or_fail(run_dir / "environment.json", environment_receipt())
    units = generate_work_units(config)
    expected_names = {f"{unit.unit_id}.json" for unit in units}
    stale_names = {
        path.name for path in units_dir.glob("*.json") if path.name not in expected_names
    }
    if stale_names:
        raise ValueError(
            "work-unit directory contains receipts from another implementation: "
            + ", ".join(sorted(stale_names)[:5])
        )
    if workers == 1:
        receipts = [_load_or_evaluate(unit, units_dir) for unit in units]
    else:
        existing: list[dict[str, Any]] = []
        missing: list[WorkUnit] = []
        for unit in units:
            path = units_dir / f"{unit.unit_id}.json"
            if path.exists():
                existing.append(_load_or_evaluate(unit, units_dir))
            else:
                missing.append(unit)
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(_unit_receipt, unit): unit for unit in missing}
            evaluated = []
            for future in as_completed(futures):
                receipt = future.result()
                write_json_compare_or_fail(
                    units_dir / f"{receipt['unit_id']}.json", receipt
                )
                evaluated.append(receipt)
        by_id = {receipt["unit_id"]: receipt for receipt in existing + evaluated}
        receipts = [by_id[unit.unit_id] for unit in units]
    rows = [receipt["result"] for receipt in receipts]
    metrics = aggregate_metrics(experiment, rows)
    gates = evaluate_registered_gates(experiment, rows, metrics)
    metrics["registered_gates"] = gates
    metrics["all_registered_gates_pass"] = all(gates.values())
    write_csv_compare_or_fail(run_dir / "aggregate.csv", rows)
    write_json_compare_or_fail(run_dir / "aggregate.json", rows)
    write_json_compare_or_fail(run_dir / "metrics.json", metrics)
    render_figure(experiment, rows, run_dir / "figure.png")
    report = markdown_report(experiment, run_id, rows, metrics).encode("utf-8")
    write_bytes_compare_or_fail(run_dir / "REPORT.md", report)
    artifact_paths = [
        path
        for path in run_dir.rglob("*")
        if path.is_file() and path.name not in {"checksums.json", "run_receipt.json"}
    ]
    checksums = checksum_manifest(artifact_paths, relative_to=run_dir)
    write_json_compare_or_fail(run_dir / "checksums.json", checksums)
    run_receipt = {
        "schema_version": "confinement-run-receipt-v1",
        "experiment": experiment,
        "run_id": run_id,
        "config_sha256": config_hash,
        "implementation_sha256": implementation_fingerprint(),
        "work_unit_count": len(units),
        "metrics": metrics,
        "checksums_sha256": content_sha256(checksums),
    }
    write_json_compare_or_fail(run_dir / "run_receipt.json", run_receipt)
    return {"run_dir": str(run_dir), **run_receipt}
