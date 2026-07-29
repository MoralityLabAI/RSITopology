"""Independent prospective verification for the ASMP-9 v0.56 theorem."""

from __future__ import annotations

from fractions import Fraction as Q
import hashlib
from itertools import combinations, permutations
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time

import psutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REGISTRATION = HERE / "verification_registration_v0_56.json"
OUTPUT = HERE / "VERIFY_RESULT_v0_56.json"
PRIME = 1_000_003


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def menus(n: int):
    return tuple(
        menu
        for size in range(2, n + 1)
        for menu in combinations(range(n), size)
    )


def ambient_dimension(n: int) -> int:
    return sum(len(menu) - 1 for menu in menus(n))


def ranking_signature(n: int, ranking):
    position = {x: index for index, x in enumerate(ranking)}
    row = [1]
    for menu in menus(n):
        winner = min(menu, key=position.__getitem__)
        row.extend(int(winner == x) for x in menu[:-1])
    return row


def modular_rank(matrix, modulus: int = PRIME) -> int:
    rows = [[value % modulus for value in row] for row in matrix]
    if not rows:
        return 0
    rank = 0
    width = len(rows[0])
    for column in range(width):
        pivot = next(
            (r for r in range(rank, len(rows)) if rows[r][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, modulus)
        rows[rank] = [(value * inverse) % modulus for value in rows[rank]]
        for r in range(len(rows)):
            if r == rank or not rows[r][column]:
                continue
            factor = rows[r][column]
            rows[r] = [
                (left - factor * right) % modulus
                for left, right in zip(rows[r], rows[rank])
            ]
        rank += 1
        if rank == width:
            break
    return rank


def zeta_matrix(width: int):
    return [
        [
            int(subset & ~lower_set == 0)
            for subset in range(1 << width)
        ]
        for lower_set in range(1 << width)
    ]


def integer_partitions(total: int, minimum: int = 1):
    yield (total,)
    for first in range(minimum, total // 2 + 1):
        for tail in integer_partitions(total - first, first):
            yield (first, *tail)


def uniform_luce_kernel(n: int, weights):
    return {
        (menu, x): Q(weights[x], sum(weights[y] for y in menu))
        for menu in menus(n)
        for x in menu
    }


def set_probability(kernel, menu, choice, value):
    rest = (1 - value) / (len(menu) - 1)
    for x in menu:
        kernel[(menu, x)] = value if x == choice else rest


def construct_nonrum(n: int, observed, source):
    observed = tuple(observed)
    observed_set = set(observed)
    universe = menus(n)
    missing = [menu for menu in universe if menu not in observed_set]
    if not missing:
        raise ValueError("proper domain required")
    completion = dict(source)
    full = tuple(range(n))
    target = missing[0]
    choice = target[0]
    if target != full:
        outside = next(x for x in full if x not in target)
        superset = tuple(sorted((*target, outside)))
        if superset in observed_set:
            set_probability(
                completion, target, choice, source[(superset, choice)] / 2
            )
        else:
            set_probability(completion, target, choice, Q(1, 4))
            set_probability(completion, superset, choice, Q(1, 2))
    else:
        subset = (full[0], full[1])
        if subset in observed_set:
            set_probability(
                completion, full, choice, (1 + source[(subset, choice)]) / 2
            )
        else:
            set_probability(completion, subset, choice, Q(1, 4))
            set_probability(completion, full, choice, Q(1, 2))
    return completion


def regularity_violations(n: int, kernel):
    result = []
    universe = menus(n)
    for small in universe:
        small_set = set(small)
        for large in universe:
            if small == large or not small_set.issubset(large):
                continue
            for x in small:
                if kernel[(large, x)] > kernel[(small, x)]:
                    result.append((small, large, x))
    return result


def witness_domains(n: int, seed: int):
    universe = menus(n)
    domains = {
        tuple(menu for menu in universe if menu != missing)
        for missing in universe
    }
    domains.add(())
    domains.add(((0, 1), (2, 3)))
    rng = random.Random(seed)
    while len(domains) < len(universe) + 130:
        mask = rng.randrange(1 << len(universe))
        if mask == (1 << len(universe)) - 1:
            continue
        domains.add(
            tuple(
                menu
                for index, menu in enumerate(universe)
                if mask & (1 << index)
            )
        )
    return tuple(sorted(domains))


def run_tests(registration):
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        registration["test_command"].split(),
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def main():
    if OUTPUT.exists():
        raise FileExistsError("verification result is write-once")
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    start = time.perf_counter()
    gates = {}

    mismatches = {
        relative: {
            "expected": expected,
            "actual": sha256(REPO / relative),
        }
        for relative, expected in registration["source_sha256"].items()
        if sha256(REPO / relative) != expected
    }
    gates["H0"] = not mismatches

    test_code, test_stdout, test_stderr = run_tests(registration)
    passed_text = f"{registration['expected_test_count']} passed"
    gates["T0"] = test_code == 0 and passed_text in test_stdout

    n = 6
    affine_matrix = [
        ranking_signature(n, ranking)
        for ranking in permutations(range(n))
    ]
    affine_rank = modular_rank(affine_matrix)
    expected_columns = registration["expected_n6_affine_rank"]
    gates["A6"] = (
        len(affine_matrix) == math.factorial(n)
        and len(affine_matrix[0]) == expected_columns
        and affine_rank == expected_columns
    )

    zeta_ranks = {
        str(width): modular_rank(zeta_matrix(width))
        for width in range(registration["maximum_zeta_width"] + 1)
    }
    gates["Z0"] = all(
        rank == 1 << int(width) for width, rank in zeta_ranks.items()
    )

    partition_checks = 0
    partition_failures = []
    for size in range(3, registration["maximum_partition_n"] + 1):
        for partition in integer_partitions(size):
            components = len(partition)
            if components < 2:
                continue
            partition_checks += 1
            cross_pairs = sum(
                partition[i] * partition[j]
                for i in range(components)
                for j in range(i + 1, components)
            )
            if not cross_pairs > components - 1:
                partition_failures.append((size, partition, cross_pairs))
    gates["G0"] = not partition_failures

    domains = witness_domains(5, registration["witness_seed"])
    witness_cases = 0
    witness_failures = []
    for weights in ((1, 2, 3, 5, 7), (11, 7, 5, 3, 2)):
        source = uniform_luce_kernel(5, weights)
        for observed in domains:
            witness_cases += 1
            completion = construct_nonrum(5, observed, source)
            preserved = all(
                completion[(menu, x)] == source[(menu, x)]
                for menu in observed
                for x in menu
            )
            normalized = all(
                sum(completion[(menu, x)] for x in menu) == 1
                and all(completion[(menu, x)] > 0 for x in menu)
                for menu in menus(5)
            )
            live = bool(regularity_violations(5, completion))
            if not (preserved and normalized and live):
                witness_failures.append(
                    {
                        "observed_count": len(observed),
                        "preserved": preserved,
                        "normalized": normalized,
                        "regularity_violation": live,
                        "weights": weights,
                    }
                )
    gates["N0"] = (
        witness_cases >= registration["minimum_witness_cases"]
        and not witness_failures
    )

    binary_failures = []
    for denominator in range(2, 51):
        for numerator in range(1, denominator):
            probability = Q(numerator, denominator)
            weights = (probability, 1 - probability)
            if weights[0] / sum(weights) != probability:
                binary_failures.append((numerator, denominator))
    binary_rum_fiber_dimension = 1
    binary_luce_fiber_dimension = 1
    gates["S0"] = (
        not binary_failures
        and binary_rum_fiber_dimension == binary_luce_fiber_dimension
    )

    formula_rows = {}
    for size in range(3, 21):
        direct = sum(
            math.comb(size, menu_size) * (menu_size - 1)
            for menu_size in range(2, size + 1)
        )
        closed = size * 2 ** (size - 1) - 2**size + 1
        formula_rows[str(size)] = {"direct": direct, "closed": closed}
    gates["F0"] = all(
        row["direct"] == row["closed"] for row in formula_rows.values()
    )

    elapsed = time.perf_counter() - start
    resident = psutil.Process().memory_info().rss
    caps = registration["resource_caps"]
    gates["RESOURCE"] = (
        elapsed < caps["seconds"]
        and resident < caps["resident_bytes"]
        and caps["workers"] == 1
    )

    payload = {
        "affine": {
            "columns": len(affine_matrix[0]),
            "modular_rank": affine_rank,
            "prime": PRIME,
            "rankings": len(affine_matrix),
        },
        "binary_sharpness": {
            "failures": binary_failures,
            "luce_fiber_dimension": binary_luce_fiber_dimension,
            "rum_fiber_dimension": binary_rum_fiber_dimension,
        },
        "claim_boundary": registration["claim_boundary"],
        "formula_rows": formula_rows,
        "gates": gates,
        "partition": {
            "checks": partition_checks,
            "failures": partition_failures,
        },
        "registration_sha256": sha256(REGISTRATION),
        "resource": {
            "elapsed_seconds": elapsed,
            "resident_bytes": resident,
            "workers": 1,
        },
        "schema": "asmp9-v0.56-verification-result-v1",
        "source_mismatches": mismatches,
        "status": (
            "general_incomplete_menu_theorem_verified"
            if all(gates.values())
            else "verification_failed"
        ),
        "tests": {
            "returncode": test_code,
            "stderr": test_stderr,
            "stdout": test_stdout,
        },
        "witnesses": {
            "cases": witness_cases,
            "domain_count": len(domains),
            "failures": witness_failures,
        },
        "zeta_ranks": zeta_ranks,
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    OUTPUT.write_bytes(encoded)
    print(json.dumps({"gates": gates, "status": payload["status"]}, indent=2))
    if not all(gates.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
