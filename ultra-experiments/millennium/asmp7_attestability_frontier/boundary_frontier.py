from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import comb, log, sqrt
from statistics import NormalDist

from scipy.stats import binom

from attestability import ERROR_LIMIT, THETA_GRID, audit_probability, fraction_text


K1_GRID = tuple(range(9, 17))
M_CAP = 1 << 15
SINGLETON_K1 = 16


@dataclass(frozen=True)
class ExactBoundaryTest:
    m: int
    k1: int
    theta: Fraction
    q0: Fraction
    q1: Fraction
    delta: Fraction
    cutoff: int
    gamma: Fraction
    fp: Fraction
    fn: Fraction

    @property
    def feasible(self) -> bool:
        return self.fp <= ERROR_LIMIT and self.fn <= ERROR_LIMIT


@dataclass(frozen=True)
class MinimumCertificate:
    k1: int
    theta: Fraction
    test: ExactBoundaryTest | None
    predecessor: ExactBoundaryTest | None
    cap_test: ExactBoundaryTest | None
    float_candidate_m: int
    exact_evaluations: int


def forbidden_class_size(k1: int) -> int:
    if k1 not in K1_GRID:
        raise ValueError("k1 outside registered grid")
    return sum(comb(16, k) for k in range(k1, 17))


def separation(k1: int, theta: Fraction) -> Fraction:
    return audit_probability(k1, theta) - Fraction(1, 2)


def _p0_tail_and_mass(m: int, cutoff: int) -> tuple[int, int, int]:
    """Return integer numerators for P(K>c), P(K=c), denominator 2^m."""
    mass = 1  # C(m,m)
    tail = 0
    for k in range(m, cutoff, -1):
        tail += mass
        mass = mass * k // (m - k + 1)
    return tail, mass, 1 << m


def _p1_lower_and_mass(m: int, cutoff: int, q: Fraction) -> tuple[int, int, int]:
    """Return integer numerators for P(K<c), P(K=c), denominator b^m."""
    a, b = q.numerator, q.denominator
    denominator = b**m
    if a == b:
        if cutoff < m:
            return 0, 0, denominator
        return 0, denominator, denominator
    complement = b - a
    mass = complement**m  # k=0
    lower = 0
    for k in range(0, cutoff):
        lower += mass
        mass = mass * (m - k) * a // ((k + 1) * complement)
    return lower, mass, denominator


def _float_cutoff(m: int) -> int:
    if m == 0:
        return 0
    return int(binom.isf(float(ERROR_LIMIT), m, 0.5))


@lru_cache(maxsize=None)
def exact_optimal_test(m: int, k1: int, theta: Fraction) -> ExactBoundaryTest:
    if not 0 <= m <= M_CAP:
        raise ValueError("m outside registered cap")
    if k1 not in K1_GRID or theta not in THETA_GRID:
        raise ValueError("cell outside registered grid")

    cutoff = _float_cutoff(m)
    tail, mass, denominator = _p0_tail_and_mass(m, cutoff)
    target = ERROR_LIMIT * denominator

    while Fraction(tail) > target:
        next_mass = mass * (m - cutoff) // (cutoff + 1)
        tail -= next_mass
        cutoff += 1
        mass = next_mass
    while Fraction(tail + mass) < target:
        tail += mass
        mass = mass * cutoff // (m - cutoff + 1)
        cutoff -= 1

    gamma = (target - tail) / mass
    if not 0 <= gamma <= 1:
        raise ArithmeticError("exact cutoff randomization outside [0,1]")
    fp = Fraction(tail, denominator) + gamma * Fraction(mass, denominator)

    q1 = audit_probability(k1, theta)
    lower, equal, denominator1 = _p1_lower_and_mass(m, cutoff, q1)
    fn = Fraction(lower, denominator1) + (1 - gamma) * Fraction(equal, denominator1)
    return ExactBoundaryTest(
        m=m,
        k1=k1,
        theta=theta,
        q0=Fraction(1, 2),
        q1=q1,
        delta=q1 - Fraction(1, 2),
        cutoff=cutoff,
        gamma=gamma,
        fp=fp,
        fn=fn,
    )


def _float_fn(m: int, k1: int, theta: Fraction) -> float:
    if m == 0:
        return 0.95
    q1 = float(audit_probability(k1, theta))
    cutoff = _float_cutoff(m)
    tail = float(binom.sf(cutoff, m, 0.5))
    mass0 = float(binom.pmf(cutoff, m, 0.5))
    gamma = (float(ERROR_LIMIT) - tail) / mass0
    return float(binom.cdf(cutoff - 1, m, q1) + (1 - gamma) * binom.pmf(cutoff, m, q1))


def _float_candidate(k1: int, theta: Fraction, cap: int) -> int:
    if separation(k1, theta) == 0:
        return cap
    if _float_fn(cap, k1, theta) > float(ERROR_LIMIT):
        return cap
    low, high = 0, cap
    while low < high:
        mid = (low + high) // 2
        if _float_fn(mid, k1, theta) <= float(ERROR_LIMIT):
            high = mid
        else:
            low = mid + 1
    return low


def certify_minimum(k1: int, theta: Fraction, cap: int = M_CAP) -> MinimumCertificate:
    candidate = _float_candidate(k1, theta, cap)
    evaluations = 0
    test = exact_optimal_test(candidate, k1, theta)
    evaluations += 1

    while candidate < cap and not test.feasible:
        candidate += 1
        test = exact_optimal_test(candidate, k1, theta)
        evaluations += 1

    if not test.feasible:
        return MinimumCertificate(k1, theta, None, None, test, candidate, evaluations)

    predecessor = exact_optimal_test(candidate - 1, k1, theta) if candidate > 0 else None
    if predecessor is not None:
        evaluations += 1
    while predecessor is not None and predecessor.feasible:
        candidate -= 1
        test = predecessor
        predecessor = exact_optimal_test(candidate - 1, k1, theta) if candidate > 0 else None
        evaluations += 1

    return MinimumCertificate(k1, theta, test, predecessor, None, _float_candidate(k1, theta, cap), evaluations)


def normal_reference_m(k1: int, theta: Fraction) -> float | None:
    delta = float(separation(k1, theta))
    if delta <= 0:
        return None
    q1 = float(audit_probability(k1, theta))
    z = NormalDist().inv_cdf(0.95)
    return (z * (sqrt(0.25) + sqrt(q1 * (1 - q1))) / delta) ** 2


def certificate_record(certificate: MinimumCertificate) -> dict[str, object]:
    test = certificate.test
    base: dict[str, object] = {
        "k1": certificate.k1,
        "theta": fraction_text(certificate.theta),
        "forbidden_class_size": forbidden_class_size(certificate.k1),
        "boundary_role": (
            "singleton_boundary_control" if certificate.k1 == SINGLETON_K1 else "primary_surface"
        ),
        "delta": fraction_text(separation(certificate.k1, certificate.theta)),
        "delta_float": float(separation(certificate.k1, certificate.theta)),
        "normal_reference_m": normal_reference_m(certificate.k1, certificate.theta),
        "float_candidate_m": certificate.float_candidate_m,
        "exact_evaluations": certificate.exact_evaluations,
    }
    if test is None:
        assert certificate.cap_test is not None
        base.update(
            {
                "status": "infeasible_within_uniform_cap",
                "m_star": None,
                "cap": certificate.cap_test.m,
                "cap_fn": fraction_text(certificate.cap_test.fn),
                "cap_fn_float": float(certificate.cap_test.fn),
            }
        )
        return base
    predecessor = certificate.predecessor
    base.update(
        {
            "status": "feasible_exact",
            "m_star": test.m,
            "cutoff": test.cutoff,
            "gamma": fraction_text(test.gamma),
            "fp": fraction_text(test.fp),
            "fn": fraction_text(test.fn),
            "fp_float": float(test.fp),
            "fn_float": float(test.fn),
            "predecessor_m": predecessor.m if predecessor is not None else None,
            "predecessor_fn": fraction_text(predecessor.fn) if predecessor is not None else None,
            "predecessor_fn_float": float(predecessor.fn) if predecessor is not None else None,
            "normal_residual": (
                test.m - normal_reference_m(certificate.k1, certificate.theta)
                if normal_reference_m(certificate.k1, certificate.theta) is not None
                else None
            ),
        }
    )
    return base


def compute_surface() -> tuple[MinimumCertificate, ...]:
    return tuple(certify_minimum(k1, theta) for k1 in K1_GRID for theta in THETA_GRID)


def descriptive_log_fit(records: list[dict[str, object]]) -> dict[str, object]:
    selected = [
        record
        for record in records
        if record["status"] == "feasible_exact"
        and record["boundary_role"] != "singleton_boundary_control"
        and int(record["m_star"]) >= 100
    ]
    if len(selected) < 3:
        return {"available": False, "row_count": len(selected)}
    xs = [log(float(record["delta_float"])) for record in selected]
    ys = [log(float(record["m_star"])) for record in selected]
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    slope = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sum(
        (x - xbar) ** 2 for x in xs
    )
    intercept = ybar - slope * xbar
    predictions = [intercept + slope * x for x in xs]
    sse = sum((y - pred) ** 2 for y, pred in zip(ys, predictions))
    sst = sum((y - ybar) ** 2 for y in ys)
    return {
        "available": True,
        "row_count": len(selected),
        "selection_rule": "feasible, non-singleton, m_star>=100",
        "log_intercept": intercept,
        "log_delta_slope": slope,
        "r_squared": 1 - sse / sst if sst else 1.0,
        "claim_role": "descriptive_only_no_gate",
    }


def evaluate_surface_gates(certificates: tuple[MinimumCertificate, ...]) -> dict[str, dict[str, object]]:
    exact_failures: list[str] = []
    for certificate in certificates:
        label = f"k1={certificate.k1},theta={fraction_text(certificate.theta)}"
        if certificate.test is not None:
            if certificate.test.fp != ERROR_LIMIT or certificate.test.fn > ERROR_LIMIT:
                exact_failures.append(f"{label}:feasible_certificate")
            if certificate.predecessor is not None and certificate.predecessor.fn <= ERROR_LIMIT:
                exact_failures.append(f"{label}:predecessor")
        elif certificate.cap_test is None or certificate.cap_test.fn <= ERROR_LIMIT:
            exact_failures.append(f"{label}:cap")

    by_cell = {(c.k1, c.theta): c for c in certificates}
    reproduction_expected = {
        Fraction(3, 4): 73,
        Fraction(4, 5): 50,
        Fraction(1): 15,
    }
    reproduction_failures = [
        f"theta={fraction_text(theta)}"
        for theta, expected in reproduction_expected.items()
        if by_cell[(14, theta)].test is None or by_cell[(14, theta)].test.m != expected
    ]
    for theta in (Fraction(1, 2), Fraction(3, 5), Fraction(2, 3)):
        if exact_optimal_test(128, 14, theta).feasible:
            reproduction_failures.append(f"old_cap_theta={fraction_text(theta)}")

    census_failures = [
        k1
        for k1 in K1_GRID
        if forbidden_class_size(k1) != sum(1 for k in range(1 << 16) if 16 - k.bit_count() >= k1)
    ]

    order_failures: list[str] = []
    for k1 in K1_GRID:
        finite = [by_cell[(k1, theta)].test for theta in THETA_GRID if by_cell[(k1, theta)].test]
        if any(left.m < right.m for left, right in zip(finite, finite[1:])):
            order_failures.append(f"theta_order_k1={k1}")
    for theta in THETA_GRID:
        finite = [by_cell[(k1, theta)].test for k1 in K1_GRID if by_cell[(k1, theta)].test]
        if any(left.m < right.m for left, right in zip(finite, finite[1:])):
            order_failures.append(f"k1_order_theta={fraction_text(theta)}")

    surface_missing = [
        f"k1={c.k1},theta={fraction_text(c.theta)}"
        for c in certificates
        if c.theta > Fraction(1, 2) and c.test is None
    ]
    boundary_failures = [
        fraction_text(c.theta)
        for c in certificates
        if c.k1 == SINGLETON_K1
        and certificate_record(c)["boundary_role"] != "singleton_boundary_control"
    ]
    return {
        "E0_exact_adjacency": {"pass": not exact_failures, "failures": exact_failures},
        "R0_v0_1_reproduction": {
            "pass": not reproduction_failures,
            "failures": reproduction_failures,
        },
        "C0_class_census": {"pass": not census_failures, "failures": census_failures},
        "O0_order": {"pass": not order_failures, "failures": order_failures},
        "S0_surface_liveness": {"pass": not surface_missing, "missing": surface_missing},
        "B0_boundary_label": {"pass": not boundary_failures, "failures": boundary_failures},
    }

