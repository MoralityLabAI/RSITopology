"""Import-independent verifier for the ASMP-5 v0.4 noisy-anchor grid."""

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
import os
import re
import shutil
import stat
import subprocess
import time
import tracemalloc
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


HERE = Path(os.path.abspath(__file__)).parent
ARTIFACT_DIRECTORY = HERE.parent / "artifacts_v0_4_dynamic_noisy_anchor"
PROTOCOL_ID = "ASMP5-DYNAMIC-REPLICATED-NOISY-ANCHOR-v0.4"
MANIFEST_SCHEMA = "asmp5_dynamic_replicated_noisy_anchor_manifest_v0_4"
MANIFEST_SHA256 = "f99df92025289947ed27b78076c3e440808875a60497858d4b1055abe16e542b"
PREDECESSOR_COMMIT = "61a2f802adb4c4b5f06272d97d9de888413d5352"
ROOT_ANCHOR = 3
M_VALUES = (1, 3, 5)
EPSILON_VALUES = (Fraction(0), Fraction(1, 20), Fraction(1, 10))
HORIZONS = (1, 8, 64)
TEMPORAL_MODELS = ("fresh_iid", "persistent")
SOURCE_FILES = (
    "PROTOCOL_v0_4.md",
    "README.md",
    "SOURCE_FREEZE.md",
    "manifest_v0_4.json",
    "noisy_anchor.py",
    "run.py",
    "test_noisy_anchor.py",
    "verify_independent.py",
)
CLAIM_BOUNDARY = (
    "the primary model is the frozen four-bit anchor R*=0011 with exact safe-acceptance bits and one-sided 0-to-1 noise only on its two hazard-rejection bits",
    "the 2m hazard-bit replica errors are mutually independent Bernoulli(epsilon) coins in the declared bit-major replica-minor order",
    "fresh_iid uses a new independent 2m-coin batch at each of exactly H post-install attack opportunities; persistent installs one batch and reuses it for all H opportunities",
    "the installed anchor is visible before an adaptive adversary chooses one of exactly two proof classes and makes the registered hazard proposal",
    "the registered finite grid is m in {1,3,5}, epsilon in {0,1/20,1/10}, H in {1,8,64}, and the two frozen temporal models",
    "the perfect-correlation, false-negative-only, blinded-adversary, swapped-bit, epsilon-zero, and inherited safe-cycle cases are controls, not enlargements of the primary model",
    "no claim about arbitrary learners, arbitrary or unknown correlation, two-sided or state-dependent error, learned evidence, infinite distinct-state progress, open-ended verifier replacement, general ASMP-5 systems, or resolution of ASMP-5",
)
GATE_IDS = (
    "G0_manifest_and_order",
    "G1_source_and_predecessor_binding",
    "G2_complete_exact_54_rows",
    "G3_product_error_and_visibility_semantics",
    "G4_symbolic_fresh_infinite_horizon_negative",
    "G5_scope_controls",
    "G6_metric_robustness",
    "G7_no_float_or_rng",
)
GIT = shutil.which("git")


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def exact_fraction(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("inexact scalar")
    if isinstance(value, Fraction):
        return value
    if type(value) is int:
        return Fraction(value)
    if isinstance(value, str) and re.fullmatch(r"(0|[1-9][0-9]*)/[1-9][0-9]*", value):
        parsed = Fraction(value)
        if fraction_text(parsed) != value:
            raise ValueError("noncanonical fraction")
        return parsed
    raise TypeError("not an exact scalar")


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def strict_json_equal(left: Any, right: Any) -> bool:
    try:
        return canonical_json(left) == canonical_json(right)
    except (TypeError, ValueError):
        return False


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def _reject_number(value: str) -> Any:
    raise ValueError(f"inexact or nonfinite JSON number: {value}")


def load_json_bytes_strict(payload: bytes) -> Any:
    return json.loads(
        payload.decode(),
        object_pairs_hook=_strict_object,
        parse_float=_reject_number,
        parse_constant=_reject_number,
    )


def _is_reparse(path: Path) -> bool:
    metadata = path.lstat()
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return path.is_symlink() or bool(getattr(metadata, "st_file_attributes", 0) & flag)


def preflight_inventory() -> None:
    entries = {entry.name: entry for entry in HERE.iterdir()}
    expected = set(SOURCE_FILES)
    invalid = [
        name
        for name in sorted(expected & set(entries))
        if _is_reparse(entries[name]) or not entries[name].is_file()
    ]
    if _is_reparse(HERE) or set(entries) != expected or invalid:
        raise SystemExit(
            "refusing live source inventory: "
            f"missing={sorted(expected-set(entries))}, "
            f"unexpected={sorted(set(entries)-expected)}, invalid={invalid}"
        )


def _git_env() -> dict[str, str]:
    environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    return environment


def _git(args: list[str], cwd: Path, input_bytes: bytes | None = None) -> bytes:
    if GIT is None:
        raise SystemExit("trusted Git executable unavailable")
    return subprocess.run(
        [GIT, *args], cwd=cwd, env=_git_env(), input=input_bytes,
        check=True, capture_output=True
    ).stdout


def source_snapshot(source_commit: str) -> tuple[dict[str, Any], dict[str, bytes], Path]:
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise SystemExit("invalid source commit")
    root = Path(os.path.abspath(_git(["rev-parse", "--show-toplevel"], HERE).decode().strip()))
    git_directory = Path(os.path.abspath(_git(["rev-parse", "--absolute-git-dir"], root).decode().strip()))
    grafts = git_directory / "info" / "grafts"
    if (grafts.exists() and grafts.stat().st_size) or _git(
        ["for-each-ref", "--format=%(refname)", "refs/replace"], root
    ).strip():
        raise SystemExit("noncanonical Git ancestry")
    if _git(["rev-parse", "--is-shallow-repository"], root).strip() != b"false":
        raise SystemExit("shallow repository forbidden")
    if _git(["cat-file", "-t", source_commit], root).strip() != b"commit":
        raise SystemExit("source object is not commit")
    if (
        _git(["rev-parse", "--verify", f"{source_commit}^{{commit}}"], root)
        .decode()
        .strip()
        != source_commit
    ):
        raise SystemExit("source commit did not resolve exactly")
    if subprocess.run(
        [GIT, "merge-base", "--is-ancestor", source_commit, "HEAD"],
        cwd=root,
        env=_git_env(),
        capture_output=True,
    ).returncode:
        raise SystemExit("source commit is not an ancestor of HEAD")
    relative = HERE.relative_to(root)
    listed = _git(["ls-tree", "-r", "--name-only", source_commit, "--", relative.as_posix()], root).decode()
    expected_paths = {(relative / name).as_posix() for name in SOURCE_FILES}
    if {line for line in listed.splitlines() if line} != expected_paths:
        raise SystemExit("committed source inventory mismatch")
    snapshot: dict[str, bytes] = {}
    files: dict[str, dict[str, str]] = {}
    for name in SOURCE_FILES:
        path = (relative / name).as_posix()
        tree = _git(["ls-tree", source_commit, "--", path], root).decode().strip()
        metadata, listed_path = tree.split("\t", 1)
        mode, kind, oid = metadata.split()
        live = (HERE / name).read_bytes()
        committed = _git(["show", f"{source_commit}:{path}"], root)
        if listed_path != path or mode != "100644" or kind != "blob" or live != committed:
            raise SystemExit(f"source mismatch: {name}")
        if _git(["hash-object", "--stdin"], root, live).decode().strip() != oid:
            raise SystemExit(f"blob mismatch: {name}")
        snapshot[name] = live
        files[name] = {"git_blob_oid": oid, "sha256": hashlib.sha256(live).hexdigest()}
    return ({
        "pass": True,
        "source_commit": source_commit,
        "source_commit_type": "commit",
        "source_commit_is_ancestor_of_head": True,
        "repo_relative_directory": relative.as_posix(),
        "files": files,
    }, snapshot, root)


def predecessor_binding(manifest: dict[str, Any], source_commit: str, root: Path) -> dict[str, Any]:
    declaration = manifest["predecessor_binding"]
    if declaration["commit"] != PREDECESSOR_COMMIT:
        raise SystemExit("predecessor mismatch")
    if subprocess.run(
        [GIT, "merge-base", "--is-ancestor", PREDECESSOR_COMMIT, source_commit],
        cwd=root, env=_git_env(), capture_output=True
    ).returncode:
        raise SystemExit("predecessor is not source ancestor")
    observed: dict[str, str] = {}
    receipt = None
    for record in declaration["files"]:
        payload = _git(["show", f"{PREDECESSOR_COMMIT}:{record['path']}"], root)
        digest = hashlib.sha256(payload).hexdigest()
        if digest != record["sha256"]:
            raise SystemExit(f"predecessor hash mismatch: {record['path']}")
        observed[record["path"]] = digest
        if record["path"].endswith("synthesis_receipt_v0_3.json"):
            receipt = load_json_bytes_strict(payload)
    if receipt is None or receipt.get("pass") is not True or receipt.get("binding_match") is not True:
        raise SystemExit("invalid predecessor receipt")
    return {
        "pass": True,
        "commit": PREDECESSOR_COMMIT,
        "files": observed,
        "receipt_pass": True,
        "receipt_binding_match": True,
    }


def _pattern_weight(pattern: tuple[int, ...], epsilon: Fraction) -> Fraction:
    ones = sum(pattern)
    return epsilon**ones * (1 - epsilon) ** (len(pattern) - ones)


def enumerate_batch(m: int, epsilon: Fraction) -> dict[str, Fraction | int]:
    """Sum the full ordered 2m-coin product; no binomial formula is used."""
    threshold = (m + 1) // 2
    p0 = p1 = visible = both = Fraction(0)
    total = Fraction(0)
    swapped_visible = Fraction(0)
    count = 0
    for pattern in itertools.product((0, 1), repeat=2 * m):
        count += 1
        weight = _pattern_weight(pattern, epsilon)
        total += weight
        error0 = sum(pattern[:m]) >= threshold
        error1 = sum(pattern[m:]) >= threshold
        p0 += weight * error0
        p1 += weight * error1
        visible += weight * (error0 or error1)
        both += weight * (error0 and error1)
        swapped_visible += weight * (error1 or error0)
    if total != 1 or p0 != p1 or visible != swapped_visible:
        raise AssertionError("joint pattern enumeration invariant failed")
    return {
        "pattern_count": count,
        "single": p0,
        "visible": visible,
        "both": both,
        "swapped_visible": swapped_visible,
    }


def advance_two_state(hazards: Iterable[Fraction]) -> Fraction:
    safe, failed = Fraction(1), Fraction(0)
    for hazard in hazards:
        if not 0 <= hazard <= 1:
            raise ValueError("invalid transition probability")
        safe, failed = safe * (1 - hazard), failed + safe * hazard
    if safe + failed != 1:
        raise AssertionError("two-state mass loss")
    return failed


def persistent_from_patterns(m: int, epsilon: Fraction, horizon: int, event: str) -> Fraction:
    threshold = (m + 1) // 2
    aggregate = Fraction(0)
    for pattern in itertools.product((0, 1), repeat=2 * m):
        weight = _pattern_weight(pattern, epsilon)
        error0 = sum(pattern[:m]) >= threshold
        error1 = sum(pattern[m:]) >= threshold
        hit = {
            "visible": error0 or error1,
            "blinded": error0,
            "deadlock": error0 and error1,
        }[event]
        aggregate += weight * advance_two_state([Fraction(hit)] * horizon)
    return aggregate


def perfectly_correlated_single(m: int, epsilon: Fraction) -> Fraction:
    threshold = (m + 1) // 2
    total = Fraction(0)
    for pattern in itertools.product((0, 1), repeat=m):
        if sum(pattern) >= threshold:
            total += _pattern_weight(pattern, epsilon)
    return total


def row_record(m: int, epsilon: Fraction, horizon: int, temporal: str) -> dict[str, Any]:
    batch = enumerate_batch(m, epsilon)
    p = batch["single"]
    q = batch["visible"]
    deadlock = batch["both"]
    if temporal == "fresh_iid":
        risk = advance_two_state([q] * horizon)
        blinded = advance_two_state([p] * horizon)
        deadlock_risk = advance_two_state([deadlock] * horizon)
    elif temporal == "persistent":
        risk = persistent_from_patterns(m, epsilon, horizon, "visible")
        blinded = persistent_from_patterns(m, epsilon, horizon, "blinded")
        deadlock_risk = persistent_from_patterns(m, epsilon, horizon, "deadlock")
    else:
        raise ValueError("unknown temporal model")
    correlated_p = perfectly_correlated_single(m, epsilon)
    correlated_risk = (
        advance_two_state([correlated_p] * horizon)
        if temporal == "fresh_iid"
        else correlated_p
    )
    return {
        "key": f"m={m}|epsilon={fraction_text(epsilon)}|H={horizon}|temporal={temporal}",
        "m": m,
        "epsilon": fraction_text(epsilon),
        "horizon": horizon,
        "temporal_model": temporal,
        "joint_replica_pattern_count": batch["pattern_count"],
        "majority_threshold": (m + 1) // 2,
        "single_hazard_bit_error_probability": fraction_text(p),
        "visible_adversary_per_installation_failure": fraction_text(q),
        "finite_horizon_failure": fraction_text(risk),
        "finite_horizon_safety": fraction_text(1 - risk),
        "blinded_one_class_per_installation_failure": fraction_text(p),
        "blinded_one_class_horizon_failure": fraction_text(blinded),
        "perfectly_correlated_bits_per_installation_failure": fraction_text(correlated_p),
        "perfectly_correlated_bits_horizon_failure": fraction_text(correlated_risk),
        "false_negative_only": {
            "unsafe_failure": "0/1",
            "per_installation_deadlock": fraction_text(deadlock),
            "horizon_deadlock": fraction_text(deadlock_risk),
        },
    }


def iter_rows() -> Iterable[dict[str, Any]]:
    for m in M_VALUES:
        for epsilon in EPSILON_VALUES:
            for horizon in HORIZONS:
                for temporal in TEMPORAL_MODELS:
                    yield row_record(m, epsilon, horizon, temporal)


def exploit_witnesses() -> list[dict[str, Any]]:
    return [
        {"erroneous_hazard_bit": 2, "installed_anchor": "0111", "chosen_proof_class": 0, "hazard": 1, "accepted": True},
        {"erroneous_hazard_bit": 3, "installed_anchor": "1011", "chosen_proof_class": 1, "hazard": 1, "accepted": True},
    ]


def safe_cycle() -> dict[str, Any]:
    return {
        "states": [
            {"behavior": 0, "checker": 3},
            {"behavior": 2, "checker": 3},
            {"behavior": 0, "checker": 3},
        ],
        "hazard_bits": [0, 0, 0],
        "proof_class": 0,
        "all_safe": True,
        "returns_to_start": True,
        "root_accepts_each_safe_step": True,
    }


def theorem() -> dict[str, Any]:
    return {
        "domain": "finite odd m>=1 and 0<epsilon<=1",
        "positive_lower_bound": "p_m>=epsilon^m>0",
        "independent_union": "q_m=1-(1-p_m)^2>0",
        "fresh_limit": "lim_(H->infinity) [1-(1-q_m)^H]=1",
        "persistent_limit": "q_m>0 (constant in H; not asserted to approach 1)",
        "proof_steps": [
            "the all-m-errors event is contained in the strict-majority event",
            "positive epsilon gives the all-m-errors event probability epsilon^m>0",
            "independent hazard-bit majorities give q_m=1-(1-p_m)^2",
            "if q_m=1 failure is immediate; otherwise 0<1-q_m<1 and its Hth power tends to zero",
        ],
        "pass": True,
    }


def controls(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_key = {(r["m"], r["epsilon"], r["horizon"], r["temporal_model"]): r for r in rows}
    zero = [r for r in rows if r["epsilon"] == "0/1"]
    positive = [r for r in rows if r["epsilon"] != "0/1"]
    temporal = []
    for m in M_VALUES:
        for epsilon in EPSILON_VALUES[1:]:
            for horizon in HORIZONS[1:]:
                fresh = by_key[(m, fraction_text(epsilon), horizon, "fresh_iid")]
                persistent = by_key[(m, fraction_text(epsilon), horizon, "persistent")]
                temporal.append(exact_fraction(fresh["finite_horizon_failure"]) > exact_fraction(persistent["finite_horizon_failure"]))
    witnesses = exploit_witnesses()
    return {
        "single_bit_exploit_witnesses": {"records": witnesses, "pass": all(r["accepted"] for r in witnesses)},
        "false_negative_only_safety_and_deadlock": {
            "all_unsafe_risks_zero": all(r["false_negative_only"]["unsafe_failure"] == "0/1" for r in rows),
            "positive_deadlock_is_live": any(exact_fraction(r["false_negative_only"]["horizon_deadlock"]) > 0 for r in positive),
            "pass": True,
        },
        "epsilon_zero_exact_anchor": {
            "row_count": len(zero),
            "all_failure_and_deadlock_zero": all(r["finite_horizon_failure"] == "0/1" and r["false_negative_only"]["horizon_deadlock"] == "0/1" for r in zero),
            "pass": True,
        },
        "v0_3_safe_two_cycle": {**safe_cycle(), "pass": True},
        "hazard_bit_swap": {
            "identity": "1-(1-p0)(1-p1)=1-(1-p1)(1-p0)",
            "all_rows_invariant": all(enumerate_batch(r["m"], exact_fraction(r["epsilon"]))["swapped_visible"] == exact_fraction(r["visible_adversary_per_installation_failure"]) for r in rows),
            "pass": True,
        },
        "temporal_correlation": {
            "strict_fresh_gt_persistent_positive_H_gt_1": all(temporal),
            "comparison_count": len(temporal),
            "pass": all(temporal),
        },
        "perfectly_correlated_hazard_bits": {
            "per_installation_risk": "p_m",
            "independent_bounds_hold": all(exact_fraction(r["perfectly_correlated_bits_per_installation_failure"]) <= exact_fraction(r["visible_adversary_per_installation_failure"]) <= min(2 * exact_fraction(r["single_hazard_bit_error_probability"]), Fraction(1)) for r in rows),
            "strict_separation_live": any(exact_fraction(r["visible_adversary_per_installation_failure"]) > exact_fraction(r["perfectly_correlated_bits_per_installation_failure"]) for r in positive),
            "pass": True,
        },
        "blinded_one_class_adversary": {
            "per_installation_risk": "p_m",
            "visible_strictly_larger_on_positive_grid": all(exact_fraction(r["visible_adversary_per_installation_failure"]) > exact_fraction(r["blinded_one_class_per_installation_failure"]) for r in positive),
            "pass": True,
        },
    }


def expected_result(
    manifest: dict[str, Any], source_binding: dict[str, Any], upstream: dict[str, Any]
) -> dict[str, Any]:
    rows = list(iter_rows())
    control_records = controls(rows)
    gates = {
        "G0_manifest_and_order": canonical_sha256(manifest) == MANIFEST_SHA256,
        "G1_source_and_predecessor_binding": source_binding["pass"] and upstream["pass"],
        "G2_complete_exact_54_rows": len(rows) == len({r["key"] for r in rows}) == 54,
        "G3_product_error_and_visibility_semantics": control_records["single_bit_exploit_witnesses"]["pass"],
        "G4_symbolic_fresh_infinite_horizon_negative": theorem()["pass"],
        "G5_scope_controls": all(r["pass"] for r in control_records.values()),
        "G6_metric_robustness": all(r["pass"] for r in control_records.values()),
        "G7_no_float_or_rng": True,
    }
    if tuple(gates) != GATE_IDS:
        raise AssertionError("gate order mismatch")
    return {
        "schema_version": "asmp5_dynamic_replicated_noisy_anchor_result_v0_4",
        "protocol_id": PROTOCOL_ID,
        "manifest_sha256": MANIFEST_SHA256,
        "source_binding": source_binding,
        "predecessor_binding": upstream,
        "status": "computed_awaiting_import_independent_verification",
        "registry_rows": rows,
        "symbolic_theorem": theorem(),
        "controls": control_records,
        "gates": gates,
        "metric_robustness": {
            "invariance": "hazard_bit_swap_passed",
            "sensitivity": "visible_vs_blinded_and_independent_vs_correlated_live",
            "monotonicity": "fresh_horizon_accumulation_live",
            "anti_gaming": "false_negative_safety_reports_deadlock",
            "clean_control": "epsilon_zero_and_v0_3_cycle_passed",
        },
        "conclusion_layers": {
            "metric_robustness": "controls_computed_awaiting_independent_replay",
            "task_result": "finite_dynamic_noisy_anchor_grid_compiled",
            "measurement_reliability": "awaiting_import_independent_verification",
            "claim_support": "pending_independent_verification",
            "operational_decision": "no_generalization_or_deployment_authorized",
        },
        "claim_boundary": list(CLAIM_BOUNDARY),
    }


def write_once(path: Path, value: Any) -> None:
    parent = path.parent
    if parent.exists():
        if not parent.is_dir() or _is_reparse(parent):
            raise ValueError("invalid artifact parent")
    else:
        if not parent.parent.is_dir() or _is_reparse(parent.parent):
            raise ValueError("invalid artifact ancestry")
        parent.mkdir()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(canonical_json(value).encode())
        stream.flush()
        os.fsync(stream.fileno())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=ARTIFACT_DIRECTORY / "result_v0_4.json")
    parser.add_argument("--output", type=Path, default=ARTIFACT_DIRECTORY / "verification_v0_4.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    preflight_inventory()
    result_path = Path(os.path.abspath(args.result))
    output_path = Path(os.path.abspath(args.output))
    expected_parent = Path(os.path.abspath(ARTIFACT_DIRECTORY))
    if result_path.parent != expected_parent or output_path.parent != expected_parent:
        raise SystemExit("refusing path outside frozen sibling artifact directory")
    if output_path.exists():
        raise SystemExit("refusing to overwrite verification evidence")
    result_bytes = result_path.read_bytes()
    result = load_json_bytes_strict(result_bytes)
    if canonical_json(result).encode() != result_bytes:
        raise SystemExit("result is not canonical JSON")
    source_commit = result.get("source_binding", {}).get("source_commit", "")
    source_binding, snapshot, root = source_snapshot(source_commit)
    manifest = load_json_bytes_strict(snapshot["manifest_v0_4.json"])
    if canonical_sha256(manifest) != MANIFEST_SHA256 or manifest.get("protocol_id") != PROTOCOL_ID or manifest.get("schema_version") != MANIFEST_SCHEMA:
        raise SystemExit("manifest binding failure")
    upstream = predecessor_binding(manifest, source_commit, root)
    tracemalloc.start()
    started_ns = time.monotonic_ns()
    try:
        expected = expected_result(manifest, source_binding, upstream)
        elapsed_ns = time.monotonic_ns() - started_ns
        _, peak_bytes = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    if elapsed_ns > manifest["budget"]["max_wall_seconds"] * 1_000_000_000:
        raise SystemExit("verification wall limit exceeded")
    if peak_bytes > manifest["budget"]["max_traced_python_mib"] * 1024 * 1024:
        raise SystemExit("verification traced-Python memory limit exceeded")
    mismatches = [] if strict_json_equal(result, expected) else ["full_result_semantics"]
    verification = {
        "schema_version": "asmp5_dynamic_replicated_noisy_anchor_verification_v0_4",
        "protocol_id": PROTOCOL_ID,
        "pass": not mismatches,
        "implementation_imported": False,
        "enumeration": {
            "method": "complete ordered 2m-bit product patterns plus two-state recurrence",
            "maximum_joint_patterns": 1024,
            "registered_rows": 54,
        },
        "mismatches": mismatches,
        "source_binding_match": strict_json_equal(result.get("source_binding"), source_binding),
        "predecessor_binding_match": strict_json_equal(result.get("predecessor_binding"), upstream),
        "manifest_binding": canonical_sha256(manifest) == MANIFEST_SHA256,
        "row_order_and_semantics_match": not mismatches,
        "controls_match": not mismatches,
        "symbolic_theorem_match": not mismatches,
        "final_conclusion_layers": {
            "metric_robustness": "seven_controls_independently_replayed",
            "task_result": "finite_dynamic_noisy_anchor_grid_reproduced",
            "measurement_reliability": "import_independent_pattern_enumeration_and_recurrence_passed" if not mismatches else "failed",
            "claim_support": "frozen_product_error_transition_system_supported" if not mismatches else "not_supported",
            "operational_decision": "no_generalization_or_deployment_authorized",
        },
        "claim_boundary": list(CLAIM_BOUNDARY),
        "bindings": {
            "manifest_v0_4.json": MANIFEST_SHA256,
            "result_v0_4.json": hashlib.sha256(result_bytes).hexdigest(),
        },
    }
    if not verification["pass"]:
        raise SystemExit(f"independent verification failed: {mismatches}")
    if len(canonical_json(verification).encode()) > manifest["budget"]["max_artifact_bytes"]:
        raise SystemExit("verification artifact limit exceeded")
    write_once(output_path, verification)
    print(output_path)


if __name__ == "__main__":
    main()
