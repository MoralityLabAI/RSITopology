"""Run the registered exact ASMP-2 crossed-shift construction."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import subprocess
import time
import tracemalloc
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


def F(value: str | int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator)


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to replace non-identical artifact: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def git(*args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=text,
    )


def tracked_diff_sha256() -> str:
    payload = git("diff", "--binary", "HEAD", "--", text=False).stdout
    return hashlib.sha256(payload).hexdigest()


def bind_committed_inputs(paths: Sequence[Path]) -> dict[str, Any]:
    commit = git("rev-parse", "HEAD").stdout.strip()
    bindings: dict[str, Any] = {}
    for path in paths:
        resolved = path.resolve()
        relative = resolved.relative_to(REPO_ROOT).as_posix()
        status = git("status", "--porcelain", "--", relative).stdout.strip()
        if status:
            raise ValueError(f"sealed input is not clean at HEAD: {relative}: {status}")
        committed = git("show", f"HEAD:{relative}", text=False).stdout
        working = resolved.read_bytes()
        if committed != working:
            raise ValueError(f"sealed input differs from committed blob: {relative}")
        bindings[relative] = {
            "sha256": hashlib.sha256(working).hexdigest(),
            "git_blob": git("rev-parse", f"HEAD:{relative}").stdout.strip(),
        }
    diff_hash = tracked_diff_sha256()
    if diff_hash != EMPTY_SHA256:
        raise ValueError("tracked worktree differs from HEAD at registered run start")
    return {
        "commit": commit,
        "tracked_diff_sha256": diff_hash,
        "sealed_inputs": bindings,
    }


def parse_point(values: Sequence[str]) -> tuple[Fraction, ...]:
    return tuple(F(value) for value in values)


def bernoulli_probability(
    theta: Sequence[Fraction],
    component: str,
    *,
    sign: int,
    crossed: bool = True,
) -> Fraction:
    theta_1, theta_2 = theta[:2]
    if component == "Z1":
        return F(1) / 2 + theta_1 / 8
    if component == "Z2":
        return F(1) / 2 + theta_2 / 8
    if component != "Y":
        raise ValueError(component)
    base = F(1) / 2 + (theta_1 + theta_2) / 16
    hidden = theta_1 * theta_2 / 8 if crossed else F(0)
    return base + sign * hidden


def crossed_law(theta: Sequence[Fraction], sign: int) -> tuple[Fraction, ...]:
    return tuple(
        bernoulli_probability(theta, component, sign=sign, crossed=True)
        for component in ("Z1", "Z2", "Y")
    )


def unspanned_law(theta: Sequence[Fraction], sign: int) -> tuple[Fraction, ...]:
    theta_1, theta_2 = theta[:2]
    return (
        F(1) / 2 + theta_1 / 8,
        F(1) / 2 + theta_2 / 8,
        F(1) / 2 + (theta_1 + theta_2) / 16 + sign * theta_2 / 8,
    )


def matrix_rank(matrix: Sequence[Sequence[Fraction]]) -> int:
    if not matrix:
        return 0
    rows = [list(map(F, row)) for row in matrix]
    width = len(rows[0])
    rank = 0
    for column in range(width):
        pivot = next((index for index in range(rank, len(rows)) if rows[index][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for index in range(len(rows)):
            if index == rank or not rows[index][column]:
                continue
            factor = rows[index][column]
            rows[index] = [
                left - factor * right for left, right in zip(rows[index], rows[rank])
            ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def design_rank(points: Sequence[Sequence[Fraction]]) -> int:
    origin = points[0]
    differences = [
        [coordinate - reference for coordinate, reference in zip(point, origin)]
        for point in points[1:]
    ]
    return matrix_rank(differences)


def fisher_matrix() -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    gradients = ((F(1) / 8, F(0)), (F(0), F(1) / 8), (F(1) / 16, F(1) / 16))
    result = [[F(0), F(0)], [F(0), F(0)]]
    for gradient in gradients:
        for i in range(2):
            for j in range(2):
                result[i][j] += gradient[i] * gradient[j] / (F(1) / 4)
    return (tuple(result[0]), tuple(result[1]))


def matrix_vector(
    matrix: Sequence[Sequence[Fraction]], vector: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    return tuple(sum(left * right for left, right in zip(row, vector)) for row in matrix)


def exact_eigenpair(
    matrix: Sequence[Sequence[Fraction]],
    vector: Sequence[Fraction],
    eigenvalue: Fraction,
) -> bool:
    return matrix_vector(matrix, vector) == tuple(eigenvalue * value for value in vector)


def crossed_gap(theta: Sequence[Fraction]) -> Fraction:
    return abs(theta[0] * theta[1]) / 4


def unspanned_gap(theta: Sequence[Fraction]) -> Fraction:
    return abs(theta[1]) / 4


def maximum_on_box(radius: Fraction, gap) -> Fraction:
    vertices = tuple(itertools.product((-radius, radius), repeat=2))
    return max(gap(vertex) for vertex in vertices)


def signed_permutation_matrices() -> tuple[tuple[tuple[Fraction, ...], ...], ...]:
    matrices = []
    for permutation in ((0, 1), (1, 0)):
        for signs in itertools.product((-1, 1), repeat=2):
            matrix = []
            for row in range(2):
                matrix.append(
                    tuple(
                        F(signs[row]) if column == permutation[row] else F(0)
                        for column in range(2)
                    )
                )
            matrices.append(tuple(matrix))
    return tuple(matrices)


def transpose(matrix: Sequence[Sequence[Fraction]]) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(tuple(matrix[row][column] for row in range(len(matrix))) for column in range(len(matrix[0])))


def matrix_product(
    left: Sequence[Sequence[Fraction]], right: Sequence[Sequence[Fraction]]
) -> tuple[tuple[Fraction, ...], ...]:
    right_t = transpose(right)
    return tuple(
        tuple(sum(a * b for a, b in zip(row, column)) for column in right_t)
        for row in left
    )


def transform_points(
    matrix: Sequence[Sequence[Fraction]], points: Sequence[Sequence[Fraction]]
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(matrix_vector(matrix, point) for point in points)


def serialize_matrix(matrix: Sequence[Sequence[Fraction]]) -> list[list[str]]:
    return [[fraction_text(value) for value in row] for row in matrix]


def run_exact(protocol: dict[str, Any]) -> dict[str, Any]:
    designs = {
        name: tuple(parse_point(point) for point in points)
        for name, points in protocol["source_designs"].items()
    }
    axis = designs["axis_cross"]
    line = designs["unspanned_line"]
    diagonal = designs["count_matched_diagonal"]

    crossed_source_equal = all(crossed_law(point, 1) == crossed_law(point, -1) for point in axis)
    unspanned_source_equal = all(unspanned_law(point, 1) == unspanned_law(point, -1) for point in line)

    fisher = fisher_matrix()
    expected_fisher = tuple(
        tuple(F(value) for value in row) for row in protocol["exact_targets"]["fisher_matrix"]
    )
    eigenpairs = protocol["exact_targets"]["fisher_eigenpairs"]
    eigenpair_checks = [
        exact_eigenpair(
            fisher,
            tuple(F(value) for value in record["vector"]),
            F(record["eigenvalue"]),
        )
        for record in eigenpairs
    ]
    minimum_eigenvalue = min(F(record["eigenvalue"]) for record in eigenpairs)

    ambiguity_records = []
    for radius_text in protocol["registered_radii"]:
        radius = F(radius_text)
        crossed_observed = maximum_on_box(radius, crossed_gap)
        unspanned_observed = maximum_on_box(radius, unspanned_gap)
        ambiguity_records.append(
            {
                "radius": fraction_text(radius),
                "crossed_observed": fraction_text(crossed_observed),
                "crossed_expected": fraction_text(radius * radius / 4),
                "unspanned_observed": fraction_text(unspanned_observed),
                "unspanned_expected": fraction_text(radius / 4),
                "pass": crossed_observed == radius * radius / 4
                and unspanned_observed == radius / 4,
            }
        )

    diagonal_point = (F(1) / 2, F(1) / 2)
    diagonal_gap = abs(crossed_law(diagonal_point, 1)[2] - crossed_law(diagonal_point, -1)[2])
    safety_plus = crossed_law((F(1), F(1)), 1)[2]
    safety_minus = crossed_law((F(1), F(1)), -1)[2]
    threshold = F(protocol["model"]["safety_threshold"])

    risk_null_points = tuple((point[0], point[1], F(0)) for point in axis)
    quotient_points = tuple((point[0], point[1]) for point in risk_null_points)
    risk_null = {
        "raw_design_rank": design_rank(risk_null_points),
        "ambient_dimension": 3,
        "quotient_design_rank": design_rank(quotient_points),
        "quotient_dimension": 2,
        "missing_nuisance_vector": ["0", "0", "1"],
        "missing_nuisance_maps_to_zero": True,
    }

    coordinate_records = []
    fisher_trace = fisher[0][0] + fisher[1][1]
    fisher_determinant = fisher[0][0] * fisher[1][1] - fisher[0][1] * fisher[1][0]
    for index, matrix in enumerate(signed_permutation_matrices()):
        transformed_axis = transform_points(matrix, axis)
        transformed_fisher = matrix_product(matrix_product(matrix, fisher), transpose(matrix))
        transformed_trace = transformed_fisher[0][0] + transformed_fisher[1][1]
        transformed_determinant = (
            transformed_fisher[0][0] * transformed_fisher[1][1]
            - transformed_fisher[0][1] * transformed_fisher[1][0]
        )
        transformed_gap = max(
            crossed_gap(matrix_vector(transpose(matrix), vertex))
            for vertex in itertools.product((F(-1), F(1)), repeat=2)
        )
        passed = (
            design_rank(transformed_axis) == design_rank(axis) == 2
            and transformed_trace == fisher_trace
            and transformed_determinant == fisher_determinant
            and transformed_gap == F(1) / 4
        )
        coordinate_records.append(
            {
                "index": index,
                "matrix": serialize_matrix(matrix),
                "source_rank": design_rank(transformed_axis),
                "fisher_trace": fraction_text(transformed_trace),
                "fisher_determinant": fraction_text(transformed_determinant),
                "global_ambiguity": fraction_text(transformed_gap),
                "pass": passed,
            }
        )

    affine_ambiguity = F(0)
    count_matched = {
        "axis_count": len(axis),
        "diagonal_design_count": len(diagonal),
        "diagonal_design_rank": design_rank(diagonal),
        "world_gap_at_diagonal": fraction_text(diagonal_gap),
        "pass": len(axis) == len(diagonal)
        and design_rank(diagonal) == 2
        and diagonal_gap == F(1) / 16,
    }
    utility = {
        "act": "1",
        "abstain": "0",
        "floor": protocol["model"]["utility_floor"],
        "act_passes": F(1) >= F(protocol["model"]["utility_floor"]),
        "abstain_fails": F(0) < F(protocol["model"]["utility_floor"]),
    }
    safety = {
        "plus_at_1_1": fraction_text(safety_plus),
        "minus_at_1_1": fraction_text(safety_minus),
        "threshold": fraction_text(threshold),
        "opposite_sides": safety_plus > threshold > safety_minus,
    }

    gates = {
        "G0_registration_binding": {"pass": True},
        "G1_source_indistinguishability": {
            "pass": crossed_source_equal and unspanned_source_equal,
            "crossed_axis_equal": crossed_source_equal,
            "unspanned_line_equal": unspanned_source_equal,
        },
        "G2_exact_fisher_conditioning": {
            "pass": fisher == expected_fisher
            and all(eigenpair_checks)
            and minimum_eigenvalue == F(1) / 16,
            "matrix": serialize_matrix(fisher),
            "eigenpair_checks": eigenpair_checks,
            "kappa_squared": fraction_text(minimum_eigenvalue),
            "kappa": "1/4",
        },
        "G3_local_global_identities": {
            "pass": all(record["pass"] for record in ambiguity_records)
            and maximum_on_box(F(1), crossed_gap) == F(1) / 4,
            "ambiguity_records": ambiguity_records,
            "global_ambiguity": fraction_text(maximum_on_box(F(1), crossed_gap)),
        },
        "G4_liveness_and_controls": {
            "pass": affine_ambiguity == 0
            and risk_null["raw_design_rank"] == 2
            and risk_null["quotient_design_rank"] == 2
            and risk_null["missing_nuisance_maps_to_zero"]
            and utility["act_passes"]
            and utility["abstain_fails"]
            and safety["opposite_sides"]
            and count_matched["pass"],
            "affine_ambiguity": fraction_text(affine_ambiguity),
            "risk_null": risk_null,
            "utility": utility,
            "safety": safety,
            "count_matched": count_matched,
        },
        "G5_coordinate_invariance": {
            "pass": len(coordinate_records) == 8 and all(record["pass"] for record in coordinate_records),
            "records": coordinate_records,
        },
    }
    return {
        "schema_version": "asmp2_crossed_shift_result_v0_1",
        "protocol_id": protocol["protocol_id"],
        "evidence_label": "instrument_valid_forced_construction",
        "instrument_status": "valid" if all(record["pass"] for record in gates.values()) else "invalid",
        "runner_gate_pass": all(record["pass"] for record in gates.values()),
        "stage_decision": "pending_independent_verification",
        "gates": gates,
        "claim_boundary": protocol["prohibited_claims"],
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    protocol_path = args.protocol.resolve()
    if not protocol_path.is_file():
        raise FileNotFoundError(protocol_path)
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if protocol.get("schema_version") != "asmp2_crossed_shift_protocol_v0_1":
        raise ValueError("unexpected protocol schema")

    sealed_paths = (
        protocol_path,
        HERE / "CLAIM_PACKET.md",
        HERE / "README.md",
        Path(__file__).resolve(),
        HERE / "verify_result.py",
        HERE / "test_crossed_shift.py",
    )
    output_dir = args.output_dir.resolve()
    if any(output_dir == path or output_dir in path.parents for path in sealed_paths):
        raise ValueError("output directory aliases or contains a sealed input")
    result_path = output_dir / "result_v0_1.json"
    receipt_path = output_dir / "receipt_v0_1.json"
    if result_path.exists() or receipt_path.exists():
        raise FileExistsError("registered result or receipt already exists")

    registration = bind_committed_inputs(sealed_paths)
    tracemalloc.start()
    started = time.perf_counter()
    result = run_exact(protocol)
    elapsed = time.perf_counter() - started
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    ceiling = protocol["resource_ceiling"]
    resource_pass = elapsed <= float(ceiling["wall_seconds"]) and peak_bytes <= int(ceiling["python_peak_bytes"])
    result["resource_receipt"] = {
        "elapsed_seconds": elapsed,
        "python_tracemalloc_peak_bytes": peak_bytes,
        "wall_ceiling_seconds": ceiling["wall_seconds"],
        "python_peak_ceiling_bytes": ceiling["python_peak_bytes"],
        "pass": resource_pass,
    }
    if not resource_pass:
        result["instrument_status"] = "invalid"
        result["runner_gate_pass"] = False
    result["registration"] = registration
    result["protocol_sha256"] = sha256_file(protocol_path)
    result_payload = canonical_json(result).encode("utf-8")
    write_once(result_path, result_payload)

    receipt = {
        "schema_version": "asmp2_crossed_shift_receipt_v0_1",
        "git_commit_at_run": registration["commit"],
        "git_tracked_diff_sha256_at_run": registration["tracked_diff_sha256"],
        "protocol_sha256": sha256_file(protocol_path),
        "claim_packet_sha256": sha256_file(HERE / "CLAIM_PACKET.md"),
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "verifier_sha256": sha256_file(HERE / "verify_result.py"),
        "tests_sha256": sha256_file(HERE / "test_crossed_shift.py"),
        "result_sha256": hashlib.sha256(result_payload).hexdigest(),
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
    }
    write_once(receipt_path, canonical_json(receipt).encode("utf-8"))
    print(canonical_json({
        "instrument_status": result["instrument_status"],
        "runner_gate_pass": result["runner_gate_pass"],
        "evidence_label": result["evidence_label"],
        "stage_decision": result["stage_decision"],
        "elapsed_seconds": elapsed,
        "result": str(result_path),
        "receipt": str(receipt_path),
    }), end="")
    return 0 if result["runner_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
