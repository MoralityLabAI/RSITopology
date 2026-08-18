"""Total evaluator for the draft ASMP-9 v0.35 measurement pilot."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import statistics
from typing import Any, Iterable, Mapping

from monotone_ruler import monotone_linf_radius, robust_zero_crossing


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
FACTORIAL_CELLS = {
    ("target_first", "natural"),
    ("target_first", "reverse"),
    ("target_second", "natural"),
    ("target_second", "reverse"),
}
RECORD_SCHEMA = "asmp9_measurement_channel_record_v0_35"
REGISTRATION_SCHEMA = "asmp9_measurement_channel_registration_v0_35"
MANIFEST_SCHEMA = "asmp9_measurement_channel_prompt_manifest_v0_35"
SUMMARY_SCHEMA = "asmp9_measurement_channel_capture_summary_v0_35"


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_registered_path(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (REPO / path).resolve()


def _finite(value: Any) -> float:
    output = float(value)
    if not math.isfinite(output):
        raise ValueError("target_log_odds must be finite")
    return output


def validate_and_join(
    manifest: Mapping[str, Any],
    records: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if manifest.get("schema_version") != (
        "asmp9_measurement_channel_prompt_manifest_v0_35"
    ):
        raise ValueError("unexpected manifest schema")
    row_by_id = {str(row["row_id"]): row for row in manifest["rows"]}
    if len(row_by_id) != int(manifest["unique_prompt_rows"]):
        raise ValueError("manifest row ids are not unique")
    joined: list[dict[str, Any]] = []
    observed: dict[str, set[int]] = defaultdict(set)
    for record in records:
        row_id = str(record["row_id"])
        if row_id not in row_by_id:
            raise ValueError(f"record outside manifest: {row_id}")
        expected_row = row_by_id[row_id]
        if (
            "row_sha256" in record
            and str(record["row_sha256"]) != str(expected_row["row_sha256"])
        ):
            raise ValueError(f"record row hash mismatch for {row_id}")
        if (
            "prompt_sha256" in record
            and str(record["prompt_sha256"])
            != str(expected_row["prompt_sha256"])
        ):
            raise ValueError(f"record prompt hash mismatch for {row_id}")
        epoch = int(record["planned_epoch"])
        if epoch not in (0, 1) or epoch in observed[row_id]:
            raise ValueError(f"invalid or duplicate epoch for {row_id}")
        observed[row_id].add(epoch)
        joined.append(
            {
                **row_by_id[row_id],
                "planned_epoch": epoch,
                "target_log_odds": _finite(record["target_log_odds"]),
            }
        )
    if set(observed) != set(row_by_id):
        raise ValueError("record universe does not equal manifest universe")
    if any(epochs != {0, 1} for epochs in observed.values()):
        raise ValueError("every prompt row requires two cold-start epochs")
    return joined


def factorial_contrasts(
    joined: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    by_content: dict[
        tuple[str, str, str],
        dict[tuple[str, str], list[float]],
    ] = defaultdict(lambda: defaultdict(list))
    metadata: dict[tuple[str, str, str], Mapping[str, Any]] = {}
    for row in joined:
        key = (
            str(row["family_id"]),
            str(row["query_type"]),
            str(row["content_id"]),
        )
        cell = (
            str(row["presentation_order"]),
            str(row["code_mapping"]),
        )
        by_content[key][cell].append(float(row["target_log_odds"]))
        metadata[key] = row
    output: list[dict[str, Any]] = []
    for key, cells in sorted(by_content.items()):
        if set(cells) != FACTORIAL_CELLS:
            raise ValueError(f"incomplete factorial for {key}")
        if any(len(values) != 2 for values in cells.values()):
            raise ValueError(f"incomplete cold-start factorial for {key}")
        means = {cell: statistics.fmean(values) for cell, values in cells.items()}
        semantic = statistics.fmean(means.values())
        position = statistics.fmean(
            (1 if cell[0] == "target_first" else -1) * value
            for cell, value in means.items()
        )
        code = statistics.fmean(
            (1 if cell[1] == "natural" else -1) * value
            for cell, value in means.items()
        )
        interaction = statistics.fmean(
            (1 if cell[0] == "target_first" else -1)
            * (1 if cell[1] == "natural" else -1)
            * value
            for cell, value in means.items()
        )
        row = metadata[key]
        keep = {
            field: row[field]
            for field in (
                "cell_id",
                "cell_index",
                "mixture_id",
                "anchor_probability",
                "lower_probability",
                "upper_probability",
                "dominance_relation",
            )
            if field in row
        }
        output.append(
            {
                "family_id": key[0],
                "query_type": key[1],
                "content_id": key[2],
                **keep,
                "semantic_contrast": semantic,
                "position_component": position,
                "code_component": code,
                "position_code_interaction": interaction,
                "factorial_cell_means": {
                    f"{cell[0]}--{cell[1]}": value
                    for cell, value in sorted(means.items())
                },
            }
        )
    return output


def cold_start_radius(joined: Iterable[Mapping[str, Any]]) -> float:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in joined:
        grouped[str(row["row_id"])].append(float(row["target_log_odds"]))
    return max(abs(values[0] - values[1]) for values in grouped.values())


def ruler_rows(
    contrasts: Iterable[Mapping[str, Any]],
    query_type: str,
    object_field: str,
    instrument_radius: float,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[tuple[Fraction, float]]] = defaultdict(
        list
    )
    for row in contrasts:
        if row["query_type"] == query_type:
            grouped[(str(row[object_field]), str(row["family_id"]))].append(
                (
                    Fraction(str(row["anchor_probability"])),
                    float(row["semantic_contrast"]),
                )
            )
    output: list[dict[str, Any]] = []
    for (object_id, family_id), points in sorted(grouped.items()):
        ordered = sorted(points)
        if [point[0] for point in ordered] != [
            Fraction(0),
            Fraction(1, 12),
            Fraction(1, 6),
            Fraction(1, 3),
            Fraction(1, 2),
            Fraction(2, 3),
            Fraction(5, 6),
            Fraction(11, 12),
            Fraction(1),
        ]:
            raise ValueError(f"probability grid changed for {object_id}")
        values = [point[1] for point in ordered]
        repair = monotone_linf_radius(values)
        output.append(
            {
                object_field: object_id,
                "family_id": family_id,
                "monotone_linf_radius": repair,
                "repair_within_instrument_radius": repair <= instrument_radius,
                "robust_zero_crossing": robust_zero_crossing(
                    values, instrument_radius
                ),
                "admitted": (
                    repair <= instrument_radius
                    and robust_zero_crossing(values, instrument_radius)
                ),
                "semantic_curve": values,
            }
        )
    return output


def resolve_gate(
    gate: str,
    passed: bool,
    reason: str,
    sequence_open: bool,
) -> tuple[dict[str, Any], bool]:
    if not sequence_open:
        return (
            {
                "gate": gate,
                "instrument_status": "not_evaluated_upstream_stop",
                "decision": "not_evaluated",
                "reason": "upstream_gate_stopped_fixed_sequence",
            },
            False,
        )
    decision = "pass" if passed else "fail"
    return (
        {
            "gate": gate,
            "instrument_status": "valid",
            "decision": decision,
            "reason": "passed" if passed else reason,
        },
        passed,
    )


def evaluate(
    manifest: Mapping[str, Any],
    records: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    joined = validate_and_join(manifest, records)
    contrasts = factorial_contrasts(joined)
    cold_radius = cold_start_radius(joined)
    equality = [
        row
        for row in contrasts
        if row["query_type"] == "semantic_equality_control"
    ]
    equality_radius = max(
        abs(float(row["semantic_contrast"])) for row in equality
    )
    instrument_radius = equality_radius + cold_radius

    by_row_epoch: dict[str, list[float]] = defaultdict(list)
    for row in joined:
        if row["query_type"] == "code_mapping_control":
            by_row_epoch[str(row["row_id"])].append(
                float(row["target_log_odds"])
            )
    c0_pass = bool(by_row_epoch) and all(
        value > 0 for values in by_row_epoch.values() for value in values
    )

    dominance = [
        row
        for row in contrasts
        if row["query_type"]
        in {"probability_order_control", "anchor_dominance_control"}
    ]
    d0_pass = bool(dominance) and all(
        float(row["semantic_contrast"]) > instrument_radius
        for row in dominance
    )

    standard = ruler_rows(
        contrasts,
        "standard_gamble",
        "cell_id",
        instrument_radius,
    )
    compound = ruler_rows(
        contrasts,
        "compound_gamble",
        "mixture_id",
        instrument_radius,
    )
    m0_pass = len(standard) == 36 and len(compound) == 18 and all(
        bool(row["admitted"]) for row in (*standard, *compound)
    )

    standard_admission = {
        (str(row["cell_id"]), str(row["family_id"])): bool(row["admitted"])
        for row in standard
    }
    compound_admission = {
        (str(row["mixture_id"]), str(row["family_id"])): bool(row["admitted"])
        for row in compound
    }
    source_mixtures = {
        str(row["mixture_id"]): (
            f"cell_{int(row['first_cell_index']):02d}",
            f"cell_{int(row['second_cell_index']):02d}",
        )
        for row in manifest["source_compound_mixtures"]
    }
    joint_rows: list[dict[str, Any]] = []
    for mixture_id, (first, second) in sorted(source_mixtures.items()):
        for family_id in sorted(manifest["families"]):
            admitted = (
                compound_admission[(mixture_id, family_id)]
                and standard_admission[(first, family_id)]
                and standard_admission[(second, family_id)]
            )
            joint_rows.append(
                {
                    "mixture_id": mixture_id,
                    "family_id": family_id,
                    "first_cell_id": first,
                    "second_cell_id": second,
                    "admitted": admitted,
                }
            )
    j0_pass = len(joint_rows) == 18 and all(
        bool(row["admitted"]) for row in joint_rows
    )

    gates: list[dict[str, Any]] = []
    sequence_open = True
    for gate, passed, reason in (
        ("C0", c0_pass, "code_channel_invalid"),
        ("D0", d0_pass, "semantic_order_invalid"),
        ("M0", m0_pass, "monotone_ruler_not_established"),
        ("J0", j0_pass, "mixture_analysis_unavailable"),
    ):
        record, sequence_open = resolve_gate(
            gate, passed, reason, sequence_open
        )
        gates.append(record)
    all_pass = all(row["decision"] == "pass" for row in gates)
    result: dict[str, Any] = {
        "schema_version": "asmp9_measurement_channel_gate_result_v0_35",
        "status": (
            "measurement_channel_admitted_for_successor_design_only"
            if all_pass
            else "measurement_channel_stopped"
        ),
        "instrument_radius": {
            "semantic_equality_maximum": equality_radius,
            "cold_start_maximum_delta": cold_radius,
            "total": instrument_radius,
        },
        "gates": gates,
        "standard_rulers": standard,
        "compound_rulers": compound,
        "joint_mixture_rows": joint_rows,
        "factorial_contrasts": contrasts,
        "claim_boundary": (
            "A passing result admits this measurement channel for successor "
            "design only. It does not confirm mixture affinity or the v0.33 "
            "decision quotient and does not resolve ASMP-9."
        ),
    }
    return result


def load_registration(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if payload.get("schema_version") != REGISTRATION_SCHEMA:
        raise ValueError("unexpected registration schema")
    expected = str(payload["registration_content_sha256"])
    actual = hashlib.sha256(
        canonical_bytes(
            {
                key: value
                for key, value in payload.items()
                if key != "registration_content_sha256"
            }
        )
    ).hexdigest()
    if actual != expected:
        raise ValueError("registration content hash mismatch")
    if (
        payload.get("outcomes_consumed") is not False
        or payload.get("status") != "registered_not_run"
    ):
        raise ValueError("registration is not an outcome-blind v0.35 freeze")
    for group_name in ("implementation", "source_artifacts"):
        for name, item in payload[group_name].items():
            candidate = resolve_registered_path(str(item["path"]))
            if not candidate.is_file():
                raise FileNotFoundError(candidate)
            if sha256_file(candidate) != str(item["sha256"]):
                raise ValueError(
                    f"registered {group_name} hash mismatch: {name}"
                )
    for group_name in ("model", "server", "cleanup_script"):
        item = payload[group_name]
        candidate = resolve_registered_path(str(item["path"]))
        if not candidate.is_file():
            raise FileNotFoundError(candidate)
        if sha256_file(candidate) != str(item["sha256"]):
            raise ValueError(f"registered {group_name} hash mismatch")
    return payload


def load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != MANIFEST_SCHEMA:
        raise ValueError("unexpected prompt-manifest schema")
    if (
        payload.get("status") != "registered_not_run"
        or payload.get("execution_authorized") is not True
        or payload.get("outcomes_consumed") is not False
    ):
        raise ValueError("manifest is not an authorized outcome-blind freeze")
    expected = str(payload["manifest_content_sha256"])
    actual = hashlib.sha256(
        canonical_bytes(
            {
                key: value
                for key, value in payload.items()
                if key != "manifest_content_sha256"
            }
        )
    ).hexdigest()
    if actual != expected:
        raise ValueError("manifest content hash mismatch")
    return payload


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    global_indices: set[int] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("schema_version") != RECORD_SCHEMA:
                raise ValueError(
                    f"unexpected record schema on line {line_number}"
                )
            expected = str(record["record_sha256"])
            actual = hashlib.sha256(
                canonical_bytes(
                    {
                        key: value
                        for key, value in record.items()
                        if key != "record_sha256"
                    }
                )
            ).hexdigest()
            if actual != expected:
                raise ValueError(f"record hash mismatch on line {line_number}")
            required = {
                "global_index",
                "planned_epoch",
                "row_id",
                "row_sha256",
                "prompt_sha256",
                "query_type",
                "phase",
                "target_label",
                "comparator_label",
                "choice_probabilities",
                "target_log_odds",
            }
            if not required.issubset(record):
                raise ValueError(
                    f"record missing required fields on line {line_number}"
                )
            global_index = int(record["global_index"])
            if global_index in global_indices:
                raise ValueError("duplicate global record index")
            global_indices.add(global_index)
            probabilities = record["choice_probabilities"]
            if not isinstance(probabilities, Mapping) or set(
                probabilities
            ) != {"A", "B"}:
                raise ValueError("record choice universe is not exactly A/B")
            if {
                str(record["target_label"]),
                str(record["comparator_label"]),
            } != {"A", "B"}:
                raise ValueError("record target/comparator labels are invalid")
            target_probability = _finite(
                probabilities[str(record["target_label"])]
            )
            comparator_probability = _finite(
                probabilities[str(record["comparator_label"])]
            )
            if (
                not 0 < target_probability <= 1
                or not 0 < comparator_probability <= 1
                or not math.isclose(
                    target_probability + comparator_probability,
                    1.0,
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                )
            ):
                raise ValueError("record contains invalid choice mass")
            expected_log_odds = math.log(
                target_probability / comparator_probability
            )
            if not math.isclose(
                _finite(record["target_log_odds"]),
                expected_log_odds,
                rel_tol=1e-12,
                abs_tol=1e-12,
            ):
                raise ValueError("record log odds disagree with probabilities")
            records.append(record)
    if not records:
        raise ValueError("record file is empty")
    return records


def validate_capture(
    registration_path: Path,
    registration: Mapping[str, Any],
    manifest_path: Path,
    manifest: Mapping[str, Any],
    output_dir: Path,
    records: list[dict[str, Any]],
) -> Path:
    registered_manifest = registration["manifest"]
    if sha256_file(manifest_path) != str(registered_manifest["sha256"]):
        raise ValueError("registered manifest file hash mismatch")
    if manifest["manifest_content_sha256"] != str(
        registered_manifest["content_sha256"]
    ):
        raise ValueError("registered manifest content hash mismatch")
    if len(records) != int(manifest["planned_receipts"]):
        raise ValueError("record count does not equal registered plan")
    if any(
        record["phase"] != "burned_measurement_pilot"
        for record in records
    ):
        raise ValueError("record outside the authorized pilot phase")

    summary_path = output_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if (
        summary.get("schema_version") != SUMMARY_SCHEMA
        or summary.get("status") != "measurement_pilot_capture_completed"
        or summary.get("execution_class") != "measurement_pilot"
    ):
        raise ValueError("analysis requires a completed measurement pilot")
    counts = summary["counts"]
    if (
        int(counts["records"]) != len(records)
        or int(counts["unique_prompts"])
        != int(manifest["unique_prompt_rows"])
        or int(counts["planned_epochs"]) != 2
    ):
        raise ValueError("capture summary counts disagree with receipts")
    inputs = summary["inputs"]
    if (
        str(inputs["registration_sha256"])
        != sha256_file(registration_path)
        or str(inputs["registration_content_sha256"])
        != str(registration["registration_content_sha256"])
    ):
        raise ValueError("capture summary registration binding mismatch")
    return summary_path


def write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing unequal output: {path}")
        return
    path.write_bytes(payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    registration_path = args.registration.resolve()
    output_dir = args.output_dir.resolve()
    registration = load_registration(registration_path)
    manifest_path = resolve_registered_path(
        str(registration["manifest"]["path"])
    )
    records_path = output_dir / "pilot_records.jsonl"
    manifest = load_manifest(manifest_path)
    records = load_records(records_path)
    summary_path = validate_capture(
        registration_path,
        registration,
        manifest_path,
        manifest,
        output_dir,
        records,
    )
    result = evaluate(
        manifest,
        records,
    )
    result["inputs"] = {
        "registration_sha256": sha256_file(registration_path),
        "registration_content_sha256": registration[
            "registration_content_sha256"
        ],
        "manifest_sha256": sha256_file(manifest_path),
        "records_sha256": sha256_file(records_path),
        "capture_summary_sha256": sha256_file(summary_path),
        "analyzer_sha256": sha256_file(Path(__file__).resolve()),
    }
    result["analysis_content_sha256"] = hashlib.sha256(
        canonical_bytes(result)
    ).hexdigest()
    write_once(args.output.resolve(), canonical_bytes(result))


if __name__ == "__main__":
    main()
