from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import random
import sys


ROOT = Path(__file__).resolve().parents[1]
HERE = (
    ROOT
    / "ultra-experiments"
    / "millennium"
    / "asmp9_reward_gauge_census"
    / "measurement_channel_v0_35"
)

spec = importlib.util.spec_from_file_location(
    "asmp9_monotone_ruler", HERE / "monotone_ruler.py"
)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

design_spec = importlib.util.spec_from_file_location(
    "asmp9_measurement_design", HERE / "pilot_design_v035.py"
)
assert design_spec and design_spec.loader
design = importlib.util.module_from_spec(design_spec)
design_spec.loader.exec_module(design)

analyzer_spec = importlib.util.spec_from_file_location(
    "asmp9_measurement_analyzer", HERE / "pilot_analyzer_v035.py"
)
assert analyzer_spec and analyzer_spec.loader
sys_path_added = str(HERE)
if sys_path_added not in sys.path:
    sys.path.insert(0, sys_path_added)
analyzer = importlib.util.module_from_spec(analyzer_spec)
analyzer_spec.loader.exec_module(analyzer)


def test_exact_radius_and_witness_on_known_sequences() -> None:
    assert module.monotone_linf_radius([3, 2, 1]) == 0
    assert module.monotone_linf_radius([1, 3]) == 1
    assert module.monotone_linf_witness([1, 3]) == (2, 2)
    assert module.robust_zero_crossing([0.5, -0.5], 0.25)
    assert not module.robust_zero_crossing([0.1, -0.5], 0.25)


def test_constructed_witness_attains_radius_on_seeded_random_curves() -> None:
    rng = random.Random(3509)
    for length in range(2, 10):
        for _ in range(100):
            curve = [rng.uniform(-2, 2) for _ in range(length)]
            radius = module.monotone_linf_radius(curve)
            witness = module.monotone_linf_witness(curve)
            assert all(
                witness[i] >= witness[i + 1]
                for i in range(len(witness) - 1)
            )
            assert max(abs(a - b) for a, b in zip(curve, witness)) <= (
                radius + 1e-12
            )


def test_v035_draft_keeps_confirmation_and_old_holdout_closed() -> None:
    protocol = json.loads(
        (HERE / "PILOT_PROTOCOL_DRAFT_v0_35.json").read_text(encoding="utf-8")
    )
    assert protocol["status"] == "draft_not_registered_not_run"
    assert protocol["data_separation"]["confirmation"] == "not_authorized"
    assert (
        protocol["data_separation"]["v0_34_future_holdout"]
        == "remains_unexecuted_and_ineligible"
    )
    assert [gate["gate"] for gate in protocol["fixed_sequence_gates"]] == [
        "C0",
        "D0",
        "M0",
        "J0",
    ]


def test_v035_has_no_new_invariant_or_post_hoc_radius() -> None:
    protocol = json.loads(
        (HERE / "PILOT_PROTOCOL_DRAFT_v0_35.json").read_text(encoding="utf-8")
    )
    assert protocol["derived_instrument_radius"]["post_hoc_override"] is False
    source = json.dumps(protocol)
    assert "holonomy" not in source.lower()
    assert "new invariant" not in source.lower()


def test_retrospective_result_has_exact_expected_boundary() -> None:
    result = json.loads(
        (HERE / "REPAIR_RADIUS_RESULT_v0_35.json").read_text(encoding="utf-8")
    )
    assert result["decision"] == "v0_34_prompt_ruler_not_admissible"
    assert result["standard_gambles"]["summary"]["robust_zero_crossings"] == 4
    assert (
        result["standard_gambles"]["preferred_basis_summary"][
            "robust_zero_crossings"
        ]
        == 2
    )
    assert result["compound_gambles"]["summary"]["robust_zero_crossings"] == 10
    assert result["input"]["outcomes_previously_consumed"] is True


def test_draft_manifest_is_complete_disjoint_and_not_executable() -> None:
    manifest = design.build_manifest()
    assert manifest["unique_prompt_rows"] == 2412
    assert manifest["planned_receipts"] == 4824
    assert manifest["execution_authorized"] is False
    assert manifest["outcomes_consumed"] is False
    assert set(manifest["families"]) == {
        "pilot_commission",
        "pilot_engineer",
        "pilot_resident",
    }
    assert "0" in manifest["probability_grid"]
    assert "1" in manifest["probability_grid"]
    assert len({row["row_id"] for row in manifest["rows"]}) == 2412
    assert not any("holdout_" in row["family_id"] for row in manifest["rows"])


def test_every_content_has_complete_position_code_factorial() -> None:
    manifest = design.build_manifest()
    grouped: dict[tuple[str, str, str], set[tuple[str, str]]] = {}
    for row in manifest["rows"]:
        key = (row["family_id"], row["query_type"], row["content_id"])
        grouped.setdefault(key, set()).add(
            (row["presentation_order"], row["code_mapping"])
        )
    expected = {
        ("target_first", "natural"),
        ("target_first", "reverse"),
        ("target_second", "natural"),
        ("target_second", "reverse"),
    }
    assert grouped
    assert all(cells == expected for cells in grouped.values())


def test_design_receipt_matches_deterministic_manifest() -> None:
    manifest = design.build_manifest()
    receipt = json.loads(
        (HERE / "DESIGN_RECEIPT_v0_35.json").read_text(encoding="utf-8")
    )
    assert receipt["manifest_content_sha256"] == (
        manifest["manifest_content_sha256"]
    )
    assert receipt["counts"]["unique_prompt_rows"] == len(manifest["rows"])
    assert receipt["counts"]["planned_receipts"] == 2 * len(manifest["rows"])
    assert receipt["separation"]["v0_35_model_queries_executed"] is False


def synthetic_records(
    manifest: dict[str, object],
    *,
    bad_code: bool = False,
    bad_curve: bool = False,
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in manifest["rows"]:
        query_type = row["query_type"]
        if query_type == "code_mapping_control":
            semantic = -0.1 if bad_code else 1.0
        elif query_type == "semantic_equality_control":
            semantic = 0.0
        elif query_type in {
            "probability_order_control",
            "anchor_dominance_control",
        }:
            semantic = 0.75
        elif query_type in {"standard_gamble", "compound_gamble"}:
            probability = float(Fraction(str(row["anchor_probability"])))
            semantic = 0.5 - probability
            if (
                bad_curve
                and query_type == "standard_gamble"
                and row["family_id"] == "pilot_commission"
                and row["cell_id"] == "cell_00"
                and row["anchor_probability"] == "1/2"
            ):
                semantic = 1.0
        else:
            raise AssertionError(query_type)
        position = 0.1 if row["presentation_order"] == "target_first" else -0.1
        code = 0.05 if row["code_mapping"] == "natural" else -0.05
        value = semantic + position + code
        for epoch in (0, 1):
            records.append(
                {
                    "row_id": row["row_id"],
                    "planned_epoch": epoch,
                    "target_log_odds": value,
                }
            )
    return records


def test_total_evaluator_passes_planted_factorial_ruler() -> None:
    manifest = design.build_manifest()
    result = analyzer.evaluate(manifest, synthetic_records(manifest))
    assert result["status"] == (
        "measurement_channel_admitted_for_successor_design_only"
    )
    assert [gate["decision"] for gate in result["gates"]] == [
        "pass",
        "pass",
        "pass",
        "pass",
    ]
    assert result["instrument_radius"]["total"] < 1e-12


def test_total_evaluator_stops_on_bad_code_without_downstream_adjudication() -> None:
    manifest = design.build_manifest()
    result = analyzer.evaluate(
        manifest, synthetic_records(manifest, bad_code=True)
    )
    assert [gate["decision"] for gate in result["gates"]] == [
        "fail",
        "not_evaluated",
        "not_evaluated",
        "not_evaluated",
    ]


def test_total_evaluator_stops_on_nonmonotone_curve() -> None:
    manifest = design.build_manifest()
    result = analyzer.evaluate(
        manifest, synthetic_records(manifest, bad_curve=True)
    )
    assert [gate["decision"] for gate in result["gates"]] == [
        "pass",
        "pass",
        "fail",
        "not_evaluated",
    ]
