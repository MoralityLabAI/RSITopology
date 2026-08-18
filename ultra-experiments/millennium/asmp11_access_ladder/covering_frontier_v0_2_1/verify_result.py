#!/usr/bin/env python3
"""Independent artifact verifier for ASMP-11 v0.2.1.

This file deliberately does not import ``crossover_frontier`` or ``run``.  It
reimplements cover replay, lower bounds, exact binomial calibration,
classification, brackets, one identity diagnostic, and four robustness probes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from collections import Counter
from datetime import datetime, timedelta
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb, isfinite
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parent
CERTIFIED = "crossover_certified"
IMPOSSIBLE = "crossover_impossible_under_bounds"
UNRESOLVED = "unresolved_covering_gap"
RELEASE_ID = "asmp11.intermediate_width_crossover.v0.2.1.2"
MATHEMATICAL_PROTOCOL_ID = "asmp11.intermediate_width_crossover.v0.2.1"
REGISTRATION_SCHEMA = "asmp11_intermediate_crossover_registration_v0_2_1_2"
RESULT_SCHEMA = "asmp11_intermediate_crossover_result_layer_v0_2_1_2"
RELIABILITY_SCHEMA = "asmp11_intermediate_crossover_reliability_layer_v0_2_1_2"
CLAIM_SCHEMA = "asmp11_intermediate_crossover_claim_layer_v0_2_1_2"
OPERATION_SCHEMA = "asmp11_intermediate_crossover_operation_layer_v0_2_1_2"
RECEIPT_SCHEMA = "asmp11_intermediate_crossover_receipt_v0_2_1_2"
VERIFICATION_SCHEMA = "asmp11_intermediate_crossover_independent_verification_v0_2_1_2"
CLAIM_BOUNDARY = (
    "Finite bounds-aware crossover surface for the transparent parity oracle only."
)
FROZEN_CLAIM_GRID = {
    "protocol_id": MATHEMATICAL_PROTOCOL_ID,
    "release_id": RELEASE_ID,
    "status": "registration_required_before_execution",
    "dimensions": [13, 15, 17],
    "degrees": [3, 4],
    "width_rule": {
        "3": "every integer s with 3 < s < n-3",
        "4": "every integer s with 4 < s < n-2",
    },
    "flip_rates": ["1/20", "3/20", "1/4"],
    "alpha": "1/20",
    "target_power": "9/10",
    "sample_cap": 4096,
    "resource_policy": {
        "max_greedy_rounds_per_cell": 4096,
        "max_candidate_blocks_per_cell": 30000,
        "hard_wall_seconds_per_cell": 15,
        "max_total_wall_seconds": 900,
        "max_ram_bytes": 4294967296,
        "execution": "sequential_cpu_only",
    },
    "expected_counts": {
        "covering_cells": 48,
        "cost_cells": 144,
        "brackets": 18,
        "metric_records_per_cost_cell": 5,
        "robustness_probes_per_cost_cell": 4,
    },
}
REGISTRATION_FILENAME = "registration_v0_2_1_2.json"
ARTIFACT_DIRECTORY = "artifacts_v0_2_1_2"
VERIFICATION_FILENAME = "independent_verification_v0_2_1_2.json"
SYNTHESIS_FILENAME = "synthesis_receipt_v0_2_1_2.json"
BOUND_SOURCES = (
    "README.md",
    "PROTOCOL_v0_2_1.md",
    "SERIALIZATION_REPAIR_v0_2_1_1.md",
    "SOURCE_HARDENING_v0_2_1_2.md",
    "experiment_v0_2_1.json",
    "prior_anchor_v0_2.json",
    "release_contract.py",
    "crossover_frontier.py",
    "run.py",
    "build_registration.py",
    "verify_result.py",
    "synthesize_receipt.py",
    "test_crossover_frontier.py",
)
PRIMARY_OUTPUTS = frozenset(
    {
        "covering_cells.jsonl",
        "cost_cells.jsonl",
        "covering_checkpoint.json",
        "cost_checkpoint.json",
        "result_layer.json",
        "reliability_layer.json",
        "claim_layer.json",
        "operation_layer.json",
    }
)
DIAGNOSTIC_PROBE_ID = "D1_primary_bound_interval_replay"
ROBUSTNESS_PROBE_IDS = (
    "P2_query_count_only",
    "P3_stricter_familywise_error",
    "P4_stricter_power",
    "P5_exact_independent_fwer",
)
ALL_PROBE_IDS = (DIAGNOSTIC_PROBE_ID, *ROBUSTNESS_PROBE_IDS)
REGISTRATION_KEYS = {
    "schema_version",
    "release_id",
    "protocol_id",
    "registered_at_utc",
    "status",
    "proposed_asmp_id",
    "source_commit",
    "source_hashes",
    "source_git_blob_oids",
    "manifest_path",
    "manifest_sha256",
    "prior_anchor_path",
    "prior_anchor_sha256",
    "claim_grid",
    "claim_boundary",
    "output_policy",
}
RECEIPT_KEYS = {
    "schema_version",
    "release_id",
    "registration_sha256",
    "manifest_sha256",
    "prior_anchor_sha256",
    "outputs",
    "verdict",
}
VERIFICATION_GATE_IDS = (
    "V0_source_registration_binding",
    "V1_receipt_output_link_closure",
    "V2_cover_witnesses_and_lower_bounds",
    "V3_exact_cost_classification",
    "V4_full_metric_probe_replay",
    "V5_minimum_width_brackets",
    "V6_layer_and_metric_firewall",
    "V7_exact_registered_cartesian_grid",
    "V8_primary_gates_exactly_recomputed",
    "V9_operation_and_resource_consistency",
    "V10_prior_anchor_independent_replay",
    "V11_checkpoint_raw_row_consistency",
    "V12_claim_operation_consistency",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_lf_text(path: Path, payload: str) -> None:
    """Write verification text with stable LF bytes on every host."""

    path.write_text(payload, encoding="utf-8", newline="\n")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite(token: str) -> None:
    raise ValueError(f"non-finite JSON number: {token}")


def strict_json_loads(payload: str) -> Any:
    return json.loads(
        payload,
        object_pairs_hook=_unique_object,
        parse_constant=_reject_nonfinite,
    )


def load_json(path: Path) -> Any:
    return strict_json_loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = strict_json_loads(line)
                if not isinstance(row, dict):
                    raise ValueError("JSONL row must be an object")
                rows.append(row)
    return rows


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def full_commit(reference: str) -> str:
    commit = git("rev-parse", "--verify", f"{reference}^{{commit}}")
    if len(commit) != 40 or any(
        character not in "0123456789abcdef" for character in commit
    ):
        raise ValueError("commit id is not full hexadecimal")
    return commit


def committed_bytes(commit: str, path: Path) -> bytes:
    repo_root = Path(git("rev-parse", "--show-toplevel"))
    relative = path.resolve().relative_to(repo_root).as_posix()
    return subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=ROOT)


def git_blob_oid(commit: str, path: Path) -> str:
    repo_root = Path(git("rev-parse", "--show-toplevel"))
    relative = path.resolve().relative_to(repo_root).as_posix()
    oid = git("rev-parse", f"{commit}:{relative}")
    if (
        len(oid) != 40
        or any(character not in "0123456789abcdef" for character in oid)
        or git("cat-file", "-t", oid) != "blob"
    ):
        raise ValueError("registered source is not a full Git blob")
    return oid


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )


def source_binding_passes(
    registration: dict[str, Any],
    registration_path: Path,
    manifest: dict[str, Any],
    manifest_path: Path,
    anchor_path: Path,
    operation: dict[str, Any],
) -> bool:
    try:
        if (
            registration_path.is_symlink()
            or registration_path.resolve() != (ROOT / REGISTRATION_FILENAME).resolve()
        ):
            return False
        if set(registration) != REGISTRATION_KEYS:
            return False
        if registration["schema_version"] != REGISTRATION_SCHEMA:
            return False
        if registration["release_id"] != RELEASE_ID:
            return False
        if registration["protocol_id"] != MATHEMATICAL_PROTOCOL_ID:
            return False
        if (
            registration["status"]
            != "prospective_registration_before_claim_grid_execution"
        ):
            return False
        if registration["proposed_asmp_id"] != "ASMP-11":
            return False
        if registration["claim_boundary"] != CLAIM_BOUNDARY:
            return False
        if registration["output_policy"] != "write_once_non_aliasing":
            return False
        registered_at = datetime.fromisoformat(str(registration["registered_at_utc"]))
        if registered_at.utcoffset() != timedelta(0):
            return False
        if registration["manifest_path"] != "experiment_v0_2_1.json":
            return False
        if registration["prior_anchor_path"] != "prior_anchor_v0_2.json":
            return False
        if (
            manifest_path.is_symlink()
            or manifest_path.resolve()
            != (ROOT / registration["manifest_path"]).resolve()
        ):
            return False
        if (
            anchor_path.is_symlink()
            or anchor_path.resolve()
            != (ROOT / registration["prior_anchor_path"]).resolve()
        ):
            return False
        if sha256(manifest_path) != registration["manifest_sha256"]:
            return False
        if sha256(anchor_path) != registration["prior_anchor_sha256"]:
            return False
        if registration["claim_grid"] != FROZEN_CLAIM_GRID:
            return False
        if registration["claim_grid"] != manifest["asmp11"]:
            return False
        source_commit = registration["source_commit"]
        if full_commit(source_commit) != source_commit:
            return False
        if set(registration["source_hashes"]) != set(BOUND_SOURCES):
            return False
        if set(registration["source_git_blob_oids"]) != set(BOUND_SOURCES):
            return False
        if (
            registration["manifest_sha256"]
            != registration["source_hashes"]["experiment_v0_2_1.json"]
        ):
            return False
        if (
            registration["prior_anchor_sha256"]
            != registration["source_hashes"]["prior_anchor_v0_2.json"]
        ):
            return False
        for name in BOUND_SOURCES:
            path = ROOT / name
            expected = registration["source_hashes"][name]
            if not path.is_file() or path.is_symlink() or sha256(path) != expected:
                return False
            if (
                hashlib.sha256(committed_bytes(source_commit, path)).hexdigest()
                != expected
            ):
                return False
            if (
                git_blob_oid(source_commit, path)
                != registration["source_git_blob_oids"][name]
            ):
                return False
        registration_record = operation["registration"]
        if set(registration_record) != {
            "path",
            "sha256",
            "source_commit",
            "registration_commit",
        }:
            return False
        if Path(registration_record["path"]).resolve() != registration_path.resolve():
            return False
        registration_commit = registration_record["registration_commit"]
        execution_commit = operation["environment"]["git_head"]
        if full_commit(registration_commit) != registration_commit:
            return False
        if full_commit(execution_commit) != execution_commit:
            return False
        if not is_ancestor(source_commit, registration_commit):
            return False
        if source_commit == registration_commit:
            return False
        if not is_ancestor(registration_commit, execution_commit):
            return False
        if hashlib.sha256(
            committed_bytes(registration_commit, registration_path)
        ).hexdigest() != sha256(registration_path):
            return False
        return True
    except (KeyError, TypeError, ValueError, OSError, subprocess.CalledProcessError):
        return False


def independent_widths(n: int, k: int) -> tuple[int, ...]:
    if k == 3:
        return tuple(range(4, n - 3))
    if k == 4:
        return tuple(range(5, n - 2))
    raise ValueError("registered degree outside {3,4}")


def expected_grid_counters(config: dict[str, Any]) -> dict[str, Counter[Any]]:
    covering = Counter(
        (int(n), int(k), int(block_size))
        for n in config["dimensions"]
        for k in config["degrees"]
        for block_size in independent_widths(int(n), int(k))
    )
    cost = Counter(
        (int(n), int(k), int(block_size), str(Fraction(flip_rate)))
        for n in config["dimensions"]
        for k in config["degrees"]
        for block_size in independent_widths(int(n), int(k))
        for flip_rate in config["flip_rates"]
    )
    bracket = Counter(
        (int(n), int(k), str(Fraction(flip_rate)))
        for n in config["dimensions"]
        for k in config["degrees"]
        for flip_rate in config["flip_rates"]
    )
    return {"covering": covering, "cost": cost, "bracket": bracket}


def grid_axes_are_unique_and_canonical(config: dict[str, Any]) -> bool:
    try:
        dimensions = config["dimensions"]
        degrees = config["degrees"]
        rates = config["flip_rates"]
        counters = expected_grid_counters(config)
        return (
            all(
                isinstance(value, int) and not isinstance(value, bool)
                for value in dimensions
            )
            and all(
                isinstance(value, int) and not isinstance(value, bool)
                for value in degrees
            )
            and len(set(dimensions)) == len(dimensions)
            and len(set(degrees)) == len(degrees)
            and all(
                isinstance(value, str) and value == str(Fraction(value))
                for value in rates
            )
            and len(set(rates)) == len(rates)
            and all(
                count == 1
                for counter in counters.values()
                for count in counter.values()
            )
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def observed_grid_counters(
    covers: Sequence[dict[str, Any]],
    costs: Sequence[dict[str, Any]],
    brackets: Sequence[dict[str, Any]],
) -> dict[str, Counter[Any]]:
    return {
        "covering": Counter(
            (int(row["n"]), int(row["k"]), int(row["block_size"])) for row in covers
        ),
        "cost": Counter(
            (
                int(row["n"]),
                int(row["k"]),
                int(row["block_size"]),
                str(Fraction(row["flip_rate"])),
            )
            for row in costs
        ),
        "bracket": Counter(
            (int(row["n"]), int(row["k"]), str(Fraction(row["flip_rate"])))
            for row in brackets
        ),
    }


def _native_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(float(value))
    )


def _canonical_fraction(value: object) -> bool:
    try:
        return isinstance(value, str) and value == str(Fraction(value))
    except (ValueError, ZeroDivisionError):
        return False


def _design_shape(record: object) -> bool:
    if record is None:
        return True
    if not isinstance(record, dict) or set(record) != {
        "query_count",
        "samples_per_query",
        "total_samples",
        "cutoff",
        "null_tail",
        "familywise_error_upper",
        "signal_power_lower",
        "fwer_mode",
    }:
        return False
    return (
        all(
            _native_int(record[field])
            for field in (
                "query_count",
                "samples_per_query",
                "total_samples",
                "cutoff",
            )
        )
        and all(
            _canonical_fraction(record[field])
            for field in (
                "null_tail",
                "familywise_error_upper",
                "signal_power_lower",
            )
        )
        and isinstance(record["fwer_mode"], str)
    )


def _primary_shape(record: object) -> bool:
    if not isinstance(record, dict) or set(record) != {
        "status",
        "lower_query_bound",
        "upper_query_bound",
        "evaluated_query_counts",
        "baseline",
        "best_certified",
        "optimistic_floor",
    }:
        return False
    return (
        isinstance(record["status"], str)
        and all(
            _native_int(record[field])
            for field in (
                "lower_query_bound",
                "upper_query_bound",
                "evaluated_query_counts",
            )
        )
        and all(
            _design_shape(record[field])
            for field in ("baseline", "best_certified", "optimistic_floor")
        )
    )


def _probe_shapes(records: object) -> bool:
    if not isinstance(records, list):
        return False
    for record in records:
        if not isinstance(record, dict):
            return False
        if not all(
            isinstance(record.get(field), bool)
            for field in (
                "agrees_with_primary",
                "binding",
                "counts_toward_robustness",
            )
        ):
            return False
        if not all(
            isinstance(record.get(field), str)
            for field in ("probe_id", "status", "record_kind")
        ):
            return False
        if "evaluated_query_counts" in record and not _native_int(
            record["evaluated_query_counts"]
        ):
            return False
    return True


def raw_record_shapes_pass(
    covers: Sequence[dict[str, Any]],
    costs: Sequence[dict[str, Any]],
    brackets: Sequence[dict[str, Any]],
) -> bool:
    cover_keys = {
        "n",
        "k",
        "block_size",
        "lower_bound",
        "lower_bound_components",
        "upper_bound",
        "optimum_certified",
        "construction_status",
        "stop_reason",
        "greedy_rounds",
        "gain_evaluations",
        "universe_size",
        "candidate_block_count",
        "elapsed_seconds",
        "selected_blocks",
    }
    cost_keys = {
        "n",
        "k",
        "block_size",
        "flip_rate",
        "primary",
        "metric_robustness_probes",
    }
    bracket_keys = {
        "n",
        "k",
        "flip_rate",
        "anchor_query_count",
        "s_no",
        "s_yes",
        "s_star",
        "unresolved_widths",
        "interval",
        "status_by_width",
    }
    covers_ok = all(
        set(row) == cover_keys
        and all(
            _native_int(row[field])
            for field in (
                "n",
                "k",
                "block_size",
                "lower_bound",
                "upper_bound",
                "greedy_rounds",
                "gain_evaluations",
                "universe_size",
                "candidate_block_count",
            )
        )
        and isinstance(row["optimum_certified"], bool)
        and isinstance(row["construction_status"], str)
        and isinstance(row["stop_reason"], str)
        and _finite_number(row["elapsed_seconds"])
        and isinstance(row["lower_bound_components"], dict)
        and set(row["lower_bound_components"]) == {"counting", "schoenheim"}
        and all(_native_int(value) for value in row["lower_bound_components"].values())
        and isinstance(row["selected_blocks"], list)
        and all(
            isinstance(block, list) and all(_native_int(point) for point in block)
            for block in row["selected_blocks"]
        )
        for row in covers
    )
    costs_ok = all(
        set(row) == cost_keys
        and all(_native_int(row[field]) for field in ("n", "k", "block_size"))
        and _canonical_fraction(row["flip_rate"])
        and _primary_shape(row["primary"])
        and _probe_shapes(row["metric_robustness_probes"])
        for row in costs
    )
    brackets_ok = all(
        set(row) == bracket_keys
        and all(
            _native_int(row[field])
            for field in ("n", "k", "anchor_query_count", "s_no", "s_yes")
        )
        and (row["s_star"] is None or _native_int(row["s_star"]))
        and _canonical_fraction(row["flip_rate"])
        and isinstance(row["unresolved_widths"], list)
        and all(_native_int(value) for value in row["unresolved_widths"])
        and (row["interval"] is None or isinstance(row["interval"], str))
        and isinstance(row["status_by_width"], dict)
        and all(
            isinstance(key, str) and key == str(int(key)) and isinstance(value, str)
            for key, value in row["status_by_width"].items()
        )
        for row in brackets
    )
    return covers_ok and costs_ok and brackets_ok


def ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def independent_schoenheim(n: int, block_size: int, support_size: int) -> int:
    if support_size == 0:
        return 1
    return ceil_div(
        n * independent_schoenheim(n - 1, block_size - 1, support_size - 1),
        block_size,
    )


def independent_lower_bounds(
    n: int, block_size: int, support_size: int
) -> dict[str, int]:
    counting = ceil_div(comb(n, support_size), comb(block_size, support_size))
    schoenheim = independent_schoenheim(n, block_size, support_size)
    return {
        "counting": counting,
        "schoenheim": schoenheim,
        "certified": max(counting, schoenheim),
    }


def independent_verify_cover(
    n: int,
    block_size: int,
    support_size: int,
    selected_blocks: Sequence[Sequence[int]],
) -> bool:
    target = set(combinations(range(n), support_size))
    observed: set[tuple[int, ...]] = set()
    for raw_block in selected_blocks:
        block = tuple(raw_block)
        if len(block) != block_size or tuple(sorted(block)) != block:
            return False
        if len(set(block)) != block_size or any(
            point not in range(n) for point in block
        ):
            return False
        observed.update(combinations(block, support_size))
    return observed == target


@lru_cache(maxsize=None)
def independent_tail(samples: int, cutoff: int, probability: Fraction) -> Fraction:
    if cutoff < 0:
        return Fraction(0)
    if 2 * cutoff >= samples:
        return Fraction(1)
    numerator = probability.numerator
    denominator = probability.denominator
    complement = denominator - numerator
    low = sum(
        comb(samples, count) * numerator**count * complement ** (samples - count)
        for count in range(cutoff + 1)
    )
    high = sum(
        comb(samples, count) * numerator**count * complement ** (samples - count)
        for count in range(samples - cutoff, samples + 1)
    )
    return Fraction(low + high, denominator**samples)


def independent_fwer(tail: Fraction, query_count: int, mode: str) -> Fraction:
    if mode == "bonferroni":
        return min(Fraction(1), query_count * tail)
    if mode == "independent_exact":
        return Fraction(1) - (Fraction(1) - tail) ** query_count
    raise ValueError(mode)


@lru_cache(maxsize=None)
def independent_design(
    query_count: int,
    flip_rate: Fraction,
    alpha: Fraction,
    power: Fraction,
    sample_cap: int,
    mode: str = "bonferroni",
    *,
    serialize_probabilities: bool = True,
) -> dict[str, object] | None:
    for samples in range(1, sample_cap + 1):
        accepted_cutoff = None
        for cutoff in range((samples - 1) // 2 + 1):
            null_tail = independent_tail(samples, cutoff, Fraction(1, 2))
            if independent_fwer(null_tail, query_count, mode) <= alpha:
                accepted_cutoff = cutoff
            else:
                break
        if accepted_cutoff is None:
            continue
        null_tail = independent_tail(samples, accepted_cutoff, Fraction(1, 2))
        signal = independent_tail(samples, accepted_cutoff, Fraction(1) - flip_rate)
        if signal >= power:
            return {
                "query_count": query_count,
                "samples_per_query": samples,
                "total_samples": query_count * samples,
                "cutoff": accepted_cutoff,
                "null_tail": str(null_tail) if serialize_probabilities else null_tail,
                "familywise_error_upper": (
                    str(independent_fwer(null_tail, query_count, mode))
                    if serialize_probabilities
                    else independent_fwer(null_tail, query_count, mode)
                ),
                "signal_power_lower": (
                    str(signal) if serialize_probabilities else signal
                ),
                "fwer_mode": mode,
            }
    return None


def independent_classification(
    lower: int,
    upper: int,
    baseline_q: int,
    flip_rate: Fraction,
    alpha: Fraction,
    power: Fraction,
    sample_cap: int,
    mode: str = "bonferroni",
    *,
    serialize_probabilities: bool = True,
) -> dict[str, object]:
    baseline = independent_design(
        baseline_q,
        flip_rate,
        alpha,
        power,
        sample_cap,
        mode,
        serialize_probabilities=serialize_probabilities,
    )
    if baseline is None:
        raise AssertionError("baseline exceeded cap")
    certified = independent_design(
        upper,
        flip_rate,
        alpha,
        power,
        sample_cap,
        mode,
        serialize_probabilities=serialize_probabilities,
    )
    feasible = [
        design
        for query_count in range(lower, upper + 1)
        if (
            design := independent_design(
                query_count,
                flip_rate,
                alpha,
                power,
                sample_cap,
                mode,
                serialize_probabilities=serialize_probabilities,
            )
        )
        is not None
    ]
    optimistic = min(
        feasible,
        key=lambda row: (int(row["total_samples"]), int(row["query_count"])),
        default=None,
    )
    if certified is not None and int(certified["total_samples"]) < int(
        baseline["total_samples"]
    ):
        status = CERTIFIED
    elif optimistic is None or int(optimistic["total_samples"]) >= int(
        baseline["total_samples"]
    ):
        status = IMPOSSIBLE
    else:
        status = UNRESOLVED
    return {
        "status": status,
        "baseline": baseline,
        "best_certified": certified,
        "optimistic_floor": optimistic,
    }


def independent_query_status(lower: int, upper: int, baseline: int) -> str:
    if upper < baseline:
        return CERTIFIED
    if lower >= baseline:
        return IMPOSSIBLE
    return UNRESOLVED


def independent_probe_statuses(
    lower: int,
    upper: int,
    baseline_q: int,
    flip_rate: Fraction,
    alpha: Fraction,
    power: Fraction,
    sample_cap: int,
) -> dict[str, str]:
    primary = independent_classification(
        lower,
        upper,
        baseline_q,
        flip_rate,
        alpha,
        power,
        sample_cap,
        serialize_probabilities=False,
    )["status"]
    return {
        DIAGNOSTIC_PROBE_ID: str(primary),
        "P2_query_count_only": independent_query_status(lower, upper, baseline_q),
        "P3_stricter_familywise_error": str(
            independent_classification(
                lower,
                upper,
                baseline_q,
                flip_rate,
                alpha / 2,
                power,
                sample_cap,
                serialize_probabilities=False,
            )["status"]
        ),
        "P4_stricter_power": str(
            independent_classification(
                lower,
                upper,
                baseline_q,
                flip_rate,
                alpha,
                Fraction(19, 20),
                sample_cap,
                serialize_probabilities=False,
            )["status"]
        ),
        "P5_exact_independent_fwer": str(
            independent_classification(
                lower,
                upper,
                baseline_q,
                flip_rate,
                alpha,
                power,
                sample_cap,
                "independent_exact",
                serialize_probabilities=False,
            )["status"]
        ),
    }


def independent_probe_records(
    lower: int,
    upper: int,
    baseline_q: int,
    flip_rate: Fraction,
    alpha: Fraction,
    power: Fraction,
    sample_cap: int,
) -> list[dict[str, object]]:
    primary = independent_classification(
        lower, upper, baseline_q, flip_rate, alpha, power, sample_cap
    )
    statuses = independent_probe_statuses(
        lower, upper, baseline_q, flip_rate, alpha, power, sample_cap
    )
    alternatives: tuple[tuple[str, dict[str, object]], ...] = (
        (
            DIAGNOSTIC_PROBE_ID,
            {
                "metric": "exact total samples over every integer q in [L,U]",
                "evaluated_query_counts": upper - lower + 1,
                "record_kind": "identity_diagnostic",
                "counts_toward_robustness": False,
            },
        ),
        (
            "P2_query_count_only",
            {
                "metric": "query count without replicate cost",
                "record_kind": "robustness_probe",
                "probe_family": "query_count_only_alternative",
                "counts_toward_robustness": True,
            },
        ),
        (
            "P3_stricter_familywise_error",
            {
                "alpha": str(alpha / 2),
                "fwer_mode": "bonferroni",
                "record_kind": "robustness_probe",
                "probe_family": "stricter_alpha_alternative",
                "counts_toward_robustness": True,
            },
        ),
        (
            "P4_stricter_power",
            {
                "target_power": "19/20",
                "fwer_mode": "bonferroni",
                "record_kind": "robustness_probe",
                "probe_family": "stricter_power_alternative",
                "counts_toward_robustness": True,
            },
        ),
        (
            "P5_exact_independent_fwer",
            {
                "alpha": str(alpha),
                "fwer_mode": "independent_exact",
                "assumption": "fresh query samples are independent",
                "record_kind": "robustness_probe",
                "probe_family": "independent_fwer_alternative",
                "counts_toward_robustness": True,
            },
        ),
    )
    return [
        {
            "probe_id": probe_id,
            "status": statuses[probe_id],
            "agrees_with_primary": statuses[probe_id] == primary["status"],
            "binding": False,
            **details,
        }
        for probe_id, details in alternatives
    ]


def independent_probe_summary(costs: Sequence[dict[str, Any]]) -> dict[str, Any]:
    records: dict[str, dict[str, Any]] = {}
    for probe_id in ALL_PROBE_IDS:
        observed = [
            probe
            for row in costs
            for probe in row["metric_robustness_probes"]
            if probe["probe_id"] == probe_id
        ]
        records[probe_id] = {
            "cells": len(observed),
            "agrees_with_primary": sum(
                probe["agrees_with_primary"] is True for probe in observed
            ),
            "disagrees_with_primary": sum(
                probe["agrees_with_primary"] is False for probe in observed
            ),
            "binding_false": sum(probe["binding"] is False for probe in observed),
            "counts_toward_robustness": probe_id in ROBUSTNESS_PROBE_IDS,
        }
    robustness = [
        probe
        for row in costs
        for probe in row["metric_robustness_probes"]
        if probe["probe_id"] in ROBUSTNESS_PROBE_IDS
    ]
    diagnostic = [
        probe
        for row in costs
        for probe in row["metric_robustness_probes"]
        if probe["probe_id"] == DIAGNOSTIC_PROBE_ID
    ]
    return {
        "records": records,
        "totals": {
            "robustness_records": len(robustness),
            "robustness_agreements": sum(
                probe["agrees_with_primary"] is True for probe in robustness
            ),
            "robustness_disagreements": sum(
                probe["agrees_with_primary"] is False for probe in robustness
            ),
            "identity_diagnostic_records": len(diagnostic),
            "identity_diagnostic_agreements": sum(
                probe["agrees_with_primary"] is True for probe in diagnostic
            ),
        },
    }


def independent_bracket(
    k: int, rows: Sequence[dict[str, Any]], anchor: int
) -> dict[str, object]:
    expected_widths = Counter({width: 1 for width in range(k + 1, anchor)})
    observed_widths = Counter(int(row["block_size"]) for row in rows)
    if observed_widths != expected_widths:
        raise ValueError("intermediate width rows are not exact and unique")
    statuses = {k: IMPOSSIBLE, anchor: CERTIFIED}
    statuses.update({int(row["block_size"]): row["primary"]["status"] for row in rows})
    s_yes = min(width for width, status in statuses.items() if status == CERTIFIED)
    unresolved = [
        width for width in range(k, s_yes) if statuses.get(width) == UNRESOLVED
    ]
    impossible = [
        width for width in range(k, s_yes) if statuses.get(width) == IMPOSSIBLE
    ]
    s_no = k
    for width in range(k + 1, s_yes):
        if statuses[width] != IMPOSSIBLE:
            break
        s_no = width
    s_star = s_yes if not unresolved and len(impossible) == s_yes - k else None
    return {
        "s_no": s_no,
        "s_yes": s_yes,
        "s_star": s_star,
        "unresolved_widths": unresolved,
        "interval": None if s_star is not None else f"({s_no},{s_yes}]",
        "status_by_width": {str(width): statuses[width] for width in sorted(statuses)},
    }


def compare_design(
    actual: dict[str, Any] | None, expected: dict[str, object] | None
) -> bool:
    if actual is None or expected is None:
        return actual is expected
    keys = {
        "query_count",
        "samples_per_query",
        "total_samples",
        "cutoff",
        "null_tail",
        "familywise_error_upper",
        "signal_power_lower",
        "fwer_mode",
    }
    return all(actual[key] == expected[key] for key in keys)


def independent_anchor_replay(
    anchor: dict[str, Any], config: dict[str, Any]
) -> tuple[bool, list[dict[str, object]]]:
    try:
        if set(anchor) != {
            "schema_version",
            "status",
            "source_frontier",
            "source_frontier_sha256",
            "source_registration",
            "source_registration_sha256",
            "rows",
        }:
            return False, []
        if (
            anchor["schema_version"] != "asmp11_covering_frontier_prior_anchor_v0_2_1"
            or anchor["status"] != "sealed_v0_2_prior_information_not_v0_2_1_claim_grid"
            or anchor["source_frontier"]
            != "../covering_frontier_v0_2/artifacts_v0_2/frontier.csv"
            or anchor["source_registration"]
            != "../covering_frontier_v0_2/registration_v0_2.json"
        ):
            return False, []
        frontier = (ROOT / anchor["source_frontier"]).resolve()
        source_registration = (ROOT / anchor["source_registration"]).resolve()
        if not frontier.is_file() or not source_registration.is_file():
            return False, []
        if sha256(frontier) != anchor["source_frontier_sha256"]:
            return False, []
        if sha256(source_registration) != anchor["source_registration_sha256"]:
            return False, []
        expected_keys = Counter(
            (int(n), int(k)) for n in config["dimensions"] for k in config["degrees"]
        )
        actual_keys = Counter((int(row["n"]), int(row["k"])) for row in anchor["rows"])
        if actual_keys != expected_keys:
            return False, []
        alpha = Fraction(config["alpha"])
        power = Fraction(config["target_power"])
        sample_cap = int(config["sample_cap"])
        receipts: list[dict[str, object]] = []
        for row in anchor["rows"]:
            n, k = int(row["n"]), int(row["k"])
            width = n - 3 if k == 3 else n - 2
            if set(row) != {"n", "k", "block_size", "query_count", "total_samples"}:
                return False, []
            if int(row["block_size"]) != width:
                return False, []
            if set(row["total_samples"]) != {
                str(Fraction(value)) for value in config["flip_rates"]
            }:
                return False, []
            for raw_rate in config["flip_rates"]:
                rate = Fraction(raw_rate)
                design = independent_design(
                    int(row["query_count"]), rate, alpha, power, sample_cap
                )
                baseline = independent_design(
                    comb(n, k), rate, alpha, power, sample_cap
                )
                expected_total = int(row["total_samples"][str(rate)])
                passed = (
                    design is not None
                    and baseline is not None
                    and int(design["total_samples"]) == expected_total
                    and expected_total < int(baseline["total_samples"])
                )
                receipts.append(
                    {
                        "n": n,
                        "k": k,
                        "block_size": width,
                        "flip_rate": str(rate),
                        "query_count": int(row["query_count"]),
                        "expected_total_samples": expected_total,
                        "replayed_total_samples": (
                            int(design["total_samples"]) if design else None
                        ),
                        "observational_baseline_total_samples": (
                            int(baseline["total_samples"]) if baseline else None
                        ),
                        "anchor_beats_observational_baseline": bool(
                            baseline is not None
                            and expected_total < int(baseline["total_samples"])
                        ),
                        "pass": passed,
                    }
                )
        return all(row["pass"] for row in receipts), receipts
    except (KeyError, TypeError, ValueError):
        return False, []


def independent_resource_accounting(
    covers: Sequence[dict[str, Any]],
    resource: dict[str, Any],
    elapsed_total: float,
    total_wall_stop: bool,
) -> dict[str, Any]:
    allowed_stops = {
        "cover_complete",
        "deterministic_round_cap",
        "operational_wall_stop",
        "construction_stalled",
    }
    nonnegative = (
        isfinite(elapsed_total)
        and elapsed_total >= 0
        and all(
            isfinite(float(row["elapsed_seconds"]))
            and float(row["elapsed_seconds"]) >= 0
            for row in covers
        )
    )
    rounds = all(
        0 <= int(row["greedy_rounds"]) <= int(resource["max_greedy_rounds_per_cell"])
        for row in covers
    )
    candidates = all(
        0
        < int(row["candidate_block_count"])
        <= int(resource["max_candidate_blocks_per_cell"])
        for row in covers
    )
    stops = all(row["stop_reason"] in allowed_stops for row in covers)
    metadata = all(
        int(row["universe_size"]) == comb(int(row["n"]), int(row["k"]))
        and int(row["candidate_block_count"])
        == comb(int(row["n"]), int(row["block_size"]))
        and int(row["gain_evaluations"]) >= 0
        for row in covers
    )
    stop_semantics = all(
        (
            row["stop_reason"] != "deterministic_round_cap"
            or int(row["greedy_rounds"]) == int(resource["max_greedy_rounds_per_cell"])
        )
        and (
            row["stop_reason"] != "construction_stalled"
            or int(row["greedy_rounds"]) < int(resource["max_greedy_rounds_per_cell"])
        )
        and (
            row["stop_reason"] != "cover_complete"
            or row["construction_status"]
            in {"deterministic_greedy_incumbent", "exact_bounds_match"}
        )
        for row in covers
    )
    wall_stop_timing = all(
        row["stop_reason"] != "operational_wall_stop"
        or float(row["elapsed_seconds"]) + 1e-9
        >= float(resource["hard_wall_seconds_per_cell"])
        for row in covers
    )
    cell_wall = all(
        row["stop_reason"] == "operational_wall_stop"
        or float(row["elapsed_seconds"])
        <= float(resource["hard_wall_seconds_per_cell"])
        for row in covers
    )
    total_wall = (
        elapsed_total <= float(resource["max_total_wall_seconds"]) or total_wall_stop
    )
    aggregate_elapsed = elapsed_total + 1e-9 >= sum(
        float(row["elapsed_seconds"]) for row in covers
    )
    return {
        "nonnegative_elapsed": nonnegative,
        "rounds_within_registered_cap": rounds,
        "candidates_within_registered_cap": candidates,
        "stop_reasons_valid": stops,
        "cover_metadata_consistent": metadata,
        "stop_semantics_valid": stop_semantics,
        "wall_stop_timing_valid": wall_stop_timing,
        "completed_cells_within_registered_wall": cell_wall,
        "total_wall_consistent": total_wall,
        "aggregate_elapsed_consistent": aggregate_elapsed,
        "ram": {
            "measurement_status": "unmeasured",
            "peak_bytes": None,
            "registered_cap_bytes": int(resource["max_ram_bytes"]),
            "compliance": "not_established",
        },
        "measured_checks_pass": all(
            (
                nonnegative,
                rounds,
                candidates,
                stops,
                metadata,
                stop_semantics,
                wall_stop_timing,
                cell_wall,
                total_wall,
                aggregate_elapsed,
            )
        ),
    }


def operation_consistency_passes(
    operation: dict[str, Any],
    registration: dict[str, Any],
    registration_path: Path,
    covers: Sequence[dict[str, Any]],
    costs: Sequence[dict[str, Any]],
    expected_costs: Counter[Any],
) -> bool:
    try:
        if set(operation) != {
            "schema_version",
            "release_id",
            "run_status",
            "started_utc",
            "finished_utc",
            "elapsed_seconds",
            "total_wall_stop",
            "missing_cost_cells",
            "resource_policy",
            "resource_compliance",
            "stop_reason_counts",
            "registration",
            "environment",
            "events",
        }:
            return False
        if (
            operation["schema_version"] != OPERATION_SCHEMA
            or operation["release_id"] != RELEASE_ID
        ):
            return False
        resource = registration["claim_grid"]["resource_policy"]
        if operation["resource_policy"] != resource:
            return False
        events = operation["events"]
        expected_events = [
            {
                "event": "covering_cell_complete",
                "n": row["n"],
                "k": row["k"],
                "block_size": row["block_size"],
                "construction_status": row["construction_status"],
                "stop_reason": row["stop_reason"],
                "elapsed_seconds": row["elapsed_seconds"],
            }
            for row in covers
        ]
        if events != expected_events:
            return False
        expected_stop_counts = dict(
            sorted(Counter(row["stop_reason"] for row in covers).items())
        )
        if operation["stop_reason_counts"] != expected_stop_counts:
            return False
        observed_costs = Counter(
            (
                int(row["n"]),
                int(row["k"]),
                int(row["block_size"]),
                str(Fraction(row["flip_rate"])),
            )
            for row in costs
        )
        missing = expected_costs - observed_costs
        if operation["missing_cost_cells"] or missing:
            return False
        if operation["total_wall_stop"] is not False:
            return False
        expected_resource = independent_resource_accounting(
            covers,
            resource,
            float(operation["elapsed_seconds"]),
            bool(operation["total_wall_stop"]),
        )
        expected_resource["events_match_covering_rows"] = True
        expected_resource["measured_checks_pass"] = bool(
            expected_resource["measured_checks_pass"]
        )
        if operation["resource_compliance"] != expected_resource:
            return False
        if expected_resource["measured_checks_pass"] is not True:
            return False
        if operation["run_status"] != "complete":
            return False
        started = datetime.fromisoformat(operation["started_utc"])
        finished = datetime.fromisoformat(operation["finished_utc"])
        registered = datetime.fromisoformat(str(registration["registered_at_utc"]))
        if (
            started.utcoffset() != timedelta(0)
            or finished.utcoffset() != timedelta(0)
            or registered.utcoffset() != timedelta(0)
            or started < registered
            or finished < started
        ):
            return False
        registration_record = operation["registration"]
        if set(registration_record) != {
            "path",
            "sha256",
            "source_commit",
            "registration_commit",
        }:
            return False
        if Path(registration_record["path"]).resolve() != registration_path.resolve():
            return False
        if registration_record["sha256"] != sha256(registration_path):
            return False
        if registration_record["source_commit"] != registration["source_commit"]:
            return False
        if set(operation["environment"]) != {
            "python",
            "platform",
            "cpu_count",
            "git_head",
        }:
            return False
        return True
    except (KeyError, TypeError, ValueError, OverflowError):
        return False


def receipt_closure_passes(
    receipt: dict[str, Any],
    registration_path: Path,
    manifest_path: Path,
    anchor_path: Path,
    artifacts: Path,
    claim: dict[str, Any],
    operation: dict[str, Any],
) -> bool:
    try:
        return (
            set(receipt) == RECEIPT_KEYS
            and receipt["schema_version"] == RECEIPT_SCHEMA
            and receipt["release_id"] == RELEASE_ID
            and receipt["registration_sha256"] == sha256(registration_path)
            and receipt["manifest_sha256"] == sha256(manifest_path)
            and receipt["prior_anchor_sha256"] == sha256(anchor_path)
            and set(receipt["outputs"]) == PRIMARY_OUTPUTS
            and receipt["verdict"] == claim["verdict"]
            and operation["registration"]["sha256"] == sha256(registration_path)
            and all(
                (artifacts / name).is_file()
                and not (artifacts / name).is_symlink()
                and sha256(artifacts / name) == receipt["outputs"][name]
                for name in PRIMARY_OUTPUTS
            )
        )
    except (KeyError, TypeError, OSError):
        return False


def expected_metric_firewall() -> dict[str, list[str]]:
    return {
        "selection": ["greedy_uncovered_support_gain"],
        "evidence": [
            "verified_cover_upper_bound",
            "replayed_combinatorial_lower_bound",
            "exact_total_oracle_samples",
            "three_way_crossover_status",
        ],
        "hazard": [
            "greedy_round_cap",
            "operational_wall_stop",
            "candidate_family_cap",
            "covering_bound_width",
            "sample_cap_failure",
        ],
        "overlap": [],
    }


def expected_claim_layer() -> dict[str, Any]:
    return {
        "schema_version": CLAIM_SCHEMA,
        "release_id": RELEASE_ID,
        "verdict": "claim_ready_for_independent_verification",
        "claim_scope": "model_only",
        "observed": "Deterministic covering bounds and exact cost classifications on the frozen intermediate-width grid.",
        "inferred": "Only strata with complete certified brackets support a minimum-width statement.",
        "not_supported": [
            "general adaptive group-testing rates",
            "an observational minimax lower bound",
            "white-box neural backdoor detection",
            "overall resource dominance after pricing intervention width or harm",
        ],
        "robustness": "Four non-identity, non-binding metric probes are reported cell by cell; the identity replay is a diagnostic and is excluded from robustness totals.",
        "confounds": [
            "covering gaps can widen minimum-width brackets",
            "Bonferroni total samples do not price intervention cost",
            "the parity oracle is transparent and finite",
        ],
        "next_experiment": "Independently verify every artifact, then target unresolved covering cells with a separately frozen proof-producing solver.",
    }


def claim_layer_passes(claim: dict[str, Any]) -> bool:
    return claim == expected_claim_layer()


def _verify_bundle_impl(
    registration_path: Path,
    artifacts: Path,
    manifest_path: Path | None = None,
    anchor_path: Path | None = None,
    *,
    enforce_preverification_stage: bool = False,
) -> dict[str, object]:
    manifest_path = (manifest_path or ROOT / "experiment_v0_2_1.json").resolve()
    anchor_path = (anchor_path or ROOT / "prior_anchor_v0_2.json").resolve()
    registration = load_json(registration_path)
    manifest = load_json(manifest_path)
    anchor = load_json(anchor_path)
    config = manifest["asmp11"]
    alpha = Fraction(config["alpha"])
    power = Fraction(config["target_power"])
    sample_cap = int(config["sample_cap"])
    receipt_path = artifacts / "receipt.json"
    receipt = load_json(receipt_path)
    result = load_json(artifacts / "result_layer.json")
    reliability = load_json(artifacts / "reliability_layer.json")
    claim = load_json(artifacts / "claim_layer.json")
    operation = load_json(artifacts / "operation_layer.json")
    covering_checkpoint = load_json(artifacts / "covering_checkpoint.json")
    cost_checkpoint = load_json(artifacts / "cost_checkpoint.json")
    covers = read_jsonl(artifacts / "covering_cells.jsonl")
    costs = read_jsonl(artifacts / "cost_cells.jsonl")

    expected_files = PRIMARY_OUTPUTS | {"receipt.json"}
    allowed_files = expected_files | {
        "independent_verification_v0_2_1_2.json",
        "synthesis_receipt_v0_2_1_2.json",
    }
    present_files = {path.name for path in artifacts.iterdir() if path.is_file()}
    no_nonfiles = all(
        path.is_file() and not path.is_symlink() for path in artifacts.iterdir()
    )
    stage_files_ok = (
        present_files == expected_files
        if enforce_preverification_stage
        else expected_files <= present_files <= allowed_files
    ) and no_nonfiles

    source_binding = source_binding_passes(
        registration, registration_path, manifest, manifest_path, anchor_path, operation
    )
    anchor_ok, anchor_receipts = independent_anchor_replay(anchor, config)
    output_hashes = receipt_closure_passes(
        receipt,
        registration_path,
        manifest_path,
        anchor_path,
        artifacts,
        claim,
        operation,
    )

    expected_grid = expected_grid_counters(config)
    observed_grid = observed_grid_counters(covers, costs, result["brackets"])
    raw_rates_canonical = all(
        isinstance(row.get("flip_rate"), str)
        and row["flip_rate"] == str(Fraction(row["flip_rate"]))
        for row in (*costs, *result["brackets"])
    )
    exact_grid = (
        grid_axes_are_unique_and_canonical(config)
        and raw_rates_canonical
        and raw_record_shapes_pass(covers, costs, result["brackets"])
        and all(observed_grid[name] == expected_grid[name] for name in expected_grid)
    )
    expected_counts = {
        "covering_cells": sum(expected_grid["covering"].values()),
        "cost_cells": sum(expected_grid["cost"].values()),
        "brackets": sum(expected_grid["bracket"].values()),
        "metric_records_per_cost_cell": len(ALL_PROBE_IDS),
        "robustness_probes_per_cost_cell": len(ROBUSTNESS_PROBE_IDS),
    }
    registered_counts = config.get("expected_counts") == expected_counts

    witness_checks: list[bool] = []
    lower_checks: list[bool] = []
    cover_index: dict[tuple[int, int, int], dict[str, Any]] = {}
    for row in covers:
        key = (int(row["n"]), int(row["k"]), int(row["block_size"]))
        lower = independent_lower_bounds(key[0], key[2], key[1])
        witness_checks.append(
            independent_verify_cover(key[0], key[2], key[1], row["selected_blocks"])
            and len(row["selected_blocks"]) == int(row["upper_bound"])
        )
        lower_checks.append(
            lower["counting"] == row["lower_bound_components"]["counting"]
            and lower["schoenheim"] == row["lower_bound_components"]["schoenheim"]
            and lower["certified"] == row["lower_bound"]
            and row["lower_bound"] <= row["upper_bound"]
            and bool(row["optimum_certified"])
            == (row["lower_bound"] == row["upper_bound"])
        )
        if key not in cover_index:
            cover_index[key] = row

    cost_checks: list[bool] = []
    probe_checks: list[bool] = []
    grouped: dict[tuple[int, int, str], list[dict[str, Any]]] = {}
    for row in costs:
        key = (int(row["n"]), int(row["k"]), int(row["block_size"]))
        cover = cover_index.get(key)
        if cover is None:
            cost_checks.append(False)
            probe_checks.append(False)
            continue
        rate = Fraction(row["flip_rate"])
        expected_classification = independent_classification(
            int(cover["lower_bound"]),
            int(cover["upper_bound"]),
            comb(key[0], key[1]),
            rate,
            alpha,
            power,
            sample_cap,
        )
        actual = row["primary"]
        cost_checks.append(
            actual["status"] == expected_classification["status"]
            and actual["lower_query_bound"] == cover["lower_bound"]
            and actual["upper_query_bound"] == cover["upper_bound"]
            and actual["evaluated_query_counts"]
            == int(cover["upper_bound"]) - int(cover["lower_bound"]) + 1
            and compare_design(actual["baseline"], expected_classification["baseline"])
            and compare_design(
                actual["best_certified"], expected_classification["best_certified"]
            )
            and compare_design(
                actual["optimistic_floor"], expected_classification["optimistic_floor"]
            )
        )
        expected_probes = independent_probe_records(
            int(cover["lower_bound"]),
            int(cover["upper_bound"]),
            comb(key[0], key[1]),
            rate,
            alpha,
            power,
            sample_cap,
        )
        probe_checks.append(row["metric_robustness_probes"] == expected_probes)
        grouped.setdefault((key[0], key[1], str(rate)), []).append(row)

    anchor_index = {(int(row["n"]), int(row["k"])): row for row in anchor["rows"]}
    bracket_index = {
        (int(row["n"]), int(row["k"]), str(Fraction(row["flip_rate"]))): row
        for row in result["brackets"]
    }
    bracket_checks: list[bool] = []
    for key in expected_grid["bracket"]:
        n, k, _ = key
        rows = grouped.get(key, [])
        try:
            expected_bracket = independent_bracket(k, rows, n - 3 if k == 3 else n - 2)
        except (KeyError, ValueError):
            bracket_checks.append(False)
            continue
        actual = bracket_index.get(key)
        bracket_checks.append(
            actual is not None
            and actual.get("anchor_query_count")
            == int(anchor_index[(n, k)]["query_count"])
            and all(
                actual.get(field) == value for field, value in expected_bracket.items()
            )
        )

    probe_summary = independent_probe_summary(costs)
    probes_complete = (
        bool(probe_checks)
        and all(probe_checks)
        and reliability.get("metric_robustness") == probe_summary
    )
    operation_ok = operation_consistency_passes(
        operation, registration, registration_path, covers, costs, expected_grid["cost"]
    )
    resource_cover_ok = all(
        (not bool(row["optimum_certified"]) or row["lower_bound"] == row["upper_bound"])
        and (
            row["stop_reason"] == "cover_complete"
            or independent_verify_cover(
                int(row["n"]),
                int(row["block_size"]),
                int(row["k"]),
                row["selected_blocks"],
            )
        )
        for row in covers
    )
    recomputed_primary_gates = {
        "B0_binding": anchor_ok and reliability.get("anchor_replay") == anchor_receipts,
        "B1_witness_validity": bool(witness_checks) and all(witness_checks),
        "B2_lower_bound_replay": bool(lower_checks) and all(lower_checks),
        "B3_probability_exactness": bool(cost_checks) and all(cost_checks),
        "B4_total_classification": exact_grid and registered_counts,
        "B5_minimum_width": bool(bracket_checks) and all(bracket_checks),
        "B6_resource_honesty_ram_unmeasured": operation_ok and resource_cover_ok,
        "B7_metric_probe_completeness": probes_complete,
    }
    primary_gates_exact = reliability.get(
        "binding_gates"
    ) == recomputed_primary_gates and all(recomputed_primary_gates.values())

    checkpoint_ok = covering_checkpoint == {
        "schema_version": "asmp11_v0_2_1_2_covering_checkpoint",
        "complete_cells": len(covers),
        "rows": covers,
    } and cost_checkpoint == {
        "schema_version": "asmp11_v0_2_1_2_cost_checkpoint",
        "complete_cells": len(costs),
        "missing_cells": [],
    }
    result_ok = (
        set(result)
        == {
            "schema_version",
            "release_id",
            "experimental_unit",
            "counts",
            "exact_grid_counters",
            "brackets",
            "raw_artifacts",
        }
        and result.get("schema_version") == RESULT_SCHEMA
        and result.get("release_id") == RELEASE_ID
        and result.get("experimental_unit") == "one deterministic (n,k,s) covering cell"
        and result.get("counts")
        == {
            "covering_cells": len(covers),
            "cost_cells": len(costs),
            "brackets": len(result["brackets"]),
            "status": dict(
                sorted(Counter(row["primary"]["status"] for row in costs).items())
            ),
        }
        and result.get("exact_grid_counters")
        == {"covering": True, "cost": True, "bracket": True}
        and result.get("raw_artifacts")
        == {"covering_cells": "covering_cells.jsonl", "cost_cells": "cost_cells.jsonl"}
    )
    layer_separation = (
        result_ok
        and set(reliability)
        == {
            "schema_version",
            "release_id",
            "binding_gates",
            "metric_firewall",
            "metric_robustness",
            "anchor_replay",
            "independent_verification",
        }
        and reliability.get("schema_version") == RELIABILITY_SCHEMA
        and reliability.get("release_id") == RELEASE_ID
        and reliability.get("metric_firewall") == expected_metric_firewall()
        and reliability.get("independent_verification")
        == "pending separate verify_result.py execution"
        and claim_layer_passes(claim)
        and operation.get("schema_version") == OPERATION_SCHEMA
        and operation.get("release_id") == RELEASE_ID
    )
    claim_operation = (
        claim_layer_passes(claim)
        and operation.get("run_status") == "complete"
        and receipt.get("verdict") == claim.get("verdict")
    )
    gates = {
        "V0_source_registration_binding": source_binding,
        "V1_receipt_output_link_closure": stage_files_ok and output_hashes,
        "V2_cover_witnesses_and_lower_bounds": bool(witness_checks)
        and all(witness_checks)
        and all(lower_checks),
        "V3_exact_cost_classification": bool(cost_checks) and all(cost_checks),
        "V4_full_metric_probe_replay": probes_complete,
        "V5_minimum_width_brackets": bool(bracket_checks) and all(bracket_checks),
        "V6_layer_and_metric_firewall": layer_separation,
        "V7_exact_registered_cartesian_grid": exact_grid and registered_counts,
        "V8_primary_gates_exactly_recomputed": primary_gates_exact,
        "V9_operation_and_resource_consistency": operation_ok,
        "V10_prior_anchor_independent_replay": anchor_ok,
        "V11_checkpoint_raw_row_consistency": checkpoint_ok,
        "V12_claim_operation_consistency": claim_operation,
    }
    verified = all(gates.values())
    return {
        "schema_version": VERIFICATION_SCHEMA,
        "release_id": RELEASE_ID,
        "verified": verified,
        "gates": gates,
        "registration_sha256": sha256(registration_path),
        "receipt_sha256": sha256(receipt_path),
        "primary_outputs": dict(sorted(receipt.get("outputs", {}).items())),
        "counts": {
            "covering_cells": len(covers),
            "cost_cells": len(costs),
            "brackets": len(result["brackets"]),
        },
        "metric_robustness": probe_summary,
        "resource_assessment": {
            "measured_resource_checks": "passed" if operation_ok else "failed",
            "wall_observations": "self_reported_internally_consistent"
            if operation_ok
            else "failed",
            "ram_compliance": "not_established_unmeasured",
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def verify_bundle(
    registration_path: Path,
    artifacts: Path,
    manifest_path: Path | None = None,
    anchor_path: Path | None = None,
    *,
    enforce_preverification_stage: bool = False,
) -> dict[str, object]:
    """Verify fail-closed; malformed or incomplete bundles produce failed gates."""

    try:
        return _verify_bundle_impl(
            registration_path,
            artifacts,
            manifest_path,
            anchor_path,
            enforce_preverification_stage=enforce_preverification_stage,
        )
    except (
        ArithmeticError,
        AssertionError,
        AttributeError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
        subprocess.CalledProcessError,
    ):
        return {
            "schema_version": VERIFICATION_SCHEMA,
            "release_id": RELEASE_ID,
            "verified": False,
            "gates": {gate: False for gate in VERIFICATION_GATE_IDS},
            "registration_sha256": (
                sha256(registration_path) if registration_path.is_file() else None
            ),
            "receipt_sha256": None,
            "primary_outputs": {},
            "counts": {"covering_cells": 0, "cost_cells": 0, "brackets": 0},
            "metric_robustness": {"records": {}, "totals": {}},
            "resource_assessment": {
                "measured_resource_checks": "failed",
                "wall_observations": "failed",
                "ram_compliance": "not_established_unmeasured",
            },
            "claim_boundary": CLAIM_BOUNDARY,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument(
        "--manifest", type=Path, default=ROOT / "experiment_v0_2_1.json"
    )
    parser.add_argument(
        "--prior-anchor", type=Path, default=ROOT / "prior_anchor_v0_2.json"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Defaults to ARTIFACTS/independent_verification_v0_2_1_2.json",
    )
    args = parser.parse_args()
    registration_path = args.registration.resolve()
    artifacts_path = args.artifacts.resolve()
    if registration_path != (ROOT / REGISTRATION_FILENAME).resolve():
        raise ValueError("verification requires the exact v0.2.1.2 registration path")
    if artifacts_path != (ROOT / ARTIFACT_DIRECTORY).resolve():
        raise ValueError("verification requires the exact v0.2.1.2 artifact directory")
    result = verify_bundle(
        registration_path,
        artifacts_path,
        args.manifest.resolve(),
        args.prior_anchor.resolve(),
        enforce_preverification_stage=True,
    )
    output = (
        args.output.resolve() if args.output else artifacts_path / VERIFICATION_FILENAME
    )
    if output != artifacts_path / VERIFICATION_FILENAME:
        raise ValueError("verification output must use its exact in-bundle path")
    if output.exists():
        raise FileExistsError(f"verification receipt is write-once: {output}")
    temporary = output.with_suffix(output.suffix + ".tmp")
    write_lf_text(
        temporary,
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )
    os.replace(temporary, output)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if result["verified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
