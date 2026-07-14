"""Frozen exact scorer for one sealed split of the patchwise holdout."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ALLOWED_SPLITS = {"selector", "audit", "outer"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def normalize_response(value: Any) -> str:
    text = str(value).strip()
    if "\n" in text or not text.startswith("ANSWER="):
        return "__INVALID_RESPONSE_CONTRACT__"
    return text[len("ANSWER=") :].strip()


def load_predictions(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        prompt_id = str(row.get("prompt_id", ""))
        if not prompt_id or prompt_id in result:
            raise ValueError(f"invalid or duplicate prompt_id on line {line_number}")
        result[prompt_id] = str(row.get("response", ""))
    return result


def score(
    *, manifest: dict[str, Any], answer_key: dict[str, Any], predictions: dict[str, str], split: str
) -> dict[str, Any]:
    if split not in ALLOWED_SPLITS:
        raise ValueError("scorer may evaluate only selector, audit, or outer")
    answer_hash = hashlib.sha256(canonical_json_bytes(answer_key)).hexdigest()
    if answer_hash != manifest.get("answer_key_sha256"):
        raise ValueError("answer key does not match the public manifest")
    prompts = [row for row in manifest["prompts"] if row["split"] == split]
    expected_ids = {str(row["prompt_id"]) for row in prompts}
    if set(predictions) != expected_ids:
        raise ValueError("predictions must exactly cover the selected split")
    by_family: dict[str, list[int]] = defaultdict(list)
    rows: list[dict[str, Any]] = []
    for prompt in prompts:
        prompt_id = str(prompt["prompt_id"])
        family = str(prompt["behavior_family"])
        expected = str(answer_key["answers"][prompt_id]["answer"])
        observed = normalize_response(predictions[prompt_id])
        correct = int(observed == expected)
        by_family[family].append(correct)
        rows.append({"prompt_id": prompt_id, "behavior_family": family, "correct": bool(correct)})
    return {
        "schema_version": "proposal_recursive_patchwise_score_v1",
        "split": split,
        "prompt_count": len(rows),
        "accuracy": sum(row["correct"] for row in rows) / len(rows),
        "accuracy_by_family": {
            family: sum(values) / len(values) for family, values in sorted(by_family.items())
        },
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--answer-key", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--split", choices=sorted(ALLOWED_SPLITS), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    answer_key = json.loads(args.answer_key.read_text(encoding="utf-8"))
    result = score(
        manifest=manifest,
        answer_key=answer_key,
        predictions=load_predictions(args.predictions),
        split=args.split,
    )
    result["manifest_sha256"] = sha256_file(args.manifest)
    result["answer_key_sha256"] = sha256_file(args.answer_key)
    result["predictions_sha256"] = sha256_file(args.predictions)
    if args.output.exists():
        raise FileExistsError("score output is write-once")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_json_bytes(result))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
