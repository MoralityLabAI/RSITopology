"""BM-28: exact rational LOWER certificate at q=8, n=16, L=2.

The 16 ordinary two-edge paths and one exceptional path have 34 Boolean
reports. Both hidden worlds use fresh uniform F2^3 vertex labels and
world-aware XOR readout masks independent of the current clean report.

A dual candidate was discovered using a floating-point HiGHS LP, rounded
to signed integers at scale D=100,000,000, and its two normalizations
decreased enough to satisfy EVERY dual inequality in exact arithmetic.
The resulting fully certified lower bound is

  eta_16(8,2) >= 4,743,879 / 50,000,000 = 0.09487758.

The 459 integer Fourier orbit multipliers are kept in a frozen
zlib+base64-encoded little-endian int64 table, with SHA256 checksum.
This is a LOSSLESS certificate archive. The verifier uses ONLY standard
library integer operations and checks all 918 mask-orbit inequalities
across both hypotheses; by BM-24's wreath symmetry this proves the same
bound against every one of 2^34 underlying Boolean mask atoms.
No numerical solver is imported or used when checking the certificate.

The exact upper 5/52 from BM-27, together with monotonic projection,
gives the strengthened *limit* bracket
  0.09487758 <= eta_infinity(8,2) <= 5/52.
Neither bound establishes the exact limiting value or finite-n optimum.
"""
from __future__ import annotations

import base64
from fractions import Fraction
import hashlib
from math import comb
from pathlib import Path
import struct
import zlib

N=16
Q=8
M_ORD=comb(N+2,2)  # 153
M=3*M_ORD          # 459
SCALE=100_000_000
W_SCALE=1<<(3*N+6)
NORM_NUMERATORS=(9_487_759,-1)
MARGINAL_NUMERATORS=(-29_001_113,-37_951_043,-33_047_844,0)
EXACT_LOWER=Fraction(4_743_879,50_000_000)
UPPER=Fraction(5,52)
DUAL_FILE="BM28_N16_RATIONAL_DUAL.b64"
EXPECTED_SHA256="47bd694403aa4ce43d1e8e8b501b7ca05d2b2f1dbe97dd1e0152cbdc1835ec16"
K2=((1,1,1),(1,0,-1),(1,-1,1))


def ordinary_histograms(n:int=N):
    if not isinstance(n,int) or n<1:
        raise ValueError("positive ordinary path count required")
    return tuple((n-a-b,a,b) for a in range(n+1) for b in range(n-a+1))


def _raw_dual_table()->bytes:
    encoded="".join(Path(__file__).with_name(DUAL_FILE).read_text().split())
    raw=zlib.decompress(base64.b64decode(encoded,validate=True))
    if len(raw)!=8*M or hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA256:
        raise AssertionError("BM-28 rational dual checksum/length mismatch")
    return raw


def frozen_dual_numerators():
    """Unpack every fully inspectable signed coefficient in a fixed order."""
    y=struct.unpack("<%dq"%M,_raw_dual_table())
    if len(y)!=M or y[0]!=0 or sum(bool(v) for v in y)!=441:
        raise AssertionError("bad dual dimensions or unexpected sparsity")
    return y


def ordinary_kernel_numerators(n:int=N):
    """Exact integer multivariate Krawtchouk matrix.

    A selected ordinary-path histogram s=(s0,s1,s2) corresponds to a
    polynomial (x0+x1+x2)^s0 (x0-x2)^s1 (x0-x1+x2)^s2.
    The coefficient of x0^t0 x1^t1 x2^t2 equals the UNNORMALIZED
    mask-orbit Walsh character. Divide by C(n;t0,t1,t2) to obtain
    the exact histogram kernel. All computations use signed integers.
    """
    hists=ordinary_histograms(n)
    signs=((1,1,1),(1,0,-1),(1,-1,1))
    rows=[]
    for selected in hists:
        poly={(0,0):1}
        for kind,repetitions in enumerate(selected):
            for _ in range(repetitions):
                nextpoly={}
                for (n1,n2),weight in poly.items():
                    for t,sign in enumerate(signs[kind]):
                        if not sign:
                            continue
                        key=(n1+(t==1),n2+(t==2))
                        nextpoly[key]=nextpoly.get(key,0)+weight*sign
                poly=nextpoly
        rows.append(tuple(poly.get((t[1],t[2]),0) for t in hists))
    den=tuple(comb(n,t[1])*comb(n-t[1],t[2]) for t in hists)
    if any(rows[0][j]!=den[j] for j in range(len(hists))):
        raise AssertionError("empty-Walsh kernel is not identically one")
    return hists,tuple(rows),den


def exact_clean_walsh(n:int,hist:tuple[int,int,int],
                      special_selected:int,hypothesis:int)->Fraction:
    """Independent q8 length-two Fourier formula, all integer fractions.

    Let b be number of ordinary 1-edge selected paths and r number
    of complete ordinary 2-edge selected paths. alpha=3/4.
    The first two special character degrees have equal clean coefficients.
    Only the completely selected exceptional path distinguishes hypotheses.
    """
    if (sum(hist)!=n or len(hist)!=3 or any(v<0 for v in hist)
        or special_selected not in (0,1,2) or hypothesis not in (0,1)):
        raise ValueError("invalid ordinary/special Walsh signature")
    b,r=hist[1],hist[2]
    if special_selected==0:
        return Fraction(3**b*(2**r+7),2**(2*b+r+3))
    if special_selected==1:
        return Fraction(3**(b+1)*(2**r+7),2**(2*b+r+5))
    if hypothesis==0:
        return Fraction(3**b*(2**(r+1)+7),2**(2*b+r+4))
    return Fraction(3**b*(2**r+8),2**(2*b+r+4))


def scaled_clean_walsh(n:int,hist:tuple[int,int,int],
                       special_selected:int,hypothesis:int)->int:
    val=exact_clean_walsh(n,hist,special_selected,hypothesis)
    scaled=val*(1<<(3*n+6))
    if scaled.denominator!=1:
        raise AssertionError("clean Fourier scaling insufficient")
    return int(scaled)


def _dual_setup():
    if len(MARGINAL_NUMERATORS)!=4 or (
        sum(MARGINAL_NUMERATORS)!=-SCALE
        or any(v>0 for v in MARGINAL_NUMERATORS)
    ):
        raise AssertionError("signed marginal dual normalization wrong")
    if Fraction(sum(NORM_NUMERATORS),SCALE)!=EXACT_LOWER:
        raise AssertionError("dual lower objective wrong")
    if not EXACT_LOWER<UPPER:
        raise AssertionError("lower bound must be below registered upper")
    return frozen_dual_numerators()


def verify_integer_dual():
    """Verify EVERY one of 2*459 original-equivalent mask orbit inequalities.

    For each world h and mask orbit t=(t0,t1,t2;t_exc), the coefficient
    of a Walsh orbit s=(s0,s1,s2;s_exc) is
        W_h(s) * K_ord(s,t) * K2(s_exc,t_exc).
    All W are fractions with denominator W_SCALE; each ordinary K
    numerator is an integer divided by multinomial(n;t0,t1,t2).
    Multiplying the dual slack by
        SCALE*W_SCALE*multinomial(t)*2*n
    gives an INTEGER. Nonpositivity of every such integer proves the
    exact weak-duality lower bound on the full hypothesis-aware LP.
    """
    y=_dual_setup()
    hists,numerators,denoms=ordinary_kernel_numerators(N)
    if len(hists)!=M_ORD or len(y)!=3*len(hists):
        raise AssertionError("histogram/certificate mismatch")
    largest_slack=None
    equality_count=0
    checks=0
    for h in (0,1):
        sign=1 if h==0 else -1
        # Fold the three special selected-character dimensions before
        # the ordinary signed-polynomial integer matrix-vector products.
        proj=tuple(
            tuple(sum(
                y[3*i+s]*
                scaled_clean_walsh(N,selected,s,h)*K2[s][t_exc]
                for s in range(3)
            ) for i,selected in enumerate(hists))
            for t_exc in range(3)
        )
        for j,t in enumerate(hists):
            den=denoms[j]
            base=W_SCALE*den
            ordinary_weight=t[1]+2*t[2]
            for t_exc in range(3):
                sum_fourier=sum(
                    value*numerators[i][j]
                    for i,value in enumerate(proj[t_exc])
                )
                numerator=(
                    NORM_NUMERATORS[h]*base*2*N
                    +sign*2*N*sum_fourier
                    +MARGINAL_NUMERATORS[2*h]*base*ordinary_weight
                    +MARGINAL_NUMERATORS[2*h+1]*base*N*t_exc
                )
                if numerator>0:
                    raise AssertionError(
                        "BM-28 dual violated at h=%d hist=%s exc=%d: %d"
                        %(h,t,t_exc,numerator)
                    )
                if numerator==0:
                    equality_count+=1
                exact_slack=Fraction(numerator,SCALE*base*2*N)
                if largest_slack is None or exact_slack>largest_slack:
                    largest_slack=exact_slack
                checks+=1
    if checks!=2*M or largest_slack is None or largest_slack>0:
        raise AssertionError("dual proof coverage/max-slack failed")
    return {
        "certified_lower":EXACT_LOWER,
        "certified_upper":UPPER,
        "proved_limit_gap":UPPER-EXACT_LOWER,
        "ordinary_paths":N,"observed_edges":2*N+2,
        "orbit_classes_per_hypothesis":M,
        "dual_inequalities_checked":checks,
        "active_Fourier_orbit_multipliers":sum(bool(v) for v in y),
        "tight_mask_orbit_inequalities":equality_count,
        "max_dual_slack":largest_slack,
        "certificate_sha256":EXPECTED_SHA256,
        "external_optimizer_needed":False,
    }


def exact_limit_bracket():
    """Monotone projection: eta_inf >= eta_16; BM-27 upper for all n."""
    r=verify_integer_dual()
    return r["certified_lower"],r["certified_upper"]
