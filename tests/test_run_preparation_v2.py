from __future__ import annotations

import json
from pathlib import Path

import pytest

import rsi_topology.run_preparation_v2 as prep
from rsi_topology.anchor_guard_v2 import canonical_json_sha256


@pytest.fixture(autouse=True)
def _stable_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        prep,
        "runtime_environment",
        lambda: {
            "python_version": "test",
            "python_executable": "test-python",
            "platform": "test-platform",
            "packages": {"numpy": "test", "torch": "test", "transformers": "test"},
            "gpu_static": ["test-gpu"],
        },
    )


def _artifact(path: Path) -> dict[str, object]:
    return {"path": str(path), "sha256": prep.sha256_file(path)}


def _complete_registration(tmp_path: Path) -> tuple[dict, Path]:
    files: dict[str, Path] = {}
    for name in (
        "parent_result",
        "new_protocol",
        "fresh_holdout",
        "proposal",
        "scorer",
        "edit_family",
        "wrapper",
        "wrapper_validation",
        "cleanup",
    ):
        path = tmp_path / f"{name}.txt"
        path.write_text(f"{name}\n", encoding="utf-8")
        files[name] = path
    registration = {
        "schema_version": prep.REGISTRATION_VERSION,
        "run_id": "unit-recursive-v2",
        "scientific_parent": {
            "gate_decision": "fail",
            "failed_gate_extension_rule_acknowledged": True,
            "result": _artifact(files["parent_result"]),
        },
        "scientific_reentry": {
            "new_hypothesis_protocol": _artifact(files["new_protocol"]),
            "fresh_holdout_manifest": {
                **_artifact(files["fresh_holdout"]),
                "disjoint_from_parent": True,
                "outcomes_unread": True,
            },
            "prior_outcomes_excluded": True,
        },
        "registered_components": {
            "proposal_entrypoint": _artifact(files["proposal"]),
            "frozen_scorer": _artifact(files["scorer"]),
            "edit_family_manifest": _artifact(files["edit_family"]),
            "exact_command": ["powershell.exe", "-File", str(files["wrapper"])],
        },
        "resource_envelope": {
            "caps_confirmed_by_user": True,
            "hard_host_working_set_mb": 5632,
            "hard_combined_commit_mb": 9199,
            "gpu_commit_allowance_mb": 3567,
            "hard_cpu_pct": 50,
            "io_abort_mb_s": 50,
            "timeout_seconds": 3600,
            "swap_bytes": 0,
            "checkpoint_every_rounds": 1,
            "checkpoint_every_seconds": 300,
            "hard_cap_wrapper": _artifact(files["wrapper"]),
            "wrapper_validation_receipt": _artifact(files["wrapper_validation"]),
            "cleanup_script": _artifact(files["cleanup"]),
            "hard_cap_validation_status": "passed",
        },
        "source_universe": {
            "complete": True,
            "entries": [
                {"id": name, **_artifact(path)}
                for name, path in files.items()
                if name
                in {
                    "parent_result",
                    "new_protocol",
                    "fresh_holdout",
                    "proposal",
                    "scorer",
                    "edit_family",
                }
            ],
        },
    }
    registration_path = tmp_path / "registration.json"
    registration_path.write_bytes(prep.canonical_json_bytes(registration))
    return registration, registration_path


def test_incomplete_draft_fails_closed() -> None:
    report = prep.readiness_report(
        {
            "schema_version": prep.REGISTRATION_VERSION,
            "run_id": "draft",
            "scientific_parent": {
                "gate_decision": "fail",
                "failed_gate_extension_rule_acknowledged": True,
            },
        }
    )
    assert report["status"] == "blocked_preparation"
    assert report["scientific_run_authorized"] is False
    assert "missing:scientific_reentry" in report["blockers"]
    assert "awaiting_user_confirmation:resource_caps" not in report["blockers"]


def test_complete_registration_seals_run_specific_payload(tmp_path: Path) -> None:
    registration, registration_path = _complete_registration(tmp_path)
    assert prep.readiness_report(registration)["ready"] is True
    output = tmp_path / "sealed"
    receipt = prep.seal_run_pre_anchor(
        registration, registration_path=registration_path, output_dir=output
    )
    payload = json.loads((output / "run_pre_anchor_payload.json").read_text())
    assert receipt["status"] == "sealed_waiting_external_pre_anchor"
    assert payload["anchor_purpose"] == "run_authorization"
    assert payload["source_data_access_authorized"] is False
    assert "environment_lock" in payload["file_sha256"]


def test_prior_failure_cannot_be_reopened_without_fresh_holdout(tmp_path: Path) -> None:
    registration, _ = _complete_registration(tmp_path)
    registration["scientific_reentry"]["fresh_holdout_manifest"][
        "disjoint_from_parent"
    ] = False
    blockers = prep.registration_blockers(registration)
    assert "not_fresh:scientific_reentry.fresh_holdout_manifest.disjoint_from_parent" in blockers


def test_registered_scientific_artifacts_must_be_in_source_universe(tmp_path: Path) -> None:
    registration, _ = _complete_registration(tmp_path)
    registration["source_universe"]["entries"] = [
        entry
        for entry in registration["source_universe"]["entries"]
        if entry["id"] != "scorer"
    ]
    assert (
        "not_in_source_universe:registered_components.frozen_scorer"
        in prep.registration_blockers(registration)
    )


def test_authorization_requires_verified_anchor_and_same_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registration, registration_path = _complete_registration(tmp_path)
    output = tmp_path / "sealed"
    prep.seal_run_pre_anchor(
        registration, registration_path=registration_path, output_dir=output
    )
    payload = json.loads((output / "run_pre_anchor_payload.json").read_text())
    anchor = {
        "anchor_role": "pre_run",
        "proof_status": "bitcoin_verified",
        "target_sha256": canonical_json_sha256(payload),
        "bitcoin_verified_blocks": [
            {"height": 100, "attested_date": "2026-07-14 UTC"}
        ],
    }
    locked_environment = json.loads((output / "environment_lock.json").read_text())
    monkeypatch.setattr(prep, "runtime_environment", lambda: locked_environment)
    authorization = prep.authorize_run(
        registration=registration,
        registration_path=registration_path,
        payload=payload,
        anchor_receipt=anchor,
    )
    assert authorization["status"] == "authorized_for_registered_launch"
    pending = {**anchor, "proof_status": "calendar_submitted_pending_bitcoin"}
    with pytest.raises(ValueError, match="not independently Bitcoin-verified"):
        prep.authorize_run(
            registration=registration,
            registration_path=registration_path,
            payload=payload,
            anchor_receipt=pending,
        )


def test_mutated_registered_file_blocks_authorization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registration, registration_path = _complete_registration(tmp_path)
    output = tmp_path / "sealed"
    prep.seal_run_pre_anchor(
        registration, registration_path=registration_path, output_dir=output
    )
    payload = json.loads((output / "run_pre_anchor_payload.json").read_text())
    locked_environment = json.loads((output / "environment_lock.json").read_text())
    monkeypatch.setattr(prep, "runtime_environment", lambda: locked_environment)
    Path(payload["file_paths"]["scorer"]).write_text("mutated\n", encoding="utf-8")
    anchor = {
        "anchor_role": "pre_run",
        "proof_status": "bitcoin_verified",
        "target_sha256": canonical_json_sha256(payload),
        "bitcoin_verified_blocks": [
            {"height": 100, "attested_date": "2026-07-14 UTC"}
        ],
    }
    with pytest.raises(ValueError, match="file hash mismatch"):
        prep.authorize_run(
            registration=registration,
            registration_path=registration_path,
            payload=payload,
            anchor_receipt=anchor,
        )
