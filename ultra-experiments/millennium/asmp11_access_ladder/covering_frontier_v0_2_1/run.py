#!/usr/bin/env python3
"""Run the prospectively registered ASMP-11 v0.2.1 bounds experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from math import comb, isfinite
from pathlib import Path
from time import monotonic
from typing import Any, Iterable

from crossover_frontier import (
    CLASSIFICATION_STATUSES,
    build_minimum_width_bracket,
    classification_record,
    deterministic_cover_bounds,
    find_exact_design,
    high_width_anchor,
    intermediate_widths,
    metric_robustness_probes,
    replayable_lower_bound,
    verify_cover,
    classify_cost_interval,
)
from release_contract import (
    ALL_PROBE_IDS,
    ARTIFACT_DIRECTORY,
    BOUND_SOURCES,
    CLAIM_BOUNDARY,
    CLAIM_SCHEMA,
    DIAGNOSTIC_PROBE_ID,
    FROZEN_CLAIM_GRID,
    MATHEMATICAL_PROTOCOL_ID,
    OPERATION_SCHEMA,
    PRIMARY_OUTPUTS,
    REGISTRATION_FILENAME,
    RECEIPT_KEYS,
    RECEIPT_SCHEMA,
    REGISTRATION_KEYS,
    REGISTRATION_SCHEMA,
    RELEASE_ID,
    RELIABILITY_SCHEMA,
    RESULT_SCHEMA,
    ROBUSTNESS_PROBE_IDS,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_MANIFEST = ROOT / "experiment_v0_2_1.json"
DEFAULT_ANCHOR = ROOT / "prior_anchor_v0_2.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def compact_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def write_lf_text(path: Path, payload: str) -> None:
    """Write UTF-8 text without platform newline translation."""

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


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_unique_object,
        parse_constant=_reject_nonfinite,
    )


def atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    write_lf_text(temporary, canonical_json(payload))
    os.replace(temporary, path)


def write_jsonl(path: Path, rows: Iterable[dict[str, object]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(compact_json(row) + "\n")
    os.replace(temporary, path)


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git(*args: str, text: bool = True) -> str | bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=text).strip()


def _full_commit(reference: str) -> str:
    commit = str(git("rev-parse", "--verify", f"{reference}^{{commit}}"))
    if len(commit) != 40 or any(
        character not in "0123456789abcdef" for character in commit
    ):
        raise RuntimeError(f"not a full Git commit id: {commit}")
    return commit


def _committed_bytes(commit: str, path: Path) -> bytes:
    repo_root = Path(str(git("rev-parse", "--show-toplevel")))
    relative = path.resolve().relative_to(repo_root).as_posix()
    return subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=ROOT)


def _git_blob_oid(commit: str, path: Path) -> str:
    repo_root = Path(str(git("rev-parse", "--show-toplevel")))
    relative = path.resolve().relative_to(repo_root).as_posix()
    oid = str(git("rev-parse", f"{commit}:{relative}"))
    if (
        len(oid) != 40
        or any(character not in "0123456789abcdef" for character in oid)
        or str(git("cat-file", "-t", oid)) != "blob"
    ):
        raise RuntimeError(f"committed source is not a full Git blob: {relative}")
    return oid


def _registration_commit(registration_path: Path, source_commit: str) -> str | None:
    head = _full_commit("HEAD")
    repo_root = Path(str(git("rev-parse", "--show-toplevel")))
    try:
        relative = registration_path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return None
    registration_commit = str(
        git("log", "-1", "--format=%H", head, "--", f":(top){relative}")
    )
    if not registration_commit or registration_commit == source_commit:
        return None
    source_before_registration = (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", source_commit, registration_commit],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )
    registration_before_execution = (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", registration_commit, head],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )
    if not source_before_registration or not registration_before_execution:
        return None
    try:
        if hashlib.sha256(
            _committed_bytes(registration_commit, registration_path)
        ).hexdigest() != sha256(registration_path):
            return None
    except (ValueError, subprocess.CalledProcessError):
        return None
    return registration_commit


def validate_registration(
    registration_path: Path,
    manifest_path: Path = DEFAULT_MANIFEST,
    anchor_path: Path = DEFAULT_ANCHOR,
    *,
    require_committed_registration: bool = True,
) -> dict[str, Any]:
    registration = load_json(registration_path)
    if (
        require_committed_registration
        and registration_path.resolve() != (ROOT / REGISTRATION_FILENAME).resolve()
    ):
        raise RuntimeError("registration path does not match the v0.2.1.2 contract")
    if set(registration) != REGISTRATION_KEYS:
        raise RuntimeError(
            "registration field set does not match the v0.2.1.2 contract"
        )
    if registration.get("schema_version") != REGISTRATION_SCHEMA:
        raise RuntimeError("registration schema does not match v0.2.1.2")
    if registration.get("release_id") != RELEASE_ID:
        raise RuntimeError("registration release id does not match v0.2.1.2")
    if registration.get("protocol_id") != MATHEMATICAL_PROTOCOL_ID:
        raise RuntimeError("registration mathematical protocol changed")
    if (
        registration.get("status")
        != "prospective_registration_before_claim_grid_execution"
    ):
        raise RuntimeError(
            "registration status does not authorize claim-grid execution"
        )
    if registration.get("proposed_asmp_id") != "ASMP-11":
        raise RuntimeError("registration ASMP id mismatch")
    if registration.get("claim_boundary") != CLAIM_BOUNDARY:
        raise RuntimeError("registration claim boundary mismatch")
    if registration.get("output_policy") != "write_once_non_aliasing":
        raise RuntimeError("registration output policy mismatch")
    try:
        registered_at = datetime.fromisoformat(str(registration["registered_at_utc"]))
    except ValueError as exc:
        raise RuntimeError("registration timestamp is not ISO-8601") from exc
    if registered_at.utcoffset() != timedelta(0):
        raise RuntimeError("registration timestamp must be UTC")
    source_commit = registration.get("source_commit")
    if (
        not isinstance(source_commit, str)
        or _full_commit(source_commit) != source_commit
    ):
        raise RuntimeError("registration must record a full source commit id")
    source_hashes = registration.get("source_hashes")
    blob_oids = registration.get("source_git_blob_oids")
    if not isinstance(source_hashes, dict) or set(source_hashes) != set(BOUND_SOURCES):
        raise RuntimeError("registration source hash set is not exact")
    if not isinstance(blob_oids, dict) or set(blob_oids) != set(BOUND_SOURCES):
        raise RuntimeError("registration Git blob set is not exact")
    mismatches = []
    for relative in BOUND_SOURCES:
        expected = source_hashes[relative]
        path = ROOT / relative
        try:
            committed = _committed_bytes(source_commit, path)
            committed_sha256 = hashlib.sha256(committed).hexdigest()
            committed_oid = _git_blob_oid(source_commit, path)
        except (ValueError, subprocess.CalledProcessError):
            mismatches.append(relative)
            continue
        if (
            not path.is_file()
            or path.is_symlink()
            or sha256(path) != expected
            or committed_sha256 != expected
            or committed_oid != blob_oids[relative]
        ):
            mismatches.append(relative)
    if mismatches:
        raise RuntimeError(f"registration source mismatch: {mismatches}")
    manifest = load_json(manifest_path)
    if registration["manifest_path"] != "experiment_v0_2_1.json":
        raise RuntimeError("registered manifest name is not exact")
    if registration["prior_anchor_path"] != "prior_anchor_v0_2.json":
        raise RuntimeError("registered prior-anchor name is not exact")
    if (
        manifest_path.is_symlink()
        or manifest_path.resolve() != (ROOT / registration["manifest_path"]).resolve()
    ):
        raise RuntimeError("supplied manifest path is not the registered manifest path")
    if (
        anchor_path.is_symlink()
        or anchor_path.resolve() != (ROOT / registration["prior_anchor_path"]).resolve()
    ):
        raise RuntimeError(
            "supplied prior-anchor path is not the registered anchor path"
        )
    if sha256(manifest_path) != registration["manifest_sha256"]:
        raise RuntimeError("supplied manifest is not the registered manifest")
    if sha256(anchor_path) != registration["prior_anchor_sha256"]:
        raise RuntimeError("supplied prior anchor is not the registered anchor")
    if registration["manifest_sha256"] != source_hashes["experiment_v0_2_1.json"]:
        raise RuntimeError("manifest hash is not closed by the source map")
    if registration["prior_anchor_sha256"] != source_hashes["prior_anchor_v0_2.json"]:
        raise RuntimeError("prior-anchor hash is not closed by the source map")
    if registration["claim_grid"] != FROZEN_CLAIM_GRID:
        raise RuntimeError("registered grid differs from the frozen v0.2.1.2 grid")
    if registration["claim_grid"] != manifest.get("asmp11"):
        raise RuntimeError("registered grid differs from the manifest grid")
    if (
        require_committed_registration
        and _registration_commit(registration_path, source_commit) is None
    ):
        raise RuntimeError("registration must be committed after the source checkpoint")
    return registration


def expected_cover_counter(config: dict[str, Any]) -> Counter[tuple[int, int, int]]:
    return Counter(
        (int(n), int(k), int(block_size))
        for n in config["dimensions"]
        for k in config["degrees"]
        for block_size in intermediate_widths(int(n), int(k))
    )


def expected_cost_counter(config: dict[str, Any]) -> Counter[tuple[int, int, int, str]]:
    return Counter(
        (
            int(n),
            int(k),
            int(block_size),
            str(Fraction(str(flip_rate))),
        )
        for n in config["dimensions"]
        for k in config["degrees"]
        for block_size in intermediate_widths(int(n), int(k))
        for flip_rate in config["flip_rates"]
    )


def expected_bracket_counter(config: dict[str, Any]) -> Counter[tuple[int, int, str]]:
    return Counter(
        (int(n), int(k), str(Fraction(str(flip_rate))))
        for n in config["dimensions"]
        for k in config["degrees"]
        for flip_rate in config["flip_rates"]
    )


def grid_axes_are_unique_and_canonical(config: dict[str, Any]) -> bool:
    try:
        dimensions = config["dimensions"]
        degrees = config["degrees"]
        rates = config["flip_rates"]
        counters = (
            expected_cover_counter(config),
            expected_cost_counter(config),
            expected_bracket_counter(config),
        )
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
            and all(count == 1 for counter in counters for count in counter.values())
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def exact_grid_counters(
    config: dict[str, Any],
    covering_rows: Iterable[dict[str, Any]],
    cost_rows: Iterable[dict[str, Any]],
    brackets: Iterable[dict[str, Any]],
) -> dict[str, bool]:
    covering_rows = list(covering_rows)
    cost_rows = list(cost_rows)
    brackets = list(brackets)
    covers = Counter(
        (int(row["n"]), int(row["k"]), int(row["block_size"])) for row in covering_rows
    )
    costs = Counter(
        (
            int(row["n"]),
            int(row["k"]),
            int(row["block_size"]),
            str(Fraction(str(row["flip_rate"]))),
        )
        for row in cost_rows
    )
    bracket_keys = Counter(
        (
            int(row["n"]),
            int(row["k"]),
            str(Fraction(str(row["flip_rate"]))),
        )
        for row in brackets
    )
    cover_key_types = all(
        all(
            isinstance(row.get(field), int) and not isinstance(row.get(field), bool)
            for field in ("n", "k", "block_size")
        )
        for row in covering_rows
    )
    cost_key_types = all(
        all(
            isinstance(row.get(field), int) and not isinstance(row.get(field), bool)
            for field in ("n", "k", "block_size")
        )
        for row in cost_rows
    )
    bracket_key_types = all(
        all(
            isinstance(row.get(field), int) and not isinstance(row.get(field), bool)
            for field in ("n", "k")
        )
        for row in brackets
    )
    canonical_cost_rates = all(
        isinstance(row.get("flip_rate"), str)
        and row["flip_rate"] == str(Fraction(row["flip_rate"]))
        for row in cost_rows
    )
    canonical_bracket_rates = all(
        isinstance(row.get("flip_rate"), str)
        and row["flip_rate"] == str(Fraction(row["flip_rate"]))
        for row in brackets
    )
    return {
        "covering": cover_key_types and covers == expected_cover_counter(config),
        "cost": cost_key_types
        and canonical_cost_rates
        and costs == expected_cost_counter(config),
        "bracket": bracket_key_types
        and canonical_bracket_rates
        and bracket_keys == expected_bracket_counter(config),
    }


def validate_prior_anchor(
    anchor_path: Path, config: dict[str, Any] | None = None
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    anchor = load_json(anchor_path)
    if config is None:
        config = load_json(DEFAULT_MANIFEST)["asmp11"]
    source_frontier = (ROOT / anchor["source_frontier"]).resolve()
    source_registration = (ROOT / anchor["source_registration"]).resolve()
    expected_rows = Counter(
        (int(n), int(k)) for n in config["dimensions"] for k in config["degrees"]
    )
    actual_rows = Counter(
        (int(row["n"]), int(row["k"])) for row in anchor.get("rows", [])
    )
    row_shapes = all(
        set(row) == {"n", "k", "block_size", "query_count", "total_samples"}
        and int(row["block_size"]) == high_width_anchor(int(row["n"]), int(row["k"]))
        and int(row["query_count"]) > 0
        and set(row["total_samples"]) == {str(value) for value in config["flip_rates"]}
        for row in anchor.get("rows", [])
    )
    checks = {
        "anchor_field_set": set(anchor)
        == {
            "schema_version",
            "status",
            "source_frontier",
            "source_frontier_sha256",
            "source_registration",
            "source_registration_sha256",
            "rows",
        },
        "anchor_schema": anchor.get("schema_version")
        == "asmp11_covering_frontier_prior_anchor_v0_2_1",
        "anchor_status": anchor.get("status")
        == "sealed_v0_2_prior_information_not_v0_2_1_claim_grid",
        "source_frontier_path": anchor.get("source_frontier")
        == "../covering_frontier_v0_2/artifacts_v0_2/frontier.csv",
        "source_registration_path": anchor.get("source_registration")
        == "../covering_frontier_v0_2/registration_v0_2.json",
        "anchor_grid_exact": actual_rows == expected_rows,
        "anchor_row_shapes": row_shapes,
        "frontier_exists": source_frontier.is_file(),
        "registration_exists": source_registration.is_file(),
        "frontier_sha256": source_frontier.is_file()
        and sha256(source_frontier) == anchor["source_frontier_sha256"],
        "registration_sha256": source_registration.is_file()
        and sha256(source_registration) == anchor["source_registration_sha256"],
    }
    if not all(checks.values()):
        raise RuntimeError(f"sealed v0.2 prior anchor mismatch: {checks}")
    return anchor, [{"check": key, "pass": value} for key, value in checks.items()]


def cover_record(certificate: Any, elapsed_seconds: float) -> dict[str, object]:
    return {
        "n": certificate.n,
        "k": certificate.support_size,
        "block_size": certificate.block_size,
        "lower_bound": certificate.lower_bound,
        "lower_bound_components": {
            "counting": certificate.counting_lower_bound,
            "schoenheim": certificate.schoenheim_lower_bound,
        },
        "upper_bound": certificate.upper_bound,
        "optimum_certified": certificate.optimum_certified,
        "construction_status": certificate.construction_status,
        "stop_reason": certificate.stop_reason,
        "greedy_rounds": certificate.greedy_rounds,
        "gain_evaluations": certificate.gain_evaluations,
        "universe_size": certificate.universe_size,
        "candidate_block_count": certificate.candidate_block_count,
        "elapsed_seconds": elapsed_seconds,
        "selected_blocks": [list(block) for block in certificate.selected_blocks],
    }


def anchor_lookup(anchor: dict[str, Any]) -> dict[tuple[int, int], dict[str, Any]]:
    return {(int(row["n"]), int(row["k"])): row for row in anchor["rows"]}


def verify_anchor_costs(
    anchor: dict[str, Any],
    flip_rates: tuple[Fraction, ...],
    alpha: Fraction,
    target_power: Fraction,
    sample_cap: int,
) -> list[dict[str, object]]:
    receipts = []
    for row in anchor["rows"]:
        n, k = int(row["n"]), int(row["k"])
        expected_width = high_width_anchor(n, k)
        if int(row["block_size"]) != expected_width:
            raise RuntimeError("sealed anchor width does not match the draft rule")
        for flip_rate in flip_rates:
            design = find_exact_design(
                int(row["query_count"]),
                flip_rate,
                alpha,
                target_power,
                sample_cap,
            )
            baseline = find_exact_design(
                comb(n, k),
                flip_rate,
                alpha,
                target_power,
                sample_cap,
            )
            expected = int(row["total_samples"][str(flip_rate)])
            passed = (
                design is not None
                and baseline is not None
                and design.total_samples == expected
                and expected < baseline.total_samples
            )
            receipts.append(
                {
                    "n": n,
                    "k": k,
                    "block_size": expected_width,
                    "flip_rate": str(flip_rate),
                    "query_count": int(row["query_count"]),
                    "expected_total_samples": expected,
                    "replayed_total_samples": design.total_samples if design else None,
                    "observational_baseline_total_samples": (
                        baseline.total_samples if baseline else None
                    ),
                    "anchor_beats_observational_baseline": bool(
                        baseline is not None and expected < baseline.total_samples
                    ),
                    "pass": passed,
                }
            )
    if not all(row["pass"] for row in receipts):
        raise RuntimeError("sealed v0.2 anchor cost failed exact replay")
    return receipts


def _design_is_exact(
    record: dict[str, object] | None, alpha: Fraction, power: Fraction
) -> bool:
    if record is None:
        return True
    return (
        Fraction(str(record["familywise_error_upper"])) <= alpha
        and Fraction(str(record["signal_power_lower"])) >= power
        and int(record["total_samples"])
        == int(record["query_count"]) * int(record["samples_per_query"])
    )


def probe_pack_is_well_formed(
    cost_rows: Iterable[dict[str, Any]], expected_records_per_cell: int
) -> bool:
    for row in cost_rows:
        probes = row.get("metric_robustness_probes")
        if not isinstance(probes, list) or len(probes) != expected_records_per_cell:
            return False
        if [probe.get("probe_id") for probe in probes] != list(ALL_PROBE_IDS):
            return False
        primary_status = row.get("primary", {}).get("status")
        for probe in probes:
            probe_id = probe["probe_id"]
            if probe.get("binding") is not False:
                return False
            if probe.get("agrees_with_primary") != (
                probe.get("status") == primary_status
            ):
                return False
            if probe_id == DIAGNOSTIC_PROBE_ID:
                if (
                    probe.get("record_kind") != "identity_diagnostic"
                    or probe.get("counts_toward_robustness") is not False
                ):
                    return False
            elif probe_id in ROBUSTNESS_PROBE_IDS:
                if (
                    probe.get("record_kind") != "robustness_probe"
                    or probe.get("counts_toward_robustness") is not True
                    or not isinstance(probe.get("probe_family"), str)
                ):
                    return False
            else:
                return False
    return True


def summarize_probe_records(cost_rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(cost_rows)
    records: dict[str, dict[str, Any]] = {}
    for probe_id in ALL_PROBE_IDS:
        observed = [
            probe
            for row in rows
            for probe in row["metric_robustness_probes"]
            if probe["probe_id"] == probe_id
        ]
        counts_toward = probe_id in ROBUSTNESS_PROBE_IDS
        records[probe_id] = {
            "cells": len(observed),
            "agrees_with_primary": sum(
                probe["agrees_with_primary"] is True for probe in observed
            ),
            "disagrees_with_primary": sum(
                probe["agrees_with_primary"] is False for probe in observed
            ),
            "binding_false": sum(probe["binding"] is False for probe in observed),
            "counts_toward_robustness": counts_toward,
        }
    robustness_records = [
        probe
        for row in rows
        for probe in row["metric_robustness_probes"]
        if probe["probe_id"] in ROBUSTNESS_PROBE_IDS
    ]
    diagnostic_records = [
        probe
        for row in rows
        for probe in row["metric_robustness_probes"]
        if probe["probe_id"] == DIAGNOSTIC_PROBE_ID
    ]
    return {
        "records": records,
        "totals": {
            "robustness_records": len(robustness_records),
            "robustness_agreements": sum(
                probe["agrees_with_primary"] is True for probe in robustness_records
            ),
            "robustness_disagreements": sum(
                probe["agrees_with_primary"] is False for probe in robustness_records
            ),
            "identity_diagnostic_records": len(diagnostic_records),
            "identity_diagnostic_agreements": sum(
                probe["agrees_with_primary"] is True for probe in diagnostic_records
            ),
        },
    }


def resource_accounting(
    covering_rows: Iterable[dict[str, Any]],
    resource: dict[str, Any],
    elapsed_total: float,
    total_wall_stop: bool,
) -> dict[str, Any]:
    rows = list(covering_rows)
    allowed_stops = {
        "cover_complete",
        "deterministic_round_cap",
        "operational_wall_stop",
        "construction_stalled",
    }
    nonnegative_elapsed = (
        isfinite(elapsed_total)
        and elapsed_total >= 0
        and all(
            isfinite(float(row["elapsed_seconds"]))
            and float(row["elapsed_seconds"]) >= 0
            for row in rows
        )
    )
    rounds_within_cap = all(
        int(row["greedy_rounds"]) <= int(resource["max_greedy_rounds_per_cell"])
        for row in rows
    )
    candidates_within_cap = all(
        int(row["candidate_block_count"])
        <= int(resource["max_candidate_blocks_per_cell"])
        for row in rows
    )
    stop_reasons_valid = all(row["stop_reason"] in allowed_stops for row in rows)
    cover_metadata_consistent = all(
        int(row["universe_size"]) == comb(int(row["n"]), int(row["k"]))
        and int(row["candidate_block_count"])
        == comb(int(row["n"]), int(row["block_size"]))
        and int(row["gain_evaluations"]) >= 0
        for row in rows
    )
    stop_semantics_valid = all(
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
        for row in rows
    )
    wall_stop_timing_valid = all(
        row["stop_reason"] != "operational_wall_stop"
        or float(row["elapsed_seconds"]) + 1e-9
        >= float(resource["hard_wall_seconds_per_cell"])
        for row in rows
    )
    completed_cells_within_wall = all(
        row["stop_reason"] == "operational_wall_stop"
        or float(row["elapsed_seconds"])
        <= float(resource["hard_wall_seconds_per_cell"])
        for row in rows
    )
    total_wall_consistent = (
        elapsed_total <= float(resource["max_total_wall_seconds"]) or total_wall_stop
    )
    aggregate_elapsed_consistent = elapsed_total + 1e-9 >= sum(
        float(row["elapsed_seconds"]) for row in rows
    )
    return {
        "nonnegative_elapsed": nonnegative_elapsed,
        "rounds_within_registered_cap": rounds_within_cap,
        "candidates_within_registered_cap": candidates_within_cap,
        "stop_reasons_valid": stop_reasons_valid,
        "cover_metadata_consistent": cover_metadata_consistent,
        "stop_semantics_valid": stop_semantics_valid,
        "wall_stop_timing_valid": wall_stop_timing_valid,
        "completed_cells_within_registered_wall": completed_cells_within_wall,
        "total_wall_consistent": total_wall_consistent,
        "aggregate_elapsed_consistent": aggregate_elapsed_consistent,
        "ram": {
            "measurement_status": "unmeasured",
            "peak_bytes": None,
            "registered_cap_bytes": int(resource["max_ram_bytes"]),
            "compliance": "not_established",
        },
        "measured_checks_pass": all(
            (
                nonnegative_elapsed,
                rounds_within_cap,
                candidates_within_cap,
                stop_reasons_valid,
                cover_metadata_consistent,
                stop_semantics_valid,
                wall_stop_timing_valid,
                completed_cells_within_wall,
                total_wall_consistent,
                aggregate_elapsed_consistent,
            )
        ),
    }


def execute(
    registration_path: Path,
    output_dir: Path,
    manifest_path: Path = DEFAULT_MANIFEST,
    anchor_path: Path = DEFAULT_ANCHOR,
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    registration = validate_registration(registration_path, manifest_path, anchor_path)
    manifest = load_json(manifest_path)
    config = manifest["asmp11"]
    if config != registration["claim_grid"]:
        raise RuntimeError("runtime grid differs from the registered grid")
    resource = config["resource_policy"]
    anchor, anchor_binding_checks = validate_prior_anchor(anchor_path, config)
    protected_outputs = {
        (ROOT / "artifacts_v0_2_1").resolve(),
        (ROOT / "artifacts_v0_2_1_1").resolve(),
    }
    if output_dir.resolve() != (ROOT / ARTIFACT_DIRECTORY).resolve():
        raise RuntimeError("v0.2.1.2 output must use its exact non-aliasing directory")
    if output_dir.resolve() in protected_outputs:
        raise RuntimeError("v0.2.1.2 cannot alias an earlier evidence directory")
    if output_dir.exists():
        raise FileExistsError(
            f"write-once output directory already exists: {output_dir}"
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    started_utc = utc_now()
    started = monotonic()
    dimensions = tuple(int(value) for value in config["dimensions"])
    degrees = tuple(int(value) for value in config["degrees"])
    flip_rates = tuple(parse_fraction(value) for value in config["flip_rates"])
    alpha = parse_fraction(config["alpha"])
    target_power = parse_fraction(config["target_power"])
    sample_cap = int(config["sample_cap"])
    expected = config["expected_counts"]
    anchor_receipts = verify_anchor_costs(
        anchor, flip_rates, alpha, target_power, sample_cap
    )
    anchors = anchor_lookup(anchor)

    covering_rows: list[dict[str, object]] = []
    certificates: dict[tuple[int, int, int], Any] = {}
    operation_events: list[dict[str, object]] = []
    total_wall_stop = False
    for n in dimensions:
        for k in degrees:
            for block_size in intermediate_widths(n, k):
                if monotonic() - started >= float(resource["max_total_wall_seconds"]):
                    total_wall_stop = True
                    break
                cell_started = monotonic()
                certificate = deterministic_cover_bounds(
                    n,
                    block_size,
                    k,
                    max_greedy_rounds=int(resource["max_greedy_rounds_per_cell"]),
                    max_candidate_blocks=int(resource["max_candidate_blocks_per_cell"]),
                    hard_wall_seconds=float(resource["hard_wall_seconds_per_cell"]),
                )
                elapsed = monotonic() - cell_started
                row = cover_record(certificate, elapsed)
                covering_rows.append(row)
                certificates[(n, k, block_size)] = certificate
                event = {
                    "event": "covering_cell_complete",
                    "n": n,
                    "k": k,
                    "block_size": block_size,
                    "construction_status": certificate.construction_status,
                    "stop_reason": certificate.stop_reason,
                    "elapsed_seconds": elapsed,
                }
                operation_events.append(event)
                atomic_json(
                    output_dir / "covering_checkpoint.json",
                    {
                        "schema_version": "asmp11_v0_2_1_2_covering_checkpoint",
                        "complete_cells": len(covering_rows),
                        "rows": covering_rows,
                    },
                )
            if total_wall_stop:
                break
        if total_wall_stop:
            break

    cost_rows: list[dict[str, object]] = []
    missing_cost_keys: list[dict[str, object]] = []
    for n in dimensions:
        for k in degrees:
            for block_size in intermediate_widths(n, k):
                certificate = certificates.get((n, k, block_size))
                for flip_rate in flip_rates:
                    if certificate is None or monotonic() - started >= float(
                        resource["max_total_wall_seconds"]
                    ):
                        total_wall_stop = True
                        missing_cost_keys.append(
                            {
                                "n": n,
                                "k": k,
                                "block_size": block_size,
                                "flip_rate": str(flip_rate),
                                "reason": "total_wall_budget",
                            }
                        )
                        continue
                    primary = classify_cost_interval(
                        certificate.lower_bound,
                        certificate.upper_bound,
                        comb(n, k),
                        flip_rate,
                        alpha,
                        target_power,
                        sample_cap,
                    )
                    primary_record = classification_record(primary)
                    probes = metric_robustness_probes(
                        primary,
                        comb(n, k),
                        flip_rate,
                        alpha,
                        target_power,
                        sample_cap,
                    )
                    cost_rows.append(
                        {
                            "n": n,
                            "k": k,
                            "block_size": block_size,
                            "flip_rate": str(flip_rate),
                            "primary": primary_record,
                            "metric_robustness_probes": list(probes),
                        }
                    )
                    atomic_json(
                        output_dir / "cost_checkpoint.json",
                        {
                            "schema_version": "asmp11_v0_2_1_2_cost_checkpoint",
                            "complete_cells": len(cost_rows),
                            "missing_cells": missing_cost_keys,
                        },
                    )

    brackets: list[dict[str, object]] = []
    grouped: dict[tuple[int, int, str], list[dict[str, object]]] = defaultdict(list)
    for row in cost_rows:
        grouped[(int(row["n"]), int(row["k"]), str(row["flip_rate"]))].append(
            {
                "block_size": row["block_size"],
                "status": row["primary"]["status"],  # type: ignore[index]
            }
        )
    for n in dimensions:
        for k in degrees:
            for flip_rate in flip_rates:
                key = (n, k, str(flip_rate))
                if len(grouped[key]) != len(intermediate_widths(n, k)):
                    continue
                anchor_row = anchors[(n, k)]
                bracket = build_minimum_width_bracket(
                    k, grouped[key], int(anchor_row["block_size"])
                )
                brackets.append(
                    {
                        "n": n,
                        "k": k,
                        "flip_rate": str(flip_rate),
                        "anchor_query_count": int(anchor_row["query_count"]),
                        **bracket,
                    }
                )

    grid_checks = exact_grid_counters(config, covering_rows, cost_rows, brackets)
    registered_counts_consistent = grid_axes_are_unique_and_canonical(
        config
    ) and expected == {
        "covering_cells": sum(expected_cover_counter(config).values()),
        "cost_cells": sum(expected_cost_counter(config).values()),
        "brackets": sum(expected_bracket_counter(config).values()),
        "metric_records_per_cost_cell": len(ALL_PROBE_IDS),
        "robustness_probes_per_cost_cell": len(ROBUSTNESS_PROBE_IDS),
    }
    elapsed_total = monotonic() - started
    resource_checks = resource_accounting(
        covering_rows, resource, elapsed_total, total_wall_stop
    )
    events_match_rows = len(operation_events) == len(covering_rows) and all(
        event
        == {
            "event": "covering_cell_complete",
            "n": row["n"],
            "k": row["k"],
            "block_size": row["block_size"],
            "construction_status": row["construction_status"],
            "stop_reason": row["stop_reason"],
            "elapsed_seconds": row["elapsed_seconds"],
        }
        for event, row in zip(operation_events, covering_rows)
    )
    resource_checks["events_match_covering_rows"] = events_match_rows
    resource_checks["measured_checks_pass"] = bool(
        resource_checks["measured_checks_pass"] and events_match_rows
    )
    binding_ok = all(row["pass"] for row in anchor_binding_checks) and all(
        row["pass"] for row in anchor_receipts
    )
    witness_ok = all(
        verify_cover(
            int(row["n"]),
            int(row["block_size"]),
            int(row["k"]),
            row["selected_blocks"],  # type: ignore[arg-type]
        )
        and len(row["selected_blocks"]) == int(row["upper_bound"])  # type: ignore[arg-type]
        for row in covering_rows
    )
    lower_ok = all(
        replayable_lower_bound(int(row["n"]), int(row["block_size"]), int(row["k"]))[
            "certified_lower_bound"
        ]
        == int(row["lower_bound"])
        and int(row["lower_bound"]) <= int(row["upper_bound"])
        for row in covering_rows
    )
    probability_ok = all(
        _design_is_exact(row["primary"]["baseline"], alpha, target_power)  # type: ignore[index,arg-type]
        and _design_is_exact(row["primary"]["best_certified"], alpha, target_power)  # type: ignore[index,arg-type]
        and _design_is_exact(row["primary"]["optimistic_floor"], alpha, target_power)  # type: ignore[index,arg-type]
        for row in cost_rows
    )
    total_classification = (
        registered_counts_consistent
        and grid_checks["covering"]
        and grid_checks["cost"]
        and not missing_cost_keys
        and all(
            row["primary"]["status"] in CLASSIFICATION_STATUSES for row in cost_rows
        )  # type: ignore[index]
    )
    bracket_ok = grid_checks["bracket"] and all(
        row["s_star"] is None
        or not row["unresolved_widths"]
        and all(
            status == "crossover_impossible_under_bounds"
            for width, status in row["status_by_width"].items()  # type: ignore[union-attr]
            if int(width) < int(row["s_star"])
        )
        for row in brackets
    )
    resource_honesty = (
        (
            resource_checks["measured_checks_pass"]
            and resource_checks["ram"]
            == {
                "measurement_status": "unmeasured",
                "peak_bytes": None,
                "registered_cap_bytes": int(resource["max_ram_bytes"]),
                "compliance": "not_established",
            }
        )
        and all(
            not bool(row["optimum_certified"])
            or int(row["lower_bound"]) == int(row["upper_bound"])
            for row in covering_rows
        )
        and all(
            row["stop_reason"] == "cover_complete"
            or verify_cover(
                int(row["n"]),
                int(row["block_size"]),
                int(row["k"]),
                row["selected_blocks"],  # type: ignore[arg-type]
            )
            for row in covering_rows
        )
    )
    probes_complete = (
        int(expected["metric_records_per_cost_cell"]) == len(ALL_PROBE_IDS)
        and int(expected["robustness_probes_per_cost_cell"])
        == len(ROBUSTNESS_PROBE_IDS)
        and probe_pack_is_well_formed(
            cost_rows, int(expected["metric_records_per_cost_cell"])
        )
    )
    gates = {
        "B0_binding": binding_ok,
        "B1_witness_validity": witness_ok,
        "B2_lower_bound_replay": lower_ok,
        "B3_probability_exactness": probability_ok,
        "B4_total_classification": total_classification,
        "B5_minimum_width": bracket_ok,
        "B6_resource_honesty_ram_unmeasured": resource_honesty,
        "B7_metric_probe_completeness": probes_complete,
    }
    core_valid = all(gates.values())
    status_counts = Counter(row["primary"]["status"] for row in cost_rows)  # type: ignore[index]
    probe_summary = summarize_probe_records(cost_rows)

    result_layer = {
        "schema_version": RESULT_SCHEMA,
        "release_id": RELEASE_ID,
        "experimental_unit": "one deterministic (n,k,s) covering cell",
        "counts": {
            "covering_cells": len(covering_rows),
            "cost_cells": len(cost_rows),
            "brackets": len(brackets),
            "status": dict(sorted(status_counts.items())),
        },
        "exact_grid_counters": grid_checks,
        "brackets": brackets,
        "raw_artifacts": {
            "covering_cells": "covering_cells.jsonl",
            "cost_cells": "cost_cells.jsonl",
        },
    }
    reliability_layer = {
        "schema_version": RELIABILITY_SCHEMA,
        "release_id": RELEASE_ID,
        "binding_gates": gates,
        "metric_firewall": {
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
        },
        "metric_robustness": probe_summary,
        "anchor_replay": anchor_receipts,
        "independent_verification": "pending separate verify_result.py execution",
    }
    claim_layer = {
        "schema_version": CLAIM_SCHEMA,
        "release_id": RELEASE_ID,
        "verdict": "claim_ready_for_independent_verification"
        if core_valid
        else "not_established",
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
    operation_layer = {
        "schema_version": OPERATION_SCHEMA,
        "release_id": RELEASE_ID,
        "run_status": "complete" if core_valid else "partial_or_invalid",
        "started_utc": started_utc,
        "finished_utc": utc_now(),
        "elapsed_seconds": elapsed_total,
        "total_wall_stop": total_wall_stop,
        "missing_cost_cells": missing_cost_keys,
        "resource_policy": resource,
        "resource_compliance": resource_checks,
        "stop_reason_counts": dict(
            sorted(Counter(row["stop_reason"] for row in covering_rows).items())
        ),
        "registration": {
            "path": str(registration_path),
            "sha256": sha256(registration_path),
            "source_commit": registration.get("source_commit"),
            "registration_commit": _registration_commit(
                registration_path, str(registration["source_commit"])
            ),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "git_head": _full_commit("HEAD"),
        },
        "events": operation_events,
    }

    write_jsonl(output_dir / "covering_cells.jsonl", covering_rows)
    write_jsonl(output_dir / "cost_cells.jsonl", cost_rows)
    atomic_json(output_dir / "result_layer.json", result_layer)
    atomic_json(output_dir / "reliability_layer.json", reliability_layer)
    atomic_json(output_dir / "claim_layer.json", claim_layer)
    atomic_json(output_dir / "operation_layer.json", operation_layer)
    outputs = {
        path.name: sha256(path)
        for path in sorted(output_dir.iterdir())
        if path.is_file() and path.name != "receipt.json"
    }
    if set(outputs) != PRIMARY_OUTPUTS:
        raise RuntimeError(
            f"primary output set mismatch: expected={sorted(PRIMARY_OUTPUTS)}, "
            f"observed={sorted(outputs)}"
        )
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "release_id": RELEASE_ID,
        "registration_sha256": sha256(registration_path),
        "manifest_sha256": sha256(manifest_path),
        "prior_anchor_sha256": sha256(anchor_path),
        "outputs": outputs,
        "verdict": claim_layer["verdict"],
    }
    if set(receipt) != RECEIPT_KEYS:
        raise AssertionError("primary receipt field set drifted")
    atomic_json(output_dir / "receipt.json", receipt)
    return result_layer, reliability_layer, claim_layer, operation_layer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--prior-anchor", type=Path, default=DEFAULT_ANCHOR)
    args = parser.parse_args()
    _, reliability, claim, operation = execute(
        args.registration.resolve(),
        args.output_dir.resolve(),
        args.manifest.resolve(),
        args.prior_anchor.resolve(),
    )
    print(
        canonical_json(
            {
                "verdict": claim["verdict"],
                "gates": reliability["binding_gates"],
                "run_status": operation["run_status"],
                "output_dir": str(args.output_dir.resolve()),
            }
        ),
        end="",
    )
    return 0 if all(reliability["binding_gates"].values()) else 2  # type: ignore[union-attr]


if __name__ == "__main__":
    raise SystemExit(main())
