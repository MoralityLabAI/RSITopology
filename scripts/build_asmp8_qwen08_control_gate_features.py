"""Seal outcome-blind ASMP-8 features from the stratified Qwen audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import fmean, pstdev
from typing import Any, Iterable, Mapping


PROMPT_PREFIX = "Represent this controller state without choosing an action.\n"


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_records(records_dir: Path) -> list[dict[str, Any]]:
    paths = sorted(records_dir.glob("*.json"))
    if not paths:
        raise ValueError("records directory is empty")
    return [load_json(path) for path in paths]


def _ranked_scores(payload: Mapping[str, Any]) -> list[tuple[str, float]]:
    values = payload.get("proposer_scores")
    if not isinstance(values, list) or len(values) < 2:
        raise ValueError("prompt requires at least two proposer scores")
    indexed = [
        (index, str(item["action"]), float(item["score"]))
        for index, item in enumerate(values)
    ]
    indexed.sort(key=lambda item: (-item[2], item[0]))
    return [(action, score) for _, action, score in indexed]


def build_feature_rows(
    manifest: Mapping[str, Any],
    records: Iterable[Mapping[str, Any]],
    *,
    probability_tolerance: float,
) -> list[dict[str, Any]]:
    manifest_rows = manifest.get("rows")
    if not isinstance(manifest_rows, list) or not manifest_rows:
        raise ValueError("manifest rows are required")
    by_row: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        if record.get("phase") != "census_crossover":
            continue
        by_row.setdefault(str(record["row_id"]), []).append(record)

    expected_ids = {str(row["row_id"]) for row in manifest_rows}
    if set(by_row) != expected_ids:
        raise ValueError("census record universe differs from manifest row universe")

    output: list[dict[str, Any]] = []
    for row in sorted(manifest_rows, key=lambda item: str(item["row_id"])):
        row_id = str(row["row_id"])
        values = by_row[row_id]
        if len(values) != 4:
            raise ValueError(f"{row_id} requires four census receipts")
        token_ids = {int(value["tokens"][0]) for value in values}
        probabilities = [float(value["probability"]) for value in values]
        if len(token_ids) != 1:
            raise ValueError(f"{row_id} has inconsistent top-token identities")
        if max(probabilities) - min(probabilities) > probability_tolerance:
            raise ValueError(f"{row_id} exceeds the registered probability tolerance")
        references = [
            value
            for value in values
            if int(value["planned_epoch"]) == 0 and not bool(value["cache_prompt"])
        ]
        if len(references) != 1:
            raise ValueError(f"{row_id} lacks one epoch-0 uncached reference")

        prompt = str(row["prompt"])
        if not prompt.startswith(PROMPT_PREFIX):
            raise ValueError("prompt prefix differs from the registered contract")
        payload = json.loads(prompt[len(PROMPT_PREFIX) :])
        ranked = _ranked_scores(payload)
        score_values = [score for _, score in ranked]
        feature = {
            "schema_version": "asmp8_qwen08_control_gate_feature_v0_1",
            "row_id": row_id,
            "application": str(row["application"]),
            "geometry_half": str(row["geometry_half"]),
            "prompt_sha256": str(row["prompt_sha256"]),
            "qwen_top_token_id": next(iter(token_ids)),
            "qwen_top_token_probability": float(references[0]["probability"]),
            "proxy_selected_action": ranked[0][0],
            "score_maximum": max(score_values),
            "score_second": ranked[1][1],
            "score_margin": ranked[0][1] - ranked[1][1],
            "score_mean": fmean(score_values),
            "score_sd": pstdev(score_values),
            "score_range": max(score_values) - min(score_values),
        }
        if not all(
            math.isfinite(float(feature[name]))
            for name in (
                "qwen_top_token_probability",
                "score_maximum",
                "score_second",
                "score_margin",
                "score_mean",
                "score_sd",
                "score_range",
            )
        ):
            raise ValueError(f"{row_id} contains a nonfinite feature")
        output.append(feature)
    return output


def write_once(path: Path, payload: bytes) -> None:
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"write-once artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--records-dir", type=Path, required=True)
    parser.add_argument("--output-jsonl", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    parser.add_argument("--probability-tolerance", type=float, default=1e-6)
    args = parser.parse_args()

    rows = build_feature_rows(
        load_json(args.manifest),
        load_records(args.records_dir),
        probability_tolerance=args.probability_tolerance,
    )
    payload = (
        "\n".join(canonical_json(row) for row in rows) + "\n"
    ).encode("utf-8")
    write_once(args.output_jsonl, payload)
    receipt = {
        "schema_version": "asmp8_qwen08_control_gate_feature_receipt_v0_1",
        "status": "outcome_blind_features_sealed",
        "row_count": len(rows),
        "application_count": len({row["application"] for row in rows}),
        "geometry_halves": sorted({row["geometry_half"] for row in rows}),
        "manifest_sha256": sha256_path(args.manifest),
        "feature_table_sha256": hashlib.sha256(payload).hexdigest(),
        "records_dir": str(args.records_dir.resolve()),
        "outcomes_consumed": False,
    }
    receipt_payload = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    write_once(args.output_receipt, receipt_payload)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
