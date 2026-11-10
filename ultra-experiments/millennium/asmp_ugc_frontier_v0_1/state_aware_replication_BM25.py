"""BM-25: sharp q=8 repeated-path erasure with TWO ordinary length-2 paths.

The q8 BM-24 family has n ordinary two-edge u-v paths of gains 0/0
(flat/frustrated) and one exceptional two-edge path with gains 0/gamma,
gamma!=0. Both worlds freshly sample uniform K=F2^3 vertex labels.
Readout masks may differ by hypothesis and correlate across all six
observed edge bits, but remain independent of the current clean pattern.

Exact thresholds:
    n=1: eta_sym=1/44  (BM-08, one four-cycle)
    n=2: eta_sym=5/118 (BM-25, three overlapping four-cycles)

The n=2 value is proven by an exact 18-mask-histogram-orbit primal with
denominator 13216 and a three-Walsh-orbit dual with objective 5/118.
The dual expands into only SEVEN nonzero full-cube Walsh multipliers.
All 36 quotient and 128 full-cube mask-atom dual inequalities can be
verified in exact rational arithmetic, as can all 64 reported-pattern
equalities. No numerical LP solver is needed for any submitted proof.

Projecting any n>=2 instance to two ordinary paths + exceptional
establishes eta_sym(n)>=5/118, and BM-24's independent common
readout sampler gives eta_sym(n)<=1/8. Projection also proves
eta_sym(n+1)>=eta_sym(n). No exact formula is asserted for n>=3.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import lcm

try:
    from .repeated_gain_erasure_BM24 import gain_family, exact_common_cap
    from .repeated_theta_orbits_BM24 import (
        check_repeated_lp_matrix, build_repeated_lp,
    )
    from .generic_fourier_erasure_BM17 import Pair, Primal, Dual, certify
    from .sharp_erasure_optimality import critical_erasure_cap
except ImportError:
    from repeated_gain_erasure_BM24 import gain_family, exact_common_cap
    from repeated_theta_orbits_BM24 import (
        check_repeated_lp_matrix, build_repeated_lp,
    )
    from generic_fourier_erasure_BM17 import Pair, Primal, Dual, certify
    from sharp_erasure_optimality import critical_erasure_cap


ORBIT_DENOMINATOR = 13216
EXACT_ETA = Fraction(5,118)

# Each key is (ordinary 0/1/2 flip histogram, exceptional flip count).
# Both gain worlds have the same paths, so the two ordinary paths
# may exchange their identities in either hypothesis.
FLAT_MASK_NUMERATORS = {
    ((0,0,2),1):10,
    ((0,1,1),0):14,
    ((0,1,1),2):14,
    ((0,2,0),1):16,
    ((1,0,1),1):272,
    ((1,1,0),0):1274,
    ((1,1,0),2):266,
    ((2,0,0),0):11088,
    ((2,0,0),1):262,
}
FRUSTRATED_MASK_NUMERATORS = {
    ((0,0,2),0):5,
    ((0,0,2),2):5,
    ((0,1,1),1):28,
    ((0,2,0),0):8,
    ((0,2,0),2):8,
    ((1,0,1),0):136,
    ((1,0,1),2):136,
    ((1,1,0),0):1008,
    ((1,1,0),1):532,
    ((2,0,0),0):11219,
    ((2,0,0),2):131,
}

# Dual on three Walsh histogram signatures.  A selected-path histogram
# records how many of the two ordinary paths have 0,1,2 selected edges;
# the exceptional selection uses the same one-path histogram.
ORBIT_DUAL_WALSH = {
    ((0,0,2),(0,1,0)):Fraction(1216,1947),
    ((0,0,2),(0,0,1)):-Fraction(64,59),
    ((0,1,1),(0,0,1)):Fraction(64,177),
}
ORBIT_DUAL_NORMALIZATION = (Fraction(0),EXACT_ETA)
ORBIT_DUAL_MARGINALS = (
    (-Fraction(11,59),-Fraction(19,59)),
    (-Fraction(10,59),-Fraction(19,59)),
)


def model(gain:int=1):
    """The registered n=2, L=2, q=8 nonflat-gain instance."""
    return gain_family(2,2,q=8,gain=gain)


def _to_histogram_signature(ordinary:tuple[int,int,int],
                            exceptional_count:int):
    return ordinary,tuple(int(exceptional_count==i) for i in range(3))


def _orbit_law(numerators:dict)->dict[tuple,Fraction]:
    return {
        _to_histogram_signature(ordinary,exc):Fraction(w,ORBIT_DENOMINATOR)
        for (ordinary,exc),w in numerators.items()
    }


def sharp_orbit_masks():
    """Matching complete-output channel pair, in exact rational orbit mass."""
    return _orbit_law(FLAT_MASK_NUMERATORS),_orbit_law(
        FRUSTRATED_MASK_NUMERATORS
    )


def verify_exact_orbit_certificate(gain:int=1)->Fraction:
    """Verify all 18 Walsh classes and 36 dual mask-class inequalities."""
    net=model(gain)
    flat,frustrated=sharp_orbit_masks()
    assert len(net.types)==2 and net.orbit_size==18
    if sum(FLAT_MASK_NUMERATORS.values())!=ORBIT_DENOMINATOR:
        raise AssertionError("flat channel mass wrong")
    if sum(FRUSTRATED_MASK_NUMERATORS.values())!=ORBIT_DENOMINATOR:
        raise AssertionError("frustrated channel mass wrong")
    upper=net.verify_primal(flat,frustrated,cap=EXACT_ETA)
    lower=net.verify_dual(
        ORBIT_DUAL_NORMALIZATION,ORBIT_DUAL_WALSH,ORBIT_DUAL_MARGINALS
    )
    if upper!=lower or upper!=EXACT_ETA:
        raise AssertionError("q8 n2 orbit primal/dual mismatch")
    lp=build_repeated_lp(net,max_orbits=64)
    if (len(lp.equalities),len(lp.inequalities),lp.variables)!=(19,4,37):
        raise AssertionError("wrong reduced LP dimension")
    if not check_repeated_lp_matrix(lp,flat,frustrated,EXACT_ETA):
        raise AssertionError("independent orbit matrix rejects primal")
    return upper


def expanded_full_mask_law(h:int):
    """Uniformly expand exact orbit masses to all individual six-bit masks."""
    if h not in (0,1):
        raise ValueError("hypothesis must be 0 or 1")
    net=model()
    masses=sharp_orbit_masks()[h]
    out={}
    for mask in range(1<<net.m):
        signature=net.signature(mask)
        orbit_mass=masses.get(signature,Fraction(0))
        if orbit_mass:
            out[mask]=orbit_mass/net.orbit_size_of_signature(signature)
    if sum(out.values(),Fraction(0))!=1:
        raise AssertionError("full mask expansion lost normalization")
    return out


def _integerize(law:dict[int,Fraction]):
    denominator=lcm(*(p.denominator for p in law.values()))
    return {mask:int(p*denominator) for mask,p in law.items()},denominator


def sparse_full_dual():
    """Seven full Fourier multipliers, lifting the exact 3-orbit dual.

    Averaging a full Walsh-dual under path/edge permutations replaces
    the coefficients on an orbit by their sum. Conversely, distribute
    the orbit multiplier equally over all individual Walsh supports
    in its orbit. Divide each type's marginal multiplier equally across
    its constituent observed edges. This gives a valid full-cube dual.
    """
    net=model()
    coefficients={}
    for mask in range(1<<net.m):
        sig=net.signature(mask)
        total=ORBIT_DUAL_WALSH.get(sig,Fraction(0))
        if total:
            coefficients[mask]=total/net.orbit_size_of_signature(sig)
    if len(coefficients)!=7 or set(coefficients)!={
        31,47,55,59,61,62,63
    }:
        raise AssertionError("unexpected seven Fourier dual supports")
    denominator=lcm(*(v.denominator for v in
        (*ORBIT_DUAL_NORMALIZATION,*coefficients.values())))
    zrows=[]
    for h in range(2):
        z=[]
        for ty,coeff in zip(net.types,ORBIT_DUAL_MARGINALS[h]):
            z.extend((coeff/Fraction(ty.length*ty.count),)*
                     (ty.length*ty.count))
        zrows.extend(z)
    marginal_denom=lcm(*(z.denominator for z in zrows))
    proof=Dual(
        denominator,
        {mask:int(v*denominator) for mask,v in coefficients.items()},
        tuple(int(v*denominator) for v in ORBIT_DUAL_NORMALIZATION),
        marginal_denom,
        tuple(int(v*marginal_denom) for v in zrows),
    )
    if -sum(proof.marginal_numerators)!=proof.marginal_denominator:
        raise AssertionError("full dual eta marginal coefficient wrong")
    return proof


@lru_cache(maxsize=8)
def verify_exact_full_certificate(gain:int=1):
    """Independent 64-output primal and 128-mask dual check via BM-17."""
    net=model(gain)
    p0,D0=_integerize(expanded_full_mask_law(0))
    p1,D1=_integerize(expanded_full_mask_law(1))
    denominator=lcm(D0,D1)
    primal=Primal(
        denominator,
        {i:w*(denominator//D0) for i,w in p0.items()},
        {i:w*(denominator//D1) for i,w in p1.items()},
        EXACT_ETA,
    )
    pair=Pair(net.game(0),net.game(1))
    report=certify(pair,net.m,primal,sparse_full_dual())
    if report.optimum!=EXACT_ETA or not report.full_output_equal:
        raise AssertionError("full six-bit q8 n2 proof failed")
    if report.walsh_terms!=7 or report.checked_mask_inequalities!=128:
        raise AssertionError("unexpected exact proof verification coverage")
    return report


def projection_bounds(n:int,*,gain:int=1):
    """Sharp known lower/upper bracket for ANY n>=2, q=8, L=2.

    Projection of any n-ordinary full-output equality onto two ordinary
    paths plus the exceptional path preserves the fresh uniform labeling
    law and yields legal mask marginals under the same error cap.
    Therefore eta_sym(n)>=eta_sym(2)=5/118 for arbitrary correlated,
    world-specific masks. BM-24's common mask gives eta_sym(n)<=1/8.
    No exact n>=3 optimum is asserted.
    """
    if not isinstance(n,int) or n<2:
        raise ValueError("projection to two ordinary paths requires n>=2")
    net=gain_family(n,2,q=8,gain=gain)
    if not (
        net.types[0].count==n and net.types[0].gain0==0
        and net.types[0].gain1==0 and net.types[1].count==1
        and net.types[1].gain1==gain
    ):
        raise AssertionError("registered repeated-path projection changed")
    return EXACT_ETA,exact_common_cap(2)


def theorem_receipt(gain:int=1):
    eta=verify_exact_orbit_certificate(gain)
    full=verify_exact_full_certificate(gain)
    return {
        "q":8,"path_length":2,"ordinary_paths":2,
        "exceptional_paths":1,"vertices":5,"edges":6,
        "full_mask_atoms_per_world":64,
        "orbit_mask_classes_per_world":18,
        "hypothesis_aware_exact_erasure":str(eta),
        "single_ordinary_cycle_exact":str(critical_erasure_cap(8,4)),
        "strict_replication_cost_ratio":str(eta/critical_erasure_cap(8,4)),
        "original_common_mask_cap":str(exact_common_cap(2)),
        "nonzero_orbit_dual_Fourier_signatures":len(ORBIT_DUAL_WALSH),
        "nonzero_full_dual_Fourier_subsets":full.walsh_terms,
        "full_dual_mask_inequalities_checked":full.checked_mask_inequalities,
        "complete_output_laws_equal":full.full_output_equal,
        "n_ge2_projected_lower":str(projection_bounds(250,gain=gain)[0]),
        "n_ge2_common_upper":str(projection_bounds(250,gain=gain)[1]),
        "higher_n_exact_optimum_claimed":False,
    }
