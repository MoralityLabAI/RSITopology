"""Write-once prospective verifier for ASMP-9 v0.61."""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import psutil

from stack_verifier_v0_61 import run_primary


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REGISTRATION = HERE / "verification_registration_v0_61.json"
CELLS = HERE / "verification_cells_v0_61.json"
OUTPUT = HERE / "VERIFY_RESULT_v0_61.json"
REPLAY = HERE / "independent_replay_v0_61.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_tests(registration: dict) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        registration["test_command"].split(),
        cwd=REPO,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def replay_is_import_independent() -> bool:
    tree = ast.parse(REPLAY.read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = {
        "stack_verifier_v0_61",
        "bounded_context_degree",
        "finite_sample_tiers",
        "contamination_radius",
        "selection_channel",
    }
    return not any(
        any(token in module for token in forbidden)
        for module in imported
    )


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError("verification result is write-once")
    if not REGISTRATION.exists():
        raise FileNotFoundError("prospective registration is required")
    started = time.perf_counter()
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    cells = json.loads(CELLS.read_text(encoding="utf-8"))

    mismatches = {}
    for group in ("source_sha256", "burned_inputs_sha256"):
        for relative, expected in registration[group].items():
            actual = sha256(REPO / relative)
            if actual != expected:
                mismatches[relative] = {"actual": actual, "expected": expected}
    source_is_ancestor = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            registration["source_commit"],
            "HEAD",
        ],
        cwd=REPO,
        check=False,
    ).returncode == 0
    gates = {"H0": not mismatches and source_is_ancestor}

    tests = run_tests(registration)
    expected_pass = f"{registration['expected_test_count']} passed"
    gates["T0"] = tests.returncode == 0 and expected_pass in tests.stdout

    primary = run_primary(cells)
    gates.update(primary["gates"])

    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    replay_process = subprocess.run(
        [sys.executable, str(REPLAY), str(CELLS)],
        cwd=REPO,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    replay = (
        json.loads(replay_process.stdout)
        if replay_process.returncode == 0
        else {}
    )
    gates["I0"] = (
        replay_process.returncode == 0
        and replay_is_import_independent()
        and replay.get("fact_digest") == primary["fact_digest"]
        and replay.get("counts") == primary["counts"]
        and replay.get("gates") == primary["gates"]
        and replay.get("rows") == primary["rows"]
    )

    elapsed = time.perf_counter() - started
    resident = psutil.Process().memory_info().rss
    caps = registration["resource_caps"]
    gates["RESOURCE"] = (
        elapsed < caps["seconds"]
        and resident < caps["resident_bytes"]
        and caps["workers"] == 1
    )

    status = (
        "conditional_structured_choice_stack_verified"
        if all(gates.values())
        else "verification_failed"
    )
    result = {
        "cells_sha256": sha256(CELLS),
        "claim_boundary": registration["claim_boundary"],
        "gates": gates,
        "primary": primary,
        "registration_sha256": sha256(REGISTRATION),
        "replay": {
            "counts": replay.get("counts"),
            "fact_digest": replay.get("fact_digest"),
            "gates": replay.get("gates"),
            "import_independent": replay_is_import_independent(),
            "returncode": replay_process.returncode,
            "stderr": replay_process.stderr,
        },
        "resource": {
            "elapsed_seconds": elapsed,
            "resident_bytes": resident,
            "workers": 1,
        },
        "schema": "asmp9-v0.61-verification-result-v1",
        "source_commit": registration["source_commit"],
        "source_mismatches": mismatches,
        "source_was_ancestor": source_is_ancestor,
        "status": status,
        "tests": {
            "returncode": tests.returncode,
            "stderr": tests.stderr,
            "stdout": tests.stdout,
        },
    }
    OUTPUT.write_bytes(
        (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    print(json.dumps({"gates": gates, "status": status}, indent=2))
    if not all(gates.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

