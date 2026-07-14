"""Generate a fresh deterministic four-family holdout without model outcomes."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
from typing import Any

import numpy as np


SEED = 2026071403
FAMILIES = ("affine_recurrence", "symbol_transport", "grid_rotation", "graph_reachability")
SPLITS = ("construction", "selector", "audit", "outer")
PER_FAMILY_SPLIT = 4


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_once_or_equal(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"write-once holdout artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _affine(rng: np.random.Generator) -> tuple[str, str]:
    multiplier = int(rng.choice([-3, -2, 2, 3]))
    offset = int(rng.integers(-7, 8))
    value = int(rng.integers(-5, 6))
    sequence = [value]
    for _ in range(4):
        value = multiplier * value + offset
        sequence.append(value)
    prompt = (
        "Apply the same affine recurrence at every step. "
        f"Sequence: {', '.join(str(item) for item in sequence[:4])}. "
        "Return the next integer as ANSWER=<integer>."
    )
    return prompt, str(sequence[4])


def _symbols(rng: np.random.Generator) -> tuple[str, str]:
    alphabet = np.asarray(list("ABCDE"))
    target = rng.permutation(alphabet)
    mapping = {str(left): str(right) for left, right in zip(alphabet, target)}
    source = "".join(str(item) for item in rng.choice(alphabet, size=5, replace=True))
    transformed = "".join(mapping[item] for item in source)
    map_text = ", ".join(f"{key}->{mapping[key]}" for key in sorted(mapping))
    prompt = (
        f"Use this symbol transport exactly once: {map_text}. Input: {source}. "
        "Return the transported string as ANSWER=<string>."
    )
    return prompt, transformed


def _grid(rng: np.random.Generator) -> tuple[str, str]:
    grid = rng.integers(0, 2, size=(3, 3))
    while int(np.sum(grid)) in {0, 9}:
        grid = rng.integers(0, 2, size=(3, 3))
    rotated = np.rot90(grid, k=-1)
    source = "/".join("".join(str(int(value)) for value in row) for row in grid)
    answer = "/".join("".join(str(int(value)) for value in row) for row in rotated)
    prompt = (
        f"The 3x3 binary grid is {source}. Rotate it 90 degrees clockwise. "
        "Return rows separated by '/' as ANSWER=<rows>."
    )
    return prompt, answer


def _reachable(edges: set[tuple[int, int]], source: int, target: int) -> bool:
    queue: deque[int] = deque([source])
    seen = {source}
    while queue:
        node = queue.popleft()
        if node == target:
            return True
        for left, right in sorted(edges):
            if left == node and right not in seen:
                seen.add(right)
                queue.append(right)
    return False


def _graph(rng: np.random.Generator, desired: bool) -> tuple[str, str]:
    nodes = list("ABCDEF")
    for _ in range(1000):
        edges = {
            (left, right)
            for left in range(6)
            for right in range(left + 1, 6)
            if float(rng.random()) < 0.27
        }
        source = int(rng.integers(0, 5))
        target = int(rng.integers(source + 1, 6))
        if _reachable(edges, source, target) == desired and edges:
            edge_text = ", ".join(f"{nodes[left]}->{nodes[right]}" for left, right in sorted(edges))
            prompt = (
                f"Directed edges: {edge_text}. Is {nodes[target]} reachable from {nodes[source]}? "
                "Return ANSWER=YES or ANSWER=NO."
            )
            return prompt, "YES" if desired else "NO"
    raise RuntimeError("could not generate balanced reachability fixture")


def generate() -> tuple[dict[str, Any], dict[str, Any]]:
    rng = np.random.default_rng(SEED)
    prompts: list[dict[str, Any]] = []
    answers: dict[str, dict[str, str]] = {}
    seen_text: set[str] = set()
    for family in FAMILIES:
        family_index = FAMILIES.index(family)
        for split in SPLITS:
            split_index = SPLITS.index(split)
            for offset in range(PER_FAMILY_SPLIT):
                if family == "affine_recurrence":
                    text, answer = _affine(rng)
                elif family == "symbol_transport":
                    text, answer = _symbols(rng)
                elif family == "grid_rotation":
                    text, answer = _grid(rng)
                else:
                    desired = (split_index * PER_FAMILY_SPLIT + offset) % 2 == 0
                    text, answer = _graph(rng, desired)
                if text in seen_text:
                    raise ValueError("generated duplicate prompt text")
                seen_text.add(text)
                prompt_id = f"pr2-{family_index:02d}-{split_index:02d}-{offset:02d}"
                prompts.append(
                    {
                        "prompt_id": prompt_id,
                        "behavior_family": family,
                        "split": split,
                        "prompt": text,
                        "response_contract": "one line exactly: ANSWER=<value>",
                    }
                )
                answers[prompt_id] = {
                    "behavior_family": family,
                    "split": split,
                    "answer": answer,
                }
    answer_key = {
        "schema_version": "proposal_recursive_patchwise_answer_key_v1",
        "seed": SEED,
        "answers": answers,
    }
    answer_bytes = canonical_json_bytes(answer_key)
    manifest = {
        "schema_version": "proposal_recursive_patchwise_holdout_v1",
        "status": "fresh_prereveal_holdout",
        "seed": SEED,
        "generator_sha256": sha256_file(Path(__file__).resolve()),
        "answer_key_sha256": sha256_bytes(answer_bytes),
        "answer_key_not_exposed_to_proposer": True,
        "parent_prompt_corpus_reused": False,
        "model_outcomes_collected": False,
        "behavior_families": list(FAMILIES),
        "splits": list(SPLITS),
        "prompts_per_family_per_split": PER_FAMILY_SPLIT,
        "prompt_count": len(prompts),
        "prompts": prompts,
    }
    return manifest, answer_key


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--answer-key", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    manifest, answer_key = generate()
    manifest_bytes = canonical_json_bytes(manifest)
    answer_bytes = canonical_json_bytes(answer_key)
    write_once_or_equal(args.manifest.resolve(), manifest_bytes)
    write_once_or_equal(args.answer_key.resolve(), answer_bytes)
    receipt = {
        "schema_version": "proposal_recursive_patchwise_holdout_generation_receipt_v1",
        "status": "complete_without_model_execution",
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "answer_key_sha256": sha256_bytes(answer_bytes),
        "generator_sha256": sha256_file(Path(__file__).resolve()),
        "prompt_count": manifest["prompt_count"],
        "model_outcomes_collected": False,
    }
    write_once_or_equal(args.receipt.resolve(), canonical_json_bytes(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
