"""Create a sealed v0.1.1 analysis authorization from the completed captures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rsi_topology.godel_capture import canonical_json_bytes, sha256_file, write_once_or_equal  # noqa: E402
from rsi_topology.qwen_precision_context_v0_1_1 import AMENDMENT_ID, validate_amendment  # noqa: E402


def _remote_commit() -> tuple[str, list[str]]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    refs = [
        line.strip()
        for line in subprocess.run(
            ["git", "branch", "-r", "--contains", commit],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        if line.strip()
    ]
    if not refs:
        raise ValueError("implementation commit is not present on a remote ref")
    return commit, refs


def main(args: argparse.Namespace) -> None:
    parent = json.loads(args.parent_authorization.read_text(encoding="utf-8-sig"))
    if parent.get("status") != "authorized_for_analysis":
        raise ValueError("parent authorization is not an analysis authorization")
    validate_amendment(args.compute_amendment, scientific_protocol_path=args.protocol)
    commit, refs = _remote_commit()
    source_paths = {
        "analysis_entrypoint_v0_1_1": ROOT / "scripts" / "run_qwen08_l19_precision_context_v0_1_1.py",
        "compute_module_v0_1_1": ROOT / "rsi_topology" / "qwen_precision_context_v0_1_1.py",
        "compute_amendment_v0_1_1": args.compute_amendment.resolve(),
        "reference_analysis_entrypoint": ROOT / "scripts" / "run_qwen08_l19_precision_context.py",
        "reference_precision_context_module": ROOT / "rsi_topology" / "qwen_precision_context.py",
        "discovery_module": ROOT / "rsi_topology" / "discovery.py",
        "godel_analysis_module": ROOT / "rsi_topology" / "godel_analysis.py",
    }
    for path in source_paths.values():
        relative = str(path.resolve().relative_to(ROOT))
        if subprocess.run(
            ["git", "ls-files", "--error-unmatch", relative], cwd=ROOT, capture_output=True
        ).returncode != 0:
            raise ValueError(f"authorization source is not committed: {relative}")
        if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", relative], cwd=ROOT).returncode:
            raise ValueError(f"authorization source differs from HEAD: {relative}")
    output = args.output_dir.resolve()
    command = [
        sys.executable,
        str(source_paths["analysis_entrypoint_v0_1_1"].resolve()),
        "--authorization", str(args.output.resolve()),
        "--compute-amendment", str(args.compute_amendment.resolve()),
        "--protocol", str(args.protocol.resolve()),
        "--manifest", str(Path(parent["source_paths"].get("prompt_manifest", args.manifest)).resolve()),
        "--separation-receipt", str(Path(parent["prompt_separation_receipt"]["path"]).resolve()),
        "--pair-receipt", str(Path(parent["precision_pair_receipt"]["path"]).resolve()),
        "--fourbit-base-index", str(Path(parent["capture_indices"]["fourbit_base"]["path"]).resolve()),
        "--fourbit-naive-index", str(Path(parent["capture_indices"]["fourbit_naive"]["path"]).resolve()),
        "--float16-base-index", str(Path(parent["capture_indices"]["float16_base"]["path"]).resolve()),
        "--float16-naive-index", str(Path(parent["capture_indices"]["float16_naive"]["path"]).resolve()),
        "--output-dir", str(output),
    ]
    value = dict(parent)
    value.update(
        {
            "run_id": args.run_id,
            "implementation_commit": commit,
            "remote_refs_containing_commit": refs,
            "source_paths": {name: str(path.resolve()) for name, path in sorted(source_paths.items())},
            "source_sha256": {name: sha256_file(path) for name, path in sorted(source_paths.items())},
            "compute_amendment": {
                "protocol_id": AMENDMENT_ID,
                "path": str(args.compute_amendment.resolve()),
                "sha256": sha256_file(args.compute_amendment),
            },
            "exact_inner_command": command,
            "output_dir": str(output),
            "wrapper_output_dir": str((output / "_wrapper").resolve()),
            "checkpoint_strategy": "immutable_hash_chained_blocks_of_16_outer_draws_per_cell",
            "capture_parameters": {"output_dir": str(output)},
        }
    )
    write_once_or_equal(args.output.resolve(), canonical_json_bytes(value))
    print(json.dumps(value, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--parent-authorization", type=Path, required=True)
    value.add_argument("--compute-amendment", type=Path, required=True)
    value.add_argument("--protocol", type=Path, required=True)
    value.add_argument("--manifest", type=Path, required=True)
    value.add_argument("--run-id", required=True)
    value.add_argument("--output-dir", type=Path, required=True)
    value.add_argument("--output", type=Path, required=True)
    return value


if __name__ == "__main__":
    main(parser().parse_args())
