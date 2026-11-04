"""Import-independent verifier for the ASMP-6 v0.3 finite grid."""

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
import stat
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent
FROZEN_PROTOCOL_ID = "ASMP6-MULTILETTER-TENSORIZATION-v0.3"
FROZEN_MANIFEST_SCHEMA = "asmp6_multiletter_tensorization_manifest_v0_3"
FROZEN_REPLAY_COMMAND = (
    "python -I run.py --source-commit <40-hex-source-commit>"
)
FROZEN_MANIFEST_CANONICAL_SHA256 = (
    "c29b6fb6642b26ad25326f900c486c792977a7af0416cc279cdcefe5dd920a32"
)
FROZEN_CELLS = tuple(
    (alphabet_size, block_length)
    for alphabet_size in (2, 3, 4, 5)
    for block_length in (1, 2, 3)
)
FROZEN_SOURCE_FILES = (
    "PROTOCOL_v0_3.md",
    "README.md",
    "SOURCE_FREEZE.md",
    "manifest_v0_3.json",
    "multiletter_tensorization.py",
    "run.py",
    "test_multiletter_tensorization.py",
    "verify_independent.py",
)
FROZEN_PROBE_IDS = (
    "P1_message_and_transcript_relabeling",
    "P2_odd_alphabet_block_sensitivity",
    "P3_encoder_class_inclusion",
    "P4_global_only_parity_pathology",
    "P5_per_message_cover_blind_control",
)
FROZEN_CLAIM_BOUNDARY = (
    "finite opaque-symbol probability models only",
    "uniform iid benign transcript cover only",
    "payload alphabet exactly {0,1}^n with uniform prior",
    "exact globally message-averaged full-transcript cover only",
    "product comparator exactly factors one payload bit and one transcript symbol per coordinate",
    "passive transcript-only decoder with no key, side information, active auditor, or shared latent variable",
    "no prefix-conditional, adaptive-audit, learned, linguistic, or semantic channel claim",
    "no asymptotic capacity, square-root law, tensorization theorem beyond the registered grid, or ASMP-6 resolution claim",
)
EXPECTED_RESULT_FIELDS = {
    "cells",
    "claim_boundary",
    "conclusion_layers",
    "controls",
    "gates",
    "manifest_sha256",
    "metric_robustness",
    "protocol_id",
    "resource_observations",
    "schema_version",
    "source_binding",
    "status",
    "stop_reason",
}
EXPECTED_PRIMARY_GATES = {
    "G0_frozen_manifest_binding",
    "G1_registered_grid_complete",
    "G2_unrestricted_joint_feasibility",
    "G3_product_joint_and_formula",
    "G4_registered_contrast_pattern",
    "G5_n1_reproduction",
    "G6_five_metric_robustness_probes",
    "G7_exact_arithmetic_firewall",
}
FINAL_CLAIM_SUPPORT = (
    "finite_exact_m2to5_n1to3_uniform_global_transcript_cover_model_only"
)
EXPECTED_PREVERIFICATION_LAYERS = {
    "metric_robustness": "five_frozen_probe_families_computed_awaiting_independent_replay",
    "task_result": "finite_global_cover_block_advantage_over_registered_product_subclass",
    "measurement_reliability": "awaiting_import_independent_verification",
    "claim_support": "pending_independent_verification",
    "operational_decision": "await_independent_verification",
}
EXPECTED_FINAL_LAYERS = {
    "metric_robustness": "five_frozen_probe_families_independently_replayed",
    "task_result": "finite_global_cover_block_advantage_over_registered_product_subclass",
    "measurement_reliability": "independent_closed_form_joint_control_and_source_replay_passed",
    "claim_support": FINAL_CLAIM_SUPPORT,
    "operational_decision": "retain_finite_boundary_and_register_stronger_cover_or_active_audit_successor",
}


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


def load_json_strict(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_strict_object,
        parse_float=_reject_float,
        parse_constant=_reject_constant,
    )


def exact_fraction(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("probabilities must be exact rationals")
    if isinstance(value, (Fraction, int, str)):
        return Fraction(value)
    raise TypeError(f"unsupported exact-rational type: {type(value).__name__}")


def contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(key) or contains_float(item) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(contains_float(item) for item in value)
    return False


def _registered_cells(manifest: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    try:
        rows = manifest["grid"]["registered_cells"]
    except (KeyError, TypeError):
        return ()
    if not isinstance(rows, list):
        return ()
    output: list[tuple[int, int]] = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"alphabet_size", "block_length"}:
            return ()
        m = row.get("alphabet_size")
        n = row.get("block_length")
        if type(m) is not int or type(n) is not int:
            return ()
        output.append((m, n))
    return tuple(output)


def manifest_binding_checks(manifest: dict[str, Any]) -> dict[str, bool]:
    artifacts = manifest.get("artifacts", {})
    source = manifest.get("source_freeze", {})
    probes = manifest.get("metric_robustness_probes", [])
    resource = manifest.get("resource_guard", {})
    write_once = manifest.get("write_once_artifacts", {})
    return {
        "canonical_manifest_hash_is_frozen": (
            canonical_sha256(manifest) == FROZEN_MANIFEST_CANONICAL_SHA256
        ),
        "identity_is_frozen": (
            manifest.get("schema") == "alife.experiment.v1"
            and manifest.get("schema_version") == FROZEN_MANIFEST_SCHEMA
            and manifest.get("protocol_id") == FROZEN_PROTOCOL_ID
        ),
        "replay_command_is_exact": (
            isinstance(artifacts, dict)
            and artifacts.get("replay_command") == FROZEN_REPLAY_COMMAND
        ),
        "registered_cells_are_exact": _registered_cells(manifest) == FROZEN_CELLS,
        "semantic_core_is_exact": _semantic_core_is_exact(manifest),
        "probe_ids_are_exact": (
            isinstance(probes, list)
            and tuple(row.get("id") if isinstance(row, dict) else None for row in probes)
            == FROZEN_PROBE_IDS
        ),
        "claim_boundary_is_exact": (
            isinstance(manifest.get("claim_boundary"), list)
            and tuple(manifest["claim_boundary"]) == FROZEN_CLAIM_BOUNDARY
        ),
        "conclusion_layers_are_exact": (
            isinstance(manifest.get("conclusion_layer_names"), list)
            and tuple(manifest["conclusion_layer_names"])
            == (
                "metric_robustness",
                "task_result",
                "measurement_reliability",
                "claim_support",
                "operational_decision",
            )
        ),
        "source_set_is_exact": (
            isinstance(source, dict)
            and source.get("required") is True
            and source.get("artifact_execution_before_commit") == "forbidden"
            and tuple(source.get("files", ())) == FROZEN_SOURCE_FILES
            and source.get("import_safe_launch")
            == "run.py and verify_independent.py require Python isolated safe-path mode (-I) before any non-builtin import"
            and source.get("live_directory_policy")
            == "exactly the eight frozen regular non-reparse source files and no other live entry"
            and source.get("ignored_live_cache_policy")
            == "none; __pycache__ is unexpected and scientific launch fails closed"
        ),
        "resource_envelope_is_exact": (
            isinstance(resource, dict)
            and resource.get("max_registered_cells") == 12
            and resource.get("max_joint_entries_per_cell") == 1000
            and resource.get("max_transcript_count") == 125
            and resource.get("max_exact_dp_states") == 1008
            and manifest.get("budget", {}).get("max_wall_seconds") == 60
            and manifest.get("budget", {}).get("max_traced_python_mib") == 64
            and manifest.get("budget", {}).get("max_result_bytes") == 1048576
        ),
        "write_once_policy_is_exact": (
            isinstance(write_once, dict)
            and write_once.get("refuse_existing_paths") is True
            and write_once.get("primary")
            == "../artifacts_v0_3_multiletter_tensorization/result_v0_3.json"
            and write_once.get("verification")
            == "../artifacts_v0_3_multiletter_tensorization/verification_v0_3.json"
        ),
    }


def _semantic_core_is_exact(manifest: dict[str, Any]) -> bool:
    return manifest.get("semantics") == {
        "benign_cover": "Q_m^n(x)=1/m^n for every x in A_m^n",
        "decoder": "MAP decoder observes the full transcript and no other variable",
        "global_cover_constraint": "for every transcript x, (1/K) sum_u P(x|u)=1/M, equivalently the joint column mass is 1/M",
        "message_count": "K=2^n",
        "message_prior": "uniform on {0,1}^n",
        "per_message_control": "P(x|u)=1/M for every u,x",
        "product_subclass": "P(x|u)=product_t p_t(x_t|u_t), with (p_t(.|0)+p_t(.|1))/2=Q_m at each coordinate",
        "score": "block MAP Bayes error 1-sum_x max_u J(u,x), where J(u,x)=P(u)P(x|u)",
        "transcript_count": "M=m^n",
        "unrestricted_class": "all K by M nonnegative rational joint matrices with row sums 1/K and column sums 1/M",
    }


def _is_reparse_point(path: Path) -> bool:
    metadata = path.lstat()
    attributes = getattr(metadata, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return path.is_symlink() or bool(attributes & reparse_flag)


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
    invalid: list[str] = []
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


def validate_joint(
    joint: Sequence[Sequence[Any]], message_count: int, transcript_count: int
) -> tuple[tuple[Fraction, ...], ...]:
    if len(joint) != message_count:
        raise ValueError("wrong message dimension")
    matrix: list[tuple[Fraction, ...]] = []
    for row in joint:
        if len(row) != transcript_count:
            raise ValueError("wrong transcript dimension")
        matrix.append(tuple(exact_fraction(value) for value in row))
    parsed = tuple(matrix)
    if any(value < 0 for row in parsed for value in row):
        raise ValueError("negative joint mass")
    if any(sum(row, Fraction()) != Fraction(1, message_count) for row in parsed):
        raise ValueError("wrong row prior")
    for column in range(transcript_count):
        if sum((parsed[row][column] for row in range(message_count)), Fraction()) != Fraction(1, transcript_count):
            raise ValueError("global transcript cover failure")
    return parsed


def bayes_error(joint: Sequence[Sequence[Any]]) -> Fraction:
    if not joint or not joint[0]:
        raise ValueError("empty joint matrix")
    width = len(joint[0])
    if any(len(row) != width for row in joint):
        raise ValueError("ragged joint matrix")
    matrix = tuple(tuple(exact_fraction(value) for value in row) for row in joint)
    success = sum(
        (max(matrix[row][column] for row in range(len(matrix))) for column in range(width)),
        Fraction(),
    )
    return 1 - success


def matrix_text(joint: Sequence[Sequence[Fraction]]) -> list[list[str]]:
    return [[fraction_text(value) for value in row] for row in joint]


def independent_unrestricted_joint(
    message_count: int, transcript_count: int
) -> tuple[tuple[Fraction, ...], ...]:
    quotient, remainder = divmod(transcript_count, message_count)
    rows = [[Fraction() for _ in range(transcript_count)] for _ in range(message_count)]
    for message in range(message_count):
        for offset in range(quotient):
            rows[message][message * quotient + offset] = Fraction(1, transcript_count)
    first_residual = quotient * message_count
    for residual in range(remainder):
        column = first_residual + residual
        rows[residual][column] = Fraction(remainder, message_count * transcript_count)
        for message in range(remainder, message_count):
            rows[message][column] = Fraction(1, message_count * transcript_count)
    return validate_joint(rows, message_count, transcript_count)


def independent_one_shot_joint(alphabet_size: int) -> tuple[tuple[Fraction, ...], ...]:
    pairs = alphabet_size // 2
    rows = [[Fraction() for _ in range(alphabet_size)] for _ in range(2)]
    for symbol in range(alphabet_size):
        if symbol < pairs:
            rows[0][symbol] = Fraction(1, alphabet_size)
        elif symbol < 2 * pairs:
            rows[1][symbol] = Fraction(1, alphabet_size)
        else:
            rows[0][symbol] = rows[1][symbol] = Fraction(1, 2 * alphabet_size)
    return validate_joint(rows, 2, alphabet_size)


def independent_product_joint(
    alphabet_size: int, block_length: int
) -> tuple[tuple[Fraction, ...], ...]:
    factor = independent_one_shot_joint(alphabet_size)
    messages = list(itertools.product((0, 1), repeat=block_length))
    transcripts = list(itertools.product(range(alphabet_size), repeat=block_length))
    rows: list[list[Fraction]] = []
    for message in messages:
        row: list[Fraction] = []
        for transcript in transcripts:
            mass = Fraction(1)
            for coordinate in range(block_length):
                mass *= factor[message[coordinate]][transcript[coordinate]]
            row.append(mass)
        rows.append(row)
    return validate_joint(rows, len(messages), len(transcripts))


def independent_occupancy_certificate(
    message_count: int, transcript_count: int
) -> dict[str, Any]:
    """Independently optimize the decoder-assignment occupancy upper bound.

    This does not reuse the primary row-state dynamic program. It exhaustively
    checks discrete concavity and every pairwise balancing exchange for
    f(c)=min(1/K,c/M), then maximizes by selecting the M largest marginal gains.
    """

    def contribution(count: int) -> Fraction:
        return min(
            Fraction(1, message_count), Fraction(count, transcript_count)
        )

    marginal_gains = [
        contribution(count + 1) - contribution(count)
        for count in range(transcript_count)
    ]
    discrete_concavity = all(
        marginal_gains[index] >= marginal_gains[index + 1]
        for index in range(len(marginal_gains) - 1)
    )
    exchange_violations: list[tuple[int, int]] = []
    for high in range(transcript_count + 1):
        for low in range(transcript_count + 1):
            if high >= low + 2 and (
                contribution(high - 1) + contribution(low + 1)
                < contribution(high) + contribution(low)
            ):
                exchange_violations.append((high, low))

    all_marginals = sorted(
        marginal_gains * message_count, reverse=True
    )
    marginal_gain_success = sum(all_marginals[:transcript_count], Fraction())
    quotient, remainder = divmod(transcript_count, message_count)
    balanced_counts = [quotient + 1] * remainder + [quotient] * (
        message_count - remainder
    )
    balanced_success = sum(
        (contribution(count) for count in balanced_counts), Fraction()
    )
    formula_success = 1 - Fraction(
        remainder * (message_count - remainder),
        message_count * transcript_count,
    )
    return {
        "balanced_counts": balanced_counts,
        "balanced_success": fraction_text(balanced_success),
        "discrete_concavity": discrete_concavity,
        "exchange_violations": [list(pair) for pair in exchange_violations],
        "formula_success": fraction_text(formula_success),
        "marginal_gain_success": fraction_text(marginal_gain_success),
        "pass": bool(
            discrete_concavity
            and not exchange_violations
            and marginal_gain_success == balanced_success == formula_success
            and sum(balanced_counts) == transcript_count
        ),
    }


def independent_cell(alphabet_size: int, block_length: int) -> dict[str, Any]:
    message_count = 2**block_length
    transcript_count = alphabet_size**block_length
    quotient, remainder = divmod(transcript_count, message_count)
    theorem_error = Fraction(
        remainder * (message_count - remainder),
        message_count * transcript_count,
    )
    unrestricted = independent_unrestricted_joint(message_count, transcript_count)
    unrestricted_error = bayes_error(unrestricted)
    if unrestricted_error != theorem_error:
        raise AssertionError("independent unrestricted witness missed its bound")
    product = independent_product_joint(alphabet_size, block_length)
    product_error = bayes_error(product)
    one_shot_error = bayes_error(independent_one_shot_joint(alphabet_size))
    product_formula = 1 - (1 - one_shot_error) ** block_length
    if product_error != product_formula:
        raise AssertionError("independent product witness missed its formula")
    return {
        "alphabet_size": alphabet_size,
        "block_length": block_length,
        "cell_id": f"m{alphabet_size}_n{block_length}",
        "message_count": message_count,
        "transcript_count": transcript_count,
        "unrestricted": {
            "bayes_error": fraction_text(unrestricted_error),
            "joint_mass": matrix_text(unrestricted),
            "occupancy_dp_error_bound": fraction_text(theorem_error),
            "optimality_gap": "0/1",
            "quotient": quotient,
            "remainder": remainder,
            "theorem_error": fraction_text(theorem_error),
        },
        "product_memoryless": {
            "bayes_error": fraction_text(product_error),
            "joint_mass": matrix_text(product),
            "one_shot_error": fraction_text(one_shot_error),
            "tensor_formula_error": fraction_text(product_formula),
        },
        "comparison": {
            "bayes_error_gap_product_minus_unrestricted": fraction_text(
                product_error - unrestricted_error
            ),
            "predicted_strict_cell": alphabet_size % 2 == 1 and block_length > 1,
            "prediction_matches": (unrestricted_error < product_error)
            == (alphabet_size % 2 == 1 and block_length > 1),
            "strict_unrestricted_advantage": unrestricted_error < product_error,
            "unrestricted_not_worse": unrestricted_error <= product_error,
        },
    }


def _coordinate_marginals(
    joint: Sequence[Sequence[Fraction]], alphabet_size: int, block_length: int
) -> list[list[list[Fraction]]]:
    transcripts = list(itertools.product(range(alphabet_size), repeat=block_length))
    message_count = len(joint)
    output: list[list[list[Fraction]]] = []
    for row in joint:
        conditional = [message_count * value for value in row]
        per_coordinate: list[list[Fraction]] = []
        for coordinate in range(block_length):
            marginal = [Fraction() for _ in range(alphabet_size)]
            for mass, transcript in zip(conditional, transcripts):
                marginal[transcript[coordinate]] += mass
            per_coordinate.append(marginal)
        output.append(per_coordinate)
    return output


def independent_pathology() -> dict[str, Any]:
    joint = validate_joint(
        (
            ("1/8", "0/1", "0/1", "1/8"),
            ("1/8", "0/1", "0/1", "1/8"),
            ("0/1", "1/8", "1/8", "0/1"),
            ("0/1", "1/8", "1/8", "0/1"),
        ),
        4,
        4,
    )
    marginals = _coordinate_marginals(joint, 2, 2)
    error = bayes_error(joint)
    return {
        "alphabet_size": 2,
        "block_length": 2,
        "message_count": 4,
        "joint_mass": matrix_text(joint),
        "bayes_error": fraction_text(error),
        "blind_uniform_error": "3/4",
        "carries_information": error < Fraction(3, 4),
        "every_message_coordinate_marginal_is_uniform": all(
            marginal == [Fraction(1, 2), Fraction(1, 2)]
            for message in marginals
            for marginal in message
        ),
        "global_transcript_cover_exact": True,
        "full_per_message_transcript_cover": False,
    }


def independent_controls(cells: Sequence[dict[str, Any]]) -> dict[str, Any]:
    n1 = [cell for cell in cells if cell["block_length"] == 1]
    n1_pass = len(n1) == 4 and all(
        cell["unrestricted"]["bayes_error"]
        == cell["product_memoryless"]["bayes_error"]
        == ("0/1" if cell["alphabet_size"] % 2 == 0 else f"1/{2 * cell['alphabet_size']}")
        for cell in n1
    )
    per_message: dict[str, dict[str, Any]] = {}
    for cell in cells:
        error = 1 - Fraction(1, cell["message_count"])
        per_message[cell["cell_id"]] = {
            "definition": "P(x|u)=1/M for every payload and transcript",
            "bayes_error": fraction_text(error),
            "blind_uniform_error": fraction_text(error),
            "zero_payload": True,
            "row_mass": fraction_text(Fraction(1, cell["message_count"])),
            "column_mass": fraction_text(Fraction(1, cell["transcript_count"])),
        }
    return {
        "global_only_pathology": independent_pathology(),
        "n1_reproduction": {
            "pass": n1_pass,
            "registered_cells": [cell["cell_id"] for cell in n1],
        },
        "per_message_cover": {
            "pass": bool(per_message)
            and all(
                row["zero_payload"]
                and row["bayes_error"] == row["blind_uniform_error"]
                for row in per_message.values()
            ),
            "cells": per_message,
        },
    }


def independent_probes(
    cells: Sequence[dict[str, Any]], controls: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    relabeling_pass = bool(cells)
    relabeling_cells: list[str] = []
    for cell in cells:
        for arm_name in ("unrestricted", "product_memoryless"):
            arm = cell[arm_name]
            original = validate_joint(
                arm["joint_mass"], cell["message_count"], cell["transcript_count"]
            )
            permuted = tuple(tuple(reversed(row)) for row in reversed(original))
            replay = validate_joint(
                permuted, cell["message_count"], cell["transcript_count"]
            )
            relabeling_pass = relabeling_pass and (
                bayes_error(replay) == Fraction(arm["bayes_error"])
            )
        relabeling_cells.append(cell["cell_id"])
    lookup = {cell["cell_id"]: cell for cell in cells}
    sensitivity_cells = [
        f"m{alphabet_size}_n{block_length}"
        for alphabet_size in (3, 5)
        for block_length in (1, 2, 3)
    ]
    sensitivity_pass = all(cell_id in lookup for cell_id in sensitivity_cells)
    if sensitivity_pass:
        sensitivity_pass = all(
            lookup[f"m{alphabet_size}_n1"]["comparison"][
                "strict_unrestricted_advantage"
            ]
            is False
            and all(
                lookup[f"m{alphabet_size}_n{block_length}"]["comparison"][
                    "strict_unrestricted_advantage"
                ]
                is True
                for block_length in (2, 3)
            )
            for alphabet_size in (3, 5)
        )
    pathology = controls["global_only_pathology"]
    per_message = controls["per_message_cover"]
    return {
        "P1_message_and_transcript_relabeling": {
            "family": "invariance",
            "pass": relabeling_pass,
            "registered_cells": relabeling_cells,
        },
        "P2_odd_alphabet_block_sensitivity": {
            "family": "sensitivity",
            "pass": sensitivity_pass,
            "registered_cells": sensitivity_cells,
        },
        "P3_encoder_class_inclusion": {
            "family": "monotonicity",
            "pass": bool(cells)
            and all(cell["comparison"]["unrestricted_not_worse"] for cell in cells),
            "registered_cells": [cell["cell_id"] for cell in cells],
        },
        "P4_global_only_parity_pathology": {
            "family": "anti_gaming",
            "pass": bool(
                pathology["global_transcript_cover_exact"]
                and pathology["every_message_coordinate_marginal_is_uniform"]
                and pathology["carries_information"]
                and not pathology["full_per_message_transcript_cover"]
            ),
            "registered_fixture": "m2_n2_four_payload_parity_duplicate",
        },
        "P5_per_message_cover_blind_control": {
            "family": "clean_control",
            "pass": per_message["pass"] is True,
            "registered_cells": sorted(per_message["cells"]),
        },
    }


def _git(
    args: list[str], *, text: bool, cwd: Path | None = None
) -> str | bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd or HERE,
        check=True,
        capture_output=True,
        text=text,
    )
    return completed.stdout.strip() if text else completed.stdout


def replay_source_binding(source_commit: str) -> dict[str, Any]:
    validate_live_source_inventory()
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("source commit must be full lowercase 40-hex")
    object_type = str(_git(["cat-file", "-t", source_commit], text=True))
    if object_type != "commit":
        raise ValueError("source object is not a commit")
    resolved = str(_git(["rev-parse", "--verify", f"{source_commit}^{{commit}}"], text=True))
    if resolved != source_commit:
        raise ValueError("source commit resolution mismatch")
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", source_commit, "HEAD"],
        cwd=HERE,
        capture_output=True,
        text=True,
    )
    if ancestry.returncode != 0:
        raise ValueError("source commit is not an ancestor of HEAD")
    repo_root = Path(str(_git(["rev-parse", "--show-toplevel"], text=True))).resolve()
    relative_directory = HERE.relative_to(repo_root)
    directory_path = relative_directory.as_posix()
    listing = str(
        _git(
            ["ls-tree", "-r", "--name-only", source_commit, "--", directory_path],
            text=True,
            cwd=repo_root,
        )
    )
    listed_paths = {line for line in listing.splitlines() if line}
    expected_paths = {
        (relative_directory / filename).as_posix() for filename in FROZEN_SOURCE_FILES
    }
    if listed_paths != expected_paths:
        raise ValueError("source tree is not the exact frozen file set")
    source_files: dict[str, dict[str, str]] = {}
    for filename in FROZEN_SOURCE_FILES:
        relative_path = (relative_directory / filename).as_posix()
        tree_line = str(
            _git(
                ["ls-tree", source_commit, "--", relative_path],
                text=True,
                cwd=repo_root,
            )
        )
        metadata, listed_path = tree_line.split("\t", 1)
        mode, kind, blob_oid = metadata.split()
        if listed_path != relative_path or mode != "100644" or kind != "blob":
            raise ValueError(f"invalid source blob: {filename}")
        current = (HERE / filename).read_bytes()
        committed = subprocess.check_output(
            ["git", "show", f"{source_commit}:{relative_path}"], cwd=repo_root
        )
        current_blob_oid = subprocess.run(
            ["git", "hash-object", "--stdin"],
            cwd=repo_root,
            check=True,
            input=current,
            capture_output=True,
        ).stdout.decode("ascii").strip()
        if current != committed or current_blob_oid != blob_oid:
            raise ValueError(f"working source differs from commit: {filename}")
        source_files[filename] = {
            "git_blob_oid": current_blob_oid,
            "sha256": sha256_bytes(current),
        }
    return {
        "repo_relative_directory": directory_path,
        "source_commit": source_commit,
        "source_commit_is_ancestor_of_head": True,
        "source_commit_type": object_type,
        "source_files": source_files,
    }


def _resource_observations_valid(result: dict[str, Any]) -> bool:
    observations = result.get("resource_observations")
    if not isinstance(observations, dict):
        return False
    integer_fields = (
        "canonical_result_bytes",
        "completed_cells",
        "elapsed_wall_ns",
        "max_dp_state_positions_observed",
        "max_joint_entries_observed",
        "max_transcript_count_observed",
        "traced_python_limit_bytes",
        "traced_python_peak_bytes",
        "wall_limit_ns",
    )
    if any(type(observations.get(name)) is not int for name in integer_fields):
        return False
    return bool(
        observations["canonical_result_bytes"]
        == len(canonical_json(result).encode("utf-8"))
        and observations["canonical_result_bytes"] <= 1048576
        and observations["completed_cells"] == 12
        and 0 <= observations["elapsed_wall_ns"] <= 60_000_000_000
        and observations["max_dp_state_positions_observed"] == 1008
        and observations["max_joint_entries_observed"] == 1000
        and observations["max_transcript_count_observed"] == 125
        and observations["memory_measurement"]
        == "tracemalloc_peak_python_allocation_only"
        and observations["traced_python_limit_bytes"] == 64 * 1024 * 1024
        and 0 <= observations["traced_python_peak_bytes"]
        <= observations["traced_python_limit_bytes"]
        and observations["wall_limit_ns"] == 60_000_000_000
    )


def replay_reported_joint_cells(reported_cells: Any) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    if not isinstance(reported_cells, list):
        return [{"cell_id": "grid", "error": "cells_not_list"}]
    for cell in reported_cells:
        cell_id = cell.get("cell_id", "unknown") if isinstance(cell, dict) else "unknown"
        try:
            message_count = cell["message_count"]
            transcript_count = cell["transcript_count"]
            if type(message_count) is not int or type(transcript_count) is not int:
                raise TypeError("dimensions_not_int")
            for arm_name in ("unrestricted", "product_memoryless"):
                arm = cell[arm_name]
                matrix = validate_joint(
                    arm["joint_mass"], message_count, transcript_count
                )
                if bayes_error(matrix) != Fraction(arm["bayes_error"]):
                    raise ValueError(f"{arm_name}_map_score_mismatch")
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
            failures.append({"cell_id": cell_id, "error": str(error)})
    return failures


def replay_reported_product_formulas(reported_cells: Any) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    if not isinstance(reported_cells, list):
        return [{"cell_id": "grid", "error": "cells_not_list"}]
    for cell in reported_cells:
        cell_id = cell.get("cell_id", "unknown") if isinstance(cell, dict) else "unknown"
        try:
            alphabet_size = cell["alphabet_size"]
            block_length = cell["block_length"]
            if type(alphabet_size) is not int or type(block_length) is not int:
                raise TypeError("cell_parameters_not_int")
            one_shot_error = bayes_error(independent_one_shot_joint(alphabet_size))
            expected = 1 - (1 - one_shot_error) ** block_length
            arm = cell["product_memoryless"]
            if (
                Fraction(arm["one_shot_error"]) != one_shot_error
                or Fraction(arm["tensor_formula_error"]) != expected
                or Fraction(arm["bayes_error"]) != expected
            ):
                raise ValueError("product_tensor_formula_mismatch")
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
            failures.append({"cell_id": cell_id, "error": str(error)})
    return failures


def primary_result_semantic_checks(result: Any) -> dict[str, bool]:
    if not isinstance(result, dict):
        return {
            "result_fields_are_exact": False,
            "result_identity_is_exact": False,
            "source_binding_shape_is_valid": False,
            "primary_gates_are_exact_and_true": False,
            "preverification_layers_are_exact": False,
            "claim_boundary_is_exact": False,
            "exact_json_firewall": False,
        }
    source = result.get("source_binding")
    source_commit = source.get("source_commit") if isinstance(source, dict) else None
    gates = result.get("gates")
    return {
        "result_fields_are_exact": set(result) == EXPECTED_RESULT_FIELDS,
        "result_identity_is_exact": bool(
            result.get("schema_version")
            == "asmp6_multiletter_tensorization_result_v0_3"
            and result.get("protocol_id") == FROZEN_PROTOCOL_ID
            and result.get("manifest_sha256") == FROZEN_MANIFEST_CANONICAL_SHA256
            and result.get("status") == "complete"
            and result.get("stop_reason") == "registered_grid_complete"
        ),
        "source_binding_shape_is_valid": bool(
            isinstance(source, dict)
            and isinstance(source_commit, str)
            and re.fullmatch(r"[0-9a-f]{40}", source_commit)
        ),
        "primary_gates_are_exact_and_true": bool(
            isinstance(gates, dict)
            and set(gates) == EXPECTED_PRIMARY_GATES
            and all(value is True for value in gates.values())
        ),
        "preverification_layers_are_exact": (
            result.get("conclusion_layers") == EXPECTED_PREVERIFICATION_LAYERS
        ),
        "claim_boundary_is_exact": (
            result.get("claim_boundary") == list(FROZEN_CLAIM_BOUNDARY)
        ),
        "exact_json_firewall": not contains_float(result),
    }


def verify(
    manifest_path: Path | None = None,
    result_path: Path | None = None,
) -> dict[str, Any]:
    manifest_path = manifest_path or HERE / "manifest_v0_3.json"
    result_path = result_path or (
        HERE.parent
        / "artifacts_v0_3_multiletter_tensorization"
        / "result_v0_3.json"
    )
    manifest = load_json_strict(manifest_path)
    result = load_json_strict(result_path)
    if not isinstance(manifest, dict) or not isinstance(result, dict):
        raise ValueError("manifest and result roots must be objects")

    binding = manifest_binding_checks(manifest)
    expected_cells = [independent_cell(m, n) for m, n in FROZEN_CELLS]
    reported_cells = result.get("cells", [])
    cell_mismatches: list[dict[str, Any]] = []
    if not isinstance(reported_cells, list) or len(reported_cells) != len(expected_cells):
        cell_mismatches.append(
            {
                "field": "cell_count",
                "expected": len(expected_cells),
                "reported": len(reported_cells) if isinstance(reported_cells, list) else "not_list",
            }
        )
    else:
        for expected, reported in zip(expected_cells, reported_cells):
            if reported != expected:
                cell_mismatches.append(
                    {
                        "cell_id": expected["cell_id"],
                        "field": "canonical_cell",
                        "expected_sha256": canonical_sha256(expected),
                        "reported_sha256": canonical_sha256(reported),
                    }
                )

    joint_replay_failures = replay_reported_joint_cells(reported_cells)
    product_formula_failures = replay_reported_product_formulas(reported_cells)
    occupancy_certificates: list[dict[str, Any]] = []
    occupancy_upper_bound_failures: list[str] = []
    for alphabet_size, block_length in FROZEN_CELLS:
        message_count = 2**block_length
        transcript_count = alphabet_size**block_length
        certificate = independent_occupancy_certificate(
            message_count, transcript_count
        )
        record = {
            "cell_id": f"m{alphabet_size}_n{block_length}",
            **certificate,
        }
        occupancy_certificates.append(record)
        if not certificate["pass"]:
            occupancy_upper_bound_failures.append(record["cell_id"])

    expected_controls = independent_controls(expected_cells)
    expected_probes = independent_probes(expected_cells, expected_controls)
    controls_match = result.get("controls") == expected_controls
    probes_match = result.get("metric_robustness") == expected_probes

    source_binding_error = ""
    replayed_source: dict[str, Any] = {}
    reported_source = result.get("source_binding")
    if isinstance(reported_source, dict):
        source_commit = reported_source.get("source_commit")
        if isinstance(source_commit, str):
            try:
                replayed_source = replay_source_binding(source_commit)
            except (OSError, subprocess.SubprocessError, TypeError, ValueError) as error:
                source_binding_error = f"{type(error).__name__}: {error}"
        else:
            source_binding_error = "missing source commit"
    else:
        source_binding_error = "source binding is not an object"
    source_binding_matches = bool(replayed_source) and reported_source == replayed_source

    result_semantic_checks = primary_result_semantic_checks(result)
    result_identity = all(
        result_semantic_checks[name]
        for name in (
            "result_fields_are_exact",
            "result_identity_is_exact",
            "source_binding_shape_is_valid",
            "claim_boundary_is_exact",
            "exact_json_firewall",
        )
    )
    primary_gates_valid = result_semantic_checks[
        "primary_gates_are_exact_and_true"
    ]
    layers_match = result_semantic_checks["preverification_layers_are_exact"]
    resource_valid = _resource_observations_valid(result)

    independent_gates = {
        "V0_frozen_manifest_binding": all(binding.values()),
        "V1_exact_source_commit_tree_and_ancestry": source_binding_matches,
        "V2_result_identity_and_exact_json": result_identity,
        "V3_registered_cells_reconstructed": not cell_mismatches,
        "V4_joint_rows_columns_and_map_scores_replayed": not joint_replay_failures,
        "V5_occupancy_upper_bound_independently_established": not occupancy_upper_bound_failures
        and len(occupancy_certificates) == len(FROZEN_CELLS),
        "V6_product_tensor_formula_replayed": not product_formula_failures,
        "V7_five_metric_probe_families_replayed": probes_match
        and tuple(expected_probes) == FROZEN_PROBE_IDS
        and all(record["pass"] for record in expected_probes.values()),
        "V8_n1_and_control_records_replayed": controls_match
        and expected_controls["n1_reproduction"]["pass"],
        "V9_primary_gates_and_preverification_layers_match": primary_gates_valid
        and layers_match,
        "V10_resource_observations_within_frozen_limits": resource_valid,
    }
    passed = all(independent_gates.values())
    final_layers = (
        dict(EXPECTED_FINAL_LAYERS)
        if passed
        else {
            "metric_robustness": "not_established",
            "task_result": "not_established",
            "measurement_reliability": "failed",
            "claim_support": "none",
            "operational_decision": "repair",
        }
    )
    return {
        "schema_version": "asmp6_multiletter_tensorization_verification_v0_3",
        "pass": passed,
        "protocol_id": FROZEN_PROTOCOL_ID,
        "manifest_binding": binding,
        "source_binding_error": source_binding_error,
        "source_binding_replay": replayed_source,
        "cell_mismatches": cell_mismatches,
        "joint_replay_failures": joint_replay_failures,
        "occupancy_certificates": occupancy_certificates,
        "occupancy_upper_bound_failures": occupancy_upper_bound_failures,
        "product_formula_failures": product_formula_failures,
        "controls_match": controls_match,
        "metric_probe_ids": list(FROZEN_PROBE_IDS),
        "metric_probes_match": probes_match,
        "resource_observations_valid": resource_valid,
        "result_semantic_checks": result_semantic_checks,
        "primary_gates_valid": primary_gates_valid,
        "preverification_layers_match": layers_match,
        "independent_gates": independent_gates,
        "final_conclusion_layers": final_layers,
        "claim_boundary": list(FROZEN_CLAIM_BOUNDARY),
        "bindings": {
            "manifest_v0_3.json": sha256_file(manifest_path),
            "result_v0_3.json": sha256_file(result_path),
        },
    }


def write_once_json(path: Path, value: Any, max_bytes: int = 1048576) -> None:
    payload = canonical_json(value).encode("utf-8")
    if len(payload) > max_bytes:
        raise ValueError("verification exceeds frozen artifact byte ceiling")
    destination = _prepare_write_once_destination(path)
    with destination.open("xb") as stream:
        stream.write(payload)


def _absolute_without_reparse_resolution(path: Path) -> Path:
    """Lexically anchor a destination without resolving links or junctions."""

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
            f"cannot inspect artifact destination component: {path}"
        ) from error


def _require_safe_artifact_directory(
    path: Path, metadata: os.stat_result
) -> None:
    if _is_reparse_point(path):
        raise ValueError(f"artifact destination contains reparse point: {path}")
    if not stat.S_ISDIR(metadata.st_mode):
        raise NotADirectoryError(
            f"artifact destination ancestor is not a directory: {path}"
        )


def _prepare_write_once_destination(path: Path) -> Path:
    """Create missing parents one-by-one after fail-closed ancestry checks."""

    destination = _absolute_without_reparse_resolution(path)
    chain = _destination_chain(destination)
    for component in chain[:-1]:
        metadata = _lstat_optional(component)
        if metadata is None:
            try:
                component.mkdir()
            except FileExistsError as error:
                raise FileExistsError(
                    f"artifact destination ancestry changed during creation: {component}"
                ) from error
            except OSError as error:
                raise ValueError(
                    f"cannot create artifact destination directory: {component}"
                ) from error
            metadata = _lstat_optional(component)
            if metadata is None:
                raise ValueError(
                    f"artifact destination directory vanished after creation: {component}"
                )
        _require_safe_artifact_directory(component, metadata)

    output_metadata = _lstat_optional(destination)
    if output_metadata is not None:
        if _is_reparse_point(destination):
            raise ValueError(
                f"artifact destination output is a reparse point: {destination}"
            )
        raise FileExistsError(f"artifact destination already exists: {destination}")

    # Recheck the complete parent chain immediately before exclusive creation.
    for component in chain[:-1]:
        metadata = _lstat_optional(component)
        if metadata is None:
            raise ValueError(
                f"artifact destination ancestor vanished before write: {component}"
            )
        _require_safe_artifact_directory(component, metadata)
    return destination


def main() -> None:
    validate_live_source_inventory()
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=HERE / "manifest_v0_3.json")
    parser.add_argument(
        "--result",
        type=Path,
        default=HERE.parent
        / "artifacts_v0_3_multiletter_tensorization"
        / "result_v0_3.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE.parent
        / "artifacts_v0_3_multiletter_tensorization"
        / "verification_v0_3.json",
    )
    args = parser.parse_args()
    verification = verify(args.manifest, args.result)
    write_once_json(args.output, verification)
    if not verification["pass"]:
        failed = [
            name
            for name, passed in verification["independent_gates"].items()
            if not passed
        ]
        raise SystemExit(
            f"independent verification failed; downgraded write-once artifact retained: {failed}"
        )
    print(args.output)


if __name__ == "__main__":
    main()
