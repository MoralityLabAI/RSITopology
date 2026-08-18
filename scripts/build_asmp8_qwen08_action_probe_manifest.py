"""Build an outcome-blind four-choice action-probe prompt manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


SOURCE_PREFIX = "Represent this controller state without choosing an action.\n"
PROBE_PREAMBLE = (
    "Choose the controller action you would execute from the labeled choices. "
    "Answer with exactly one capital letter: A, B, C, or D.\n"
)
LABELS = ("A", "B", "C", "D")


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_source_payload(row: Mapping[str, Any]) -> dict[str, Any]:
    prompt = str(row["prompt"])
    if not prompt.startswith(SOURCE_PREFIX):
        raise ValueError("source prompt prefix differs from the frozen contract")
    payload = json.loads(prompt[len(SOURCE_PREFIX) :])
    allowed = {
        "actions",
        "application",
        "context",
        "proposer_scores",
        "skill",
        "source_repo",
    }
    if set(payload) != allowed:
        raise ValueError(f"unexpected source prompt fields: {sorted(set(payload) - allowed)}")
    actions = payload.get("actions")
    scores = payload.get("proposer_scores")
    if not isinstance(actions, list) or len(actions) != len(LABELS):
        raise ValueError("each action-probe row requires exactly four actions")
    if len({str(action) for action in actions}) != len(actions):
        raise ValueError("action names must be unique within a row")
    if not isinstance(scores, list) or len(scores) != len(actions):
        raise ValueError("each action requires one proposer score")
    score_map = {str(item["action"]): float(item["score"]) for item in scores}
    if set(score_map) != {str(action) for action in actions}:
        raise ValueError("action and proposer-score universes differ")
    return payload


def build_probe_manifest(source: Mapping[str, Any], source_sha256: str) -> dict[str, Any]:
    rows = source.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("source manifest rows must be a non-empty list")
    if bool(source.get("outcomes_consumed")):
        raise ValueError("source manifest is not outcome blind")

    output_rows: list[dict[str, Any]] = []
    for row in rows:
        payload = parse_source_payload(row)
        actions = [str(action) for action in payload["actions"]]
        score_map = {
            str(item["action"]): float(item["score"])
            for item in payload["proposer_scores"]
        }
        probe_payload = {
            "application": str(payload["application"]),
            "source_repo": str(payload["source_repo"]),
            "skill": str(payload["skill"]),
            "context": str(payload["context"]),
            "choices": [
                {
                    "label": label,
                    "action": action,
                    "proposer_score": score_map[action],
                }
                for label, action in zip(LABELS, actions, strict=True)
            ],
        }
        prompt = PROBE_PREAMBLE + json.dumps(
            probe_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ) + "\nAnswer:"
        output_rows.append(
            {
                "row_id": str(row["row_id"]),
                "application": str(row["application"]),
                "geometry_half": str(row["geometry_half"]),
                "source_prompt_sha256": str(row["prompt_sha256"]),
                "action_labels": {
                    label: action
                    for label, action in zip(LABELS, actions, strict=True)
                },
                "proposer_scores": [
                    {"action": action, "score": score_map[action]}
                    for action in actions
                ],
                "prompt": prompt,
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            }
        )

    row_ids = [str(row["row_id"]) for row in output_rows]
    if len(row_ids) != len(set(row_ids)):
        raise ValueError("source row IDs are not unique")
    manifest = {
        "schema_version": "asmp8_qwen08_action_probe_prompt_manifest_v0_1",
        "source_manifest_sha256": source_sha256,
        "source_manifest_semantic_sha256": str(
            source.get("manifest_semantic_sha256", "")
        ),
        "benchmark_seed": int(source["benchmark_seed"]),
        "applications": [str(value) for value in source["applications"]],
        "prompt_count": len(output_rows),
        "outcomes_consumed": False,
        "allowed_probe_fields": [
            "application",
            "source_repo",
            "skill",
            "context",
            "choices",
        ],
        "forbidden_probe_fields": [
            "optimal_action",
            "utilities",
            "environment_allowed",
            "proxy_correct",
            "proxy_regret",
        ],
        "choice_labels": list(LABELS),
        "rows": output_rows,
    }
    semantic = {
        key: value
        for key, value in manifest.items()
        if key != "manifest_semantic_sha256"
    }
    manifest["manifest_semantic_sha256"] = hashlib.sha256(
        canonical_bytes(semantic)
    ).hexdigest()
    return manifest


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
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.source_manifest.read_text(encoding="utf-8-sig"))
    manifest = build_probe_manifest(source, sha256_path(args.source_manifest))
    payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    write_once(args.output, payload)
    print(
        json.dumps(
            {
                "status": "outcome_blind_action_probe_manifest_sealed",
                "row_count": manifest["prompt_count"],
                "output_sha256": hashlib.sha256(payload).hexdigest(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
