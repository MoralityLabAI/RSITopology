"""BM-10: five-edge contrabalanced diamond exact erasure/dual certificates.

Take theta path lengths (1,2,2), with four vertices and five edges.
The path translation gains are 0,1,2 in K=F2^2, so both triangles and
the outer four-cycle are frustrated. An adversary may choose a distinct
Boolean XOR mask law under the flat or frustrated hypothesis, independently
of the current fresh uniform vertex labeling; each reported edge has mask
marginal <= eta.

The exact minimum full-output erasure cap is eta*=1/5. A *common*
mask law attains it. A sparse rational Walsh-domain dual proves that
every erasing pair needs eta>=1/5.

Keeping ONLY the Fourier constraints whose clean coefficient vanishes in
the frustrated world gives an exact weaker LP optimum 1/8. This supplies
a certified counterexample to a zero-spectrum-only surrogate for the
ASMP-14 symmetrization interaction index.

No external optimizer, floating point, model weights, or GPU is required
to verify either certificate.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product

EDGES = ((0,1),(0,2),(2,1),(0,3),(3,1))
SHIFT = (0,1,0,2,0)
N_VERTICES=4
N_EDGES=5
MASK_COUNT=1<<N_EDGES
ALPHABET=4
LABEL_COUNT=ALPHABET**N_VERTICES

# Both worlds use the same common mask distribution (integer /20).
PRIMAL_DENOMINATOR=20
PRIMAL_MASK_COUNTS={
    0:5,1:2,2:2,4:2,5:1,8:2,9:1,10:1,16:2,18:1,20:1
}

# Dual to the FULL output erasure LP in Walsh form.
# y_norm=(1/20,3/20), and y_walsh[S] below. The signed
# marginal multipliers z_h,i are -1/5 at the registered bit positions.
DUAL_NORMALIZATION=(Fraction(1,20),Fraction(3,20))
DUAL_WALSH={
    1:Fraction(1,10),2:-Fraction(1,10),4:Fraction(1,10),
    6:-Fraction(1,5),7:Fraction(1,5),9:-Fraction(1,5),
    10:-Fraction(1,5),11:Fraction(2,5),14:Fraction(2,5),
    17:Fraction(1,5),18:Fraction(1,5),19:-Fraction(2,5),
    22:Fraction(2,5),25:Fraction(2,5),27:-Fraction(2,5),
    29:-Fraction(2,5),30:-Fraction(2,5)
}
DUAL_MARGINAL=(
    {1:-Fraction(1,5),3:-Fraction(1,5)},
    {0:-Fraction(1,5),2:-Fraction(1,5),4:-Fraction(1,5)}
)

# This weaker mask law (integer /16) satisfies exactly the Fourier
# vanishing constraints, but does not erase the entire output.
ZERO_DENOMINATOR=16
ZERO_ONLY_MASK_COUNTS={
    0:7,1:1,2:2,4:2,8:1,9:1,16:2
}


def counts_for(shifts: tuple[int,...]) -> tuple[int,...]:
    """Exact vertex-label oracle for every Boolean edge-satisfaction pattern."""
    if len(shifts)!=N_EDGES or any(not 0<=x<ALPHABET for x in shifts):
        raise ValueError("five shifts from F2^2 required")
    counts=[0]*MASK_COUNT
    for a in product(range(ALPHABET),repeat=N_VERTICES):
        mask=0
        for i,((u,v),shift) in enumerate(zip(EDGES,shifts)):
            if (a[u]^a[v])==shift:
                mask|=1<<i
        counts[mask]+=1
    if sum(counts)!=LABEL_COUNT:
        raise AssertionError("label census normalization failed")
    return tuple(counts)


def clean_counts() -> tuple[tuple[int,...],tuple[int,...]]:
    return counts_for((0,)*N_EDGES),counts_for(SHIFT)


def walsh(counts: tuple[int,...], subset: int) -> int:
    """Unnormalized Walsh coefficient: signed integer sum over patterns."""
    if len(counts)!=MASK_COUNT or not 0<=subset<MASK_COUNT:
        raise ValueError("invalid clean distribution/subset")
    return sum(
        (-1 if (x&subset).bit_count()%2 else 1)*count
        for x,count in enumerate(counts)
    )


def output_counts(
    clean: tuple[int,...],
    mask_weights: dict[int,int],
) -> tuple[int,...]:
    """Integer convolution with the Boolean XOR mask channel."""
    if len(clean)!=MASK_COUNT or any(
        not 0<=mask<MASK_COUNT or weight<0
        for mask,weight in mask_weights.items()
    ):
        raise ValueError("invalid count table or mask")
    return tuple(
        sum(clean[y^mask]*weight for mask,weight in mask_weights.items())
        for y in range(MASK_COUNT)
    )


def per_bit_counts(mask_weights: dict[int,int]) -> tuple[int,...]:
    return tuple(
        sum(weight for mask,weight in mask_weights.items()
            if mask&(1<<i))
        for i in range(N_EDGES)
    )


def zero_only_constraints() -> tuple[int,...]:
    """Clean Fourier coefficients present flat, absent nonflat."""
    p0,p1=clean_counts()
    return tuple(
        subset for subset in range(1,MASK_COUNT)
        if walsh(p0,subset)!=0 and walsh(p1,subset)==0
    )


def verify_full_primal() -> bool:
    """Legal common Q with eta=1/5, exact full-output equality."""
    p0,p1=clean_counts()
    m=PRIMAL_MASK_COUNTS
    assert sum(m.values())==PRIMAL_DENOMINATOR
    assert per_bit_counts(m)==(4,)*N_EDGES
    assert output_counts(p0,m)==output_counts(p1,m)
    return True


def full_dual_slacks() -> tuple[tuple[Fraction,...],tuple[Fraction,...]]:
    """A universal dual bound on each of 2*32 adversarial mask atoms.

    The primal has normalization equalities for Q0 and Q1; for each
    nonempty Walsh subset S,
        hatP0(S) E_Q0[chi_S] - hatP1(S) E_Q1[chi_S] = 0,
    and marginal inequalities E_Qh[M_i]-eta<=0.

    The minimization dual has y for equalities (unrestricted), z<=0 for
    inequalities, and all mask-atom coefficient slacks <=0. The eta
    coefficient is -sum(z)=1. Its objective y_norm0+y_norm1=1/5.
    """
    p0,p1=clean_counts()
    results=[]
    for h in (0,1):
        slacks=[]
        for mask in range(MASK_COUNT):
            lhs=DUAL_NORMALIZATION[h]
            for subset,weight in DUAL_WALSH.items():
                sign=-1 if (mask&subset).bit_count()%2 else 1
                term=Fraction(walsh(p0 if h==0 else p1,subset),
                              LABEL_COUNT)*sign*weight
                lhs+=term if h==0 else -term
            lhs+=sum(
                (dual_weight for i,dual_weight in DUAL_MARGINAL[h].items()
                 if mask&(1<<i)),Fraction(0)
            )
            slacks.append(lhs)
        results.append(tuple(slacks))
    return results[0],results[1]


def verify_full_dual() -> bool:
    """Any erasing pair satisfies eta>=1/5, by weak LP duality."""
    assert sum(DUAL_NORMALIZATION)==Fraction(1,5)
    assert all(z<=0 for row in DUAL_MARGINAL for z in row.values())
    assert -sum(
        (z for row in DUAL_MARGINAL for z in row.values()),Fraction(0)
    )==1
    slacks=full_dual_slacks()
    assert all(v<=0 for row in slacks for v in row)
    return True


def verify_zero_only_surrogate() -> bool:
    """The Fourier-ZERO-ONLY relaxation has exact optimum 1/8.

    The two zero constraints have subset masks 30 (size 4) and 31 (size 5).
    For subset 30, E[chi_30(M)]=0 forces Pr(odd on 30)=1/2.
    Union bound then gives 4eta>=1/2, so eta>=1/8.
    The explicit witness achieves eta=1/8 and has both characters zero.
    """
    assert zero_only_constraints()==(30,31)
    m=ZERO_ONLY_MASK_COUNTS
    assert sum(m.values())==ZERO_DENOMINATOR
    assert per_bit_counts(m)==(2,)*N_EDGES
    for subset in (30,31):
        assert sum(
            ((-1 if (mask&subset).bit_count()%2 else 1)*weight)
            for mask,weight in m.items()
        )==0
    # The zero-only mask law fails to equalize the complete outputs.
    p0,p1=clean_counts()
    assert output_counts(p0,m)!=output_counts(p1,m)
    return True


def receipt() -> dict[str,str|bool|int]:
    return {
        "graph":"5-edge diamond theta, path lengths (1,2,2)",
        "q":ALPHABET,
        "full_erasure_optimum":"1/5",
        "full_primal":verify_full_primal(),
        "full_dual":verify_full_dual(),
        "zero_only_optimum":"1/8",
        "zero_only_certificate":verify_zero_only_surrogate(),
        "zero_only_underestimate_factor":"8/5",
        "single_triangle_threshold":"1/6",
        "symmetrization_interaction_index":"6/5",
        "dual_mask_constraints_checked":2*MASK_COUNT,
        "numeric_optimizer_required":False,
    }


if __name__=="__main__":
    print(receipt())
