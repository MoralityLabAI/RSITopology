"""BM-09: exact shared-cycle theta-graph erasure certificates.

K_{2,3} consists of three length-two u-v paths. Edge occurrences are ordered
as path A=(0,1), B=(2,3), C=(4,5). The tested pair is flat vs path
translation gains (0,1,2), so all three four-cycles are frustrated in the
second world. For q=4, the exact minimax cap is 1/6 via a short parity
counting proof and an explicit common mask. For q=8 it is 29/630 via a
fully exact rational primal/dual linear-program certificate.

The channel is state/hypothesis-aware, a Boolean XOR mask independent of the
current freshly sampled uniform vertex labeling, with a common per-edge
marginal flip cap. No external solver is needed to VERIFY the certificates.

This module is an elementary finite result, not a general theta-family
formula or a real-world AI safety claim.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product

THETA_EDGES = ((0,2),(1,2),(0,3),(1,3),(0,4),(1,4))
THETA_SHIFTS = (0,0,0,1,0,2)
N_EDGES = 6
MASKS = 1 << N_EDGES

# Each integer is probability numerator, denominator 10080. These arose
# from an LP search and are reverified with integer arithmetic in every test.
Q8_FLAT = (
    8736,107,107,0,107,0,0,55,107,0,0,55,0,55,55,0,
    107,0,0,55,0,3,3,0,0,3,3,0,55,0,0,3,
    107,0,0,55,0,3,3,0,0,3,3,0,55,0,0,3,
    0,55,55,0,55,0,0,3,55,0,0,3,0,3,3,0,
)
Q8_FRUSTRATED = (
    8895,0,0,107,0,55,55,0,0,55,55,0,107,0,0,55,
    0,55,55,0,55,0,0,3,55,0,0,3,0,3,3,0,
    0,55,55,0,55,0,0,3,55,0,0,3,0,3,3,0,
    107,0,0,55,0,3,3,0,0,3,3,0,55,0,0,3,
)

# Exact dual certificate for the LP with 64 output-equality equations,
# two normalization equations, and 12 edge-marginal inequalities.
# Equality dual: 66 entries /37800. Inequality dual: 12 entries /300.
# Signed dual margins are nonpositive, matching min(c.x), Ax=b, Gx<=0.
Q8_DUAL_EQUALITY = (
    25288,42712,85048,-7096,42712,15080,-7096,104536,
    42712,15080,-7096,104536,15080,62200,104536,-17304,
    42712,15080,-7096,104536,15080,62200,104536,-17304,
    15080,62200,104536,-17304,62200,4872,-17304,124024,
    37840,10208,-11968,99664,10208,57328,99664,-22176,
    10208,57328,99664,-22176,57328,0,-22176,119152,
    10208,57328,99664,-22176,57328,0,-22176,119152,
    57328,0,-22176,119152,0,76816,119152,-32384,
    -31519,33259,
)
Q8_DUAL_MARGINAL = (-29,-155,-29,-29,-29,0,0,0,0,0,0,-29)
Q8_MASS_DENOMINATOR = 10080
Q8_DUAL_EQ_DENOMINATOR = 37800
Q8_DUAL_MARG_DENOMINATOR = 300


def theta_counts(q: int, shifts: tuple[int,...]) -> tuple[int,...]:
    """Independent exact vertex enumeration, probability denominator q^5."""
    if q < 2 or q & (q-1) or len(shifts)!=N_EDGES or any(
        not 0<=s<q for s in shifts
    ):
        raise ValueError("q must be F2^s and six valid edge gains required")
    counts=[0]*MASKS
    for labels in product(range(q),repeat=5):
        observed=sum(
            1<<i for i,((u,v),s) in enumerate(zip(THETA_EDGES,shifts))
            if labels[u]^labels[v]==s
        )
        counts[observed]+=1
    assert sum(counts)==q**5
    return tuple(counts)


def theta_laws(q: int) -> tuple[tuple[int,...],tuple[int,...]]:
    return theta_counts(q,(0,)*N_EDGES),theta_counts(q,THETA_SHIFTS)


def xor_convolve_counts(
    clean_counts: tuple[int,...],mask_weights: tuple[int,...],
) -> tuple[int,...]:
    """Unnormalized output counts for clean denominator q^5 and mask D."""
    if len(clean_counts)!=MASKS or len(mask_weights)!=MASKS:
        raise ValueError("six-edge Boolean vectors required")
    return tuple(
        sum(clean_counts[out^mask]*weight
            for mask,weight in enumerate(mask_weights))
        for out in range(MASKS)
    )


def signed_walsh_count(counts: tuple[int,...], subset: int) -> int:
    """Unnormalized Walsh numerator: sign by parity of observed TRUE bits."""
    if len(counts)!=MASKS or not 0<=subset<MASKS:
        raise ValueError("six-edge count table and subset mask required")
    return sum((-1 if (subset & x).bit_count()%2 else 1)*count
               for x,count in enumerate(counts))


def uniform_cap_counts(weights: tuple[int,...]) -> int:
    """Maximum per-bit marginal numerator for a normalized mask integer law."""
    if len(weights)!=MASKS or any(x<0 for x in weights):
        raise ValueError("invalid six-edge mask weights")
    return max(
        sum(weight for mask,weight in enumerate(weights)
            if mask & (1<<edge))
        for edge in range(N_EDGES)
    )


def q4_common_mask() -> tuple[int,...]:
    """Exact erasure channel: 0 mask with 3/12, six singles and three pairs /12."""
    weights=[0]*MASKS
    weights[0]=3
    for mask in (1,2,4,8,16,32,10,17,36):
        weights[mask]=1
    assert sum(weights)==12
    assert uniform_cap_counts(tuple(weights))==2
    return tuple(weights)



def q4_one_balanced_mask() -> tuple[int,...]:
    """One balanced theta cycle, two frustrated; sharp eta=1/8.

    Path gains (0,1,0), with the (A,C) four-cycle balanced. This
    common-channel mask achieves the isolated four-cycle lower bound.
    Denominator 16: zero mask 6, masks 4 and 8 weight 2, remaining
    singleton/pair masks (1,2,16,17,32,34) weight 1.
    """
    weights=[0]*MASKS
    weights[0]=6
    weights[4]=weights[8]=2
    for mask in (1,2,16,17,32,34):
        weights[mask]=1
    assert sum(weights)==16
    assert uniform_cap_counts(tuple(weights))==2
    return tuple(weights)


def verify_q4_one_balanced_case() -> bool:
    """Sharp by isolated-cycle restriction and explicit common mask."""
    shifts=(0,0,0,1,0,0)
    p0=theta_counts(4,(0,)*N_EDGES)
    p1=theta_counts(4,shifts)
    mask=q4_one_balanced_mask()
    assert xor_convolve_counts(p0,mask)==xor_convolve_counts(p1,mask)
    assert Fraction(uniform_cap_counts(mask),sum(mask))==Fraction(1,8)
    return True


def verify_q4_primal() -> bool:
    p0,p1=theta_laws(4)
    m=q4_common_mask()
    assert uniform_cap_counts(m)==2
    assert xor_convolve_counts(p0,m)==xor_convolve_counts(p1,m)
    return True


def verify_q4_lower_lemma() -> bool:
    """Finite premises and pointwise inequality for the universal 1/6 proof.

    For each of the six 5-subsets and the full 6-edge set, the Fourier
    character is nonzero under flat but ZERO under all-distinct path gains.
    Any achieving Q0 must therefore have 5-subset and 6-subset Fourier
    coefficients zero. This forces P[odd weight]=1/2 and E(T)=3, where
    T(mask)=k for even mask weight k, else 6-k.
    Since T<=k+4*1[odd], E[k]>=1 and some marginal>=1/6.
    The pointwise inequality is checked for all 64 masks here.
    """
    p0,p1=theta_laws(4)
    for subset in [MASKS-1]+[(MASKS-1)^(1<<i) for i in range(N_EDGES)]:
        expect=4**5//(4 if subset==MASKS-1 else 8)
        assert signed_walsh_count(p0,subset)==expect
        assert signed_walsh_count(p1,subset)==0
    for mask in range(MASKS):
        k=mask.bit_count()
        t=k if not k%2 else N_EDGES-k
        assert t<=k+4*(k%2)
    return True


def verify_q8_primal() -> bool:
    """Exact rational attaining pair, erasure eta=29/630."""
    p0,p1=theta_laws(8)
    a,b=Q8_FLAT,Q8_FRUSTRATED
    d=Q8_MASS_DENOMINATOR
    assert len(a)==len(b)==MASKS
    assert all(x>=0 for x in a+b)
    assert sum(a)==sum(b)==d
    assert uniform_cap_counts(a)==uniform_cap_counts(b)==464
    assert Fraction(464,d)==Fraction(29,630)
    assert xor_convolve_counts(p0,a)==xor_convolve_counts(p1,b)
    return True


def verify_q8_dual() -> bool:
    """Exact dual lower bound: eta>=29/630, with integer arithmetic.

    Primal layout (Q0[0:64],Q1[0:64],eta); constraints:
      sum Q0=sum Q1=1;
      clean_P0 * Q0 = clean_P1 * Q1;
      sum_{mask:bit_i=1} Q_h(mask) - eta <= 0 for each h,i.
    All primal variables >=0.

    y is equality multiplier, z<=0 for marginal inequalities.
    Dual feasibility requires for every mask:
      sum_y y[out]*P0[out xor mask]+y[64]+sum_i z[i]bit_i <=0
      -sum_y y[out]*P1[out xor mask]+y[65]+sum_i z[6+i]bit_i <=0
      -sum z <=1.
    Then eta>=y[64]+y[65]. Everything is exact integer arithmetic.
    """
    p0,p1=theta_laws(8)
    y,z=Q8_DUAL_EQUALITY,Q8_DUAL_MARGINAL
    assert len(y)==MASKS+2 and len(z)==2*N_EDGES
    assert all(v<=0 for v in z)
    assert -sum(z)==Q8_DUAL_MARG_DENOMINATOR
    assert Fraction(y[64]+y[65],Q8_DUAL_EQ_DENOMINATOR)==Fraction(29,630)
    factor=Q8_DUAL_EQ_DENOMINATOR//Q8_DUAL_MARG_DENOMINATOR
    scale=8**5
    for mask in range(MASKS):
        u0=(sum(y[out]*p0[out^mask] for out in range(MASKS))
            +y[64]*scale
            +factor*scale*sum(z[i] for i in range(N_EDGES)
                              if mask&(1<<i)))
        u1=(-sum(y[out]*p1[out^mask] for out in range(MASKS))
            +y[65]*scale
            +factor*scale*sum(z[N_EDGES+i] for i in range(N_EDGES)
                              if mask&(1<<i)))
        if u0>0 or u1>0:
            raise AssertionError("dual constraint violated at mask "+str(mask))
    return True


def exact_theta_certificate() -> dict[str,str|bool]:
    a=verify_q4_lower_lemma() and verify_q4_primal()
    a1=verify_q4_one_balanced_case()
    b=verify_q8_primal() and verify_q8_dual()
    return {
        "graph":"K_{2,3}; two independent cycles with shared paths",
        "gains":"(0,1,2) path translations",
        "q4_exact_erasure":"1/6",
        "q4_one_balanced_exact_erasure":"1/8",
        "q4_one_balanced_verified":a1,
        "q4_lower_verified":a,
        "q8_exact_erasure":"29/630",
        "q8_primal_dual_verified":b,
        "q4_single_cycle_bound":"1/8",
        "q8_single_cycle_bound":"1/44",
        "external_solver_required":False,
    }


if __name__=="__main__":
    print(exact_theta_certificate())
