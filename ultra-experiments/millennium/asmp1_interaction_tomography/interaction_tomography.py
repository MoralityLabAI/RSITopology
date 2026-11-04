"""Exact interaction-order tomography for finite Boolean mechanisms.

The order-r design observes conditional output sums under every intervention
fixing at most r parent coordinates. These measurements are exactly equivalent
to Walsh coefficients of degree at most r. Parent-coordinate permutations and
input-sign flips are gauge; semantic output signs are not.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Iterator, Sequence


PRIME = 2_147_483_647


def subsets_upto(n: int, order: int) -> tuple[int, ...]:
    if n < 0 or order < 0 or order > n:
        raise ValueError("require 0 <= order <= n")
    return tuple(
        subset
        for size in range(order + 1)
        for subset in range(1 << n)
        if subset.bit_count() == size
    )


def submasks(mask: int) -> tuple[int, ...]:
    values = []
    current = mask
    while True:
        values.append(current)
        if current == 0:
            break
        current = (current - 1) & mask
    return tuple(sorted(values))


def design_dimension(n: int, order: int) -> int:
    return sum(math.comb(n, size) for size in range(order + 1))


def minimum_structural_cost(n: int, order: int) -> int:
    return sum(size * math.comb(n, size) for size in range(1, order + 1))


def chi(character: int, assignment: int) -> int:
    return -1 if (character & assignment).bit_count() % 2 else 1


def intervention_rows(n: int, order: int) -> list[dict[str, object]]:
    columns = subsets_upto(n, order)
    rows: list[dict[str, object]] = []
    for fixed in subsets_upto(n, order):
        for assignment in submasks(fixed):
            vector = tuple(
                chi(character, assignment) if character & ~fixed == 0 else 0
                for character in columns
            )
            rows.append(
                {
                    "fixed_mask": fixed,
                    "assignment_mask": assignment,
                    "cost": fixed.bit_count(),
                    "vector": vector,
                }
            )
    return rows


def add_to_modular_basis(
    vector: Sequence[int], basis: dict[int, list[int]], prime: int = PRIME
) -> bool:
    row = [value % prime for value in vector]
    for pivot in sorted(basis):
        if row[pivot]:
            factor = row[pivot]
            pivot_row = basis[pivot]
            row = [
                (left - factor * right) % prime
                for left, right in zip(row, pivot_row)
            ]
    pivot = next((index for index, value in enumerate(row) if value), None)
    if pivot is None:
        return False
    inverse = pow(row[pivot], -1, prime)
    basis[pivot] = [(value * inverse) % prime for value in row]
    return True


def matrix_rank_mod(matrix: Sequence[Sequence[int]], prime: int = PRIME) -> int:
    basis: dict[int, list[int]] = {}
    for row in matrix:
        add_to_modular_basis(row, basis, prime)
    return len(basis)


def greedy_minimum_cost_basis(n: int, order: int) -> dict[str, object]:
    rows = sorted(
        intervention_rows(n, order),
        key=lambda row: (
            row["cost"],
            row["fixed_mask"],
            row["assignment_mask"],
        ),
    )
    basis: dict[int, list[int]] = {}
    selected: list[dict[str, object]] = []
    for row in rows:
        if add_to_modular_basis(row["vector"], basis):
            selected.append(row)
        if len(basis) == design_dimension(n, order):
            break
    return {
        "row_count": len(selected),
        "total_cost": sum(int(row["cost"]) for row in selected),
        "all_positive_assignment_count": sum(
            int(row["assignment_mask"] == 0) for row in selected
        ),
        "selected_rows": [
            {
                "fixed_mask": row["fixed_mask"],
                "assignment_mask": row["assignment_mask"],
                "cost": row["cost"],
            }
            for row in selected
        ],
        "matrix": [row["vector"] for row in selected],
    }


def condition_number(matrix: Sequence[Sequence[int]]) -> float:
    import numpy as np

    array = np.asarray(matrix, dtype=np.float64)
    return round(float(np.linalg.cond(array)), 12)


def fwht(values: Sequence[int]) -> tuple[int, ...]:
    transformed = list(values)
    stride = 1
    while stride < len(transformed):
        for start in range(0, len(transformed), stride * 2):
            for offset in range(stride):
                left = transformed[start + offset]
                right = transformed[start + offset + stride]
                transformed[start + offset] = left + right
                transformed[start + offset + stride] = left - right
        stride *= 2
    return tuple(transformed)


def truth_values(truth_mask: int, n: int) -> tuple[int, ...]:
    size = 1 << n
    if truth_mask < 0 or truth_mask >= (1 << size):
        raise ValueError("truth mask outside the n-parent Boolean universe")
    return tuple(1 if truth_mask & (1 << assignment) else -1 for assignment in range(size))


def walsh_coefficients(truth_mask: int, n: int) -> tuple[int, ...]:
    return fwht(truth_values(truth_mask, n))


def walsh_signature(truth_mask: int, n: int, order: int) -> tuple[int, ...]:
    coefficients = walsh_coefficients(truth_mask, n)
    return tuple(coefficients[subset] for subset in subsets_upto(n, order))


def condition_row_specs(n: int) -> list[dict[str, object]]:
    specs: list[dict[str, object]] = []
    for fixed in subsets_upto(n, n):
        fixed_size = fixed.bit_count()
        for assignment in submasks(fixed):
            assignment_truth_mask = 0
            for full_assignment in range(1 << n):
                if full_assignment & fixed == assignment:
                    assignment_truth_mask |= 1 << full_assignment
            specs.append(
                {
                    "fixed_mask": fixed,
                    "fixed_size": fixed_size,
                    "assignment_mask": assignment,
                    "truth_mask": assignment_truth_mask,
                    "rhs_terms": tuple(
                        (character, chi(character, assignment))
                        for character in submasks(fixed)
                    ),
                }
            )
    return specs


def conditional_walsh_mismatches_for_table(
    truth_mask: int,
    n: int,
    coefficients: Sequence[int] | None = None,
    specs: Sequence[dict[str, object]] | None = None,
) -> int:
    if coefficients is None:
        coefficients = walsh_coefficients(truth_mask, n)
    if specs is None:
        specs = condition_row_specs(n)
    mismatches = 0
    for spec in specs:
        fixed_size = int(spec["fixed_size"])
        subcube_size = 1 << (n - fixed_size)
        positive_count = (truth_mask & int(spec["truth_mask"])).bit_count()
        conditional_sum = 2 * positive_count - subcube_size
        lhs = (1 << fixed_size) * conditional_sum
        rhs = sum(
            coefficients[character] * sign
            for character, sign in spec["rhs_terms"]
        )
        mismatches += int(lhs != rhs)
    return mismatches


def signed_parent_assignment_maps(n: int) -> tuple[tuple[int, ...], ...]:
    maps = []
    for permutation in itertools.permutations(range(n)):
        for flip_mask in range(1 << n):
            assignment_map = []
            for old_assignment in range(1 << n):
                new_assignment = 0
                for new_coordinate, old_coordinate in enumerate(permutation):
                    old_bit = (old_assignment >> old_coordinate) & 1
                    flip_bit = (flip_mask >> new_coordinate) & 1
                    new_assignment |= (old_bit ^ flip_bit) << new_coordinate
                assignment_map.append(new_assignment)
            maps.append(tuple(assignment_map))
    if len(set(maps)) != math.factorial(n) * (1 << n):
        raise AssertionError("signed parent action did not produce the full B_n group")
    return tuple(maps)


def transform_truth_mask(truth_mask: int, assignment_map: Sequence[int]) -> int:
    transformed = 0
    remaining = truth_mask
    while remaining:
        lowest = remaining & -remaining
        old_assignment = lowest.bit_length() - 1
        transformed |= 1 << assignment_map[old_assignment]
        remaining ^= lowest
    return transformed


def canonical_orbit_map(n: int) -> tuple[list[int], dict[str, int]]:
    function_count = 1 << (1 << n)
    group_maps = signed_parent_assignment_maps(n)
    canonical = [-1] * function_count
    orbit_count = 0
    transformations = 0
    for truth_mask in range(function_count):
        if canonical[truth_mask] != -1:
            continue
        orbit = {
            transform_truth_mask(truth_mask, assignment_map)
            for assignment_map in group_maps
        }
        transformations += len(group_maps)
        representative = min(orbit)
        if representative != truth_mask:
            raise AssertionError("ascending orbit traversal did not begin at its representative")
        for member in orbit:
            canonical[member] = representative
        orbit_count += 1
    if any(value < 0 for value in canonical):
        raise AssertionError("gauge orbit census left unassigned truth tables")
    return canonical, {
        "group_size": len(group_maps),
        "orbit_count": orbit_count,
        "orbit_seed_transformations": transformations,
    }


def parity_truth_mask(n: int, character: int, sign: int = 1) -> int:
    if sign not in (-1, 1):
        raise ValueError("parity sign must be -1 or +1")
    truth_mask = 0
    for assignment in range(1 << n):
        if sign * chi(character, assignment) == 1:
            truth_mask |= 1 << assignment
    return truth_mask


def signature_collision_summary(
    n: int, order: int, canonical: Sequence[int]
) -> dict[str, object]:
    groups: dict[tuple[int, ...], list[object]] = {}
    for truth_mask in range(1 << (1 << n)):
        signature = walsh_signature(truth_mask, n, order)
        representative = canonical[truth_mask]
        if signature not in groups:
            groups[signature] = [1, representative]
            continue
        state = groups[signature]
        state[0] = int(state[0]) + 1
        orbit_state = state[1]
        if isinstance(orbit_state, int):
            if representative != orbit_state:
                state[1] = {orbit_state, representative}
        else:
            orbit_state.add(representative)

    labelled_ambiguous = 0
    quotient_ambiguous = 0
    max_tables = 0
    max_orbits = 0
    for table_count, orbit_state in groups.values():
        orbit_count = 1 if isinstance(orbit_state, int) else len(orbit_state)
        labelled_ambiguous += int(table_count > 1)
        quotient_ambiguous += int(orbit_count > 1)
        max_tables = max(max_tables, int(table_count))
        max_orbits = max(max_orbits, orbit_count)
    return {
        "order": order,
        "signature_count": len(groups),
        "labelled_ambiguous_signature_count": labelled_ambiguous,
        "quotient_ambiguous_signature_count": quotient_ambiguous,
        "maximum_tables_per_signature": max_tables,
        "maximum_gauge_orbits_per_signature": max_orbits,
        "labelled_identifiable": labelled_ambiguous == 0,
        "quotient_identifiable": quotient_ambiguous == 0,
    }


def parity_fixture_checks(
    n: int, order: int, canonical: Sequence[int]
) -> dict[str, object]:
    if order <= n - 2:
        first_character = (1 << (order + 1)) - 1
        second_character = (1 << (order + 2)) - 1
        first = parity_truth_mask(n, first_character)
        second = parity_truth_mask(n, second_character)
        checks = {
            "same_observed_signature": walsh_signature(first, n, order)
            == walsh_signature(second, n, order),
            "distinct_parent_gauge_orbits": canonical[first] != canonical[second],
            "degrees_are_r_plus_one_and_two": (
                first_character.bit_count(), second_character.bit_count()
            )
            == (order + 1, order + 2),
        }
        fixture_type = "distinct_degree_parity_obstruction"
    elif order == n - 1:
        character = (1 << n) - 1
        first = parity_truth_mask(n, character, sign=1)
        second = parity_truth_mask(n, character, sign=-1)
        checks = {
            "same_observed_signature": walsh_signature(first, n, order)
            == walsh_signature(second, n, order),
            "same_parent_gauge_orbit": canonical[first] == canonical[second],
            "labelled_tables_are_distinct": first != second,
        }
        fixture_type = "top_parity_gauge_collapse"
    else:
        raise ValueError("parity fixture only registered through order n-1")
    return {
        "n": n,
        "order": order,
        "fixture_type": fixture_type,
        "first_truth_mask": first,
        "second_truth_mask": second,
        "checks": checks,
        "passed": all(checks.values()),
    }


def analyze_boolean_census(n: int) -> dict[str, object]:
    canonical, orbit_metadata = canonical_orbit_map(n)
    specs = condition_row_specs(n)
    identity_mismatches = 0
    for truth_mask in range(1 << (1 << n)):
        coefficients = walsh_coefficients(truth_mask, n)
        identity_mismatches += conditional_walsh_mismatches_for_table(
            truth_mask, n, coefficients=coefficients, specs=specs
        )

    order_summaries = [
        signature_collision_summary(n, order, canonical)
        for order in range(n + 1)
    ]
    labelled_threshold = next(
        summary["order"] for summary in order_summaries if summary["labelled_identifiable"]
    )
    quotient_threshold = next(
        summary["order"] for summary in order_summaries if summary["quotient_identifiable"]
    )
    fixtures = [parity_fixture_checks(n, order, canonical) for order in range(n)]
    return {
        "n": n,
        "function_count": 1 << (1 << n),
        **orbit_metadata,
        "conditional_walsh_identity_mismatch_count": identity_mismatches,
        "labelled_identifiability_threshold": labelled_threshold,
        "quotient_identifiability_threshold": quotient_threshold,
        "order_summaries": order_summaries,
        "parity_fixtures": fixtures,
    }


def analyze_rank_basis_cell(n: int, order: int) -> dict[str, object]:
    rows = intervention_rows(n, order)
    matrix = [row["vector"] for row in rows]
    observed_rank = matrix_rank_mod(matrix)
    expected_rank = design_dimension(n, order)
    basis = greedy_minimum_cost_basis(n, order)
    basis_matrix = basis.pop("matrix")
    return {
        "n": n,
        "order": order,
        "candidate_row_count": len(rows),
        "expected_rank": expected_rank,
        "observed_modular_rank": observed_rank,
        "rank_exact": observed_rank == expected_rank,
        "minimum_basis": basis,
        "expected_minimum_cost": minimum_structural_cost(n, order),
        "minimum_basis_exact": basis["row_count"] == expected_rank
        and basis["total_cost"] == minimum_structural_cost(n, order)
        and basis["all_positive_assignment_count"] == expected_rank,
        "minimum_cost_basis_condition_number": condition_number(basis_matrix),
        "full_design_condition_number": condition_number(matrix),
    }


def run_registered() -> dict[str, object]:
    rank_cells = [
        analyze_rank_basis_cell(n, order)
        for n in range(1, 9)
        for order in range(0, min(n, 4) + 1)
    ]
    boolean_censuses = [analyze_boolean_census(n) for n in range(2, 5)]
    gates = {
        "G1_all_registered_design_ranks_exact": all(
            cell["rank_exact"] for cell in rank_cells
        ),
        "G2_conditional_sum_walsh_identity_exact": all(
            census["conditional_walsh_identity_mismatch_count"] == 0
            for census in boolean_censuses
        ),
        "G3_labelled_threshold_equals_n": all(
            census["labelled_identifiability_threshold"] == census["n"]
            for census in boolean_censuses
        ),
        "G4_parent_gauge_quotient_threshold_equals_n_minus_one": all(
            census["quotient_identifiability_threshold"] == census["n"] - 1
            for census in boolean_censuses
        ),
        "G5_registered_parity_fixtures_pass": all(
            fixture["passed"]
            for census in boolean_censuses
            for fixture in census["parity_fixtures"]
        ),
        "G6_minimum_weight_bases_match_analytic_cost": all(
            cell["minimum_basis_exact"] for cell in rank_cells
        ),
    }
    return {
        "schema_version": "asmp1_interaction_tomography_result_v0_1",
        "rank_basis_cell_count": len(rank_cells),
        "boolean_census_count": len(boolean_censuses),
        "total_boolean_functions_censused": sum(
            census["function_count"] for census in boolean_censuses
        ),
        "total_conditional_walsh_identity_mismatches": sum(
            census["conditional_walsh_identity_mismatch_count"]
            for census in boolean_censuses
        ),
        "rank_basis_cells": rank_cells,
        "boolean_censuses": boolean_censuses,
        "gates": gates,
        "all_gates_pass": all(gates.values()),
    }


def protocol_registration_checks(protocol: dict[str, object]) -> dict[str, bool]:
    object_spec = protocol.get("object", {})
    grid = protocol.get("registered_grid", {})
    rank_grid = grid.get("rank_and_basis", {})
    boolean_grid = grid.get("boolean_quotient_census", {})
    return {
        "status_registered_before_full_enumeration": protocol.get("status")
        == "registered_before_full_enumeration",
        "rank_n_grid_matches": rank_grid.get("n") == [1, 8],
        "rank_order_grid_matches": rank_grid.get("r") == "0..min(n,4)",
        "boolean_n_grid_matches": boolean_grid.get("n") == [2, 4],
        "boolean_order_grid_matches": boolean_grid.get("r") == "0..n",
        "boolean_function_universe_matches": boolean_grid.get("functions")
        == "all 2^(2^n) labelled Boolean truth tables",
        "gauge_matches": object_spec.get("gauge_group")
        == "B_n = Sym(n) semidirect (Z/2)^n acting by parent-coordinate permutations and input-sign flips; intervention labels transform with the same action",
        "semantic_outputs_match": object_spec.get("output_labels")
        == "semantic -1 and +1; output complementation is not gauge",
        "integer_measurement_semantics_match": object_spec.get("measurements")
        == "passive conditional sum and every perfect-intervention conditional sum fixing S with |S|<=r; integer sums are stored",
        "gate_universe_matches": set(protocol.get("gates", {}))
        == {f"G{index}" for index in range(1, 10)},
    }
def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def git_registration_binding(paths: Sequence[Path]) -> dict[str, object]:
    def git(
        *arguments: str, text: bool = True, cwd: Path | None = None
    ) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", *arguments],
            check=True,
            capture_output=True,
            text=text,
            cwd=cwd,
        )

    repo_root = Path(git("rev-parse", "--show-toplevel").stdout.strip()).resolve()
    commit = git("rev-parse", "HEAD").stdout.strip()
    relative_paths = []
    for path in paths:
        try:
            relative_paths.append(path.resolve().relative_to(repo_root).as_posix())
        except ValueError as error:
            raise ValueError(f"sealed input is outside repository: {path}") from error
    status = git(
        "status", "--porcelain", "--", *relative_paths, cwd=repo_root
    ).stdout.strip()
    if status:
        raise ValueError(f"sealed registration inputs are not clean at HEAD: {status}")
    bindings = {}
    for path, relative in zip(paths, relative_paths):
        committed = git("show", f"HEAD:{relative}", text=False, cwd=repo_root).stdout
        working_hash = sha256(path)
        committed_hash = sha256_bytes(committed)
        if working_hash != committed_hash:
            raise ValueError(f"working input differs from committed blob: {relative}")
        bindings[relative] = {
            "working_sha256": working_hash,
            "committed_blob_sha256": committed_hash,
        }
    return {
        "registration_commit": commit,
        "repository_root": str(repo_root),
        "sealed_inputs": bindings,
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    argv_list = list(sys.argv[1:] if argv is None else argv)
    args = parse_args(argv_list)
    if not args.protocol.is_file():
        raise FileNotFoundError(args.protocol)
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if protocol.get("schema_version") != "asmp1_interaction_tomography_protocol_v0_1":
        raise ValueError("unexpected protocol schema")
    registration_checks = protocol_registration_checks(protocol)
    if not all(registration_checks.values()):
        raise ValueError(f"protocol registration fields do not match runner: {registration_checks}")
    theorem_path = Path(__file__).with_name("THEOREM_v0_1.md")
    sealed_inputs = [args.protocol, Path(__file__), theorem_path]
    output_resolved = args.output.resolve()
    if output_resolved in {path.resolve() for path in sealed_inputs}:
        raise ValueError("output path aliases a sealed input")
    checksum_path = args.output.with_suffix(args.output.suffix + ".sha256")
    if args.output.exists() or checksum_path.exists():
        raise FileExistsError("result or checksum already exists; outputs are write-once")

    pre_run_hashes = {str(path.resolve()): sha256(path) for path in sealed_inputs}
    registration = git_registration_binding(sealed_inputs)
    result = run_registered()
    post_run_hashes = {str(path.resolve()): sha256(path) for path in sealed_inputs}
    if post_run_hashes != pre_run_hashes:
        raise RuntimeError("sealed inputs changed during enumeration")

    result["protocol_sha256"] = pre_run_hashes[str(args.protocol.resolve())]
    result["source_sha256"] = pre_run_hashes[str(Path(__file__).resolve())]
    result["theorem_sha256"] = pre_run_hashes[str(theorem_path.resolve())]
    result["registration"] = registration
    result["argv"] = argv_list
    result["protocol_registration_checks"] = registration_checks
    result["gates"]["G7_write_once_non_aliasing_output_policy"] = True
    result["gates"]["G8_committed_registration_and_pre_post_hashes_bound"] = True
    result["gates"]["G9_protocol_fields_match_executed_universe"] = all(
        registration_checks.values()
    )
    result["all_gates_pass"] = all(result["gates"].values())
    result["environment"] = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "working_directory": str(Path.cwd().resolve()),
    }
    try:
        import numpy as np

        result["environment"]["numpy"] = np.__version__
    except ImportError:
        result["environment"]["numpy"] = "unavailable"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with checksum_path.open("x", encoding="ascii", newline="\n") as handle:
        handle.write(f"{sha256(args.output)}  {args.output.name}\n")
    print(
        json.dumps(
            {
                "rank_basis_cell_count": result["rank_basis_cell_count"],
                "total_boolean_functions_censused": result[
                    "total_boolean_functions_censused"
                ],
                "total_conditional_walsh_identity_mismatches": result[
                    "total_conditional_walsh_identity_mismatches"
                ],
                "thresholds": {
                    census["n"]: {
                        "labelled": census["labelled_identifiability_threshold"],
                        "quotient": census["quotient_identifiability_threshold"],
                    }
                    for census in result["boolean_censuses"]
                },
                "all_gates_pass": result["all_gates_pass"],
            },
            indent=2,
        )
    )
    return 0 if result["all_gates_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
