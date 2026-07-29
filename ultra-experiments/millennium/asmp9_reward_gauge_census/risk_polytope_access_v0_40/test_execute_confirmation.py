import json
from pathlib import Path

import pytest

from execute_confirmation import (
    PROTOCOL_ID,
    canonical_bytes,
    sha256_bytes,
    sha256_file,
    validate_registration,
)


def test_hash_helpers_are_canonical(tmp_path: Path):
    payload = {"b": 2, "a": 1}
    path = tmp_path / "payload.json"
    path.write_bytes(canonical_bytes(payload))
    assert sha256_file(path) == sha256_bytes(canonical_bytes(payload))


def test_executor_rejects_unregistered_state(tmp_path: Path):
    path = tmp_path / "registration.json"
    path.write_text(
        json.dumps(
            {
                "status": "prospective_unregistered",
                "protocol_id": PROTOCOL_ID,
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="registered_prereveal"):
        validate_registration(path)
