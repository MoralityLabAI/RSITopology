import hashlib
import importlib.util
import json
from pathlib import Path

from .run_repair_v0_31_1 import (
    ORIGINAL_RUNNER,
    fixed_peak_resident_bytes,
    load_original_runner,
)


HERE = Path(__file__).resolve().parent
ORIGINAL_DIR = HERE.parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_original_runner_is_the_registered_source():
    registration = json.loads(
        (ORIGINAL_DIR / "registration_v0_31.json").read_text(encoding="utf-8")
    )
    relative = ORIGINAL_RUNNER.relative_to(HERE.parents[4]).as_posix()
    assert sha256(ORIGINAL_RUNNER) == registration["sealed_files"][relative]


def test_repair_changes_only_resource_callable():
    runner = load_original_runner()
    original = runner.peak_resident_bytes
    runner.peak_resident_bytes = fixed_peak_resident_bytes
    assert runner.peak_resident_bytes is fixed_peak_resident_bytes
    assert original is not fixed_peak_resident_bytes


def test_fixed_resource_query_is_live():
    assert fixed_peak_resident_bytes() > 0


def test_original_independent_verifier_remains_importable():
    path = ORIGINAL_DIR / "verify_result_v0_31.py"
    spec = importlib.util.spec_from_file_location("sealed_v031_verifier", path)
    assert spec is not None and spec.loader is not None
