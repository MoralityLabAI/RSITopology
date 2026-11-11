"""BM-14: exact path-orbit LP and Krawtchouk dual compression.

Fix k internally vertex-disjoint u-v paths with lengths (L1,...,Lk),
F2^s edge gains, and two hidden gain assignments h=0,1. In every episode
fresh uniform vertex labels generate the *entire* Boolean satisfaction
vector. Nature may choose a different current-sample-independent XOR
error-mask distribution under each hypothesis, with uniform per-bit
marginal <= eta.

The clean laws are invariant under the product of permutation groups
S_L1 x ... x S_Lk. Averaging each feasible mask over this group preserves
both erasure and the common marginal cap. Consequently the full LP has an
EXACT orbit reduction from 2^m mask atoms to M=product_i(Li+1) mass classes
per hypothesis, with M-1 Fourier equalities and 2k marginal constraints.
For fixed k, all rational model data have polynomial bit complexity in
m=sum Li and log q; generic rational LP is polynomial time in this size.
The dependence O(m^k) is XP as k varies, NOT an FPT bound in k.

Dual solutions can likewise be represented by M Walsh *orbit signatures*,
using products of binary Krawtchouk polynomials. A single compressed orbit
multiplier represents an average of potentially many individual Walsh
coefficients and does not establish sparsity in the original Fourier basis.

Pure standard library, exact fractions. Tests compare against independent
vertex enumeration and existing BM-09/BM-10/BM-13 full-mask witnesses.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb, prod

try:
    from .theta_fourier_transfer_BM12 import theta_walsh_transfer, theta_path_game
except ImportError:
    from theta_fourier_transfer_BM12 import theta_walsh_transfer, theta_path_game


def _C(n:int,k:int)->int:
    return comb(n,k) if 0<=k<=n else 0


@lru_cache(maxsize=None)
def orbit_signatures(lengths:tuple[int,...])->tuple[tuple[int,...],...]:
    if len(lengths)<2 or any(not isinstance(v,int) or v<1 for v in lengths):
        raise ValueError("at least two positive path lengths required")
    return tuple(product(*(range(n+1) for n in lengths)))


def mask_signature(lengths:tuple[int,...],mask:int)->tuple[int,...]:
    if not 0<=mask<(1<<sum(lengths)):
        raise ValueError("mask index outside path network")
    out=[]
    offset=0
    for n in lengths:
        out.append(((mask>>offset)&((1<<n)-1)).bit_count())
        offset+=n
    return tuple(out)


def canonical_subset(lengths:tuple[int,...],signature:tuple[int,...])->int:
    if len(signature)!=len(lengths) or any(not 0<=s<=n
                                            for s,n in zip(signature,lengths)):
        raise ValueError("invalid Walsh signature")
    offset=0;mask=0
    for n,s in zip(lengths,signature):
        mask|=((1<<s)-1)<<offset
        offset+=n
    return mask


@lru_cache(maxsize=None)
def walsh_kernel_one(n:int,s:int,t:int)->Fraction:
    """E[chi_S(M)] for fixed |S|=s and uniform mask with |M|=t.

    Sum_{j} (-1)^j C(s,j) C(n-s,t-j) / C(n,t).
    This is binary Krawtchouk orbit averaging; the roles s/t may be
    swapped only with their appropriate binomial normalizers.
    """
    if n<1 or not 0<=s<=n or not 0<=t<=n:
        raise ValueError("invalid Hamming orbital indices")
    return Fraction(sum(
        (-1)**j*_C(s,j)*_C(n-s,t-j)
        for j in range(max(0,t-(n-s)),min(s,t)+1)
    ),comb(n,t))


@lru_cache(maxsize=None)
def walsh_kernel(
    lengths:tuple[int,...],s:tuple[int,...],t:tuple[int,...]
)->Fraction:
    if len(s)!=len(lengths) or len(t)!=len(lengths):
        raise ValueError("orbit dimension mismatch")
    return prod((walsh_kernel_one(n,a,b)
                 for n,a,b in zip(lengths,s,t)),start=Fraction(1))


@lru_cache(maxsize=None)
def orbit_clean_walsh(q:int,lengths:tuple[int,...],
                      gains:tuple[int,...],s:tuple[int,...])->Fraction:
    return theta_walsh_transfer(q,lengths,gains,canonical_subset(lengths,s))


@dataclass(frozen=True)
class OrbitModel:
    q:int
    lengths:tuple[int,...]
    gains0:tuple[int,...]
    gains1:tuple[int,...]

    def __post_init__(self):
        theta_path_game(self.q,self.lengths,self.gains0)
        theta_path_game(self.q,self.lengths,self.gains1)

    @property
    def classes(self)->tuple[tuple[int,...],...]:
        return orbit_signatures(self.lengths)

    @property
    def dimension(self)->int:
        return prod((n+1 for n in self.lengths))

    @property
    def edge_count(self)->int:
        return sum(self.lengths)

    def clean_walsh(self,h:int,s:tuple[int,...])->Fraction:
        if h not in (0,1):
            raise ValueError("hypothesis must be 0 or 1")
        return orbit_clean_walsh(
            self.q,self.lengths,self.gains0 if h==0 else self.gains1,s
        )


def mask_mass_orbits(
    lengths:tuple[int,...],weights:dict[int,int],denominator:int
)->dict[tuple[int,...],Fraction]:
    """Push arbitrary full-mask weights to the permutation-orbit quotient."""
    orbit_signatures(lengths)
    if denominator<1 or any(
        not 0<=m<(1<<sum(lengths)) or w<0 for m,w in weights.items()
    ) or sum(weights.values())!=denominator:
        raise ValueError("invalid full-mask probability law")
    masses:dict[tuple[int,...],Fraction]={}
    for mask,w in weights.items():
        key=mask_signature(lengths,mask)
        masses[key]=masses.get(key,Fraction(0))+Fraction(w,denominator)
    return {s:v for s,v in masses.items() if v}


def expand_orbit_masses(
    lengths:tuple[int,...],masses:dict[tuple[int,...],Fraction]
)->dict[int,Fraction]:
    """Uniformly distribute each orbit mass among its C(Li,ti) mask atoms."""
    cls=orbit_signatures(lengths)
    if any(k not in cls or v<0 for k,v in masses.items()) or sum(masses.values())!=1:
        raise ValueError("normalized nonnegative orbit distribution required")
    return {
        mask:masses.get(mask_signature(lengths,mask),Fraction(0))/
        prod(comb(n,t) for n,t in zip(lengths,mask_signature(lengths,mask)))
        for mask in range(1<<sum(lengths))
    }


def mask_orbit_walsh(
    model:OrbitModel,s:tuple[int,...],masses:dict[tuple[int,...],Fraction]
)->Fraction:
    return sum((weight*walsh_kernel(model.lengths,s,t)
                for t,weight in masses.items()),Fraction(0))


def orbit_marginals(
    model:OrbitModel,masses:dict[tuple[int,...],Fraction]
)->tuple[Fraction,...]:
    return tuple(
        sum((v*Fraction(t[i],model.lengths[i]) for t,v in masses.items()),
            Fraction(0))
        for i in range(len(model.lengths))
    )


def verify_orbit_primal(
    model:OrbitModel,flat:dict[tuple[int,...],Fraction],
    frustrated:dict[tuple[int,...],Fraction],
    *,cap:Fraction|None=None
)->Fraction:
    """Verify the exact full-output equality via all M Walsh orbit constraints."""
    cls=set(model.classes)
    for mass in (flat,frustrated):
        if any(k not in cls or v<0 for k,v in mass.items()) or sum(mass.values())!=1:
            raise ValueError("invalid probability distribution over path orbits")
    for s in model.classes:
        lhs=model.clean_walsh(0,s)*mask_orbit_walsh(model,s,flat)
        rhs=model.clean_walsh(1,s)*mask_orbit_walsh(model,s,frustrated)
        if lhs!=rhs:
            raise AssertionError("masked Walsh mismatch at orbit "+str(s))
    eta=max(orbit_marginals(model,flat)+orbit_marginals(model,frustrated))
    if cap is not None and eta>Fraction(cap):
        raise AssertionError("readout mask exceeds registered cap")
    return eta


def aggregate_dual_to_orbits(
    lengths:tuple[int,...],
    norm:tuple[Fraction,Fraction],
    walsh_by_subset:dict[int,Fraction],
    marginal_by_edge:tuple[dict[int,Fraction],dict[int,Fraction]],
):
    """Project any full Fourier dual into an orbit-invariant certificate.

    Fourier coefficients within an orbit are summed into one multiplier.
    All per-edge marginal multipliers within a path are similarly summed.
    Averaging the full dual under path permutations preserves the objective
    and makes the dual slack constant on each mask orbit.
    """
    cls=set(orbit_signatures(lengths))
    m=sum(lengths)
    coeff:dict[tuple[int,...],Fraction]={}
    for subset,weight in walsh_by_subset.items():
        if not 0<subset<(1<<m):
            raise ValueError("dual Walsh index outside graph or empty")
        s=mask_signature(lengths,subset)
        coeff[s]=coeff.get(s,Fraction(0))+Fraction(weight)
    z=[]
    for side in marginal_by_edge:
        if any(not 0<=e<m for e in side):
            raise ValueError("marginal dual index outside graph")
        row=[];offset=0
        for n in lengths:
            row.append(sum((Fraction(side.get(i,0))
                            for i in range(offset,offset+n)),Fraction(0)))
            offset+=n
        z.append(tuple(row))
    return tuple(Fraction(v) for v in norm), {
        s:v for s,v in coeff.items() if v and s in cls
    },tuple(z)


def verify_orbit_dual(
    model:OrbitModel,norm:tuple[Fraction,Fraction],
    walsh_by_orbit:dict[tuple[int,...],Fraction],
    marginal_by_path:tuple[tuple[Fraction,...],tuple[Fraction,...]],
)->Fraction:
    """Exact weak LP dual verifier over just 2*M orbit mask atoms.

    For each path-count mask t and hypothesis h, the slack is
      norm[h]+(-1)^h sum_s y[s] P_h_hat(s)*Phi_s(t)
             + sum_i z[h,i] t_i/L_i.
    Nonpositive slacks, z<=0, and -sum z=1 certify the lower bound
    norm[0]+norm[1] on the *full* uncompressed erasure LP.
    """
    if len(norm)!=2 or len(marginal_by_path)!=2 or any(
        len(row)!=len(model.lengths) for row in marginal_by_path
    ):
        raise ValueError("dual dimensions inconsistent with graph")
    if any(s not in model.classes or s==(0,)*len(model.lengths)
           for s in walsh_by_orbit):
        raise ValueError("nonempty valid Walsh orbit keys required")
    if any(v>0 for row in marginal_by_path for v in row):
        raise ValueError("marginal multipliers must be nonpositive")
    if -sum((v for row in marginal_by_path for v in row),Fraction(0))!=1:
        raise ValueError("dual eta coefficient must equal one")
    for h in (0,1):
        for t in model.classes:
            slack=Fraction(norm[h])
            for s,value in walsh_by_orbit.items():
                slack+=((1 if h==0 else -1)*value*model.clean_walsh(h,s)
                        *walsh_kernel(model.lengths,s,t))
            slack+=sum((v*Fraction(t[i],model.lengths[i])
                        for i,v in enumerate(marginal_by_path[h])),
                       Fraction(0))
            if slack>0:
                raise AssertionError(f"dual slack >0 at world={h} orbit={t}")
    return sum((Fraction(v) for v in norm),Fraction(0))


def clean_orbit_probability(
    model:OrbitModel,h:int,success_counts:tuple[int,...]
)->Fraction:
    """Independent residual-character count formula for full path count law.

    For path i and k_i failed edges, per-pattern residual counts:
      N0(k)=((q-1)^k+(q-1)(-1)^k)/q if endpoint d==gain_i,
      N1(k)=((q-1)^k-(-1)^k)/q otherwise.
    Average over the q possible shared endpoint differences d, grouping
    equal gains. Multiply by C(L_i,k_i) patterns in the count orbit.
    """
    if h not in (0,1) or len(success_counts)!=len(model.lengths) or any(
        not 0<=r<=n for r,n in zip(success_counts,model.lengths)
    ):
        raise ValueError("invalid hypothesis or path counts")
    q=model.q
    gains=model.gains0 if h==0 else model.gains1
    failures=tuple(n-r for n,r in zip(model.lengths,success_counts))
    def count(failed:int,flat:bool)->int:
        value=(q-1)**failed+((q-1) if flat else -1)*((-1)**failed)
        if value%q:
            raise AssertionError("invalid finite character count")
        return value//q
    distinct=set(gains)
    total=(q-len(distinct))*prod(count(x,False) for x in failures)
    for g in distinct:
        total+=prod(count(x,gi==g) for x,gi in zip(failures,gains))
    multiplicity=prod(comb(n,r) for n,r in zip(model.lengths,success_counts))
    denominator=q**(1+sum(n-1 for n in model.lengths))
    return Fraction(total*multiplicity,denominator)


def clean_orbit_law(model:OrbitModel,h:int)->dict[tuple[int,...],Fraction]:
    law={s:clean_orbit_probability(model,h,s) for s in model.classes}
    if sum(law.values())!=1 or any(v<0 for v in law.values()):
        raise AssertionError("invalid independent clean count distribution")
    return law


@lru_cache(maxsize=None)
def count_transition_one(
    n:int,input_success:int,mask_weight:int,output_success:int
)->Fraction:
    """Hypergeometric count transition under uniform mask of given weight."""
    if n<1 or any(not 0<=r<=n for r in
                 (input_success,mask_weight,output_success)):
        raise ValueError("invalid count transition")
    value=0
    for intersection in range(
        max(0,mask_weight-(n-input_success)),
        min(mask_weight,input_success)+1,
    ):
        if input_success+mask_weight-2*intersection==output_success:
            value+=comb(input_success,intersection)*comb(
                n-input_success,mask_weight-intersection
            )
    return Fraction(value,comb(n,mask_weight))


def masked_count_law(
    model:OrbitModel,h:int,masses:dict[tuple[int,...],Fraction]
)->dict[tuple[int,...],Fraction]:
    """Independent count-channel convolution, separate from Walsh theorem."""
    clean=clean_orbit_law(model,h)
    out={}
    for target in model.classes:
        total=Fraction(0)
        for initial,prob in clean.items():
            if not prob:
                continue
            for mask,weight in masses.items():
                transition=prod((
                    count_transition_one(n,s,t,r)
                    for n,s,t,r in zip(model.lengths,initial,mask,target)
                ),start=Fraction(1))
                total+=prob*weight*transition
        out[target]=total
    if sum(out.values())!=1 or any(v<0 for v in out.values()):
        raise AssertionError("invalid independent count channel")
    return out



@dataclass(frozen=True)
class OrbitLP:
    """An exact rational standard-form erasure LP on mask weight orbits.

    Variables are ordered Q0[t] for t in classes, Q1[t] for t in classes,
    followed by eta. Equalities: all nonempty Walsh signatures plus the
    two law normalizations. Inequalities: 2k path-marginal caps.
    """
    signatures:tuple[tuple[int,...],...]
    equality_rows:tuple[tuple[Fraction,...],...]
    equality_rhs:tuple[Fraction,...]
    inequality_rows:tuple[tuple[Fraction,...],...]
    inequality_rhs:tuple[Fraction,...]
    objective:tuple[Fraction,...]


def build_orbit_lp(model:OrbitModel,*,max_classes:int=100)->OrbitLP:
    """Materialize an exact LP with 2M+1 variables and M+1 equalities.

    Ordinary LP solvers can optimize the rational system; verification
    remains independent with verify_orbit_primal / verify_orbit_dual.
    max_classes bounds eager Fraction memory consumption; for larger
    graphs use lazy Walsh rows and separation oracles.
    """
    cls=model.classes
    M=len(cls);k=len(model.lengths)
    if M>max_classes or max_classes<1:
        raise ValueError("orbit LP exceeds registered eager class limit")
    eq=[];rhs=[]
    for s in cls:
        if s==(0,)*k:
            continue
        p0,p1=model.clean_walsh(0,s),model.clean_walsh(1,s)
        eq.append(tuple(p0*walsh_kernel(model.lengths,s,t) for t in cls)
                  +tuple(-p1*walsh_kernel(model.lengths,s,t) for t in cls)
                  +(Fraction(0),))
        rhs.append(Fraction(0))
    eq.append(tuple(Fraction(1) for _ in cls)+
              tuple(Fraction(0) for _ in cls)+(Fraction(0),))
    rhs.append(Fraction(1))
    eq.append(tuple(Fraction(0) for _ in cls)+
              tuple(Fraction(1) for _ in cls)+(Fraction(0),))
    rhs.append(Fraction(1))
    ineq=[];zero=[]
    for h in (0,1):
        for i,n in enumerate(model.lengths):
            row=tuple(Fraction(t[i],n) if hh==h else Fraction(0)
                      for hh in (0,1) for t in cls)+(Fraction(-1),)
            ineq.append(row)
            zero.append(Fraction(0))
    objective=tuple(Fraction(0) for _ in range(2*M))+(Fraction(1),)
    return OrbitLP(cls,tuple(eq),tuple(rhs),tuple(ineq),tuple(zero),
                   objective)


def check_orbit_lp_primal(
    lp:OrbitLP,flat:dict[tuple[int,...],Fraction],
    frustrated:dict[tuple[int,...],Fraction],eta:Fraction,
)->bool:
    """Independent exact matrix evaluation of an orbit primal point."""
    x=tuple(Fraction(flat.get(t,0)) for t in lp.signatures)+tuple(
        Fraction(frustrated.get(t,0)) for t in lp.signatures
    )+(Fraction(eta),)
    if any(v<0 for v in x):
        return False
    return (all(sum((a*b for a,b in zip(row,x)),Fraction(0))==rhs
                for row,rhs in zip(lp.equality_rows,lp.equality_rhs))
            and all(sum((a*b for a,b in zip(row,x)),Fraction(0))<=rhs
                    for row,rhs in zip(lp.inequality_rows,lp.inequality_rhs)))


def orbit_manifest(model:OrbitModel)->dict[str,int|tuple[int,...]]:
    """Expose compression sizes and full-vs-orbit verification counts."""
    M=model.dimension
    m=model.edge_count
    return {
        "path_lengths":model.lengths,
        "number_of_paths":len(model.lengths),
        "number_of_edges":m,
        "full_mask_states_per_world":1<<m,
        "orbit_mask_states_per_world":M,
        "full_walsh_signatures":1<<m,
        "orbit_walsh_signatures":M,
        "orbit_lp_variables":2*M+1,
        "orbit_lp_equalities":M+1,
        "orbit_lp_marginal_inequalities":2*len(model.lengths),
    }
