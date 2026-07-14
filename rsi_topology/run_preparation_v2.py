"""Fail-closed preparation and authorization for proposal-recursion runs.

This module does not implement an editor, scorer, or recursive proposal loop.
It binds those future components to a complete registration and refuses to
authorize a launch unless the failed v1 branch has been replaced by a new
hypothesis with a fresh holdout, all resource controls are explicit, and a
run-specific pre-anchor is independently Bitcoin-verified.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

from rsi_topology.anchor_guard_v2 import validate_pre_anchor


REGISTRATION_VERSION = "proposal_recursive_run_preparation_v2_0_3"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def write_once_or_equal(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"write-once run-preparation artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _version(package: str) -> str:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def runtime_environment() -> dict[str, Any]:
    """Return stable runtime fields; omit utilization and free-memory values."""

    gpu: list[str] = []
    try:
        completed = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        gpu = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    except (FileNotFoundError, subprocess.SubprocessError):
        gpu = []
    return {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "packages": {
            "numpy": _version("numpy"),
            "torch": _version("torch"),
            "transformers": _version("transformers"),
        },
        "gpu_static": gpu,
    }


def _is_sha256(value: Any) -> bool:
    text = str(value).lower()
    return len(text) == 64 and all(character in "0123456789abcdef" for character in text)


def _path_present(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _artifact_blockers(
    value: Any, *, name: str, require_fresh: bool = False
) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"missing:{name}"]
    blockers: list[str] = []
    if not _path_present(value.get("path")):
        blockers.append(f"missing:{name}.path")
    if not _is_sha256(value.get("sha256")):
        blockers.append(f"missing_or_invalid:{name}.sha256")
    if require_fresh:
        if value.get("disjoint_from_parent") is not True:
            blockers.append(f"not_fresh:{name}.disjoint_from_parent")
        if value.get("outcomes_unread") is not True:
            blockers.append(f"outcomes_not_sealed:{name}.outcomes_unread")
    return blockers


def registration_blockers(registration: Mapping[str, Any]) -> list[str]:
    """Return every preregistration blocker without reading scientific files."""

    blockers: list[str] = []
    if registration.get("schema_version") != REGISTRATION_VERSION:
        blockers.append("invalid:schema_version")
    if not str(registration.get("run_id", "")).strip():
        blockers.append("missing:run_id")

    parent = registration.get("scientific_parent")
    if not isinstance(parent, Mapping):
        blockers.append("missing:scientific_parent")
    else:
        if parent.get("gate_decision") != "fail":
            blockers.append("invalid:scientific_parent.gate_decision_must_carry_v1_fail")
        if parent.get("failed_gate_extension_rule_acknowledged") is not True:
            blockers.append("missing:failed_gate_extension_rule_acknowledged")
        blockers.extend(
            _artifact_blockers(parent.get("result"), name="scientific_parent.result")
        )

    reentry = registration.get("scientific_reentry")
    if not isinstance(reentry, Mapping):
        blockers.append("missing:scientific_reentry")
    else:
        blockers.extend(
            _artifact_blockers(
                reentry.get("new_hypothesis_protocol"),
                name="scientific_reentry.new_hypothesis_protocol",
            )
        )
        blockers.extend(
            _artifact_blockers(
                reentry.get("fresh_holdout_manifest"),
                name="scientific_reentry.fresh_holdout_manifest",
                require_fresh=True,
            )
        )
        if reentry.get("prior_outcomes_excluded") is not True:
            blockers.append("invalid:scientific_reentry.prior_outcomes_excluded")

    components = registration.get("registered_components")
    if not isinstance(components, Mapping):
        blockers.append("missing:registered_components")
    else:
        for name in ("proposal_entrypoint", "frozen_scorer", "edit_family_manifest"):
            blockers.extend(
                _artifact_blockers(components.get(name), name=f"registered_components.{name}")
            )
        command = components.get("exact_command")
        if not isinstance(command, list) or len(command) < 2 or not all(
            isinstance(item, str) and item for item in command
        ):
            blockers.append("missing:registered_components.exact_command")

    resources = registration.get("resource_envelope")
    if not isinstance(resources, Mapping):
        blockers.append("missing:resource_envelope")
    else:
        if resources.get("caps_confirmed_by_user") is not True:
            blockers.append("awaiting_user_confirmation:resource_caps")
        for field in (
            "hard_host_working_set_mb",
            "hard_combined_commit_mb",
            "gpu_commit_allowance_mb",
            "hard_cpu_pct",
            "io_abort_mb_s",
            "timeout_seconds",
        ):
            try:
                valid = float(resources.get(field, 0)) > 0
            except (TypeError, ValueError):
                valid = False
            if not valid:
                blockers.append(f"invalid:resource_envelope.{field}")
        if int(resources.get("swap_bytes", -1)) != 0:
            blockers.append("invalid:resource_envelope.swap_bytes")
        if int(resources.get("checkpoint_every_rounds", 0)) <= 0:
            blockers.append("invalid:resource_envelope.checkpoint_every_rounds")
        if int(resources.get("checkpoint_every_seconds", 0)) <= 0:
            blockers.append("invalid:resource_envelope.checkpoint_every_seconds")
        blockers.extend(
            _artifact_blockers(
                resources.get("hard_cap_wrapper"),
                name="resource_envelope.hard_cap_wrapper",
            )
        )
        blockers.extend(
            _artifact_blockers(
                resources.get("wrapper_validation_receipt"),
                name="resource_envelope.wrapper_validation_receipt",
            )
        )
        blockers.extend(
            _artifact_blockers(
                resources.get("cleanup_script"),
                name="resource_envelope.cleanup_script",
            )
        )
        if resources.get("hard_cap_validation_status") != "passed":
            blockers.append("invalid:resource_envelope.hard_cap_validation_status")

    universe = registration.get("source_universe")
    if not isinstance(universe, Mapping):
        blockers.append("missing:source_universe")
    else:
        if universe.get("complete") is not True:
            blockers.append("incomplete:source_universe")
        entries = universe.get("entries")
        if not isinstance(entries, list) or not entries:
            blockers.append("missing:source_universe.entries")
        else:
            ids: list[str] = []
            for index, entry in enumerate(entries):
                if not isinstance(entry, Mapping):
                    blockers.append(f"invalid:source_universe.entries[{index}]")
                    continue
                entry_id = str(entry.get("id", ""))
                ids.append(entry_id)
                if not entry_id:
                    blockers.append(f"missing:source_universe.entries[{index}].id")
                if not _path_present(entry.get("path")):
                    blockers.append(f"missing:source_universe.entries[{index}].path")
                if not _is_sha256(entry.get("sha256")):
                    blockers.append(f"missing_or_invalid:source_universe.entries[{index}].sha256")
            if len(ids) != len(set(ids)):
                blockers.append("invalid:source_universe.duplicate_ids")
            declared_paths = {
                str(Path(str(entry["path"])).resolve())
                for entry in entries
                if isinstance(entry, Mapping) and _path_present(entry.get("path"))
            }
            required_artifacts: list[tuple[str, Any]] = []
            if isinstance(parent, Mapping):
                required_artifacts.append(("scientific_parent.result", parent.get("result")))
            if isinstance(reentry, Mapping):
                required_artifacts.extend(
                    (
                        ("scientific_reentry.new_hypothesis_protocol", reentry.get("new_hypothesis_protocol")),
                        ("scientific_reentry.fresh_holdout_manifest", reentry.get("fresh_holdout_manifest")),
                    )
                )
            if isinstance(components, Mapping):
                required_artifacts.extend(
                    (f"registered_components.{name}", components.get(name))
                    for name in ("proposal_entrypoint", "frozen_scorer", "edit_family_manifest")
                )
            for name, artifact in required_artifacts:
                if isinstance(artifact, Mapping) and _path_present(artifact.get("path")):
                    if str(Path(str(artifact["path"])).resolve()) not in declared_paths:
                        blockers.append(f"not_in_source_universe:{name}")

    if isinstance(resources, Mapping) and isinstance(components, Mapping):
        wrapper = resources.get("hard_cap_wrapper")
        command = components.get("exact_command")
        if isinstance(wrapper, Mapping) and isinstance(command, list) and len(command) >= 2:
            wrapper_path = str(Path(str(wrapper.get("path", ""))).resolve())
            command_paths = {
                str(Path(item).resolve())
                for item in command
                if isinstance(item, str) and ("\\" in item or "/" in item)
            }
            if wrapper_path not in command_paths:
                blockers.append("invalid:exact_command_does_not_invoke_hard_cap_wrapper")
    return sorted(set(blockers))


def readiness_report(registration: Mapping[str, Any]) -> dict[str, Any]:
    blockers = registration_blockers(registration)
    return {
        "schema_version": "proposal_recursive_run_readiness_v2",
        "run_id": registration.get("run_id"),
        "status": "ready_to_seal_run_pre_anchor" if not blockers else "blocked_preparation",
        "ready": not blockers,
        "blockers": blockers,
        "scientific_run_authorized": False,
        "next_transition": (
            "seal_complete_run_specific_pre_anchor_payload"
            if not blockers
            else "resolve_all_blockers_without_reading_outcomes"
        ),
    }


def _declared_files(registration: Mapping[str, Any]) -> dict[str, Path]:
    entries = registration["source_universe"]["entries"]
    files = {str(entry["id"]): Path(str(entry["path"])).resolve() for entry in entries}
    resources = registration["resource_envelope"]
    for logical_id, key in (
        ("hard_cap_wrapper", "hard_cap_wrapper"),
        ("wrapper_validation_receipt", "wrapper_validation_receipt"),
        ("cleanup_script", "cleanup_script"),
    ):
        files[f"resource:{logical_id}"] = Path(str(resources[key]["path"])).resolve()
    return files


def seal_run_pre_anchor(
    registration: Mapping[str, Any], *, registration_path: Path, output_dir: Path
) -> dict[str, Any]:
    """Hash the complete declared run universe and emit a non-authorized payload."""

    blockers = registration_blockers(registration)
    if blockers:
        raise ValueError(f"run registration is not sealable: {blockers}")
    declared = _declared_files(registration)
    missing = [name for name, path in declared.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"registered files missing: {missing}")
    expected = {
        str(entry["id"]): str(entry["sha256"]).lower()
        for entry in registration["source_universe"]["entries"]
    }
    resources = registration["resource_envelope"]
    expected.update(
        {
            "resource:hard_cap_wrapper": str(resources["hard_cap_wrapper"]["sha256"]).lower(),
            "resource:wrapper_validation_receipt": str(
                resources["wrapper_validation_receipt"]["sha256"]
            ).lower(),
            "resource:cleanup_script": str(resources["cleanup_script"]["sha256"]).lower(),
        }
    )
    for name, path in declared.items():
        actual = sha256_file(path)
        if actual != expected[name]:
            raise ValueError(f"registered hash mismatch: {name}")

    environment = runtime_environment()
    environment_path = output_dir / "environment_lock.json"
    write_once_or_equal(environment_path, canonical_json_bytes(environment))
    files = {
        **declared,
        "run_registration": registration_path.resolve(),
        "environment_lock": environment_path.resolve(),
    }
    file_hashes = {name: sha256_file(path) for name, path in sorted(files.items())}
    payload = {
        "schema_version": "proposal_recursive_run_pre_anchor_payload_v1",
        "anchor_purpose": "run_authorization",
        "run_id": registration["run_id"],
        "registration_sha256": sha256_file(registration_path),
        "environment_lock_included": True,
        "file_sha256": file_hashes,
        "file_paths": {name: str(path) for name, path in sorted(files.items())},
        "source_data_access_authorized": False,
        "authorization_condition": "independent Bitcoin verification plus runtime guard validation",
    }
    payload_path = output_dir / "run_pre_anchor_payload.json"
    write_once_or_equal(payload_path, canonical_json_bytes(payload))
    receipt = {
        "schema_version": "proposal_recursive_run_preparation_seal_v1",
        "status": "sealed_waiting_external_pre_anchor",
        "run_id": registration["run_id"],
        "registration_sha256": sha256_file(registration_path),
        "environment_lock_sha256": sha256_file(environment_path),
        "run_pre_anchor_payload_sha256": sha256_file(payload_path),
        "file_count": len(files),
        "scientific_run_authorized": False,
    }
    write_once_or_equal(output_dir / "preparation_seal_receipt.json", canonical_json_bytes(receipt))
    return receipt


def authorize_run(
    *,
    registration: Mapping[str, Any],
    registration_path: Path,
    payload: Mapping[str, Any],
    anchor_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Authorize only the exact registered command after all guards pass."""

    blockers = registration_blockers(registration)
    if blockers:
        raise ValueError(f"registration is not launch-ready: {blockers}")
    if payload.get("registration_sha256") != sha256_file(registration_path):
        raise ValueError("pre-anchor payload does not bind the registration")
    paths = payload.get("file_paths")
    if not isinstance(paths, Mapping) or set(paths) != set(payload.get("file_sha256", {})):
        raise ValueError("pre-anchor payload path universe is incomplete")
    files = {str(name): Path(str(path)).resolve() for name, path in paths.items()}
    pre = validate_pre_anchor(payload=payload, anchor_receipt=anchor_receipt, files=files)
    environment_path = files.get("environment_lock")
    if environment_path is None:
        raise ValueError("pre-anchor payload omits environment_lock")
    locked_environment = json.loads(environment_path.read_text(encoding="utf-8"))
    if locked_environment != runtime_environment():
        raise ValueError("runtime environment differs from the pre-anchored lock")
    command = list(registration["registered_components"]["exact_command"])
    return {
        "schema_version": "proposal_recursive_run_authorization_v1",
        "status": "authorized_for_registered_launch",
        "run_id": registration["run_id"],
        "registration_sha256": sha256_file(registration_path),
        "pre_anchor": pre,
        "exact_command": command,
        "exact_command_sha256": canonical_json_sha256(command),
        "resource_envelope": registration["resource_envelope"],
        "authorization_scope": "one launch of the exact registered command",
    }
