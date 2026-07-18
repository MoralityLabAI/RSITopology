"""Exact enumeration for a finite hidden-state identifiability theorem.

The model is a deterministic chain X -> H -> Y with maps h:X->H and g:H->Y.
Hidden labels are gauge: Sym(H) acts on h, g, and the intervention interface.
The registered observations are all environment outputs g(h(x)) and all hidden
intervention outputs g(a), considered modulo that one global relabeling.
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
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Iterator, Sequence


MapTuple = tuple[int, ...]
Signature = tuple[tuple[int, ...], tuple[int, ...]]
ModelCanonical = tuple[MapTuple, MapTuple]


def all_maps(domain_size: int, codomain_size: int) -> Iterator[MapTuple]:
    """Yield every map from a labelled finite domain to a labelled codomain."""

    if domain_size < 0 or codomain_size <= 0:
        raise ValueError("domain_size must be nonnegative and codomain_size positive")
    yield from itertools.product(range(codomain_size), repeat=domain_size)


def is_surjective(mapping: Sequence[int], codomain_size: int) -> bool:
    return len(set(mapping)) == codomain_size


def compose(h_map: Sequence[int], g_map: Sequence[int]) -> MapTuple:
    return tuple(g_map[hidden] for hidden in h_map)


def relabel_hidden(
    h_map: Sequence[int], g_map: Sequence[int], permutation: Sequence[int]
) -> ModelCanonical:
    """Apply old hidden label a -> new hidden label permutation[a]."""

    hidden_size = len(g_map)
    if sorted(permutation) != list(range(hidden_size)):
        raise ValueError("permutation is not a bijection of the hidden alphabet")
    h_new = tuple(permutation[value] for value in h_map)
    g_new_list = [-1] * hidden_size
    for old_label, new_label in enumerate(permutation):
        g_new_list[new_label] = g_map[old_label]
    return tuple(g_new_list), h_new


def observation_signature(
    h_map: Sequence[int], g_map: Sequence[int], output_size: int
) -> Signature:
    """Return the gauge-invariant intervention histogram and environment outputs."""

    fiber_sizes = tuple(sum(value == output for value in g_map) for output in range(output_size))
    return fiber_sizes, compose(h_map, g_map)


def canonical_model_and_gauge_count(
    h_map: Sequence[int], g_map: Sequence[int], output_size: int
) -> tuple[ModelCanonical, int]:
    """Canonicalize a model and exhaustively check observation gauge invariance."""

    base_signature = observation_signature(h_map, g_map, output_size)
    candidates: list[ModelCanonical] = []
    checked = 0
    for permutation in itertools.permutations(range(len(g_map))):
        g_new, h_new = relabel_hidden(h_map, g_map, permutation)
        if observation_signature(h_new, g_new, output_size) != base_signature:
            raise AssertionError("hidden relabeling changed the observation signature")
        candidates.append((g_new, h_new))
        checked += 1
    return min(candidates), checked


def canonical_model(h_map: Sequence[int], g_map: Sequence[int]) -> ModelCanonical:
    candidates = [
        relabel_hidden(h_map, g_map, permutation)
        for permutation in itertools.permutations(range(len(g_map)))
    ]
    return min(candidates)


@lru_cache(maxsize=None)
def stirling_second(n: int, k: int) -> int:
    """Stirling number S(n,k), with its standard total boundary conventions."""

    if n < 0 or k < 0:
        return 0
    if n == 0:
        return 1 if k == 0 else 0
    if k == 0 or k > n:
        return 0
    return stirling_second(n - 1, k - 1) + k * stirling_second(n - 1, k)


def restricted_bell(n: int, maximum_blocks: int) -> int:
    return sum(stirling_second(n, blocks) for blocks in range(0, maximum_blocks + 1))


def predicted_orbit_count(signature: Signature, surjective_hidden: bool) -> int:
    """Count compatible model orbits from the observation-fiber partition theorem."""

    hidden_fiber_sizes, environment_outputs = signature
    result = 1
    for output, hidden_count in enumerate(hidden_fiber_sizes):
        input_count = sum(value == output for value in environment_outputs)
        if surjective_hidden:
            factor = stirling_second(input_count, hidden_count)
        else:
            factor = restricted_bell(input_count, hidden_count)
        result *= factor
    return result


def enumerate_configuration(
    input_size: int, hidden_size: int, output_size: int
) -> dict[str, object]:
    unrestricted: dict[Signature, set[ModelCanonical]] = defaultdict(set)
    surjective: dict[Signature, set[ModelCanonical]] = defaultdict(set)
    model_count = 0
    surjective_model_count = 0
    gauge_transform_checks = 0

    for g_map in all_maps(hidden_size, output_size):
        for h_map in all_maps(input_size, hidden_size):
            signature = observation_signature(h_map, g_map, output_size)
            canonical, checked = canonical_model_and_gauge_count(h_map, g_map, output_size)
            gauge_transform_checks += checked
            unrestricted[signature].add(canonical)
            model_count += 1
            if is_surjective(h_map, hidden_size):
                surjective[signature].add(canonical)
                surjective_model_count += 1

    mismatches: list[dict[str, object]] = []
    for signature, orbits in unrestricted.items():
        predicted = predicted_orbit_count(signature, surjective_hidden=False)
        if len(orbits) != predicted:
            mismatches.append(
                {
                    "mode": "unrestricted",
                    "signature": signature,
                    "observed": len(orbits),
                    "predicted": predicted,
                }
            )
    for signature, orbits in surjective.items():
        predicted = predicted_orbit_count(signature, surjective_hidden=True)
        if len(orbits) != predicted:
            mismatches.append(
                {
                    "mode": "surjective_hidden",
                    "signature": signature,
                    "observed": len(orbits),
                    "predicted": predicted,
                }
            )

    expected_model_count = (output_size**hidden_size) * (hidden_size**input_size)
    expected_surjective_model_count = (
        (output_size**hidden_size)
        * math.factorial(hidden_size)
        * stirling_second(input_size, hidden_size)
    )
    expected_gauge_transform_checks = expected_model_count * math.factorial(hidden_size)
    return {
        "input_size": input_size,
        "hidden_size": hidden_size,
        "output_size": output_size,
        "model_count": model_count,
        "surjective_hidden_model_count": surjective_model_count,
        "unrestricted_signature_count": len(unrestricted),
        "surjective_signature_count": len(surjective),
        "unrestricted_ambiguous_signature_count": sum(len(orbits) > 1 for orbits in unrestricted.values()),
        "surjective_ambiguous_signature_count": sum(len(orbits) > 1 for orbits in surjective.values()),
        "gauge_transform_checks": gauge_transform_checks,
        "expected_model_count": expected_model_count,
        "expected_surjective_hidden_model_count": expected_surjective_model_count,
        "expected_gauge_transform_checks": expected_gauge_transform_checks,
        "universe_complete": model_count == expected_model_count
        and surjective_model_count == expected_surjective_model_count,
        "gauge_universe_complete": gauge_transform_checks == expected_gauge_transform_checks,
        "formula_mismatches": mismatches,
    }


def explicit_cut_counterexample() -> dict[str, object]:
    """Return and verify the registered smallest surjective active counterexample."""

    # X has four labelled environments; H has three states; Y has two states.
    g_map = (0, 0, 1)
    h_left = (0, 0, 1, 2)
    h_right = (0, 1, 1, 2)
    signature_left = observation_signature(h_left, g_map, output_size=2)
    signature_right = observation_signature(h_right, g_map, output_size=2)
    canonical_left = canonical_model(h_left, g_map)
    canonical_right = canonical_model(h_right, g_map)

    checks = {
        "same_registered_observation": signature_left == signature_right,
        "distinct_gauge_orbits": canonical_left != canonical_right,
        "left_hidden_map_surjective": is_surjective(h_left, 3),
        "right_hidden_map_surjective": is_surjective(h_right, 3),
        "output_map_surjective_and_nonconstant": is_surjective(g_map, 2),
        "all_hidden_do_values_registered": True,
        "all_input_environments_registered": True,
    }
    if not all(checks.values()):
        raise AssertionError(f"registered counterexample failed: {checks}")
    return {
        "X_size": 4,
        "H_size": 3,
        "Y_size": 2,
        "g": g_map,
        "h_left": h_left,
        "h_right": h_right,
        "observation_signature": signature_left,
        "left_canonical_orbit_representative": canonical_left,
        "right_canonical_orbit_representative": canonical_right,
        "compatible_surjective_orbit_count": predicted_orbit_count(
            signature_left, surjective_hidden=True
        ),
        "checks": checks,
    }


def bit_tuple(index: int, width: int) -> tuple[int, ...]:
    return tuple((index >> (width - 1 - coordinate)) & 1 for coordinate in range(width))


def bit_index(bits: Sequence[int]) -> int:
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value


def singleton_do_design(input_bits: int) -> list[list[int]]:
    """Rows for passive and all singleton-do output-count measurements."""

    columns = 1 << input_bits
    rows = [[1] * columns]
    for coordinate in range(input_bits):
        for fixed_value in (0, 1):
            rows.append(
                [
                    int(bit_tuple(index, input_bits)[coordinate] == fixed_value)
                    for index in range(columns)
                ]
            )
    return rows


def matrix_rank_exact(matrix: Sequence[Sequence[int]]) -> int:
    rows = [[Fraction(value) for value in row] for row in matrix]
    if not rows:
        return 0
    row_count = len(rows)
    column_count = len(rows[0])
    rank = 0
    for column in range(column_count):
        pivot = next((row for row in range(rank, row_count) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][column]
        rows[rank] = [value / pivot_value for value in rows[rank]]
        for row in range(row_count):
            if row == rank or not rows[row][column]:
                continue
            factor = rows[row][column]
            rows[row] = [left - factor * right for left, right in zip(rows[row], rows[rank])]
        rank += 1
        if rank == row_count:
            break
    return rank


def singleton_do_signature(table: Sequence[int], input_bits: int) -> tuple[int, ...]:
    return tuple(sum(weight * value for weight, value in zip(row, table)) for row in singleton_do_design(input_bits))


def coordinate_influences(table: Sequence[int], input_bits: int) -> tuple[int, ...]:
    influences = []
    for coordinate in range(input_bits):
        count = 0
        mask = 1 << (input_bits - 1 - coordinate)
        for index in range(1 << input_bits):
            if index & mask:
                continue
            if table[index] != table[index | mask]:
                count += 1
        influences.append(count)
    return tuple(influences)


def transform_star_table(
    table: Sequence[int], coordinate_permutation: Sequence[int], input_flips: Sequence[int]
) -> tuple[int, ...]:
    input_bits = len(coordinate_permutation)
    transformed = [-1] * (1 << input_bits)
    for old_index in range(1 << input_bits):
        old_bits = bit_tuple(old_index, input_bits)
        new_bits = tuple(
            old_bits[coordinate_permutation[new_coordinate]] ^ input_flips[new_coordinate]
            for new_coordinate in range(input_bits)
        )
        transformed[bit_index(new_bits)] = table[old_index]
    return tuple(transformed)


def canonical_star_table(table: Sequence[int], input_bits: int) -> tuple[int, ...]:
    candidates = []
    for permutation in itertools.permutations(range(input_bits)):
        for flips in itertools.product((0, 1), repeat=input_bits):
            candidates.append(transform_star_table(table, permutation, flips))
    return min(candidates)


def singleton_do_star_counterexample() -> dict[str, object]:
    """Verify that singleton-do cut coverage misses a 3-way Boolean interaction."""

    input_bits = 3
    f_ones = {0b011, 0b100, 0b111}
    g_ones = {0b011, 0b101, 0b110}
    f_table = tuple(int(index in f_ones) for index in range(1 << input_bits))
    g_table = tuple(int(index in g_ones) for index in range(1 << input_bits))
    design = singleton_do_design(input_bits)
    delta = tuple(left - right for left, right in zip(f_table, g_table))
    design_delta = tuple(sum(weight * value for weight, value in zip(row, delta)) for row in design)
    f_influences = coordinate_influences(f_table, input_bits)
    g_influences = coordinate_influences(g_table, input_bits)
    checks = {
        "same_passive_and_singleton_do_signature": singleton_do_signature(f_table, input_bits)
        == singleton_do_signature(g_table, input_bits),
        "distinct_input_gauge_orbits": canonical_star_table(f_table, input_bits)
        != canonical_star_table(g_table, input_bits),
        "every_input_essential_in_f": all(value > 0 for value in f_influences),
        "every_input_essential_in_g": all(value > 0 for value in g_influences),
        "difference_is_in_design_kernel": all(value == 0 for value in design_delta),
        "singleton_design_rank_is_four_of_eight": matrix_rank_exact(design) == 4,
    }
    if not all(checks.values()):
        raise AssertionError(f"singleton-do star counterexample failed: {checks}")
    return {
        "input_bits": input_bits,
        "f_truth_table": f_table,
        "g_truth_table": g_table,
        "f_one_set": sorted(f_ones),
        "g_one_set": sorted(g_ones),
        "shared_measurement_signature": singleton_do_signature(f_table, input_bits),
        "f_coordinate_influences": f_influences,
        "g_coordinate_influences": g_influences,
        "design_shape": [len(design), len(design[0])],
        "design_rank": matrix_rank_exact(design),
        "design_nullity": len(design[0]) - matrix_rank_exact(design),
        "design_times_difference": design_delta,
        "checks": checks,
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
    """Bind a run to committed, path-clean registration inputs."""

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
    bindings: dict[str, dict[str, str]] = {}
    relative_paths: list[str] = []
    for path in paths:
        resolved = path.resolve()
        try:
            relative = resolved.relative_to(repo_root).as_posix()
        except ValueError as error:
            raise ValueError(f"sealed input is outside the git repository: {resolved}") from error
        relative_paths.append(relative)

    status = git(
        "status", "--porcelain", "--", *relative_paths, cwd=repo_root
    ).stdout.strip()
    if status:
        raise ValueError(f"sealed registration inputs are not clean at HEAD: {status}")

    for path, relative in zip(paths, relative_paths):
        committed = git(
            "show", f"HEAD:{relative}", text=False, cwd=repo_root
        ).stdout
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


def protocol_fixture_checks(
    protocol: dict[str, object], result: dict[str, object]
) -> dict[str, bool]:
    registered_chain = protocol["registered_counterexample"]
    observed_chain = result["counterexample"]
    registered_star = protocol["registered_singleton_do_counterexample"]
    observed_star = result["singleton_do_star_counterexample"]
    return {
        "chain_dimensions_match": [
            observed_chain["X_size"],
            observed_chain["H_size"],
            observed_chain["Y_size"],
        ]
        == [
            registered_chain["X_size"],
            registered_chain["H_size"],
            registered_chain["Y_size"],
        ],
        "chain_g_matches": list(observed_chain["g"]) == registered_chain["g"],
        "chain_h_left_matches": list(observed_chain["h_left"])
        == registered_chain["h_left"],
        "chain_h_right_matches": list(observed_chain["h_right"])
        == registered_chain["h_right"],
        "chain_expected_orbit_count_matches": observed_chain[
            "compatible_surjective_orbit_count"
        ]
        == registered_chain["expected_compatible_surjective_orbits"],
        "star_input_bits_match": observed_star["input_bits"] == 3,
        "star_f_one_set_matches": observed_star["f_one_set"] == registered_star["f_one_set"],
        "star_g_one_set_matches": observed_star["g_one_set"] == registered_star["g_one_set"],
        "star_design_rank_matches": observed_star["design_rank"]
        == registered_star["expected_design_rank"],
        "star_truth_table_dimension_matches": len(observed_star["f_truth_table"])
        == registered_star["truth_table_dimension"],
    }


def run_exhaustive(
    max_input_size: int, max_hidden_size: int, max_output_size: int
) -> dict[str, object]:
    configurations: list[dict[str, object]] = []
    for input_size in range(1, max_input_size + 1):
        for hidden_size in range(1, max_hidden_size + 1):
            for output_size in range(1, max_output_size + 1):
                configurations.append(
                    enumerate_configuration(input_size, hidden_size, output_size)
                )

    mismatches = [
        mismatch
        for configuration in configurations
        for mismatch in configuration["formula_mismatches"]
    ]
    boolean_active_failures = []
    for input_size in range(2, max_input_size + 1):
        # Check the active bijective g case directly.
        orbit_groups: dict[Signature, set[ModelCanonical]] = defaultdict(set)
        for g_map in all_maps(2, 2):
            if not is_surjective(g_map, 2):
                continue
            for h_map in all_maps(input_size, 2):
                if not is_surjective(h_map, 2):
                    continue
                signature = observation_signature(h_map, g_map, 2)
                orbit_groups[signature].add(canonical_model(h_map, g_map))
        for signature, orbits in orbit_groups.items():
            if len(orbits) != 1:
                boolean_active_failures.append(
                    {"input_size": input_size, "signature": signature, "orbits": len(orbits)}
                )

    counterexample = explicit_cut_counterexample()
    star_counterexample = singleton_do_star_counterexample()
    gates = {
        "G1_partition_formula_and_universe_census_exact_on_full_grid": len(mismatches) == 0
        and all(configuration["universe_complete"] for configuration in configurations),
        "G2_all_hidden_relabelings_preserve_observations": all(
            configuration["gauge_universe_complete"] for configuration in configurations
        ),
        "G3_registered_cut_counterexample_valid": all(counterexample["checks"].values()),
        "G4_binary_active_surjective_positive_control_identifiable": len(boolean_active_failures) == 0,
        "G5_singleton_do_star_design_has_verified_blind_pair": all(
            star_counterexample["checks"].values()
        ),
    }
    return {
        "schema_version": "asmp1_finite_chain_result_v0_1",
        "grid": {
            "input_size": [1, max_input_size],
            "hidden_size": [1, max_hidden_size],
            "output_size": [1, max_output_size],
        },
        "configuration_count": len(configurations),
        "total_models_enumerated": sum(c["model_count"] for c in configurations),
        "total_surjective_hidden_models": sum(
            c["surjective_hidden_model_count"] for c in configurations
        ),
        "total_observation_signatures_checked": sum(
            c["unrestricted_signature_count"] + c["surjective_signature_count"]
            for c in configurations
        ),
        "total_gauge_transform_checks": sum(
            c["gauge_transform_checks"] for c in configurations
        ),
        "formula_mismatch_count": len(mismatches),
        "formula_mismatches": mismatches,
        "binary_active_positive_control_failures": boolean_active_failures,
        "counterexample": counterexample,
        "singleton_do_star_counterexample": star_counterexample,
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "configuration_summaries": configurations,
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-input-size", type=int, default=5)
    parser.add_argument("--max-hidden-size", type=int, default=4)
    parser.add_argument("--max-output-size", type=int, default=3)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    argv_list = list(sys.argv[1:] if argv is None else argv)
    args = parse_args(argv_list)
    if not args.protocol.is_file():
        raise FileNotFoundError(args.protocol)
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if protocol.get("schema_version") != "asmp1_finite_chain_protocol_v0_1":
        raise ValueError("unexpected protocol schema")
    registered_grid = protocol.get("full_grid", {})
    requested_grid = {
        "input_size": [1, args.max_input_size],
        "hidden_size": [1, args.max_hidden_size],
        "output_size": [1, args.max_output_size],
    }
    for key, requested in requested_grid.items():
        if registered_grid.get(key) != requested:
            raise ValueError(
                f"requested {key} grid {requested} differs from registered "
                f"{registered_grid.get(key)}"
            )
    output_resolved = args.output.resolve()
    protected_inputs = {args.protocol.resolve(), Path(__file__).resolve()}
    if output_resolved in protected_inputs:
        raise ValueError("output path aliases a sealed input")
    checksum_path = args.output.with_suffix(args.output.suffix + ".sha256")
    if args.output.exists() or checksum_path.exists():
        raise FileExistsError("result or checksum already exists; outputs are write-once")
    theorem_path = Path(__file__).with_name("THEOREM_v0_1.md")
    sealed_inputs = [args.protocol, Path(__file__), theorem_path]
    pre_run_hashes = {str(path.resolve()): sha256(path) for path in sealed_inputs}
    registration = git_registration_binding(sealed_inputs)
    result = run_exhaustive(
        max_input_size=args.max_input_size,
        max_hidden_size=args.max_hidden_size,
        max_output_size=args.max_output_size,
    )
    post_run_hashes = {str(path.resolve()): sha256(path) for path in sealed_inputs}
    if post_run_hashes != pre_run_hashes:
        raise RuntimeError("sealed inputs changed during enumeration")
    result["protocol_sha256"] = pre_run_hashes[str(args.protocol.resolve())]
    result["source_sha256"] = pre_run_hashes[str(Path(__file__).resolve())]
    result["theorem_sha256"] = pre_run_hashes[str(theorem_path.resolve())]
    result["registration"] = registration
    result["argv"] = argv_list
    result["protocol_fixture_checks"] = protocol_fixture_checks(protocol, result)
    result["gates"]["G6_protocol_fixtures_match_executed_objects"] = all(
        result["protocol_fixture_checks"].values()
    )
    result["gates"]["G7_write_once_non_aliasing_output_policy"] = True
    result["gates"]["G8_committed_registration_and_pre_post_hashes_bound"] = True
    result["all_gates_pass"] = all(result["gates"].values())
    result["environment"] = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "working_directory": str(Path.cwd().resolve()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with checksum_path.open("x", encoding="ascii", newline="\n") as handle:
        handle.write(f"{sha256(args.output)}  {args.output.name}\n")
    print(json.dumps({key: result[key] for key in (
        "configuration_count",
        "total_models_enumerated",
        "total_observation_signatures_checked",
        "total_gauge_transform_checks",
        "formula_mismatch_count",
        "all_gates_pass",
    )}, indent=2))
    return 0 if result["all_gates_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
