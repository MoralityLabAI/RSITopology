import copy
import subprocess
from fractions import Fraction
from pathlib import Path

import pytest

import multiletter_tensorization as primary
import verify_independent as independent
from multiletter_tensorization import (
    FROZEN_RESULT_FIELDS,
    FROZEN_METRIC_PROBE_IDS,
    FROZEN_SOURCE_FILES,
    bayes_error_from_joint,
    exact_cell,
    global_only_pathology_control,
    load_json_strict,
    load_manifest,
    live_source_inventory_checks,
    manifest_binding_checks,
    occupancy_success_upper_bound,
    source_commit_binding,
    validate_joint,
    validate_manifest_binding,
)


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "manifest_v0_3.json"


def _set_nested(document, path, value):
    target = document
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def test_frozen_manifest_binds_in_both_paths():
    manifest = load_manifest(MANIFEST_PATH)
    assert all(manifest_binding_checks(manifest).values())
    assert all(independent.manifest_binding_checks(manifest).values())
    assert tuple(row["id"] for row in manifest["metric_robustness_probes"]) == (
        FROZEN_METRIC_PROBE_IDS
    )


def test_replay_command_requires_isolated_mode_and_mutation_fails_both_paths():
    manifest = load_manifest(MANIFEST_PATH)
    expected = "python -I run.py --source-commit <40-hex-source-commit>"
    assert manifest["artifacts"]["replay_command"] == expected
    assert primary.FROZEN_REPLAY_COMMAND == expected
    assert independent.FROZEN_REPLAY_COMMAND == expected

    mutated = copy.deepcopy(manifest)
    mutated["artifacts"]["replay_command"] = expected.replace(" -I", "")
    assert not manifest_binding_checks(mutated)["replay_command_is_exact"]
    assert not independent.manifest_binding_checks(mutated)[
        "replay_command_is_exact"
    ]
    with pytest.raises(ValueError, match="manifest binding failed"):
        validate_manifest_binding(mutated)


@pytest.mark.parametrize(
    ("path", "mutation"),
    (
        (("protocol_id",), "ASMP6-MULTILETTER-TENSORIZATION-v9.9"),
        (("semantics", "message_prior"), "unequal"),
        (("semantics", "message_count"), "K=2"),
        (("semantics", "benign_cover"), "nonuniform"),
        (("semantics", "global_cover_constraint"), "marginals only"),
        (("semantics", "score"), "mutated metric"),
        (("semantics", "product_subclass"), "shared latent product"),
        (("semantics", "decoder"), "decoder receives a key"),
        (("resource_guard", "max_transcript_count"), 124),
        (("write_once_artifacts", "refuse_existing_paths"), False),
        (("conclusion_layer_names",), ["task_result"]),
        (("claim_boundary",), ["unbounded claim"]),
        (("source_freeze", "files"), ["run.py"]),
        (("metric_robustness_probes",), []),
    ),
)
def test_manifest_semantic_mutations_fail_closed_in_both_paths(path, mutation):
    manifest = load_manifest(MANIFEST_PATH)
    mutated = copy.deepcopy(manifest)
    _set_nested(mutated, path, mutation)

    with pytest.raises(ValueError, match="manifest binding failed"):
        validate_manifest_binding(mutated)
    primary_checks = manifest_binding_checks(mutated)
    independent_checks = independent.manifest_binding_checks(mutated)
    assert not primary_checks["canonical_manifest_hash_is_frozen"]
    assert len([passed for passed in primary_checks.values() if not passed]) >= 2
    assert not independent_checks["canonical_manifest_hash_is_frozen"]
    assert len([passed for passed in independent_checks.values() if not passed]) >= 2


def test_grid_shrink_probe_id_mutation_and_unexpected_field_fail_closed():
    manifest = load_manifest(MANIFEST_PATH)
    variants = []

    shrunk = copy.deepcopy(manifest)
    shrunk["grid"]["registered_cells"].pop()
    variants.append(shrunk)

    probe_mutation = copy.deepcopy(manifest)
    probe_mutation["metric_robustness_probes"][0]["id"] = "P1_renamed"
    variants.append(probe_mutation)

    extended = copy.deepcopy(manifest)
    extended["unexpected_semantic_extension"] = True
    variants.append(extended)

    for variant in variants:
        with pytest.raises(ValueError, match="manifest binding failed"):
            validate_manifest_binding(variant)
        assert not all(independent.manifest_binding_checks(variant).values())


@pytest.mark.parametrize(
    "payload",
    (
        '{"a": 1, "a": 2}',
        '{"a": 1.0}',
        '{"a": 1e0}',
        '{"a": NaN}',
        '{"a": Infinity}',
    ),
)
def test_strict_json_rejects_duplicates_floats_numeric_aliases_and_nonfinite(
    tmp_path, payload
):
    path = tmp_path / "bad.json"
    path.write_text(payload, encoding="utf-8")
    with pytest.raises(ValueError):
        load_json_strict(path)
    with pytest.raises(ValueError):
        independent.load_json_strict(path)


def test_exact_occupancy_dp_on_nonregistered_microproblem():
    # K=3,M=5 is intentionally outside the scientific grid. r=2 gives
    # error 2*(3-2)/(3*5)=2/15 and success 13/15.
    assert occupancy_success_upper_bound(3, 5) == Fraction(13, 15)


def test_n1_control_reproduces_v02_without_running_the_grid():
    cell = exact_cell(3, 1)
    assert cell["message_count"] == 2
    assert cell["transcript_count"] == 3
    assert cell["unrestricted"]["bayes_error"] == "1/6"
    assert cell["product_memoryless"]["bayes_error"] == "1/6"
    assert not cell["comparison"]["strict_unrestricted_advantage"]


def test_global_only_pathology_is_informative_but_not_full_per_message_cover():
    record = global_only_pathology_control()
    assert record["global_transcript_cover_exact"]
    assert record["every_message_coordinate_marginal_is_uniform"]
    assert record["carries_information"]
    assert record["bayes_error"] == "1/2"
    assert record["blind_uniform_error"] == "3/4"
    assert not record["full_per_message_transcript_cover"]


def test_marginal_only_false_positive_is_rejected_by_full_transcript_cover():
    # Every conditional row has uniform single-coordinate marginals, but the
    # averaged law concentrates on 00 and 11 instead of the four transcripts.
    marginal_only = (
        ("1/8", "0/1", "0/1", "1/8"),
        ("1/8", "0/1", "0/1", "1/8"),
        ("1/8", "0/1", "0/1", "1/8"),
        ("1/8", "0/1", "0/1", "1/8"),
    )
    with pytest.raises(ValueError, match="global transcript cover"):
        validate_joint(marginal_only, 4, 4)


@pytest.mark.parametrize(
    "joint",
    (
        (("1/2", "0/1"),),
        (("1/2",), ("0/1",)),
        (("1/2", "0/1"), ("-1/4", "3/4")),
        ((0.5, 0), (0, 0.5)),
        (("1/2", "0/1"), ("1/2", "0/1")),
    ),
)
def test_joint_dimension_probability_and_exactness_mutations_are_rejected(joint):
    with pytest.raises((TypeError, ValueError)):
        validate_joint(joint, 2, 2)


def test_bayes_score_rejects_ragged_dimension_instead_of_silent_zip():
    with pytest.raises(ValueError, match="equal lengths"):
        bayes_error_from_joint((("1/2", "0/1"), ("0/1",)))


@pytest.mark.parametrize(
    "writer", (primary.write_once_json, independent.write_once_json)
)
def test_write_once_artifact_refuses_overwrite_in_both_paths(tmp_path, writer):
    output = tmp_path / "new" / "nested" / "result.json"
    writer(output, {"status": "first"})
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        writer(output, {"status": "second"})
    assert output.read_bytes() == original


@pytest.mark.parametrize(
    ("writer", "module"),
    (
        (primary.write_once_json, primary),
        (independent.write_once_json, independent),
    ),
)
def test_write_once_rejects_reparse_ancestor_in_both_paths(
    tmp_path, monkeypatch, writer, module
):
    real_parent = tmp_path / "real-artifacts"
    (real_parent / "nested").mkdir(parents=True)
    linked_parent = tmp_path / "linked-artifacts"
    try:
        linked_parent.symlink_to(real_parent, target_is_directory=True)
    except (NotImplementedError, OSError):
        linked_parent.mkdir()
        (linked_parent / "nested").mkdir()
        original = module._is_reparse_point
        monkeypatch.setattr(
            module,
            "_is_reparse_point",
            lambda path: path == linked_parent or original(path),
        )

    output = linked_parent / "nested" / "result.json"
    with pytest.raises(ValueError, match="reparse point"):
        writer(output, {"status": "must-not-write"})
    assert not (real_parent / "nested" / "result.json").exists()
    assert not output.exists()


@pytest.mark.parametrize(
    ("writer", "module"),
    (
        (primary.write_once_json, primary),
        (independent.write_once_json, independent),
    ),
)
def test_write_once_rejects_reparse_output_in_both_paths(
    tmp_path, monkeypatch, writer, module
):
    target = tmp_path / "existing-evidence.json"
    target.write_text("preserve\n", encoding="utf-8")
    output = tmp_path / "result.json"
    try:
        output.symlink_to(target)
    except (NotImplementedError, OSError):
        output.write_text("link stand-in\n", encoding="utf-8")
        original = module._is_reparse_point
        monkeypatch.setattr(
            module,
            "_is_reparse_point",
            lambda path: path == output or original(path),
        )

    with pytest.raises(ValueError, match="reparse point"):
        writer(output, {"status": "must-not-write"})
    assert target.read_text(encoding="utf-8") == "preserve\n"


@pytest.mark.parametrize(
    "writer", (primary.write_once_json, independent.write_once_json)
)
def test_write_once_rejects_non_directory_parent_in_both_paths(tmp_path, writer):
    blocked_parent = tmp_path / "not-a-directory"
    blocked_parent.write_text("preserve\n", encoding="utf-8")
    output = blocked_parent / "result.json"
    with pytest.raises(NotADirectoryError, match="not a directory"):
        writer(output, {"status": "must-not-write"})
    assert blocked_parent.read_text(encoding="utf-8") == "preserve\n"


def _materialize_source_inventory(directory: Path) -> None:
    for filename in FROZEN_SOURCE_FILES:
        (directory / filename).write_text("source\n", encoding="utf-8")


@pytest.mark.parametrize(
    "unexpected_name",
    ("json.py", "fractions.py", "subprocess.py", "argparse.py", "__pycache__"),
)
def test_shadow_candidates_and_unexpected_live_entries_fail_closed(
    tmp_path, unexpected_name
):
    _materialize_source_inventory(tmp_path)
    assert live_source_inventory_checks(tmp_path)["pass"]
    assert independent.live_source_inventory_checks(tmp_path)["pass"]
    unexpected = tmp_path / unexpected_name
    if unexpected_name == "__pycache__":
        unexpected.mkdir()
    else:
        unexpected.write_text("raise RuntimeError('shadow')\n", encoding="utf-8")
    assert not live_source_inventory_checks(tmp_path)["pass"]
    assert unexpected_name in live_source_inventory_checks(tmp_path)["unexpected"]
    assert not independent.live_source_inventory_checks(tmp_path)["pass"]


def test_reparse_detection_fails_closed_in_both_inventory_paths(tmp_path, monkeypatch):
    _materialize_source_inventory(tmp_path)
    target = tmp_path / FROZEN_SOURCE_FILES[0]
    original_primary = __import__("multiletter_tensorization")._is_reparse_point
    original_independent = independent._is_reparse_point
    monkeypatch.setattr(
        "multiletter_tensorization._is_reparse_point",
        lambda path: path == target or original_primary(path),
    )
    monkeypatch.setattr(
        independent,
        "_is_reparse_point",
        lambda path: path == target or original_independent(path),
    )
    assert FROZEN_SOURCE_FILES[0] in live_source_inventory_checks(tmp_path)[
        "invalid_source_entries"
    ]
    assert FROZEN_SOURCE_FILES[0] in independent.live_source_inventory_checks(
        tmp_path
    )["invalid_source_entries"]


@pytest.mark.parametrize("entrypoint", ("run.py", "verify_independent.py"))
def test_scientific_entrypoints_reject_nonisolated_launch_before_import(entrypoint):
    completed = subprocess.run(
        [__import__("sys").executable, str(HERE / entrypoint), "--help"],
        cwd=HERE,
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "refusing unsafe launch before imports" in (
        completed.stdout + completed.stderr
    )


@pytest.mark.parametrize("entrypoint", ("run.py", "verify_independent.py"))
def test_scientific_entrypoint_help_succeeds_in_isolated_mode(entrypoint):
    completed = subprocess.run(
        [__import__("sys").executable, "-I", str(HERE / entrypoint), "--help"],
        cwd=HERE,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr


def _valid_primary_result_shell():
    result = {field: {} for field in FROZEN_RESULT_FIELDS}
    result.update(
        {
            "schema_version": "asmp6_multiletter_tensorization_result_v0_3",
            "protocol_id": independent.FROZEN_PROTOCOL_ID,
            "manifest_sha256": independent.FROZEN_MANIFEST_CANONICAL_SHA256,
            "status": "complete",
            "stop_reason": "registered_grid_complete",
            "source_binding": {"source_commit": "a" * 40},
            "gates": {name: True for name in independent.EXPECTED_PRIMARY_GATES},
            "conclusion_layers": dict(independent.EXPECTED_PREVERIFICATION_LAYERS),
            "claim_boundary": list(independent.FROZEN_CLAIM_BOUNDARY),
        }
    )
    return result


def test_result_conclusion_gate_source_and_schema_mutations_fail_specific_checks():
    baseline = _valid_primary_result_shell()
    assert all(independent.primary_result_semantic_checks(baseline).values())

    layer_mutation = copy.deepcopy(baseline)
    layer_mutation["conclusion_layers"]["claim_support"] = "promoted_early"
    assert not independent.primary_result_semantic_checks(layer_mutation)[
        "preverification_layers_are_exact"
    ]

    gate_mutation = copy.deepcopy(baseline)
    gate_mutation["gates"]["G6_five_metric_robustness_probes"] = False
    assert not independent.primary_result_semantic_checks(gate_mutation)[
        "primary_gates_are_exact_and_true"
    ]

    source_mutation = copy.deepcopy(baseline)
    source_mutation["source_binding"]["source_commit"] = "short"
    assert not independent.primary_result_semantic_checks(source_mutation)[
        "source_binding_shape_is_valid"
    ]

    schema_mutation = copy.deepcopy(baseline)
    schema_mutation["unexpected"] = True
    assert not independent.primary_result_semantic_checks(schema_mutation)[
        "result_fields_are_exact"
    ]


def test_independent_gate_evidence_channels_are_distinct_and_mutation_sensitive():
    certificate = independent.independent_occupancy_certificate(4, 9)
    assert certificate["pass"]
    assert certificate["marginal_gain_success"] == "11/12"
    assert certificate["exchange_violations"] == []

    cell = independent.independent_cell(6, 2)  # outside the registered grid
    assert independent.replay_reported_joint_cells([cell]) == []
    assert independent.replay_reported_product_formulas([cell]) == []

    joint_mutation = copy.deepcopy(cell)
    joint_mutation["unrestricted"]["joint_mass"][0][0] = "0/1"
    assert independent.replay_reported_joint_cells([joint_mutation])

    product_mutation = copy.deepcopy(cell)
    product_mutation["product_memoryless"]["tensor_formula_error"] = "1/2"
    assert independent.replay_reported_joint_cells([product_mutation]) == []
    assert independent.replay_reported_product_formulas([product_mutation])


def test_real_repo_root_relative_source_binding_after_source_commit():
    """Exercise the real Git chain once this source candidate is committed.

    Before the source-freeze commit exists, skipping is the only valid state:
    the scientific runner must not accept an uncommitted package.
    """

    repo_root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=HERE,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    ).resolve()
    relative_manifest = (HERE.relative_to(repo_root) / "manifest_v0_3.json").as_posix()
    source_commit = subprocess.run(
        [
            "git",
            "log",
            "-1",
            "--format=%H",
            "--diff-filter=A",
            "--",
            relative_manifest,
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not source_commit:
        pytest.skip("source-freeze commit does not exist yet")

    primary = source_commit_binding(source_commit)
    replay = independent.replay_source_binding(source_commit)
    assert primary == replay
    assert primary["source_commit_type"] == "commit"
    assert primary["source_commit_is_ancestor_of_head"]
    assert tuple(sorted(primary["source_files"])) == FROZEN_SOURCE_FILES
