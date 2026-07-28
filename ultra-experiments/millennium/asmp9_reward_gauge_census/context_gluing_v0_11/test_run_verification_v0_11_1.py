from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def test_repair_preserves_every_scientific_specification() -> None:
    original = json.loads((HERE / "protocol_v0_11.json").read_text(encoding="utf-8"))
    repair = json.loads((HERE / "protocol_v0_11_1.json").read_text(encoding="utf-8"))
    for field in (
        "tuple_census",
        "random_cells",
        "minimality_controls",
        "allowed_statuses",
        "resource_limits",
        "gate_ids",
    ):
        assert repair[field] == original[field]
