from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from rsi_topology.qwen_precision_context import (
    _complete_margin_draw,
    _rank_one_retention,
)
from rsi_topology.qwen_precision_context_v0_1_1 import (
    complete_margin_draw_fast,
    paired_complete_margin_summary_resumable,
    rank_one_retention_fast,
)


def _fixture(seed: int = 7) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    classes = 4
    per_class = 6
    labels = np.asarray(
        [f"class-{label}" for _half in range(2) for label in range(classes) for _ in range(per_class)],
        dtype=object,
    )
    halves = np.asarray(
        [half for half in ("construction", "geometry_validation") for _label in range(classes) for _ in range(per_class)],
        dtype=object,
    )
    signal = rng.normal(size=(classes, 24))
    class_index = np.asarray([int(str(label).split("-")[-1]) for label in labels])
    base = signal[class_index] + 0.4 * rng.normal(size=(len(labels), 24))
    return {
        "4bit": base + 0.03 * rng.normal(size=base.shape),
        "float16": base,
    }, labels, halves


def test_fast_rank_one_retention_matches_reference() -> None:
    features, labels, halves = _fixture()
    for values in features.values():
        expected = _rank_one_retention(values, labels, halves)
        observed = rank_one_retention_fast(values, labels, halves)
        assert observed == pytest.approx(expected, abs=1e-12)


def test_fast_complete_margin_preserves_rng_and_estimand() -> None:
    features, labels, halves = _fixture()
    reference_rng = np.random.default_rng(991)
    fast_rng = np.random.default_rng(991)
    expected = _complete_margin_draw(
        feature_by_precision=features,
        labels=labels,
        halves=halves,
        inner_replicates=12,
        rng=reference_rng,
        strict_margin=0.02,
    )
    observed = complete_margin_draw_fast(
        feature_by_precision=features,
        labels=labels,
        halves=halves,
        inner_replicates=12,
        rng=fast_rng,
        strict_margin=0.02,
    )
    assert observed == pytest.approx(expected, abs=1e-10)
    assert fast_rng.bit_generator.state == reference_rng.bit_generator.state


def _summary_inputs() -> tuple[dict, dict, dict]:
    first = _fixture(11)
    second = _fixture(19)
    raw = {
        ("base", "model.layers.19", "shard-00", "graph_reachability"): {
            "4bit": (first[0]["4bit"], first[1], first[2]),
            "float16": (first[0]["float16"], first[1], first[2]),
        },
        ("naive_qlora", "model.layers.19", "shard-01", "graph_reachability"): {
            "4bit": (second[0]["4bit"], second[1], second[2]),
            "float16": (second[0]["float16"], second[1], second[2]),
        },
    }
    gates = {}
    for key in raw:
        for precision in ("4bit", "float16"):
            gates[(precision, *key)] = SimpleNamespace(
                objects=[SimpleNamespace(passed=True)]
            )
    protocol = {
        "primary_comparison": {
            "paired_bootstrap_outer_replicates": 8,
            "paired_bootstrap_inner_replicates": 3,
        },
        "primary_object": {"minimum_strict_null_margin": 0.02},
        "sentinel": {
            "state": "base",
            "site": "model.layers.19",
            "context_shard": "shard-00",
            "family": "graph_reachability",
        },
    }
    return raw, gates, protocol


def test_interrupted_run_resumes_to_identical_summary(tmp_path: Path) -> None:
    raw, gates, protocol = _summary_inputs()
    clean = paired_complete_margin_summary_resumable(
        raw_cells=raw,
        gate_filtrations=gates,
        protocol=protocol,
        seed=123,
        checkpoint_dir=tmp_path / "clean",
        binding_sha256="a" * 64,
        block_size=2,
    )
    calls = 0

    def interrupt(_value: dict) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("registered interruption")

    with pytest.raises(RuntimeError, match="registered interruption"):
        paired_complete_margin_summary_resumable(
            raw_cells=raw,
            gate_filtrations=gates,
            protocol=protocol,
            seed=123,
            checkpoint_dir=tmp_path / "resume",
            binding_sha256="a" * 64,
            block_size=2,
            progress=interrupt,
        )
    resumed = paired_complete_margin_summary_resumable(
        raw_cells=raw,
        gate_filtrations=gates,
        protocol=protocol,
        seed=123,
        checkpoint_dir=tmp_path / "resume",
        binding_sha256="a" * 64,
        block_size=2,
    )
    assert resumed == clean


def test_tampered_checkpoint_fails_closed(tmp_path: Path) -> None:
    raw, gates, protocol = _summary_inputs()
    paired_complete_margin_summary_resumable(
        raw_cells=raw,
        gate_filtrations=gates,
        protocol=protocol,
        seed=123,
        checkpoint_dir=tmp_path,
        binding_sha256="b" * 64,
        block_size=4,
    )
    path = sorted(tmp_path.rglob("block_*.json"))[0]
    value = json.loads(path.read_text(encoding="utf-8"))
    value["binding_sha256"] = "c" * 64
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="binding differs"):
        paired_complete_margin_summary_resumable(
            raw_cells=raw,
            gate_filtrations=gates,
            protocol=protocol,
            seed=123,
            checkpoint_dir=tmp_path,
            binding_sha256="b" * 64,
            block_size=4,
        )
