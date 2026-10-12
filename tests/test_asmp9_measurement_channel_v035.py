from __future__ import annotations

from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import subprocess
import sys

import pytest


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

runner_spec = importlib.util.spec_from_file_location(
    "asmp9_measurement_runner", HERE / "run_measurement_pilot_v035.py"
)
assert runner_spec and runner_spec.loader
runner = importlib.util.module_from_spec(runner_spec)
runner_spec.loader.exec_module(runner)

preparer_spec = importlib.util.spec_from_file_location(
    "asmp9_measurement_preparer", HERE / "prepare_registration_v035.py"
)
assert preparer_spec and preparer_spec.loader
preparer = importlib.util.module_from_spec(preparer_spec)
preparer_spec.loader.exec_module(preparer)


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


def test_frozen_protocol_preserves_scope_and_matches_design() -> None:
    protocol = json.loads(
        (HERE / "PILOT_PROTOCOL_v0_35.json").read_text(encoding="utf-8")
    )
    manifest = design.build_manifest()
    assert protocol["status"] == (
        "scientific_protocol_frozen_environment_registration_pending"
    )
    assert protocol["data_separation"]["confirmation"] == "not_authorized"
    assert protocol["planned_scale"]["unique_prompt_rows"] == len(
        manifest["rows"]
    )
    assert protocol["planned_scale"]["planned_receipts"] == (
        manifest["planned_receipts"]
    )
    assert [gate["gate"] for gate in protocol["fixed_sequence_gates"]] == [
        "C0",
        "D0",
        "M0",
        "J0",
    ]
    assert protocol["factorial_code_design"]["response_code_mapping"] == [
        "natural_A_for_description_1",
        "reverse_B_for_description_1",
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


def test_design_receipt_file_hashes_are_current() -> None:
    receipt = json.loads(
        (HERE / "DESIGN_RECEIPT_v0_35.json").read_text(encoding="utf-8")
    )
    paths = {
        "pilot_design_v035.py": HERE / "pilot_design_v035.py",
        "PILOT_PROTOCOL_DRAFT_v0_35.json": (
            HERE / "PILOT_PROTOCOL_DRAFT_v0_35.json"
        ),
        "PILOT_PROTOCOL_v0_35.json": HERE / "PILOT_PROTOCOL_v0_35.json",
        "pilot_analyzer_v035.py": HERE / "pilot_analyzer_v035.py",
        "run_measurement_pilot_v035.py": (
            HERE / "run_measurement_pilot_v035.py"
        ),
        "prepare_registration_v035.py": (
            HERE / "prepare_registration_v035.py"
        ),
        "run_prime_asmp9_measurement_v035_guarded.sh": (
            ROOT / "scripts" / "run_prime_asmp9_measurement_v035_guarded.sh"
        ),
        "test_asmp9_measurement_channel_v035.py": Path(__file__).resolve(),
        "source_v0_34_prompt_manifest": (
            HERE.parent
            / "physical_acquisition_v0_34"
            / "burned_pilot_prompt_manifest_v0_34_1.json"
        ),
    }
    assert set(receipt["files"]) == set(paths)
    for name, path in paths.items():
        assert receipt["files"][name] == {
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }


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


def test_live_selection_rejects_draft_and_accepts_only_registered_universe() -> None:
    draft = design.build_manifest()
    with pytest.raises(RuntimeError, match="registered, authorized"):
        runner.selected_rows(draft, "measurement_pilot", 2)

    registered = preparer.registered_manifest("a" * 40)
    assert len(runner.selected_rows(registered, "measurement_pilot", 2)) == 2412
    smoke = runner.selected_rows(registered, "smoke", 1)
    assert len(smoke) == len(runner.QUERY_TYPES)
    assert {row["query_type"] for row in smoke} == set(runner.QUERY_TYPES)


def test_runner_adapter_calls_sealed_request_once_and_rehashes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []

    def fake_request(**kwargs: object) -> dict[str, object]:
        calls.append(dict(kwargs))
        item = dict(kwargs["item"])  # type: ignore[arg-type]
        row = dict(kwargs["row"])  # type: ignore[arg-type]
        assert row["choice_order"] == row["presentation_order"]
        return {
            "schema_version": "old",
            **item,
            "row_id": row["row_id"],
            "query_type": row["query_type"],
            "target_log_odds": 0.25,
            "choice_probabilities": {"A": 0.6, "B": 0.4},
            "record_sha256": "old",
        }

    monkeypatch.setattr(runner, "SEALED_REQUEST_RECORD", fake_request)
    row = preparer.registered_manifest("b" * 40)["rows"][0]
    item = {
        "global_index": 0,
        "planned_epoch": 0,
        "row_index": 0,
        "row_id": row["row_id"],
        "row_sha256": row["row_sha256"],
        "prompt_sha256": row["prompt_sha256"],
        "query_type": row["query_type"],
        "plan_item_sha256": "plan",
    }
    record = runner.request_record(
        base_url="http://127.0.0.1:1",
        item=item,
        row=row,
        server_session=0,
        request_timeout=1.0,
        seed_base=1,
    )
    assert len(calls) == 1
    assert record["schema_version"] == runner.RECORD_SCHEMA
    assert record["presentation_order"] == row["presentation_order"]
    expected = hashlib.sha256(
        runner.sealed_runner.canonical_bytes(
            {
                key: value
                for key, value in record.items()
                if key != "record_sha256"
            }
        )
    ).hexdigest()
    assert record["record_sha256"] == expected


def test_registration_materialization_is_complete_and_compare_or_fail(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "manifest.json"
    registration_path = tmp_path / "registration.json"
    model_path = tmp_path / "model.gguf"
    server_path = tmp_path / "llama-server"
    cuda_path = tmp_path / "libggml-cuda.so"
    model_path.write_bytes(b"model")
    server_path.write_bytes(b"server")
    cuda_path.write_bytes(b"cuda")

    manifest = preparer.registered_manifest("c" * 40)
    preparer.compare_or_fail(manifest_path, manifest)
    registration = preparer.build_registration(
        manifest_path=manifest_path,
        registration_path=registration_path,
        model_path=model_path,
        server_path=server_path,
        cuda_library_path=cuda_path,
        output_dir=tmp_path / "output",
        prepared_utc="2026-07-29T12:00:00Z",
        git_commit="c" * 40,
        git_branch="feat/test",
        pod_id="pod-test",
        provider="test-provider",
        region="test-region",
        gpu_description="test-gpu",
        listed_hourly_usd=0.01,
    )
    assert registration["outcomes_consumed"] is False
    assert registration["manifest"]["content_sha256"] == (
        manifest["manifest_content_sha256"]
    )
    assert registration["phase_authorization"]["confirmation"] == (
        "not_authorized"
    )
    assert registration["resource_caps"]["memory_mb"] == 4096
    assert registration["resource_caps"]["gpu_allowance_mb"] == 1600
    assert registration["implementation"]["hard_cap_wrapper"]["sha256"]
    assert registration["implementation"]["cuda_library"]["sha256"] == (
        hashlib.sha256(b"cuda").hexdigest()
    )
    assert registration["exact_inner_command"][3] == (
        registration_path.resolve().as_posix()
    )
    assert registration["exact_launch_environment"]["REGISTRATION"] == (
        registration_path.resolve().as_posix()
    )
    assert registration["exact_launch_environment"]["OUTPUT_DIR"] == (
        (tmp_path / "output").resolve().as_posix()
    )

    preparer.compare_or_fail(registration_path, registration)
    preparer.compare_or_fail(registration_path, registration)
    changed = dict(registration)
    changed["status"] = "changed"
    with pytest.raises(FileExistsError, match="refusing to replace"):
        preparer.compare_or_fail(registration_path, changed)


def test_hard_cap_wrapper_contains_registered_resource_sentinels() -> None:
    source = (
        ROOT / "scripts" / "run_prime_asmp9_measurement_v035_guarded.sh"
    ).read_text(encoding="utf-8")
    for sentinel in (
        "findmnt -T",
        "MemoryMax=4096M",
        "MemorySwapMax=0",
        "CPUQuota=50%",
        "RuntimeMaxSec=1800",
        "GPU_MEMORY_LIMIT_MB",
        "GPU_TEMPERATURE_LIMIT_C",
        "GPU_CLEAN_START_CEILING_MB",
        "LD_LIBRARY_PATH=/workspace/llama.cpp/build-sm89/bin",
        "ASMP9_V034_HARD_CAP_ACTIVE=${WRAPPER_SHA256}",
        "--execution-class measurement_pilot",
    ):
        assert sentinel in source
    assert 'GPU_MEMORY_LIMIT_MB="${GPU_MEMORY_LIMIT_MB:-' not in source
    assert 'GPU_TEMPERATURE_LIMIT_C="${GPU_TEMPERATURE_LIMIT_C:-' not in source


def test_registered_capture_analysis_path_is_hash_bound_end_to_end(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "manifest.json"
    registration_path = tmp_path / "registration.json"
    model_path = tmp_path / "model.gguf"
    server_path = tmp_path / "llama-server"
    cuda_path = tmp_path / "libggml-cuda.so"
    output_dir = tmp_path / "capture"
    output_dir.mkdir()
    for path, data in (
        (model_path, b"model"),
        (server_path, b"server"),
        (cuda_path, b"cuda"),
    ):
        path.write_bytes(data)

    manifest = preparer.registered_manifest("d" * 40)
    preparer.compare_or_fail(manifest_path, manifest)
    registration = preparer.build_registration(
        manifest_path=manifest_path,
        registration_path=registration_path,
        model_path=model_path,
        server_path=server_path,
        cuda_library_path=cuda_path,
        output_dir=output_dir,
        prepared_utc="2026-07-29T12:00:00Z",
        git_commit="d" * 40,
        git_branch="feat/test",
        pod_id="pod-test",
        provider="test-provider",
        region="test-region",
        gpu_description="test-gpu",
        listed_hourly_usd=0.01,
    )
    preparer.compare_or_fail(registration_path, registration)

    planted = synthetic_records(manifest)
    row_by_id = {row["row_id"]: row for row in manifest["rows"]}
    record_lines: list[bytes] = []
    for global_index, source in enumerate(planted):
        row = row_by_id[source["row_id"]]
        value = float(source["target_log_odds"])
        target_probability = math.exp(value) / (1.0 + math.exp(value))
        target_label = str(row["target_label"])
        comparator_label = str(row["comparator_label"])
        probabilities = {
            target_label: target_probability,
            comparator_label: 1.0 - target_probability,
        }
        record: dict[str, object] = {
            "schema_version": runner.RECORD_SCHEMA,
            "global_index": global_index,
            "planned_epoch": source["planned_epoch"],
            "row_id": row["row_id"],
            "row_sha256": row["row_sha256"],
            "prompt_sha256": row["prompt_sha256"],
            "query_type": row["query_type"],
            "phase": row["phase"],
            "target_label": target_label,
            "comparator_label": comparator_label,
            "choice_probabilities": probabilities,
            "target_log_odds": value,
        }
        record["record_sha256"] = hashlib.sha256(
            analyzer.canonical_bytes(record)
        ).hexdigest()
        record_lines.append(analyzer.canonical_bytes(record))
    records_path = output_dir / "pilot_records.jsonl"
    records_path.write_bytes(b"".join(record_lines))

    summary = {
        "schema_version": runner.SUMMARY_SCHEMA,
        "status": "measurement_pilot_capture_completed",
        "execution_class": "measurement_pilot",
        "counts": {
            "records": len(planted),
            "unique_prompts": manifest["unique_prompt_rows"],
            "planned_epochs": 2,
        },
        "inputs": {
            "registration_sha256": preparer.sha256_file(registration_path),
            "registration_content_sha256": registration[
                "registration_content_sha256"
            ],
        },
    }
    (output_dir / "summary.json").write_bytes(
        analyzer.canonical_bytes(summary)
    )
    result_path = tmp_path / "analysis.json"
    subprocess.run(
        [
            sys.executable,
            str(HERE / "pilot_analyzer_v035.py"),
            "--registration",
            str(registration_path),
            "--output-dir",
            str(output_dir),
            "--output",
            str(result_path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["status"] == (
        "measurement_channel_admitted_for_successor_design_only"
    )
    assert result["inputs"]["registration_sha256"] == (
        preparer.sha256_file(registration_path)
    )
    expected_analysis_hash = hashlib.sha256(
        analyzer.canonical_bytes(
            {
                key: value
                for key, value in result.items()
                if key != "analysis_content_sha256"
            }
        )
    ).hexdigest()
    assert result["analysis_content_sha256"] == expected_analysis_hash
