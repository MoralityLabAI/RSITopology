from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def test_registries_are_disjoint_from_v016_attempt() -> None:
    protocol = json.loads(
        (HERE / "protocol_v0_16_1.json").read_text(encoding="utf-8")
    )
    assert set(protocol["pair_registry"]["epsilon"]).isdisjoint(
        {"1/32", "3/16", "5/16", "11/24"}
    )
    assert set(protocol["pair_registry"]["a"]).isdisjoint({7, 9, 12})
    assert set(protocol["pair_registry"]["differences"]).isdisjoint(
        {8, 11, 15}
    )
    assert set(
        protocol["global_allocation_registry"]["extra_total_trials"]
    ).isdisjoint({11, 13, 15, 17})
    assert set(protocol["compact_value_registry"]["cycle_lengths"]).isdisjoint(
        {12, 14}
    )
    assert set(protocol["threshold_registry"]["cycle_lengths"]).isdisjoint(
        {12, 14, 17}
    )


def test_resource_cap_is_not_relaxed() -> None:
    current = json.loads(
        (HERE / "protocol_v0_16_1.json").read_text(encoding="utf-8")
    )
    previous = json.loads(
        (
            HERE.parent
            / "balanced_design_v0_16"
            / "protocol_v0_16.json"
        ).read_text(encoding="utf-8")
    )
    assert current["resource_caps"] == previous["resource_caps"]


def test_gate_universe_is_unchanged() -> None:
    current = json.loads(
        (HERE / "protocol_v0_16_1.json").read_text(encoding="utf-8")
    )
    previous = json.loads(
        (
            HERE.parent
            / "balanced_design_v0_16"
            / "protocol_v0_16.json"
        ).read_text(encoding="utf-8")
    )
    assert current["gate_ids"] == previous["gate_ids"]


def test_frozen_cell_counts() -> None:
    protocol = json.loads(
        (HERE / "protocol_v0_16_1.json").read_text(encoding="utf-8")
    )
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
