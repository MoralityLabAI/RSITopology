"""Seal outcome-blind features from two cold-start action-probe captures."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import fmean, pstdev
from typing import Any, Iterable, Mapping


LABELS = ("A", "B", "C", "D")
PROBE_FEATURES = (
    "probe_probability_A",
    "probe_probability_B",
    "probe_probability_C",
    "probe_probability_D",
    "probe_probability_maximum",
    "probe_probability_margin",
    "probe_proxy_action_probability",
    "probe_normalized_entropy",
    "probe_proxy_disagreement",
)


def canonical_json(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )


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


def _ranked_scores(row: Mapping[str, Any]) -> list[tuple[str, float]]:
    values = row.get("proposer_scores")
    if not isinstance(values, list) or len(values) != 4:
        raise ValueError("each row requires four proposer scores")
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
    sum_tolerance: float,
) -> list[dict[str, Any]]:
    rows = manifest.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("manifest rows are required")
    by_row: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        by_row.setdefault(str(record["row_id"]), []).append(record)
    expected_ids = {str(row["row_id"]) for row in rows}
    if set(by_row) != expected_ids:
        raise ValueError("record universe differs from manifest universe")

    output = []
    for row in sorted(rows, key=lambda item: str(item["row_id"])):
        row_id = str(row["row_id"])
        row_records = sorted(
            by_row[row_id], key=lambda item: int(item["planned_epoch"])
        )
        if len(row_records) != 2:
            raise ValueError(f"{row_id} requires exactly two cold-start records")
        if [int(record["planned_epoch"]) for record in row_records] != [0, 1]:
            raise ValueError(f"{row_id} has unexpected epoch coverage")
        vectors = []
        for record in row_records:
            values = record.get("choice_probabilities")
            if not isinstance(values, Mapping) or set(values) != set(LABELS):
                raise ValueError(f"{row_id} has an incomplete choice vector")
            vector = {label: float(values[label]) for label in LABELS}
            if not all(math.isfinite(value) and value >= 0 for value in vector.values()):
                raise ValueError(f"{row_id} has invalid choice probabilities")
            if abs(sum(vector.values()) - 1.0) > sum_tolerance:
                raise ValueError(f"{row_id} choice vector does not sum to one")
            vectors.append(vector)
        maximum_delta = max(
            abs(vectors[0][label] - vectors[1][label]) for label in LABELS
        )
        if maximum_delta > probability_tolerance:
            raise ValueError(f"{row_id} exceeds cold-start repeat tolerance")

        vector = vectors[0]
        label_order = {label: index for index, label in enumerate(LABELS)}
        ranked_labels = sorted(
            LABELS, key=lambda label: (-vector[label], label_order[label])
        )
        action_labels = {
            str(label): str(action) for label, action in row["action_labels"].items()
        }
        if set(action_labels) != set(LABELS):
            raise ValueError(f"{row_id} action-label map differs")
        scores = _ranked_scores(row)
        score_values = [score for _, score in scores]
        proxy_action = scores[0][0]
        proxy_label = next(
            label for label in LABELS if action_labels[label] == proxy_action
        )
        entropy = -sum(
            value * math.log(value) for value in vector.values() if value > 0
        )
        feature = {
            "schema_version": "asmp8_qwen08_action_probe_feature_v0_1",
            "row_id": row_id,
            "application": str(row["application"]),
            "geometry_half": str(row["geometry_half"]),
            "prompt_sha256": str(row["prompt_sha256"]),
            "proxy_selected_action": proxy_action,
            "proxy_selected_label": proxy_label,
            "probe_selected_label": ranked_labels[0],
            "probe_selected_action": action_labels[ranked_labels[0]],
            "probe_proxy_disagreement": float(ranked_labels[0] != proxy_label),
            "probe_probability_A": vector["A"],
            "probe_probability_B": vector["B"],
            "probe_probability_C": vector["C"],
            "probe_probability_D": vector["D"],
            "probe_probability_maximum": vector[ranked_labels[0]],
            "probe_probability_margin": (
                vector[ranked_labels[0]] - vector[ranked_labels[1]]
            ),
            "probe_proxy_action_probability": vector[proxy_label],
            "probe_entropy_nats": entropy,
            "probe_normalized_entropy": entropy / math.log(4.0),
            "cold_start_maximum_probability_delta": maximum_delta,
            "score_maximum": max(score_values),
            "score_second": scores[1][1],
            "score_margin": scores[0][1] - scores[1][1],
            "score_mean": fmean(score_values),
            "score_sd": pstdev(score_values),
            "score_range": max(score_values) - min(score_values),
        }
        numeric = [
            value
            for key, value in feature.items()
            if key.startswith("probe_") or key.startswith("score_")
        ]
        if not all(
            isinstance(value, (int, float)) and math.isfinite(float(value))
            for value in numeric
            if not isinstance(value, str)
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
    parser.add_argument("--probability-tolerance", type=float, default=1e-7)
    parser.add_argument("--sum-tolerance", type=float, default=1e-7)
    parser.add_argument("--liveness-variance-floor", type=float, default=1e-6)
    args = parser.parse_args()

    rows = build_feature_rows(
        load_json(args.manifest),
        load_records(args.records_dir),
        probability_tolerance=args.probability_tolerance,
        sum_tolerance=args.sum_tolerance,
    )
    payload = (
        "\n".join(canonical_json(row) for row in rows) + "\n"
    ).encode("utf-8")
    write_once(args.output_jsonl, payload)
    construction = [
        row for row in rows if row["geometry_half"] == "construction"
    ]
    variances = {
        name: pstdev(float(row[name]) for row in construction) ** 2
        for name in PROBE_FEATURES
    }
    liveness_pass = max(variances.values()) >= args.liveness_variance_floor
    receipt = {
        "schema_version": "asmp8_qwen08_action_probe_feature_receipt_v0_1",
        "status": "outcome_blind_action_probe_features_sealed",
        "row_count": len(rows),
        "manifest_sha256": sha256_path(args.manifest),
        "feature_table_sha256": hashlib.sha256(payload).hexdigest(),
        "records_dir": str(args.records_dir.resolve()),
        "probability_tolerance": args.probability_tolerance,
        "sum_tolerance": args.sum_tolerance,
        "liveness": {
            "status": "pass" if liveness_pass else "fail",
            "population_variances": variances,
            "required_maximum_variance_floor": args.liveness_variance_floor,
            "observed_maximum_variance": max(variances.values()),
        },
        "outcomes_consumed": False,
    }
    receipt_payload = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    write_once(args.output_receipt, receipt_payload)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
