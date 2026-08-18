import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def protocol() -> dict:
    return json.loads(
        (HERE / "protocol_v0_19_2.json").read_text(encoding="utf-8")
    )


def test_v0_19_2_has_total_gate_schema_and_unchanged_caps() -> None:
    value = protocol()
    assert value["version"] == "0.19.2"
    assert len(value["gate_ids"]) == len(set(value["gate_ids"])) == 10
    assert value["resource_caps"] == {
        "gpu_allowed": False,
        "peak_resident_bytes": 1073741824,
        "wall_seconds": 180,
    }
    assert "ASMP-9 resolution" in value["claim_boundary"]


def test_v0_19_2_fresh_epsilons_are_outside_burned_set() -> None:
    value = protocol()
    burned = {
        Fraction(item)
        for item in value["development_registry"][
            "burned_epsilon_values"
        ]
    }
    sections = (
        value["factorization_cells"],
        value["dp_cells"],
        value["comparator_cells"],
        {"global": value["global_edge_census"]},
    )
    fresh = {
        Fraction(raw["epsilon"])
        for section in sections
        for raw in section.values()
    }
    assert fresh == {Fraction(8, 27), Fraction(6, 23), Fraction(7, 26)}
    assert fresh.isdisjoint(burned)


def test_v0_19_2_dimensions_and_non_narrower_quad() -> None:
    value = protocol()
    for raw in value["factorization_cells"].values():
        edge_count = sum(raw["cycle_lengths"]) + raw["bridge_count"]
        if "counts" in raw:
            assert len(raw["counts"]) == edge_count
        else:
            assert len(raw["counts_a"]) == edge_count
            assert len(raw["counts_b"]) == edge_count
            assert all(len(row) == edge_count for row in raw["label_vectors"])
    for section in ("dp_cells", "comparator_cells"):
        for raw in value[section].values():
            assert raw["total_budget"] >= (
                sum(raw["cycle_lengths"]) + raw["bridge_count"]
            )
    quad = value["dp_cells"]["fresh_19_2_quad_5_8_10_12"]
    assert sum(quad["cycle_lengths"]) > sum((4, 6, 8, 11))
    assert max(quad["cycle_lengths"]) > 11
