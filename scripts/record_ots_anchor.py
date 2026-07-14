"""Record an OpenTimestamps proof against its exact target without overclaiming it."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_once_or_equal(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"write-once anchor artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _command(cli: Path, *args: str) -> list[str]:
    return (["node", str(cli)] if cli.suffix.lower() == ".js" else [str(cli)]) + list(args)


def record(
    *,
    target: Path,
    proof: Path,
    ots_cli: Path,
    role: str,
    output_dir: Path,
    submitted_at_utc: str | None,
) -> dict[str, Any]:
    completed = subprocess.run(
        _command(ots_cli, "info", str(proof)),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    info_text = completed.stdout
    match = re.search(r"File sha256 hash:\s*([0-9a-f]{64})", info_text)
    if not match:
        raise ValueError("OTS info did not report a SHA-256 target")
    target_hash = sha256_file(target)
    if match.group(1) != target_hash:
        raise ValueError("OTS proof does not bind the supplied target")
    calendars = sorted(set(re.findall(r"PendingAttestation\('([^']+)'\)", info_text)))
    bitcoin_matches = re.findall(r"BitcoinBlockHeaderAttestation\((\d+)\)", info_text)
    verification = subprocess.run(
        _command(ots_cli, "verify", "-f", str(target), str(proof)),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    verification_text = verification.stdout
    verified_blocks = re.findall(
        r"Success! Bitcoin block (\d+) attests existence as of ([^\r\n]+)",
        verification_text,
    )
    if verified_blocks:
        proof_status = "bitcoin_verified"
    elif calendars and "Pending confirmation in Bitcoin blockchain" in verification_text:
        proof_status = "calendar_submitted_pending_bitcoin"
    else:
        raise ValueError("OTS proof has neither calendar nor Bitcoin attestation")
    package_json = ots_cli.parent / "package.json"
    package = json.loads(package_json.read_text(encoding="utf-8"))
    info_path = output_dir / "ots_info.txt"
    write_once_or_equal(info_path, info_text.encode("utf-8"))
    verification_path = output_dir / "ots_verify.txt"
    write_once_or_equal(verification_path, verification_text.encode("utf-8"))
    scopes = {
        "schema_chronology": (
            "Forward chronology anchor for a prereveal schema only. It can date the design "
            "but can never authorize source-data access or substitute for the later "
            "run-specific pre-anchor."
        ),
        "forward_v1_release": (
            "Forward anchor only. It cannot prove that the v1 protocol predated the v1 run. "
            "While pending, it records external calendar submissions but is not yet an "
            "independently Bitcoin-verifiable timestamp."
        ),
        "pre_run": (
            "Prospective pre-run anchor. Source-data access remains prohibited while pending. "
            "After independent Bitcoin verification, it may authorize the registered runner "
            "to read the sealed source universe."
        ),
        "post_run": (
            "Post-run anchor for the exact write-once run receipt. A pending calendar "
            "submission permits only a provisional release; the final chronology claim "
            "requires independent Bitcoin verification."
        ),
    }
    if role not in scopes:
        raise ValueError(f"unknown anchor role: {role}")
    receipt = {
        "schema_version": "ots_anchor_receipt_v1",
        "anchor_role": role,
        "target_file": target.name,
        "target_sha256": target_hash,
        "proof_file": proof.name,
        "proof_sha256": sha256_file(proof),
        "proof_status": proof_status,
        "submitted_at_utc": submitted_at_utc
        or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "calendar_urls": calendars,
        "bitcoin_attestations_in_proof": [int(value) for value in bitcoin_matches],
        "bitcoin_verified_blocks": [
            {"height": int(height), "attested_date": date.strip()}
            for height, date in verified_blocks
        ],
        "client": {
            "name": package["name"],
            "version": package["version"],
            "package_json_sha256": sha256_file(package_json),
            "cli_sha256": sha256_file(ots_cli),
        },
        "info_stdout_sha256": sha256_file(info_path),
        "verification_stdout_sha256": sha256_file(verification_path),
        "chronology_scope": scopes[role],
    }
    receipt_path = output_dir / "anchor_receipt.json"
    write_once_or_equal(
        receipt_path,
        (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--ots-cli", type=Path, required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--submitted-at-utc")
    args = parser.parse_args()
    receipt = record(
        target=args.target.resolve(),
        proof=args.proof.resolve(),
        ots_cli=args.ots_cli.resolve(),
        role=args.role,
        output_dir=args.output_dir.resolve(),
        submitted_at_utc=args.submitted_at_utc,
    )
    print(
        json.dumps(
            {
                "proof_status": receipt["proof_status"],
                "target_sha256": receipt["target_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
