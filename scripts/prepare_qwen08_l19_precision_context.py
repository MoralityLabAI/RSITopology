"""Prepare fresh prompts and hard-capped Qwen precision/context authorizations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rsi_topology.godel_capture import (  # noqa: E402
    canonical_json_bytes,
    runtime_environment,
    sha256_file,
    write_once_or_equal,
)
from rsi_topology.qwen_precision_context import (  # noqa: E402
    PRECISIONS,
    STATES,
    generate_manifest,
    load_protocol,
    precision_manifest_pair_receipt,
    prompt_separation_receipt,
    validate_manifest,
)


CAPTURE_WRAPPER_SCHEMA = "qwen_holonomy_state_capture_authorization_v0_1"
ANALYSIS_WRAPPER_SCHEMA = "qwen_holonomy_geometry_analysis_authorization_v0_1"
DEFAULT_PROTOCOL = ROOT / "protocols" / "qwen08_l19_precision_context_v0_1.json"
DEFAULT_CAUSAL = ROOT / "protocols" / "qwen_holonomy_causal_transfer_v0_1.json"
DEFAULT_PRIOR = ROOT / "protocols" / "qwen08_context_stageb_prompt_manifest_v0_1.json"


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _remote_commit() -> tuple[str, list[str]]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    refs = subprocess.run(
        ["git", "branch", "-r", "--contains", commit],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    refs = [item.strip() for item in refs if item.strip()]
    if not refs:
        raise ValueError("implementation commit is not present on a remote ref")
    return commit, refs


def _require_clean_tracked(paths: Mapping[str, Path]) -> None:
    for path in paths.values():
        relative = str(path.resolve().relative_to(ROOT))
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", relative],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if tracked.returncode != 0:
            raise ValueError(f"authorization source is uncommitted: {relative}")
        changed = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", relative], cwd=ROOT)
        if changed.returncode != 0:
            raise ValueError(f"authorization source differs from HEAD: {relative}")


def _validated_hard_cap_artifacts(args: argparse.Namespace) -> dict[str, Any]:
    validation = _json(args.hard_cap_validation_receipt.resolve())
    if validation.get("hard_cap_validation_status") != "passed":
        raise ValueError("hard-cap validation receipt is not a pass")
    artifacts = {
        "hard_cap_validation_receipt": args.hard_cap_validation_receipt.resolve(),
        "hard_cap_wrapper": args.hard_cap_wrapper.resolve(),
        "cleanup_script": args.cleanup_script.resolve(),
    }
    for path in artifacts.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    if validation.get("wrapper", {}).get("sha256") != sha256_file(artifacts["hard_cap_wrapper"]):
        raise ValueError("validation receipt does not bind wrapper")
    if validation.get("cleanup", {}).get("sha256") != sha256_file(artifacts["cleanup_script"]):
        raise ValueError("validation receipt does not bind cleanup script")
    return {
        name: {"path": str(path), "sha256": sha256_file(path)}
        for name, path in artifacts.items()
    }


def _caps(args: argparse.Namespace) -> dict[str, int]:
    if not args.confirm_caps:
        raise ValueError("authorization requires --confirm-caps")
    values = {
        "memory_mb": args.memory_mb,
        "cpu_percent": args.cpu_percent,
        "io_mb_s": args.io_mb_s,
        "timeout_seconds": args.timeout_seconds,
        "gpu_allowance_mb": args.gpu_allowance_mb,
        "checkpoint_every_seconds": args.checkpoint_every_seconds,
        "swap_bytes": args.swap_bytes,
    }
    if any(int(values[key]) <= 0 for key in values if key != "swap_bytes"):
        raise ValueError("all resource caps must be positive")
    if values["swap_bytes"] != 0:
        raise ValueError("registered run requires zero deliberate swap")
    try:
        import psutil

        free_memory_mb = int(psutil.virtual_memory().available / (1024 * 1024))
    except (ImportError, AttributeError):
        free_memory_mb = 0
    required_memory_mb = int(args.memory_mb + args.host_reserve_mb)
    if free_memory_mb < required_memory_mb:
        raise ValueError(
            f"insufficient free physical memory: {free_memory_mb}MB < {required_memory_mb}MB"
        )
    if args.gpu_allowance_mb > 1:
        completed = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.free",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        gpu_free_mb = min(int(line.strip()) for line in completed.stdout.splitlines() if line.strip())
        required_gpu_mb = int(args.gpu_allowance_mb + args.gpu_reserve_mb)
        if gpu_free_mb < required_gpu_mb:
            raise ValueError(
                f"insufficient free GPU memory: {gpu_free_mb}MB < {required_gpu_mb}MB"
            )
    else:
        gpu_free_mb = 0
        required_gpu_mb = 0
    values.update(
        {
            "host_reserve_mb": int(args.host_reserve_mb),
            "minimum_free_memory_mb": required_memory_mb,
            "gpu_reserve_mb": int(args.gpu_reserve_mb),
            "free_physical_memory_mb_at_authorization": free_memory_mb,
            "free_gpu_memory_mb_at_authorization": gpu_free_mb,
            "minimum_free_gpu_memory_mb": required_gpu_mb,
        }
    )
    return values


def generate(args: argparse.Namespace) -> None:
    protocol = load_protocol(args.protocol)
    manifest = generate_manifest(protocol_path=args.protocol)
    validate_manifest(manifest, protocol_path=args.protocol)
    separation = prompt_separation_receipt(
        manifest, compared_manifest_paths=[args.prior_manifest]
    )
    if separation["passed"] is not True:
        raise ValueError("fresh prompt separation failed")
    pair = precision_manifest_pair_receipt(manifest)
    if pair["identical_except_runtime_precision"] is not True:
        raise ValueError("precision prompt payloads differ")
    write_once_or_equal(args.manifest_output.resolve(), canonical_json_bytes(manifest))
    write_once_or_equal(args.separation_output.resolve(), canonical_json_bytes(separation))
    write_once_or_equal(args.pair_output.resolve(), canonical_json_bytes(pair))
    print(
        json.dumps(
            {
                "status": "written",
                "protocol_id": protocol["protocol_id"],
                "manifest": {"path": str(args.manifest_output.resolve()), "sha256": sha256_file(args.manifest_output)},
                "separation": {"path": str(args.separation_output.resolve()), "sha256": sha256_file(args.separation_output)},
                "pair": {"path": str(args.pair_output.resolve()), "sha256": sha256_file(args.pair_output)},
            },
            indent=2,
            sort_keys=True,
        )
    )


def verify(args: argparse.Namespace) -> None:
    manifest = _json(args.manifest.resolve())
    validate_manifest(manifest, protocol_path=args.protocol)
    separation = _json(args.separation_receipt.resolve())
    pair = _json(args.pair_receipt.resolve())
    expected_separation = prompt_separation_receipt(
        manifest, compared_manifest_paths=[args.prior_manifest]
    )
    expected_pair = precision_manifest_pair_receipt(manifest)
    if separation != expected_separation or separation.get("passed") is not True:
        raise ValueError("separation receipt is not reproducible")
    if pair != expected_pair or pair.get("identical_except_runtime_precision") is not True:
        raise ValueError("precision-pair receipt is not reproducible")
    print(json.dumps({"status": "passed", "manifest_sha256": sha256_file(args.manifest)}, sort_keys=True))


def _base_authorization(
    args: argparse.Namespace,
    *,
    status: str,
    source_paths: Mapping[str, Path],
    exact_command: list[str],
    output_dir: Path,
    wrapper_schema: str,
) -> dict[str, Any]:
    protocol = load_protocol(args.protocol)
    if sha256_file(args.causal_protocol) != protocol["model_lock"]["causal_protocol_sha256"]:
        raise ValueError("causal protocol differs from the scientific model lock")
    manifest = _json(args.manifest.resolve())
    validate_manifest(manifest, protocol_path=args.protocol)
    _require_clean_tracked(source_paths)
    commit, refs = _remote_commit()
    hard_cap = _validated_hard_cap_artifacts(args)
    separation = _json(args.separation_receipt.resolve())
    if separation.get("passed") is not True:
        raise ValueError("capture/analysis authorization requires passing separation")
    pair = _json(args.pair_receipt.resolve())
    if pair.get("identical_except_runtime_precision") is not True:
        raise ValueError("capture/analysis authorization requires identical prompt pair")
    return {
        "schema_version": wrapper_schema,
        "status": status,
        "run_id": args.run_id,
        "caps_confirmed_by_user": True,
        "implementation_commit": commit,
        "remote_refs_containing_commit": refs,
        "environment_lock": runtime_environment(),
        "scientific_protocol_sha256": sha256_file(args.protocol),
        "causal_protocol_sha256": sha256_file(args.causal_protocol),
        "prompt_manifest_sha256": sha256_file(args.manifest),
        "prompt_separation_receipt": {"path": str(args.separation_receipt.resolve()), "sha256": sha256_file(args.separation_receipt)},
        "precision_pair_receipt": {"path": str(args.pair_receipt.resolve()), "sha256": sha256_file(args.pair_receipt)},
        "source_paths": {name: str(path.resolve()) for name, path in sorted(source_paths.items())},
        "source_sha256": {name: sha256_file(path) for name, path in sorted(source_paths.items())},
        **hard_cap,
        "resource_caps": _caps(args),
        "wrapper_output_dir": str((output_dir / "_wrapper").resolve()),
        "checkpoint_strategy": "one_state_site_context_shard_geometry_half" if status == "authorized_for_capture" else "one_precision_then_nested_bootstrap_progress",
        "capture_parameters": {"output_dir": str(output_dir.resolve())},
        "exact_inner_command": exact_command,
        "outcomes_consumed": False,
        "generation": False,
        "gradients": False,
        "weight_mutation": False,
    }


def prepare_capture(args: argparse.Namespace) -> None:
    protocol = load_protocol(args.protocol)
    if args.state not in STATES or args.precision not in PRECISIONS:
        raise ValueError("capture arm is not registered")
    if args.batch_size != int(protocol["resource_contract"]["capture"]["batch_size"]):
        raise ValueError("capture batch size differs from protocol")
    expected_caps = protocol["resource_contract"]["capture"]
    for field in (
        "memory_mb", "cpu_percent", "io_mb_s", "timeout_seconds",
        "gpu_allowance_mb", "checkpoint_every_seconds", "swap_bytes",
    ):
        if int(getattr(args, field)) != int(expected_caps[field]):
            raise ValueError(f"capture cap differs from protocol: {field}")
    entrypoint = ROOT / "scripts" / "capture_qwen08_l19_precision_context.py"
    source_paths = {
        "capture_entrypoint": entrypoint,
        "precision_context_module": ROOT / "rsi_topology" / "qwen_precision_context.py",
        "godel_capture_module": ROOT / "rsi_topology" / "godel_capture.py",
        "state_capture_module": ROOT / "rsi_topology" / "qwen_state_capture.py",
        "preparation_entrypoint": Path(__file__).resolve(),
    }
    command = [
        sys.executable,
        str(entrypoint.resolve()),
        "--causal-protocol", str(args.causal_protocol.resolve()),
        "--scientific-protocol", str(args.protocol.resolve()),
        "--geometry-manifest", str(args.manifest.resolve()),
        "--authorization", str(args.output.resolve()),
        "--state", args.state,
        "--precision", args.precision,
        "--output-dir", str(args.capture_output_dir.resolve()),
        "--batch-size", str(args.batch_size),
    ]
    value = _base_authorization(
        args,
        status="authorized_for_capture",
        source_paths=source_paths,
        exact_command=command,
        output_dir=args.capture_output_dir,
        wrapper_schema=CAPTURE_WRAPPER_SCHEMA,
    )
    value.update({
        "state": args.state,
        "precision": args.precision,
        "output_dir": str(args.capture_output_dir.resolve()),
        "batch_size": args.batch_size,
    })
    write_once_or_equal(args.output.resolve(), canonical_json_bytes(value))
    print(json.dumps(value, indent=2, sort_keys=True))


def prepare_analysis(args: argparse.Namespace) -> None:
    protocol = load_protocol(args.protocol)
    expected_caps = protocol["resource_contract"]["analysis"]
    for field in (
        "memory_mb", "cpu_percent", "io_mb_s", "timeout_seconds",
        "gpu_allowance_mb", "checkpoint_every_seconds", "swap_bytes",
    ):
        if int(getattr(args, field)) != int(expected_caps[field]):
            raise ValueError(f"analysis cap differs from protocol: {field}")
    entrypoint = ROOT / "scripts" / "run_qwen08_l19_precision_context.py"
    source_paths = {
        "analysis_entrypoint": entrypoint,
        "precision_context_module": ROOT / "rsi_topology" / "qwen_precision_context.py",
        "discovery_module": ROOT / "rsi_topology" / "discovery.py",
        "godel_analysis_module": ROOT / "rsi_topology" / "godel_analysis.py",
        "preparation_entrypoint": Path(__file__).resolve(),
    }
    index_args = [
        "--fourbit-base-index", str(args.fourbit_base_index.resolve()),
        "--fourbit-naive-index", str(args.fourbit_naive_index.resolve()),
        "--float16-base-index", str(args.float16_base_index.resolve()),
        "--float16-naive-index", str(args.float16_naive_index.resolve()),
    ]
    command = [
        sys.executable,
        str(entrypoint.resolve()),
        "--authorization", str(args.output.resolve()),
        "--protocol", str(args.protocol.resolve()),
        "--manifest", str(args.manifest.resolve()),
        "--separation-receipt", str(args.separation_receipt.resolve()),
        "--pair-receipt", str(args.pair_receipt.resolve()),
        *index_args,
        "--output-dir", str(args.analysis_output_dir.resolve()),
    ]
    value = _base_authorization(
        args,
        status="authorized_for_analysis",
        source_paths=source_paths,
        exact_command=command,
        output_dir=args.analysis_output_dir,
        wrapper_schema=ANALYSIS_WRAPPER_SCHEMA,
    )
    indices = {
        "fourbit_base": args.fourbit_base_index,
        "fourbit_naive": args.fourbit_naive_index,
        "float16_base": args.float16_base_index,
        "float16_naive": args.float16_naive_index,
    }
    for path in indices.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    value["capture_indices"] = {
        name: {"path": str(path.resolve()), "sha256": sha256_file(path)}
        for name, path in indices.items()
    }
    value["output_dir"] = str(args.analysis_output_dir.resolve())
    write_once_or_equal(args.output.resolve(), canonical_json_bytes(value))
    print(json.dumps(value, indent=2, sort_keys=True))


def _common(parent: argparse.ArgumentParser) -> None:
    parent.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parent.add_argument("--causal-protocol", type=Path, default=DEFAULT_CAUSAL)
    parent.add_argument("--manifest", type=Path, required=True)
    parent.add_argument("--separation-receipt", type=Path, required=True)
    parent.add_argument("--pair-receipt", type=Path, required=True)
    parent.add_argument("--run-id", required=True)
    parent.add_argument("--hard-cap-wrapper", type=Path, required=True)
    parent.add_argument("--hard-cap-validation-receipt", type=Path, required=True)
    parent.add_argument("--cleanup-script", type=Path, required=True)
    parent.add_argument("--memory-mb", type=int, required=True)
    parent.add_argument("--cpu-percent", type=int, required=True)
    parent.add_argument("--io-mb-s", type=int, required=True)
    parent.add_argument("--timeout-seconds", type=int, required=True)
    parent.add_argument("--gpu-allowance-mb", type=int, required=True)
    parent.add_argument("--checkpoint-every-seconds", type=int, required=True)
    parent.add_argument("--swap-bytes", type=int, required=True)
    parent.add_argument("--host-reserve-mb", type=int, required=True)
    parent.add_argument("--gpu-reserve-mb", type=int, required=True)
    parent.add_argument("--output", type=Path, required=True)
    parent.add_argument("--confirm-caps", action="store_true")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    sub = value.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate-manifest")
    gen.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    gen.add_argument("--prior-manifest", type=Path, default=DEFAULT_PRIOR)
    gen.add_argument("--manifest-output", type=Path, required=True)
    gen.add_argument("--separation-output", type=Path, required=True)
    gen.add_argument("--pair-output", type=Path, required=True)
    gen.set_defaults(function=generate)
    check = sub.add_parser("verify-manifest")
    check.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    check.add_argument("--prior-manifest", type=Path, default=DEFAULT_PRIOR)
    check.add_argument("--manifest", type=Path, required=True)
    check.add_argument("--separation-receipt", type=Path, required=True)
    check.add_argument("--pair-receipt", type=Path, required=True)
    check.set_defaults(function=verify)
    capture = sub.add_parser("prepare-capture-authorization")
    _common(capture)
    capture.add_argument("--state", choices=STATES, required=True)
    capture.add_argument("--precision", choices=PRECISIONS, required=True)
    capture.add_argument("--batch-size", type=int, required=True)
    capture.add_argument("--capture-output-dir", type=Path, required=True)
    capture.set_defaults(function=prepare_capture)
    analysis = sub.add_parser("prepare-analysis-authorization")
    _common(analysis)
    analysis.add_argument("--fourbit-base-index", type=Path, required=True)
    analysis.add_argument("--fourbit-naive-index", type=Path, required=True)
    analysis.add_argument("--float16-base-index", type=Path, required=True)
    analysis.add_argument("--float16-naive-index", type=Path, required=True)
    analysis.add_argument("--analysis-output-dir", type=Path, required=True)
    analysis.set_defaults(function=prepare_analysis)
    return value


if __name__ == "__main__":
    args = parser().parse_args()
    args.function(args)
