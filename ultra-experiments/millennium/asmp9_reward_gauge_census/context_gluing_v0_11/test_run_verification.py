from __future__ import annotations

import json
from math import comb
from pathlib import Path

from run_verification import peak_resident_bytes


HERE = Path(__file__).resolve().parent


def test_machine_protocol_counts_are_derived() -> None:
    protocol = json.loads((HERE / "protocol_v0_11.json").read_text(encoding="utf-8"))
    census = protocol["tuple_census"]
    expected = 2 ** (census["context_count"] * comb(census["item_count"], 2))
    assert census["expected_tuple_count"] == expected
    assert census["maximum_tuple_count"] == expected
    maximum_mixed_rank = (census["context_count"] - 1) * (census["item_count"] - 1)
    assert census["expected_mixed_ranks"] == list(range(maximum_mixed_rank + 1))


def test_gate_and_status_universes_are_unique() -> None:
    protocol = json.loads((HERE / "protocol_v0_11.json").read_text(encoding="utf-8"))
    assert len(protocol["gate_ids"]) == len(set(protocol["gate_ids"])) == 10
    assert (
        len(protocol["allowed_statuses"]) == len(set(protocol["allowed_statuses"])) == 4
    )


def test_peak_resident_measurement_is_live() -> None:
    assert peak_resident_bytes() > 0
