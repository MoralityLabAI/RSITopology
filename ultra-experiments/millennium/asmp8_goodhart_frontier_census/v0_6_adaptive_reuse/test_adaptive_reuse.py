import ast
import copy
import json
import platform
from fractions import Fraction
from pathlib import Path

import pytest

import verify_independent as independent

from adaptive_reuse import (
    adaptive_census,
    compile_result,
    local_monotonicity_failures,
    policy_registry,
    robust_lower_bound,
    robustness_probes,
    true_gain,
    validate_protocol,
)
from run import SOURCE_FILES, sha256_file, write_json


HERE = Path(__file__).resolve().parent


def test_policy_registry_is_probability_valid():
    policies = policy_registry(6)
    assert len(policies) == 30
    assert all(min(policy["distribution"]) >= 0 and sum(policy["distribution"]) == 1 for policy in policies)


def test_pointwise_bound_on_representative_errors_and_masks():
    policies = policy_registry(6)
    errors = tuple(Fraction(value) for value in (-1, 0, 1, 1, -1, 0))
    for mask in (0, 1, 0b010101, 0b111111):
        for policy in policies:
            assert robust_lower_bound(policy, errors, mask, Fraction(1)) <= true_gain(policy, errors)


def test_full_census_is_exact():
    errors = tuple(Fraction(value) for value in (1, -1, 0, 1, 0, -1))
    for policy in policy_registry(6):
        assert robust_lower_bound(policy, errors, 0b111111, Fraction(1)) == true_gain(policy, errors)


def test_reveal_increment_is_monotone():
    assert local_monotonicity_failures(6, Fraction(1)) == 0


def test_adaptive_negative_control_is_live_and_robust_bound_is_sound():
    result = adaptive_census(4, Fraction(1))
    assert result["adaptive_robust_false_declarations"] == 0
    assert result["adaptive_naive_false_declarations"] > 0


def test_metric_robustness_probes_on_small_complete_summary():
    adaptive = adaptive_census(4, Fraction(1))
    summary = {
        "adaptive": adaptive,
        "pointwise": {"full_census_failures": 0},
        "local_monotonicity_failures": 0,
    }
    # The relabeling fixture is six-dimensional, so retain the registered
    # dimension while injecting the exact small adaptive census.
    probes = robustness_probes(summary, 6, Fraction(1))
    assert set(probes) == {"invariance", "sensitivity", "monotonicity", "anti_gaming", "clean_control"}
    assert all(record["pass"] for record in probes.values())


def test_independent_replay_derives_complete_payload_and_conclusions():
    protocol = json.loads((HERE / "protocol_v0_6.json").read_text(encoding="utf-8"))
    expected = independent.expected_result()
    verification = independent.verify_payload(protocol, expected)

    assert verification["pass"], verification
    assert all(verification["independent_gates"].values())
    assert verification["replayed_pointwise_cells"] == 1_399_680
    assert verification["replayed_adaptive_traces"] == 729
    assert verification["derived_conclusion_layers"]["claim_support"] == (
        "deterministic_finite_adaptive_audit_reuse"
    )


def test_universal_claim_forged_gates_digest_and_adaptive_counts_are_rejected():
    protocol = json.loads((HERE / "protocol_v0_6.json").read_text(encoding="utf-8"))
    tampered = copy.deepcopy(independent.expected_result())
    tampered["task_result"] = "ASMP8_UNIVERSALLY_SOLVED"
    tampered["claim_support"] = "universal_stochastic_optional_stopping_reuse"
    tampered["operational_decision"] = "deploy_without_further_validation"
    tampered["gates"] = {"forged_gate": True}
    tampered["metric_robustness"] = {"forged": {"pass": False}}
    tampered["summary"]["adaptive"]["adaptive_robust_false_declarations"] = 999_999
    tampered["summary"]["adaptive"]["adaptive_naive_false_declarations"] = 0
    tampered["summary"]["local_monotonicity_failures"] = 999_999
    tampered["summary"]["pointwise"]["pointwise_digest_sha256"] = "0" * 64

    verification = independent.verify_payload(protocol, tampered)

    assert not verification["pass"]
    assert not verification["independent_gates"]["V3_adaptive_policy_and_audit_replayed"]
    assert not verification["independent_gates"]["V5_metric_probes_and_primary_gates_derived"]
    assert not verification["independent_gates"]["V6_conclusion_layers_and_boundary_derived"]
    assert "summary.pointwise.pointwise_digest_sha256" in verification["mismatch_paths"]
    assert verification["claim_support"] == "none"
    assert verification["operational_decision"] == "repair"


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("error_alphabet", [-2, 0, 2]),
        ("error_cap", 2),
        ("policy_mass_move", "1/100"),
        ("alphabet_size", 7),
        ("claim_boundary", ["universal claim"]),
    ),
)
def test_primary_and_independent_reject_registered_protocol_mutations(field, value):
    protocol = json.loads((HERE / "protocol_v0_6.json").read_text(encoding="utf-8"))
    protocol[field] = value
    with pytest.raises(ValueError, match="protocol binding failed"):
        compile_result(protocol)
    verification = independent.verify_payload(protocol, independent.expected_result())
    assert not verification["pass"]
    assert not verification["independent_gates"]["V0_exact_registered_protocol"]


def test_artifact_bundle_binds_protocol_result_receipt_and_exact_sources(tmp_path):
    protocol_path = HERE / "protocol_v0_6.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    result_path = tmp_path / "result_v0_6.json"
    receipt_path = tmp_path / "run_receipt_v0_6.json"
    write_json(result_path, independent.expected_result())
    receipt = {
        "schema_version": "asmp8_adaptive_reuse_run_receipt_v0_6_1",
        "protocol_id": protocol["protocol_id"],
        "executed_utc": "2026-08-03T00:00:00+00:00",
        "protocol_sha256": sha256_file(protocol_path),
        "result_sha256": sha256_file(result_path),
        "source_hashes": {name: sha256_file(HERE / name) for name in SOURCE_FILES},
        "protocol_binding": validate_protocol(protocol),
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "arithmetic": "fractions.Fraction",
            "gpu": "not used",
        },
    }
    write_json(receipt_path, receipt)

    verification = independent.verify_artifact_bundle(tmp_path, HERE)
    assert verification["pass"], verification
    assert all(verification["binding_gates"].values())

    receipt["source_hashes"]["adaptive_reuse.py"] = "0" * 64
    write_json(receipt_path, receipt)
    rejected = independent.verify_artifact_bundle(tmp_path, HERE)
    assert not rejected["pass"]
    assert not rejected["binding_gates"]["B3_exact_source_set_and_hashes_bound"]


def test_independent_verifier_does_not_import_primary_implementation():
    tree = ast.parse((HERE / "verify_independent.py").read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert "adaptive_reuse" not in imported
