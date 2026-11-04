from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
V016 = HERE.parent / "balanced_design_v0_16"
V0161 = HERE.parent / "balanced_design_v0_16_1"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_registries_are_disjoint_from_both_aborted_attempts() -> None:
    current = load(HERE / "protocol_v0_16_2.json")
    previous = [
        load(V016 / "protocol_v0_16.json"),
        load(V0161 / "protocol_v0_16_1.json"),
    ]
    for old in previous:
        assert set(current["pair_registry"]["epsilon"]).isdisjoint(
            old["pair_registry"]["epsilon"]
        )
        assert set(current["pair_registry"]["a"]).isdisjoint(
            old["pair_registry"]["a"]
        )
        assert set(current["pair_registry"]["differences"]).isdisjoint(
            old["pair_registry"]["differences"]
        )
        assert set(
            current["global_allocation_registry"]["extra_total_trials"]
        ).isdisjoint(
            old["global_allocation_registry"]["extra_total_trials"]
        )
        assert set(
            current["compact_value_registry"]["cycle_lengths"]
        ).isdisjoint(old["compact_value_registry"]["cycle_lengths"])
        assert set(
            current["threshold_registry"]["cycle_lengths"]
        ).isdisjoint(old["threshold_registry"]["cycle_lengths"])


def test_resource_cap_and_gate_universe_are_unchanged() -> None:
    current = load(HERE / "protocol_v0_16_2.json")
    first = load(V016 / "protocol_v0_16.json")
    second = load(V0161 / "protocol_v0_16_1.json")
    assert current["resource_caps"] == first["resource_caps"]
    assert current["resource_caps"] == second["resource_caps"]
    assert current["gate_ids"] == first["gate_ids"]
    assert current["gate_ids"] == second["gate_ids"]


def test_frozen_cell_counts() -> None:
    protocol = load(HERE / "protocol_v0_16_2.json")
    pair = protocol["pair_registry"]
    label_count = sum(
        2 ** len(values) for values in pair["other_count_tuples"]
    )
    assert (
        len(pair["epsilon"])
        * len(pair["a"])
        * len(pair["differences"])
        * label_count
        == 504
    )
    global_registry = protocol["global_allocation_registry"]
    assert (
        len(global_registry["cycle_lengths"])
        * len(global_registry["epsilon"])
        * len(global_registry["extra_total_trials"])
        == 16
    )
    compact = protocol["compact_value_registry"]
    assert (
        len(compact["cycle_lengths"])
        * len(compact["epsilon"])
        * len(compact["extra_total_trials"])
        == 12
    )
    threshold = protocol["threshold_registry"]
    assert (
        len(threshold["cycle_lengths"])
        * len(threshold["epsilon"])
        * len(threshold["delta"])
        == 36
    )
