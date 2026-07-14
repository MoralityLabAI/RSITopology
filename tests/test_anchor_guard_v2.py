from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from rsi_topology.anchor_guard_v2 import (
    canonical_json_sha256,
    release_anchor_guard,
    sha256_file,
    validate_post_anchor,
    validate_pre_anchor,
)


def _fixture(tmp_path: Path) -> tuple[dict, dict[str, Path]]:
    protocol = tmp_path / "protocol.json"
    environment = tmp_path / "environment.json"
    protocol.write_text("protocol-v2\n", encoding="utf-8")
    environment.write_text("environment-v2\n", encoding="utf-8")
    files = {"protocol": protocol, "environment_lock": environment}
    payload = {
        "anchor_purpose": "run_authorization",
        "environment_lock_included": True,
        "file_sha256": {name: sha256_file(path) for name, path in files.items()},
    }
    return payload, files


def test_pre_anchor_requires_verified_bitcoin_and_exact_environment(tmp_path: Path) -> None:
    payload, files = _fixture(tmp_path)
    receipt = {
        "anchor_role": "pre_run",
        "proof_status": "bitcoin_verified",
        "target_sha256": canonical_json_sha256(payload),
        "bitcoin_verified_blocks": [
            {"height": 999, "attested_date": "2026-07-14 UTC"}
        ],
    }
    assert validate_pre_anchor(payload=payload, anchor_receipt=receipt, files=files)[
        "status"
    ] == "valid_pre_anchor"
    pending = {**receipt, "proof_status": "calendar_submitted_pending_bitcoin"}
    with pytest.raises(ValueError, match="not independently Bitcoin-verified"):
        validate_pre_anchor(payload=payload, anchor_receipt=pending, files=files)


def test_pre_anchor_rejects_swapped_environment(tmp_path: Path) -> None:
    payload, files = _fixture(tmp_path)
    receipt = {
        "anchor_role": "pre_run",
        "proof_status": "bitcoin_verified",
        "target_sha256": canonical_json_sha256(payload),
        "bitcoin_verified_blocks": [
            {"height": 999, "attested_date": "2026-07-14 UTC"}
        ],
    }
    files["environment_lock"].write_text("swapped\n", encoding="utf-8")
    with pytest.raises(ValueError, match="environment_lock"):
        validate_pre_anchor(payload=payload, anchor_receipt=receipt, files=files)


def test_pre_anchor_rejects_unsubstantiated_verified_label(tmp_path: Path) -> None:
    payload, files = _fixture(tmp_path)
    receipt = {
        "anchor_role": "pre_run",
        "proof_status": "bitcoin_verified",
        "target_sha256": canonical_json_sha256(payload),
        "bitcoin_verified_blocks": [],
    }
    with pytest.raises(ValueError, match="no independently verified Bitcoin block"):
        validate_pre_anchor(payload=payload, anchor_receipt=receipt, files=files)


def test_schema_chronology_anchor_cannot_authorize_source_access(tmp_path: Path) -> None:
    payload, files = _fixture(tmp_path)
    payload["anchor_purpose"] = "schema_chronology_only"
    receipt = {
        "anchor_role": "pre_run",
        "proof_status": "bitcoin_verified",
        "target_sha256": canonical_json_sha256(payload),
        "bitcoin_verified_blocks": [
            {"height": 999, "attested_date": "2026-07-14 UTC"}
        ],
    }
    with pytest.raises(ValueError, match="not run-specific authorization"):
        validate_pre_anchor(payload=payload, anchor_receipt=receipt, files=files)


def test_post_anchor_binds_exact_receipt_and_may_be_pending(tmp_path: Path) -> None:
    run_receipt = tmp_path / "run_receipt.json"
    run_receipt.write_text('{"status":"complete"}\n', encoding="utf-8")
    anchor = {
        "anchor_role": "post_run",
        "proof_status": "calendar_submitted_pending_bitcoin",
        "target_sha256": sha256_file(run_receipt),
        "calendar_urls": ["https://example.invalid/calendar"],
    }
    result = validate_post_anchor(run_receipt_path=run_receipt, anchor_receipt=anchor)
    assert result["release_label"] == "provisional_pending_bitcoin_upgrade"
    run_receipt.write_text('{"status":"changed"}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="does not bind"):
        validate_post_anchor(run_receipt_path=run_receipt, anchor_receipt=anchor)


def test_pending_post_anchor_requires_external_calendar(tmp_path: Path) -> None:
    run_receipt = tmp_path / "run_receipt.json"
    run_receipt.write_text('{"status":"complete"}\n', encoding="utf-8")
    anchor = {
        "anchor_role": "post_run",
        "proof_status": "calendar_submitted_pending_bitcoin",
        "target_sha256": sha256_file(run_receipt),
        "calendar_urls": [],
    }
    with pytest.raises(ValueError, match="no serialized external calendar"):
        validate_post_anchor(run_receipt_path=run_receipt, anchor_receipt=anchor)


def test_release_guard_requires_both_sides(tmp_path: Path) -> None:
    payload, files = _fixture(tmp_path)
    pre = {
        "anchor_role": "pre_run",
        "proof_status": "bitcoin_verified",
        "target_sha256": canonical_json_sha256(payload),
        "bitcoin_verified_blocks": [
            {"height": 999, "attested_date": "2026-07-14 UTC"}
        ],
    }
    run_receipt = tmp_path / "run_receipt.json"
    run_receipt.write_text('{"status":"complete"}\n', encoding="utf-8")
    post = {
        "anchor_role": "post_run",
        "proof_status": "calendar_submitted_pending_bitcoin",
        "target_sha256": hashlib.sha256(run_receipt.read_bytes()).hexdigest(),
        "calendar_urls": ["https://example.invalid/calendar"],
    }
    result = release_anchor_guard(
        pre_payload=payload,
        pre_anchor_receipt=pre,
        pre_files=files,
        run_receipt_path=run_receipt,
        post_anchor_receipt=post,
    )
    assert result["status"] == "release_anchor_guard_passed"
    assert result["post_anchor"]["release_label"] == "provisional_pending_bitcoin_upgrade"
