from __future__ import annotations

from fractions import Fraction
from math import comb
from typing import Iterable


MU = Fraction(1, 5)
ERROR_LIMIT = Fraction(1, 20)
QUERY_GRID = (1, 3, 5, 7, 9)
RHO_GRID = (
    Fraction(0),
    Fraction(1, 100),
    Fraction(1, 50),
    Fraction(1, 20),
    Fraction(1, 10),
    Fraction(1, 5),
    Fraction(1, 3),
    Fraction(1, 2),
)


def rising(x: Fraction, n: int) -> Fraction:
    value = Fraction(1)
    for i in range(n):
        value *= x + i
    return value


def beta_binomial_distribution(n: int, rho: Fraction) -> tuple[Fraction, ...]:
    if n < 0:
        raise ValueError("n must be nonnegative")
    if not Fraction(0) <= rho < Fraction(1):
        raise ValueError("rho must lie in [0,1)")
    if rho == 0:
        return tuple(
            Fraction(comb(n, k)) * MU**k * (1 - MU) ** (n - k)
            for k in range(n + 1)
        )

    concentration = (1 - rho) / rho
    alpha = MU * concentration
    beta = (1 - MU) * concentration
    denominator = rising(alpha + beta, n)
    return tuple(
        Fraction(comb(n, k))
        * rising(alpha, k)
        * rising(beta, n - k)
        / denominator
        for k in range(n + 1)
    )


def convolve(left: Iterable[Fraction], right: Iterable[Fraction]) -> tuple[Fraction, ...]:
    a = tuple(left)
    b = tuple(right)
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return tuple(out)


def balanced_family_sizes(q: int, families: int) -> tuple[int, ...]:
    if q <= 0 or q % 2 == 0:
        raise ValueError("q must be positive and odd")
    if families <= 0 or families > q:
        raise ValueError("families must lie in [1,q]")
    base, remainder = divmod(q, families)
    return tuple(base + (i < remainder) for i in range(families))


def majority_error(q: int, families: int, rho: Fraction) -> Fraction:
    total = (Fraction(1),)
    for size in balanced_family_sizes(q, families):
        total = convolve(total, beta_binomial_distribution(size, rho))
    assert sum(total) == 1
    return sum(total[q // 2 + 1 :], Fraction(0))


def global_flip_error(_q: int) -> Fraction:
    return MU


def targeted_average_attack(n_atoms: int) -> dict[str, Fraction]:
    if n_atoms <= 0:
        raise ValueError("n_atoms must be positive")
    return {
        "atom_average_error": Fraction(1, n_atoms),
        "worst_case_false_accept": Fraction(1),
    }


def fraction_record(value: Fraction) -> dict[str, object]:
    return {
        "exact": str(value),
        "decimal": float(value),
    }


def family_grid(q: int) -> tuple[int, ...]:
    return tuple(sorted({1, min(3, q), q}))


def compute_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for q in QUERY_GRID:
        for families in family_grid(q):
            for rho in RHO_GRID:
                error = majority_error(q, families, rho)
                gap = 1 - 2 * error
                rows.append(
                    {
                        "q": q,
                        "families": families,
                        "family_sizes": list(balanced_family_sizes(q, families)),
                        "rho": str(rho),
                        "rho_decimal": float(rho),
                        "false_accept": fraction_record(error),
                        "false_reject": fraction_record(error),
                        "robust_gap": fraction_record(gap),
                        "admissible": error <= ERROR_LIMIT,
                    }
                )
    return rows


def lookup(rows: list[dict[str, object]], q: int, families: int, rho: Fraction) -> dict[str, object]:
    for row in rows:
        if row["q"] == q and row["families"] == families and row["rho"] == str(rho):
            return row
    raise KeyError((q, families, rho))


def evaluate_gates(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    independent = lookup(rows, 9, 1, Fraction(0))
    corr_pass = lookup(rows, 9, 1, Fraction(1, 20))
    corr_fail = lookup(rows, 9, 1, Fraction(1, 10))
    diverse_one = lookup(rows, 9, 1, Fraction(1, 5))
    diverse_three = lookup(rows, 9, 3, Fraction(1, 5))
    diverse_nine = lookup(rows, 9, 9, Fraction(1, 5))

    exactness = all(
        row["false_accept"]["exact"] == row["false_reject"]["exact"]
        for row in rows
    )
    global_kill = all(global_flip_error(q) == MU for q in QUERY_GRID)
    attacks = [targeted_average_attack(n) for n in (16, 64, 256, 1024)]
    marginal_kill = all(
        attack["atom_average_error"] <= MU
        and attack["worst_case_false_accept"] == 1
        for attack in attacks
    )
    separate_error = all(
        row["admissible"]
        == (
            Fraction(row["false_accept"]["exact"]) <= ERROR_LIMIT
            and Fraction(row["false_reject"]["exact"]) <= ERROR_LIMIT
        )
        for row in rows
    )

    return {
        "E0_exactness": {"pass": exactness},
        "I0_independent_liveness": {
            "pass": independent["admissible"],
            "error": independent["false_accept"],
        },
        "C0_correlation_boundary": {
            "pass": bool(corr_pass["admissible"] and not corr_fail["admissible"]),
            "rho_0.05_error": corr_pass["false_accept"],
            "rho_0.10_error": corr_fail["false_accept"],
        },
        "D0_diversity_recovery": {
            "pass": bool(
                not diverse_one["admissible"]
                and diverse_three["admissible"]
                and diverse_nine["admissible"]
            ),
            "one_family_error": diverse_one["false_accept"],
            "three_family_error": diverse_three["false_accept"],
            "nine_family_error": diverse_nine["false_accept"],
        },
        "G0_global_correlation_kill": {
            "pass": global_kill,
            "error_each_q": fraction_record(MU),
        },
        "M0_marginal_bound_kill": {
            "pass": marginal_kill,
            "attacks": [
                {
                    "n_atoms": n,
                    "atom_average_error": fraction_record(a["atom_average_error"]),
                    "worst_case_false_accept": fraction_record(a["worst_case_false_accept"]),
                }
                for n, a in zip((16, 64, 256, 1024), attacks)
            ],
        },
        "S0_separate_error_rule": {"pass": separate_error},
    }

