from pathlib import Path

from execute_confirmation import canonical_bytes, sha256_bytes, sha256_file


def test_canonical_bytes_are_stable():
    assert canonical_bytes({"b": 2, "a": 1}) == (
        b'{\n  "a": 1,\n  "b": 2\n}\n'
    )


def test_file_hash_matches_byte_hash(tmp_path: Path):
    path = tmp_path / "payload.bin"
    payload = b"sequential-risk-access\n"
    path.write_bytes(payload)
    assert sha256_file(path) == sha256_bytes(payload)
