import hashlib
import json
from pathlib import Path

import pytest

from execute_confirmation import (
    canonical_bytes,
    sha256_bytes,
    sha256_file,
    validate_registration,
)


def test_canonical_hash_helpers(tmp_path: Path) -> None:
    payload = {"b": 2, "a": 1}
    path = tmp_path / "payload.json"
    path.write_bytes(canonical_bytes(payload))
    assert sha256_file(path) == sha256_bytes(canonical_bytes(payload))
    assert sha256_file(path) == hashlib.sha256(path.read_bytes()).hexdigest()


def test_registration_rejects_unregistered_state(tmp_path: Path) -> None:
    path = tmp_path / "registration.json"
    path.write_text(
        json.dumps(
            {
                "status": "prospective_unregistered",
                "protocol_id": "asmp9-decision-relative-access-v0.38",
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="registered_prereveal"):
        validate_registration(path)

