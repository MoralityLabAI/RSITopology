import copy
import json
from fractions import Fraction
from pathlib import Path

import pytest

import verify_independent as independent
from balanced_cover import (
    bayes_error,
    canonical_json,
    compile_result,
    load_protocol,
    optimal_balanced_laws,
    robustness_probes,
    sign_count_tv_upper_bound,
    theorem_cell,
    total_variation,
)
from synthesize_receipt import build_receipt


HERE = Path(__file__).resolve().parent


def _write_verified_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    protocol = load_protocol(HERE / "protocol_v0_2.json")
    protocol_path = tmp_path / "protocol_v0_2.json"
    result_path = tmp_path / "result_v0_2.json"
    verification_path = tmp_path / "verification_v0_2.json"
    protocol_path.write_text(canonical_json(protocol), encoding="utf-8")
    result_path.write_text(canonical_json(compile_result(protocol)), encoding="utf-8")
    verification = independent.verify(protocol_path, result_path)
    verification_path.write_text(independent.canonical_json(verification), encoding="utf-8")
    return protocol_path, result_path, verification_path


def test_optimizer_is_a_probability_pair_with_exact_uniform_average():
    for alphabet_size in range(2, 16):
        p0, p1 = optimal_balanced_laws(alphabet_size)
        assert min(p0 + p1) >= 0
        assert sum(p0) == sum(p1) == 1
        assert all(
            (left + right) / 2 == Fraction(1, alphabet_size)
            for left, right in zip(p0, p1)
        )


def test_parity_frontier_and_odd_error_formula():
    for alphabet_size in range(2, 32):
        cell = theorem_cell(alphabet_size)
        assert cell["perfect_decoding"] == (alphabet_size % 2 == 0)
        expected = Fraction(0) if alphabet_size % 2 == 0 else Fraction(1, 2 * alphabet_size)
        assert Fraction(cell["bayes_error"]) == expected


def test_witness_meets_sign_count_dual_bound():
    for alphabet_size in range(2, 32):
        p0, p1 = optimal_balanced_laws(alphabet_size)
        assert total_variation(p0, p1) == sign_count_tv_upper_bound(alphabet_size)


def test_per_message_cover_is_chance():
    for alphabet_size in range(2, 16):
        cover = [Fraction(1, alphabet_size)] * alphabet_size
        assert bayes_error(cover, cover) == Fraction(1, 2)


def test_metric_robustness_pack_passes():
    probes = robustness_probes()
    assert set(probes) == {
        "invariance",
        "sensitivity",
        "monotonicity",
        "anti_gaming",
        "clean_control",
    }
    assert all(record["pass"] for record in probes.values())


@pytest.mark.parametrize(
    ("field", "mutation"),
    (
        ("cover_law", "nonuniform"),
        ("message_count", 3),
        ("message_prior", ["3/4", "1/4"]),
        ("alphabet_sizes", {"minimum": 2, "maximum": 30}),
        ("independent_extremal_enumeration_maximum", 8),
        ("claim_boundary", ["unbounded claim"]),
        ("unexpected_semantic_extension", True),
    ),
)
def test_primary_rejects_protocol_semantic_mutations(field, mutation):
    protocol = load_protocol(HERE / "protocol_v0_2.json")
    protocol[field] = mutation
    with pytest.raises(ValueError, match="protocol binding failed"):
        compile_result(protocol)


@pytest.mark.parametrize(
    ("field", "mutation"),
    (
        ("cover_law", "nonuniform"),
        ("message_count", 3),
        ("message_prior", ["3/4", "1/4"]),
        ("alphabet_sizes", {"minimum": 2, "maximum": 30}),
        ("independent_extremal_enumeration_maximum", 8),
        ("claim_boundary", ["unbounded claim"]),
        ("unexpected_semantic_extension", True),
    ),
)
def test_independent_verifier_rejects_protocol_semantic_mutations(
    tmp_path, field, mutation
):
    protocol = load_protocol(HERE / "protocol_v0_2.json")
    result = compile_result(protocol)
    mutated = copy.deepcopy(protocol)
    mutated[field] = mutation
    protocol_path = tmp_path / "protocol_v0_2.json"
    result_path = tmp_path / "result_v0_2.json"
    protocol_path.write_text(canonical_json(mutated), encoding="utf-8")
    result_path.write_text(canonical_json(result), encoding="utf-8")

    verification = independent.verify(protocol_path, result_path)

    assert not verification["pass"]
    assert not verification["independent_gates"]["V0_frozen_protocol_binding"]


def test_independent_verifier_recomputes_every_registered_cell(tmp_path):
    protocol_path, result_path, _ = _write_verified_fixture(tmp_path)
    verification = independent.verify(protocol_path, result_path)

    assert verification["pass"]
    assert verification["registered_alphabet_sizes"] == list(range(2, 32))
    assert verification["cell_mismatches"] == []
    assert verification["probability_failures"] == []
    assert verification["independent_gates"][
        "V2_every_registered_cell_recomputed_exactly"
    ]
    assert all(verification["derived_primary_gates"].values())


def test_late_grid_corruption_is_detected_without_trusting_primary_gates(tmp_path):
    protocol = load_protocol(HERE / "protocol_v0_2.json")
    result = compile_result(protocol)
    assert all(result["gates"].values())
    result["cells"][-1]["bayes_error"] = "0/1"
    result["cells"][-1]["undeclared_field"] = "must not be ignored"
    protocol_path = tmp_path / "protocol_v0_2.json"
    result_path = tmp_path / "result_v0_2.json"
    protocol_path.write_text(canonical_json(protocol), encoding="utf-8")
    result_path.write_text(canonical_json(result), encoding="utf-8")

    verification = independent.verify(protocol_path, result_path)

    assert not verification["pass"]
    assert any(
        mismatch["alphabet_size"] == 31 and mismatch["field"] == "bayes_error"
        for mismatch in verification["cell_mismatches"]
    )
    assert any(
        mismatch["alphabet_size"] == 31
        and mismatch["field"] == "undeclared_field"
        for mismatch in verification["cell_mismatches"]
    )
    assert 31 in verification["probability_failures"]
    assert "G4_odd_error_formula" in verification["primary_gate_mismatches"]
    assert not verification["independent_gates"][
        "V2_every_registered_cell_recomputed_exactly"
    ]


def test_final_receipt_binds_source_commit_protocol_result_and_verification(tmp_path):
    protocol_path, result_path, verification_path = _write_verified_fixture(tmp_path)
    source_path = tmp_path / "source.py"
    source_path.write_text("frozen source\n", encoding="utf-8")
    committed_source = source_path.read_bytes()
    source_commit = "a" * 40
    resolver = lambda value: value
    blob_reader = lambda _commit, _name: committed_source

    receipt = build_receipt(
        source_commit,
        protocol_path,
        result_path,
        verification_path,
        source_files={"source.py": source_path},
        commit_resolver=resolver,
        committed_blob_reader=blob_reader,
    )

    assert receipt["pass"]
    assert all(receipt["checks"].values())
    assert {
        "metric_robustness",
        "task_result",
        "measurement_reliability",
        "claim_support",
        "operational_decision",
    } <= set(receipt)

    result_path.write_text(result_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
    artifact_tamper = build_receipt(
        source_commit,
        protocol_path,
        result_path,
        verification_path,
        source_files={"source.py": source_path},
        commit_resolver=resolver,
        committed_blob_reader=blob_reader,
    )
    assert not artifact_tamper["pass"]
    assert not artifact_tamper["checks"][
        "C5_verification_binds_protocol_and_primary_result"
    ]


def test_final_receipt_rejects_source_bytes_not_in_declared_commit(tmp_path):
    protocol_path, result_path, verification_path = _write_verified_fixture(tmp_path)
    source_path = tmp_path / "source.py"
    source_path.write_text("working tree source\n", encoding="utf-8")
    source_commit = "b" * 40

    receipt = build_receipt(
        source_commit,
        protocol_path,
        result_path,
        verification_path,
        source_files={"source.py": source_path},
        commit_resolver=lambda value: value,
        committed_blob_reader=lambda _commit, _name: b"different committed source\n",
    )

    assert not receipt["pass"]
    assert not receipt["checks"]["C1_source_files_match_commit"]
    assert receipt["binding_diagnostics"]["source_mismatches"] == ["source.py"]
    assert receipt["task_result"] == "not_established"
    assert receipt["operational_decision"] == "repair"


def test_final_receipt_replays_verifier_instead_of_trusting_stale_booleans(tmp_path):
    protocol_path, result_path, verification_path = _write_verified_fixture(tmp_path)
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["cells"][-1]["bayes_error"] = "0/1"
    result_path.write_text(canonical_json(result), encoding="utf-8")
    stale_verification = json.loads(verification_path.read_text(encoding="utf-8"))
    stale_verification["bindings"]["result_v0_2.json"] = independent.sha256_file(
        result_path
    )
    verification_path.write_text(
        independent.canonical_json(stale_verification), encoding="utf-8"
    )
    source_path = tmp_path / "source.py"
    source_path.write_text("frozen source\n", encoding="utf-8")
    committed_source = source_path.read_bytes()
    source_commit = "c" * 40

    receipt = build_receipt(
        source_commit,
        protocol_path,
        result_path,
        verification_path,
        source_files={"source.py": source_path},
        commit_resolver=lambda value: value,
        committed_blob_reader=lambda _commit, _name: committed_source,
    )

    assert not receipt["pass"]
    assert receipt["checks"]["C5_verification_binds_protocol_and_primary_result"]
    assert not receipt["checks"]["C4_verification_pass_and_gates"]
    assert not receipt["binding_diagnostics"][
        "verification_replay_matches_artifact"
    ]
