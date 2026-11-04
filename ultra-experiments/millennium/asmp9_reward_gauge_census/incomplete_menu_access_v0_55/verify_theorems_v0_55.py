"""Independent exact verification for ASMP-9 v0.55."""

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
REGISTRATION = HERE / "verification_registration_v0_55.json"
OUTPUT = HERE / "VERIFY_RESULT_v0_55.json"

X = ("a", "b", "c")
AB = ("a", "b")
AC = ("a", "c")
BC = ("b", "c")
ABC = ("a", "b", "c")
MENUS = (AB, AC, BC, ABC)
ORDERS = tuple(permutations(X))
L = "scalar_luce"
R = "random_utility_non_luce"
N = "no_random_utility_representation"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def domains():
    for size in range(1, 5):
        yield from combinations(MENUS, size)


def name(domain):
    labels = {AB: "ab", AC: "ac", BC: "bc", ABC: "abc"}
    return "+".join(labels[menu] for menu in domain)


def kernel(pair_ab, pair_ac, pair_bc, triple):
    return {
        (AB, "a"): Q(pair_ab), (AB, "b"): 1 - Q(pair_ab),
        (AC, "a"): Q(pair_ac), (AC, "c"): 1 - Q(pair_ac),
        (BC, "b"): Q(pair_bc), (BC, "c"): 1 - Q(pair_bc),
        (ABC, "a"): Q(triple[0]),
        (ABC, "b"): Q(triple[1]),
        (ABC, "c"): Q(triple[2]),
    }


def grid():
    pairs = tuple(Q(k, 6) for k in range(1, 6))
    triples = tuple(
        (Q(a, 6), Q(b, 6), Q(c, 6))
        for a in range(1, 6)
        for b in range(1, 6)
        for c in range(1, 6)
        if a + b + c == 6
    )
    for values in product(pairs, pairs, pairs, triples):
        yield kernel(*values)


def projection(full, domain):
    return {
        (menu, choice): full[(menu, choice)]
        for menu in domain for choice in menu
    }


def projection_key(partial):
    return tuple(sorted(partial.items()))


def scalar_weights(partial, domain):
    if any(value <= 0 for value in partial.values()):
        return None
    graph = {x: [] for x in X}
    for menu in domain:
        for x, y in combinations(menu, 2):
            ratio = partial[(menu, x)] / partial[(menu, y)]
            graph[x].append((y, ratio))
            graph[y].append((x, 1 / ratio))
    weights = {}
    for root in X:
        if root in weights:
            continue
        weights[root] = Q(1)
        pending = [root]
        while pending:
            x = pending.pop()
            for y, ratio in graph[x]:
                proposed = weights[x] / ratio
                if y in weights and weights[y] != proposed:
                    return None
                if y not in weights:
                    weights[y] = proposed
                    pending.append(y)
    for menu in domain:
        total = sum((weights[x] for x in menu), Q(0))
        if any(partial[(menu, x)] != weights[x] / total for x in menu):
            return None
    return weights


def rank(matrix):
    rows = [list(map(Q, row)) for row in matrix]
    if not rows:
        return 0
    row_index = 0
    for column in range(len(rows[0])):
        pivot = next(
            (r for r in range(row_index, len(rows)) if rows[r][column]),
            None,
        )
        if pivot is None:
            continue
        rows[row_index], rows[pivot] = rows[pivot], rows[row_index]
        scale = rows[row_index][column]
        rows[row_index] = [value / scale for value in rows[row_index]]
        for r in range(len(rows)):
            if r != row_index and rows[r][column]:
                factor = rows[r][column]
                rows[r] = [
                    left - factor * right
                    for left, right in zip(rows[r], rows[row_index])
                ]
        row_index += 1
    return row_index


def independent_rows(matrix):
    selected = []
    rows = []
    current_rank = 0
    for index, row in enumerate(matrix):
        candidate = rows + [row]
        candidate_rank = rank(candidate)
        if candidate_rank > current_rank:
            selected.append(index)
            rows.append(row)
            current_rank = candidate_rank
    return tuple(selected)


def solve_square(matrix, rhs):
    size = len(matrix)
    rows = [
        [Q(value) for value in row] + [Q(target)]
        for row, target in zip(matrix, rhs)
    ]
    for column in range(size):
        pivot = next(
            (r for r in range(column, size) if rows[r][column]),
            None,
        )
        if pivot is None:
            return None
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [value / scale for value in rows[column]]
        for r in range(size):
            if r != column and rows[r][column]:
                factor = rows[r][column]
                rows[r] = [
                    left - factor * right
                    for left, right in zip(rows[r], rows[column])
                ]
    return tuple(rows[i][-1] for i in range(size))


def system(partial, domain):
    matrix = [[Q(1) for _ in ORDERS]]
    rhs = [Q(1)]
    for menu in domain:
        for choice in menu:
            matrix.append([
                Q(int(next(x for x in order if x in menu) == choice))
                for order in ORDERS
            ])
            rhs.append(partial[(menu, choice)])
    return matrix, rhs


def rum_basic_mixtures(partial, domain):
    matrix, rhs = system(partial, domain)
    rows = independent_rows(matrix)
    reduced = [matrix[i] for i in rows]
    targets = [rhs[i] for i in rows]
    feasible = []
    for columns in combinations(range(6), len(rows)):
        square = [
            [reduced[r][column] for column in columns]
            for r in range(len(rows))
        ]
        values = solve_square(square, targets)
        if values is None or any(value < 0 for value in values):
            continue
        candidate = [Q(0) for _ in ORDERS]
        for column, value in zip(columns, values):
            candidate[column] = value
        if all(
            sum(a * b for a, b in zip(row, candidate)) == target
            for row, target in zip(matrix, rhs)
        ):
            mixture = tuple(candidate)
            if mixture not in feasible:
                feasible.append(mixture)
    return tuple(feasible)


def from_mixture(mixture):
    return {
        (menu, choice): sum(
            mixture[index]
            for index, order in enumerate(ORDERS)
            if next(x for x in order if x in menu) == choice
        )
        for menu in MENUS for choice in menu
    }


def bm_rum(full):
    for size in range(1, 4):
        for lower in combinations(X, size):
            missing = tuple(x for x in X if x not in lower)
            for choice in lower:
                value = Q(0)
                for k in range(len(missing) + 1):
                    for added in combinations(missing, k):
                        upper_set = set(lower).union(added)
                        upper = tuple(x for x in X if x in upper_set)
                        probability = (
                            Q(1) if len(upper) == 1 else full[(upper, choice)]
                        )
                        value += (-1 if k % 2 else 1) * probability
                if value < 0:
                    return False
    return True


def full_status(full):
    if scalar_weights(full, MENUS) is not None:
        return L
    return R if bm_rum(full) else N


def nonrum_extension(partial, domain):
    full = {}
    for menu in (AB, AC, BC):
        if menu in domain:
            for x in menu:
                full[(menu, x)] = partial[(menu, x)]
        else:
            full[(menu, menu[0])] = Q(1, 2)
            full[(menu, menu[1])] = Q(1, 2)
    if ABC not in domain:
        pair_a = full[(AB, "a")]
        full_a = (1 + pair_a) / 2
        full[(ABC, "a")] = full_a
        full[(ABC, "b")] = (1 - full_a) / 2
        full[(ABC, "c")] = (1 - full_a) / 2
    else:
        for x in ABC:
            full[(ABC, x)] = partial[(ABC, x)]
        missing = next(menu for menu in (AB, AC, BC) if menu not in domain)
        x, y = missing
        full[(missing, x)] = full[(ABC, x)] / 2
        full[(missing, y)] = 1 - full[(missing, x)]
    return full


def tier_set(partial, domain, mixtures, weights):
    if set(domain) == set(MENUS):
        return (full_status(partial),)
    if not mixtures:
        return (N,)
    if weights is None:
        return (R, N)
    return (L, R, N)


def nonluce_basic_exists(mixtures):
    raise RuntimeError("weights are required for a positive completion check")


def plackett_luce(weights):
    result = []
    for order in ORDERS:
        remaining = list(order)
        value = Q(1)
        while len(remaining) > 1:
            value *= weights[remaining[0]] / sum(
                (weights[x] for x in remaining), Q(0)
            )
            remaining.pop(0)
        result.append(value)
    return tuple(result)


def average_mixtures(mixtures):
    return tuple(
        sum((mixture[index] for mixture in mixtures), Q(0)) / len(mixtures)
        for index in range(len(ORDERS))
    )


def positive_nonluce_rum_exists(mixtures, weights):
    base = plackett_luce(weights)
    candidates = list(mixtures)
    candidates.append(average_mixtures(mixtures))
    for other in candidates:
        for epsilon in (Q(1, 4), Q(1, 2), Q(3, 4)):
            mixture = tuple(
                (1 - epsilon) * left + epsilon * right
                for left, right in zip(base, other)
            )
            full = from_mixture(mixture)
            if all(value > 0 for value in full.values()) and full_status(full) == R:
                return True
    return False


def positive_middle_rum_exists(mixtures):
    mixture = average_mixtures(mixtures)
    full = from_mixture(mixture)
    return all(value > 0 for value in full.values()) and full_status(full) == R


def domain_census():
    full_grid = tuple(grid())
    rows = []
    proper_counts = Counter()
    proper_projection_count = 0
    construction_failures = 0
    scalar_witness_failures = 0
    middle_witness_failures = 0
    solver_failures = 0
    for domain in domains():
        unique = {}
        for full in full_grid:
            partial = projection(full, domain)
            unique.setdefault(projection_key(partial), partial)
        tier_counts = Counter()
        scalar_count = 0
        rum_count = 0
        for partial in unique.values():
            weights = scalar_weights(partial, domain)
            mixtures = rum_basic_mixtures(partial, domain)
            scalar_count += weights is not None
            rum_count += bool(mixtures)
            tiers = tier_set(partial, domain, mixtures, weights)
            label = "|".join(tiers)
            tier_counts[label] += 1
            if set(domain) != set(MENUS):
                proper_counts[label] += 1
                proper_projection_count += 1
                constructed_none = nonrum_extension(partial, domain)
                construction_failures += (
                    projection(constructed_none, domain) != partial
                    or full_status(constructed_none) != N
                )
                if weights is not None:
                    scalar_witness_failures += not positive_nonluce_rum_exists(
                        mixtures, weights
                    )
                elif mixtures:
                    middle_witness_failures += not positive_middle_rum_exists(
                        mixtures
                    )
            if mixtures and any(sum(mix, Q(0)) != 1 for mix in mixtures):
                solver_failures += 1
        rows.append({
            "domain": name(domain),
            "menu_count": len(domain),
            "observed_dimension": sum(len(menu) - 1 for menu in domain),
            "complete": set(domain) == set(MENUS),
            "unique_projection_count": len(unique),
            "scalar_compatible_count": scalar_count,
            "rum_compatible_count": rum_count,
            "tier_set_counts": dict(sorted(tier_counts.items())),
        })
    return {
        "rows": rows,
        "proper_counts": dict(sorted(proper_counts.items())),
        "proper_projection_count": proper_projection_count,
        "construction_failures": construction_failures,
        "scalar_witness_failures": scalar_witness_failures,
        "middle_witness_failures": middle_witness_failures,
        "solver_failures": solver_failures,
    }


def validate_hashes(registration):
    rows = []
    for relative, expected in registration["source_sha256"].items():
        path = REPO / relative
        actual = sha256(path) if path.is_file() else None
        rows.append({
            "path": relative, "expected": expected, "actual": actual,
            "match": actual == expected,
        })
    return all(row["match"] for row in rows), rows


def run_tests(expected):
    command = [
        sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
        str(HERE / "test_incomplete_menu.py"),
        str(HERE / "test_verifier_v0_55.py"),
    ]
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command, cwd=REPO, env=environment, capture_output=True, text=True
    )
    output = (completed.stdout + completed.stderr).strip()
    return {
        "ok": completed.returncode == 0 and f"{expected} passed" in output,
        "expected": expected,
        "returncode": completed.returncode,
        "output": output,
    }


def main():
    if not REGISTRATION.is_file():
        raise FileNotFoundError("prospective registration is missing")
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    started = time.perf_counter()
    process = psutil.Process()
    integrity_ok, integrity_rows = validate_hashes(registration)
    tests = run_tests(registration["expected_test_count"])
    census = domain_census()
    domain_bytes = json.dumps(
        census["rows"], sort_keys=True, separators=(",", ":")
    ).encode()
    domain_hash = hashlib.sha256(domain_bytes).hexdigest()
    full_row = next(row for row in census["rows"] if row["complete"])
    gates = {
        "H0_source_integrity": integrity_ok,
        "T0_tests": tests["ok"],
        "D0_domain_lattice_completeness": (
            len(census["rows"]) == registration["expected_domain_count"]
            and sum(not row["complete"] for row in census["rows"])
            == registration["expected_proper_domain_count"]
            and census["proper_projection_count"]
            == registration["expected_proper_projection_count"]
            and domain_hash == registration["expected_domain_summary_sha256"]
        ),
        "E0_existential_compatibility": census["solver_failures"] == 0,
        "N0_non_rum_completion": census["construction_failures"] == 0,
        "R0_non_luce_rum_completion": (
            census["scalar_witness_failures"] == 0
            and census["middle_witness_failures"] == 0
        ),
        "TIER0_compatibility_set_trichotomy": (
            census["proper_counts"] == registration["expected_proper_tier_counts"]
        ),
        "FULL0_complete_domain_control": (
            full_row["tier_set_counts"] == registration["expected_full_tier_counts"]
        ),
    }
    elapsed = time.perf_counter() - started
    resident = process.memory_info().rss
    gates["RESOURCE"] = (
        elapsed < registration["resource_caps"]["seconds"]
        and resident < registration["resource_caps"]["resident_bytes"]
    )
    verified = all(gates.values())
    payload = {
        "schema": "asmp9-v0.55-verification-result-v1",
        "status": (
            "incomplete_menu_tier_identification_verified"
            if verified else "verification_failed"
        ),
        "verified": verified,
        "registration_sha256": sha256(REGISTRATION),
        "source_commit": registration["source_commit"],
        "gates": gates,
        "source_integrity": integrity_rows,
        "tests": tests,
        "census": {
            "domain_count": len(census["rows"]),
            "proper_projection_count": census["proper_projection_count"],
            "proper_tier_counts": census["proper_counts"],
            "domain_summary_sha256": domain_hash,
            "construction_failures": census["construction_failures"],
            "scalar_witness_failures": census["scalar_witness_failures"],
            "middle_witness_failures": census["middle_witness_failures"],
            "solver_failures": census["solver_failures"],
            "domains": census["rows"],
        },
        "resource": {
            "elapsed_seconds": round(elapsed, 6),
            "resident_bytes": resident,
            "workers": 1,
        },
        "claim_boundary": registration["claim_boundary"],
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
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
