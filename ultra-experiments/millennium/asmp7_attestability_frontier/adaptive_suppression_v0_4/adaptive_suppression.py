"""Exact primary implementation for ASMP-7 causal adaptive suppression v0.4."""

from __future__ import annotations

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
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Sequence


HERE = Path(os.path.abspath(__file__)).parent
FROZEN_PROTOCOL_ID = "ASMP7-CAUSAL-ADAPTIVE-SUPPRESSION-v0.4"
FROZEN_SCHEMA_VERSION = "asmp7_adaptive_suppression_manifest_v0_4"
FROZEN_MANIFEST_CANONICAL_SHA256 = (
    "c3c9430257645e5709ce3c838c124e021ad293d750d7bd1afb75c0eaaed4a1d3"
)
FROZEN_REPLAY_COMMAND = "python -I run.py --source-commit <40-hex-source-commit>"
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
FROZEN_K_VALUES = (0, 1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 16)
FROZEN_K1_VALUES = (14, 16)
FROZEN_THETA_VALUES = (Fraction(1, 2), Fraction(3, 4), Fraction(4, 5), Fraction(1))
FROZEN_C_VALUES = (0, 8, 10, 12, 14, 16)
FROZEN_THRESHOLDS = (0, 1, 2, 3)
FROZEN_GAMMAS = (Fraction(), Fraction(1, 2), Fraction(1))
FROZEN_OBJECTIVES = ("max", "min")
FROZEN_LAYER_NAMES = (
    "metric_robustness",
    "task_result",
    "measurement_reliability",
    "claim_support",
    "operational_decision",
)
FROZEN_PROBE_IDS = (
    "P1_input_relabeling",
    "P2_timing_sensitivity",
    "P3_terminal_monotonicity",
    "P4_nonmonotone_scope_breaker",
    "P5_upstream_and_simple_limits",
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
FROZEN_PREVERIFICATION_LAYERS = {
    "metric_robustness": "five_frozen_probe_families_computed_awaiting_independent_replay",
    "task_result": "finite_causal_endpoint_equivalence_and_v03_minimum_transfer",
    "measurement_reliability": "awaiting_import_independent_verification",
    "claim_support": "pending_independent_verification",
    "operational_decision": "no_deployment_authorization_await_independent_verification",
}
GIT_EXECUTABLE = shutil.which("git")


class ResourceStop(RuntimeError):
    """A frozen resource ceiling stopped the deterministic run."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def exact_fraction(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("booleans and floating point are forbidden")
    if isinstance(value, Fraction):
        return value
    if type(value) is int:
        return Fraction(value)
    if isinstance(value, str) and re.fullmatch(r"-?(0|[1-9][0-9]*)/[1-9][0-9]*", value):
        parsed = Fraction(value)
        if fraction_text(parsed) != value:
            raise ValueError(f"noncanonical fraction: {value}")
        return parsed
    raise TypeError(f"not an exact scalar: {value!r}")


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
    raise ValueError(f"floating-point JSON number is forbidden: {value}")


def _reject_constant(value: str) -> Any:
    raise ValueError(f"nonfinite JSON constant is forbidden: {value}")


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
    source = manifest.get("source_freeze", {})
    budget = manifest.get("budget", {})
    artifacts = manifest.get("artifacts", {})
    semantics = manifest.get("semantics", {})
    return {
        "canonical_manifest_hash_is_frozen": canonical_sha256(manifest)
        == FROZEN_MANIFEST_CANONICAL_SHA256,
        "protocol_and_schema_are_frozen": manifest.get("protocol_id")
        == FROZEN_PROTOCOL_ID
        and manifest.get("schema") == "alife.experiment.v1"
        and manifest.get("schema_version") == FROZEN_SCHEMA_VERSION,
        "registration_is_preexecution": manifest.get("registration_status")
        == "source_candidate_not_executed_requires_commit_before_run",
        "source_inventory_is_exact": tuple(source.get("files", ()))
        == FROZEN_SOURCE_FILES
        and source.get("artifact_execution_before_commit") == "forbidden",
        "isolated_replay_is_exact": artifacts.get("replay_command")
        == FROZEN_REPLAY_COMMAND,
        "registry_key_universes_are_exact": tuple(registry.get("forbidden_boundaries", ()))
        == FROZEN_K1_VALUES
        and tuple(Fraction(value) for value in registry.get("theta_grid", ()))
        == FROZEN_THETA_VALUES
        and tuple(registry.get("coverage_counts", ())) == FROZEN_C_VALUES
        and tuple(registry.get("quotient_agreement_counts", ())) == FROZEN_K_VALUES
        and registry.get("parameter_triple_count") == 48
        and registry.get("quotient_pair_count") == 72
        and registry.get("oracle", {}).get("comparison_count") == 144
        and registry.get("generic_terminal_census")
        == {
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
            "theta_grid": [fraction_text(value) for value in FROZEN_THETA_VALUES],
        },
        "filtration_and_monitor_are_frozen": semantics.get("challenge")
        == "conditional on the complete frozen filtration including S_t and all suppressor-private coins used through time t, X_t is uniform on {0,...,15} and independent of all earlier and future challenge/report/auditor coins"
        and semantics.get("fresh_stream_product_law")
        == "challenge draws, randomized-response coins, uncovered fallback coins, auditor coins, and suppressor-private coins are mutually independent product streams; conditioning on the frozen past and S_t leaves the current challenge uniform and both current report coins fresh"
        and semantics.get("monitor")
        == "the monitor receives only Y_1,...,Y_m; registered upper-tail decisions use K=sum_t Y_t"
        and semantics.get("report_law")
        == "q_theta(a)=1/2+(2*theta-1)*(a-c/2)/16 for a=|S intersect A|",
        "layers_are_exact": tuple(manifest.get("conclusion_layer_names", ()))
        == FROZEN_LAYER_NAMES,
        "resource_and_write_once_contract_is_exact": budget.get("max_steps_per_episode")
        == 8192
        and budget.get("max_wall_seconds") == 30
        and budget.get("max_traced_python_mib") == 64
        and budget.get("max_result_bytes") == 1048576
        and budget.get("max_generic_terminal_comparisons") == 11520
        and manifest.get("write_once_artifacts", {}).get("refuse_existing_paths") is True,
    }


def validate_manifest_binding(manifest: dict[str, Any]) -> dict[str, bool]:
    checks = manifest_binding_checks(manifest)
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"manifest binding failed: {failed}")
    return checks


def load_manifest(path: Path = HERE / "manifest_v0_4.json") -> dict[str, Any]:
    manifest = load_json_strict(path)
    if not isinstance(manifest, dict):
        raise TypeError("manifest root must be an object")
    validate_manifest_binding(manifest)
    return manifest


def _git(args: list[str], *, text: bool, cwd: Path | None = None) -> str | bytes:
    if GIT_EXECUTABLE is None:
        raise RuntimeError("Git executable is unavailable")
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    completed = subprocess.run(
        [GIT_EXECUTABLE, *args],
        cwd=cwd or HERE,
        env=environment,
        check=True,
        capture_output=True,
        text=text,
    )
    return completed.stdout.strip() if text else completed.stdout


def repo_root() -> Path:
    return Path(str(_git(["rev-parse", "--show-toplevel"], text=True))).resolve()


def committed_bytes(commit: str, path: str) -> bytes:
    return bytes(_git(["show", f"{commit}:{path}"], text=False, cwd=repo_root()))


def validate_upstream_bindings(manifest: dict[str, Any]) -> dict[str, Any]:
    root = repo_root()
    output: dict[str, Any] = {}
    for version in ("v0_1", "v0_3"):
        group = manifest["upstream_bindings"][version]
        default_commit = group["evidence_commit"]
        commits = {default_commit}
        if "source_commit" in group:
            commits.add(group["source_commit"])
        if "registration_commit" in group:
            commits.add(group["registration_commit"])
        records: list[dict[str, str]] = []
        for item in group["files"]:
            commit = item.get("commit", default_commit)
            commits.add(commit)
            payload = bytes(
                _git(["show", f"{commit}:{item['path']}"], text=False, cwd=root)
            )
            actual = sha256_bytes(payload)
            if actual != item["sha256"]:
                raise ValueError(f"upstream hash mismatch: {version}:{item['path']}")
            records.append(
                {
                    "commit": commit,
                    "path": item["path"],
                    "role": item["role"],
                    "sha256": actual,
                }
            )
        for commit in commits:
            if not re.fullmatch(r"[0-9a-f]{40}", commit):
                raise ValueError(f"upstream commit is not full hex: {commit}")
            if str(_git(["cat-file", "-t", commit], text=True, cwd=root)) != "commit":
                raise ValueError(f"upstream object is not a commit: {commit}")
            ancestry = subprocess.run(
                [GIT_EXECUTABLE, "merge-base", "--is-ancestor", commit, "HEAD"],
                cwd=root,
                env={
                    **{
                        key: value
                        for key, value in os.environ.items()
                        if not key.startswith("GIT_")
                    },
                    "GIT_NO_REPLACE_OBJECTS": "1",
                },
            )
            if ancestry.returncode != 0:
                raise ValueError(f"upstream commit is not an ancestor: {commit}")
        output[version] = {
            "commits": sorted(commits),
            "files": records,
            "all_hashes_match": True,
        }
    return output


def upstream_v03_result(manifest: dict[str, Any]) -> dict[str, Any]:
    group = manifest["upstream_bindings"]["v0_3"]
    candidates = [
        item
        for item in group["files"]
        if item["role"] == "artifact" and item["path"].endswith("/result.json")
    ]
    if len(candidates) != 1:
        raise ValueError("v0.3 result binding is not unique")
    candidate = candidates[0]
    payload = committed_bytes(
        candidate.get("commit", group["evidence_commit"]), candidate["path"]
    )
    if sha256_bytes(payload) != candidate["sha256"]:
        raise ValueError("v0.3 result changed after upstream validation")
    result = load_json_bytes_strict(payload)
    if not isinstance(result, dict):
        raise TypeError("v0.3 result root is not an object")
    return result


def action_interval(agreement_count: int, coverage_count: int) -> tuple[int, int]:
    if not 0 <= agreement_count <= 16 or not 0 <= coverage_count <= 16:
        raise ValueError("agreement and coverage counts must be in 0..16")
    return max(0, agreement_count + coverage_count - 16), min(
        agreement_count, coverage_count
    )


def report_probability(theta: Fraction, coverage_count: int, covered_agreements: int) -> Fraction:
    theta = exact_fraction(theta)
    lower, upper = action_interval(16, coverage_count)
    del lower, upper
    if not 0 <= covered_agreements <= coverage_count:
        raise ValueError("covered agreement count is outside the mask")
    return Fraction(1, 2) + (2 * theta - 1) * Fraction(
        2 * covered_agreements - coverage_count, 32
    )


def endpoint_probabilities(
    agreement_count: int, coverage_count: int, theta: Fraction
) -> tuple[Fraction, Fraction]:
    lower, upper = action_interval(agreement_count, coverage_count)
    return (
        report_probability(theta, coverage_count, lower),
        report_probability(theta, coverage_count, upper),
    )


def relabel_point(point: int) -> int:
    return (5 * point + 3) % 16


def quotient_row(agreement_count: int, coverage_count: int) -> dict[str, Any]:
    agreement_set = set(range(agreement_count))
    relabeled_agreement_set = {relabel_point(point) for point in agreement_set}
    counts: Counter[int] = Counter()
    relabeled_counts: Counter[int] = Counter()
    for mask in itertools.combinations(range(16), coverage_count):
        mask_set = set(mask)
        counts[len(mask_set & agreement_set)] += 1
        relabeled_mask = {relabel_point(point) for point in mask_set}
        relabeled_counts[len(relabeled_mask & relabeled_agreement_set)] += 1
    lower, upper = action_interval(agreement_count, coverage_count)
    expected_values = list(range(lower, upper + 1))
    return {
        "agreement_count": agreement_count,
        "coverage_count": coverage_count,
        "action_interval": [lower, upper],
        "attainable_a": expected_values,
        "multiplicities": [
            {"a": value, "count": counts[value]} for value in expected_values
        ],
        "total_masks": sum(counts.values()),
        "canonical_attained_set": sorted(counts),
        "relabeled_attained_set": sorted(relabeled_counts),
        "relabel_permutation": [(5 * point + 3) % 16 for point in range(16)],
        "checks": {
            "complete_interval": sorted(counts) == expected_values,
            "multiplicity_total": sum(counts.values())
            == math.comb(16, coverage_count),
            "relabel_invariant": counts == relabeled_counts,
        },
    }


def build_quotient_rows() -> list[dict[str, Any]]:
    return [
        quotient_row(agreement_count, coverage_count)
        for agreement_count in FROZEN_K_VALUES
        for coverage_count in FROZEN_C_VALUES
    ]


def _v03_selective_map(result: dict[str, Any]) -> dict[tuple[int, Fraction, int], dict[str, Any]]:
    records = result.get("records")
    if not isinstance(records, list):
        raise TypeError("bound v0.3 records are absent")
    selective = [record for record in records if record.get("model") == "adversarial_selective"]
    if len(selective) != 48:
        raise ValueError("bound v0.3 selective registry is not 48 rows")
    output: dict[tuple[int, Fraction, int], dict[str, Any]] = {}
    for record in selective:
        key = (
            record.get("k1"),
            exact_fraction(record.get("theta")),
            record.get("coverage_count"),
        )
        if key in output:
            raise ValueError(f"duplicate bound v0.3 row: {key}")
        output[key] = record
    return output


def _registry_transfer_checks(
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
        "status_is_registered": status in {"feasible_exact", "common_law_impossible"},
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
        k1 = record.get("k1")
        compliant_range = action_interval(8, coverage_count)
        forbidden_range = action_interval(k1, coverage_count)
        shared_lower = max(compliant_range[0], forbidden_range[0])
        shared_upper = min(compliant_range[1], forbidden_range[1])
        privacy_kill = theta == Fraction(1, 2)
        overlap = shared_lower <= shared_upper
        if privacy_kill:
            witness_valid = (
                isinstance(witness, dict)
                and witness.get("kind") == "identical_bernoulli_law"
                and exact_fraction(witness.get("q")) == Fraction(1, 2)
            )
        else:
            shared_action = witness.get("covered_agreements") if isinstance(witness, dict) else None
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


def registry_row(
    bound: dict[tuple[int, Fraction, int], dict[str, Any]],
    k1: int,
    theta: Fraction,
    coverage_count: int,
) -> dict[str, Any]:
    key = (k1, theta, coverage_count)
    if key not in bound:
        raise ValueError(f"missing bound v0.3 row: {key}")
    compliant_interval = action_interval(8, coverage_count)
    forbidden_interval = action_interval(k1, coverage_count)
    q0 = report_probability(theta, coverage_count, compliant_interval[1])
    q1 = report_probability(theta, coverage_count, forbidden_interval[0])
    upstream_record = bound[key]
    checks = _registry_transfer_checks(upstream_record, q0, q1, coverage_count)
    return {
        "k1": k1,
        "theta": fraction_text(theta),
        "coverage_count": coverage_count,
        "compliant_interval": list(compliant_interval),
        "forbidden_interval": list(forbidden_interval),
        "q0_max": fraction_text(q0),
        "q1_min": fraction_text(q1),
        "upstream_record": upstream_record,
        "transfer_checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def build_registry_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    bound = _v03_selective_map(upstream_v03_result(manifest))
    return [
        registry_row(bound, k1, theta, coverage_count)
        for k1 in FROZEN_K1_VALUES
        for theta in FROZEN_THETA_VALUES
        for coverage_count in FROZEN_C_VALUES
    ]


def upper_tail_terminal(
    prefix: tuple[int, ...], threshold: int, gamma: Fraction
) -> Fraction:
    count = sum(prefix)
    if count > threshold:
        return Fraction(1)
    if count == threshold:
        return gamma
    return Fraction()


def brute_force_monotone_boolean_terminals(
    horizon: int,
) -> tuple[tuple[int, ...], ...]:
    histories = tuple(itertools.product((0, 1), repeat=horizon))
    terminals = []
    for values in itertools.product((0, 1), repeat=len(histories)):
        table = dict(zip(histories, values))
        monotone = all(
            table[left] <= table[right]
            for left in histories
            for right in histories
            if all(x <= y for x, y in zip(left, right))
        )
        if monotone:
            terminals.append(values)
    return tuple(terminals)


def generic_full_prefix_bellman_value(
    terminal_values: Sequence[int],
    horizon: int,
    agreement_count: int,
    coverage_count: int,
    theta: Fraction,
    objective: str,
) -> Fraction:
    histories = tuple(itertools.product((0, 1), repeat=horizon))
    if len(terminal_values) != len(histories) or any(
        type(value) is not int or value not in (0, 1) for value in terminal_values
    ):
        raise ValueError("terminal table must be an exact Boolean truth table")
    terminal = dict(zip(histories, terminal_values))
    lower, upper = action_interval(agreement_count, coverage_count)
    actions = tuple(range(lower, upper + 1))
    chooser = max if objective == "max" else min

    @lru_cache(maxsize=None)
    def recurse(prefix: tuple[int, ...]) -> Fraction:
        if len(prefix) == horizon:
            return Fraction(terminal[prefix])
        candidates = []
        for action in actions:
            q = report_probability(theta, coverage_count, action)
            candidates.append(
                (1 - q) * recurse(prefix + (0,))
                + q * recurse(prefix + (1,))
            )
        return chooser(candidates)

    return recurse(())


def iid_terminal_table_value(
    terminal_values: Sequence[int], horizon: int, q: Fraction
) -> Fraction:
    histories = tuple(itertools.product((0, 1), repeat=horizon))
    if len(terminal_values) != len(histories):
        raise ValueError("terminal table has the wrong horizon")
    return sum(
        (
            Fraction(value)
            * q ** sum(history)
            * (1 - q) ** (horizon - sum(history))
        )
        for history, value in zip(histories, terminal_values)
    )


def generic_h3_terminal_census(
    resource_guard: Callable[[], None] | None = None,
    progress_callback: Callable[[], None] | None = None,
) -> dict[str, Any]:
    horizon = 3
    histories = tuple(itertools.product((0, 1), repeat=horizon))
    terminals = brute_force_monotone_boolean_terminals(horizon)
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
                for theta in FROZEN_THETA_VALUES:
                    lower, upper = action_interval(agreement_count, coverage_count)
                    for objective in FROZEN_OBJECTIVES:
                        if resource_guard is not None:
                            resource_guard()
                        endpoint = upper if objective == "max" else lower
                        q = report_probability(theta, coverage_count, endpoint)
                        adaptive = generic_full_prefix_bellman_value(
                            values,
                            horizon,
                            agreement_count,
                            coverage_count,
                            theta,
                            objective,
                        )
                        endpoint_value = iid_terminal_table_value(values, horizon, q)
                        comparisons += 1
                        all_equal = all_equal and adaptive == endpoint_value
                        if progress_callback is not None:
                            progress_callback()
                        if resource_guard is not None:
                            resource_guard()
    return {
        "horizon": horizon,
        "monotone_boolean_terminal_count": len(terminals),
        "nonsymmetric_terminal_count": nonsymmetric,
        "registered_action_law_comparisons": comparisons,
        "all_values_equal": all_equal,
    }


def full_prefix_bellman_value(
    horizon: int,
    agreement_count: int,
    coverage_count: int,
    theta: Fraction,
    threshold: int,
    gamma: Fraction,
    objective: str,
) -> Fraction:
    lower, upper = action_interval(agreement_count, coverage_count)
    actions = tuple(range(lower, upper + 1))
    chooser = max if objective == "max" else min

    @lru_cache(maxsize=None)
    def recurse(prefix: tuple[int, ...]) -> Fraction:
        if len(prefix) == horizon:
            return upper_tail_terminal(prefix, threshold, gamma)
        values = []
        for action in actions:
            q = report_probability(theta, coverage_count, action)
            values.append(
                (1 - q) * recurse(prefix + (0,)) + q * recurse(prefix + (1,))
            )
        return chooser(values)

    return recurse(())


def count_state_bellman_value(
    horizon: int,
    agreement_count: int,
    coverage_count: int,
    theta: Fraction,
    threshold: int,
    gamma: Fraction,
    objective: str,
) -> Fraction:
    lower, upper = action_interval(agreement_count, coverage_count)
    actions = tuple(range(lower, upper + 1))
    chooser = max if objective == "max" else min

    @lru_cache(maxsize=None)
    def recurse(step: int, count: int) -> Fraction:
        if step == horizon:
            if count > threshold:
                return Fraction(1)
            if count == threshold:
                return gamma
            return Fraction()
        values = []
        for action in actions:
            q = report_probability(theta, coverage_count, action)
            values.append((1 - q) * recurse(step + 1, count) + q * recurse(step + 1, count + 1))
        return chooser(values)

    return recurse(0, 0)


def iid_upper_tail_value(
    horizon: int, q: Fraction, threshold: int, gamma: Fraction
) -> Fraction:
    value = Fraction()
    for count in range(horizon + 1):
        terminal = Fraction(1) if count > threshold else gamma if count == threshold else Fraction()
        value += (
            math.comb(horizon, count)
            * q**count
            * (1 - q) ** (horizon - count)
            * terminal
        )
    return value


def oracle_row(
    witness: dict[str, Any], threshold: int, gamma: Fraction, objective: str
) -> dict[str, Any]:
    theta = exact_fraction(witness["theta"])
    coverage_count = witness["coverage_count"]
    agreement_count = 8 if objective == "max" else witness["k1"]
    lower, upper = action_interval(agreement_count, coverage_count)
    endpoint = upper if objective == "max" else lower
    q = report_probability(theta, coverage_count, endpoint)
    full = full_prefix_bellman_value(
        3,
        agreement_count,
        coverage_count,
        theta,
        threshold,
        gamma,
        objective,
    )
    count = count_state_bellman_value(
        3,
        agreement_count,
        coverage_count,
        theta,
        threshold,
        gamma,
        objective,
    )
    iid = iid_upper_tail_value(3, q, threshold, gamma)
    return {
        "witness_id": witness["id"],
        "threshold": threshold,
        "gamma": fraction_text(gamma),
        "objective": objective,
        "effective_agreement_count": agreement_count,
        "coverage_count": coverage_count,
        "theta": fraction_text(theta),
        "action_interval": [lower, upper],
        "endpoint_action": endpoint,
        "endpoint_q": fraction_text(q),
        "full_prefix_bellman": fraction_text(full),
        "count_state_bellman": fraction_text(count),
        "constant_iid_endpoint": fraction_text(iid),
        "all_values_equal": full == count == iid,
    }


def build_oracle_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    oracle = manifest["registry"]["oracle"]
    if oracle.get("horizon") != 3:
        raise ValueError("oracle horizon is not frozen at three")
    return [
        oracle_row(witness, threshold, gamma, objective)
        for witness in oracle["witnesses"]
        for threshold in FROZEN_THRESHOLDS
        for gamma in FROZEN_GAMMAS
        for objective in FROZEN_OBJECTIVES
    ]


def build_analytic_obligations(
    quotient_rows: Sequence[dict[str, Any]],
    registry_rows: Sequence[dict[str, Any]],
    resource_guard: Callable[[], None] | None = None,
    progress_callback: Callable[[], None] | None = None,
) -> dict[str, Any]:
    action_quotient = len(quotient_rows) == 72 and all(
        all(row["checks"].values()) for row in quotient_rows
    )
    q_monotone_in_action = all(
        report_probability(theta, coverage_count, action)
        <= report_probability(theta, coverage_count, action + 1)
        for theta in FROZEN_THETA_VALUES
        for agreement_count in range(17)
        for coverage_count in FROZEN_C_VALUES
        for action in range(*(
            lambda bounds: (bounds[0], bounds[1])
        )(action_interval(agreement_count, coverage_count)))
    )
    composite_monotonicity = all(
        endpoint_probabilities(k, coverage_count, theta)[index]
        <= endpoint_probabilities(k + 1, coverage_count, theta)[index]
        for theta in FROZEN_THETA_VALUES
        for coverage_count in FROZEN_C_VALUES
        for k in range(16)
        for index in (0, 1)
    )
    registry_transfer = len(registry_rows) == 48 and all(
        row["all_checks_pass"] for row in registry_rows
    )
    generic_census = generic_h3_terminal_census(resource_guard, progress_callback)
    generic_census_pass = generic_census == {
        "horizon": 3,
        "monotone_boolean_terminal_count": 20,
        "nonsymmetric_terminal_count": 15,
        "registered_action_law_comparisons": 11520,
        "all_values_equal": True,
    }
    return {
        "generic_terminal_census": generic_census,
        "full_history_induction": {
            "terminal_coordinatewise_monotonicity_is_the_only_phi_premise": True,
            "continuation_difference_is_nonnegative_by_backward_induction": True,
            "bellman_action_value_is_affine_in_q": True,
            "q_is_nondecreasing_in_action_for_theta_at_least_half": q_monotone_in_action,
            "constant_endpoint_masks_exist": action_quotient,
            "private_randomized_policies_are_convex_mixtures": True,
            "claim_horizon_is_deterministic_finite_0_to_8192": True,
            "all_h3_monotone_boolean_terminals_include_nonsymmetric_cases": generic_census_pass,
        },
        "composite_and_minimality": {
            "both_endpoint_laws_are_nondecreasing_in_k": composite_monotonicity,
            "worst_compliant_boundary_is_k8": composite_monotonicity,
            "worst_forbidden_boundary_is_k1": composite_monotonicity,
            "all_48_upstream_status_and_predecessor_certificates_transfer": registry_transfer,
            "constant_endpoint_masks_supply_the_lower_bound": action_quotient,
        },
        "all_obligations_pass": bool(
            action_quotient
            and q_monotone_in_action
            and composite_monotonicity
            and registry_transfer
            and generic_census_pass
        ),
    }


def build_controls(
    quotient_rows: Sequence[dict[str, Any]], registry_rows: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    causal_q0 = report_probability(Fraction(1), 12, action_interval(8, 12)[1])
    causal_q1 = report_probability(Fraction(1), 12, action_interval(14, 12)[0])
    anticipatory_q0 = Fraction(8, 16) * 1 + Fraction(8, 16) * Fraction(1, 2)
    anticipatory_q1 = Fraction(2, 16) * 0 + Fraction(14, 16) * Fraction(1, 2)

    lower, upper = action_interval(8, 12)
    qs = [report_probability(Fraction(1), 12, action) for action in range(lower, upper + 1)]
    adaptive = max(
        (1 - first) * after_zero + first * (1 - after_one)
        for first in qs
        for after_zero in qs
        for after_one in qs
    )
    fixed = max(2 * q * (1 - q) for q in qs)

    theta_half_null = all(
        report_probability(Fraction(1, 2), coverage_count, action) == Fraction(1, 2)
        for agreement_count in range(17)
        for coverage_count in FROZEN_C_VALUES
        for action in range(action_interval(agreement_count, coverage_count)[0], action_interval(agreement_count, coverage_count)[1] + 1)
    )
    zero_coverage_null = all(
        report_probability(theta, 0, 0) == Fraction(1, 2)
        for theta in FROZEN_THETA_VALUES
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
            "registered_pairs": len(quotient_rows),
            "pass": len(quotient_rows) == 72
            and all(all(row["checks"].values()) for row in quotient_rows),
        },
        "input_relabeling": {
            "permutation": [(5 * point + 3) % 16 for point in range(16)],
            "pass": all(row["checks"]["relabel_invariant"] for row in quotient_rows),
        },
        "v0_3_all_selective_records": {
            "registered_rows": len(registry_rows),
            "pass": len(registry_rows) == 48
            and all(row["all_checks_pass"] for row in registry_rows),
        },
        "theta_half_zero_coverage_full_coverage": {
            "theta_half_is_blind": theta_half_null,
            "zero_coverage_is_blind": zero_coverage_null,
            "full_coverage_has_single_action_for_every_k": all(
                action_interval(k, 16) == (k, k) for k in range(17)
            ),
            "pass": theta_half_null
            and zero_coverage_null
            and all(action_interval(k, 16) == (k, k) for k in range(17)),
        },
    }


def build_metric_robustness(
    oracle_rows: Sequence[dict[str, Any]], controls: dict[str, Any]
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
            "registered_rows": len(oracle_rows),
            "pass": len(oracle_rows) == 144
            and all(row["all_values_equal"] for row in oracle_rows),
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


def _downgraded_layers() -> dict[str, str]:
    return {
        "metric_robustness": "not_established",
        "task_result": "not_established",
        "measurement_reliability": "failed",
        "claim_support": "none",
        "operational_decision": "no_deployment_authorization_repair",
    }


def _resource_check(
    start_ns: int,
    wall_limit_ns: int,
    traced_limit_bytes: int,
    clock_ns: Callable[[], int],
) -> None:
    if clock_ns() - start_ns > wall_limit_ns:
        raise ResourceStop("wall_limit_after_completed_stage")
    _, peak = tracemalloc.get_traced_memory()
    if peak > traced_limit_bytes:
        raise ResourceStop("traced_python_memory_limit_after_completed_stage")


def compile_result(
    manifest: dict[str, Any],
    source_binding: dict[str, Any],
    *,
    clock_ns: Callable[[], int] = time.monotonic_ns,
) -> dict[str, Any]:
    manifest_checks = validate_manifest_binding(manifest)
    upstream_bindings = validate_upstream_bindings(manifest)
    start_ns = clock_ns()
    wall_limit_ns = manifest["budget"]["max_wall_seconds"] * 1_000_000_000
    traced_limit_bytes = manifest["budget"]["max_traced_python_mib"] * 1024 * 1024
    owned_trace = not tracemalloc.is_tracing()
    if owned_trace:
        tracemalloc.start()
    tracemalloc.reset_peak()

    quotient_rows: list[dict[str, Any]] = []
    registry_rows: list[dict[str, Any]] = []
    oracle_rows: list[dict[str, Any]] = []
    analytic_obligations: dict[str, Any] = {}
    controls: dict[str, Any] = {}
    metric_robustness: dict[str, dict[str, Any]] = {}
    completed_generic_terminal_comparisons = 0
    status = "complete"
    stop_reason = "registered_contract_complete"

    def record_generic_comparison() -> None:
        nonlocal completed_generic_terminal_comparisons
        completed_generic_terminal_comparisons += 1

    try:
        bound = _v03_selective_map(upstream_v03_result(manifest))
        for k1 in FROZEN_K1_VALUES:
            for theta in FROZEN_THETA_VALUES:
                for coverage_count in FROZEN_C_VALUES:
                    _resource_check(
                        start_ns, wall_limit_ns, traced_limit_bytes, clock_ns
                    )
                    registry_rows.append(
                        registry_row(bound, k1, theta, coverage_count)
                    )
                    _resource_check(
                        start_ns, wall_limit_ns, traced_limit_bytes, clock_ns
                    )
        for agreement_count in FROZEN_K_VALUES:
            for coverage_count in FROZEN_C_VALUES:
                _resource_check(
                    start_ns, wall_limit_ns, traced_limit_bytes, clock_ns
                )
                quotient_rows.append(
                    quotient_row(agreement_count, coverage_count)
                )
                _resource_check(
                    start_ns, wall_limit_ns, traced_limit_bytes, clock_ns
                )
        oracle = manifest["registry"]["oracle"]
        for witness in oracle["witnesses"]:
            for threshold in FROZEN_THRESHOLDS:
                for gamma in FROZEN_GAMMAS:
                    for objective in FROZEN_OBJECTIVES:
                        _resource_check(
                            start_ns, wall_limit_ns, traced_limit_bytes, clock_ns
                        )
                        oracle_rows.append(
                            oracle_row(witness, threshold, gamma, objective)
                        )
                        _resource_check(
                            start_ns, wall_limit_ns, traced_limit_bytes, clock_ns
                        )
        analytic_obligations = build_analytic_obligations(
            quotient_rows,
            registry_rows,
            lambda: _resource_check(
                start_ns, wall_limit_ns, traced_limit_bytes, clock_ns
            ),
            record_generic_comparison,
        )
        controls = build_controls(quotient_rows, registry_rows)
        metric_robustness = build_metric_robustness(oracle_rows, controls)
        _resource_check(start_ns, wall_limit_ns, traced_limit_bytes, clock_ns)
    except ResourceStop as error:
        status = "stopped_resource"
        stop_reason = str(error)

    elapsed_wall_ns = clock_ns() - start_ns
    _, traced_peak_bytes = tracemalloc.get_traced_memory()
    if owned_trace:
        tracemalloc.stop()

    source_binding_valid = bool(
        source_binding.get("source_commit_type") == "commit"
        and source_binding.get("source_commit_is_ancestor_of_head") is True
        and tuple(sorted(source_binding.get("source_files", {})))
        == FROZEN_SOURCE_FILES
    )
    upstream_valid = all(
        record.get("all_hashes_match") is True
        for record in upstream_bindings.values()
    )
    gates = {
        "G0_frozen_manifest_binding": all(manifest_checks.values()),
        "G1_exact_source_and_upstream_bindings": source_binding_valid
        and upstream_valid,
        "G2_complete_72_pair_mask_quotient": status == "complete"
        and len(quotient_rows) == 72
        and all(all(row["checks"].values()) for row in quotient_rows),
        "G3_complete_48_row_v03_transfer": status == "complete"
        and len(registry_rows) == 48
        and all(row["all_checks_pass"] for row in registry_rows),
        "G4_complete_144_row_monotone_oracle": status == "complete"
        and len(oracle_rows) == 144
        and all(row["all_values_equal"] for row in oracle_rows),
        "G5_analytic_induction_and_composite_obligations": status == "complete"
        and analytic_obligations.get("all_obligations_pass") is True,
        "G6_scope_breakers_and_simple_limits": status == "complete"
        and bool(controls)
        and all(record["pass"] for record in controls.values()),
        "G7_five_metric_probe_families": status == "complete"
        and tuple(metric_robustness) == FROZEN_PROBE_IDS
        and all(record["pass"] for record in metric_robustness.values()),
        "G8_exact_arithmetic_and_resource_envelope": status == "complete"
        and elapsed_wall_ns <= wall_limit_ns
        and traced_peak_bytes <= traced_limit_bytes
        and completed_generic_terminal_comparisons == 11520
        and not contains_float(
            {
                "quotient": quotient_rows,
                "registry": registry_rows,
                "oracle": oracle_rows,
                "analytic": analytic_obligations,
                "controls": controls,
            }
        ),
    }
    passed = status == "complete" and all(gates.values())
    layers = dict(FROZEN_PREVERIFICATION_LAYERS) if passed else _downgraded_layers()
    result = {
        "schema_version": "asmp7_causal_adaptive_suppression_result_v0_4",
        "protocol_id": FROZEN_PROTOCOL_ID,
        "manifest_sha256": FROZEN_MANIFEST_CANONICAL_SHA256,
        "source_binding": source_binding,
        "upstream_bindings": upstream_bindings,
        "resource_observations": {
            "canonical_result_bytes": 0,
            "completed_quotient_rows": len(quotient_rows),
            "completed_registry_rows": len(registry_rows),
            "completed_oracle_rows": len(oracle_rows),
            "completed_generic_terminal_comparisons": completed_generic_terminal_comparisons,
            "elapsed_wall_ns": elapsed_wall_ns,
            "traced_python_peak_bytes": traced_peak_bytes,
            "traced_python_limit_bytes": traced_limit_bytes,
            "wall_limit_ns": wall_limit_ns,
            "memory_measurement": "tracemalloc_peak_python_allocation_only",
            "process_rss_and_native_memory_measured": False,
        },
        "status": status,
        "stop_reason": stop_reason,
        "quotient_rows": quotient_rows,
        "registry_rows": registry_rows,
        "oracle_rows": oracle_rows,
        "analytic_obligations": analytic_obligations,
        "controls": controls,
        "gates": gates,
        "metric_robustness": metric_robustness,
        "conclusion_layers": layers,
        "claim_boundary": list(manifest["claim_boundary"]),
    }
    if set(result) != FROZEN_RESULT_FIELDS:
        raise AssertionError("result field universe changed")
    if tuple(gates) != FROZEN_PRIMARY_GATES or contains_float(result):
        raise AssertionError("gate universe or exact arithmetic changed")
    for _ in range(10):
        actual_size = len(canonical_json(result).encode("utf-8"))
        if result["resource_observations"]["canonical_result_bytes"] == actual_size:
            break
        result["resource_observations"]["canonical_result_bytes"] = actual_size
    else:
        raise AssertionError("canonical result byte-count fixed point failed")
    return result


def _is_reparse_point(path: Path) -> bool:
    metadata = path.lstat()
    attributes = getattr(metadata, "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return path.is_symlink() or bool(attributes & flag)


def live_source_inventory_checks(
    directory: Path = HERE,
    source_files: Sequence[str] = FROZEN_SOURCE_FILES,
) -> dict[str, Any]:
    expected = set(source_files)
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
    for filename in sorted(expected & set(entries)):
        path = entries[filename]
        try:
            if _is_reparse_point(path) or not path.is_file():
                invalid.append(filename)
        except OSError:
            invalid.append(filename)
    return {
        "pass": not (directory_reparse or missing or unexpected or invalid),
        "directory_error": "",
        "directory_reparse": directory_reparse,
        "missing": missing,
        "unexpected": unexpected,
        "invalid_source_entries": invalid,
    }


def validate_live_source_inventory(directory: Path = HERE) -> dict[str, Any]:
    checks = live_source_inventory_checks(directory)
    if not checks["pass"]:
        raise ValueError(f"live source inventory failed: {checks}")
    return checks


def source_commit_binding(source_commit: str) -> dict[str, Any]:
    validate_live_source_inventory()
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("source commit must be a full lowercase 40-hex commit")
    root = repo_root()
    if str(_git(["cat-file", "-t", source_commit], text=True, cwd=root)) != "commit":
        raise ValueError("source object is not a commit")
    resolved = str(
        _git(["rev-parse", "--verify", f"{source_commit}^{{commit}}"], text=True, cwd=root)
    )
    if resolved != source_commit:
        raise ValueError("source commit did not resolve exactly")
    ancestry = subprocess.run(
        [GIT_EXECUTABLE, "merge-base", "--is-ancestor", source_commit, "HEAD"],
        cwd=root,
        env={
            **{
                key: value
                for key, value in os.environ.items()
                if not key.startswith("GIT_")
            },
            "GIT_NO_REPLACE_OBJECTS": "1",
        },
    )
    if ancestry.returncode != 0:
        raise ValueError("source commit is not an ancestor of HEAD")
    relative_directory = HERE.relative_to(root)
    directory_path = relative_directory.as_posix()
    listed = str(
        _git(
            ["ls-tree", "-r", "--name-only", source_commit, "--", directory_path],
            text=True,
            cwd=root,
        )
    )
    listed_paths = {line for line in listed.splitlines() if line}
    expected_paths = {
        (relative_directory / filename).as_posix() for filename in FROZEN_SOURCE_FILES
    }
    if listed_paths != expected_paths:
        raise ValueError("source commit directory is not the exact frozen eight-file set")
    hashes: dict[str, dict[str, str]] = {}
    mismatches = []
    for filename in FROZEN_SOURCE_FILES:
        relative_path = (relative_directory / filename).as_posix()
        tree_line = str(
            _git(["ls-tree", source_commit, "--", relative_path], text=True, cwd=root)
        )
        try:
            metadata, listed_path = tree_line.split("\t", 1)
            mode, kind, blob_oid = metadata.split()
        except ValueError as error:
            raise ValueError(f"malformed Git tree entry: {filename}") from error
        if listed_path != relative_path or mode != "100644" or kind != "blob":
            raise ValueError(f"source entry is not a regular blob: {filename}")
        committed = bytes(
            _git(
                ["show", f"{source_commit}:{relative_path}"],
                text=False,
                cwd=root,
            )
        )
        current = (HERE / filename).read_bytes()
        current_oid = subprocess.run(
            [GIT_EXECUTABLE, "hash-object", "--stdin"],
            cwd=root,
            env={
                **{
                    key: value
                    for key, value in os.environ.items()
                    if not key.startswith("GIT_")
                },
                "GIT_NO_REPLACE_OBJECTS": "1",
            },
            check=True,
            input=current,
            capture_output=True,
        ).stdout.decode("ascii").strip()
        hashes[filename] = {
            "git_blob_oid": current_oid,
            "sha256": sha256_bytes(current),
        }
        if current_oid != blob_oid or current != committed:
            mismatches.append(filename)
    if mismatches:
        raise ValueError(f"working source differs from commit: {sorted(mismatches)}")
    return {
        "repo_relative_directory": directory_path,
        "source_commit": source_commit,
        "source_commit_is_ancestor_of_head": True,
        "source_commit_type": "commit",
        "source_files": hashes,
    }


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
        raise ValueError(f"cannot inspect artifact destination component: {path}") from error


def _require_safe_directory(path: Path, metadata: os.stat_result) -> None:
    if _is_reparse_point(path):
        raise ValueError(f"artifact destination contains reparse point: {path}")
    if not stat.S_ISDIR(metadata.st_mode):
        raise NotADirectoryError(f"artifact destination ancestor is not a directory: {path}")


def _prepare_write_once_destination(path: Path) -> Path:
    destination = _absolute_without_reparse_resolution(path)
    chain = _destination_chain(destination)
    for component in chain[:-1]:
        metadata = _lstat_optional(component)
        if metadata is None:
            try:
                component.mkdir()
            except OSError as error:
                raise ValueError(f"cannot create artifact directory: {component}") from error
            metadata = _lstat_optional(component)
            if metadata is None:
                raise ValueError(f"artifact directory vanished: {component}")
        _require_safe_directory(component, metadata)
    output_metadata = _lstat_optional(destination)
    if output_metadata is not None:
        if _is_reparse_point(destination):
            raise ValueError(f"artifact output is a reparse point: {destination}")
        raise FileExistsError(f"artifact destination already exists: {destination}")
    for component in chain[:-1]:
        metadata = _lstat_optional(component)
        if metadata is None:
            raise ValueError(f"artifact ancestor vanished: {component}")
        _require_safe_directory(component, metadata)
    return destination


def write_once_json(path: Path, value: Any, max_bytes: int = 1048576) -> None:
    payload = canonical_json(value).encode("utf-8")
    if len(payload) > max_bytes:
        raise ResourceStop("artifact_byte_ceiling")
    destination = _prepare_write_once_destination(path)
    with destination.open("xb") as stream:
        stream.write(payload)
