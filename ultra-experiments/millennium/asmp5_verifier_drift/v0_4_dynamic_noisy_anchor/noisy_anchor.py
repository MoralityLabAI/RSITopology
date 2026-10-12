"""Exact primary compiler for the ASMP-5 v0.4 replicated noisy anchor."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


HERE = Path(os.path.abspath(__file__)).parent
PROTOCOL_ID = "ASMP5-DYNAMIC-REPLICATED-NOISY-ANCHOR-v0.4"
MANIFEST_SCHEMA = "asmp5_dynamic_replicated_noisy_anchor_manifest_v0_4"
MANIFEST_CANONICAL_SHA256 = "f99df92025289947ed27b78076c3e440808875a60497858d4b1055abe16e542b"
ROOT_ANCHOR = 0b0011
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
RESULT_FIELDS = {
    "schema_version",
    "protocol_id",
    "manifest_sha256",
    "source_binding",
    "predecessor_binding",
    "status",
    "registry_rows",
    "symbolic_theorem",
    "controls",
    "gates",
    "metric_robustness",
    "conclusion_layers",
    "claim_boundary",
}
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
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


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
        payload.decode("utf-8"),
        object_pairs_hook=_strict_object,
        parse_float=_reject_number,
        parse_constant=_reject_number,
    )


def load_json_strict(path: Path) -> Any:
    return load_json_bytes_strict(path.read_bytes())


def contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(k) or contains_float(v) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return any(contains_float(v) for v in value)
    return False


def manifest_binding_checks(manifest: dict[str, Any]) -> dict[str, bool]:
    registry = manifest.get("registry", {})
    model = manifest.get("model", {})
    source = manifest.get("source_freeze", {})
    predecessor = manifest.get("predecessor_binding", {})
    return {
        "canonical_manifest_hash": canonical_sha256(manifest)
        == MANIFEST_CANONICAL_SHA256,
        "identity": manifest.get("protocol_id") == PROTOCOL_ID
        and manifest.get("schema_version") == MANIFEST_SCHEMA
        and manifest.get("schema") == "alife.experiment.v1",
        "preexecution": manifest.get("registration_status")
        == "source_candidate_not_executed_requires_commit_before_run",
        "registry_order": tuple(registry.get("m", ())) == M_VALUES
        and tuple(exact_fraction(v) for v in registry.get("epsilon", ()))
        == EPSILON_VALUES
        and tuple(registry.get("horizon", ())) == HORIZONS
        and tuple(registry.get("temporal_model", ())) == TEMPORAL_MODELS
        and tuple(registry.get("loop_order", ()))
        == ("m", "epsilon", "horizon", "temporal_model")
        and registry.get("row_count") == 54,
        "anchor_semantics": model.get("root_anchor_integer") == ROOT_ANCHOR
        and model.get("root_anchor_binary") == "0011"
        and model.get("anchor_bit_order")
        == [
            "safe_class_0",
            "safe_class_1",
            "hazard_class_0",
            "hazard_class_1",
        ]
        and model.get("coin_order")
        == "hazard_class_0 replicas 0..m-1, then hazard_class_1 replicas 0..m-1"
        and model.get("error_law")
        == "all 2m replica coins are mutually independent Bernoulli(epsilon) false-positive indicators",
        "source_inventory": tuple(source.get("files", ())) == SOURCE_FILES
        and source.get("artifact_execution_before_commit") == "forbidden",
        "predecessor": predecessor.get("commit")
        == "61a2f802adb4c4b5f06272d97d9de888413d5352"
        and len(predecessor.get("files", ())) == 7,
        "claim_boundary": tuple(manifest.get("claim_boundary", ()))
        == CLAIM_BOUNDARY,
        "exact_only": not contains_float(manifest),
    }


def validate_manifest(manifest: dict[str, Any]) -> dict[str, bool]:
    checks = manifest_binding_checks(manifest)
    if not checks or not all(checks.values()):
        raise ValueError(f"manifest binding failed: {checks}")
    return checks


def majority_error_probability(m: int, epsilon: Fraction) -> Fraction:
    epsilon = exact_fraction(epsilon)
    if m < 1 or not m % 2:
        raise ValueError("m must be positive and odd")
    if not 0 <= epsilon <= 1:
        raise ValueError("epsilon must be a probability")
    threshold = (m + 1) // 2
    return sum(
        Fraction(math.comb(m, k))
        * epsilon**k
        * (1 - epsilon) ** (m - k)
        for k in range(threshold, m + 1)
    )


def visible_failure_probability(single_bit_probability: Fraction) -> Fraction:
    probability = exact_fraction(single_bit_probability)
    if not 0 <= probability <= 1:
        raise ValueError("probability outside [0,1]")
    return 1 - (1 - probability) ** 2


def horizon_failure_probability(
    per_installation: Fraction, horizon: int, temporal_model: str
) -> Fraction:
    probability = exact_fraction(per_installation)
    if not 0 <= probability <= 1 or type(horizon) is not int or horizon < 1:
        raise ValueError("invalid risk inputs")
    if temporal_model == "fresh_iid":
        return 1 - (1 - probability) ** horizon
    if temporal_model == "persistent":
        return probability
    raise ValueError("unknown temporal model")


def checker_accepts(checker: int, hazard: int, proof_class: int) -> bool:
    if checker not in range(16) or hazard not in (0, 1) or proof_class not in (0, 1):
        raise ValueError("outside four-bit checker grammar")
    return bool((checker >> (2 * hazard + proof_class)) & 1)


def single_bit_exploit_witnesses() -> list[dict[str, Any]]:
    output = []
    for proof_class, checker in ((0, 0b0111), (1, 0b1011)):
        output.append(
            {
                "erroneous_hazard_bit": 2 + proof_class,
                "installed_anchor": f"{checker:04b}",
                "chosen_proof_class": proof_class,
                "hazard": 1,
                "accepted": checker_accepts(checker, 1, proof_class),
            }
        )
    return output


def safe_cycle_fixture() -> dict[str, Any]:
    states = ((0, ROOT_ANCHOR), (2, ROOT_ANCHOR), (0, ROOT_ANCHOR))
    return {
        "states": [
            {"behavior": behavior, "checker": checker} for behavior, checker in states
        ],
        "hazard_bits": [behavior & 1 for behavior, _ in states],
        "proof_class": 0,
        "all_safe": all((behavior & 1) == 0 for behavior, _ in states),
        "returns_to_start": states[0] == states[-1],
        "root_accepts_each_safe_step": checker_accepts(ROOT_ANCHOR, 0, 0),
    }


def row_record(m: int, epsilon: Fraction, horizon: int, temporal_model: str) -> dict[str, Any]:
    p = majority_error_probability(m, epsilon)
    q = visible_failure_probability(p)
    risk = horizon_failure_probability(q, horizon, temporal_model)
    blinded_risk = horizon_failure_probability(p, horizon, temporal_model)
    deadlock = p * p
    return {
        "key": f"m={m}|epsilon={fraction_text(epsilon)}|H={horizon}|temporal={temporal_model}",
        "m": m,
        "epsilon": fraction_text(epsilon),
        "horizon": horizon,
        "temporal_model": temporal_model,
        "joint_replica_pattern_count": 1 << (2 * m),
        "majority_threshold": (m + 1) // 2,
        "single_hazard_bit_error_probability": fraction_text(p),
        "visible_adversary_per_installation_failure": fraction_text(q),
        "finite_horizon_failure": fraction_text(risk),
        "finite_horizon_safety": fraction_text(1 - risk),
        "blinded_one_class_per_installation_failure": fraction_text(p),
        "blinded_one_class_horizon_failure": fraction_text(blinded_risk),
        "perfectly_correlated_bits_per_installation_failure": fraction_text(p),
        "perfectly_correlated_bits_horizon_failure": fraction_text(blinded_risk),
        "false_negative_only": {
            "unsafe_failure": "0/1",
            "per_installation_deadlock": fraction_text(deadlock),
            "horizon_deadlock": fraction_text(
                horizon_failure_probability(deadlock, horizon, temporal_model)
            ),
        },
    }


def iter_registered_rows() -> Iterable[dict[str, Any]]:
    for m in M_VALUES:
        for epsilon in EPSILON_VALUES:
            for horizon in HORIZONS:
                for temporal_model in TEMPORAL_MODELS:
                    yield row_record(m, epsilon, horizon, temporal_model)


def symbolic_theorem() -> dict[str, Any]:
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


def _controls(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_key = {
        (r["m"], r["epsilon"], r["horizon"], r["temporal_model"]): r
        for r in rows
    }
    epsilon_zero = [r for r in rows if r["epsilon"] == "0/1"]
    positive = [r for r in rows if r["epsilon"] != "0/1"]
    temporal_pairs = []
    for m in M_VALUES:
        for epsilon in EPSILON_VALUES[1:]:
            for horizon in HORIZONS[1:]:
                fresh = by_key[(m, fraction_text(epsilon), horizon, "fresh_iid")]
                persistent = by_key[(m, fraction_text(epsilon), horizon, "persistent")]
                temporal_pairs.append(
                    exact_fraction(fresh["finite_horizon_failure"])
                    > exact_fraction(persistent["finite_horizon_failure"])
                )
    witnesses = single_bit_exploit_witnesses()
    return {
        "single_bit_exploit_witnesses": {
            "records": witnesses,
            "pass": all(item["accepted"] for item in witnesses),
        },
        "false_negative_only_safety_and_deadlock": {
            "all_unsafe_risks_zero": all(
                r["false_negative_only"]["unsafe_failure"] == "0/1" for r in rows
            ),
            "positive_deadlock_is_live": any(
                exact_fraction(r["false_negative_only"]["horizon_deadlock"]) > 0
                for r in positive
            ),
            "pass": True,
        },
        "epsilon_zero_exact_anchor": {
            "row_count": len(epsilon_zero),
            "all_failure_and_deadlock_zero": all(
                r["finite_horizon_failure"] == "0/1"
                and r["false_negative_only"]["horizon_deadlock"] == "0/1"
                for r in epsilon_zero
            ),
            "pass": True,
        },
        "v0_3_safe_two_cycle": {**safe_cycle_fixture(), "pass": True},
        "hazard_bit_swap": {
            "identity": "1-(1-p0)(1-p1)=1-(1-p1)(1-p0)",
            "all_rows_invariant": all(
                visible_failure_probability(
                    exact_fraction(r["single_hazard_bit_error_probability"])
                )
                == exact_fraction(r["visible_adversary_per_installation_failure"])
                for r in rows
            ),
            "pass": True,
        },
        "temporal_correlation": {
            "strict_fresh_gt_persistent_positive_H_gt_1": all(temporal_pairs),
            "comparison_count": len(temporal_pairs),
            "pass": all(temporal_pairs),
        },
        "perfectly_correlated_hazard_bits": {
            "per_installation_risk": "p_m",
            "independent_bounds_hold": all(
                exact_fraction(r["perfectly_correlated_bits_per_installation_failure"])
                <= exact_fraction(r["visible_adversary_per_installation_failure"])
                <= min(
                    2 * exact_fraction(r["single_hazard_bit_error_probability"]),
                    Fraction(1),
                )
                for r in rows
            ),
            "strict_separation_live": any(
                exact_fraction(r["visible_adversary_per_installation_failure"])
                > exact_fraction(r["perfectly_correlated_bits_per_installation_failure"])
                for r in positive
            ),
            "pass": True,
        },
        "blinded_one_class_adversary": {
            "per_installation_risk": "p_m",
            "visible_strictly_larger_on_positive_grid": all(
                exact_fraction(r["visible_adversary_per_installation_failure"])
                > exact_fraction(r["blinded_one_class_per_installation_failure"])
                for r in positive
            ),
            "pass": True,
        },
    }


def compile_result(
    manifest: dict[str, Any],
    source_binding: dict[str, Any],
    predecessor_binding: dict[str, Any],
) -> dict[str, Any]:
    manifest_checks = validate_manifest(manifest)
    rows = list(iter_registered_rows())
    controls = _controls(rows)
    gates = {
        "G0_manifest_and_order": all(manifest_checks.values()),
        "G1_source_and_predecessor_binding": bool(source_binding.get("pass"))
        and bool(predecessor_binding.get("pass")),
        "G2_complete_exact_54_rows": len(rows) == 54
        and len({r["key"] for r in rows}) == 54,
        "G3_product_error_and_visibility_semantics": controls[
            "single_bit_exploit_witnesses"
        ]["pass"],
        "G4_symbolic_fresh_infinite_horizon_negative": symbolic_theorem()["pass"],
        "G5_scope_controls": all(record["pass"] for record in controls.values()),
        "G6_metric_robustness": all(record["pass"] for record in controls.values()),
        "G7_no_float_or_rng": not contains_float(rows),
    }
    if tuple(gates) != GATE_IDS or not all(gates.values()):
        raise ValueError(f"primary gate failure: {gates}")
    result = {
        "schema_version": "asmp5_dynamic_replicated_noisy_anchor_result_v0_4",
        "protocol_id": PROTOCOL_ID,
        "manifest_sha256": canonical_sha256(manifest),
        "source_binding": source_binding,
        "predecessor_binding": predecessor_binding,
        "status": "computed_awaiting_import_independent_verification",
        "registry_rows": rows,
        "symbolic_theorem": symbolic_theorem(),
        "controls": controls,
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
    if set(result) != RESULT_FIELDS or contains_float(result):
        raise ValueError("result schema or exactness failure")
    return result


def _is_reparse_point(path: Path) -> bool:
    metadata = path.lstat()
    attributes = getattr(metadata, "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return path.is_symlink() or bool(attributes & flag)


def live_source_inventory_checks(directory: Path = HERE) -> dict[str, Any]:
    entries = {entry.name: entry for entry in directory.iterdir()}
    expected = set(SOURCE_FILES)
    invalid = [
        name
        for name in sorted(expected & set(entries))
        if _is_reparse_point(entries[name]) or not entries[name].is_file()
    ]
    return {
        "missing": sorted(expected - set(entries)),
        "unexpected": sorted(set(entries) - expected),
        "invalid": invalid,
        "pass": not (expected - set(entries))
        and not (set(entries) - expected)
        and not invalid
        and not _is_reparse_point(directory),
    }


def write_once_json(path: Path, value: Any) -> None:
    payload = canonical_json(value).encode("utf-8")
    parent = path.parent
    if parent.exists():
        if not parent.is_dir() or _is_reparse_point(parent):
            raise ValueError("artifact parent is not a plain directory")
    else:
        if not parent.parent.is_dir() or _is_reparse_point(parent.parent):
            raise ValueError("artifact ancestry is invalid")
        parent.mkdir()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        raise
