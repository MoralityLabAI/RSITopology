"""BM-36: an independent triangular Bernstein Hessian certificate.

BM-35's unclipped ordinary-path statistic lives in a triangle, so a
rectangle-wide monomial triangle-inequality Hessian bound is unnecessary.
Evaluate degree-(3,3) tensor Bernstein coefficients by exact Lagrange
collocation on 32 triangle patches. Only the BM-35 polynomial coefficient
table is imported. No BM-35 Bernstein transformation is reused.

This certifies the sharper all-n readout-erasure convergence gap 117/n.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb

try:
    from .smooth_polynomial_overlap_BM35 import (
        COEFFICIENT_NUMERATORS, DENOMINATOR, DEGREE,
    )
except ImportError:
    from smooth_polynomial_overlap_BM35 import (
        COEFFICIENT_NUMERATORS, DENOMINATOR, DEGREE,
    )


NODES = tuple(Fraction(i, 3) for i in range(4))
U_BREAKS = tuple(Fraction(k, 3) for k in (-4, -3, -2, -1, 0, 1, 2, 3, 4))
Y_BREAKS = tuple(Fraction(k, 4) for k in range(5))
DERIVATIVES = ((2, 0), (1, 1), (0, 2))
# The exact inverse of [B_{i,3}(r/3)]_{r,i=0}^3.
INVERSE_BERNSTEIN = (
    (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
    (Fraction(-5, 6), Fraction(3), Fraction(-3, 2), Fraction(1, 3)),
    (Fraction(1, 3), Fraction(-3, 2), Fraction(3), Fraction(-5, 6)),
    (Fraction(0), Fraction(0), Fraction(0), Fraction(1)),
)
SIMPLE_RATE_CONSTANT = 117


def in_observation_triangle(u: Fraction, w: Fraction) -> bool:
    """Exact convex hull of ordinary one-path Fourier observations."""
    u, w = Fraction(u), Fraction(w)
    return abs(u) <= Fraction(4, 3) and Fraction(3, 2)*abs(u)-1 <= w <= 1


def bernstein_basis(i: int, t: Fraction) -> Fraction:
    t = Fraction(t)
    if not 0 <= i <= 3:
        raise ValueError("only cubic Bernstein indices are supported")
    return Fraction(comb(3, i))*t**i*(1-t)**(3-i)


def verify_basis_inverse() -> bool:
    """Independent 4x4 exact inverse check for the collocation transform."""
    matrix = tuple(tuple(bernstein_basis(i, t) for i in range(4)) for t in NODES)
    for i in range(4):
        for j in range(4):
            entry = sum((INVERSE_BERNSTEIN[i][k]*matrix[k][j]
                         for k in range(4)), Fraction(0))
            if entry != (1 if i == j else 0):
                raise AssertionError("invalid cubic Bernstein collocation inverse")
    return True


def _validate_coefficients(coefficients: dict) -> dict:
    if not isinstance(coefficients, dict):
        raise ValueError("monomial coefficients must be a dictionary")
    for key, value in coefficients.items():
        if (not isinstance(key, tuple) or len(key) != 2
                or any(not isinstance(x, int) or x < 0 for x in key)
                or sum(key) > DEGREE or not isinstance(value, int)):
            raise ValueError("invalid degree-five integer numerator table")
    return coefficients


def hessian_value(
    derivative: tuple[int, int], u: Fraction, w: Fraction,
    *, coefficients: dict | None = None,
) -> Fraction:
    """Directly differentiate the original monomials in exact arithmetic."""
    if derivative not in DERIVATIVES:
        raise ValueError("only uu, uw and ww second derivatives are supported")
    terms = _validate_coefficients(
        COEFFICIENT_NUMERATORS if coefficients is None else coefficients
    )
    du, dw = derivative
    u, w = Fraction(u), Fraction(w)
    result = Fraction(0)
    for (i, j), numerator in terms.items():
        if i < du or j < dw:
            continue
        factor = Fraction(numerator, DENOMINATOR)
        for k in range(du):
            factor *= i-k
        for k in range(dw):
            factor *= j-k
        result += factor*u**(i-du)*w**(j-dw)
    return result


def cell_bernstein_coefficients(
    derivative: tuple[int, int],
    ua: Fraction, ub: Fraction, ya: Fraction, yb: Fraction,
    *, coefficients: dict | None = None,
) -> tuple[tuple[Fraction, ...], ...]:
    """Independently interpolate the transformed derivative in B_3 tensor B_3.

    u=ua+(ub-ua)x, w=l(u)+(1-l(u))*(ya+(yb-ya)y);
    l(u)=3|u|/2-1. Each u-cell has constant sign, so w is
    bilinear in (x,y). Since a second derivative of total-degree-five
    f has total degree <=3, its pullback has bidegree <=(3,3).
    Sixteen exact nodal values therefore determine it uniquely.
    """
    ua, ub, ya, yb = map(Fraction, (ua, ub, ya, yb))
    if not (ua < ub and -Fraction(4, 3) <= ua < ub <= Fraction(4, 3)
            and (ub <= 0 or ua >= 0) and 0 <= ya < yb <= 1):
        raise ValueError("cell must lie on one signed half of the triangle")
    values = []
    for x in NODES:
        u = ua+(ub-ua)*x
        lo = Fraction(3, 2)*abs(u)-1
        values.append(tuple(
            hessian_value(
                derivative, u, lo+(1-lo)*(ya+(yb-ya)*y),
                coefficients=coefficients,
            )
            for y in NODES
        ))
    return tuple(tuple(
        sum((
            INVERSE_BERNSTEIN[i][r]*values[r][s]*
            INVERSE_BERNSTEIN[j][s]
            for r in range(4) for s in range(4)
        ), Fraction(0))
        for j in range(4)
    ) for i in range(4))


@dataclass(frozen=True)
class TriangularHessianReceipt:
    cells: int
    derivative_fields: int
    coefficients_checked: int
    hessian_uu: Fraction
    hessian_uw: Fraction
    hessian_ww: Fraction
    matched_bias_coefficient: Fraction
    unmatched_bias_coefficient: Fraction
    exact_rate_coefficient: Fraction
    integer_rate_coefficient: int


def verify_triangular_hessian(
    *, coefficients: dict | None = None,
) -> TriangularHessianReceipt:
    """Finite exact proof of all three uniform second-derivative bounds.

    8 signed-u intervals x 4 y intervals =32 complete triangle cells.
    On each, every derivative is reconstructed from 16 exact values,
    then bounded by its 16 cubic tensor-Bernstein coefficients.
    """
    verify_basis_inverse()
    terms = _validate_coefficients(
        COEFFICIENT_NUMERATORS if coefficients is None else coefficients
    )
    bounds = [Fraction(0) for _ in DERIVATIVES]
    checked = 0
    for k, derivative in enumerate(DERIVATIVES):
        for ua, ub in zip(U_BREAKS[:-1], U_BREAKS[1:]):
            for ya, yb in zip(Y_BREAKS[:-1], Y_BREAKS[1:]):
                beta = cell_bernstein_coefficients(
                    derivative, ua, ub, ya, yb, coefficients=terms,
                )
                for row in beta:
                    for entry in row:
                        checked += 1
                        bounds[k] = max(bounds[k], abs(entry))
    if len(U_BREAKS) != 9 or len(Y_BREAKS) != 5 or checked != 1536:
        raise AssertionError("incomplete triangular domain certificate")
    muu, muw, mww = bounds
    # BM-34 exact conditional mean/variance table, reused from BM-35.
    a = Fraction(7, 18)*muu
    b = Fraction(2, 9)*muu + Fraction(3, 5)*muw + Fraction(3, 8)*mww
    rate = Fraction(40, 13)*max(a, b)
    if rate >= SIMPLE_RATE_CONSTANT:
        raise AssertionError("triangular Hessian cannot certify 117/n")
    return TriangularHessianReceipt(
        32, 3, checked, muu, muw, mww, a, b, rate,
        SIMPLE_RATE_CONSTANT,
    )


def finite_gap_bound(n: int) -> Fraction:
    """BM-36 certificate: 0 <= 5/52 - eta_n(8,2) <= 117/n."""
    if not isinstance(n, int) or n < 1:
        raise ValueError("number of ordinary paths must be a positive integer")
    return Fraction(SIMPLE_RATE_CONSTANT, n)


def theorem_receipt(n: int = 10**6) -> dict[str, object]:
    bound = finite_gap_bound(n)
    receipt = verify_triangular_hessian()
    return {
        "ordinary_paths": n,
        "domain": "conv{(-4/3,1),(0,-1),(4/3,1)}",
        "cells": receipt.cells,
        "hessian_fields": receipt.derivative_fields,
        "exact_bernstein_coefficients": receipt.coefficients_checked,
        "hessian_bounds": tuple(str(t) for t in (
            receipt.hessian_uu, receipt.hessian_uw, receipt.hessian_ww
        )),
        "rational_rate_constant": str(receipt.exact_rate_coefficient),
        "certified_rate": "0 <= 5/52-eta_n(8,2) <= 117/n",
        "gap_bound": str(bound),
        "uses_same_BM35_polynomial": True,
        "trusts_external_optimizer": False,
    }
