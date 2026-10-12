"""Import-independent verifier for ASMP-7 adaptive suppression v0.4."""

from __future__ import annotations

import sys as _sys


if __name__ == "__main__" and not (
    _sys.flags.isolated and getattr(_sys.flags, "safe_path", False)
):
    raise SystemExit(
        "refusing unsafe launch before imports; invoke with `python -I verify_independent.py ...`"
    )
if __name__ == "__main__":
    _sys.dont_write_bytecode = True


import argparse
import hashlib
import itertools
import json
import math
import os
import re
import shutil
import stat
import subprocess
import time
import tracemalloc
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any


HERE = Path(os.path.abspath(__file__)).parent
ARTIFACT_DIRECTORY = HERE.parent / "artifacts_v0_4_adaptive_suppression"
FROZEN_PROTOCOL_ID = "ASMP7-CAUSAL-ADAPTIVE-SUPPRESSION-v0.4"
FROZEN_MANIFEST_SCHEMA = "asmp7_adaptive_suppression_manifest_v0_4"
FROZEN_MANIFEST_CANONICAL_SHA256 = (
    "c3c9430257645e5709ce3c838c124e021ad293d750d7bd1afb75c0eaaed4a1d3"
)
FROZEN_SOURCE_FILES = (
    "PROTOCOL_v0_4.md",
    "README.md",
    "SOURCE_FREEZE.md",
    "adaptive_suppression.py",
    "manifest_v0_4.json",
    "run.py",
    "test_adaptive_suppression.py",
    "verify_independent.py",
)
FROZEN_RESULT_FIELDS = {
    "schema_version",
    "protocol_id",
    "manifest_sha256",
    "source_binding",
    "upstream_bindings",
    "resource_observations",
    "status",
    "stop_reason",
    "quotient_rows",
    "registry_rows",
    "oracle_rows",
    "analytic_obligations",
    "controls",
    "gates",
    "metric_robustness",
    "conclusion_layers",
    "claim_boundary",
}
FROZEN_PRIMARY_GATES = (
    "G0_frozen_manifest_binding",
    "G1_exact_source_and_upstream_bindings",
    "G2_complete_72_pair_mask_quotient",
    "G3_complete_48_row_v03_transfer",
    "G4_complete_144_row_monotone_oracle",
    "G5_analytic_induction_and_composite_obligations",
    "G6_scope_breakers_and_simple_limits",
    "G7_five_metric_probe_families",
    "G8_exact_arithmetic_and_resource_envelope",
)
FROZEN_PROBE_IDS = (
    "P1_input_relabeling",
    "P2_timing_sensitivity",
    "P3_terminal_monotonicity",
    "P4_nonmonotone_scope_breaker",
    "P5_upstream_and_simple_limits",
)
FROZEN_PREVERIFICATION_LAYERS = {
    "metric_robustness": "five_frozen_probe_families_computed_awaiting_independent_replay",
    "task_result": "finite_causal_endpoint_equivalence_and_v03_minimum_transfer",
    "measurement_reliability": "awaiting_import_independent_verification",
    "claim_support": "pending_independent_verification",
    "operational_decision": "no_deployment_authorization_await_independent_verification",
}
FROZEN_FINAL_LAYERS = {
    "metric_robustness": "five_frozen_probe_families_independently_replayed",
    "task_result": "finite_causal_endpoint_equivalence_and_v03_minimum_transfer",
    "measurement_reliability": "independent_combinatorial_historical_oracle_and_source_replay_passed",
    "claim_support": "finite_registered_causal_adaptation_equivalence_supported",
    "operational_decision": "no_deployment_authorization",
}
FROZEN_CLAIM_BOUNDARY = (
    "fixed 16-point Boolean execution known completely to the suppressor",
    "iid uniform current challenge sampled only after the exact-c mask is frozen and conditionally independent of the frozen filtration",
    "causal private-randomized mask policies measurable with respect to past X, Y, S and private coins",
    "fresh randomized-response and fallback coins and post-transcript auditor randomization are hidden from the suppressor",
    "monitor receives only the report-bit history Y; registered sample minima use the count K",
    "arbitrary rational coordinatewise-monotone terminal functions are covered; the NP minimum-transfer corollary is for registered count upper-tail tests",
    "deterministic finite horizons m from 0 through 8192 only",
    "no current-X-aware mask, nonmonotone audit theorem, random stopping time, infinite horizon, stateful execution, nonuniform or dependent challenge, mask leakage, real meter, deployment, transformation-universal attestability, or ASMP-7 resolution claim",
)
FROZEN_K_VALUES = (0, 1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 16)
FROZEN_K1_VALUES = (14, 16)
FROZEN_THETAS = (Fraction(1, 2), Fraction(3, 4), Fraction(4, 5), Fraction(1))
FROZEN_C_VALUES = (0, 8, 10, 12, 14, 16)
FROZEN_THRESHOLDS = (0, 1, 2, 3)
FROZEN_GAMMAS = (Fraction(), Fraction(1, 2), Fraction(1))
FROZEN_OBJECTIVES = ("max", "min")
FROZEN_VERIFICATION_FIELDS = {
    "schema_version",
    "pass",
    "protocol_id",
    "manifest_binding",
    "source_binding_error",
    "source_binding_replay",
    "upstream_binding_checks",
    "result_semantic_checks",
    "quotient_mismatches",
    "registry_mismatches",
    "oracle_mismatches",
    "analytic_obligations",
    "control_mismatches",
    "metric_probe_ids",
    "metric_probes_match",
    "resource_observations_valid",
    "verification_resource_observations",
    "primary_gates_valid",
    "preverification_layers_match",
    "independent_gates",
    "final_conclusion_layers",
    "claim_boundary",
    "bindings",
    "implementation_imported",
}
FROZEN_VERIFICATION_GATES = (
    "V0_frozen_manifest_binding",
    "V1_exact_live_and_source_commit_binding",
    "V2_exact_historical_upstream_bytes",
    "V3_result_identity_and_canonical_json",
    "V4_complete_72_pair_combinatorial_quotient",
    "V5_complete_48_row_v03_and_minimum_transfer",
    "V6_complete_144_row_independent_oracle",
    "V7_induction_composite_and_scope_obligations",
    "V8_scope_breakers_and_simple_limits",
    "V9_five_metric_probe_families",
    "V10_primary_gates_and_preverification_layers",
    "V11_resource_observations_within_frozen_limits",
)
GIT_EXECUTABLE = shutil.which("git")


def require_isolated_safe_path() -> None:
    if not (_sys.flags.isolated and getattr(_sys.flags, "safe_path", False)):
        raise SystemExit(
            "refusing unsafe launch before imports; invoke with `python -I verify_independent.py ...`"
        )
    _sys.dont_write_bytecode = True


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def strict_json_equal(left: Any, right: Any) -> bool:
    try:
        return canonical_json(left) == canonical_json(right)
    except (TypeError, ValueError):
        return False


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def exact_fraction(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("inexact scalar")
    if isinstance(value, Fraction):
        return value
    if type(value) is int:
        return Fraction(value)
    if isinstance(value, str) and re.fullmatch(r"-?(0|[1-9][0-9]*)/[1-9][0-9]*", value):
        parsed = Fraction(value)
        if fraction_text(parsed) != value:
            raise ValueError("noncanonical fraction")
        return parsed
    raise TypeError("not an exact scalar")


def contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(key) or contains_float(item) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(contains_float(item) for item in value)
    return False


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def _reject_float(value: str) -> Any:
    raise ValueError(f"floating point forbidden: {value}")


def _reject_constant(value: str) -> Any:
    raise ValueError(f"nonfinite value forbidden: {value}")


def load_json_bytes_strict(payload: bytes) -> Any:
    return json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=_strict_object,
        parse_float=_reject_float,
        parse_constant=_reject_constant,
    )


def load_json_strict(path: Path) -> Any:
    return load_json_bytes_strict(path.read_bytes())


def manifest_binding_checks(manifest: dict[str, Any]) -> dict[str, bool]:
    registry = manifest.get("registry", {})
    return {
        "canonical_manifest_hash_is_frozen": canonical_sha256(manifest)
        == FROZEN_MANIFEST_CANONICAL_SHA256,
        "identity_is_frozen": manifest.get("protocol_id") == FROZEN_PROTOCOL_ID
        and manifest.get("schema") == "alife.experiment.v1"
        and manifest.get("schema_version") == FROZEN_MANIFEST_SCHEMA,
        "source_set_and_replay_are_frozen": tuple(
            manifest.get("source_freeze", {}).get("files", ())
        )
        == FROZEN_SOURCE_FILES
        and manifest.get("artifacts", {}).get("replay_command")
        == "python -I run.py --source-commit <40-hex-source-commit>",
        "registry_is_exact": tuple(registry.get("forbidden_boundaries", ()))
        == FROZEN_K1_VALUES
        and tuple(exact_fraction(value) for value in registry.get("theta_grid", ()))
        == FROZEN_THETAS
        and tuple(registry.get("coverage_counts", ())) == FROZEN_C_VALUES
        and tuple(registry.get("quotient_agreement_counts", ())) == FROZEN_K_VALUES
        and registry.get("parameter_triple_count") == 48
        and registry.get("quotient_pair_count") == 72
        and registry.get("oracle", {}).get("comparison_count") == 144
        and strict_json_equal(
            registry.get("generic_terminal_census"),
            {
                "agreement_counts": list(FROZEN_K_VALUES),
                "comparison_count": 11520,
                "coverage_counts": list(FROZEN_C_VALUES),
                "horizon": 3,
                "loop_order": [
                    "terminal_truth_table",
                    "agreement_count",
                    "coverage_count",
                    "theta",
                    "objective",
                ],
                "nonsymmetric_terminal_count": 15,
                "objectives": list(FROZEN_OBJECTIVES),
                "terminal_count": 20,
                "terminal_family": "all coordinatewise-monotone Boolean truth tables on lexicographically ordered {0,1}^3",
                "theta_grid": [fraction_text(value) for value in FROZEN_THETAS],
            },
        ),
        "filtration_is_causal_and_monitor_report_only": manifest.get(
            "semantics", {}
        ).get("challenge")
        == "conditional on the complete frozen filtration including S_t and all suppressor-private coins used through time t, X_t is uniform on {0,...,15} and independent of all earlier and future challenge/report/auditor coins"
        and manifest.get("semantics", {}).get("fresh_stream_product_law")
        == "challenge draws, randomized-response coins, uncovered fallback coins, auditor coins, and suppressor-private coins are mutually independent product streams; conditioning on the frozen past and S_t leaves the current challenge uniform and both current report coins fresh"
        and manifest.get("semantics", {}).get("monitor")
        == "the monitor receives only Y_1,...,Y_m; registered upper-tail decisions use K=sum_t Y_t",
        "resource_contract_is_exact": manifest.get("budget", {}).get("max_steps_per_episode")
        == 8192
        and manifest.get("budget", {}).get("max_wall_seconds") == 30
        and manifest.get("budget", {}).get("max_traced_python_mib") == 64
        and manifest.get("budget", {}).get("max_result_bytes") == 1048576
        and manifest.get("budget", {}).get("max_generic_terminal_comparisons")
        == 11520,
    }


def _git_environment() -> dict[str, str]:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    return environment


def _git(args: list[str], *, text: bool, cwd: Path | None = None) -> str | bytes:
    if GIT_EXECUTABLE is None:
        raise RuntimeError("Git executable is unavailable")
    completed = subprocess.run(
        [GIT_EXECUTABLE, *args],
        cwd=cwd or HERE,
        env=_git_environment(),
        check=True,
        capture_output=True,
        text=text,
    )
    return completed.stdout.strip() if text else completed.stdout


def repo_root() -> Path:
    return Path(
        os.path.abspath(str(_git(["rev-parse", "--show-toplevel"], text=True)))
    )


def validate_git_view(root: Path) -> None:
    git_directory = Path(
        os.path.abspath(
            str(_git(["rev-parse", "--absolute-git-dir"], text=True, cwd=root))
        )
    )
    grafts = git_directory / "info" / "grafts"
    if grafts.exists() and grafts.stat().st_size:
        raise ValueError("legacy Git grafts are forbidden")
    if str(
        _git(
            ["for-each-ref", "--format=%(refname)", "refs/replace"],
            text=True,
            cwd=root,
        )
    ):
        raise ValueError("Git replacement refs are forbidden")
    if str(
        _git(["rev-parse", "--is-shallow-repository"], text=True, cwd=root)
    ) != "false":
        raise ValueError("shallow repository is forbidden")


def committed_bytes(commit: str, path: str) -> bytes:
    return bytes(_git(["show", f"{commit}:{path}"], text=False, cwd=repo_root()))


def replay_upstream_bindings(manifest: dict[str, Any]) -> dict[str, Any]:
    root = repo_root()
    validate_git_view(root)
    output: dict[str, Any] = {}
    for version in ("v0_1", "v0_3"):
        group = manifest["upstream_bindings"][version]
        default_commit = group["evidence_commit"]
        commits = {default_commit}
        for optional in ("source_commit", "registration_commit"):
            if optional in group:
                commits.add(group[optional])
        files = []
        for item in group["files"]:
            commit = item.get("commit", default_commit)
            commits.add(commit)
            payload = bytes(
                _git(["show", f"{commit}:{item['path']}"], text=False, cwd=root)
            )
            digest = sha256_bytes(payload)
            if digest != item["sha256"]:
                raise ValueError(f"upstream hash mismatch: {item['path']}")
            files.append(
                {
                    "commit": commit,
                    "path": item["path"],
                    "role": item["role"],
                    "sha256": digest,
                }
            )
        for commit in commits:
            if not re.fullmatch(r"[0-9a-f]{40}", commit):
                raise ValueError("upstream commit is not full hex")
            if str(_git(["cat-file", "-t", commit], text=True, cwd=root)) != "commit":
                raise ValueError("upstream object is not a commit")
            if subprocess.run(
                [GIT_EXECUTABLE, "merge-base", "--is-ancestor", commit, "HEAD"],
                cwd=root,
                env=_git_environment(),
            ).returncode != 0:
                raise ValueError("upstream commit is not an ancestor")
        output[version] = {
            "commits": sorted(commits),
            "files": files,
            "all_hashes_match": True,
        }
    return output


def upstream_v03_result(manifest: dict[str, Any]) -> dict[str, Any]:
    group = manifest["upstream_bindings"]["v0_3"]
    rows = [
        item
        for item in group["files"]
        if item["role"] == "artifact" and item["path"].endswith("/result.json")
    ]
    if len(rows) != 1:
        raise ValueError("v0.3 result binding is not unique")
    candidate = rows[0]
    payload = committed_bytes(
        candidate.get("commit", group["evidence_commit"]), candidate["path"]
    )
    if sha256_bytes(payload) != candidate["sha256"]:
        raise ValueError("v0.3 result changed after upstream validation")
    value = load_json_bytes_strict(payload)
    if not isinstance(value, dict):
        raise TypeError("v0.3 result is not an object")
    return value


def action_interval(k: int, c: int) -> tuple[int, int]:
    return max(0, k + c - 16), min(k, c)


def report_probability(theta: Fraction, c: int, a: int) -> Fraction:
    return Fraction(1, 2) + (2 * theta - 1) * Fraction(2 * a - c, 32)


def upper_tail(prefix: tuple[int, ...], threshold: int, gamma: Fraction) -> Fraction:
    count = sum(prefix)
    return Fraction(1) if count > threshold else gamma if count == threshold else Fraction()


def independent_policy_value(
    horizon: int,
    k: int,
    c: int,
    theta: Fraction,
    threshold: int,
    gamma: Fraction,
    objective: str,
) -> Fraction:
    lower, upper = action_interval(k, c)
    actions = tuple(range(lower, upper + 1))
    choose = max if objective == "max" else min

    @lru_cache(maxsize=None)
    def visit(prefix: tuple[int, ...]) -> Fraction:
        if len(prefix) == horizon:
            return upper_tail(prefix, threshold, gamma)
        candidates = []
        for action in actions:
            q = report_probability(theta, c, action)
            candidates.append(
                (1 - q) * visit(prefix + (0,)) + q * visit(prefix + (1,))
            )
        return choose(candidates)

    return visit(())


def iid_value(horizon: int, q: Fraction, threshold: int, gamma: Fraction) -> Fraction:
    return sum(
        (
            Fraction(math.comb(horizon, count))
            * q**count
            * (1 - q) ** (horizon - count)
            * (Fraction(1) if count > threshold else gamma if count == threshold else Fraction())
        )
        for count in range(horizon + 1)
    )


def antichain_monotone_boolean_terminals(
    horizon: int,
) -> tuple[tuple[int, ...], ...]:
    histories = tuple(itertools.product((0, 1), repeat=horizon))
    terminals: set[tuple[int, ...]] = set()
    for selected_bits in itertools.product((0, 1), repeat=len(histories)):
        minimal_points = tuple(
            history
            for history, selected in zip(histories, selected_bits)
            if selected
        )
        is_antichain = all(
            not all(x <= y for x, y in zip(left, right))
            and not all(y <= x for x, y in zip(left, right))
            for index, left in enumerate(minimal_points)
            for right in minimal_points[index + 1 :]
        )
        if not is_antichain:
            continue
        terminals.add(
            tuple(
                int(
                    any(
                        all(x <= y for x, y in zip(minimal, history))
                        for minimal in minimal_points
                    )
                )
                for history in histories
            )
        )
    return tuple(sorted(terminals))


def iterative_generic_policy_value(
    terminal_values: tuple[int, ...],
    horizon: int,
    agreement_count: int,
    coverage_count: int,
    theta: Fraction,
    objective: str,
) -> Fraction:
    terminal_histories = tuple(itertools.product((0, 1), repeat=horizon))
    if len(terminal_values) != len(terminal_histories):
        raise ValueError("terminal table has the wrong horizon")
    values = {
        history: Fraction(value)
        for history, value in zip(terminal_histories, terminal_values)
    }
    lower, upper = action_interval(agreement_count, coverage_count)
    actions = tuple(range(lower, upper + 1))
    chooser = max if objective == "max" else min
    for depth in range(horizon - 1, -1, -1):
        previous = {}
        for prefix in itertools.product((0, 1), repeat=depth):
            candidates = []
            for action in actions:
                q = report_probability(theta, coverage_count, action)
                candidates.append(
                    (1 - q) * values[prefix + (0,)]
                    + q * values[prefix + (1,)]
                )
            previous[prefix] = chooser(candidates)
        values = previous
    return values[()]


def independent_iid_terminal_value(
    terminal_values: tuple[int, ...], horizon: int, q: Fraction
) -> Fraction:
    histories = tuple(itertools.product((0, 1), repeat=horizon))
    return sum(
        (
            Fraction(value)
            * q ** sum(history)
            * (1 - q) ** (horizon - sum(history))
        )
        for history, value in zip(histories, terminal_values)
    )


def independent_generic_h3_terminal_census() -> dict[str, Any]:
    horizon = 3
    histories = tuple(itertools.product((0, 1), repeat=horizon))
    terminals = antichain_monotone_boolean_terminals(horizon)
    nonsymmetric = sum(
        any(
            len(
                {
                    values[index]
                    for index, history in enumerate(histories)
                    if sum(history) == count
                }
            )
            > 1
            for count in range(horizon + 1)
        )
        for values in terminals
    )
    comparisons = 0
    all_equal = True
    for values in terminals:
        for agreement_count in FROZEN_K_VALUES:
            for coverage_count in FROZEN_C_VALUES:
                for theta in FROZEN_THETAS:
                    lower, upper = action_interval(agreement_count, coverage_count)
                    for objective in FROZEN_OBJECTIVES:
                        endpoint = upper if objective == "max" else lower
                        q = report_probability(theta, coverage_count, endpoint)
                        adaptive = iterative_generic_policy_value(
                            values,
                            horizon,
                            agreement_count,
                            coverage_count,
                            theta,
                            objective,
                        )
                        endpoint_value = independent_iid_terminal_value(
                            values, horizon, q
                        )
                        comparisons += 1
                        all_equal = all_equal and adaptive == endpoint_value
    return {
        "horizon": horizon,
        "monotone_boolean_terminal_count": len(terminals),
        "nonsymmetric_terminal_count": nonsymmetric,
        "registered_action_law_comparisons": comparisons,
        "all_values_equal": all_equal,
    }


def _is_reparse_point(path: Path) -> bool:
    metadata = path.lstat()
    attributes = getattr(metadata, "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return path.is_symlink() or bool(attributes & flag)


def live_source_inventory_checks(directory: Path = HERE) -> dict[str, Any]:
    expected = set(FROZEN_SOURCE_FILES)
    try:
        entries = {entry.name: entry for entry in directory.iterdir()}
        directory_reparse = _is_reparse_point(directory)
    except OSError as error:
        return {
            "pass": False,
            "directory_error": type(error).__name__,
            "directory_reparse": True,
            "missing": sorted(expected),
            "unexpected": [],
            "invalid_source_entries": [],
        }
    missing = sorted(expected - set(entries))
    unexpected = sorted(set(entries) - expected)
    invalid = []
    for name in sorted(expected & set(entries)):
        try:
            if _is_reparse_point(entries[name]) or not entries[name].is_file():
                invalid.append(name)
        except OSError:
            invalid.append(name)
    return {
        "pass": not (directory_reparse or missing or unexpected or invalid),
        "directory_error": "",
        "directory_reparse": directory_reparse,
        "missing": missing,
        "unexpected": unexpected,
        "invalid_source_entries": invalid,
    }


def validate_live_source_inventory() -> dict[str, Any]:
    checks = live_source_inventory_checks()
    if not checks["pass"]:
        raise ValueError(f"live source inventory failed: {checks}")
    return checks


def replay_source_binding(source_commit: str) -> dict[str, Any]:
    validate_live_source_inventory()
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("source commit must be full lowercase hex")
    root = repo_root()
    validate_git_view(root)
    cursor = HERE
    while True:
        if _is_reparse_point(cursor):
            raise ValueError(f"source ancestry contains reparse point: {cursor}")
        if cursor == root:
            break
        if cursor.parent == cursor or root not in cursor.parents:
            raise ValueError("source directory is outside the repository root")
        cursor = cursor.parent
    if str(_git(["cat-file", "-t", source_commit], text=True, cwd=root)) != "commit":
        raise ValueError("source object is not a commit")
    resolved = str(
        _git(["rev-parse", "--verify", f"{source_commit}^{{commit}}"], text=True, cwd=root)
    )
    if resolved != source_commit:
        raise ValueError("source commit did not resolve exactly")
    if subprocess.run(
        [
            GIT_EXECUTABLE,
            "merge-base",
            "--is-ancestor",
            source_commit,
            "HEAD",
        ],
        cwd=root,
        env=_git_environment(),
    ).returncode != 0:
        raise ValueError("source commit is not an ancestor")
    relative = HERE.relative_to(root)
    directory_path = relative.as_posix()
    listed = str(
        _git(
            ["ls-tree", "-r", "--name-only", source_commit, "--", directory_path],
            text=True,
            cwd=root,
        )
    )
    expected_paths = {(relative / name).as_posix() for name in FROZEN_SOURCE_FILES}
    if {line for line in listed.splitlines() if line} != expected_paths:
        raise ValueError("source tree does not contain the exact eight files")
    hashes = {}
    for name in FROZEN_SOURCE_FILES:
        relative_path = (relative / name).as_posix()
        tree_line = str(
            _git(["ls-tree", source_commit, "--", relative_path], text=True, cwd=root)
        )
        metadata, listed_path = tree_line.split("\t", 1)
        mode, kind, blob_oid = metadata.split()
        if listed_path != relative_path or mode != "100644" or kind != "blob":
            raise ValueError(f"source tree entry is not a regular blob: {name}")
        committed = bytes(
            _git(
                ["show", f"{source_commit}:{relative_path}"],
                text=False,
                cwd=root,
            )
        )
        current = (HERE / name).read_bytes()
        current_oid = subprocess.run(
            [GIT_EXECUTABLE, "hash-object", "--stdin"],
            cwd=root,
            env=_git_environment(),
            check=True,
            input=current,
            capture_output=True,
        ).stdout.decode("ascii").strip()
        if current != committed or current_oid != blob_oid:
            raise ValueError(f"working source differs from commit: {name}")
        hashes[name] = {
            "git_blob_oid": current_oid,
            "sha256": sha256_bytes(current),
        }
    return {
        "repo_relative_directory": directory_path,
        "source_commit": source_commit,
        "source_commit_is_ancestor_of_head": True,
        "source_commit_type": "commit",
        "source_files": hashes,
    }


def expected_quotient_row(k: int, c: int) -> dict[str, Any]:
    lower, upper = action_interval(k, c)
    values = list(range(lower, upper + 1))
    multiplicities = [
        {"a": action, "count": math.comb(k, action) * math.comb(16 - k, c - action)}
        for action in values
    ]
    total = sum(item["count"] for item in multiplicities)
    return {
        "agreement_count": k,
        "coverage_count": c,
        "action_interval": [lower, upper],
        "attainable_a": values,
        "multiplicities": multiplicities,
        "total_masks": total,
        "canonical_attained_set": values,
        "relabeled_attained_set": values,
        "relabel_permutation": [(5 * point + 3) % 16 for point in range(16)],
        "checks": {
            "complete_interval": True,
            "multiplicity_total": total == math.comb(16, c),
            "relabel_invariant": True,
        },
    }


def quotient_mismatches(reported: Any) -> list[dict[str, Any]]:
    expected = [expected_quotient_row(k, c) for k in FROZEN_K_VALUES for c in FROZEN_C_VALUES]
    if not isinstance(reported, list) or len(reported) != len(expected):
        return [{"field": "row_count", "expected": 72, "reported": len(reported) if isinstance(reported, list) else "not_list"}]
    return [
        {
            "row": index,
            "expected_sha256": canonical_sha256(expected_row),
            "reported_sha256": canonical_sha256(reported_row),
        }
        for index, (expected_row, reported_row) in enumerate(zip(expected, reported))
        if not strict_json_equal(expected_row, reported_row)
    ]


def _selective_map(result: dict[str, Any]) -> dict[tuple[int, Fraction, int], dict[str, Any]]:
    output = {}
    for record in result.get("records", []):
        if record.get("model") != "adversarial_selective":
            continue
        key = (record["k1"], exact_fraction(record["theta"]), record["coverage_count"])
        if key in output:
            raise ValueError("duplicate upstream selective row")
        output[key] = record
    if len(output) != 48:
        raise ValueError("upstream selective registry is not 48 rows")
    return output


def _upstream_record_semantics(record: dict[str, Any], q0: Fraction, q1: Fraction) -> bool:
    if exact_fraction(record.get("q0_worst")) != q0 or exact_fraction(record.get("q1_worst")) != q1:
        return False
    if exact_fraction(record.get("effective_delta")) != max(Fraction(), q1 - q0):
        return False
    status = record.get("status")
    if status == "feasible_exact":
        test = record.get("test", {})
        predecessor = record.get("predecessor", {})
        try:
            test_errors = randomized_upper_tail_errors(
                test.get("m"),
                q0,
                q1,
                test.get("cutoff"),
                exact_fraction(test.get("gamma")),
            )
            predecessor_errors = randomized_upper_tail_errors(
                predecessor.get("m"),
                q0,
                q1,
                predecessor.get("cutoff"),
                exact_fraction(predecessor.get("gamma")),
            )
        except (TypeError, ValueError, ZeroDivisionError):
            return False
        return bool(
            record.get("m_star") == test.get("m")
            and predecessor.get("m") == test.get("m") - 1
            and exact_fraction(test.get("fp")) == Fraction(1, 20)
            and exact_fraction(test.get("fn")) <= Fraction(1, 20)
            and exact_fraction(predecessor.get("fp")) == Fraction(1, 20)
            and exact_fraction(predecessor.get("fn")) > Fraction(1, 20)
            and test_errors
            == (exact_fraction(test.get("fp")), exact_fraction(test.get("fn")))
            and predecessor_errors
            == (
                exact_fraction(predecessor.get("fp")),
                exact_fraction(predecessor.get("fn")),
            )
            and record.get("common_law_witness") is None
        )
    if status != "common_law_impossible":
        return False
    witness = record.get("common_law_witness", {})
    theta = exact_fraction(record["theta"])
    c = record["coverage_count"]
    compliant = action_interval(8, c)
    forbidden = action_interval(record["k1"], c)
    if theta == Fraction(1, 2):
        witness_ok = witness.get("kind") == "identical_bernoulli_law" and exact_fraction(witness.get("q")) == Fraction(1, 2)
    else:
        action = witness.get("covered_agreements")
        witness_ok = bool(
            witness.get("kind") == "selective_mask_common_law"
            and witness.get("compliant_range") == list(compliant)
            and witness.get("forbidden_range") == list(forbidden)
            and type(action) is int
            and max(compliant[0], forbidden[0]) <= action <= min(compliant[1], forbidden[1])
            and exact_fraction(witness.get("q")) == report_probability(theta, c, action)
        )
    return bool(
        witness_ok
        and record.get("m_star") is None
        and exact_fraction(record.get("sum_error_lower_bound")) == 1
    )


def randomized_upper_tail_errors(
    horizon: Any,
    q0: Fraction,
    q1: Fraction,
    cutoff: Any,
    gamma: Fraction,
) -> tuple[Fraction, Fraction]:
    if type(horizon) is not int or type(cutoff) is not int:
        raise TypeError("horizon and cutoff must be exact integers")
    if not 0 <= cutoff <= horizon or not 0 <= gamma <= 1:
        raise ValueError("randomized upper-tail parameters are out of range")

    def masses(q: Fraction) -> list[Fraction]:
        return [
            Fraction(math.comb(horizon, count))
            * q**count
            * (1 - q) ** (horizon - count)
            for count in range(horizon + 1)
        ]

    null_mass = masses(q0)
    forbidden_mass = masses(q1)
    false_positive = (
        sum(null_mass[cutoff + 1 :], Fraction()) + gamma * null_mass[cutoff]
    )
    false_negative = (
        sum(forbidden_mass[:cutoff], Fraction())
        + (1 - gamma) * forbidden_mass[cutoff]
    )
    return false_positive, false_negative


def expected_transfer_checks(
    record: dict[str, Any], q0: Fraction, q1: Fraction, coverage_count: int
) -> dict[str, bool]:
    status = record.get("status")
    checks = {
        "model_is_selective": record.get("model") == "adversarial_selective",
        "coverage_is_exact": exact_fraction(record.get("coverage"))
        == Fraction(coverage_count, 16),
        "q0_endpoint_matches": exact_fraction(record.get("q0_worst")) == q0,
        "q1_endpoint_matches": exact_fraction(record.get("q1_worst")) == q1,
        "delta_matches": exact_fraction(record.get("effective_delta"))
        == max(Fraction(), q1 - q0),
        "status_is_registered": status
        in {"feasible_exact", "common_law_impossible"},
    }
    if status == "feasible_exact":
        test = record.get("test")
        predecessor = record.get("predecessor")
        checks.update(
            {
                "test_and_predecessor_present": isinstance(test, dict)
                and isinstance(predecessor, dict),
                "minimum_matches_test": isinstance(test, dict)
                and record.get("m_star") == test.get("m"),
                "predecessor_is_immediate": isinstance(test, dict)
                and isinstance(predecessor, dict)
                and predecessor.get("m") == test.get("m") - 1,
                "test_controls_both_errors": isinstance(test, dict)
                and exact_fraction(test.get("fp")) == Fraction(1, 20)
                and exact_fraction(test.get("fn")) <= Fraction(1, 20),
                "predecessor_is_infeasible": isinstance(predecessor, dict)
                and exact_fraction(predecessor.get("fp")) == Fraction(1, 20)
                and exact_fraction(predecessor.get("fn")) > Fraction(1, 20),
                "no_common_law_witness": record.get("common_law_witness") is None,
            }
        )
    elif status == "common_law_impossible":
        witness = record.get("common_law_witness")
        theta = exact_fraction(record.get("theta"))
        compliant_range = action_interval(8, coverage_count)
        forbidden_range = action_interval(record.get("k1"), coverage_count)
        shared_lower = max(compliant_range[0], forbidden_range[0])
        shared_upper = min(compliant_range[1], forbidden_range[1])
        privacy_kill = theta == Fraction(1, 2)
        overlap = shared_lower <= shared_upper
        if privacy_kill:
            witness_valid = bool(
                isinstance(witness, dict)
                and witness.get("kind") == "identical_bernoulli_law"
                and exact_fraction(witness.get("q")) == Fraction(1, 2)
            )
        else:
            shared_action = (
                witness.get("covered_agreements")
                if isinstance(witness, dict)
                else None
            )
            witness_valid = bool(
                overlap
                and isinstance(witness, dict)
                and witness.get("kind") == "selective_mask_common_law"
                and witness.get("compliant_range") == list(compliant_range)
                and witness.get("forbidden_range") == list(forbidden_range)
                and type(shared_action) is int
                and shared_lower <= shared_action <= shared_upper
                and exact_fraction(witness.get("q"))
                == report_probability(theta, coverage_count, shared_action)
            )
        checks.update(
            {
                "privacy_kill_or_action_overlap": privacy_kill or overlap,
                "no_finite_minimum": record.get("m_star") is None,
                "sum_error_lower_bound_is_one": exact_fraction(
                    record.get("sum_error_lower_bound")
                )
                == 1,
                "common_law_witness_matches": witness_valid,
            }
        )
    return checks


def expected_registry_row(
    bound: dict[str, Any], k1: int, theta: Fraction, coverage_count: int
) -> dict[str, Any]:
    compliant = action_interval(8, coverage_count)
    forbidden = action_interval(k1, coverage_count)
    q0 = report_probability(theta, coverage_count, compliant[1])
    q1 = report_probability(theta, coverage_count, forbidden[0])
    transfer_checks = expected_transfer_checks(bound, q0, q1, coverage_count)
    return {
        "k1": k1,
        "theta": fraction_text(theta),
        "coverage_count": coverage_count,
        "compliant_interval": list(compliant),
        "forbidden_interval": list(forbidden),
        "q0_max": fraction_text(q0),
        "q1_min": fraction_text(q1),
        "upstream_record": bound,
        "transfer_checks": transfer_checks,
        "all_checks_pass": all(transfer_checks.values()),
    }


def registry_row_matches_bound(
    reported: Any,
    bound: dict[str, Any],
    k1: int,
    theta: Fraction,
    coverage_count: int,
) -> bool:
    expected = expected_registry_row(bound, k1, theta, coverage_count)
    checks = expected["transfer_checks"]
    q0 = exact_fraction(expected["q0_max"])
    q1 = exact_fraction(expected["q1_min"])
    return bool(
        strict_json_equal(reported, expected)
        and all(value is True for value in checks.values())
        and _upstream_record_semantics(bound, q0, q1)
    )


def registry_mismatches(manifest: dict[str, Any], reported: Any) -> list[dict[str, Any]]:
    if not isinstance(reported, list) or len(reported) != 48:
        return [{"field": "row_count", "expected": 48, "reported": len(reported) if isinstance(reported, list) else "not_list"}]
    upstream = _selective_map(upstream_v03_result(manifest))
    mismatches = []
    index = 0
    for k1 in FROZEN_K1_VALUES:
        for theta in FROZEN_THETAS:
            for c in FROZEN_C_VALUES:
                row = reported[index]
                index += 1
                bound = upstream[(k1, theta, c)]
                valid = registry_row_matches_bound(row, bound, k1, theta, c)
                if not valid:
                    mismatches.append({"row": index - 1, "key": [k1, fraction_text(theta), c]})
    return mismatches


def oracle_mismatches(manifest: dict[str, Any], reported: Any) -> list[dict[str, Any]]:
    if not isinstance(reported, list) or len(reported) != 144:
        return [{"field": "row_count", "expected": 144, "reported": len(reported) if isinstance(reported, list) else "not_list"}]
    mismatches = []
    index = 0
    for witness in manifest["registry"]["oracle"]["witnesses"]:
        theta = exact_fraction(witness["theta"])
        c = witness["coverage_count"]
        for threshold in FROZEN_THRESHOLDS:
            for gamma in FROZEN_GAMMAS:
                for objective in FROZEN_OBJECTIVES:
                    row = reported[index]
                    index += 1
                    k = 8 if objective == "max" else witness["k1"]
                    lower, upper = action_interval(k, c)
                    endpoint = upper if objective == "max" else lower
                    q = report_probability(theta, c, endpoint)
                    policy = independent_policy_value(3, k, c, theta, threshold, gamma, objective)
                    iid = iid_value(3, q, threshold, gamma)
                    expected = {
                        "witness_id": witness["id"],
                        "threshold": threshold,
                        "gamma": fraction_text(gamma),
                        "objective": objective,
                        "effective_agreement_count": k,
                        "coverage_count": c,
                        "theta": fraction_text(theta),
                        "action_interval": [lower, upper],
                        "endpoint_action": endpoint,
                        "endpoint_q": fraction_text(q),
                        "full_prefix_bellman": fraction_text(policy),
                        "count_state_bellman": fraction_text(policy),
                        "constant_iid_endpoint": fraction_text(iid),
                        "all_values_equal": policy == iid,
                    }
                    if not strict_json_equal(row, expected) or policy != iid:
                        mismatches.append(
                            {
                                "row": index - 1,
                                "witness": witness["id"],
                                "expected_sha256": canonical_sha256(expected),
                                "reported_sha256": canonical_sha256(row),
                            }
                        )
    return mismatches


def independent_analytic_obligations(
    *, quotient_rows_valid: bool, registry_rows_valid: bool
) -> dict[str, Any]:
    q_monotone_in_action = all(
        report_probability(theta, coverage_count, action)
        <= report_probability(theta, coverage_count, action + 1)
        for theta in FROZEN_THETAS
        for agreement_count in range(17)
        for coverage_count in FROZEN_C_VALUES
        for action in range(
            action_interval(agreement_count, coverage_count)[0],
            action_interval(agreement_count, coverage_count)[1],
        )
    )
    composite_monotonicity = all(
        report_probability(
            theta, coverage_count, action_interval(k, coverage_count)[endpoint]
        )
        <= report_probability(
            theta,
            coverage_count,
            action_interval(k + 1, coverage_count)[endpoint],
        )
        for theta in FROZEN_THETAS
        for coverage_count in FROZEN_C_VALUES
        for k in range(16)
        for endpoint in (0, 1)
    )
    generic_census = independent_generic_h3_terminal_census()
    generic_census_pass = strict_json_equal(
        generic_census,
        {
            "horizon": 3,
            "monotone_boolean_terminal_count": 20,
            "nonsymmetric_terminal_count": 15,
            "registered_action_law_comparisons": 11520,
            "all_values_equal": True,
        },
    )
    return {
        "generic_terminal_census": generic_census,
        "full_history_induction": {
            "terminal_coordinatewise_monotonicity_is_the_only_phi_premise": True,
            "continuation_difference_is_nonnegative_by_backward_induction": True,
            "bellman_action_value_is_affine_in_q": True,
            "q_is_nondecreasing_in_action_for_theta_at_least_half": q_monotone_in_action,
            "constant_endpoint_masks_exist": quotient_rows_valid,
            "private_randomized_policies_are_convex_mixtures": True,
            "claim_horizon_is_deterministic_finite_0_to_8192": True,
            "all_h3_monotone_boolean_terminals_include_nonsymmetric_cases": generic_census_pass,
        },
        "composite_and_minimality": {
            "both_endpoint_laws_are_nondecreasing_in_k": composite_monotonicity,
            "worst_compliant_boundary_is_k8": composite_monotonicity,
            "worst_forbidden_boundary_is_k1": composite_monotonicity,
            "all_48_upstream_status_and_predecessor_certificates_transfer": registry_rows_valid,
            "constant_endpoint_masks_supply_the_lower_bound": quotient_rows_valid,
        },
        "all_obligations_pass": bool(
            quotient_rows_valid
            and registry_rows_valid
            and q_monotone_in_action
            and composite_monotonicity
            and generic_census_pass
        ),
    }


def independent_controls(
    *, quotient_rows_valid: bool, registry_rows_valid: bool
) -> dict[str, Any]:
    causal_q0 = report_probability(Fraction(1), 12, action_interval(8, 12)[1])
    causal_q1 = report_probability(Fraction(1), 12, action_interval(14, 12)[0])
    anticipatory_q0 = Fraction(8, 16) + Fraction(8, 16) * Fraction(1, 2)
    anticipatory_q1 = Fraction(14, 16) * Fraction(1, 2)

    lower, upper = action_interval(8, 12)
    probabilities = tuple(
        report_probability(Fraction(1), 12, action)
        for action in range(lower, upper + 1)
    )
    adaptive = max(
        (1 - first) * after_zero + first * (1 - after_one)
        for first in probabilities
        for after_zero in probabilities
        for after_one in probabilities
    )
    fixed = max(2 * probability * (1 - probability) for probability in probabilities)

    theta_half_null = all(
        report_probability(Fraction(1, 2), coverage_count, action)
        == Fraction(1, 2)
        for agreement_count in range(17)
        for coverage_count in FROZEN_C_VALUES
        for action in range(
            action_interval(agreement_count, coverage_count)[0],
            action_interval(agreement_count, coverage_count)[1] + 1,
        )
    )
    zero_coverage_null = all(
        report_probability(theta, 0, 0) == Fraction(1, 2)
        for theta in FROZEN_THETAS
    )
    full_coverage_single_action = all(
        action_interval(k, 16) == (k, k) for k in range(17)
    )
    return {
        "current_X_anticipatory_timing": {
            "causal_compliant_q0": fraction_text(causal_q0),
            "causal_forbidden_q1": fraction_text(causal_q1),
            "anticipatory_compliant_q0": fraction_text(anticipatory_q0),
            "anticipatory_forbidden_q1": fraction_text(anticipatory_q1),
            "causal_ordering": causal_q0 < causal_q1,
            "anticipatory_reversal": anticipatory_q0 > anticipatory_q1,
            "pass": (
                causal_q0,
                causal_q1,
                anticipatory_q0,
                anticipatory_q1,
            )
            == (Fraction(5, 8), Fraction(3, 4), Fraction(3, 4), Fraction(7, 16)),
        },
        "nonmonotone_h2_exactly_one": {
            "adaptive_value": fraction_text(adaptive),
            "best_fixed_value": fraction_text(fixed),
            "intended_divergence": adaptive > fixed,
            "pass": adaptive == Fraction(5, 8) and fixed == Fraction(1, 2),
        },
        "concrete_masks_equal_attainable_a_quotient": {
            "registered_pairs": 72,
            "pass": quotient_rows_valid,
        },
        "input_relabeling": {
            "permutation": [(5 * point + 3) % 16 for point in range(16)],
            "pass": quotient_rows_valid,
        },
        "v0_3_all_selective_records": {
            "registered_rows": 48,
            "pass": registry_rows_valid,
        },
        "theta_half_zero_coverage_full_coverage": {
            "theta_half_is_blind": theta_half_null,
            "zero_coverage_is_blind": zero_coverage_null,
            "full_coverage_has_single_action_for_every_k": full_coverage_single_action,
            "pass": bool(
                theta_half_null
                and zero_coverage_null
                and full_coverage_single_action
            ),
        },
    }


def independent_metric_robustness(
    *, oracle_rows_valid: bool, controls: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    return {
        "P1_input_relabeling": {
            "family": "invariance",
            "pass": controls["input_relabeling"]["pass"],
        },
        "P2_timing_sensitivity": {
            "family": "sensitivity",
            "pass": controls["current_X_anticipatory_timing"]["pass"],
        },
        "P3_terminal_monotonicity": {
            "family": "monotonicity",
            "registered_rows": 144,
            "pass": oracle_rows_valid,
        },
        "P4_nonmonotone_scope_breaker": {
            "family": "anti_gaming",
            "pass": controls["nonmonotone_h2_exactly_one"]["pass"],
        },
        "P5_upstream_and_simple_limits": {
            "family": "clean_control",
            "pass": controls["v0_3_all_selective_records"]["pass"]
            and controls["theta_half_zero_coverage_full_coverage"]["pass"],
        },
    }


def find_control_mismatches(
    reported: Any, expected: dict[str, Any]
) -> list[dict[str, Any]]:
    if not isinstance(reported, dict):
        return [{"field": "controls", "error": "not_object"}]
    mismatches: list[dict[str, Any]] = []
    if set(reported) != set(expected):
        mismatches.append(
            {
                "field": "control_key_universe",
                "expected": sorted(expected),
                "reported": sorted(reported),
            }
        )
    for name, expected_record in expected.items():
        reported_record = reported.get(name)
        if not strict_json_equal(reported_record, expected_record):
            mismatches.append(
                {
                    "field": name,
                    "expected_sha256": canonical_sha256(expected_record),
                    "reported_sha256": canonical_sha256(reported_record),
                }
            )
    return mismatches


def resource_observations_valid(result: dict[str, Any]) -> bool:
    observations = result.get("resource_observations")
    if not isinstance(observations, dict):
        return False
    expected_fields = {
        "canonical_result_bytes",
        "completed_quotient_rows",
        "completed_registry_rows",
        "completed_oracle_rows",
        "completed_generic_terminal_comparisons",
        "elapsed_wall_ns",
        "traced_python_peak_bytes",
        "traced_python_limit_bytes",
        "wall_limit_ns",
        "memory_measurement",
        "process_rss_and_native_memory_measured",
    }
    if set(observations) != expected_fields:
        return False
    integer_fields = (
        "canonical_result_bytes",
        "completed_quotient_rows",
        "completed_registry_rows",
        "completed_oracle_rows",
        "completed_generic_terminal_comparisons",
        "elapsed_wall_ns",
        "traced_python_peak_bytes",
        "traced_python_limit_bytes",
        "wall_limit_ns",
    )
    if any(type(observations.get(name)) is not int for name in integer_fields):
        return False
    return bool(
        observations["canonical_result_bytes"]
        == len(canonical_json(result).encode("utf-8"))
        and observations["canonical_result_bytes"] <= 1048576
        and observations["completed_quotient_rows"] == 72
        and observations["completed_registry_rows"] == 48
        and observations["completed_oracle_rows"] == 144
        and observations["completed_generic_terminal_comparisons"] == 11520
        and 0 <= observations["elapsed_wall_ns"] <= 30_000_000_000
        and observations["traced_python_limit_bytes"] == 64 * 1024 * 1024
        and 0
        <= observations["traced_python_peak_bytes"]
        <= observations["traced_python_limit_bytes"]
        and observations["wall_limit_ns"] == 30_000_000_000
        and observations["memory_measurement"]
        == "tracemalloc_peak_python_allocation_only"
        and observations["process_rss_and_native_memory_measured"] is False
    )


def primary_result_semantic_checks(
    result: Any, *, raw_result_bytes: bytes, manifest: dict[str, Any]
) -> dict[str, bool]:
    if not isinstance(result, dict):
        return {
            "result_fields_are_exact": False,
            "result_identity_is_exact": False,
            "source_binding_shape_is_valid": False,
            "upstream_binding_shape_is_valid": False,
            "raw_result_is_canonical_json": False,
            "claim_boundary_is_exact": False,
            "exact_json_firewall": False,
            "primary_gates_are_exact_and_true": False,
            "preverification_layers_are_exact": False,
        }
    source = result.get("source_binding")
    upstream = result.get("upstream_bindings")
    gates = result.get("gates")
    source_files = source.get("source_files") if isinstance(source, dict) else None
    return {
        "result_fields_are_exact": set(result) == FROZEN_RESULT_FIELDS,
        "result_identity_is_exact": bool(
            result.get("schema_version")
            == "asmp7_causal_adaptive_suppression_result_v0_4"
            and result.get("protocol_id") == FROZEN_PROTOCOL_ID
            and result.get("manifest_sha256")
            == FROZEN_MANIFEST_CANONICAL_SHA256
            and result.get("status") == "complete"
            and result.get("stop_reason") == "registered_contract_complete"
        ),
        "source_binding_shape_is_valid": bool(
            isinstance(source, dict)
            and set(source)
            == {
                "repo_relative_directory",
                "source_commit",
                "source_commit_is_ancestor_of_head",
                "source_commit_type",
                "source_files",
            }
            and isinstance(source.get("source_commit"), str)
            and re.fullmatch(r"[0-9a-f]{40}", source["source_commit"])
            and source.get("source_commit_type") == "commit"
            and source.get("source_commit_is_ancestor_of_head") is True
            and isinstance(source_files, dict)
            and set(source_files) == set(FROZEN_SOURCE_FILES)
        ),
        "upstream_binding_shape_is_valid": bool(
            isinstance(upstream, dict) and set(upstream) == {"v0_1", "v0_3"}
        ),
        "raw_result_is_canonical_json": raw_result_bytes
        == canonical_json(result).encode("utf-8"),
        "claim_boundary_is_exact": bool(
            strict_json_equal(
                result.get("claim_boundary"), list(FROZEN_CLAIM_BOUNDARY)
            )
            and strict_json_equal(
                manifest.get("claim_boundary"), list(FROZEN_CLAIM_BOUNDARY)
            )
        ),
        "exact_json_firewall": not contains_float(result),
        "primary_gates_are_exact_and_true": bool(
            isinstance(gates, dict)
            and tuple(gates) == FROZEN_PRIMARY_GATES
            and all(value is True for value in gates.values())
        ),
        "preverification_layers_are_exact": (
            strict_json_equal(
                result.get("conclusion_layers"), FROZEN_PREVERIFICATION_LAYERS
            )
        ),
    }


def verify(
    manifest_path: Path | None = None, result_path: Path | None = None
) -> dict[str, Any]:
    verification_start_ns = time.monotonic_ns()
    owned_trace = not tracemalloc.is_tracing()
    if owned_trace:
        tracemalloc.start()
    tracemalloc.reset_peak()
    manifest_path = manifest_path or HERE / "manifest_v0_4.json"
    result_path = result_path or (
        HERE.parent / "artifacts_v0_4_adaptive_suppression" / "result_v0_4.json"
    )
    manifest_bytes = manifest_path.read_bytes()
    result_bytes = result_path.read_bytes()
    manifest = load_json_bytes_strict(manifest_bytes)
    result = load_json_bytes_strict(result_bytes)
    if not isinstance(manifest, dict) or not isinstance(result, dict):
        raise ValueError("manifest and result roots must be objects")

    binding = manifest_binding_checks(manifest)

    source_binding_error = ""
    replayed_source: dict[str, Any] = {}
    reported_source = result.get("source_binding")
    if isinstance(reported_source, dict) and isinstance(
        reported_source.get("source_commit"), str
    ):
        try:
            replayed_source = replay_source_binding(reported_source["source_commit"])
        except (OSError, subprocess.SubprocessError, TypeError, ValueError) as error:
            source_binding_error = f"{type(error).__name__}: {error}"
    else:
        source_binding_error = "source binding or source commit is absent"
    source_binding_matches = bool(replayed_source) and strict_json_equal(
        reported_source, replayed_source
    )

    upstream_error = ""
    replayed_upstream: dict[str, Any] = {}
    try:
        replayed_upstream = replay_upstream_bindings(manifest)
    except (OSError, subprocess.SubprocessError, KeyError, TypeError, ValueError) as error:
        upstream_error = f"{type(error).__name__}: {error}"
    upstream_matches = bool(replayed_upstream) and strict_json_equal(
        result.get("upstream_bindings"), replayed_upstream
    )
    upstream_checks = {
        "error": upstream_error,
        "reported_matches_replay": upstream_matches,
        "replayed_bindings": replayed_upstream,
    }

    quotient_failures = quotient_mismatches(result.get("quotient_rows"))
    try:
        registry_failures = registry_mismatches(
            manifest, result.get("registry_rows")
        )
    except (OSError, subprocess.SubprocessError, KeyError, TypeError, ValueError) as error:
        registry_failures = [{"field": "reconstruction", "error": str(error)}]
    try:
        oracle_failures = oracle_mismatches(manifest, result.get("oracle_rows"))
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        oracle_failures = [{"field": "reconstruction", "error": str(error)}]

    quotient_valid = not quotient_failures
    registry_valid = not registry_failures
    oracle_valid = not oracle_failures
    expected_analytic = independent_analytic_obligations(
        quotient_rows_valid=quotient_valid,
        registry_rows_valid=registry_valid,
    )
    analytic_checks = {
        "independent_reconstruction": expected_analytic,
        "reported_matches_independent_reconstruction": strict_json_equal(
            result.get("analytic_obligations"), expected_analytic
        ),
        "independent_full_history_checks_pass": all(
            expected_analytic["full_history_induction"].values()
        ),
        "independent_composite_checks_pass": all(
            expected_analytic["composite_and_minimality"].values()
        ),
        "independent_all_obligations_pass": expected_analytic[
            "all_obligations_pass"
        ]
        is True,
    }

    expected_controls = independent_controls(
        quotient_rows_valid=quotient_valid,
        registry_rows_valid=registry_valid,
    )
    control_failures = find_control_mismatches(
        result.get("controls"), expected_controls
    )
    expected_metrics = independent_metric_robustness(
        oracle_rows_valid=oracle_valid, controls=expected_controls
    )
    metrics_match = bool(
        strict_json_equal(result.get("metric_robustness"), expected_metrics)
        and tuple(expected_metrics) == FROZEN_PROBE_IDS
        and all(record["pass"] for record in expected_metrics.values())
    )

    semantic_checks = primary_result_semantic_checks(
        result, raw_result_bytes=result_bytes, manifest=manifest
    )
    identity_check_names = (
        "result_fields_are_exact",
        "result_identity_is_exact",
        "source_binding_shape_is_valid",
        "upstream_binding_shape_is_valid",
        "raw_result_is_canonical_json",
        "claim_boundary_is_exact",
        "exact_json_firewall",
    )
    result_identity_valid = all(
        semantic_checks[name] for name in identity_check_names
    )
    primary_gates_valid = semantic_checks["primary_gates_are_exact_and_true"]
    layers_match = semantic_checks["preverification_layers_are_exact"]
    resources_valid = resource_observations_valid(result)
    verification_elapsed_ns = time.monotonic_ns() - verification_start_ns
    _, verification_peak_bytes = tracemalloc.get_traced_memory()
    if owned_trace:
        tracemalloc.stop()
    verification_resources = {
        "completed_generic_terminal_comparisons": expected_analytic[
            "generic_terminal_census"
        ]["registered_action_law_comparisons"],
        "elapsed_wall_ns": verification_elapsed_ns,
        "memory_measurement": "tracemalloc_peak_python_allocation_only",
        "process_rss_and_native_memory_measured": False,
        "traced_python_limit_bytes": 64 * 1024 * 1024,
        "traced_python_peak_bytes": verification_peak_bytes,
        "wall_limit_ns": 30_000_000_000,
    }
    verification_resources_valid = bool(
        verification_resources["completed_generic_terminal_comparisons"] == 11520
        and 0 <= verification_elapsed_ns <= 30_000_000_000
        and 0 <= verification_peak_bytes <= 64 * 1024 * 1024
    )

    analytic_valid = bool(
        analytic_checks["reported_matches_independent_reconstruction"]
        and analytic_checks["independent_full_history_checks_pass"]
        and analytic_checks["independent_composite_checks_pass"]
        and analytic_checks["independent_all_obligations_pass"]
    )
    controls_valid = not control_failures and all(
        record["pass"] for record in expected_controls.values()
    )
    independent_gates = {
        "V0_frozen_manifest_binding": all(binding.values()),
        "V1_exact_live_and_source_commit_binding": bool(
            not source_binding_error and source_binding_matches
        ),
        "V2_exact_historical_upstream_bytes": bool(
            not upstream_error and upstream_matches
        ),
        "V3_result_identity_and_canonical_json": result_identity_valid,
        "V4_complete_72_pair_combinatorial_quotient": quotient_valid,
        "V5_complete_48_row_v03_and_minimum_transfer": registry_valid,
        "V6_complete_144_row_independent_oracle": oracle_valid,
        "V7_induction_composite_and_scope_obligations": analytic_valid,
        "V8_scope_breakers_and_simple_limits": controls_valid,
        "V9_five_metric_probe_families": metrics_match,
        "V10_primary_gates_and_preverification_layers": primary_gates_valid
        and layers_match,
        "V11_resource_observations_within_frozen_limits": resources_valid
        and verification_resources_valid,
    }
    if tuple(independent_gates) != FROZEN_VERIFICATION_GATES:
        raise AssertionError("independent gate universe changed")
    passed = all(independent_gates.values())
    final_layers = (
        dict(FROZEN_FINAL_LAYERS)
        if passed
        else {
            "metric_robustness": "not_established",
            "task_result": "not_established",
            "measurement_reliability": "failed",
            "claim_support": "none",
            "operational_decision": "no_deployment_authorization_repair",
        }
    )
    verification = {
        "schema_version": "asmp7_causal_adaptive_suppression_verification_v0_4",
        "pass": passed,
        "protocol_id": FROZEN_PROTOCOL_ID,
        "manifest_binding": binding,
        "source_binding_error": source_binding_error,
        "source_binding_replay": replayed_source,
        "upstream_binding_checks": upstream_checks,
        "result_semantic_checks": semantic_checks,
        "quotient_mismatches": quotient_failures,
        "registry_mismatches": registry_failures,
        "oracle_mismatches": oracle_failures,
        "analytic_obligations": analytic_checks,
        "control_mismatches": control_failures,
        "metric_probe_ids": list(FROZEN_PROBE_IDS),
        "metric_probes_match": metrics_match,
        "resource_observations_valid": resources_valid,
        "verification_resource_observations": verification_resources,
        "primary_gates_valid": primary_gates_valid,
        "preverification_layers_match": layers_match,
        "independent_gates": independent_gates,
        "final_conclusion_layers": final_layers,
        "claim_boundary": list(FROZEN_CLAIM_BOUNDARY),
        "bindings": {
            "manifest_v0_4.json": {
                "raw_sha256": sha256_bytes(manifest_bytes),
                "canonical_sha256": canonical_sha256(manifest),
            },
            "result_v0_4.json": {
                "raw_sha256": sha256_bytes(result_bytes),
                "canonical_sha256": canonical_sha256(result),
            },
        },
        "implementation_imported": False,
    }
    if set(verification) != FROZEN_VERIFICATION_FIELDS:
        raise AssertionError("verification field universe changed")
    if contains_float(verification):
        raise AssertionError("independent verification contains a float")
    return verification


def _absolute_without_reparse_resolution(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _destination_chain(destination: Path) -> tuple[Path, ...]:
    chain = [destination]
    while chain[-1].parent != chain[-1]:
        chain.append(chain[-1].parent)
    chain.reverse()
    return tuple(chain)


def _lstat_optional(path: Path) -> os.stat_result | None:
    try:
        return path.lstat()
    except FileNotFoundError:
        return None
    except OSError as error:
        raise ValueError(
            f"cannot inspect verification destination component: {path}"
        ) from error


def _require_safe_directory(path: Path, metadata: os.stat_result) -> None:
    if _is_reparse_point(path):
        raise ValueError(f"verification destination contains reparse point: {path}")
    if not stat.S_ISDIR(metadata.st_mode):
        raise NotADirectoryError(
            f"verification destination ancestor is not a directory: {path}"
        )


def _prepare_write_once_destination(path: Path) -> Path:
    destination = _absolute_without_reparse_resolution(path)
    chain = _destination_chain(destination)
    for component in chain[:-1]:
        metadata = _lstat_optional(component)
        if metadata is None:
            try:
                component.mkdir()
            except OSError as error:
                raise ValueError(
                    f"cannot create verification directory: {component}"
                ) from error
            metadata = _lstat_optional(component)
            if metadata is None:
                raise ValueError(f"verification directory vanished: {component}")
        _require_safe_directory(component, metadata)
    output_metadata = _lstat_optional(destination)
    if output_metadata is not None:
        if _is_reparse_point(destination):
            raise ValueError(f"verification output is a reparse point: {destination}")
        raise FileExistsError(
            f"verification destination already exists: {destination}"
        )
    for component in chain[:-1]:
        metadata = _lstat_optional(component)
        if metadata is None:
            raise ValueError(f"verification ancestor vanished: {component}")
        _require_safe_directory(component, metadata)
    return destination


def write_once_json(path: Path, value: Any, max_bytes: int = 1048576) -> None:
    payload = canonical_json(value).encode("utf-8")
    if len(payload) > max_bytes:
        raise ValueError("verification exceeds frozen artifact byte ceiling")
    destination = _prepare_write_once_destination(path)
    with destination.open("xb") as stream:
        stream.write(payload)


def validate_output_path(path: Path) -> Path:
    destination = _absolute_without_reparse_resolution(path)
    artifact_directory = _absolute_without_reparse_resolution(ARTIFACT_DIRECTORY)
    if destination.parent != artifact_directory:
        raise SystemExit(
            "refusing output outside the frozen sibling artifact directory"
        )
    try:
        destination.lstat()
    except FileNotFoundError:
        return destination
    except OSError as error:
        raise SystemExit(f"cannot inspect output path: {destination}") from error
    raise SystemExit(f"refusing occupied write-once output path: {destination}")


def validate_input_paths(manifest_path: Path, result_path: Path) -> None:
    manifest = _absolute_without_reparse_resolution(manifest_path)
    frozen_manifest = _absolute_without_reparse_resolution(
        HERE / "manifest_v0_4.json"
    )
    result = _absolute_without_reparse_resolution(result_path)
    artifact_directory = _absolute_without_reparse_resolution(ARTIFACT_DIRECTORY)
    if manifest != frozen_manifest:
        raise SystemExit("refusing a manifest outside the frozen source directory")
    if result.parent != artifact_directory:
        raise SystemExit("refusing a result outside the frozen artifact directory")
    try:
        if _is_reparse_point(result) or not result.is_file():
            raise SystemExit("refusing non-regular or reparse-point result input")
    except FileNotFoundError as error:
        raise SystemExit(f"result input is absent: {result}") from error


def main() -> None:
    require_isolated_safe_path()
    validate_live_source_inventory()
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=HERE / "manifest_v0_4.json")
    parser.add_argument(
        "--result",
        type=Path,
        default=HERE.parent
        / "artifacts_v0_4_adaptive_suppression"
        / "result_v0_4.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ARTIFACT_DIRECTORY / "verification_v0_4.json",
    )
    args = parser.parse_args()
    output_path = validate_output_path(args.output)
    validate_input_paths(args.manifest, args.result)
    verification = verify(args.manifest, args.result)
    write_once_json(output_path, verification)
    if not verification["pass"]:
        failed = [
            name
            for name, gate_passed in verification["independent_gates"].items()
            if not gate_passed
        ]
        raise SystemExit(
            "independent verification failed; downgraded write-once artifact "
            f"retained: {failed}"
        )
    print(output_path)


if __name__ == "__main__":
    main()
