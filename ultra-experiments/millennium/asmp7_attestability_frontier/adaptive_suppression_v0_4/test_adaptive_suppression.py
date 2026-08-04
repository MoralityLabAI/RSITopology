from __future__ import annotations

import copy
import math
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

import adaptive_suppression as primary
import run as runner
import verify_independent as verifier


HERE = Path(os.path.abspath(__file__)).parent
MANIFEST_PATH = HERE / "manifest_v0_4.json"

EXPECTED_SOURCE_FILES = (
    "PROTOCOL_v0_4.md",
    "README.md",
    "SOURCE_FREEZE.md",
    "adaptive_suppression.py",
    "manifest_v0_4.json",
    "run.py",
    "test_adaptive_suppression.py",
    "verify_independent.py",
)
EXPECTED_RESULT_FIELDS = {
    "schema_version",
    "protocol_id",
    "manifest_sha256",
    "source_binding",
    "upstream_bindings",
    "resource_observations",
    "status",
    "stop_reason",
    "quotient_rows",
    "registry_rows",
    "oracle_rows",
    "analytic_obligations",
    "controls",
    "gates",
    "metric_robustness",
    "conclusion_layers",
    "claim_boundary",
}
EXPECTED_GATES = (
    "G0_frozen_manifest_binding",
    "G1_exact_source_and_upstream_bindings",
    "G2_complete_72_pair_mask_quotient",
    "G3_complete_48_row_v03_transfer",
    "G4_complete_144_row_monotone_oracle",
    "G5_analytic_induction_and_composite_obligations",
    "G6_scope_breakers_and_simple_limits",
    "G7_five_metric_probe_families",
    "G8_exact_arithmetic_and_resource_envelope",
)
EXPECTED_PROBES = (
    "P1_input_relabeling",
    "P2_timing_sensitivity",
    "P3_terminal_monotonicity",
    "P4_nonmonotone_scope_breaker",
    "P5_upstream_and_simple_limits",
)
EXPECTED_PREVERIFICATION_LAYERS = {
    "metric_robustness": (
        "five_frozen_probe_families_computed_awaiting_independent_replay"
    ),
    "task_result": "finite_causal_endpoint_equivalence_and_v03_minimum_transfer",
    "measurement_reliability": "awaiting_import_independent_verification",
    "claim_support": "pending_independent_verification",
    "operational_decision": (
        "no_deployment_authorization_await_independent_verification"
    ),
}


def _set_nested(document, path, value):
    target = document
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def test_static_source_result_gate_probe_and_layer_universes_are_frozen():
    assert primary.FROZEN_SOURCE_FILES == EXPECTED_SOURCE_FILES
    assert primary.FROZEN_RESULT_FIELDS == EXPECTED_RESULT_FIELDS
    assert primary.FROZEN_PRIMARY_GATES == EXPECTED_GATES
    assert primary.FROZEN_PROBE_IDS == EXPECTED_PROBES
    assert primary.FROZEN_PREVERIFICATION_LAYERS == EXPECTED_PREVERIFICATION_LAYERS


def test_import_independent_verifier_freezes_matching_public_universes():
    assert verifier.FROZEN_SOURCE_FILES == EXPECTED_SOURCE_FILES
    assert verifier.FROZEN_RESULT_FIELDS == EXPECTED_RESULT_FIELDS
    assert verifier.FROZEN_PRIMARY_GATES == EXPECTED_GATES
    assert verifier.FROZEN_PROBE_IDS == EXPECTED_PROBES
    assert verifier.FROZEN_PREVERIFICATION_LAYERS == EXPECTED_PREVERIFICATION_LAYERS
    assert set(verifier.FROZEN_VERIFICATION_FIELDS) == {
        "schema_version",
        "pass",
        "protocol_id",
        "manifest_binding",
        "source_binding_error",
        "source_binding_replay",
        "upstream_binding_checks",
        "result_semantic_checks",
        "quotient_mismatches",
        "registry_mismatches",
        "oracle_mismatches",
        "analytic_obligations",
        "control_mismatches",
        "metric_probe_ids",
        "metric_probes_match",
        "resource_observations_valid",
        "verification_resource_observations",
        "primary_gates_valid",
        "preverification_layers_match",
        "independent_gates",
        "final_conclusion_layers",
        "claim_boundary",
        "bindings",
        "implementation_imported",
    }


def test_independent_verifier_reconstructs_direct_controls():
    controls = verifier.independent_controls(
        quotient_rows_valid=True, registry_rows_valid=True
    )
    metrics = verifier.independent_metric_robustness(
        oracle_rows_valid=True, controls=controls
    )
    assert controls["current_X_anticipatory_timing"] == {
        "causal_compliant_q0": "5/8",
        "causal_forbidden_q1": "3/4",
        "anticipatory_compliant_q0": "3/4",
        "anticipatory_forbidden_q1": "7/16",
        "causal_ordering": True,
        "anticipatory_reversal": True,
        "pass": True,
    }
    assert controls["nonmonotone_h2_exactly_one"]["adaptive_value"] == "5/8"
    assert controls["nonmonotone_h2_exactly_one"]["best_fixed_value"] == "1/2"
    assert tuple(metrics) == EXPECTED_PROBES
    assert all(record["pass"] for record in metrics.values())


def test_nonsymmetric_monotone_terminal_matches_endpoint_in_both_implementations():
    terminal = (0, 0, 1, 1)  # phi(y1,y2)=y1: monotone, not count-symmetric.
    primary_value = primary.generic_full_prefix_bellman_value(
        terminal, 2, 8, 12, Fraction(1), "max"
    )
    independent_value = verifier.iterative_generic_policy_value(
        terminal, 2, 8, 12, Fraction(1), "max"
    )
    endpoint = primary.iid_terminal_table_value(terminal, 2, Fraction(5, 8))
    assert primary_value == independent_value == endpoint == Fraction(5, 8)
    assert len(verifier.antichain_monotone_boolean_terminals(2)) == 6


def test_h3_monotone_terminal_enumerations_match_without_running_action_grid():
    primary_tables = primary.brute_force_monotone_boolean_terminals(3)
    independent_tables = verifier.antichain_monotone_boolean_terminals(3)
    assert len(primary_tables) == len(independent_tables) == 20
    assert set(primary_tables) == set(independent_tables)
    histories = tuple(
        tuple((index >> shift) & 1 for shift in (2, 1, 0))
        for index in range(8)
    )
    nonsymmetric = sum(
        any(
            len(
                {
                    values[index]
                    for index, history in enumerate(histories)
                    if sum(history) == count
                }
            )
            > 1
            for count in range(4)
        )
        for values in primary_tables
    )
    assert nonsymmetric == 15


def test_independent_verifier_uses_type_strict_json_equality():
    assert verifier.strict_json_equal({"value": False}, {"value": False})
    assert not verifier.strict_json_equal(False, 0)
    assert not verifier.strict_json_equal(True, 1)
    assert not verifier.strict_json_equal(
        {"nested": [{"pass": True, "count": 0}]},
        {"nested": [{"pass": 1, "count": False}]},
    )
    expected_controls = verifier.independent_controls(
        quotient_rows_valid=True, registry_rows_valid=True
    )
    tampered = copy.deepcopy(expected_controls)
    tampered["input_relabeling"]["pass"] = 1
    assert verifier.find_control_mismatches(tampered, expected_controls)


def test_independent_randomized_upper_tail_replay_is_exact():
    fp, fn = verifier.randomized_upper_tail_errors(
        1, Fraction(1, 4), Fraction(3, 4), 1, Fraction(1, 5)
    )
    assert fp == Fraction(1, 20)
    assert fn == Fraction(17, 20)


def test_frozen_manifest_binds_before_any_registered_work():
    manifest = primary.load_json_strict(MANIFEST_PATH)
    checks = primary.manifest_binding_checks(manifest)
    assert checks
    assert all(checks.values()), checks
    assert primary.validate_manifest_binding(manifest) == checks


@pytest.mark.parametrize(
    ("path", "mutation", "specific_check"),
    (
        (("protocol_id",), "ASMP7-MUTATED", "protocol_and_schema_are_frozen"),
        (
            ("registration_status",),
            "authorized_without_commit",
            "registration_is_preexecution",
        ),
        (("source_freeze", "files"), ["run.py"], "source_inventory_is_exact"),
        (
            ("artifacts", "replay_command"),
            "python run.py --source-commit <40-hex-source-commit>",
            "isolated_replay_is_exact",
        ),
        (("registry", "coverage_counts"), [0], "registry_key_universes_are_exact"),
        (
            ("registry", "generic_terminal_census", "comparison_count"),
            11519,
            "registry_key_universes_are_exact",
        ),
        (
            ("semantics", "report_law"),
            "q_theta(a)=1/2+(2*theta-1)*(a-c/2)/8",
            "filtration_and_monitor_are_frozen",
        ),
        (
            ("semantics", "fresh_stream_product_law"),
            "shared private/challenge randomness allowed",
            "filtration_and_monitor_are_frozen",
        ),
        (("conclusion_layer_names",), ["task_result"], "layers_are_exact"),
        (
            ("budget", "max_steps_per_episode"),
            8191,
            "resource_and_write_once_contract_is_exact",
        ),
    ),
)
def test_manifest_mutations_fail_their_specific_binding(
    path, mutation, specific_check
):
    manifest = primary.load_json_strict(MANIFEST_PATH)
    mutated = copy.deepcopy(manifest)
    _set_nested(mutated, path, mutation)
    checks = primary.manifest_binding_checks(mutated)
    assert not checks["canonical_manifest_hash_is_frozen"]
    assert not checks[specific_check]
    with pytest.raises(ValueError, match="manifest binding failed"):
        primary.validate_manifest_binding(mutated)


@pytest.mark.parametrize(
    "payload",
    (
        b'{"a":1,"a":2}',
        b'{"a":1.0}',
        b'{"a":1e0}',
        b'{"a":NaN}',
        b'{"a":Infinity}',
    ),
)
def test_strict_json_rejects_duplicate_float_alias_and_nonfinite(payload):
    with pytest.raises(ValueError):
        primary.load_json_bytes_strict(payload)


def test_exact_fraction_rejects_bool_float_and_noncanonical_text():
    assert primary.exact_fraction("5/8") == Fraction(5, 8)
    for value in (True, 0.5, "2/4", "1", "01/2"):
        with pytest.raises((TypeError, ValueError)):
            primary.exact_fraction(value)


def test_nonregistered_k9_c4_quotient_and_relabeling_are_exact():
    row = primary.quotient_row(9, 4)
    expected_counts = [
        math.comb(9, action) * math.comb(7, 4 - action)
        for action in range(5)
    ]
    assert row["agreement_count"] == 9
    assert row["coverage_count"] == 4
    assert row["action_interval"] == [0, 4]
    assert row["attainable_a"] == [0, 1, 2, 3, 4]
    assert expected_counts == [35, 315, 756, 588, 126]
    assert [item["count"] for item in row["multiplicities"]] == expected_counts
    assert row["total_masks"] == sum(expected_counts) == math.comb(16, 4)
    assert row["canonical_attained_set"] == row["relabeled_attained_set"]
    assert all(row["checks"].values())


def test_action_interval_and_denominator_sixteen_report_law():
    assert primary.action_interval(8, 12) == (4, 8)
    assert primary.action_interval(14, 12) == (10, 12)
    assert primary.action_interval(9, 4) == (0, 4)
    assert primary.report_probability(Fraction(1), 12, 4) == Fraction(3, 8)
    assert primary.report_probability(Fraction(1), 12, 8) == Fraction(5, 8)
    assert primary.report_probability(Fraction(1), 12, 10) == Fraction(3, 4)
    assert primary.report_probability(Fraction(1, 2), 12, 4) == Fraction(1, 2)
    with pytest.raises(ValueError):
        primary.action_interval(17, 0)
    with pytest.raises(ValueError):
        primary.report_probability(Fraction(1), 12, 13)


@pytest.mark.parametrize(
    ("horizon", "threshold", "gamma", "objective", "endpoint_q"),
    (
        (1, 0, Fraction(), "max", Fraction(5, 8)),
        (1, 0, Fraction(), "min", Fraction(3, 8)),
        (2, 1, Fraction(1, 2), "max", Fraction(5, 8)),
        (2, 1, Fraction(1, 2), "min", Fraction(3, 8)),
    ),
)
def test_small_monotone_full_prefix_and_count_bellman_equal_iid_endpoint(
    horizon, threshold, gamma, objective, endpoint_q
):
    full = primary.full_prefix_bellman_value(
        horizon, 8, 12, Fraction(1), threshold, gamma, objective
    )
    count = primary.count_state_bellman_value(
        horizon, 8, 12, Fraction(1), threshold, gamma, objective
    )
    iid = primary.iid_upper_tail_value(horizon, endpoint_q, threshold, gamma)
    assert full == count == iid


def test_current_x_timing_scope_breaker_from_direct_exact_functions():
    causal_q0 = primary.report_probability(
        Fraction(1), 12, primary.action_interval(8, 12)[1]
    )
    causal_q1 = primary.report_probability(
        Fraction(1), 12, primary.action_interval(14, 12)[0]
    )
    anticipatory_q0 = Fraction(8, 16) + Fraction(8, 16) * Fraction(1, 2)
    anticipatory_q1 = Fraction(14, 16) * Fraction(1, 2)
    assert (causal_q0, causal_q1) == (Fraction(5, 8), Fraction(3, 4))
    assert (anticipatory_q0, anticipatory_q1) == (
        Fraction(3, 4),
        Fraction(7, 16),
    )
    assert causal_q0 < causal_q1
    assert anticipatory_q0 > anticipatory_q1


def test_nonmonotone_h2_scope_breaker_from_direct_exact_functions():
    lower, upper = primary.action_interval(8, 12)
    probabilities = [
        primary.report_probability(Fraction(1), 12, action)
        for action in range(lower, upper + 1)
    ]
    adaptive = max(
        (1 - first) * after_zero + first * (1 - after_one)
        for first in probabilities
        for after_zero in probabilities
        for after_one in probabilities
    )
    fixed = max(2 * probability * (1 - probability) for probability in probabilities)
    assert adaptive == Fraction(5, 8)
    assert fixed == Fraction(1, 2)


def test_one_upstream_file_hash_mutation_fails_before_scientific_work():
    manifest = primary.load_json_strict(MANIFEST_PATH)
    mutated = copy.deepcopy(manifest)
    item = mutated["upstream_bindings"]["v0_1"]["files"][0]
    item["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="upstream hash mismatch"):
        primary.validate_upstream_bindings(mutated)


def test_independent_registry_row_rejects_deleted_transfer_checks():
    manifest = primary.load_json_strict(MANIFEST_PATH)
    upstream = verifier._selective_map(verifier.upstream_v03_result(manifest))
    key, bound = next(
        (key, row) for key, row in upstream.items() if row["status"] == "feasible_exact"
    )
    k1, theta, coverage_count = key
    expected = verifier.expected_registry_row(
        bound, k1, theta, coverage_count
    )
    assert verifier.registry_row_matches_bound(
        expected, bound, k1, theta, coverage_count
    )
    tampered = copy.deepcopy(expected)
    tampered["transfer_checks"] = {}
    assert not verifier.registry_row_matches_bound(
        tampered, bound, k1, theta, coverage_count
    )


def _materialize_live_inventory(directory: Path) -> None:
    for filename in EXPECTED_SOURCE_FILES:
        (directory / filename).write_text("source\n", encoding="utf-8")


def test_live_inventory_rejects_shadow_module(tmp_path):
    _materialize_live_inventory(tmp_path)
    assert primary.live_source_inventory_checks(tmp_path)["pass"]
    shadow = tmp_path / "json.py"
    shadow.write_text("raise RuntimeError('shadow')\n", encoding="utf-8")
    checks = primary.live_source_inventory_checks(tmp_path)
    assert not checks["pass"]
    assert "json.py" in checks["unexpected"]


def test_live_inventory_rejects_reparse_source_entry(tmp_path, monkeypatch):
    _materialize_live_inventory(tmp_path)
    target = tmp_path / EXPECTED_SOURCE_FILES[0]
    original = primary._is_reparse_point
    monkeypatch.setattr(
        primary,
        "_is_reparse_point",
        lambda path: path == target or original(path),
    )
    checks = primary.live_source_inventory_checks(tmp_path)
    assert not checks["pass"]
    assert EXPECTED_SOURCE_FILES[0] in checks["invalid_source_entries"]


def test_write_once_creates_nested_parent_then_refuses_overwrite(tmp_path):
    output = tmp_path / "new" / "nested" / "result.json"
    primary.write_once_json(output, {"status": "first"})
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        primary.write_once_json(output, {"status": "second"})
    assert output.read_bytes() == original


def test_write_once_rejects_reparse_ancestor(tmp_path, monkeypatch):
    real_parent = tmp_path / "real-artifacts"
    (real_parent / "nested").mkdir(parents=True)
    linked_parent = tmp_path / "linked-artifacts"
    try:
        linked_parent.symlink_to(real_parent, target_is_directory=True)
    except (NotImplementedError, OSError):
        linked_parent.mkdir()
        (linked_parent / "nested").mkdir()
        original = primary._is_reparse_point
        monkeypatch.setattr(
            primary,
            "_is_reparse_point",
            lambda path: path == linked_parent or original(path),
        )
    output = linked_parent / "nested" / "result.json"
    with pytest.raises(ValueError, match="reparse point"):
        primary.write_once_json(output, {"status": "must-not-write"})
    assert not (real_parent / "nested" / "result.json").exists()


def test_write_once_rejects_non_directory_parent(tmp_path):
    blocked_parent = tmp_path / "not-a-directory"
    blocked_parent.write_text("preserve\n", encoding="utf-8")
    with pytest.raises(NotADirectoryError, match="not a directory"):
        primary.write_once_json(
            blocked_parent / "result.json", {"status": "must-not-write"}
        )
    assert blocked_parent.read_text(encoding="utf-8") == "preserve\n"


@pytest.mark.parametrize("entrypoint", ("run.py", "verify_independent.py"))
def test_scientific_entrypoints_require_isolated_safe_path(entrypoint):
    assert {path.name for path in HERE.iterdir()} == set(EXPECTED_SOURCE_FILES)
    unsafe = subprocess.run(
        [sys.executable, str(HERE / entrypoint), "--help"],
        cwd=HERE,
        capture_output=True,
        text=True,
    )
    assert unsafe.returncode != 0
    assert "refusing unsafe launch before imports" in (
        unsafe.stdout + unsafe.stderr
    )

    isolated = subprocess.run(
        [sys.executable, "-I", str(HERE / entrypoint), "--help"],
        cwd=HERE,
        capture_output=True,
        text=True,
    )
    assert isolated.returncode == 0, isolated.stderr
    help_text = isolated.stdout + isolated.stderr
    assert "usage:" in help_text.lower()
    assert "--output" in help_text
    if entrypoint == "run.py":
        assert "--source-commit" in help_text
    else:
        assert "--result" in help_text


@pytest.mark.parametrize("entrypoint", ("run.py", "verify_independent.py"))
def test_scientific_entrypoints_reject_output_inside_source(entrypoint):
    forbidden = HERE / "must_not_write.json"
    command = [sys.executable, "-I", str(HERE / entrypoint)]
    if entrypoint == "run.py":
        command.extend(["--source-commit", "0" * 40])
    command.extend(["--output", str(forbidden)])
    completed = subprocess.run(
        command,
        cwd=HERE,
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "outside the frozen sibling artifact directory" in (
        completed.stdout + completed.stderr
    )
    assert not forbidden.exists()


def test_real_repo_source_binding_skips_precommit_and_passes_after_freeze():
    root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=HERE,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    ).resolve()
    relative_manifest = (HERE.relative_to(root) / "manifest_v0_4.json").as_posix()
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
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not source_commit:
        pytest.skip("source-freeze commit does not exist yet")

    binding = primary.source_commit_binding(source_commit)
    bootstrap_binding = runner.bootstrap_source_commit_binding(source_commit)
    assert binding["source_commit"] == source_commit
    assert binding["source_commit_type"] == "commit"
    assert binding["source_commit_is_ancestor_of_head"]
    assert tuple(binding["source_files"]) == EXPECTED_SOURCE_FILES
    assert bootstrap_binding == binding
