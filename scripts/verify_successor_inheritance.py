#!/usr/bin/env python3
"""Verify the pinned source, port, and paired semantic ablation locally."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research/successor_inheritance"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True,
                        help="New directory for results, test logs, and verification receipt")
    args = parser.parse_args()
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    provenance = json.loads((RESEARCH / "provenance.json").read_text())
    sources = []
    for item in provenance["source"]["files"]:
        path = ROOT / item["archived_path"]
        content = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        if blob != item["git_blob_sha1"]:
            raise RuntimeError(f"Source archive differs from pinned Git blob: {path}")
        sources.append({"path": item["path"], "git_blob_sha1": blob, "sha256": sha256(path)})

    commands = []

    def run(label: str, command: list[str], cwd: Path) -> None:
        result = subprocess.run([sys.executable, *command], cwd=cwd,
                                capture_output=True, text=True, encoding="utf-8")
        (out / f"{label}.txt").write_bytes((result.stdout + result.stderr).encode("utf-8"))
        commands.append({"label": label, "arguments": command,
                         "cwd": str(cwd.relative_to(ROOT)), "exit_code": result.returncode})
        if result.returncode:
            raise RuntimeError(f"{label} failed; see {out / (label + '.txt')}")

    source = RESEARCH / "source_pr12"
    run("source_tests", ["-m", "unittest", "discover", "-s", "tests", "-p",
                         "test_successor_inheritance.py", "-v"], source)
    run("ported_tests", ["-m", "unittest", "discover", "-s", "tests", "-p",
                         "test_successor_inheritance.py", "-v"], ROOT)
    run("semantic_tests", ["-m", "pytest", "tests/test_successor_semantic.py", "-q"], ROOT)
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        source_rows, source_summary = temp / "trials.jsonl", temp / "summary.json"
        run("source_run", ["scripts/run_successor_inheritance.py", "--out", str(source_rows),
                           "--summary-out", str(source_summary)], source)
        regenerated = json.loads(source_summary.read_text())
        original = json.loads((source / "results/successor_inheritance/v1_summary.json").read_text())
        if regenerated != original:
            raise RuntimeError("Source regeneration disagrees with recorded summary")
        source_observations = [json.loads(line) for line in source_rows.read_text().splitlines()]
        for semantic in (False, True):
            name = "semantic_v1" if semantic else "v1"
            command = ["scripts/run_successor_inheritance.py", "--out", str(out / f"{name}_trials.jsonl"),
                       "--summary-out", str(out / f"{name}_summary.json")]
            run(name + "_run", command + (["--semantic"] if semantic else []), ROOT)
        port_rows = [json.loads(line) for line in (out / "v1_trials.jsonl").read_text().splitlines()]
        semantic_rows = [json.loads(line) for line in (out / "semantic_v1_trials.jsonl").read_text().splitlines()]
        port_summary = json.loads((out / "v1_summary.json").read_text())
        semantic_summary = json.loads((out / "semantic_v1_summary.json").read_text())
        checks = {
            "source_summary_matches_recorded_json": regenerated == original,
            "port_summary_matches_recorded_json": port_summary == original,
            "all_1024_port_rows_equal_independent_source": port_rows == source_observations,
            "semantic_projection_equals_baseline_rows": [
                {k: v for k, v in row.items() if k != "semantic"} for row in semantic_rows] == port_rows,
            "semantic_projection_equals_baseline_summary": {
                k: v for k, v in semantic_summary.items() if k != "semantic_comparison"} == port_summary,
            "semantic_oracle_agreement": semantic_summary["semantic_comparison"]["oracle_disagreements"] == 0,
            "trial_counts": len(port_rows) == len(semantic_rows) == len(source_observations) == 1024,
        }
        if not all(checks.values()):
            raise RuntimeError(f"Reproduction discrepancy: {checks}")
        source_generated_hashes = {"trials_sha256": sha256(source_rows),
                                   "summary_sha256": sha256(source_summary)}

    implementation = ["rsi_topology/successor_inheritance.py", "scripts/run_successor_inheritance.py",
                      "scripts/verify_successor_inheritance.py", "tests/test_successor_inheritance.py",
                      "tests/test_successor_semantic.py", "protocols/successor_inheritance_v1.json"]
    receipt = {
        "status": "verified_synthetic_model_free", "utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": provenance["source"]["commit"],
        "destination_base_commit": provenance["destination"]["base_commit"],
        "python": sys.version, "platform": platform.platform(),
        "packages": {p: importlib.metadata.version(p) for p in ("numpy", "scipy", "scikit-learn", "pytest")},
        "checks": checks, "source_files": sources, "commands": commands,
        "source_regenerated_file_hashes": source_generated_hashes,
        "comparison_policy": "Parsed JSON equality: int/float spellings and CRLF/LF are not scientific discrepancies",
        "implementation_sha256": {p: sha256(ROOT / p) for p in implementation},
        "output_sha256": {p.name: sha256(p) for p in sorted(out.iterdir()) if p.is_file()},
        "semantic_comparison": semantic_summary["semantic_comparison"],
    }
    (out / "verification.json").write_bytes((json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"checks": checks, "semantic_comparison": receipt["semantic_comparison"],
                      "receipt": str(out / "verification.json")}, indent=2))


if __name__ == "__main__":
    main()
