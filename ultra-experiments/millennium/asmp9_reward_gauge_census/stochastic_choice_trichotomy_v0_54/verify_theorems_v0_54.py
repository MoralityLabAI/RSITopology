"""Independent exact verification for ASMP-9 v0.54."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction as Q
import hashlib
from itertools import combinations, permutations, product
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import psutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REGISTRATION = HERE / "verification_registration_v0_54.json"
OUTPUT = HERE / "VERIFY_RESULT_v0_54.json"
UNIVERSE = ("a", "b", "c")
RANKINGS = tuple(permutations(UNIVERSE))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def complete_kernel(pair_ab, pair_ac, pair_bc, triple):
    a, b, c = UNIVERSE
    return {
        ((a, b), a): Q(pair_ab),
        ((a, b), b): 1 - Q(pair_ab),
        ((a, c), a): Q(pair_ac),
        ((a, c), c): 1 - Q(pair_ac),
        ((b, c), b): Q(pair_bc),
        ((b, c), c): 1 - Q(pair_bc),
        ((a, b, c), a): Q(triple[0]),
        ((a, b, c), b): Q(triple[1]),
        ((a, b, c), c): Q(triple[2]),
    }


def menu_family(include_singletons=False):
    start = 1 if include_singletons else 2
    for size in range(start, 4):
        yield from combinations(UNIVERSE, size)


def p(kernel, menu, choice):
    if len(menu) == 1:
        return Q(1)
    return kernel[(menu, choice)]


def independent_luce(kernel):
    full = UNIVERSE
    weights = {x: p(kernel, full, x) for x in UNIVERSE}
    if any(value <= 0 for value in weights.values()):
        return None
    for menu in menu_family():
        denominator = sum((weights[x] for x in menu), Q(0))
        for x in menu:
            if p(kernel, menu, x) * denominator != weights[x]:
                return None
    return weights


def independent_bm_table(kernel):
    table = {}
    for lower in menu_family(include_singletons=True):
        missing = tuple(x for x in UNIVERSE if x not in lower)
        for choice in lower:
            total = Q(0)
            for size in range(len(missing) + 1):
                for added in combinations(missing, size):
                    upper_set = set(lower).union(added)
                    upper = tuple(x for x in UNIVERSE if x in upper_set)
                    total += (-1 if size % 2 else 1) * p(
                        kernel, upper, choice
                    )
            table[(choice, lower)] = total
    return table


def exact_unique_solution(matrix, rhs):
    width = len(matrix[0])
    rows = [
        [Q(value) for value in row] + [Q(value_rhs)]
        for row, value_rhs in zip(matrix, rhs)
    ]
    pivot_row = 0
    pivots = []
    for column in range(width):
        found = next(
            (r for r in range(pivot_row, len(rows)) if rows[r][column]),
            None,
        )
        if found is None:
            continue
        rows[pivot_row], rows[found] = rows[found], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for r in range(len(rows)):
            if r == pivot_row:
                continue
            factor = rows[r][column]
            if factor:
                rows[r] = [
                    left - factor * right
                    for left, right in zip(rows[r], rows[pivot_row])
                ]
        pivots.append(column)
        pivot_row += 1
    if any(
        all(value == 0 for value in row[:width]) and row[width] != 0
        for row in rows
    ):
        return None
    if len(pivots) != width:
        raise AssertionError("ranking system lost registered unique rank")
    solution = [Q(0) for _ in range(width)]
    for row_index, column in enumerate(pivots):
        solution[column] = rows[row_index][width]
    return tuple(solution)


def independent_ranking_mixture(kernel):
    matrix = [[Q(1) for _ in RANKINGS]]
    rhs = [Q(1)]
    for menu in menu_family():
        for choice in menu:
            matrix.append(
                [
                    Q(int(next(x for x in ranking if x in menu) == choice))
                    for ranking in RANKINGS
                ]
            )
            rhs.append(p(kernel, menu, choice))
    solution = exact_unique_solution(matrix, rhs)
    if solution is None or any(value < 0 for value in solution):
        return None
    mixture = dict(zip(RANKINGS, solution))
    for menu in menu_family():
        for choice in menu:
            reproduced = sum(
                value
                for ranking, value in mixture.items()
                if next(x for x in ranking if x in menu) == choice
            )
            if reproduced != p(kernel, menu, choice):
                raise AssertionError("mixture reproduction failure")
    return mixture


def independent_classification(kernel):
    weights = independent_luce(kernel)
    bm = independent_bm_table(kernel)
    bm_ok = all(value >= 0 for value in bm.values())
    mixture = independent_ranking_mixture(kernel)
    if bm_ok != (mixture is not None):
        return "classifier_disagreement", weights, mixture, bm
    if weights is not None:
        return "scalar_luce", weights, mixture, bm
    if mixture is not None:
        return "random_utility_non_luce", None, mixture, bm
    return "no_random_utility_representation", None, None, bm


def census_kernels():
    pairs = tuple(Q(k, 6) for k in range(1, 6))
    triples = tuple(
        (Q(a, 6), Q(b, 6), Q(c, 6))
        for a in range(1, 6)
        for b in range(1, 6)
        for c in range(1, 6)
        if a + b + c == 6
    )
    for pair_ab, pair_ac, pair_bc, triple in product(
        pairs, pairs, pairs, triples
    ):
        yield complete_kernel(pair_ab, pair_ac, pair_bc, triple)


def kernel_from_mixture(mixture):
    result = {}
    for menu in menu_family():
        for choice in menu:
            result[(menu, choice)] = sum(
                value
                for ranking, value in mixture.items()
                if next(x for x in ranking if x in menu) == choice
            )
    return result


def witnesses():
    scalar = complete_kernel(
        Q(1, 3), Q(1, 4), Q(2, 5), (Q(1, 6), Q(1, 3), Q(1, 2))
    )
    middle = kernel_from_mixture(
        {
            ("a", "b", "c"): Q(1, 3),
            ("b", "c", "a"): Q(1, 3),
            ("c", "a", "b"): Q(1, 3),
        }
    )
    none = complete_kernel(
        Q(1, 2), Q(1, 2), Q(1, 2), (Q(3, 4), Q(1, 8), Q(1, 8))
    )
    scalar_access = complete_kernel(
        Q(1, 2), Q(1, 2), Q(1, 2), (Q(1, 3), Q(1, 3), Q(1, 3))
    )
    return scalar, middle, none, scalar_access


def binary_projection(kernel):
    return tuple(
        sorted((event, value) for event, value in kernel.items() if len(event[0]) == 2)
    )


def validate_source_hashes(registration):
    rows = []
    for relative, expected in registration["source_sha256"].items():
        path = REPO / relative
        actual = sha256(path) if path.is_file() else None
        rows.append(
            {
                "path": relative,
                "expected": expected,
                "actual": actual,
                "match": actual == expected,
            }
        )
    return all(row["match"] for row in rows), rows


def run_tests(expected):
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        str(HERE / "test_stochastic_choice.py"),
        str(HERE / "test_verifier_v0_54.py"),
    ]
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        cwd=REPO,
        env=environment,
        capture_output=True,
        text=True,
    )
    output = (completed.stdout + completed.stderr).strip()
    return {
        "ok": completed.returncode == 0 and f"{expected} passed" in output,
        "expected": expected,
        "returncode": completed.returncode,
        "output": output,
    }


def run_census():
    counts = Counter()
    classifier_disagreements = 0
    mixture_reproduction_failures = 0
    certificate_failures = 0
    scalar_without_mixture = 0
    total = 0
    for kernel in census_kernels():
        status, weights, mixture, bm = independent_classification(kernel)
        total += 1
        counts[status] += 1
        classifier_disagreements += status == "classifier_disagreement"
        if status in ("scalar_luce", "random_utility_non_luce"):
            if mixture is None or any(value < 0 for value in mixture.values()):
                certificate_failures += 1
            if status == "scalar_luce" and weights is not None and mixture is None:
                scalar_without_mixture += 1
            if mixture is not None:
                reconstructed = kernel_from_mixture(mixture)
                mixture_reproduction_failures += reconstructed != kernel
        elif status == "no_random_utility_representation":
            certificate_failures += not any(value < 0 for value in bm.values())
    return {
        "kernel_count": total,
        "class_counts": dict(sorted(counts.items())),
        "classifier_disagreements": classifier_disagreements,
        "mixture_reproduction_failures": mixture_reproduction_failures,
        "certificate_failures": certificate_failures,
        "scalar_without_mixture": scalar_without_mixture,
    }


def main():
    if not REGISTRATION.is_file():
        raise FileNotFoundError("prospective registration is missing")
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    started = time.perf_counter()
    process = psutil.Process()

    integrity_ok, integrity_rows = validate_source_hashes(registration)
    tests = run_tests(registration["expected_test_count"])
    census = run_census()

    scalar, middle, none, scalar_access = witnesses()
    scalar_status, scalar_weights, scalar_mix, _ = independent_classification(scalar)
    middle_status, _, middle_mix, _ = independent_classification(middle)
    none_status, _, none_mix, none_bm = independent_classification(none)
    access_scalar_status, _, _, _ = independent_classification(scalar_access)
    exact_negative = none_bm[("a", ("a", "b"))]
    access_match = binary_projection(none) == binary_projection(scalar_access)

    elapsed = time.perf_counter() - started
    resident = process.memory_info().rss
    expected_counts = registration["expected_class_counts"]
    gates = {
        "H0_source_integrity": integrity_ok,
        "T0_tests": tests["ok"],
        "C0_census_completeness": (
            census["kernel_count"] == registration["expected_kernel_count"]
            and census["class_counts"] == expected_counts
        ),
        "E0_equivalent_rationalizability_decisions": (
            census["classifier_disagreements"] == 0
            and census["mixture_reproduction_failures"] == 0
            and census["certificate_failures"] == 0
        ),
        "S0_scalar_tier": (
            scalar_status == "scalar_luce"
            and scalar_weights == {"a": Q(1, 6), "b": Q(1, 3), "c": Q(1, 2)}
            and scalar_mix is not None
            and census["scalar_without_mixture"] == 0
        ),
        "R0_middle_tier": (
            middle_status == "random_utility_non_luce"
            and middle_mix is not None
            and census["class_counts"].get("random_utility_non_luce", 0) > 0
        ),
        "N0_no_object_tier": (
            none_status == "no_random_utility_representation"
            and none_mix is None
            and exact_negative == Q(-1, 4)
        ),
        "A0_access_insufficiency": (
            access_match
            and access_scalar_status == "scalar_luce"
            and none_status == "no_random_utility_representation"
        ),
        "RESOURCE": (
            elapsed < registration["resource_caps"]["seconds"]
            and resident < registration["resource_caps"]["resident_bytes"]
        ),
    }
    verified = all(gates.values())
    payload = {
        "schema": "asmp9-v0.54-verification-result-v1",
        "status": (
            "finite_stochastic_choice_trichotomy_verified"
            if verified
            else "verification_failed"
        ),
        "verified": verified,
        "registration_sha256": sha256(REGISTRATION),
        "source_commit": registration["source_commit"],
        "gates": gates,
        "source_integrity": integrity_rows,
        "tests": tests,
        "census": census,
        "witnesses": {
            "scalar_status": scalar_status,
            "scalar_weights": {
                key: qstr(value) for key, value in (scalar_weights or {}).items()
            },
            "middle_status": middle_status,
            "no_object_status": none_status,
            "no_object_certificate": {
                "choice": "a",
                "lower_menu": ["a", "b"],
                "value": qstr(exact_negative),
            },
            "binary_projection_match": access_match,
        },
        "resource": {
            "elapsed_seconds": round(elapsed, 6),
            "resident_bytes": resident,
            "workers": 1,
        },
        "claim_boundary": registration["claim_boundary"],
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if OUTPUT.exists():
        if OUTPUT.read_bytes() != encoded:
            raise FileExistsError("write-once result exists with different bytes")
    else:
        OUTPUT.write_bytes(encoded)
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

