"""Source-only and off-grid tests; never execute the registered 54-row grid."""

from __future__ import annotations

import copy
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

import noisy_anchor as primary
import run as runner
import verify_independent as verifier


HERE = Path(os.path.abspath(__file__)).parent
MANIFEST = HERE / "manifest_v0_4.json"
EXPECTED_FILES = (
    "PROTOCOL_v0_4.md",
    "README.md",
    "SOURCE_FREEZE.md",
    "manifest_v0_4.json",
    "noisy_anchor.py",
    "run.py",
    "test_noisy_anchor.py",
    "verify_independent.py",
)


def test_atomic_source_inventory_and_public_constants_are_frozen():
    assert primary.SOURCE_FILES == runner.SOURCE_FILES == verifier.SOURCE_FILES
    assert primary.SOURCE_FILES == EXPECTED_FILES
    assert {path.name for path in HERE.iterdir()} == set(EXPECTED_FILES)
    assert primary.PROTOCOL_ID == verifier.PROTOCOL_ID
    assert primary.ROOT_ANCHOR == verifier.ROOT_ANCHOR == 0b0011
    assert primary.MANIFEST_CANONICAL_SHA256 == verifier.MANIFEST_SHA256


def test_manifest_is_exact_and_has_the_alife_contract():
    manifest = primary.load_json_strict(MANIFEST)
    checks = primary.validate_manifest(manifest)
    assert all(checks.values())
    assert manifest["benefit"] == "robustness"
    assert manifest["claim_scope"] == "model_only"
    assert manifest["experimental_unit"]
    assert len(manifest["hypotheses"]) == 3
    assert manifest["registry"]["row_count"] == 54
    assert manifest["model"]["coin_order"].startswith("hazard_class_0")
    assert manifest["metrics"]["selection"] == []


@pytest.mark.parametrize(
    ("path", "value", "specific_check"),
    (
        (("protocol_id",), "MUTATED", "identity"),
        (("registry", "m"), [1, 5, 3], "registry_order"),
        (("model", "coin_order"), "interleaved", "anchor_semantics"),
        (("source_freeze", "files"), ["run.py"], "source_inventory"),
        (("predecessor_binding", "commit"), "0" * 40, "predecessor"),
        (("claim_boundary",), ["broad claim"], "claim_boundary"),
    ),
)
def test_manifest_mutations_fail_binding(path, value, specific_check):
    manifest = primary.load_json_strict(MANIFEST)
    mutated = copy.deepcopy(manifest)
    target = mutated
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    checks = primary.manifest_binding_checks(mutated)
    assert not checks["canonical_manifest_hash"]
    assert not checks[specific_check]
    with pytest.raises(ValueError, match="manifest binding failed"):
        primary.validate_manifest(mutated)


def test_strict_json_and_fraction_parsers_reject_aliases():
    for payload in (
        b'{"x":1,"x":2}',
        b'{"x":1.0}',
        b'{"x":1e0}',
        b'{"x":NaN}',
    ):
        with pytest.raises(ValueError):
            primary.load_json_bytes_strict(payload)
    for value in (True, 0.5, "2/4", "1", "01/2"):
        with pytest.raises((TypeError, ValueError)):
            primary.exact_fraction(value)


def test_off_grid_formula_matches_complete_joint_pattern_enumerator():
    m = 3
    epsilon = Fraction(1, 7)
    p = primary.majority_error_probability(m, epsilon)
    enumerated = verifier.enumerate_batch(m, epsilon)
    assert enumerated["pattern_count"] == 64
    assert enumerated["single"] == p
    assert enumerated["visible"] == primary.visible_failure_probability(p)
    assert enumerated["both"] == p * p
    assert sum(
        verifier._pattern_weight(pattern, epsilon)
        for pattern in __import__("itertools").product((0, 1), repeat=2 * m)
    ) == 1


def test_largest_registered_pattern_space_has_exactly_1024_atoms_off_grid_rate():
    enumerated = verifier.enumerate_batch(5, Fraction(1, 9))
    assert enumerated["pattern_count"] == 1024
    assert enumerated["single"] == primary.majority_error_probability(5, Fraction(1, 9))


def test_two_state_recurrence_is_not_formula_reuse():
    q = Fraction(2, 7)
    assert verifier.advance_two_state([q] * 4) == 1 - (1 - q) ** 4
    assert verifier.advance_two_state([Fraction(0)] * 9) == 0
    assert verifier.advance_two_state([Fraction(1)] * 9) == 1


def test_off_grid_primary_and_independent_rows_match_both_temporal_laws():
    for temporal in primary.TEMPORAL_MODELS:
        observed = primary.row_record(3, Fraction(1, 7), 4, temporal)
        replayed = verifier.row_record(3, Fraction(1, 7), 4, temporal)
        assert verifier.strict_json_equal(observed, replayed)
    fresh = primary.row_record(3, Fraction(1, 7), 4, "fresh_iid")
    persistent = primary.row_record(3, Fraction(1, 7), 4, "persistent")
    assert primary.exact_fraction(fresh["finite_horizon_failure"]) > primary.exact_fraction(
        persistent["finite_horizon_failure"]
    )


def test_visibility_and_single_bit_exploit_witnesses_are_live():
    witnesses = primary.single_bit_exploit_witnesses()
    assert witnesses == verifier.exploit_witnesses()
    assert witnesses[0]["installed_anchor"] == "0111"
    assert witnesses[1]["installed_anchor"] == "1011"
    assert all(record["accepted"] for record in witnesses)
    p = primary.majority_error_probability(3, Fraction(1, 7))
    q = primary.visible_failure_probability(p)
    assert 0 < p < q < 1


def test_perfect_correlation_and_blinding_are_one_bit_controls():
    m, epsilon = 3, Fraction(1, 7)
    p = primary.majority_error_probability(m, epsilon)
    assert verifier.perfectly_correlated_single(m, epsilon) == p
    row = primary.row_record(m, epsilon, 4, "fresh_iid")
    assert primary.exact_fraction(
        row["perfectly_correlated_bits_per_installation_failure"]
    ) == p
    assert primary.exact_fraction(row["blinded_one_class_per_installation_failure"]) == p
    assert primary.exact_fraction(row["visible_adversary_per_installation_failure"]) > p


def test_false_negative_only_control_is_safe_but_can_deadlock():
    row = primary.row_record(3, Fraction(1, 7), 4, "fresh_iid")
    control = row["false_negative_only"]
    p = primary.majority_error_probability(3, Fraction(1, 7))
    assert control["unsafe_failure"] == "0/1"
    assert primary.exact_fraction(control["per_installation_deadlock"]) == p * p
    assert primary.exact_fraction(control["horizon_deadlock"]) > 0


def test_epsilon_zero_and_inherited_cycle_are_exact_clean_controls():
    for temporal in primary.TEMPORAL_MODELS:
        row = primary.row_record(5, Fraction(0), 11, temporal)
        assert row["finite_horizon_failure"] == "0/1"
        assert row["false_negative_only"]["horizon_deadlock"] == "0/1"
    cycle = primary.safe_cycle_fixture()
    assert cycle == verifier.safe_cycle()
    assert cycle["all_safe"] and cycle["returns_to_start"]


def test_symbolic_negative_theorem_has_correct_fresh_only_scope():
    theorem = primary.symbolic_theorem()
    assert theorem == verifier.theorem()
    assert theorem["fresh_limit"].endswith("=1")
    assert "not asserted to approach 1" in theorem["persistent_limit"]
    for m in (1, 3, 7):
        epsilon = Fraction(1, 13)
        assert primary.majority_error_probability(m, epsilon) >= epsilon**m > 0


def test_live_inventory_rejects_an_extra_shadow_module(tmp_path):
    for filename in EXPECTED_FILES:
        (tmp_path / filename).write_text("source\n", encoding="utf-8")
    assert primary.live_source_inventory_checks(tmp_path)["pass"]
    (tmp_path / "json.py").write_text("raise RuntimeError\n", encoding="utf-8")
    checks = primary.live_source_inventory_checks(tmp_path)
    assert not checks["pass"]
    assert checks["unexpected"] == ["json.py"]


def test_write_once_preserves_existing_file(tmp_path):
    path = tmp_path / "artifacts" / "record.json"
    primary.write_once_json(path, {"value": "first"})
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        primary.write_once_json(path, {"value": "second"})
    assert path.read_bytes() == original


@pytest.mark.parametrize("entrypoint", ("run.py", "verify_independent.py"))
def test_scientific_entrypoints_require_isolated_safe_path(entrypoint):
    unsafe = subprocess.run(
        [sys.executable, str(HERE / entrypoint), "--help"],
        cwd=HERE,
        capture_output=True,
        text=True,
    )
    assert unsafe.returncode != 0
    assert "refusing unsafe launch before imports" in unsafe.stdout + unsafe.stderr
    isolated = subprocess.run(
        [sys.executable, "-I", str(HERE / entrypoint), "--help"],
        cwd=HERE,
        capture_output=True,
        text=True,
    )
    assert isolated.returncode == 0, isolated.stderr
    assert "usage:" in isolated.stdout.lower()


def test_registered_compiler_is_not_called_by_source_suite(monkeypatch):
    monkeypatch.setattr(
        primary,
        "iter_registered_rows",
        lambda: (_ for _ in ()).throw(AssertionError("registered grid forbidden")),
    )
    assert primary.row_record(3, Fraction(1, 7), 4, "fresh_iid")["m"] == 3
