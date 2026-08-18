from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_protocol() -> dict:
    return json.loads(
        (HERE / "protocol_v0_25.json").read_text(encoding="utf-8")
    )


def test_gate_universe_is_unique_and_total() -> None:
    protocol = load_protocol()
    gates = protocol["gate_ids"]
    assert len(gates) == len(set(gates)) == 9
    assert gates[0] == "G0_registration_binding"
    assert gates[-1] == "G8_resource_and_scope"


def test_fresh_optimizer_cells_do_not_match_burned_cells() -> None:
    protocol = load_protocol()
    burned = {
        (
            tuple(cell["path_lengths"]),
            cell["total_budget"],
        )
        for cell in protocol["freshness_rule"]["burned_cells"]
    }
    fresh = {
        (
            tuple(cell["path_lengths"]),
            cell["total_budget"],
        )
        for cell in protocol["fresh_validation"]["optimizer_cells"]
    }
    assert not (burned & fresh)


def test_all_registered_graphs_are_overlapping_cycle_theta_blocks() -> None:
    protocol = load_protocol()
    cells = (
        protocol["fresh_validation"]["formula_cells"]
        + protocol["fresh_validation"]["optimizer_cells"]
    )
    for cell in cells:
        lengths = cell["path_lengths"]
        assert len(lengths) >= 3
        assert all(length >= 1 for length in lengths)
        assert lengths.count(1) <= 1


def test_claim_boundary_forbids_resolution_and_novelty_overclaim() -> None:
    protocol = load_protocol()
    forbidden = "\n".join(protocol["structured_claims"]["forbidden"])
    assert "ASMP-9 is resolved" in forbidden
    assert "is new" in forbidden
    assert "no novelty claim" in protocol["claim_boundary"]


def test_resources_are_cpu_only_and_bounded() -> None:
    caps = load_protocol()["resource_caps"]
    assert caps["gpu_allowed"] is False
    assert 0 < caps["wall_seconds"] <= 180
    assert 0 < caps["peak_resident_bytes"] <= 2**30
