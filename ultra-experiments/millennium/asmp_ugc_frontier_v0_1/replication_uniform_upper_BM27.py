"""BM-27: a uniform q=8 world-dependent eraser with cap 5/52.

Consider n ordinary two-edge u-v paths whose total gain is 0 in both
hypotheses, and one exceptional two-edge path whose gain switches from
0 to a fixed nonzero element of F2^3. Each episode draws fresh uniform
vertex labels. The adversary chooses a hypothesis-dependent correlated
XOR readout mask, independent of the current clean observation.

The exact, finite-branch erasing construction below works for ALL n>=1:
  eta_sym(n,8,2) <= 5/52 ~ 0.09615384615.
It improves BM-24's universal common-channel bound 1/8.

Define pair mask/clean laws (bits ordered 00,10,01,11):
  I = delta_00,
  A = 7/8 delta_00 + 1/8 delta_11,
  B = 3/4 delta_00 + 1/8(delta_10+delta_01),
  E = 1/2 delta_00 + 1/4(delta_10+delta_01).

The clean laws are
 P0 = 1/8 A^n tensor A + 7/8 B^n tensor B,
 P1 = 1/8 A^n tensor B + 1/8 B^n tensor A
                            +6/8 B^n tensor B.

Here A^n means n-fold TENSOR product, while * denotes pairwise XOR
convolution. Let I^n be the all-zero ordinary mask.

Q0= (3/13) I^n tensor E + (1/13) A^n tensor I
    +(1/13) A^n tensor E + (6/13) B^n tensor I
    +(2/13) B^n tensor A.

Q1= (3/13) I^n tensor E + (2/13) A^n tensor A
    +(6/13) B^n tensor I + (2/13) B^n tensor B.

The identities E=2B-I as signed measures and A*E=B*E make
P0*Q0=P1*Q1 as a formal polynomial identity in the five ordinary
tensor-power distributions A^n,B^n,(A*A)^n,(A*B)^n,(B*B)^n.
All world/edge marginal readout flip probabilities equal 5/52.

The clean measurement's pair distributions and the mask branches have
denominators <=13*8^n; the sampler uses O(n) independent small draws.
This is an UPPER BOUND, not an asymptotically sharp theorem.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import lcm

try:
    from .repeated_gain_erasure_BM24 import gain_family
    from .state_aware_three_replica_BM26 import EXACT_CAP as N3_LOWER
except ImportError:
    from repeated_gain_erasure_BM24 import gain_family
    from state_aware_three_replica_BM26 import EXACT_CAP as N3_LOWER


PAIR_I=(Fraction(1),Fraction(0),Fraction(0),Fraction(0))
PAIR_A=(Fraction(7,8),Fraction(0),Fraction(0),Fraction(1,8))
PAIR_B=(Fraction(3,4),Fraction(1,8),Fraction(1,8),Fraction(0))
PAIR_E=(Fraction(1,2),Fraction(1,4),Fraction(1,4),Fraction(0))
PAIRS={"I":PAIR_I,"A":PAIR_A,"B":PAIR_B,"E":PAIR_E}
UPPER_CAP=Fraction(5,52)

# Each component is (ordinary path pair-mask distribution, exceptional
# path pair-mask distribution, integer mixture numerator over 13).
COMPONENTS={
    0:(("I","E",3),("A","I",1),("A","E",1),
       ("B","I",6),("B","A",2)),
    1:(("I","E",3),("A","A",2),("B","I",6),("B","B",2)),
}
# Clean endpoint-difference mixture, with numerators over q=8.
CLEAN_COMPONENTS={
    0:(("A","A",1),("B","B",7)),
    1:(("A","B",1),("B","A",1),("B","B",6)),
}


def _check_world(h:int)->None:
    if h not in (0,1):
        raise ValueError("hypothesis must be 0 or 1")


def xor_pair(a:tuple[Fraction,...],b:tuple[Fraction,...]):
    """Four-state pairwise XOR convolution, exact and independent."""
    if len(a)!=4 or len(b)!=4:
        raise ValueError("need four-state pair distributions")
    return tuple(sum((a[x]*b[x^out] for x in range(4)),
                     Fraction(0)) for out in range(4))


def pair_bit_marginals(pair:tuple[Fraction,...])->tuple[Fraction,Fraction]:
    if len(pair)!=4 or sum(pair,Fraction(0))!=1 or any(x<0 for x in pair):
        raise ValueError("normalized nonnegative pair distribution required")
    return pair[1]+pair[3],pair[2]+pair[3]


def ordinary_category(clean:str,mask:str)->str:
    if clean not in ("A","B") or mask not in ("I","A","B"):
        raise ValueError("registered ordinary pair categories required")
    return clean if mask=="I" else "".join(sorted((clean,mask)))


def formal_output_components(h:int):
    """Coefficients of five separate ordinary tensor-power laws.

    Every category is a 4-entry exact probability vector on the
    exceptional two-bit readout. Equality of the resulting dictionaries
    proves complete equality of ALL 2^(2n+2) outputs for any n, because
    each ordinary category denotes the same n-fold tensor power under
    either hypothesis.
    """
    _check_world(h)
    result=defaultdict(lambda: (Fraction(0),)*4)
    for ordinary_mask,exception_mask,mask_weight in COMPONENTS[h]:
        for clean_ord,clean_exc,clean_weight in CLEAN_COMPONENTS[h]:
            category=ordinary_category(clean_ord,ordinary_mask)
            special=xor_pair(PAIRS[clean_exc],PAIRS[exception_mask])
            weight=Fraction(mask_weight*clean_weight,13*8)
            result[category]=tuple(
                x+weight*y for x,y in zip(result[category],special)
            )
    return dict(result)


def verify_convolution_identity()->bool:
    """Finite exact signed-measure identities imply equality for all n."""
    if tuple(2*b-i for b,i in zip(PAIR_B,PAIR_I))!=PAIR_E:
        raise AssertionError("E=2B-I signed convolution identity failed")
    if xor_pair(PAIR_A,PAIR_E)!=xor_pair(PAIR_B,PAIR_E):
        raise AssertionError("the pair equalizer is not symmetric")
    if any(sum(PAIRS[k],Fraction(0))!=1 or any(x<0 for x in PAIRS[k])
           for k in PAIRS):
        raise AssertionError("illegal pair noise distribution")
    for h in (0,1):
        if sum(weight for _,_,weight in COMPONENTS[h])!=13:
            raise AssertionError("hypothesis mask mixture not normalized")
        if sum(weight for _,_,weight in CLEAN_COMPONENTS[h])!=8:
            raise AssertionError("clean conditional mixture not normalized")
    a,b=formal_output_components(0),formal_output_components(1)
    if a!=b or set(a)!={"A","B","AA","AB","BB"}:
        raise AssertionError("full ordinary tensor-power identity failed")
    if sum((sum(vec,Fraction(0)) for vec in a.values()),
           Fraction(0))!=1:
        raise AssertionError("outcome law lost probability")
    return True


def exact_mask_rate(h:int):
    """Per-ordinary-bit and per-exceptional-bit error costs in Qh."""
    _check_world(h)
    ordinary=sum(
        (Fraction(weight,13)*pair_bit_marginals(PAIRS[o])[0]
         for o,_,weight in COMPONENTS[h]),Fraction(0)
    )
    special=sum(
        (Fraction(weight,13)*pair_bit_marginals(PAIRS[e])[0]
         for _,e,weight in COMPONENTS[h]),Fraction(0)
    )
    if (ordinary,special)!=(UPPER_CAP,UPPER_CAP):
        raise AssertionError("exact two-world marginal caps differ")
    return ordinary,special


def theorem_upper(n:int,*,gain:int=1)->Fraction:
    """Exact proof for unbounded replication, with constant-size algebra."""
    if not isinstance(n,int) or n<1:
        raise ValueError("one or more ordinary paths required")
    net=gain_family(n,2,q=8,gain=gain)
    assert net.path_count==n+1 and net.m==2*n+2
    if not verify_convolution_identity():
        raise AssertionError("failed convolution identity")
    if any(exact_mask_rate(h)!=(UPPER_CAP,UPPER_CAP) for h in (0,1)):
        raise AssertionError("mask cap violated")
    return UPPER_CAP


def _tensor_pair(a:dict[int,Fraction],pair:tuple[Fraction,...],
                 shift:int)->dict[int,Fraction]:
    out={}
    for existing,weight in a.items():
        for bits,p in enumerate(pair):
            if p:
                mask=existing | (bits<<shift)
                out[mask]=out.get(mask,Fraction(0))+weight*p
    return out


def explicit_mask_law(n:int,h:int,*,max_bits:int=12):
    """Exact hypothesis-aware mask distribution for small graph controls."""
    _check_world(h)
    if n<1 or 2*n+2>max_bits:
        raise ValueError("explicit masks exceed registered resource limit")
    result={}
    for ordinary,special,weight in COMPONENTS[h]:
        branch={0:Fraction(weight,13)}
        for j in range(n):
            branch=_tensor_pair(branch,PAIRS[ordinary],2*j)
        branch=_tensor_pair(branch,PAIRS[special],2*n)
        for mask,p in branch.items():
            result[mask]=result.get(mask,Fraction(0))+p
    result={mask:p for mask,p in result.items() if p}
    if sum(result.values(),Fraction(0))!=1:
        raise AssertionError("explicit mask law normalization")
    return result


def exact_clean_law(n:int,h:int,*,max_bits:int=12):
    """Independent symbolic clean conditional mixture, no vertex census."""
    _check_world(h)
    if n<1 or 2*n+2>max_bits:
        raise ValueError("explicit clean law exceeds registered resource limit")
    result={}
    for ordinary,exceptional,weight in CLEAN_COMPONENTS[h]:
        branch={0:Fraction(weight,8)}
        for j in range(n):
            branch=_tensor_pair(branch,PAIRS[ordinary],2*j)
        branch=_tensor_pair(branch,PAIRS[exceptional],2*n)
        for mask,p in branch.items():
            result[mask]=result.get(mask,Fraction(0))+p
    if sum(result.values(),Fraction(0))!=1:
        raise AssertionError("clean conditional mixture not normalized")
    return result


def xor_convolve(a:dict[int,Fraction],b:dict[int,Fraction]):
    """Finite direct XOR convolution of separately derived laws."""
    out={}
    for x,px in a.items():
        for y,py in b.items():
            index=x^y
            out[index]=out.get(index,Fraction(0))+px*py
    return {x:p for x,p in out.items() if p}


def verify_complete_small(n:int,*,max_bits:int=12)->bool:
    """All 2^(2n+2) complete reported probabilities after separate Qh."""
    if n<1 or 2*n+2>max_bits:
        raise ValueError("small independent full-output check only")
    p0,p1=exact_clean_law(n,0),exact_clean_law(n,1)
    q0,q1=explicit_mask_law(n,0),explicit_mask_law(n,1)
    if xor_convolve(p0,q0)!=xor_convolve(p1,q1):
        raise AssertionError("BM-27 full output distributions not identical")
    for h,q in ((0,q0),(1,q1)):
        for bit in range(2*n+2):
            rate=sum((weight for mask,weight in q.items()
                      if mask&(1<<bit)),Fraction(0))
            if rate!=UPPER_CAP:
                raise AssertionError("wrong per-bit flip on world %d"%h)
    return True


def exact_orbit_masks(n:int,*,max_bits:int=12):
    """Project explicit masks onto the BM-24 repeated-path histograms."""
    net=gain_family(n,2,q=8)
    if 2*n+2>max_bits:
        raise ValueError("exact orbit projection fixture limited to small n")
    masses=[]
    for h in (0,1):
        law=explicit_mask_law(n,h)
        histogram={}
        for mask,weight in law.items():
            signature=net.signature(mask)
            histogram[signature]=histogram.get(signature,Fraction(0))+weight
        masses.append(histogram)
    return tuple(masses)


def sample_mask(n:int,h:int,rng):
    """O(n) exact sampler, valid even for thousands of ordinary paths."""
    _check_world(h)
    if n<1:
        raise ValueError("at least one ordinary path required")
    ticket=rng.randrange(13)
    chosen=None
    for ordinary,special,weight in COMPONENTS[h]:
        ticket-=weight
        if ticket<0:
            chosen=(ordinary,special)
            break
    if chosen is None:
        raise AssertionError("mixture ticket failed")
    result=0
    ordinary,special=chosen
    for j in range(n):
        r=rng.randrange(8)
        if ordinary=="A":
            pair=3 if r==0 else 0
        elif ordinary=="B":
            pair=1 if r==0 else 2 if r==1 else 0
        else:
            pair=0
        result|=pair<<(2*j)
    if special=="E":
        r=rng.randrange(4)
        pair=1 if r==0 else 2 if r==1 else 0
    elif special=="A":
        pair=3 if rng.randrange(8)==0 else 0
    elif special=="B":
        r=rng.randrange(8)
        pair=1 if r==0 else 2 if r==1 else 0
    else:
        pair=0
    return result | (pair<<(2*n))


def theorem_receipt(n:int=250):
    eta=theorem_upper(n)
    return {
        "alphabet":8,"ordinary_paths":n,
        "total_paths":n+1,"reported_bits":2*n+2,
        "exact_upper_cap":str(eta),
        "prior_common_upper":"1/8",
        "improvement_absolute":str(Fraction(1,8)-eta),
        "improvement_relative":str(1-eta/Fraction(1,8)),
        "n_ge3_exact_lower":str(N3_LOWER) if n>=3 else None,
        "full_mask_states_per_world":1<<(2*n+2),
        "flat_branches":len(COMPONENTS[0]),
        "frustrated_branches":len(COMPONENTS[1]),
        "formal_tensor_power_components":len(formal_output_components(0)),
        "no_full_mask_table_materialized":True,
        "asymptotic_limit_claimed":False,
    }
