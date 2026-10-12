from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).parents[1]
RUNNER_PATH = ROOT / "scripts" / "run_qwen08_stratified_audits.py"
ANALYZER_PATH = ROOT / "scripts" / "analyze_qwen08_stratified_audits.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = load_module("run_qwen08_stratified_audits", RUNNER_PATH)
ANALYZER = load_module("analyze_qwen08_stratified_audits", ANALYZER_PATH)


def synthetic_manifest() -> dict:
    applications = [f"app_{index}" for index in range(9)]
    rows = []
    manifest_index = 0
    for application in applications:
        for within_pair in range(32):
            for half in ("validation", "construction"):
                prompt = f"{application}/{half}/{within_pair}"
                rows.append(
                    {
                        "application": application,
                        "geometry_half": half,
                        "prompt": prompt,
                        "prompt_sha256": f"prompt-hash-{manifest_index:03d}",
                        "row_id": f"row-{manifest_index:03d}",
                    }
                )
                manifest_index += 1
    return {
        "schema_version": "synthetic",
        "manifest_semantic_sha256": "synthetic-manifest",
        "applications": applications,
        "rows": rows,
    }


def synthetic_records(manifest: dict, plan: dict) -> list[dict]:
    row_index = {
        str(row["row_id"]): index for index, row in enumerate(manifest["rows"])
    }
    records = []
    for item in plan["items"]:
        index = row_index[str(item["row_id"])]
        probability = 0.5 + index / 10_000.0
        record = {
            "schema_version": RUNNER.RECORD_SCHEMA,
            **item,
            "server_session": int(item["planned_epoch"]),
            "content": f"token-{index}",
            "tokens": [index],
            "probability": probability,
            "stop": True,
            "latency_seconds": 0.01,
        }
        record["record_sha256"] = RUNNER.sha256_bytes(
            RUNNER.canonical_bytes(
                {key: value for key, value in record.items() if key != "record_sha256"}
            )
        )
        records.append(record)
    return records


def test_interleaving_covers_every_stratum_before_repeating() -> None:
    manifest = synthetic_manifest()
    rows = RUNNER.interleaved_rows(manifest)
    first_round = rows[:18]
    observed = {
        (row["application"], row["geometry_half"]) for row in first_round
    }
    expected = {
        (application, half)
        for application in manifest["applications"]
        for half in ("construction", "validation")
    }
    assert observed == expected
    assert {row["within_stratum_index"] for row in first_round} == {0}
    assert len({row["row_id"] for row in rows}) == 576


def test_plan_has_full_crossover_and_frozen_repeat_panel() -> None:
    plan = RUNNER.build_plan(synthetic_manifest(), stability_repeats=32)
    assert plan["item_count"] == 3456
    census = [
        item for item in plan["items"] if item["phase"] == "census_crossover"
    ]
    repeats = [
        item for item in plan["items"] if item["phase"] == "repeat_cached"
    ]
    assert len(census) == 2304
    assert len(repeats) == 1152
    assert len({item["row_id"] for item in repeats}) == 18
    assert {item["planned_epoch"] for item in plan["items"]} == {0, 1, 2, 3}


def test_synthetic_measurement_passes_all_gates() -> None:
    manifest = synthetic_manifest()
    plan = RUNNER.build_plan(manifest, stability_repeats=32)
    result = ANALYZER.analyze(
        manifest=manifest,
        plan=plan,
        records=synthetic_records(manifest, plan),
        probability_tolerance=1e-6,
        liveness_variance_floor=1e-8,
    )
    assert result["status"] == "measurement_instrument_pass"
    assert result["record_count"] == 3456
    assert result["unique_prompt_count"] == 576
    assert all(gate["status"] == "pass" for gate in result["gates"].values())


def test_cache_dependent_token_is_detected() -> None:
    manifest = synthetic_manifest()
    plan = RUNNER.build_plan(manifest, stability_repeats=32)
    records = synthetic_records(manifest, plan)
    records[1] = {**records[1], "content": "cache-dependent-token"}
    result = ANALYZER.analyze(
        manifest=manifest,
        plan=plan,
        records=records,
        probability_tolerance=1e-6,
        liveness_variance_floor=1e-8,
    )
    assert (
        result["gates"]["C0_full_census_and_cache_order_invariance"]["status"]
        == "fail"
    )
    assert result["status"] == "measurement_instrument_not_established"


def test_unplanned_restart_is_not_silently_accepted() -> None:
    manifest = synthetic_manifest()
    plan = RUNNER.build_plan(manifest, stability_repeats=32)
    records = synthetic_records(manifest, plan)
    records[100] = {**records[100], "server_session": 99}
    result = ANALYZER.analyze(
        manifest=manifest,
        plan=plan,
        records=records,
        probability_tolerance=1e-6,
        liveness_variance_floor=1e-8,
    )
    assert result["gates"]["P0_plan_and_session_integrity"]["status"] == "fail"
