from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_external_reproduction():
    source = (
        Path(__file__).resolve().parents[1]
        / "artifacts"
        / "external_fable_files7"
        / "holonomy_from_spec_repro.py"
    )
    spec = importlib.util.spec_from_file_location("holonomy_from_spec_repro", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load external from-spec reproduction")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_independent_prose_specification_reproduces_headline_control() -> None:
    reproduction = _load_external_reproduction()
    flat = reproduction.loop(reproduction.B_flat)
    curved = reproduction.loop(reproduction.B_curv)

    assert abs(flat["det"] - 1.0) < 1e-12
    assert abs(curved["det"] - 1.0) < 1e-12
    assert abs(flat["angle"]) < 1e-10
    assert abs(curved["angle"] - (-62.17264500317497)) < 1e-9
    assert abs(curved["signed_return"] - 0.46680891687574333) < 1e-12
    assert abs(
        flat["min_edge_worst_direction_retention"]
        - curved["min_edge_worst_direction_retention"]
    ) < 1e-12
    assert abs(flat["min_edge_worst_direction_retention"] - 0.9900332889206206) < 1e-12
    assert abs(flat["mean_edge_chordal"] - 0.9925706435134696) < 1e-12
    assert abs(curved["mean_edge_chordal"] - 0.9946919820036424) < 1e-12

