"""BM-39: exact TV for BM-27 graded correlated-mask family, every n.

Pure-rational proof:
  clean P0-P1 = (A^n-B^n) tensor (A-B) / 8;
  supp(A)={00,11}, supp(B)={00,10,01};
  TV(A^n,B^n)=1-(3/4)^n and TV(A,B)=1/4;
  TV(clean worlds)=[1-(3/4)^n]/16;
  mask Qh(lam)=(1-lam)*BM27_eraser_h+lam*delta_0;
  BM27 eraser worlds have identical reported distributions.
  Hence TV(masked worlds)=lam*[1-(3/4)^n]/16, EXACTLY.

This is a family-specific formula. It is NOT the general adversarial
minimax distinguishability frontier or a theorem about neural monitors.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction

try:
    from .replication_uniform_upper_BM27 import (
        PAIR_A, PAIR_B, UPPER_CAP, verify_convolution_identity,
        exact_clean_law, explicit_mask_law, xor_convolve,
    )
except ImportError:
    from replication_uniform_upper_BM27 import (
        PAIR_A, PAIR_B, UPPER_CAP, verify_convolution_identity,
        exact_clean_law, explicit_mask_law, xor_convolve,
    )


def _inputs(n: int, lam: Fraction) -> Fraction:
    if not isinstance(n, int) or n < 1:
        raise ValueError("positive ordinary-path count required")
    lam = Fraction(lam)
    if not 0 <= lam <= 1:
        raise ValueError("mixture lambda must lie in [0,1]")
    return lam


def clean_total_variation(n: int) -> Fraction:
    _inputs(n, Fraction(1))
    return Fraction(1, 16)*(1-Fraction(3, 4)**n)


def graded_total_variation(n: int, lam: Fraction) -> Fraction:
    lam = _inputs(n, lam)
    return lam*clean_total_variation(n)


def graded_mask_cap(lam: Fraction) -> Fraction:
    lam = _inputs(1, lam)
    return (1-lam)*UPPER_CAP


def attacker_family_tv_at_budget(n: int, cap: Fraction) -> Fraction:
    """Achievable TV in the registered family, cap in [0,5/52].

    Because the adversary may choose this mask, the returned value
    is an *upper bound* on minimax TV over all legal mask pairs
    with that cap. It is NOT an unrestricted minimax identity.
    """
    cap = Fraction(cap)
    if not 0 <= cap <= UPPER_CAP:
        raise ValueError("graded family covers per-bit caps [0,5/52]")
    lam = 1-cap/UPPER_CAP
    return graded_total_variation(n, lam)


def asymptotic_total_variation(lam: Fraction) -> Fraction:
    return _inputs(1, lam)/16


def ideal_equal_prior_bayes_risk(n: int, lam: Fraction) -> Fraction:
    """Exact optimal equal-prior error for the graded family, one episode."""
    return (1-graded_total_variation(n, lam))/2


def population_tpr_upper(n: int, lam: Fraction,
                         fpr: Fraction) -> Fraction:
    """Any fixed or randomized test has TPR<=FPR+TV(P0,P1)."""
    alpha = Fraction(fpr)
    if not 0 <= alpha <= 1:
        raise ValueError("population FPR must lie in [0,1]")
    return min(Fraction(1),alpha+graded_total_variation(n,lam))


def _full_mask(n: int, h: int, lam: Fraction) -> dict[int, Fraction]:
    original = explicit_mask_law(n, h)
    return {
        x: weight
        for x, weight in (
            (k, (1-lam)*original.get(k,Fraction(0))+
                (lam if k == 0 else 0))
            for k in original.keys()|{0}
        ) if weight
    }


def _tv(a: dict[int, Fraction],b: dict[int, Fraction]) -> Fraction:
    return sum((abs(a.get(k,0)-b.get(k,0))
                for k in a.keys()|b.keys()),Fraction(0))/2


@dataclass(frozen=True)
class ExactWitness:
    n: int
    lam: Fraction
    per_bit_mask_cap: Fraction
    full_output_tv: Fraction
    predicted_full_output_tv: Fraction
    clean_tv: Fraction
    complete_probabilities_checked: int


def verify_full_output(n: int, lam: Fraction) -> ExactWitness:
    """Independent explicit 2^(2n+2) distribution check, n<=3."""
    lam = _inputs(n, lam)
    if n > 3:
        raise ValueError("full-output census limited to 1<=n<=3")
    if not verify_convolution_identity():
        raise AssertionError("BM27 exact eraser algebra invalid")
    clean = [exact_clean_law(n,h) for h in (0,1)]
    masked = [
        xor_convolve(clean[h],_full_mask(n,h,lam)) for h in (0,1)
    ]
    actual = _tv(*masked)
    theoretical = graded_total_variation(n,lam)
    if actual != theoretical or _tv(*clean) != clean_total_variation(n):
        raise AssertionError("exact graded clean/erased mixture mismatch")
    cap = graded_mask_cap(lam)
    for h in (0,1):
        q = _full_mask(n,h,lam)
        for bit in range(2*n+2):
            measured = sum((p for x,p in q.items() if x & (1<<bit)),
                           Fraction(0))
            if measured != cap:
                raise AssertionError("incorrect per-bit cost")
    return ExactWitness(
        n,lam,cap,actual,theoretical,clean_total_variation(n),
        1<<(2*n+2)
    )


def theorem_receipt(n: int = 4096, lam: Fraction = Fraction(1,2)) -> dict:
    lam = _inputs(n,lam)
    if (_tv({0:PAIR_A[0],1:PAIR_A[1],2:PAIR_A[2],3:PAIR_A[3]},
            {0:PAIR_B[0],1:PAIR_B[1],2:PAIR_B[2],3:PAIR_B[3]})
            != Fraction(1,4)):
        raise AssertionError("registered A/B pair TV changed")
    if ({k for k,p in enumerate(PAIR_A) if p>0} &
        {k for k,p in enumerate(PAIR_B) if p>0}) != {0}:
        raise AssertionError("ordinary pair overlap proof invalid")
    if PAIR_A[0]!=Fraction(7,8) or PAIR_B[0]!=Fraction(3,4):
        raise AssertionError("ordinary all-zero overlap changed")
    if not verify_convolution_identity():
        raise AssertionError("BM27 full erasure identity invalid")
    return {
        "ordinary_paths": n,
        "unmasked_fraction": str(lam),
        "mask_cap": str(graded_mask_cap(lam)),
        "exact_TV": str(graded_total_variation(n,lam)),
        "exact_formula": "lambda*(1-(3/4)^n)/16",
        "asymptotic_TV": str(asymptotic_total_variation(lam)),
        "equal_prior_bayes_error": str(ideal_equal_prior_bayes_risk(n,lam)),
        "population_TPR_upper_at_5pct_FPR":
            str(population_tpr_upper(n,lam,Fraction(1,20))),
        "family_specific": True,
        "unrestricted_minimax_claim": False,
    }
