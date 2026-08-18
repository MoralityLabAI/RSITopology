"""Deterministic prompt and activation-capture contracts for Godel Globes v0.1.

The scientific analyzer consumes only sealed prompt metadata and chunked NPZ
activation arrays.  Model loading is intentionally kept in a thin script so
the geometry can be replayed without PyTorch, Transformers, a GPU, or model
weights.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


PROTOCOL_ID = "godel_globes_falsification_v0_1"
PROMPT_SCHEMA = "godel_globes_prompt_manifest_v0_1"
CAPTURE_SCHEMA = "godel_globes_capture_index_v0_1"
FAMILIES = (
    "affine_recurrence",
    "symbol_transport",
    "grid_rotation",
    "graph_reachability",
)
HALVES = ("construction", "geometry_validation")


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_once_or_equal(path: str | Path, data: bytes) -> None:
    target = Path(path)
    if target.exists():
        if target.read_bytes() != data:
            raise FileExistsError(f"write-once artifact differs: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def load_protocol(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if value.get("protocol_id") != PROTOCOL_ID:
        raise ValueError(f"expected protocol_id {PROTOCOL_ID}")
    if value.get("new_invariant_levels") is not False:
        raise ValueError("Godel protocol must not introduce an invariant level")
    return value


def _package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def runtime_environment() -> dict[str, Any]:
    """Return stable capture-environment fields, excluding utilization."""

    gpu_static: list[str] = []
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
        gpu_static = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    except (FileNotFoundError, subprocess.SubprocessError):
        gpu_static = []
    return {
        "python_version": sys.version,
        "python_executable": str(Path(sys.executable).resolve()),
        "platform": platform.platform(),
        "packages": {
            name: _package_version(name)
            for name in ("numpy", "scipy", "scikit-learn", "torch", "transformers")
        },
        "gpu_static": gpu_static,
    }


def _rng(seed: int, *coordinates: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([seed, *coordinates]))


def _affine_prompt(rng: np.random.Generator, subcondition: int) -> tuple[str, str, dict]:
    coefficients = (
        (2, 1), (2, -1), (-2, 1), (-2, -1), (3, 0),
        (1, 2), (1, -2), (-1, 3), (-1, -3),
    )
    a, b = coefficients[subcondition]
    sequence = [int(rng.integers(-4, 5))]
    for _ in range(3):
        sequence.append(a * sequence[-1] + b)
    answer = a * sequence[-1] + b
    prompt = (
        f"Use the recurrence x_(t+1)={a}*x_t{b:+d}. "
        f"Sequence: {', '.join(map(str, sequence))}. "
        "Return the next integer as ANSWER=<integer>."
    )
    return prompt, str(answer), {"multiplier": a, "offset": b}


def _symbol_permutation(subcondition: int) -> tuple[str, ...]:
    alphabet = "ABCDE"
    candidates: list[tuple[str, ...]] = []
    for reverse in (False, True):
        source = alphabet[::-1] if reverse else alphabet
        for shift in range(5):
            candidates.append(tuple(source[(index + shift) % 5] for index in range(5)))
    return candidates[subcondition]


def _symbol_prompt(rng: np.random.Generator, subcondition: int) -> tuple[str, str, dict]:
    alphabet = "ABCDE"
    permutation = _symbol_permutation(subcondition)
    mapping = dict(zip(alphabet, permutation))
    source = "".join(rng.choice(list(alphabet), size=6).tolist())
    answer = "".join(mapping[value] for value in source)
    rule = ", ".join(f"{left}->{right}" for left, right in mapping.items())
    prompt = (
        f"Apply this symbol transport exactly once: {rule}. Input: {source}. "
        "Return the transported string as ANSWER=<string>."
    )
    return prompt, answer, {"permutation": "".join(permutation)}


def _rotate_grid(rows: Sequence[str], turns: int) -> tuple[str, ...]:
    value = tuple(rows)
    for _ in range(turns % 4):
        value = tuple("".join(row[index] for row in value[::-1]) for index in range(len(value)))
    return value


def _grid_prompt(rng: np.random.Generator, subcondition: int) -> tuple[str, str, dict]:
    size = 3 + subcondition // 3
    turns = 1 + subcondition % 3
    rows = tuple(
        "".join(map(str, rng.integers(0, 2, size=size).tolist()))
        for _ in range(size)
    )
    answer_rows = _rotate_grid(rows, turns)
    degrees = 90 * turns
    prompt = (
        f"The {size}x{size} binary grid is {'/'.join(rows)}. Rotate it {degrees} "
        "degrees clockwise. Return rows separated by '/' as ANSWER=<rows>."
    )
    return prompt, "/".join(answer_rows), {"size": size, "quarter_turns": turns}


def _reachable(edges: Iterable[tuple[str, str]], source: str, target: str) -> bool:
    adjacency: dict[str, set[str]] = {}
    for left, right in edges:
        adjacency.setdefault(left, set()).add(right)
    unseen = [source]
    visited: set[str] = set()
    while unseen:
        node = unseen.pop()
        if node == target:
            return True
        if node in visited:
            continue
        visited.add(node)
        unseen.extend(sorted(adjacency.get(node, ()), reverse=True))
    return False


def _graph_prompt(
    rng: np.random.Generator, subcondition: int, sample_index: int
) -> tuple[str, str, dict]:
    path_length = 1 + subcondition // 3
    distractor_count = 2 * (subcondition % 3)
    nodes = tuple("ABCDEFGHI")
    path_nodes = nodes[: path_length + 1]
    positive = sample_index % 2 == 0
    edges = list(zip(path_nodes[:-1], path_nodes[1:]))
    if not positive:
        edges = edges[:-1]
    unused = list(nodes[path_length + 1 :])
    candidates = [
        (unused[left], unused[right])
        for left in range(len(unused))
        for right in range(left + 1, len(unused))
    ]
    if candidates:
        order = rng.permutation(len(candidates))
        edges.extend(candidates[index] for index in order[:distractor_count])
    source, target = path_nodes[0], path_nodes[-1]
    observed = _reachable(edges, source, target)
    if observed != positive:
        raise AssertionError("graph generator violated its planted reachability")
    rendered = ", ".join(f"{left}->{right}" for left, right in sorted(edges)) or "none"
    prompt = (
        f"Directed edges: {rendered}. Is {target} reachable from {source}? "
        "Return ANSWER=YES or ANSWER=NO."
    )
    return prompt, "YES" if observed else "NO", {
        "path_length": path_length,
        "distractor_count": distractor_count,
        "planted_positive": positive,
    }


def _prompt_for(
    family: str,
    *,
    rng: np.random.Generator,
    subcondition: int,
    sample_index: int,
) -> tuple[str, str, dict]:
    if family == "affine_recurrence":
        return _affine_prompt(rng, subcondition)
    if family == "symbol_transport":
        return _symbol_prompt(rng, subcondition)
    if family == "grid_rotation":
        return _grid_prompt(rng, subcondition)
    if family == "graph_reachability":
        return _graph_prompt(rng, subcondition, sample_index)
    raise ValueError(f"unsupported behavior family: {family}")


def generate_prompt_manifest(
    *,
    protocol_sha256: str,
    seed: int = 2026071601,
    families: Sequence[str] = FAMILIES,
    subconditions_per_family: int = 9,
    context_shards: int = 8,
    prompts_per_half: int = 2,
) -> dict[str, Any]:
    if subconditions_per_family < 2 or subconditions_per_family > 9:
        raise ValueError("subconditions_per_family must lie in [2, 9]")
    if context_shards < 2 or prompts_per_half < 2:
        raise ValueError("at least two shards and two prompts per half are required")
    unknown = sorted(set(families) - set(FAMILIES))
    if unknown:
        raise ValueError(f"unknown behavior families: {unknown}")
    rows: list[dict[str, Any]] = []
    for family_index, family in enumerate(families):
        for subcondition in range(subconditions_per_family):
            for shard in range(context_shards):
                for half_index, half in enumerate(HALVES):
                    for within_half in range(prompts_per_half):
                        sample_index = half_index * prompts_per_half + within_half
                        generator = _rng(
                            seed, family_index, subcondition, shard, sample_index
                        )
                        prompt, answer, parameters = _prompt_for(
                            family,
                            rng=generator,
                            subcondition=subcondition,
                            sample_index=sample_index,
                        )
                        rows.append(
                            {
                                "prompt_id": (
                                    f"gg01-{family_index:02d}-{subcondition:02d}-"
                                    f"{shard:02d}-{half_index}-{within_half}"
                                ),
                                "behavior_family": family,
                                "subcondition_id": f"{family}-condition-{subcondition:02d}",
                                "context_shard": f"shard-{shard:02d}",
                                "half": half,
                                "within_half_index": within_half,
                                "prompt": prompt,
                                "expected_answer": answer,
                                "response_contract": "one line exactly: ANSWER=<value>",
                                "subcondition_parameters": parameters,
                                "geometry_consumes_expected_answer": False,
                            }
                        )
    manifest = {
        "schema_version": PROMPT_SCHEMA,
        "protocol_id": PROTOCOL_ID,
        "protocol_sha256": protocol_sha256,
        "seed": seed,
        "families": list(families),
        "subconditions_per_family": subconditions_per_family,
        "context_shards": context_shards,
        "halves": list(HALVES),
        "prompts_per_subcondition_per_half_per_shard": prompts_per_half,
        "prompt_count": len(rows),
        "outcomes_unread": True,
        "vpd_selector_audit_outer_excluded": True,
        "rows": rows,
    }
    validate_prompt_manifest(manifest)
    return manifest


def validate_prompt_manifest(value: Mapping[str, Any]) -> None:
    if value.get("schema_version") != PROMPT_SCHEMA:
        raise ValueError("invalid prompt manifest schema")
    if value.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("prompt manifest protocol mismatch")
    if value.get("outcomes_unread") is not True:
        raise ValueError("prompt manifest must keep model outcomes unread")
    if value.get("vpd_selector_audit_outer_excluded") is not True:
        raise ValueError("prompt manifest must exclude existing VPD outcome splits")
    rows = value.get("rows")
    if not isinstance(rows, list) or len(rows) != int(value.get("prompt_count", -1)):
        raise ValueError("prompt_count does not match rows")
    ids = [str(row.get("prompt_id", "")) for row in rows]
    if not all(ids) or len(ids) != len(set(ids)):
        raise ValueError("prompt IDs must be nonempty and unique")
    expected = {
        (
            family,
            f"{family}-condition-{condition:02d}",
            f"shard-{shard:02d}",
            half,
        )
        for family in value["families"]
        for condition in range(int(value["subconditions_per_family"]))
        for shard in range(int(value["context_shards"]))
        for half in HALVES
    }
    counts: dict[tuple[str, str, str, str], int] = {}
    for row in rows:
        key = (
            str(row.get("behavior_family")),
            str(row.get("subcondition_id")),
            str(row.get("context_shard")),
            str(row.get("half")),
        )
        counts[key] = counts.get(key, 0) + 1
        if row.get("geometry_consumes_expected_answer") is not False:
            raise ValueError("identity geometry must not consume expected answers")
    if set(counts) != expected:
        raise ValueError("prompt manifest family/subcondition/shard/half universe differs")
    required_count = int(value["prompts_per_subcondition_per_half_per_shard"])
    if any(count != required_count for count in counts.values()):
        raise ValueError("prompt cells are unbalanced")
    failures = audit_prompt_answer_keys(value)
    if failures:
        raise ValueError(f"prompt answer-key audit failed: {failures[:3]}")


def audit_prompt_answer_keys(value: Mapping[str, Any]) -> list[str]:
    """Independently recompute every deterministic expected-answer cell."""

    failures: list[str] = []
    for row in value.get("rows", ()):
        family = str(row.get("behavior_family"))
        prompt = str(row.get("prompt", ""))
        expected = str(row.get("expected_answer", ""))
        parameters = row.get("subcondition_parameters", {})
        try:
            if family == "affine_recurrence":
                match = re.search(r"Sequence: ([^.]*)\.", prompt)
                if match is None:
                    raise ValueError("sequence missing")
                sequence = [int(item.strip()) for item in match.group(1).split(",")]
                answer = int(parameters["multiplier"]) * sequence[-1] + int(parameters["offset"])
                actual = str(answer)
            elif family == "symbol_transport":
                match = re.search(r"Input: ([A-E]+)\.", prompt)
                if match is None:
                    raise ValueError("symbol input missing")
                mapping = dict(zip("ABCDE", str(parameters["permutation"])))
                actual = "".join(mapping[item] for item in match.group(1))
            elif family == "grid_rotation":
                match = re.search(r"grid is ([01/]+)\.", prompt)
                if match is None:
                    raise ValueError("grid missing")
                rows = tuple(match.group(1).split("/"))
                actual = "/".join(_rotate_grid(rows, int(parameters["quarter_turns"])))
            elif family == "graph_reachability":
                edges_match = re.search(r"Directed edges: (.*?)\. Is", prompt)
                query_match = re.search(r"Is ([A-Z]) reachable from ([A-Z])\?", prompt)
                if edges_match is None or query_match is None:
                    raise ValueError("graph or query missing")
                rendered = edges_match.group(1)
                edges = [] if rendered == "none" else [
                    tuple(item.strip().split("->")) for item in rendered.split(",")
                ]
                target, source = query_match.groups()
                actual = "YES" if _reachable(edges, source, target) else "NO"
            else:
                raise ValueError("unknown family")
        except (KeyError, TypeError, ValueError) as error:
            failures.append(f"{row.get('prompt_id')}:unparseable:{error}")
            continue
        if actual != expected:
            failures.append(
                f"{row.get('prompt_id')}:expected={expected}:recomputed={actual}"
            )
    return failures


def prompt_rows_for_chunk(
    manifest: Mapping[str, Any], *, context_shard: str, half: str
) -> list[Mapping[str, Any]]:
    rows = [
        row
        for row in manifest["rows"]
        if row["context_shard"] == context_shard and row["half"] == half
    ]
    return sorted(
        rows,
        key=lambda row: (
            manifest["families"].index(row["behavior_family"]),
            row["subcondition_id"],
            row["within_half_index"],
        ),
    )


def expected_capture_keys(
    manifest: Mapping[str, Any], *, runtimes: Sequence[str], sites: Sequence[str]
) -> tuple[tuple[str, str, str, str], ...]:
    shards = [f"shard-{value:02d}" for value in range(int(manifest["context_shards"]))]
    return tuple(
        (runtime, site, shard, half)
        for runtime in runtimes
        for site in sites
        for shard in shards
        for half in HALVES
    )


def capture_chunk_id(runtime: str, site: str, shard: str, half: str) -> str:
    safe_site = site.replace(".", "__")
    return f"{runtime}--{safe_site}--{shard}--{half}"


@dataclass(frozen=True)
class CaptureChunk:
    chunk_id: str
    runtime_precision: str
    site_id: str
    context_shard: str
    half: str
    path: Path
    sha256: str
    prompt_ids: tuple[str, ...]
    row_count: int
    ambient_dimension: int
    dtype: str


class CaptureStore:
    """Validated, lazy reader for a complete activation-chunk universe."""

    def __init__(
        self,
        *,
        index_path: Path,
        index: Mapping[str, Any],
        chunks: Mapping[tuple[str, str, str, str], CaptureChunk],
    ) -> None:
        self.index_path = index_path
        self.index = dict(index)
        self.chunks = dict(chunks)

    def load(self, runtime: str, site: str, shard: str, half: str) -> np.ndarray:
        chunk = self.chunks[(runtime, site, shard, half)]
        with np.load(chunk.path, allow_pickle=False) as archive:
            if set(archive.files) != {"activations"}:
                raise ValueError(f"chunk {chunk.chunk_id} must contain only activations")
            values = np.asarray(archive["activations"])
        if values.shape != (chunk.row_count, chunk.ambient_dimension):
            raise ValueError(f"chunk {chunk.chunk_id} changed shape after validation")
        if str(values.dtype) != chunk.dtype or not np.all(np.isfinite(values)):
            raise ValueError(f"chunk {chunk.chunk_id} changed dtype or finiteness")
        return values.astype(np.float64, copy=False)


def validate_capture_index(
    *,
    index_path: str | Path,
    manifest: Mapping[str, Any],
    protocol: Mapping[str, Any],
) -> CaptureStore:
    validate_prompt_manifest(manifest)
    path = Path(index_path).resolve()
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema_version") != CAPTURE_SCHEMA:
        raise ValueError("invalid capture index schema")
    if value.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("capture index protocol mismatch")
    if value.get("protocol_sha256") != canonical_json_sha256(protocol):
        raise ValueError("capture index does not bind the canonical protocol")
    if value.get("prompt_manifest_sha256") != canonical_json_sha256(manifest):
        raise ValueError("capture index does not bind the prompt manifest")
    if value.get("outcomes_read") is not False or value.get("weight_mutation") is not False:
        raise ValueError("capture must be target-blind and mutation-free")
    runtimes = tuple(protocol["runtime_precisions"])
    sites = tuple(protocol["candidate_sites"])
    if tuple(value.get("runtime_precisions", ())) != runtimes:
        raise ValueError("capture index runtime universe differs from protocol")
    if tuple(value.get("candidate_sites", ())) != sites:
        raise ValueError("capture index site universe differs from protocol")
    expected = set(expected_capture_keys(manifest, runtimes=runtimes, sites=sites))
    entries = value.get("chunks")
    if not isinstance(entries, list):
        raise ValueError("capture index chunks must be a list")
    chunks: dict[tuple[str, str, str, str], CaptureChunk] = {}
    ids: set[str] = set()
    dimensions_by_site: dict[str, int] = {}
    for entry in entries:
        key = (
            str(entry.get("runtime_precision")),
            str(entry.get("site_id")),
            str(entry.get("context_shard")),
            str(entry.get("half")),
        )
        chunk_id = str(entry.get("chunk_id", ""))
        if key in chunks or chunk_id in ids:
            raise ValueError("capture index has duplicate chunk key or ID")
        if key not in expected:
            raise ValueError(f"capture index contains unregistered chunk: {key}")
        ids.add(chunk_id)
        chunk_path = (path.parent / str(entry.get("path", ""))).resolve()
        if not chunk_path.is_file():
            raise FileNotFoundError(chunk_path)
        actual_hash = sha256_file(chunk_path)
        if actual_hash != str(entry.get("sha256", "")).lower():
            raise ValueError(f"chunk hash mismatch: {chunk_id}")
        prompt_rows = prompt_rows_for_chunk(
            manifest, context_shard=key[2], half=key[3]
        )
        expected_prompt_ids = tuple(str(row["prompt_id"]) for row in prompt_rows)
        supplied_prompt_ids = tuple(map(str, entry.get("prompt_ids", ())))
        if supplied_prompt_ids != expected_prompt_ids:
            raise ValueError(f"chunk prompt order mismatch: {chunk_id}")
        with np.load(chunk_path, allow_pickle=False) as archive:
            if set(archive.files) != {"activations"}:
                raise ValueError(f"chunk {chunk_id} must contain exactly activations")
            activations = np.asarray(archive["activations"])
        if activations.ndim != 2 or activations.shape[0] != len(expected_prompt_ids):
            raise ValueError(f"chunk {chunk_id} has invalid activation shape")
        if not np.issubdtype(activations.dtype, np.floating) or not np.all(np.isfinite(activations)):
            raise ValueError(f"chunk {chunk_id} activations must be finite floating values")
        dimension = int(activations.shape[1])
        if key[1] in dimensions_by_site and dimensions_by_site[key[1]] != dimension:
            raise ValueError(f"ambient dimension changed for site {key[1]}")
        dimensions_by_site[key[1]] = dimension
        chunk = CaptureChunk(
            chunk_id=chunk_id,
            runtime_precision=key[0],
            site_id=key[1],
            context_shard=key[2],
            half=key[3],
            path=chunk_path,
            sha256=actual_hash,
            prompt_ids=supplied_prompt_ids,
            row_count=int(activations.shape[0]),
            ambient_dimension=dimension,
            dtype=str(activations.dtype),
        )
        chunks[key] = chunk
    if set(chunks) != expected:
        missing = sorted(expected - set(chunks))
        raise ValueError(f"capture index is incomplete; missing {len(missing)} chunks")
    return CaptureStore(index_path=path, index=value, chunks=chunks)


def build_synthetic_capture(
    *,
    output_dir: str | Path,
    manifest: Mapping[str, Any],
    protocol: Mapping[str, Any],
    ambient_dimension: int = 24,
    planted_rank: int | None = None,
    seed: int = 2026071602,
    bfloat16_failure: bool = False,
) -> Path:
    """Create a small target-blind activation fixture through the live contract."""

    validate_prompt_manifest(manifest)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    runtimes = tuple(protocol["runtime_precisions"])
    sites = tuple(protocol["candidate_sites"])
    family_names = tuple(manifest["families"])
    subconditions = int(manifest["subconditions_per_family"])
    shards = int(manifest["context_shards"])
    maximum_rank = min(subconditions - 1, ambient_dimension)
    rank = planted_rank or maximum_rank
    if rank < 1 or rank > maximum_rank:
        raise ValueError("planted rank is incompatible with the prompt fixture")
    codes_by_family: dict[str, np.ndarray] = {}
    bases: dict[tuple[str, str, str, str], np.ndarray] = {}
    for family_index, family in enumerate(family_names):
        code_rng = _rng(seed, 10, family_index)
        codes = code_rng.normal(size=(subconditions, rank))
        codes -= np.mean(codes, axis=0, keepdims=True)
        codes_by_family[family] = codes
        for site_index, site in enumerate(sites):
            base_rng = _rng(seed, 11, family_index, site_index)
            base = np.linalg.qr(base_rng.normal(size=(ambient_dimension, rank)), mode="reduced")[0]
            direction_a = base_rng.normal(size=(ambient_dimension, rank))
            direction_b = base_rng.normal(size=(ambient_dimension, rank))
            for runtime_index, runtime in enumerate(runtimes):
                for shard in range(shards):
                    if bfloat16_failure and runtime == "full_bfloat16":
                        node_rng = _rng(seed, 12, family_index, site_index, runtime_index, shard)
                        frame = np.linalg.qr(
                            node_rng.normal(size=(ambient_dimension, rank)), mode="reduced"
                        )[0]
                    else:
                        context = shard / max(shards - 1, 1)
                        raw = (
                            base
                            + 0.025 * context * direction_a
                            + 0.018 * runtime_index * direction_b
                            + 0.010 * runtime_index * context * (direction_a - direction_b)
                        )
                        frame = np.linalg.qr(raw, mode="reduced")[0]
                    bases[(runtime, site, family, f"shard-{shard:02d}")] = frame

    chunks: list[dict[str, Any]] = []
    for runtime, site, shard, half in expected_capture_keys(
        manifest, runtimes=runtimes, sites=sites
    ):
        rows = prompt_rows_for_chunk(manifest, context_shard=shard, half=half)
        values = np.empty((len(rows), ambient_dimension), dtype=np.float32)
        for row_index, row in enumerate(rows):
            family = str(row["behavior_family"])
            condition = int(str(row["subcondition_id"]).rsplit("-", 1)[1])
            frame = bases[(runtime, site, family, shard)]
            identity = hashlib.sha256(
                f"{runtime}\0{site}\0{shard}\0{half}\0{row['prompt_id']}".encode("utf-8")
            ).digest()
            row_rng = _rng(seed, 20, int.from_bytes(identity[:4], "big"), row_index)
            signal = 5.0 * (frame @ codes_by_family[family][condition])
            noise_scale = 0.20
            if bfloat16_failure and runtime == "full_bfloat16":
                noise_scale = 1.0
            values[row_index] = signal + row_rng.normal(
                scale=noise_scale, size=ambient_dimension
            )
        chunk_id = capture_chunk_id(runtime, site, shard, half)
        relative = Path("chunks") / runtime / site.replace(".", "__") / f"{shard}--{half}.npz"
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        np.savez(target, activations=values)
        chunks.append(
            {
                "chunk_id": chunk_id,
                "runtime_precision": runtime,
                "site_id": site,
                "context_shard": shard,
                "half": half,
                "path": relative.as_posix(),
                "sha256": sha256_file(target),
                "prompt_ids": [row["prompt_id"] for row in rows],
                "row_count": len(rows),
                "ambient_dimension": ambient_dimension,
                "dtype": str(values.dtype),
            }
        )
    index = {
        "schema_version": CAPTURE_SCHEMA,
        "protocol_id": PROTOCOL_ID,
        "protocol_sha256": canonical_json_sha256(protocol),
        "prompt_manifest_sha256": canonical_json_sha256(manifest),
        "capture_kind": "synthetic_contract_fixture",
        "outcomes_read": False,
        "weight_mutation": False,
        "final_nonpadding_prompt_token": True,
        "attention_masked_padding": True,
        "runtime_precisions": list(runtimes),
        "candidate_sites": list(sites),
        "chunks": chunks,
    }
    index_path = output / "capture_index.json"
    write_once_or_equal(index_path, canonical_json_bytes(index))
    return index_path
