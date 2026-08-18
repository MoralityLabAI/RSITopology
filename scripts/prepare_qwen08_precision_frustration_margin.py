"""Seal the analysis-only frustration-margin correction authorization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rsi_topology.godel_capture import canonical_json_bytes, runtime_environment, sha256_file, write_once_or_equal  # noqa: E402


def main(args: argparse.Namespace) -> None:
    parent = json.loads(args.parent_authorization.read_text(encoding="utf-8-sig"))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    refs = [line.strip() for line in subprocess.run(["git", "branch", "-r", "--contains", commit], cwd=ROOT, check=True, capture_output=True, text=True).stdout.splitlines() if line.strip()]
    if not refs:
        raise ValueError("implementation commit is not on a remote ref")
    sources = {
        "protocol": args.protocol.resolve(),
        "analysis_module": ROOT / "rsi_topology" / "qwen_precision_frustration_margin.py",
        "analysis_entrypoint": ROOT / "scripts" / "run_qwen08_precision_frustration_margin.py",
        "preparation_entrypoint": Path(__file__).resolve(),
        "filtration_module": ROOT / "rsi_topology" / "qwen_precision_filtration_w1.py",
        "parent_precision_module": ROOT / "rsi_topology" / "qwen_precision_context.py",
        "discovery_module": ROOT / "rsi_topology" / "discovery.py",
        "detached_launcher": ROOT / "scripts" / "start_qwen08_l19_precision_context_v0_1_1.ps1",
    }
    for path in sources.values():
        relative = str(path.resolve().relative_to(ROOT))
        if subprocess.run(["git", "ls-files", "--error-unmatch", relative], cwd=ROOT, capture_output=True).returncode:
            raise ValueError(f"source is not committed: {relative}")
        if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", relative], cwd=ROOT).returncode:
            raise ValueError(f"source differs from HEAD: {relative}")
    output = args.output_dir.resolve()
    command = [
        sys.executable, str(sources["analysis_entrypoint"]),
        "--authorization", str(args.output.resolve()),
        "--protocol", str(args.protocol.resolve()),
        "--scientific-protocol", str(args.scientific_protocol.resolve()),
        "--manifest", str(args.manifest.resolve()),
        "--filtration-result", str(args.filtration_result.resolve()),
        "--filtration-run-receipt", str(args.filtration_run_receipt.resolve()),
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
            "environment_lock": runtime_environment(),
            "scientific_protocol_sha256": sha256_file(args.protocol),
            "parent_scientific_protocol": {"path": str(args.scientific_protocol.resolve()), "sha256": sha256_file(args.scientific_protocol)},
            "filtration_result": {"path": str(args.filtration_result.resolve()), "sha256": sha256_file(args.filtration_result)},
            "filtration_run_receipt": {"path": str(args.filtration_run_receipt.resolve()), "sha256": sha256_file(args.filtration_run_receipt)},
            "source_paths": {name: str(path.resolve()) for name, path in sorted(sources.items())},
            "source_sha256": {name: sha256_file(path) for name, path in sorted(sources.items())},
            "exact_inner_command": command,
            "output_dir": str(output),
            "wrapper_output_dir": str((output / "_wrapper").resolve()),
            "checkpoint_strategy": "immutable_hash_chained_blocks_of_16_paired_resamples",
            "capture_parameters": {"output_dir": str(output)},
            "outcomes_consumed": False,
            "generation": False,
            "gradients": False,
            "weight_mutation": False,
        }
    )
    write_once_or_equal(args.output.resolve(), canonical_json_bytes(value))
    print(json.dumps({"status": "sealed", "implementation_commit": commit, "authorization_sha256": sha256_file(args.output)}, indent=2))


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--parent-authorization", type=Path, required=True)
    value.add_argument("--protocol", type=Path, required=True)
    value.add_argument("--scientific-protocol", type=Path, required=True)
    value.add_argument("--manifest", type=Path, required=True)
    value.add_argument("--filtration-result", type=Path, required=True)
    value.add_argument("--filtration-run-receipt", type=Path, required=True)
    value.add_argument("--output-dir", type=Path, required=True)
    value.add_argument("--output", type=Path, required=True)
    value.add_argument("--run-id", required=True)
    return value


if __name__ == "__main__":
    main(parser().parse_args())
