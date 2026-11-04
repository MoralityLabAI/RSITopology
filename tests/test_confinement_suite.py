from __future__ import annotations

import json
from pathlib import Path

from rsi_topology.confinement_experiments.common import WorkUnit, load_config
from rsi_topology.confinement_experiments.runner import run_config
from rsi_topology.confinement_experiments.suite import generate_work_units


ROOT = Path(__file__).resolve().parents[1]


def test_all_registered_configs_parse_and_generate_unique_units():
    for profile in ("smoke", "pilot", "full"):
        for path in sorted((ROOT / "configs" / profile).glob("*.yaml")):
            config = load_config(path)
            units = generate_work_units(config)
            assert units
            assert len({unit.unit_id for unit in units}) == len(units)


def test_scientific_seed_is_independent_of_implementation_receipt_identity():
    left = WorkUnit("example", {"cell": 1}, 17, "implementation-a")
    right = WorkUnit("example", {"cell": 1}, 17, "implementation-b")
    assert left.unit_id != right.unit_id
    assert left.scientific_identity == right.scientific_identity
    assert left.seed == right.seed


def test_tiny_run_is_resumable_and_receipted(tmp_path):
    config = {
        "schema_version": "confinement-experiment-config-v1",
        "experiment": "02_spectral_entropy",
        "run_id": "unit",
        "seed": 12,
        "parameters": {
            "horizon": 5,
            "block_length": 2,
            "collar_ratio": 0.5,
            "family_a_index": 1,
            "family_a_values": [1.2],
            "family_b_entropy": 1.0,
            "family_b_indices": [1],
            "family_c_delta": 0.1,
            "family_c_indices": [1],
            "precision_bits": [1],
        },
    }
    path = tmp_path / "config.yaml"
    path.write_text(json.dumps(config), encoding="utf-8")
    first = run_config(path, output_root=tmp_path / "results")
    second = run_config(path, output_root=tmp_path / "results")
    assert first == second
    run_dir = Path(first["run_dir"])
    assert (run_dir / "aggregate.csv").exists()
    assert (run_dir / "figure.png").exists()
    assert (run_dir / "checksums.json").exists()
