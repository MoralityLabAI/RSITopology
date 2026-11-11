"""ASMP-15: exact multilevel descent of labeled graph covers.

This is a purely combinatorial Hamming inequality. It assumes all graph-cover
maps are independently validated before a security/safety certificate is used.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction

try:
    from .finite_seed import descent_error
except ImportError:
    from finite_seed import descent_error


def fiberwise_mode(labels: tuple[int, ...], n_base: int, sheets: int) -> tuple[int, ...]:
    """A closest descending labeling, tie-broken by smallest K label."""
    if n_base < 1 or sheets < 1 or len(labels) != n_base * sheets:
        raise ValueError("invalid cover dimensions")
    return tuple(min(
        (x for x, count in Counter(labels[u*sheets:(u+1)*sheets]).items()
         if count == max(Counter(labels[u*sheets:(u+1)*sheets]).values()))
    ) for u in range(n_base))


def pullback_hamming(
    labels: tuple[int, ...], base_labels: tuple[int, ...], sheets: int
) -> Fraction:
    """Normalized Hamming distance between a covering labeling and pullback."""
    if sheets < 1 or not base_labels or len(labels) != len(base_labels)*sheets:
        raise ValueError("invalid pullback dimensions")
    return Fraction(sum(labels[i] != base_labels[i//sheets]
                        for i in range(len(labels))), len(labels))


def two_step_descent(
    labels_top: tuple[int, ...], n_base: int, sheets_first: int, sheets_second: int
) -> dict[str, Fraction | tuple[int, ...]]:
    """Composable eta bound for G'' -> G' -> G with regular cardinalities.

    The labeling at G' is the nearest per-fiber projection of G''.
    eta_{composite} <= eta_{second} + eta_{first}.
    """
    if n_base < 1 or sheets_first < 1 or sheets_second < 1:
        raise ValueError("positive parameters required")
    middle = fiberwise_mode(labels_top, n_base*sheets_first, sheets_second)
    first = fiberwise_mode(middle, n_base, sheets_first)
    eta_second = pullback_hamming(labels_top, middle, sheets_second)
    eta_first = pullback_hamming(middle, first, sheets_first)
    eta_composite = descent_error(labels_top, n_base, sheets_first*sheets_second)
    bound = eta_second + eta_first
    if eta_composite > bound:
        raise AssertionError("Hamming triangle inequality failed")
    return {
        "middle_labels": middle,
        "base_labels": first,
        "eta_second": eta_second,
        "eta_first": eta_first,
        "eta_composite": eta_composite,
        "bound": bound,
    }
