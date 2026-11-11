"""BM-37: quantitative output-TV certificates for the replicated q8 masking game.

Two separately labeled access classes:
  * MATCHED-MARGINAL pairs, with shared symmetrized ordinary histogram
    and same ordinary-plus-one-special-bit noise marginal;
  * ALL independent-of-current-clean, hypothesis-aware correlated masks,
    with a universal low-noise Walsh test and a formally positive but
    exponentially ill-conditioned deconvolution extension.

All arithmetic for certificate constants and finite witnesses is rational.
The upper bound on adaptive multi-episode Bayes risk presumes the stated
one-episode TV separation at EVERY common public history.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import comb

try:
    from .smooth_polynomial_overlap_BM35 import (
        polynomial, COEFFICIENT_NUMERATORS, DENOMINATOR,
    )
    from .triangular_hessian_BM36 import verify_triangular_hessian
    from .finite_empirical_extension_BM31 import (
        empirical_joint_law, directing_law, total_variation,
    )
    from .replication_uniform_upper_BM27 import (
        exact_clean_law, xor_convolve,
    )
except ImportError:
    from smooth_polynomial_overlap_BM35 import (
        polynomial, COEFFICIENT_NUMERATORS, DENOMINATOR,
    )
    from triangular_hessian_BM36 import verify_triangular_hessian
    from finite_empirical_extension_BM31 import (
        empirical_joint_law, directing_law, total_variation,
    )
    from replication_uniform_upper_BM27 import (
        exact_clean_law, xor_convolve,
    )


LIMIT = Fraction(5, 52)
K_TRI = Fraction(
    433489819753448825447087550392,
    3727057529810093862630619125,
)
CERTIFIED_SUP = Fraction(127, 50)
EXPECTED_BERNSTEIN_SUP = Fraction(
    3636528285638174746233679387,
    1433483665311574562550238125,
)
U_BREAKS = tuple(Fraction(k, 3) for k in range(-4, 5))
Y_BREAKS = tuple(Fraction(k, 4) for k in range(5))
NODES = tuple(Fraction(k, 5) for k in range(6))


def _bernstein(i: int, t: Fraction) -> Fraction:
    return Fraction(comb(5, i))*t**i*(1-t)**(5-i)


@lru_cache(maxsize=1)
def _collocation_inverse() -> tuple[tuple[Fraction, ...], ...]:
    """Direct Gauss-Jordan inverse; independent of BM-35's monomial expander."""
    n = 6
    rows = [
        [_bernstein(j, NODES[i]) for j in range(n)]
        + [Fraction(int(i == j)) for j in range(n)]
        for i in range(n)
    ]
    for k in range(n):
        pivot = next((i for i in range(k, n) if rows[i][k]), None)
        if pivot is None:
            raise AssertionError("singular exact Bernstein collocation matrix")
        rows[k], rows[pivot] = rows[pivot], rows[k]
        a = rows[k][k]
        rows[k] = [x/a for x in rows[k]]
        for i in range(n):
            if i == k:
                continue
            a = rows[i][k]
            if a:
                rows[i] = [x-a*y for x, y in zip(rows[i], rows[k])]
    inverse = tuple(tuple(row[n:]) for row in rows)
    for i in range(n):
        for j in range(n):
            value = sum(
                (inverse[i][k]*_bernstein(j, NODES[k])
                 for k in range(n)), Fraction(0)
            )
            if value != int(i == j):
                raise AssertionError("collocation inverse multiplication failed")
    return inverse


def _sup_cell(
    ua: Fraction, ub: Fraction, ya: Fraction, yb: Fraction
) -> tuple[Fraction, ...]:
    inv = _collocation_inverse()
    values = []
    for x in NODES:
        u = ua+(ub-ua)*x
        low = Fraction(3, 2)*abs(u)-1
        values.append(tuple(
            polynomial(u, low+(1-low)*(ya+(yb-ya)*y))
            for y in NODES
        ))
    return tuple(
        sum((
            inv[i][r]*values[r][s]*inv[j][s]
            for r in range(6) for s in range(6)
        ), Fraction(0))
        for i in range(6) for j in range(6)
    )


@dataclass(frozen=True)
class SupremumCertificate:
    cells: int
    coefficients: int
    exact_bernstein_envelope: Fraction
    simple_rational_envelope: Fraction


@lru_cache(maxsize=1)
def certify_supremum() -> SupremumCertificate:
    """Proof |f| <=127/50 on the COMPLETE unclipped observation triangle.

    8 signed-u intervals by 4 y intervals. The pullback of degree-five
    f to each bilinear parameter cell has bidegree <=(5,5).
    Cubic BM-36 Hessian collocation and BM-35 power-to-Bernstein code
    are not used. The 6x6 exact inverse is rederived from first principles.
    """
    if len(COEFFICIENT_NUMERATORS) != 15 or not DENOMINATOR:
        raise AssertionError("registered BM-35 polynomial table changed")
    M = Fraction(0)
    count = 0
    for ua, ub in zip(U_BREAKS[:-1], U_BREAKS[1:]):
        for ya, yb in zip(Y_BREAKS[:-1], Y_BREAKS[1:]):
            for value in _sup_cell(ua, ub, ya, yb):
                count += 1
                M = max(M, abs(value))
    if count != 1152 or M != EXPECTED_BERNSTEIN_SUP or M >= CERTIFIED_SUP:
        raise AssertionError("full triangle supremum certificate invalid")
    return SupremumCertificate(32, count, M, CERTIFIED_SUP)


def _input(n: int, eta: Fraction) -> Fraction:
    if not isinstance(n, int) or n < 1:
        raise ValueError("ordinary path count must be a positive integer")
    eta = Fraction(eta)
    if not 0 <= eta <= 1:
        raise ValueError("per-bit corruption cap must be in [0,1]")
    return eta


def _gap(n: int, eta: Fraction) -> Fraction:
    eta = _input(n, eta)
    return max(Fraction(0), LIMIT-eta-K_TRI/n)


def matched_marginal_tv_lower(n: int, eta: Fraction) -> Fraction:
    """TV >= [(5/52-eta)-K_tri/n]_+ / ((40/13)*(127/50)).

    Requires same ordinary mask histogram and same conditional one-bit
    exceptional noise marginals after legitimate permutation symmetrization.
    Applies to ALL correlated, hypothesis-aware masks in that access class.
    """
    return Fraction(65, 508)*_gap(n, eta)


def unrestricted_low_noise_tv_lower(eta: Fraction) -> Fraction:
    """Four-bit Walsh witness TV >= [1/64-11*eta/8]_+ for every n>=1."""
    eta = _input(1, eta)
    return max(Fraction(0), Fraction(1, 64)-Fraction(11, 8)*eta)


def _inverse_multiplier(n: int) -> tuple[Fraction, Fraction]:
    """Uniform Fourier deconvolution bounds on mask-marginal TV.

    Clean Fourier: ordinary >=(3/4)^n/8; with one special bit
    >=(3/4)^(n+1)/8. Walsh inversion + Parseval + Cauchy gives
    TV(noise0,noise1) <=2^(m/2)*TV(output0,output1)/minhat.
    Rationalizing sqrt(2) <=2 leads to the second multiplier.
    """
    if not isinstance(n, int) or n < 1:
        raise ValueError("positive ordinary path count required")
    v = Fraction(8, 3)**n
    return 8*v, Fraction(64, 3)*v


def unrestricted_tv_lower(n: int, eta: Fraction) -> Fraction:
    """All-mask TV lower bound, including approximate marginal mismatch.

    The inverse-convolution term is exponential in n. This bound is
    mathematically positive near eta<5/52 for sufficiently large n,
    but extremely conservative and unsuitable for detection planning.
    """
    gap = _gap(n, eta)
    if not gap:
        return unrestricted_low_noise_tv_lower(eta)
    lo, ls = _inverse_multiplier(n)
    alpha = LIMIT*(
        32*CERTIFIED_SUP + (3+32*CERTIFIED_SUP)*lo + 2*ls
    )
    return max(unrestricted_low_noise_tv_lower(eta), gap/alpha)


def adaptive_bayes_error_upper(
    episodes: int, per_history_tv: Fraction,
) -> Fraction:
    """For any adaptive transcript with each conditional TV >= t.

    At every common public history, the two next-episode laws have
    TV >= t, so Hellinger affinity <=1-t^2/2. Multiplying affinities
    yields optimal equal-prior transcript Bayes risk <=
        (1/2)*(1-t^2/2)^episodes.
    This is a pair-specific optimal test, with conditionally fresh
    hidden labels and a per-history threat-model guarantee.
    """
    if not isinstance(episodes, int) or episodes < 0:
        raise ValueError("nonnegative integer episode count required")
    t = Fraction(per_history_tv)
    if not 0 <= t <= 1:
        raise ValueError("TV lower bound must lie in [0,1]")
    return Fraction(1, 2)*(1-t*t/2)**episodes


def _special_signed(joint: dict) -> dict:
    """Signed first exceptional-bit law indexed by ordinary histogram."""
    v = {}
    for (hist, special), weight in joint.items():
        value = Fraction(weight)*(1 if not special&1 else -1)
        v[hist] = v.get(hist, Fraction(0))+value
    return {hist: value for hist, value in v.items() if value}


@dataclass(frozen=True)
class ExactSmallWitness:
    n: int
    corruption_cap: Fraction
    observed_tv: Fraction
    matched_margins: bool
    conditional_tv_lower: Fraction | None
    universal_low_noise_lower: Fraction
    universal_all_mask_lower: Fraction


def verify_small_mask_pair(
    n: int, q0: dict[int, Fraction], q1: dict[int, Fraction]
) -> ExactSmallWitness:
    """Independent complete-output witness for n<=4; validates scope."""
    if not isinstance(n, int) or not 1 <= n <= 4:
        raise ValueError("finite full-output verification supports n=1..4")
    j0, j1 = (empirical_joint_law(n, law) for law in (q0, q1))
    matched = (directing_law(n, j0) == directing_law(n, j1)
               and _special_signed(j0) == _special_signed(j1))
    outputs = (
        xor_convolve(exact_clean_law(n, 0), q0),
        xor_convolve(exact_clean_law(n, 1), q1),
    )
    observed = total_variation(*outputs)
    eta = max(
        sum((Fraction(p) for mask, p in law.items() if mask&(1<<bit)),
            Fraction(0))
        for law in (q0, q1) for bit in range(2*n+2)
    )
    conditional = matched_marginal_tv_lower(n, eta) if matched else None
    universal = unrestricted_tv_lower(n, eta)
    if observed < universal or (conditional is not None
                                and observed < conditional):
        raise AssertionError("BM-37 analytic bound violated by exact masks")
    return ExactSmallWitness(
        n, eta, observed, matched, conditional,
        unrestricted_low_noise_tv_lower(eta), universal,
    )


def theorem_receipt(n: int = 10**4, eta: Fraction = Fraction(1, 20)
                    ) -> dict[str, object]:
    eta = _input(n, eta)
    sup = certify_supremum()
    tri = verify_triangular_hessian()
    if tri.exact_rate_coefficient != K_TRI:
        raise AssertionError("BM-36 rate dependency changed")
    return {
        "alphabet": "F2^3",
        "ordinary_paths": n,
        "per_bit_cap": str(eta),
        "bernstein_cells": sup.cells,
        "supremum_bernstein_coefficients": sup.coefficients,
        "exact_supremum_envelope": str(sup.exact_bernstein_envelope),
        "certified_supremum_bound": str(CERTIFIED_SUP),
        "matched_marginal_tv_lower": str(matched_marginal_tv_lower(n, eta)),
        "unrestricted_low_noise_tv_lower":
            str(unrestricted_low_noise_tv_lower(eta)),
        "conditional_adaptive_testing_only": True,
        "external_optimizer_required": False,
        "near_threshold_unrestricted_bound_exponentially_weak": True,
    }
