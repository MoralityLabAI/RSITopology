"""Pure validation logic for the v2 OpenTimestamps anchor sandwich."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


PRE_RUN_VALID_STATUS = "bitcoin_verified"
POST_SUBMITTED_STATUSES = {
    "calendar_submitted_pending_bitcoin",
    "bitcoin_verified",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_sha256(value: Mapping[str, Any]) -> str:
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def validate_pre_anchor(
    *,
    payload: Mapping[str, Any],
    anchor_receipt: Mapping[str, Any],
    files: Mapping[str, Path],
) -> dict[str, Any]:
    """Validate the externally confirmed pre-anchor before any source read."""

    if payload.get("anchor_purpose") != "run_authorization":
        raise ValueError("pre-anchor payload is not run-specific authorization")
    if anchor_receipt.get("anchor_role") != "pre_run":
        raise ValueError("pre-anchor receipt has the wrong role")
    if anchor_receipt.get("proof_status") != PRE_RUN_VALID_STATUS:
        raise ValueError("pre-anchor is not independently Bitcoin-verified")
    verified_blocks = anchor_receipt.get("bitcoin_verified_blocks")
    if not isinstance(verified_blocks, list) or not verified_blocks:
        raise ValueError("pre-anchor has no independently verified Bitcoin block")
    target = canonical_json_sha256(payload)
    if anchor_receipt.get("target_sha256") != target:
        raise ValueError("pre-anchor target does not bind the supplied payload")
    registered = payload.get("file_sha256")
    if not isinstance(registered, dict) or not registered:
        raise ValueError("pre-anchor payload has no file universe")
    if set(registered) != set(files):
        raise ValueError("pre-anchor file universe is incomplete or contains extras")
    for name, path in files.items():
        if sha256_file(path) != registered[name]:
            raise ValueError(f"pre-anchor file hash mismatch: {name}")
    if payload.get("environment_lock_included") is not True:
        raise ValueError("environment lock is not inside the pre-anchor payload")
    return {
        "status": "valid_pre_anchor",
        "target_sha256": target,
        "bitcoin_verified_blocks": verified_blocks,
    }


def validate_post_anchor(
    *, run_receipt_path: Path, anchor_receipt: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate that the exact canonical run receipt was submitted or verified."""

    if anchor_receipt.get("anchor_role") != "post_run":
        raise ValueError("post-anchor receipt has the wrong role")
    status = str(anchor_receipt.get("proof_status"))
    if status not in POST_SUBMITTED_STATUSES:
        raise ValueError("post-anchor was not submitted to an external calendar")
    if status == "calendar_submitted_pending_bitcoin":
        calendars = anchor_receipt.get("calendar_urls")
        if not isinstance(calendars, list) or not calendars:
            raise ValueError("pending post-anchor has no serialized external calendar")
    if status == "bitcoin_verified":
        verified_blocks = anchor_receipt.get("bitcoin_verified_blocks")
        if not isinstance(verified_blocks, list) or not verified_blocks:
            raise ValueError("verified post-anchor has no independently verified block")
    target = sha256_file(run_receipt_path)
    if anchor_receipt.get("target_sha256") != target:
        raise ValueError("post-anchor does not bind the canonical run receipt")
    return {
        "status": "valid_post_submission",
        "target_sha256": target,
        "proof_status": status,
        "release_label": (
            "bitcoin_verified"
            if status == "bitcoin_verified"
            else "provisional_pending_bitcoin_upgrade"
        ),
    }


def release_anchor_guard(
    *,
    pre_payload: Mapping[str, Any],
    pre_anchor_receipt: Mapping[str, Any],
    pre_files: Mapping[str, Path],
    run_receipt_path: Path,
    post_anchor_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Refuse release unless both sides of the timestamp sandwich validate."""

    pre = validate_pre_anchor(
        payload=pre_payload,
        anchor_receipt=pre_anchor_receipt,
        files=pre_files,
    )
    post = validate_post_anchor(
        run_receipt_path=run_receipt_path,
        anchor_receipt=post_anchor_receipt,
    )
    return {
        "status": "release_anchor_guard_passed",
        "pre_anchor": pre,
        "post_anchor": post,
        "chronology_claim": "run_receipt_bracketed_by_external_pre_and_post_anchors",
    }
