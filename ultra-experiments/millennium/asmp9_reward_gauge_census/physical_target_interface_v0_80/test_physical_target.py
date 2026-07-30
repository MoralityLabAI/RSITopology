from __future__ import annotations

import json
from pathlib import Path

from physical_target import (
    NON_GAUGE_DELTA,
    SHAPING_DELTA,
    build_candidates,
    choice_probability,
    exact_wellposedness,
    record_seed,
    route_margin,
    squared_norm,
)


ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "config_v0_80.json").read_text(encoding="utf-8"))


def test_shaping_and_nongauge_deltas_have_exact_matched_norm() -> None:
    assert squared_norm(SHAPING_DELTA) == squared_norm(NON_GAUGE_DELTA) == 2


def test_shaping_preserves_and_nongauge_changes_route_margin() -> None:
    assert route_margin(SHAPING_DELTA) == 0
    assert route_margin(NON_GAUGE_DELTA) == 2
    assert exact_wellposedness(CONFIG)["pass"]


def test_candidate_registry_is_complete() -> None:
    candidates = build_candidates(CONFIG)
    assert len(candidates) == 20
    assert {candidate.split for candidate in candidates} == {
        "construction",
        "holdout",
    }
    assert {candidate.arm for candidate in candidates} == {
        "base",
        "shape_plus",
        "shape_minus",
        "nongauge_plus",
        "nongauge_minus",
    }


def test_population_response_depends_only_on_target_margin() -> None:
    candidates = build_candidates(CONFIG)
    for context in {candidate.context for candidate in candidates}:
        local = {candidate.arm: candidate for candidate in candidates if candidate.context == context}
        beta = 1.0
        assert choice_probability(local["base"].target_margin, beta) == choice_probability(
            local["shape_plus"].target_margin, beta
        )
        assert choice_probability(local["base"].target_margin, beta) == choice_probability(
            local["shape_minus"].target_margin, beta
        )


def test_seed_derivation_is_stable_and_candidate_specific() -> None:
    first = record_seed(8001, "a")
    assert first == record_seed(8001, "a")
    assert first != record_seed(8001, "b")
    assert first != record_seed(8002, "a")
