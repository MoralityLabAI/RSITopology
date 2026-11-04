"""Reveal deterministic control-task outcomes after ASMP-8 feature sealing."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


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
    parser.add_argument("--feature-table", type=Path, required=True)
    parser.add_argument("--module-root", type=Path, required=True)
    parser.add_argument("--control-tasks-source", type=Path, required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--per-split-per-application", type=int, required=True)
    parser.add_argument("--output-jsonl", type=Path, required=True)
    args = parser.parse_args()

    if sha256_path(args.control_tasks_source) != args.expected_source_sha256:
        raise ValueError("control-task generator source hash differs")
    sys.path.insert(0, str(args.module_root.resolve()))
    from research_gym.envs.control_tasks import generate_control_tasks  # noqa: PLC0415

    features = load_jsonl(args.feature_table)
    feature_ids = [str(row["row_id"]) for row in features]
    if len(feature_ids) != len(set(feature_ids)):
        raise ValueError("feature table contains duplicate row IDs")

    tasks = generate_control_tasks(
        n_train=args.per_split_per_application,
        n_eval=args.per_split_per_application,
        seed=args.seed,
    )
    task_map = {task.task_id: task for task in tasks if task.split == "train"}
    if set(feature_ids) != set(task_map):
        raise ValueError("feature and generated outcome universes differ")

    rows = []
    for feature in sorted(features, key=lambda item: str(item["row_id"])):
        task = task_map[str(feature["row_id"])]
        order = {action: index for index, action in enumerate(task.actions)}
        selected = sorted(
            task.actions,
            key=lambda action: (-float(task.trm_scores[action]), order[action]),
        )[0]
        if selected != feature["proxy_selected_action"]:
            raise ValueError("feature-side proxy action differs from task generator")
        optimal = task.optimal_action
        row = {
            "schema_version": "asmp8_control_task_outcome_v0_1",
            "row_id": task.task_id,
            "proxy_selected_action": selected,
            "optimal_action": optimal,
            "proxy_correct": selected == optimal,
            "proxy_safe": selected in task.environment_allowed,
            "proxy_utility": float(task.utilities[selected]),
            "optimal_utility": float(task.utilities[optimal]),
            "proxy_regret": float(task.utilities[optimal] - task.utilities[selected]),
        }
        rows.append(row)
    payload = (
        "\n".join(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows)
        + "\n"
    ).encode()
    write_once(args.output_jsonl, payload)
    print(
        json.dumps(
            {
                "status": "outcomes_revealed",
                "row_count": len(rows),
                "outcome_table_sha256": hashlib.sha256(payload).hexdigest(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
