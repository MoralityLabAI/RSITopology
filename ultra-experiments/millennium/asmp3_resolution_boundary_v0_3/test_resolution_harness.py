import json
from fractions import Fraction
from pathlib import Path

from build_release_manifest import verify_manifest
from resolution_harness import (
    ETA,
    RESULT_PATH,
    build_result,
    closure_audit,
    exhaustive_parity_gap,
    exhaustive_parity_refutation_dimension,
    exhaustive_replica_minimum,
    parity_decision_gap,
    parity_error_binomial_sum,
    parity_error_closed_form,
    persistent_single_atom_error,
    replicated_refutation_dimension,
    xor_cross_examination_local_lemma,
)
from verify_result import verify
from verify_fourier_certificate import verify as verify_fourier
from verify_expert_reviews import MANIFEST, evaluate_reviews, sha256


def test_canonical_interface_axioms_are_missing() -> None:
    audit = closure_audit()
    assert audit["canonical_section_found"]
    assert not audit["refute_binding_axiom_present"]
    assert not audit["refute_adequacy_axiom_present"]


def test_single_atom_persistent_error_does_not_amplify() -> None:
    for queries in (1, 2, 3, 9, 1000):
        assert persistent_single_atom_error(queries) == ETA
        assert persistent_single_atom_error(queries) < Fraction(1, 2)


def test_formal_xor_component_has_local_cross_examination_step() -> None:
    assert xor_cross_examination_local_lemma()


def test_parity_error_closed_form_matches_binomial_sum() -> None:
    for atom_count in range(1, 65):
        assert parity_error_closed_form(atom_count) == parity_error_binomial_sum(
            atom_count
        )


def test_exact_total_variation_matches_parity_gap() -> None:
    for atom_count in range(1, 10):
        assert exhaustive_parity_gap(atom_count) == parity_decision_gap(atom_count)


def test_false_parity_claim_requires_every_semantic_atom() -> None:
    for atom_count in range(1, 8):
        assert exhaustive_parity_refutation_dimension(atom_count) == atom_count


def test_joint_gap_vanishes_despite_polylog_refutation_size() -> None:
    gaps = [parity_decision_gap(depth) for depth in range(1, 33)]
    assert all(right < left for left, right in zip(gaps, gaps[1:]))
    assert gaps[-1] < Fraction(1, 10**6)


def test_meaning_preserving_replication_rescales_dimension() -> None:
    for replicas in range(1, 17):
        assert replicated_refutation_dimension(replicas, False) == 1
        assert replicated_refutation_dimension(replicas, True) == replicas
        assert exhaustive_replica_minimum(replicas, False) == 1
        assert exhaustive_replica_minimum(replicas, True) == replicas


def test_result_is_certified_and_matches_artifact() -> None:
    result = build_result()
    assert result["certified"]
    assert all(result["gates"].values())
    assert json.loads(RESULT_PATH.read_text(encoding="utf-8")) == result


def test_independent_verifier_passes() -> None:
    verification = verify()
    assert verification["passed"]
    assert all(verification["checks"].values())


def test_independent_fourier_verifier_passes() -> None:
    verification = verify_fourier()
    assert verification["passed"]
    assert all(verification["checks"].values())


def test_release_manifest_matches_all_candidate_artifacts() -> None:
    assert verify_manifest()


def test_external_review_gate_is_truthfully_pending_without_receipts() -> None:
    status = evaluate_reviews()
    assert status["minimum_independent_teams"] == 2
    assert status["qualifying_receipts"] == 0
    assert not status["completion_gate_satisfied"]


def review_receipt(
    reviewer: str,
    track: str,
    manifest_sha256: str,
) -> dict[str, object]:
    return {
        "schema_version": "asmp3_v0_3_expert_review_v3",
        "reviewer": reviewer,
        "expertise": "test fixture",
        "conflicts": "none",
        "review_track": track,
        "release_manifest_sha256": manifest_sha256,
        "independent_initial_review": True,
        "question_answers": [
            {"question": index, "answer": "yes", "evidence": "fixture"}
            for index in range(1, 13)
        ],
        "verdict": "accept",
        "material_issue_found": False,
        "repository_storage_permission": True,
        "independent_checker": {
            "implemented_by_review_team": False,
            "artifact": "",
            "artifact_sha256": "",
            "method": "",
            "result": "not_run",
        },
    }


def write_receipt(path: Path, receipt: dict[str, object]) -> None:
    path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def test_external_review_gate_accepts_two_distinct_tracks_and_reviewers(
    tmp_path: Path,
) -> None:
    manifest_hash = sha256(MANIFEST)
    write_receipt(
        tmp_path / "complexity.json",
        review_receipt(
            "reviewer-a",
            "complexity_and_game_semantics",
            manifest_hash,
        ),
    )
    checker_path = tmp_path / "checkers" / "probability_checker.py"
    checker_path.parent.mkdir()
    checker_path.write_text(
        "# independently implemented test fixture\nprint('pass')\n",
        encoding="utf-8",
        newline="\n",
    )
    probability = review_receipt(
        "reviewer-b",
        "probability_noise_and_lower_bound",
        manifest_hash,
    )
    probability["independent_checker"] = {
        "implemented_by_review_team": True,
        "artifact": "checkers/probability_checker.py",
        "artifact_sha256": sha256(checker_path),
        "method": "independent test fixture",
        "result": "pass",
    }
    write_receipt(
        tmp_path / "probability.json",
        probability,
    )
    status = evaluate_reviews(reviews_directory=tmp_path)
    assert status["qualifying_receipts"] == 2
    assert status["qualifying_independently_implemented_checkers"] == 1
    assert status["completion_gate_satisfied"]


def test_external_review_gate_requires_an_independently_implemented_checker(
    tmp_path: Path,
) -> None:
    manifest_hash = sha256(MANIFEST)
    write_receipt(
        tmp_path / "complexity.json",
        review_receipt(
            "reviewer-a",
            "complexity_and_game_semantics",
            manifest_hash,
        ),
    )
    write_receipt(
        tmp_path / "probability.json",
        review_receipt(
            "reviewer-b",
            "probability_noise_and_lower_bound",
            manifest_hash,
        ),
    )
    status = evaluate_reviews(reviews_directory=tmp_path)
    assert status["qualifying_receipts"] == 2
    assert status["qualifying_independently_implemented_checkers"] == 0
    assert not status["completion_gate_satisfied"]


def test_external_review_gate_rejects_checker_hash_mismatch(
    tmp_path: Path,
) -> None:
    manifest_hash = sha256(MANIFEST)
    checker_path = tmp_path / "checkers" / "probability_checker.py"
    checker_path.parent.mkdir()
    checker_path.write_text("# independent fixture\n", encoding="utf-8")
    receipt = review_receipt(
        "reviewer-b",
        "probability_noise_and_lower_bound",
        manifest_hash,
    )
    receipt["independent_checker"] = {
        "implemented_by_review_team": True,
        "artifact": "checkers/probability_checker.py",
        "artifact_sha256": "0" * 64,
        "method": "independent test fixture",
        "result": "pass",
    }
    write_receipt(tmp_path / "probability.json", receipt)
    status = evaluate_reviews(reviews_directory=tmp_path)
    assert status["qualifying_receipts"] == 0
    assert status["qualifying_independently_implemented_checkers"] == 0
    assert "independent checker artifact hash mismatch" in status["receipts"][0][
        "errors"
    ]


def test_external_review_gate_does_not_qualify_unclear_answer(
    tmp_path: Path,
) -> None:
    manifest_hash = sha256(MANIFEST)
    receipt = review_receipt(
        "reviewer-a",
        "complexity_and_game_semantics",
        manifest_hash,
    )
    receipt["question_answers"][3]["answer"] = "unclear"
    write_receipt(tmp_path / "complexity.json", receipt)
    status = evaluate_reviews(reviews_directory=tmp_path)
    assert status["qualifying_receipts"] == 0
    assert not status["receipts"][0]["all_required_questions_answered_yes"]
    assert not status["completion_gate_satisfied"]


def test_external_review_gate_rejects_duplicate_identity_or_wrong_hash(
    tmp_path: Path,
) -> None:
    manifest_hash = sha256(MANIFEST)
    write_receipt(
        tmp_path / "complexity.json",
        review_receipt(
            "same-reviewer",
            "complexity_and_game_semantics",
            manifest_hash,
        ),
    )
    wrong = review_receipt(
        "same-reviewer",
        "probability_noise_and_lower_bound",
        "0" * 64,
    )
    write_receipt(tmp_path / "probability.json", wrong)
    status = evaluate_reviews(reviews_directory=tmp_path)
    assert status["qualifying_receipts"] == 1
    assert not status["completion_gate_satisfied"]
