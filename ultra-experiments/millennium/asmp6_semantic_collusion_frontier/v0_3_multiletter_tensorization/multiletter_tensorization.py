"""Exact primary path for the source-frozen ASMP-6 v0.3 finite grid."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import stat
import subprocess
import time
import tracemalloc
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Sequence


HERE = Path(__file__).resolve().parent
FROZEN_PROTOCOL_ID = "ASMP6-MULTILETTER-TENSORIZATION-v0.3"
FROZEN_SCHEMA_VERSION = "asmp6_multiletter_tensorization_manifest_v0_3"
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
FROZEN_CONCLUSION_LAYER_NAMES = (
    "metric_robustness",
    "task_result",
    "measurement_reliability",
    "claim_support",
    "operational_decision",
)
FROZEN_METRIC_PROBE_IDS = (
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
FROZEN_RESULT_FIELDS = {
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


class ResourceStop(RuntimeError):
    """A declared resource ceiling stopped the deterministic cell sequence."""


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
        raise TypeError("probabilities must be exact rationals, never bool or float")
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


def load_manifest(path: Path) -> dict[str, Any]:
    value = load_json_strict(path)
    if not isinstance(value, dict):
        raise ValueError("manifest root must be an object")
    return value


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


def _registered_cells(manifest: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    grid = manifest.get("grid", {})
    rows = grid.get("registered_cells", []) if isinstance(grid, dict) else []
    parsed: list[tuple[int, int]] = []
    if not isinstance(rows, list):
        return ()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"alphabet_size", "block_length"}:
            return ()
        m = row.get("alphabet_size")
        n = row.get("block_length")
        if type(m) is not int or type(n) is not int:
            return ()
        parsed.append((m, n))
    return tuple(parsed)


def manifest_binding_checks(manifest: dict[str, Any]) -> dict[str, bool]:
    artifacts = manifest.get("artifacts", {})
    source_freeze = manifest.get("source_freeze", {})
    resource_guard = manifest.get("resource_guard", {})
    write_once = manifest.get("write_once_artifacts", {})
    return {
        "canonical_manifest_hash_is_frozen": (
            canonical_sha256(manifest) == FROZEN_MANIFEST_CANONICAL_SHA256
        ),
        "protocol_id_is_frozen": manifest.get("protocol_id") == FROZEN_PROTOCOL_ID,
        "schema_is_frozen": (
            manifest.get("schema") == "alife.experiment.v1"
            and manifest.get("schema_version") == FROZEN_SCHEMA_VERSION
        ),
        "registration_is_preexecution": (
            manifest.get("registration_status")
            == "source_candidate_not_executed_requires_commit_before_run"
        ),
        "replay_command_is_exact": (
            isinstance(artifacts, dict)
            and artifacts.get("replay_command") == FROZEN_REPLAY_COMMAND
        ),
        "registered_cells_are_exact": _registered_cells(manifest) == FROZEN_CELLS,
        "claim_boundary_is_exact": (
            isinstance(manifest.get("claim_boundary"), list)
            and tuple(manifest["claim_boundary"]) == FROZEN_CLAIM_BOUNDARY
        ),
        "conclusion_layers_are_exact": (
            isinstance(manifest.get("conclusion_layer_names"), list)
            and tuple(manifest["conclusion_layer_names"])
            == FROZEN_CONCLUSION_LAYER_NAMES
        ),
        "metric_probe_ids_are_exact": (
            isinstance(manifest.get("metric_robustness_probes"), list)
            and tuple(
                row.get("id") if isinstance(row, dict) else None
                for row in manifest["metric_robustness_probes"]
            )
            == FROZEN_METRIC_PROBE_IDS
        ),
        "source_file_set_is_exact": (
            isinstance(source_freeze, dict)
            and source_freeze.get("required") is True
            and source_freeze.get("artifact_execution_before_commit") == "forbidden"
            and tuple(source_freeze.get("files", ())) == FROZEN_SOURCE_FILES
            and source_freeze.get("import_safe_launch")
            == "run.py and verify_independent.py require Python isolated safe-path mode (-I) before any non-builtin import"
            and source_freeze.get("live_directory_policy")
            == "exactly the eight frozen regular non-reparse source files and no other live entry"
            and source_freeze.get("ignored_live_cache_policy")
            == "none; __pycache__ is unexpected and scientific launch fails closed"
        ),
        "resource_envelope_is_exact": (
            isinstance(resource_guard, dict)
            and resource_guard.get("max_exact_dp_states") == 1008
            and resource_guard.get("max_joint_entries_per_cell") == 1000
            and resource_guard.get("max_registered_cells") == 12
            and resource_guard.get("max_transcript_count") == 125
            and resource_guard.get("memory_measurement")
            == "tracemalloc peak Python allocation only; process RSS and native allocator memory are not measured"
        ),
        "write_once_policy_is_exact": (
            isinstance(write_once, dict)
            and write_once.get("refuse_existing_paths") is True
            and write_once.get("primary")
            == "../artifacts_v0_3_multiletter_tensorization/result_v0_3.json"
            and write_once.get("verification")
            == "../artifacts_v0_3_multiletter_tensorization/verification_v0_3.json"
        ),
        "semantic_core_is_exact": _semantic_core_is_exact(manifest),
    }


def _semantic_core_is_exact(manifest: dict[str, Any]) -> bool:
    semantics = manifest.get("semantics")
    if not isinstance(semantics, dict):
        return False
    expected = {
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
    return semantics == expected


def validate_manifest_binding(manifest: dict[str, Any]) -> dict[str, bool]:
    checks = manifest_binding_checks(manifest)
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"manifest binding failed: {failed}")
    return checks


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
    passed = not (directory_reparse or missing or unexpected or invalid)
    return {
        "pass": passed,
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


def message_words(block_length: int) -> list[tuple[int, ...]]:
    if block_length < 1:
        raise ValueError("block_length must be positive")
    return list(itertools.product((0, 1), repeat=block_length))


def transcript_words(alphabet_size: int, block_length: int) -> list[tuple[int, ...]]:
    if alphabet_size < 2 or block_length < 1:
        raise ValueError("alphabet_size >= 2 and block_length >= 1 are required")
    return list(itertools.product(range(alphabet_size), repeat=block_length))


def validate_joint(
    joint: Sequence[Sequence[Any]], message_count: int, transcript_count: int
) -> tuple[tuple[Fraction, ...], ...]:
    if len(joint) != message_count:
        raise ValueError("joint matrix has the wrong message dimension")
    parsed: list[tuple[Fraction, ...]] = []
    for row in joint:
        if len(row) != transcript_count:
            raise ValueError("joint matrix has the wrong transcript dimension")
        parsed.append(tuple(exact_fraction(value) for value in row))
    matrix = tuple(parsed)
    if any(value < 0 for row in matrix for value in row):
        raise ValueError("joint matrix contains negative mass")
    expected_row = Fraction(1, message_count)
    if any(sum(row, Fraction()) != expected_row for row in matrix):
        raise ValueError("joint matrix row prior is not uniform")
    expected_column = Fraction(1, transcript_count)
    for column in range(transcript_count):
        if sum((matrix[row][column] for row in range(message_count)), Fraction()) != expected_column:
            raise ValueError("joint matrix violates exact global transcript cover")
    return matrix


def bayes_success_from_joint(joint: Sequence[Sequence[Any]]) -> Fraction:
    if not joint or not joint[0]:
        raise ValueError("joint matrix must be nonempty")
    width = len(joint[0])
    if any(len(row) != width for row in joint):
        raise ValueError("joint matrix rows must have equal lengths")
    matrix = tuple(tuple(exact_fraction(value) for value in row) for row in joint)
    return sum((max(matrix[row][column] for row in range(len(matrix))) for column in range(width)), Fraction())


def bayes_error_from_joint(joint: Sequence[Sequence[Any]]) -> Fraction:
    return 1 - bayes_success_from_joint(joint)


def unrestricted_joint(message_count: int, transcript_count: int) -> tuple[tuple[Fraction, ...], ...]:
    if message_count < 2 or transcript_count < message_count:
        raise ValueError("registered cells require transcript_count >= message_count >= 2")
    quotient, remainder = divmod(transcript_count, message_count)
    matrix = [
        [Fraction() for _ in range(transcript_count)]
        for _ in range(message_count)
    ]
    column = 0
    for message in range(message_count):
        for _ in range(quotient):
            matrix[message][column] = Fraction(1, transcript_count)
            column += 1
    for residual in range(remainder):
        column = quotient * message_count + residual
        matrix[residual][column] = Fraction(
            remainder, message_count * transcript_count
        )
        for message in range(remainder, message_count):
            matrix[message][column] = Fraction(
                1, message_count * transcript_count
            )
    return validate_joint(matrix, message_count, transcript_count)


def occupancy_success_upper_bound(message_count: int, transcript_count: int) -> Fraction:
    """Enumerate decoder-column occupancies by exact dynamic programming."""

    if message_count < 2 or transcript_count < message_count:
        raise ValueError("invalid finite occupancy problem")
    states: dict[int, Fraction] = {0: Fraction()}
    for _ in range(message_count):
        next_states: dict[int, Fraction] = {}
        for used, score in states.items():
            for count in range(transcript_count - used + 1):
                contribution = min(
                    Fraction(1, message_count),
                    Fraction(count, transcript_count),
                )
                candidate = score + contribution
                total = used + count
                incumbent = next_states.get(total)
                if incumbent is None or candidate > incumbent:
                    next_states[total] = candidate
        states = next_states
    return states[transcript_count]


def one_shot_joint(alphabet_size: int) -> tuple[tuple[Fraction, ...], ...]:
    if alphabet_size < 2:
        raise ValueError("alphabet_size must be at least two")
    pairs = alphabet_size // 2
    matrix = [[Fraction() for _ in range(alphabet_size)] for _ in range(2)]
    for symbol in range(pairs):
        matrix[0][symbol] = Fraction(1, alphabet_size)
    for symbol in range(pairs, 2 * pairs):
        matrix[1][symbol] = Fraction(1, alphabet_size)
    if alphabet_size % 2:
        matrix[0][-1] = matrix[1][-1] = Fraction(1, 2 * alphabet_size)
    return validate_joint(matrix, 2, alphabet_size)


def product_joint(alphabet_size: int, block_length: int) -> tuple[tuple[Fraction, ...], ...]:
    factor = one_shot_joint(alphabet_size)
    messages = message_words(block_length)
    transcripts = transcript_words(alphabet_size, block_length)
    matrix: list[list[Fraction]] = []
    for message in messages:
        row: list[Fraction] = []
        for transcript in transcripts:
            mass = Fraction(1)
            for bit, symbol in zip(message, transcript):
                mass *= factor[bit][symbol]
            row.append(mass)
        matrix.append(row)
    return validate_joint(matrix, len(messages), len(transcripts))


def matrix_text(joint: Sequence[Sequence[Fraction]]) -> list[list[str]]:
    return [[fraction_text(value) for value in row] for row in joint]


def exact_cell(alphabet_size: int, block_length: int) -> dict[str, Any]:
    message_count = 2**block_length
    transcript_count = alphabet_size**block_length
    if message_count * transcript_count > 1000:
        raise ResourceStop("joint_entry_ceiling")
    if transcript_count > 125:
        raise ResourceStop("transcript_count_ceiling")
    if message_count * (transcript_count + 1) > 1008:
        raise ResourceStop("exact_dp_state_ceiling")

    unrestricted = unrestricted_joint(message_count, transcript_count)
    unrestricted_error = bayes_error_from_joint(unrestricted)
    occupancy_success = occupancy_success_upper_bound(message_count, transcript_count)
    occupancy_error = 1 - occupancy_success
    quotient, remainder = divmod(transcript_count, message_count)
    formula_error = Fraction(
        remainder * (message_count - remainder),
        message_count * transcript_count,
    )

    product = product_joint(alphabet_size, block_length)
    product_error = bayes_error_from_joint(product)
    one_shot_error = bayes_error_from_joint(one_shot_joint(alphabet_size))
    product_formula = 1 - (1 - one_shot_error) ** block_length

    return {
        "alphabet_size": alphabet_size,
        "block_length": block_length,
        "cell_id": f"m{alphabet_size}_n{block_length}",
        "message_count": message_count,
        "transcript_count": transcript_count,
        "unrestricted": {
            "bayes_error": fraction_text(unrestricted_error),
            "joint_mass": matrix_text(unrestricted),
            "occupancy_dp_error_bound": fraction_text(occupancy_error),
            "optimality_gap": fraction_text(unrestricted_error - occupancy_error),
            "quotient": quotient,
            "remainder": remainder,
            "theorem_error": fraction_text(formula_error),
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
            "predicted_strict_cell": alphabet_size % 2 == 1
            and block_length > 1,
            "prediction_matches": (unrestricted_error < product_error)
            == (alphabet_size % 2 == 1 and block_length > 1),
            "strict_unrestricted_advantage": unrestricted_error < product_error,
            "unrestricted_not_worse": unrestricted_error <= product_error,
        },
    }


def per_message_cover_control(message_count: int, transcript_count: int) -> dict[str, Any]:
    error = 1 - Fraction(1, message_count)
    return {
        "definition": "P(x|u)=1/M for every payload and transcript",
        "bayes_error": fraction_text(error),
        "blind_uniform_error": fraction_text(error),
        "zero_payload": True,
        "row_mass": fraction_text(Fraction(1, message_count)),
        "column_mass": fraction_text(Fraction(1, transcript_count)),
    }


def _conditional_coordinate_marginals(
    joint: Sequence[Sequence[Fraction]], alphabet_size: int, block_length: int
) -> list[list[list[Fraction]]]:
    message_count = len(joint)
    transcripts = transcript_words(alphabet_size, block_length)
    output: list[list[list[Fraction]]] = []
    for row in joint:
        conditional = [message_count * value for value in row]
        coordinates: list[list[Fraction]] = []
        for coordinate in range(block_length):
            marginal = [Fraction() for _ in range(alphabet_size)]
            for mass, transcript in zip(conditional, transcripts):
                marginal[transcript[coordinate]] += mass
            coordinates.append(marginal)
        output.append(coordinates)
    return output


def global_only_pathology_control() -> dict[str, Any]:
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
    marginals = _conditional_coordinate_marginals(joint, 2, 2)
    benign = [Fraction(1, 2), Fraction(1, 2)]
    error = bayes_error_from_joint(joint)
    return {
        "alphabet_size": 2,
        "block_length": 2,
        "message_count": 4,
        "joint_mass": matrix_text(joint),
        "bayes_error": fraction_text(error),
        "blind_uniform_error": "3/4",
        "carries_information": error < Fraction(3, 4),
        "every_message_coordinate_marginal_is_uniform": all(
            marginal == benign
            for message in marginals
            for marginal in message
        ),
        "global_transcript_cover_exact": True,
        "full_per_message_transcript_cover": False,
    }


def control_pack(cells: Sequence[dict[str, Any]]) -> dict[str, Any]:
    n1 = [cell for cell in cells if cell["block_length"] == 1]
    n1_pass = len(n1) == 4 and all(
        cell["unrestricted"]["bayes_error"]
        == cell["product_memoryless"]["bayes_error"]
        == ("0/1" if cell["alphabet_size"] % 2 == 0 else f"1/{2 * cell['alphabet_size']}")
        for cell in n1
    )
    per_message = {
        cell["cell_id"]: per_message_cover_control(
            cell["message_count"], cell["transcript_count"]
        )
        for cell in cells
    }
    per_message_pass = bool(per_message) and all(
        record["zero_payload"]
        and record["bayes_error"] == record["blind_uniform_error"]
        for record in per_message.values()
    )
    pathology = global_only_pathology_control()
    return {
        "global_only_pathology": pathology,
        "n1_reproduction": {
            "pass": n1_pass,
            "registered_cells": [cell["cell_id"] for cell in n1],
        },
        "per_message_cover": {
            "pass": per_message_pass,
            "cells": per_message,
        },
    }


def metric_robustness_pack(
    cells: Sequence[dict[str, Any]], controls: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    relabeling_cells: list[str] = []
    relabeling_pass = bool(cells)
    for cell in cells:
        for arm_name in ("unrestricted", "product_memoryless"):
            arm = cell[arm_name]
            original = validate_joint(
                arm["joint_mass"], cell["message_count"], cell["transcript_count"]
            )
            permuted = tuple(
                tuple(reversed(row)) for row in reversed(original)
            )
            try:
                replay = validate_joint(
                    permuted, cell["message_count"], cell["transcript_count"]
                )
            except (TypeError, ValueError):
                relabeling_pass = False
            else:
                relabeling_pass = relabeling_pass and (
                    bayes_error_from_joint(replay)
                    == Fraction(arm["bayes_error"])
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
            (
                lookup[f"m{alphabet_size}_n1"]["comparison"][
                    "strict_unrestricted_advantage"
                ]
                is False
            )
            and all(
                lookup[f"m{alphabet_size}_n{block_length}"]["comparison"][
                    "strict_unrestricted_advantage"
                ]
                is True
                for block_length in (2, 3)
            )
            for alphabet_size in (3, 5)
        )

    monotonicity_pass = bool(cells) and all(
        cell["comparison"]["unrestricted_not_worse"] for cell in cells
    )
    pathology = controls.get("global_only_pathology", {})
    pathology_pass = bool(
        pathology.get("global_transcript_cover_exact") is True
        and pathology.get("every_message_coordinate_marginal_is_uniform") is True
        and pathology.get("carries_information") is True
        and pathology.get("full_per_message_transcript_cover") is False
    )
    per_message = controls.get("per_message_cover", {})
    clean_control_pass = per_message.get("pass") is True

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
            "pass": monotonicity_pass,
            "registered_cells": [cell["cell_id"] for cell in cells],
        },
        "P4_global_only_parity_pathology": {
            "family": "anti_gaming",
            "pass": pathology_pass,
            "registered_fixture": "m2_n2_four_payload_parity_duplicate",
        },
        "P5_per_message_cover_blind_control": {
            "family": "clean_control",
            "pass": clean_control_pass,
            "registered_cells": sorted(per_message.get("cells", {})),
        },
    }


def _downgraded_layers() -> dict[str, str]:
    return {
        "metric_robustness": "not_established",
        "task_result": "not_established",
        "measurement_reliability": "failed",
        "claim_support": "none",
        "operational_decision": "repair",
    }


def compile_result(
    manifest: dict[str, Any],
    source_binding: dict[str, Any],
    *,
    clock_ns: Callable[[], int] = time.monotonic_ns,
) -> dict[str, Any]:
    binding = validate_manifest_binding(manifest)
    start_ns = clock_ns()
    wall_limit_ns = manifest["budget"]["max_wall_seconds"] * 1_000_000_000
    traced_limit_bytes = manifest["budget"]["max_traced_python_mib"] * 1024 * 1024
    owned_trace = not tracemalloc.is_tracing()
    if owned_trace:
        tracemalloc.start()
    tracemalloc.reset_peak()
    cells: list[dict[str, Any]] = []
    status = "complete"
    stop_reason = "registered_grid_complete"

    for alphabet_size, block_length in FROZEN_CELLS:
        if clock_ns() - start_ns > wall_limit_ns:
            status = "stopped_resource"
            stop_reason = "wall_limit_before_next_cell"
            break
        try:
            cells.append(exact_cell(alphabet_size, block_length))
        except ResourceStop as error:
            status = "stopped_resource"
            stop_reason = str(error)
            break
        _, traced_peak = tracemalloc.get_traced_memory()
        if traced_peak > traced_limit_bytes:
            status = "stopped_resource"
            stop_reason = "traced_python_memory_limit_after_completed_cell"
            break
        if clock_ns() - start_ns > wall_limit_ns:
            status = "stopped_resource"
            stop_reason = "wall_limit_after_completed_cell"
            break

    controls = control_pack(cells) if status == "complete" else {}
    metric_robustness = (
        metric_robustness_pack(cells, controls) if status == "complete" else {}
    )
    elapsed_wall_ns = clock_ns() - start_ns
    _, traced_peak_bytes = tracemalloc.get_traced_memory()
    if owned_trace:
        tracemalloc.stop()
    if status == "complete" and elapsed_wall_ns > wall_limit_ns:
        status = "stopped_resource"
        stop_reason = "wall_limit_after_controls"
        controls = {}
        metric_robustness = {}
    if status == "complete" and traced_peak_bytes > traced_limit_bytes:
        status = "stopped_resource"
        stop_reason = "traced_python_memory_limit_after_controls"
        controls = {}
        metric_robustness = {}

    gates = {
        "G0_frozen_manifest_binding": all(binding.values()),
        "G1_registered_grid_complete": status == "complete"
        and tuple((cell["alphabet_size"], cell["block_length"]) for cell in cells)
        == FROZEN_CELLS,
        "G2_unrestricted_joint_feasibility": status == "complete"
        and all(
            cell["unrestricted"]["optimality_gap"] == "0/1"
            and cell["unrestricted"]["bayes_error"]
            == cell["unrestricted"]["theorem_error"]
            for cell in cells
        ),
        "G3_product_joint_and_formula": status == "complete"
        and all(
            cell["product_memoryless"]["bayes_error"]
            == cell["product_memoryless"]["tensor_formula_error"]
            for cell in cells
        ),
        "G4_registered_contrast_pattern": status == "complete"
        and all(
            cell["comparison"]["unrestricted_not_worse"]
            and cell["comparison"]["prediction_matches"]
            for cell in cells
        ),
        "G5_n1_reproduction": bool(controls)
        and controls["n1_reproduction"]["pass"],
        "G6_five_metric_robustness_probes": (
            tuple(metric_robustness) == FROZEN_METRIC_PROBE_IDS
            and all(record["pass"] for record in metric_robustness.values())
        ),
        "G7_exact_arithmetic_firewall": not contains_float(
            {"cells": cells, "controls": controls, "metric_robustness": metric_robustness}
        ),
    }
    passed = status == "complete" and all(gates.values())
    conclusion_layers = (
        {
            "metric_robustness": "five_frozen_probe_families_computed_awaiting_independent_replay",
            "task_result": "finite_global_cover_block_advantage_over_registered_product_subclass",
            "measurement_reliability": "awaiting_import_independent_verification",
            "claim_support": "pending_independent_verification",
            "operational_decision": "await_independent_verification",
        }
        if passed
        else _downgraded_layers()
    )
    result = {
        "schema_version": "asmp6_multiletter_tensorization_result_v0_3",
        "protocol_id": FROZEN_PROTOCOL_ID,
        "manifest_sha256": FROZEN_MANIFEST_CANONICAL_SHA256,
        "source_binding": source_binding,
        "resource_observations": {
            "canonical_result_bytes": 0,
            "completed_cells": len(cells),
            "elapsed_wall_ns": elapsed_wall_ns,
            "max_dp_state_positions_observed": max(
                (cell["message_count"] * (cell["transcript_count"] + 1) for cell in cells),
                default=0,
            ),
            "max_joint_entries_observed": max(
                (cell["message_count"] * cell["transcript_count"] for cell in cells),
                default=0,
            ),
            "max_transcript_count_observed": max(
                (cell["transcript_count"] for cell in cells), default=0
            ),
            "memory_measurement": "tracemalloc_peak_python_allocation_only",
            "traced_python_limit_bytes": traced_limit_bytes,
            "traced_python_peak_bytes": traced_peak_bytes,
            "wall_limit_ns": wall_limit_ns,
        },
        "status": status,
        "stop_reason": stop_reason,
        "gates": gates,
        "cells": cells,
        "controls": controls,
        "metric_robustness": metric_robustness,
        "conclusion_layers": conclusion_layers,
        "claim_boundary": list(FROZEN_CLAIM_BOUNDARY),
    }
    if set(result) != FROZEN_RESULT_FIELDS or contains_float(result):
        raise AssertionError("result schema or exact-arithmetic firewall failed")
    for _ in range(10):
        actual_size = len(canonical_json(result).encode("utf-8"))
        if result["resource_observations"]["canonical_result_bytes"] == actual_size:
            break
        result["resource_observations"]["canonical_result_bytes"] = actual_size
    else:
        raise AssertionError("artifact byte-count fixed point failed")
    return result


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


def source_commit_binding(source_commit: str) -> dict[str, Any]:
    validate_live_source_inventory()
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("source commit must be a full lowercase 40-hex commit")
    object_type = str(_git(["cat-file", "-t", source_commit], text=True))
    if object_type != "commit":
        raise ValueError("source object is not a commit")
    resolved = str(_git(["rev-parse", "--verify", f"{source_commit}^{{commit}}"], text=True))
    if resolved != source_commit:
        raise ValueError("source commit did not resolve exactly")
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
    listed_text = str(
        _git(
            ["ls-tree", "-r", "--name-only", source_commit, "--", directory_path],
            text=True,
            cwd=repo_root,
        )
    )
    listed_paths = {line for line in listed_text.splitlines() if line}
    expected_paths = {
        (relative_directory / filename).as_posix()
        for filename in FROZEN_SOURCE_FILES
    }
    if listed_paths != expected_paths:
        raise ValueError(
            "source commit directory is not the exact frozen eight-file set"
        )
    hashes: dict[str, dict[str, str]] = {}
    mismatches: list[str] = []
    for filename in FROZEN_SOURCE_FILES:
        current_path = HERE / filename
        relative_path = (relative_directory / filename).as_posix()
        tree_line = str(
            _git(
                ["ls-tree", source_commit, "--", relative_path],
                text=True,
                cwd=repo_root,
            )
        )
        try:
            metadata, listed_path = tree_line.split("\t", 1)
            mode, kind, blob_oid = metadata.split()
        except ValueError as error:
            raise ValueError(f"malformed Git tree entry for {filename}") from error
        if listed_path != relative_path or mode != "100644" or kind != "blob":
            raise ValueError(f"source entry is not a regular blob: {filename}")
        try:
            committed = subprocess.check_output(
                ["git", "show", f"{source_commit}:{relative_path}"], cwd=repo_root
            )
        except subprocess.CalledProcessError as error:
            raise ValueError(f"source file is absent from commit: {filename}") from error
        current = current_path.read_bytes()
        current_blob_oid = subprocess.run(
            ["git", "hash-object", "--stdin"],
            cwd=repo_root,
            check=True,
            input=current,
            capture_output=True,
        ).stdout.decode("ascii").strip()
        hashes[filename] = {
            "git_blob_oid": current_blob_oid,
            "sha256": sha256_bytes(current),
        }
        if current_blob_oid != blob_oid:
            mismatches.append(filename)
        if current != committed:
            mismatches.append(filename)
    if mismatches:
        raise ValueError(
            f"working source differs from commit: {sorted(set(mismatches))}"
        )
    return {
        "repo_relative_directory": directory_path,
        "source_commit": source_commit,
        "source_commit_is_ancestor_of_head": True,
        "source_commit_type": object_type,
        "source_files": hashes,
    }


def write_once_json(path: Path, value: Any, max_bytes: int = 1048576) -> None:
    payload = canonical_json(value).encode("utf-8")
    if len(payload) > max_bytes:
        raise ResourceStop("artifact_byte_ceiling")
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
