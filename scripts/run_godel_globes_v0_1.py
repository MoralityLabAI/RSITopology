"""Generate, validate, replay, and package Godel Globes v0.1 receipts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Mapping

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.godel_analysis import analyze_godel_capture, write_analysis_bundle
from rsi_topology.godel_capture import (
    build_synthetic_capture,
    canonical_json_bytes,
    canonical_json_sha256,
    generate_prompt_manifest,
    load_protocol,
    runtime_environment,
    sha256_file,
    validate_capture_index,
    validate_prompt_manifest,
    write_once_or_equal,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = ROOT / "protocols" / "godel_globes_falsification_v0_1.json"
HARD_CAP_VALIDATION_SCHEMA = "qwen_holonomy_hard_cap_validation_v0_1"


def _load_manifest(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    validate_prompt_manifest(value)
    return value


def _validate_hard_cap_receipt(
    validation: Mapping[str, object],
    *,
    wrapper_path: Path,
    cleanup_path: Path,
) -> None:
    """Bind a passed validation receipt to the exact launch machinery."""

    if validation.get("schema_version") != HARD_CAP_VALIDATION_SCHEMA:
        raise ValueError("hard-cap validation receipt schema is not registered")
    validation_status = validation.get(
        "hard_cap_validation_status", validation.get("status")
    )
    if validation_status != "passed":
        raise ValueError("hard-cap validation receipt is not passed")
    checks = validation.get("checks")
    required_checks = {
        "success_path",
        "memory_cap_configured",
        "memory_probe_terminated",
        "memory_probe_stayed_at_cap",
        "cpu_cap_configured",
        "cpu_probe_completed",
        "cpu_observed_below_margin",
        "io_monitor_aborted",
        "timeout_aborted",
        "all_cleanup_passed",
    }
    if not isinstance(checks, Mapping) or any(
        checks.get(name) is not True for name in required_checks
    ):
        raise ValueError("hard-cap validation receipt lacks passing required checks")

    expected = {
        "wrapper": wrapper_path.resolve(),
        "cleanup": cleanup_path.resolve(),
    }
    for name, registered_path in expected.items():
        artifact = validation.get(name)
        if not isinstance(artifact, Mapping):
            raise ValueError(f"hard-cap validation receipt lacks {name} binding")
        artifact_path = Path(str(artifact.get("path", ""))).resolve()
        if artifact_path != registered_path:
            raise ValueError(f"hard-cap validation {name} path mismatch")
        current_hash = sha256_file(registered_path)
        if artifact.get("sha256") != current_hash:
            raise ValueError(f"hard-cap validation {name} hash mismatch")


def generate(args: argparse.Namespace) -> None:
    protocol = load_protocol(args.protocol)
    manifest = generate_prompt_manifest(
        protocol_sha256=sha256_file(args.protocol),
        seed=int(protocol["prompt_design"]["seed"]),
        families=protocol["prompt_design"]["families"],
        subconditions_per_family=int(
            protocol["prompt_design"]["subconditions_per_family"]
        ),
        context_shards=int(protocol["prompt_design"]["context_shards"]),
        prompts_per_half=int(
            protocol["prompt_design"][
                "prompts_per_subcondition_per_half_per_shard"
            ]
        ),
    )
    write_once_or_equal(args.output, canonical_json_bytes(manifest))
    print(
        json.dumps(
            {
                "status": "prompt_manifest_written",
                "path": str(args.output.resolve()),
                "sha256": sha256_file(args.output),
                "prompt_count": manifest["prompt_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )


def smoke_capture(args: argparse.Namespace) -> None:
    protocol = load_protocol(args.protocol)
    manifest = _load_manifest(args.prompt_manifest)
    index = build_synthetic_capture(
        output_dir=args.output_dir,
        manifest=manifest,
        protocol=protocol,
        ambient_dimension=args.ambient_dimension,
        planted_rank=args.planted_rank,
        seed=args.seed,
        bfloat16_failure=args.bfloat16_failure,
    )
    validate_capture_index(
        index_path=index, manifest=manifest, protocol=protocol
    )
    print(
        json.dumps(
            {
                "status": "synthetic_capture_written_and_validated",
                "capture_index": str(index.resolve()),
                "sha256": sha256_file(index),
            },
            indent=2,
            sort_keys=True,
        )
    )


def analyze(args: argparse.Namespace) -> None:
    protocol = load_protocol(args.protocol)
    manifest = _load_manifest(args.prompt_manifest)
    store = validate_capture_index(
        index_path=args.capture_index,
        manifest=manifest,
        protocol=protocol,
    )
    result = analyze_godel_capture(
        store=store,
        manifest=manifest,
        protocol=protocol,
        seed=args.seed,
    )
    release = write_analysis_bundle(args.output_dir, result)
    print(
        json.dumps(
            {
                "status": "analysis_complete",
                "summary": result["summary"],
                "release_manifest": release,
            },
            indent=2,
            sort_keys=True,
        )
    )


def verify(args: argparse.Namespace) -> None:
    protocol = load_protocol(args.protocol)
    manifest = _load_manifest(args.prompt_manifest)
    store = validate_capture_index(
        index_path=args.capture_index,
        manifest=manifest,
        protocol=protocol,
    )
    release_path = args.release_dir / "release_manifest.json"
    release = json.loads(release_path.read_text(encoding="utf-8"))
    failures = []
    if release.get("protocol_sha256") != canonical_json_sha256(protocol):
        failures.append("protocol_hash_mismatch")
    if release.get("prompt_manifest_sha256") != canonical_json_sha256(manifest):
        failures.append("prompt_manifest_hash_mismatch")
    if release.get("capture_index_sha256") != sha256_file(store.index_path):
        failures.append("capture_index_hash_mismatch")
    for name, expected in release.get("file_sha256", {}).items():
        path = args.release_dir / name
        if not path.is_file() or sha256_file(path) != expected:
            failures.append(f"release_file_hash_mismatch:{name}")
    status = "passed" if not failures else "failed"
    print(json.dumps({"status": status, "failures": failures}, indent=2, sort_keys=True))
    if failures:
        raise SystemExit(1)


def prepare_authorization(args: argparse.Namespace) -> None:
    protocol = load_protocol(args.protocol)
    manifest = _load_manifest(args.prompt_manifest)
    if not args.confirm_caps:
        raise ValueError("live authorization requires --confirm-caps")
    if args.batch_size < 1:
        raise ValueError("batch size must be positive")
    validation = json.loads(
        args.hard_cap_validation_receipt.read_text(encoding="utf-8-sig")
    )
    _validate_hard_cap_receipt(
        validation,
        wrapper_path=args.hard_cap_wrapper,
        cleanup_path=args.cleanup_script,
    )
    if args.swap_bytes != 0:
        raise ValueError("live capture requires --swap-bytes 0")
    positive = (
        args.memory_mb,
        args.cpu_percent,
        args.io_mb_s,
        args.timeout_seconds,
        args.gpu_allowance_mb,
        args.checkpoint_every_seconds,
        args.host_reserve_mb,
    )
    if any(value <= 0 for value in positive):
        raise ValueError("all resource caps must be explicit and positive")
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
    dirty = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if dirty:
        raise ValueError("capture authorization requires a clean committed worktree")
    remote_contains = subprocess.run(
        ["git", "branch", "-r", "--contains", commit],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not remote_contains:
        raise ValueError("capture authorization requires the implementation commit on a remote ref")
    capture_entrypoint = ROOT / "scripts" / "capture_godel_globes_qwen.py"
    source_paths = {
        "capture_entrypoint": capture_entrypoint,
        "godel_capture_module": ROOT / "rsi_topology" / "godel_capture.py",
        "godel_analysis_module": ROOT / "rsi_topology" / "godel_analysis.py",
        "discovery_module": ROOT / "rsi_topology" / "discovery.py",
        "attestation_module": ROOT / "rsi_topology" / "attestation.py",
        "bifiltration_module": ROOT / "rsi_topology" / "bifiltration.py",
        "sectioning_module": ROOT / "rsi_topology" / "sectioning.py",
    }
    authorization = {
        "schema_version": "godel_capture_authorization_v0_1",
        "status": "authorized_for_godel_capture",
        "run_id": args.run_id,
        "protocol_sha256": sha256_file(args.protocol),
        "prompt_manifest_sha256": sha256_file(args.prompt_manifest),
        "prompt_manifest_canonical_sha256": canonical_json_sha256(manifest),
        "caps_confirmed_by_user": True,
        "hard_cap_validation_status": "passed",
        "implementation_commit": commit,
        "remote_refs_containing_commit": remote_contains.splitlines(),
        "environment_lock": runtime_environment(),
        "source_sha256": {
            name: sha256_file(path) for name, path in sorted(source_paths.items())
        },
        "source_paths": {
            name: str(path.resolve()) for name, path in sorted(source_paths.items())
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
            "host_reserve_mb": args.host_reserve_mb,
            "minimum_free_memory_mb": args.memory_mb + args.host_reserve_mb,
            "cpu_percent": args.cpu_percent,
            "io_mb_s": args.io_mb_s,
            "timeout_seconds": args.timeout_seconds,
            "gpu_allowance_mb": args.gpu_allowance_mb,
            "checkpoint_every_seconds": args.checkpoint_every_seconds,
            "swap_bytes": args.swap_bytes,
        },
        "capture_contract": {
            "outcomes_read": False,
            "generation": False,
            "gradients": False,
            "weight_mutation": False,
            "runtime_precisions": protocol["runtime_precisions"],
            "candidate_sites": protocol["candidate_sites"],
        },
        "capture_parameters": {
            "output_dir": str(args.capture_output_dir.resolve()),
            "device": args.device,
            "batch_size": args.batch_size,
        },
        "checkpoint_strategy": (
            "durable_partial_group_at_or_before_registered_interval_and_"
            "full_shard_half_group"
        ),
        "wrapper_output_dir": str(
            (args.capture_output_dir.resolve() / "_wrapper")
        ),
        "exact_inner_command": [
            sys.executable,
            str(capture_entrypoint.resolve()),
            "--protocol",
            str(args.protocol.resolve()),
            "--prompt-manifest",
            str(args.prompt_manifest.resolve()),
            "--authorization",
            str(args.output.resolve()),
            "--output-dir",
            str(args.capture_output_dir.resolve()),
            "--device",
            args.device,
            "--batch-size",
            str(args.batch_size),
        ],
    }
    write_once_or_equal(args.output, canonical_json_bytes(authorization))
    print(json.dumps(authorization, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    sub = value.add_subparsers(dest="command", required=True)

    generate_parser = sub.add_parser("generate-prompts")
    generate_parser.add_argument("--output", type=Path, required=True)
    generate_parser.set_defaults(function=generate)

    smoke_parser = sub.add_parser("make-smoke-capture")
    smoke_parser.add_argument("--prompt-manifest", type=Path, required=True)
    smoke_parser.add_argument("--output-dir", type=Path, required=True)
    smoke_parser.add_argument("--ambient-dimension", type=int, default=24)
    smoke_parser.add_argument("--planted-rank", type=int)
    smoke_parser.add_argument("--seed", type=int, default=2026071602)
    smoke_parser.add_argument("--bfloat16-failure", action="store_true")
    smoke_parser.set_defaults(function=smoke_capture)

    analyze_parser = sub.add_parser("analyze")
    analyze_parser.add_argument("--prompt-manifest", type=Path, required=True)
    analyze_parser.add_argument("--capture-index", type=Path, required=True)
    analyze_parser.add_argument("--output-dir", type=Path, required=True)
    analyze_parser.add_argument("--seed", type=int, default=2026071603)
    analyze_parser.set_defaults(function=analyze)

    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--prompt-manifest", type=Path, required=True)
    verify_parser.add_argument("--capture-index", type=Path, required=True)
    verify_parser.add_argument("--release-dir", type=Path, required=True)
    verify_parser.set_defaults(function=verify)

    prepare_parser = sub.add_parser("prepare-authorization")
    prepare_parser.add_argument("--run-id", required=True)
    prepare_parser.add_argument("--prompt-manifest", type=Path, required=True)
    prepare_parser.add_argument("--hard-cap-wrapper", type=Path, required=True)
    prepare_parser.add_argument(
        "--hard-cap-validation-receipt", type=Path, required=True
    )
    prepare_parser.add_argument("--cleanup-script", type=Path, required=True)
    prepare_parser.add_argument("--memory-mb", type=int, required=True)
    prepare_parser.add_argument("--host-reserve-mb", type=int, required=True)
    prepare_parser.add_argument("--cpu-percent", type=int, required=True)
    prepare_parser.add_argument("--io-mb-s", type=int, required=True)
    prepare_parser.add_argument("--timeout-seconds", type=int, required=True)
    prepare_parser.add_argument("--gpu-allowance-mb", type=int, required=True)
    prepare_parser.add_argument(
        "--checkpoint-every-seconds", type=int, required=True
    )
    prepare_parser.add_argument("--swap-bytes", type=int, required=True)
    prepare_parser.add_argument("--confirm-caps", action="store_true")
    prepare_parser.add_argument("--output", type=Path, required=True)
    prepare_parser.add_argument("--capture-output-dir", type=Path, required=True)
    prepare_parser.add_argument("--device", default="cuda")
    prepare_parser.add_argument("--batch-size", type=int, required=True)
    prepare_parser.set_defaults(function=prepare_authorization)
    return value


def main() -> None:
    args = parser().parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
