"""Prepare and validate the prereveal Qwen holonomy causal prompt split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.godel_capture import (
    canonical_json_bytes,
    runtime_environment,
    sha256_file,
    write_once_or_equal,
)
from rsi_topology.qwen_holonomy_causal import (
    generate_causal_outer_manifest,
    load_and_validate_outer_manifest,
    validate_causal_outer_manifest,
)
from rsi_topology.qwen_state_capture import development_state


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = ROOT / "protocols" / "qwen_holonomy_causal_transfer_v0_1.json"
DEFAULT_GEOMETRY_MANIFEST = ROOT / "protocols" / "godel_globes_prompt_manifest_v0_1.json"


def _protocol(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("protocol_id") != "qwen_holonomy_causal_transfer_v0_1":
        raise ValueError("unexpected causal protocol_id")
    if value.get("new_invariant_levels") is not False:
        raise ValueError("causal protocol introduces an invariant level")
    return value


def generate(args: argparse.Namespace) -> None:
    protocol = _protocol(args.protocol)
    geometry = json.loads(args.geometry_manifest.read_text(encoding="utf-8"))
    split = protocol["prompt_splits"]
    value = generate_causal_outer_manifest(
        protocol_sha256=sha256_file(args.protocol),
        geometry_manifest_sha256=sha256_file(args.geometry_manifest),
        seed=int(split["causal_seed"]),
        families=geometry["families"],
        subconditions_per_family=int(geometry["subconditions_per_family"]),
        context_shards=int(geometry["context_shards"]),
        prompts_per_cell=2,
    )
    validate_causal_outer_manifest(value, geometry_manifest=geometry)
    write_once_or_equal(args.output, canonical_json_bytes(value))
    print(
        json.dumps(
            {
                "status": "causal_outer_manifest_written",
                "path": str(args.output.resolve()),
                "sha256": sha256_file(args.output),
                "protocol_sha256": sha256_file(args.protocol),
                "geometry_manifest_sha256": sha256_file(args.geometry_manifest),
                "prompt_count": value["prompt_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )


def verify(args: argparse.Namespace) -> None:
    protocol = _protocol(args.protocol)
    value = load_and_validate_outer_manifest(
        args.outer_manifest, geometry_manifest_path=args.geometry_manifest
    )
    failures = []
    if value.get("protocol_sha256") != sha256_file(args.protocol):
        failures.append("protocol_hash_mismatch")
    if value.get("prompt_count") != int(
        protocol["prompt_splits"]["causal_prompt_count"]
    ):
        failures.append("prompt_count_mismatch")
    status = "passed" if not failures else "failed"
    print(
        json.dumps(
            {
                "status": status,
                "failures": failures,
                "outer_manifest_sha256": sha256_file(args.outer_manifest),
            },
            indent=2,
            sort_keys=True,
        )
    )
    if failures:
        raise SystemExit(1)


def prepare_state_authorization(args: argparse.Namespace) -> None:
    protocol = _protocol(args.protocol)
    development_state(protocol, args.state_id)
    if not args.confirm_caps:
        raise ValueError("state authorization requires --confirm-caps")
    if args.swap_bytes != 0:
        raise ValueError("state capture requires --swap-bytes 0")
    if args.batch_size < 1:
        raise ValueError("batch size must be positive")
    caps = (
        args.memory_mb,
        args.cpu_percent,
        args.io_mb_s,
        args.timeout_seconds,
        args.gpu_allowance_mb,
        args.checkpoint_every_seconds,
    )
    if any(value <= 0 for value in caps):
        raise ValueError("all state-capture caps must be explicit and positive")
    validation = json.loads(
        args.hard_cap_validation_receipt.read_text(encoding="utf-8")
    )
    validation_status = validation.get(
        "hard_cap_validation_status", validation.get("status")
    )
    if validation_status != "passed":
        raise ValueError("hard-cap validation receipt is not passed")
    for path in (args.hard_cap_wrapper, args.cleanup_script):
        if not path.is_file():
            raise FileNotFoundError(path)

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    remote_refs = subprocess.run(
        ["git", "branch", "-r", "--contains", commit],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not remote_refs:
        raise ValueError("authorization implementation commit is not on a remote ref")
    source_paths = {
        "capture_entrypoint": ROOT / "scripts" / "capture_qwen_holonomy_state.py",
        "state_capture_module": ROOT / "rsi_topology" / "qwen_state_capture.py",
        "godel_capture_module": ROOT / "rsi_topology" / "godel_capture.py",
        "causal_prompt_module": ROOT / "rsi_topology" / "qwen_holonomy_causal.py",
        "preparation_entrypoint": Path(__file__).resolve(),
    }
    for path in source_paths.values():
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path.relative_to(ROOT))],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if tracked.returncode != 0:
            raise ValueError(f"authorization source is not committed: {path}")
        changed = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", str(path.relative_to(ROOT))],
            cwd=ROOT,
        )
        if changed.returncode != 0:
            raise ValueError(f"authorization source differs from HEAD: {path}")
    capture_entrypoint = source_paths["capture_entrypoint"]
    value = {
        "schema_version": "qwen_holonomy_state_capture_authorization_v0_1",
        "status": "authorized_for_qwen_holonomy_state_capture",
        "run_id": args.run_id,
        "state_id": args.state_id,
        "wrapper_output_dir": str(
            (args.capture_output_dir.resolve() / "_wrapper").resolve()
        ),
        "checkpoint_strategy": "one_state_site_context_shard_geometry_half",
        "protocol_sha256": sha256_file(args.protocol),
        "geometry_manifest_sha256": sha256_file(args.geometry_manifest),
        "caps_confirmed_by_user": True,
        "hard_cap_validation_status": "passed",
        "implementation_commit": commit,
        "remote_refs_containing_commit": remote_refs.splitlines(),
        "environment_lock": runtime_environment(),
        "source_paths": {
            name: str(path.resolve()) for name, path in sorted(source_paths.items())
        },
        "source_sha256": {
            name: sha256_file(path) for name, path in sorted(source_paths.items())
        },
        "hard_cap_validation_receipt": {
            "path": str(args.hard_cap_validation_receipt.resolve()),
            "sha256": sha256_file(args.hard_cap_validation_receipt),
        },
        "hard_cap_wrapper": {
            "path": str(args.hard_cap_wrapper.resolve()),
            "sha256": sha256_file(args.hard_cap_wrapper),
        },
        "cleanup_script": {
            "path": str(args.cleanup_script.resolve()),
            "sha256": sha256_file(args.cleanup_script),
        },
        "resource_caps": {
            "memory_mb": args.memory_mb,
            "cpu_percent": args.cpu_percent,
            "io_mb_s": args.io_mb_s,
            "timeout_seconds": args.timeout_seconds,
            "gpu_allowance_mb": args.gpu_allowance_mb,
            "checkpoint_every_seconds": args.checkpoint_every_seconds,
            "swap_bytes": args.swap_bytes,
        },
        "capture_parameters": {
            "output_dir": str(args.capture_output_dir.resolve()),
            "batch_size": args.batch_size,
            "quantization": args.quantization,
        },
        "capture_contract": {
            "generation": False,
            "gradients": False,
            "weight_mutation": False,
            "state_id": args.state_id,
            "activation_sites": protocol["development_model"]["activation_sites"],
        },
        "exact_inner_command": [
            sys.executable,
            str(capture_entrypoint.resolve()),
            "--protocol",
            str(args.protocol.resolve()),
            "--geometry-manifest",
            str(args.geometry_manifest.resolve()),
            "--authorization",
            str(args.output.resolve()),
            "--state-id",
            args.state_id,
            "--output-dir",
            str(args.capture_output_dir.resolve()),
            "--batch-size",
            str(args.batch_size),
            "--quantization",
            args.quantization,
        ],
    }
    write_once_or_equal(args.output, canonical_json_bytes(value))
    print(json.dumps(value, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    value.add_argument(
        "--geometry-manifest", type=Path, default=DEFAULT_GEOMETRY_MANIFEST
    )
    sub = value.add_subparsers(dest="command", required=True)

    generate_parser = sub.add_parser("generate-outer")
    generate_parser.add_argument("--output", type=Path, required=True)
    generate_parser.set_defaults(function=generate)

    verify_parser = sub.add_parser("verify-outer")
    verify_parser.add_argument("--outer-manifest", type=Path, required=True)
    verify_parser.set_defaults(function=verify)

    authorization_parser = sub.add_parser("prepare-state-authorization")
    authorization_parser.add_argument("--run-id", required=True)
    authorization_parser.add_argument("--state-id", required=True)
    authorization_parser.add_argument("--hard-cap-wrapper", type=Path, required=True)
    authorization_parser.add_argument(
        "--hard-cap-validation-receipt", type=Path, required=True
    )
    authorization_parser.add_argument("--cleanup-script", type=Path, required=True)
    authorization_parser.add_argument("--memory-mb", type=int, required=True)
    authorization_parser.add_argument("--cpu-percent", type=int, required=True)
    authorization_parser.add_argument("--io-mb-s", type=int, required=True)
    authorization_parser.add_argument("--timeout-seconds", type=int, required=True)
    authorization_parser.add_argument("--gpu-allowance-mb", type=int, required=True)
    authorization_parser.add_argument(
        "--checkpoint-every-seconds", type=int, required=True
    )
    authorization_parser.add_argument("--swap-bytes", type=int, required=True)
    authorization_parser.add_argument("--batch-size", type=int, required=True)
    authorization_parser.add_argument(
        "--quantization", choices=("4bit", "float16"), default="4bit"
    )
    authorization_parser.add_argument("--capture-output-dir", type=Path, required=True)
    authorization_parser.add_argument("--output", type=Path, required=True)
    authorization_parser.add_argument("--confirm-caps", action="store_true")
    authorization_parser.set_defaults(function=prepare_state_authorization)
    return value


def main() -> None:
    args = parser().parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
