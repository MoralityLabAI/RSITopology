from __future__ import annotations

import json
from fractions import Fraction
from math import comb
from pathlib import Path

import build_registration
import crossover_frontier as primary
import run
import verify_result as independent


ROOT = Path(__file__).resolve().parent


def test_full_draft_grid_has_48_covering_cells() -> None:
    count = sum(
        len(primary.intermediate_widths(n, k))
        for n in (13, 15, 17)
        for k in (3, 4)
    )
    assert count == 48
    assert primary.intermediate_widths(13, 3) == (4, 5, 6, 7, 8, 9)
    assert primary.intermediate_widths(13, 4) == (5, 6, 7, 8, 9, 10)


def test_deterministic_incumbent_and_replayable_bounds() -> None:
    first = primary.deterministic_cover_bounds(
        7,
        4,
        3,
        max_greedy_rounds=100,
        max_candidate_blocks=1000,
    )
    second = primary.deterministic_cover_bounds(
        7,
        4,
        3,
        max_greedy_rounds=100,
        max_candidate_blocks=1000,
    )
    assert first == second
    assert primary.verify_cover(7, 4, 3, first.selected_blocks)
    replay = primary.replayable_lower_bound(7, 4, 3)
    assert first.lower_bound == replay["certified_lower_bound"]
    assert first.lower_bound <= first.upper_bound


def test_resource_stop_keeps_valid_incumbent_and_does_not_claim_optimum() -> None:
    stopped = primary.deterministic_cover_bounds(
        6,
        3,
        2,
        max_greedy_rounds=0,
        max_candidate_blocks=1000,
    )
    assert stopped.stop_reason == "deterministic_round_cap"
    assert stopped.construction_status == "bounded_stop_with_trivial_incumbent"
    assert stopped.upper_bound == comb(6, 3)
    assert primary.verify_cover(6, 3, 2, stopped.selected_blocks)
    assert not stopped.optimum_certified
    assert stopped.lower_bound < stopped.upper_bound


def test_exact_probability_reproduces_sealed_v02_costs() -> None:
    cases = (
        (4, Fraction(1, 20), 60),
        (5, Fraction(1, 4), 285),
        (comb(13, 3), Fraction(1, 20), 6292),
    )
    for query_count, flip_rate, expected_total in cases:
        design = primary.find_exact_design(
            query_count,
            flip_rate,
            Fraction(1, 20),
            Fraction(9, 10),
            4096,
        )
        assert design is not None
        assert design.total_samples == expected_total
        assert design.familywise_error_upper <= Fraction(1, 20)
        assert design.signal_power_lower >= Fraction(9, 10)


def test_all_three_bound_aware_classifications_are_live() -> None:
    args = (
        10,
        Fraction(1, 20),
        Fraction(1, 20),
        Fraction(9, 10),
        4096,
    )
    certified = primary.classify_cost_interval(1, 1, *args)
    impossible = primary.classify_cost_interval(10, 10, *args)
    unresolved = primary.classify_cost_interval(1, 10, *args)
    assert certified.status == primary.STATUS_CERTIFIED
    assert impossible.status == primary.STATUS_IMPOSSIBLE
    assert unresolved.status == primary.STATUS_UNRESOLVED


def test_minimum_width_uses_interval_when_any_smaller_cell_is_unresolved() -> None:
    bracket = primary.build_minimum_width_bracket(
        3,
        (
            {"block_size": 4, "status": primary.STATUS_IMPOSSIBLE},
            {"block_size": 5, "status": primary.STATUS_UNRESOLVED},
            {"block_size": 6, "status": primary.STATUS_CERTIFIED},
        ),
        7,
    )
    assert bracket["s_no"] == 4
    assert bracket["s_yes"] == 6
    assert bracket["s_star"] is None
    assert bracket["unresolved_widths"] == [5]
    assert bracket["interval"] == "(4,6]"

    exact = primary.build_minimum_width_bracket(
        3,
        tuple(
            {"block_size": width, "status": primary.STATUS_IMPOSSIBLE}
            for width in (4, 5, 6)
        ),
        7,
    )
    assert exact["s_star"] == 7
    assert exact["interval"] is None


def test_five_metric_probes_are_nonbinding_and_independently_replay() -> None:
    primary_result = primary.classify_cost_interval(
        2,
        5,
        30,
        Fraction(3, 20),
        Fraction(1, 20),
        Fraction(9, 10),
        4096,
    )
    probes = primary.metric_robustness_probes(
        primary_result,
        30,
        Fraction(3, 20),
        Fraction(1, 20),
        Fraction(9, 10),
        4096,
    )
    assert len(probes) == 5
    assert all(probe["binding"] is False for probe in probes)
    independent_statuses = independent.independent_probe_statuses(
        2,
        5,
        30,
        Fraction(3, 20),
        Fraction(1, 20),
        Fraction(9, 10),
        4096,
    )
    assert {probe["probe_id"]: probe["status"] for probe in probes} == independent_statuses


def test_independent_cover_lower_bound_and_probability_implementations_agree() -> None:
    cover = primary.deterministic_cover_bounds(
        8,
        5,
        3,
        max_greedy_rounds=100,
        max_candidate_blocks=1000,
    )
    assert independent.independent_verify_cover(8, 5, 3, cover.selected_blocks)
    independent_lower = independent.independent_lower_bounds(8, 5, 3)
    assert independent_lower["certified"] == cover.lower_bound
    independent_design = independent.independent_design(
        4,
        Fraction(1, 20),
        Fraction(1, 20),
        Fraction(9, 10),
        4096,
    )
    assert independent_design is not None
    assert independent_design["total_samples"] == 60


def test_manifest_anchor_and_future_registration_source_set_are_complete() -> None:
    manifest = json.loads((ROOT / "experiment_v0_2_1.json").read_text(encoding="utf-8"))
    assert manifest["asmp11"]["status"] == "source_freeze_candidate_not_registered"
    assert manifest["asmp11"]["expected_counts"] == {
        "covering_cells": 48,
        "cost_cells": 144,
        "brackets": 18,
        "metric_probes_per_cost_cell": 5,
    }
    _, checks = run.validate_prior_anchor(ROOT / "prior_anchor_v0_2.json")
    assert all(row["pass"] for row in checks)
    assert all((ROOT / relative).is_file() for relative in build_registration.BOUND_SOURCES)


def test_all_hash_bound_text_writers_emit_lf_bytes(tmp_path: Path) -> None:
    payload = '{\n  "alpha": 1,\n  "beta": 2\n}\n'
    for index, writer in enumerate(
        (run.write_lf_text, build_registration.write_lf_text, independent.write_lf_text)
    ):
        output = tmp_path / f"writer_{index}.json"
        writer(output, payload)
        emitted = output.read_bytes()
        assert emitted == payload.encode("utf-8")
        assert b"\r\n" not in emitted
        assert emitted.endswith(b"\n")


def test_atomic_json_and_jsonl_emit_lf_bytes(tmp_path: Path) -> None:
    json_path = tmp_path / "atomic.json"
    jsonl_path = tmp_path / "rows.jsonl"
    run.atomic_json(json_path, {"nested": {"value": 1}, "rows": [1, 2]})
    run.write_jsonl(jsonl_path, ({"row": 1}, {"row": 2}))
    for output in (json_path, jsonl_path):
        emitted = output.read_bytes()
        assert b"\r\n" not in emitted
        assert emitted.endswith(b"\n")
