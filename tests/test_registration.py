from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "register_one_prompt_benchmark",
    ROOT / "scripts" / "register_one_prompt_benchmark.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def valid_registration() -> dict:
    return {
        "run_id": "one-prompt-001",
        "dry_run": False,
        "model_id": "model",
        "model_revision": "revision",
        "model_weight_sha256": "a" * 64,
        "tokenizer_id": "tokenizer",
        "tokenizer_sha256": "b" * 64,
        "prompt_id": "prompt-1",
        "prompt_corpus_sha256": "c" * 64,
        "jspace_protocol_sha256": "d" * 64,
        "implementation_commit": "abcdef1",
        "exact_command": ["python", "runner.py"],
        "environment_lock_sha256": "e" * 64,
        "module_graph_mapping": {"layer0": "h0"},
        "candidate_sites": ["h1"],
        "norm_grid": [0.25, 0.5, 1.0],
        "candidate_ranks": [1, 2, 4],
        "candidate_count": 12,
        "resource_caps": {
            "memory_mb": 1024,
            "cpu_percent": 25,
            "io_mb_s": 20,
            "swap_bytes": 0,
            "timeout_seconds": 900,
        },
        "checkpoint_interval": "one_phase",
        "chunk_strategy": "64 rows",
        "outcomes_prohibited": True,
        "weight_mutation_prohibited": True,
    }


def test_one_prompt_registration_requires_hard_caps_and_prohibitions() -> None:
    MODULE.validate(valid_registration())
    bad = valid_registration()
    bad["resource_caps"]["io_mb_s"] = 0
    with pytest.raises(ValueError, match="resource caps"):
        MODULE.validate(bad)
    bad = valid_registration()
    bad["outcomes_prohibited"] = False
    with pytest.raises(ValueError, match="prohibit"):
        MODULE.validate(bad)

