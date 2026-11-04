"""Register and run the outcome-free Möbius synergy identity experiment."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from mobius import evaluate_grid  # noqa: E402

PROTOCOL_PATH = HERE / "protocol_v0_1.json"
SOURCE_PATHS = (HERE / "mobius.py", HERE / "run.py")


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_once_or_equal(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"write-once artifact differs: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value) + b"\n")
    temporary.replace(path)


def validate_input_contract(
    capture_index: Mapping[str, Any],
    prompt_manifest: Mapping[str, Any],
    protocol: Mapping[str, Any],
) -> None:
    contract = protocol["first_input_contract"]
    if capture_index.get("capture_kind") != contract["capture_kind"]:
        raise ValueError("capture kind differs from the frozen contract")
    chunks = capture_index.get("chunks")
    if not isinstance(chunks, list) or len(chunks) != int(
        contract["expected_capture_chunks"]
    ):
        raise ValueError("capture chunk universe is incomplete")
    if int(prompt_manifest.get("prompt_count", -1)) != int(contract["prompt_count"]):
        raise ValueError("prompt count differs from the frozen contract")
    if int(prompt_manifest.get("context_shards", -1)) != int(
        contract["expected_context_shards"]
    ):
        raise ValueError("context-shard count differs from the frozen contract")
    if list(prompt_manifest.get("halves", [])) != list(contract["expected_halves"]):
        raise ValueError("split-half universe differs from the frozen contract")
    runtimes = sorted({str(item.get("runtime_precision")) for item in chunks})
    if runtimes != sorted(contract["expected_runtimes"]):
        raise ValueError("runtime universe differs from the frozen contract")
    sites = {str(item.get("site_id")) for item in chunks}
    if len(sites) != int(contract["expected_sites"]):
        raise ValueError("site universe differs from the frozen contract")


def register(args: argparse.Namespace) -> None:
    protocol = load_json(PROTOCOL_PATH)
    capture_index = load_json(args.capture_index.resolve())
    prompt_manifest = load_json(args.prompt_manifest.resolve())
    validate_input_contract(capture_index, prompt_manifest, protocol)
    registration = {
        "schema_version": "mobius_synergy_identity_registration_v0_1",
        "status": "registered_before_claim_eligible_analysis",
        "chronology": "retrospective_on_outcome_free_capture_after_disclosed_engineering_smoke_and_before_claim_eligible_analysis",
        "registered_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": {
            "path": str(PROTOCOL_PATH),
            "sha256": sha256_file(PROTOCOL_PATH),
        },
        "capture_index": {
            "path": str(args.capture_index.resolve()),
            "sha256": sha256_file(args.capture_index.resolve()),
        },
        "prompt_manifest": {
            "path": str(args.prompt_manifest.resolve()),
            "sha256": sha256_file(args.prompt_manifest.resolve()),
        },
        "source_sha256": {
            path.name: sha256_file(path) for path in SOURCE_PATHS
        },
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
    }
    write_once_or_equal(
        args.output.resolve(), canonical_json_bytes(registration) + b"\n"
    )
    print(json.dumps(registration, indent=2, sort_keys=True))


def validate_registration(path: Path) -> tuple[dict[str, Any], Path, Path]:
    value = load_json(path.resolve())
    if value.get("status") != "registered_before_claim_eligible_analysis":
        raise ValueError("registration status is not admissible")
    protocol_artifact = value.get("protocol", {})
    if (
        Path(str(protocol_artifact.get("path"))).resolve() != PROTOCOL_PATH
        or protocol_artifact.get("sha256") != sha256_file(PROTOCOL_PATH)
    ):
        raise ValueError("registered protocol path or hash mismatch")
    for source in SOURCE_PATHS:
        if value.get("source_sha256", {}).get(source.name) != sha256_file(source):
            raise ValueError(f"registered source hash mismatch: {source.name}")
    capture = Path(str(value["capture_index"]["path"])).resolve()
    prompts = Path(str(value["prompt_manifest"]["path"])).resolve()
    if value["capture_index"]["sha256"] != sha256_file(capture):
        raise ValueError("registered capture-index hash mismatch")
    if value["prompt_manifest"]["sha256"] != sha256_file(prompts):
        raise ValueError("registered prompt-manifest hash mismatch")
    return value, capture, prompts


def _condition_index(
    row: Mapping[str, Any], layout: Mapping[str, Any]
) -> tuple[int, int] | None:
    parameters = row.get("subcondition_parameters")
    if not isinstance(parameters, Mapping):
        raise ValueError("prompt row lacks subcondition_parameters")
    for name, expected in layout.get("fixed_parameters", {}).items():
        if parameters.get(name) != expected:
            return None
    axis_a = layout["axis_a_levels"]
    axis_b = layout["axis_b_levels"]
    try:
        return (
            list(axis_a).index(parameters.get(layout["axis_a"])),
            list(axis_b).index(parameters.get(layout["axis_b"])),
        )
    except ValueError:
        return None


def build_cell_tensors(
    *,
    capture_index_path: Path,
    prompt_manifest_path: Path,
    protocol: Mapping[str, Any],
    targets: set[tuple[str, str, str]] | None = None,
) -> dict[tuple[str, str, str, str], np.ndarray]:
    """Join activations to factor cells without reading expected answers."""

    capture_index = load_json(capture_index_path)
    prompt_manifest = load_json(prompt_manifest_path)
    validate_input_contract(capture_index, prompt_manifest, protocol)
    rows = prompt_manifest.get("rows")
    if not isinstance(rows, list):
        raise ValueError("prompt manifest lacks rows")
    prompt_rows: dict[str, dict[str, Any]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("prompt row is not an object")
        prompt_id = str(raw["prompt_id"])
        if prompt_id in prompt_rows:
            raise ValueError(f"duplicate prompt id: {prompt_id}")
        # Deliberately copy only target-blind metadata. expected_answer is ignored.
        prompt_rows[prompt_id] = {
            "behavior_family": raw["behavior_family"],
            "context_shard": raw["context_shard"],
            "half": raw["half"],
            "subcondition_parameters": raw["subcondition_parameters"],
        }

    layouts = protocol["factor_grids"]
    shards = [f"shard-{index:02d}" for index in range(prompt_manifest["context_shards"])]
    shard_index = {name: index for index, name in enumerate(shards)}
    sums: dict[tuple[str, str, str, str, str, int, int], np.ndarray] = {}
    counts: defaultdict[tuple[str, str, str, str, str, int, int], int] = defaultdict(int)
    ambient_by_site: dict[str, int] = {}

    chunks = capture_index["chunks"]
    for chunk in chunks:
        runtime = str(chunk["runtime_precision"])
        site = str(chunk["site_id"])
        half = str(chunk["half"])
        shard = str(chunk["context_shard"])
        if targets is not None and not any(
            candidate_runtime == runtime and candidate_site == site
            for candidate_runtime, candidate_site, _ in targets
        ):
            continue
        if shard not in shard_index:
            raise ValueError(f"unknown context shard: {shard}")
        chunk_prompt_ids = [str(value) for value in chunk["prompt_ids"]]
        path = capture_index_path.parent / str(chunk["path"])
        with np.load(path, allow_pickle=False) as archive:
            activations = np.asarray(archive["activations"], dtype=np.float64)
        if len(activations) != len(chunk_prompt_ids) or activations.ndim != 2:
            raise ValueError(f"activation row mismatch: {path}")
        ambient_by_site.setdefault(site, activations.shape[1])
        if ambient_by_site[site] != activations.shape[1]:
            raise ValueError(f"ambient dimension changed at {site}")
        for prompt_id, vector in zip(chunk_prompt_ids, activations, strict=True):
            metadata = prompt_rows[prompt_id]
            family = str(metadata["behavior_family"])
            if family not in layouts:
                continue
            target = (runtime, site, family)
            if targets is not None and target not in targets:
                continue
            if metadata["half"] != half or metadata["context_shard"] != shard:
                raise ValueError("capture/manifest split identity mismatch")
            indices = _condition_index(metadata, layouts[family])
            if indices is None:
                continue
            axis_a, axis_b = indices
            key = (runtime, site, family, half, shard, axis_a, axis_b)
            if key not in sums:
                sums[key] = np.zeros(activations.shape[1], dtype=np.float64)
            sums[key] += vector
            counts[key] += 1

    result: dict[tuple[str, str, str, str], np.ndarray] = {}
    target_universe = targets
    if target_universe is None:
        runtimes = sorted({str(item["runtime_precision"]) for item in chunks})
        sites = sorted({str(item["site_id"]) for item in chunks})
        target_universe = {
            (runtime, site, family)
            for runtime in runtimes
            for site in sites
            for family in layouts
        }
    for runtime, site, family in sorted(target_universe):
        layout = layouts[family]
        shape = (
            len(shards),
            len(layout["axis_a_levels"]),
            len(layout["axis_b_levels"]),
            ambient_by_site[site],
        )
        for half in prompt_manifest["halves"]:
            tensor = np.empty(shape, dtype=np.float64)
            for shard in shards:
                for axis_a in range(shape[1]):
                    for axis_b in range(shape[2]):
                        key = (
                            runtime,
                            site,
                            family,
                            half,
                            shard,
                            axis_a,
                            axis_b,
                        )
                        if counts[key] < 1:
                            raise ValueError(f"missing registered factor cell: {key}")
                        tensor[shard_index[shard], axis_a, axis_b] = (
                            sums[key] / counts[key]
                        )
            result[(runtime, site, family, half)] = tensor
    return result


def stable_grid_seed(base_seed: int, identity: tuple[str, str, str]) -> int:
    digest = hashlib.sha256("|".join(identity).encode("utf-8")).digest()
    return (base_seed + int.from_bytes(digest[:4], "little")) % (2**32)


def run_analysis(
    *,
    capture_index_path: Path,
    prompt_manifest_path: Path,
    output_dir: Path,
    protocol: Mapping[str, Any],
    claim_level: str,
    smoke: bool,
) -> dict[str, Any]:
    confirmatory = protocol["confirmatory_target"]
    primary_identity = (
        str(confirmatory["runtime_precision"]),
        str(confirmatory["site_id"]),
        str(confirmatory["behavior_family"]),
    )
    targets = {primary_identity} if smoke else None
    cells = build_cell_tensors(
        capture_index_path=capture_index_path,
        prompt_manifest_path=prompt_manifest_path,
        protocol=protocol,
        targets=targets,
    )
    grid_identities = sorted({key[:3] for key in cells})
    ranks = [1, 2] if smoke else list(protocol["ranks"])
    bootstrap_replicates = 8 if smoke else int(protocol["bootstrap"]["replicates"])
    permutation_replicates = 8 if smoke else int(
        protocol["permutation_null"]["replicates"]
    )
    receipts: list[dict[str, Any]] = []
    grid_summaries: list[dict[str, Any]] = []
    basis_dir = output_dir / "supported_bases"
    output_dir.mkdir(parents=True, exist_ok=True)

    for runtime, site, family in grid_identities:
        identity = (runtime, site, family)
        evaluation = evaluate_grid(
            cells[(*identity, "construction")],
            cells[(*identity, "geometry_validation")],
            ranks=ranks,
            bootstrap_replicates=bootstrap_replicates,
            permutation_replicates=permutation_replicates,
            lower_quantile=float(protocol["bootstrap"]["lower_quantile"]),
            upper_quantile=float(protocol["permutation_null"]["upper_quantile"]),
            minimum_strict_margin=float(protocol["gate"]["minimum_strict_margin"]),
            seed=stable_grid_seed(int(protocol["seed"]), identity),
        )
        passing_ranks: list[int] = []
        for raw in evaluation.receipts:
            receipt = {
                "runtime_precision": runtime,
                "site_id": site,
                "behavior_family": family,
                "claim_role": (
                    "confirmatory" if identity == primary_identity else "exploratory"
                ),
                "unit_count": evaluation.unit_count,
                "plaquettes_per_shard": evaluation.plaquettes_per_shard,
                **raw,
            }
            if receipt["passed"]:
                passing_ranks.append(int(receipt["rank"]))
                left, right = evaluation.observed_bases[int(receipt["rank"])]
                name = hashlib.sha256(
                    f"{runtime}|{site}|{family}|{receipt['rank']}".encode("utf-8")
                ).hexdigest()[:16]
                path = basis_dir / f"basis-{name}.npz"
                basis_dir.mkdir(parents=True, exist_ok=True)
                np.savez(
                    path,
                    construction_basis=left,
                    geometry_validation_basis=right,
                )
                receipt["basis_path"] = path.relative_to(output_dir).as_posix()
                receipt["basis_sha256"] = sha256_file(path)
            receipts.append(receipt)
        grid_summaries.append(
            {
                "runtime_precision": runtime,
                "site_id": site,
                "behavior_family": family,
                "claim_role": (
                    "confirmatory" if identity == primary_identity else "exploratory"
                ),
                "status": "supported" if passing_ranks else "no_supported_rank",
                "passing_ranks": passing_ranks,
            }
        )

    primary_summary = next(
        item
        for item in grid_summaries
        if (
            item["runtime_precision"],
            item["site_id"],
            item["behavior_family"],
        )
        == primary_identity
    )
    if smoke:
        decision = "not_evaluated_engineering_smoke"
    else:
        decision = "pass" if primary_summary["passing_ranks"] else "fail"
    summary = {
        "schema_version": "mobius_synergy_identity_result_v0_1",
        "protocol_id": protocol["protocol_id"],
        "claim_level": claim_level,
        "confirmatory_decision": decision,
        "confirmatory_target": primary_summary,
        "grid_count": len(grid_summaries),
        "supported_grid_count": sum(
            item["status"] == "supported" for item in grid_summaries
        ),
        "rank_receipt_count": len(receipts),
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
        "claim_boundary": protocol["claim_boundary"],
        "capture_index_sha256": sha256_file(capture_index_path),
        "prompt_manifest_sha256": sha256_file(prompt_manifest_path),
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "grid_summaries": grid_summaries,
    }
    receipts_path = output_dir / "rank_receipts.jsonl"
    receipts_path.write_bytes(
        b"".join(canonical_json_bytes(item) + b"\n" for item in receipts)
    )
    write_json(output_dir / "summary.json", summary)
    manifest = {
        "schema_version": "mobius_synergy_identity_release_v0_1",
        "summary_sha256": sha256_file(output_dir / "summary.json"),
        "rank_receipts_sha256": sha256_file(receipts_path),
        "basis_files": {
            path.relative_to(output_dir).as_posix(): sha256_file(path)
            for path in sorted(basis_dir.glob("*.npz"))
        }
        if basis_dir.exists()
        else {},
    }
    write_json(output_dir / "release_manifest.json", manifest)
    return summary


def analyze(args: argparse.Namespace) -> None:
    _, capture, prompts = validate_registration(args.registration)
    protocol = load_json(PROTOCOL_PATH)
    capture_index = load_json(capture)
    prompt_manifest = load_json(prompts)
    validate_input_contract(capture_index, prompt_manifest, protocol)
    summary = run_analysis(
        capture_index_path=capture,
        prompt_manifest_path=prompts,
        output_dir=args.output_dir.resolve(),
        protocol=protocol,
        claim_level="registered_real_model_analysis",
        smoke=False,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


def smoke(args: argparse.Namespace) -> None:
    protocol = load_json(PROTOCOL_PATH)
    capture = args.capture_index.resolve()
    prompts = args.prompt_manifest.resolve()
    validate_input_contract(load_json(capture), load_json(prompts), protocol)
    summary = run_analysis(
        capture_index_path=capture,
        prompt_manifest_path=prompts,
        output_dir=args.output_dir.resolve(),
        protocol=protocol,
        claim_level="engineering_smoke_only",
        smoke=True,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    subparsers = value.add_subparsers(dest="command", required=True)
    register_parser = subparsers.add_parser("register")
    register_parser.add_argument("--capture-index", type=Path, required=True)
    register_parser.add_argument("--prompt-manifest", type=Path, required=True)
    register_parser.add_argument("--output", type=Path, required=True)
    register_parser.set_defaults(function=register)
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("--registration", type=Path, required=True)
    analyze_parser.add_argument("--output-dir", type=Path, required=True)
    analyze_parser.set_defaults(function=analyze)
    smoke_parser = subparsers.add_parser("smoke")
    smoke_parser.add_argument("--capture-index", type=Path, required=True)
    smoke_parser.add_argument("--prompt-manifest", type=Path, required=True)
    smoke_parser.add_argument("--output-dir", type=Path, required=True)
    smoke_parser.set_defaults(function=smoke)
    return value


def main() -> None:
    args = parser().parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
