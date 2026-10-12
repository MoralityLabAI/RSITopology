"""Receipt-preserving adapter for the ASMP-9 v0.35 measurement pilot."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
import time
from typing import Any, Callable, Mapping


HERE = Path(__file__).resolve().parent
PHYSICAL = HERE.parent / "physical_acquisition_v0_34"
if str(PHYSICAL) not in sys.path:
    sys.path.insert(0, str(PHYSICAL))

import run_burned_pilot as sealed_runner  # noqa: E402


SEALED_REQUEST_RECORD: Callable[..., dict[str, Any]] = (
    sealed_runner.request_record
)
REGISTRATION_SCHEMA = "asmp9_measurement_channel_registration_v0_35"
MANIFEST_SCHEMA = "asmp9_measurement_channel_prompt_manifest_v0_35"
RECORD_SCHEMA = "asmp9_measurement_channel_record_v0_35"
PLAN_SCHEMA = "asmp9_measurement_channel_plan_v0_35"
SUMMARY_SCHEMA = "asmp9_measurement_channel_capture_summary_v0_35"
QUERY_TYPES = (
    "standard_gamble",
    "compound_gamble",
    "anchor_dominance_control",
    "probability_order_control",
    "semantic_equality_control",
    "code_mapping_control",
)


def selected_rows(
    manifest: Mapping[str, Any],
    execution_class: str,
    smoke_rows_per_type: int,
) -> list[dict[str, Any]]:
    if (
        manifest.get("status") != "registered_not_run"
        or manifest.get("execution_authorized") is not True
    ):
        raise RuntimeError(
            "model execution requires a registered, authorized v0.35 manifest"
        )
    rows = [
        dict(row)
        for row in manifest["rows"]
        if row["phase"] == "burned_measurement_pilot"
    ]
    if len(rows) != 2412:
        raise ValueError("v0.35 prompt universe changed")
    observed_types = {str(row["query_type"]) for row in rows}
    if observed_types != set(QUERY_TYPES):
        raise ValueError("v0.35 query-type universe changed")
    if execution_class == "measurement_pilot":
        return rows
    if execution_class != "smoke" or smoke_rows_per_type <= 0:
        raise ValueError("invalid execution class or smoke row count")
    output: list[dict[str, Any]] = []
    for query_type in QUERY_TYPES:
        candidates = [
            row for row in rows if row["query_type"] == query_type
        ]
        output.extend(candidates[:smoke_rows_per_type])
    return output


def request_record(
    *,
    base_url: str,
    item: Mapping[str, Any],
    row: Mapping[str, Any],
    server_session: int,
    request_timeout: float,
    seed_base: int,
) -> dict[str, Any]:
    compatibility_row = {
        **row,
        "choice_order": row["presentation_order"],
    }
    record = SEALED_REQUEST_RECORD(
        base_url=base_url,
        item=item,
        row=compatibility_row,
        server_session=server_session,
        request_timeout=request_timeout,
        seed_base=seed_base,
    )
    record["schema_version"] = RECORD_SCHEMA
    for field in (
        "content_id",
        "presentation_order",
        "code_mapping",
        "lower_probability",
        "upper_probability",
        "dominance_relation",
    ):
        if field in row:
            record[field] = row[field]
    record["record_sha256"] = sealed_runner.sha256_bytes(
        sealed_runner.canonical_bytes(
            {
                key: value
                for key, value in record.items()
                if key != "record_sha256"
            }
        )
    )
    return record


def summarize(
    records_dir: Path,
    plan: Mapping[str, Any],
    registration_path: Path,
    progress: Mapping[str, Any],
) -> dict[str, Any]:
    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(records_dir.glob("*.json"))
    ]
    by_row: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record.get("schema_version") != RECORD_SCHEMA:
            raise ValueError("unexpected v0.35 record schema")
        by_row[str(record["row_id"])].append(record)
    probability_delta = 0.0
    log_odds_delta = 0.0
    for row_records in by_row.values():
        if len(row_records) != 2:
            raise ValueError("each row requires two cold starts")
        first, second = row_records
        probability_delta = max(
            probability_delta,
            max(
                abs(
                    float(first["choice_probabilities"][label])
                    - float(second["choice_probabilities"][label])
                )
                for label in ("A", "B")
            ),
        )
        log_odds_delta = max(
            log_odds_delta,
            abs(
                float(first["target_log_odds"])
                - float(second["target_log_odds"])
            ),
        )
    expected_records = int(plan["item_count"])
    if len(records) != expected_records:
        raise ValueError("capture is incomplete")
    return {
        "schema_version": SUMMARY_SCHEMA,
        "status": (
            "measurement_pilot_capture_completed"
            if plan["execution_class"] == "measurement_pilot"
            else "measurement_smoke_capture_completed"
        ),
        "execution_class": plan["execution_class"],
        "counts": {
            "records": len(records),
            "unique_prompts": len(by_row),
            "planned_epochs": int(plan["epoch_count"]),
            "server_sessions": int(progress["server_session_count"]),
            "query_types": {
                query_type: sum(
                    record["query_type"] == query_type for record in records
                )
                for query_type in QUERY_TYPES
            },
        },
        "reliability": {
            "maximum_choice_probability_delta_across_cold_starts": (
                probability_delta
            ),
            "maximum_target_log_odds_delta_across_cold_starts": (
                log_odds_delta
            ),
            "all_choice_vectors_complete": all(
                set(record["choice_probabilities"]) == {"A", "B"}
                for record in records
            ),
        },
        "inputs": {
            "registration_sha256": sealed_runner.sha256_file(
                registration_path
            ),
            "registration_content_sha256": progress[
                "registration_content_sha256"
            ],
            "plan_sha256": plan["plan_sha256"],
            "runner_adapter_sha256": sealed_runner.sha256_file(
                Path(__file__).resolve()
            ),
            "sealed_runner_sha256": sealed_runner.sha256_file(
                Path(sealed_runner.__file__).resolve()
            ),
        },
        "thermal": {
            "maximum_runner_observed_temperature_c": float(
                progress["maximum_runner_observed_temperature_c"]
            ),
            "pause_count": int(progress["thermal_pause_count"]),
            "pause_seconds": float(progress["thermal_pause_seconds"]),
        },
        "claim_boundary": (
            "Burned measurement-pilot data only. This capture can validate or "
            "reject one semantic-choice channel; it cannot confirm mixture "
            "affinity or the decision quotient and cannot resolve ASMP-9."
        ),
        "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def configure_adapter() -> None:
    sealed_runner.REGISTRATION_SCHEMA = REGISTRATION_SCHEMA
    sealed_runner.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    sealed_runner.RECORD_SCHEMA = RECORD_SCHEMA
    sealed_runner.PLAN_SCHEMA = PLAN_SCHEMA
    sealed_runner.SUMMARY_SCHEMA = SUMMARY_SCHEMA
    sealed_runner.selected_rows = selected_rows
    sealed_runner.request_record = request_record
    sealed_runner.summarize = summarize


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--execution-class",
        choices=("smoke", "measurement_pilot"),
        required=True,
    )
    parser.add_argument("--smoke-rows-per-type", type=int, default=2)
    return parser.parse_args()


def main() -> None:
    configure_adapter()
    sealed_runner.run(parse_args())


if __name__ == "__main__":
    main()
