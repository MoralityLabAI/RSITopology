"""BM-22: implicit Fourier supports and a sharp erasure theorem on theta blocks.

A theta network has k >=2 internally vertex-disjoint paths between two
terminals, lengths L_i, and path gains g_{h,i} in K=F2^s under two
hypotheses h=0,1. Every observation uses fresh uniform vertex labels.
For any Fourier subset S, let J(S) denote the paths ALL of whose edges
are selected, and b(S) the number of selected edges in the other paths.
Set alpha=1-2/q. Then EXACTLY

    W_h(S) = alpha**b(S) * A_h(J(S)),

where A_h(J) is a conditional terminal-difference average over the
fully selected paths and can be evaluated in O(k^2) gain-grouped
rational operations without enumerating q labelings. Consequently

    Delta(S) = alpha**b(S) * [A_0(J)-A_1(J)].

For q>2, its entire clean discrepancy support is represented by at most
2^k Boolean states J, with exact count

    |D| = sum_{J: A_0(J)!=A_1(J)}
                    prod_{i notin J} (2**L_i - 1).

For q=2, only proper paths with ZERO selected edges contribute,
and their factor is 1. Arbitrary explicit hypothesis-dependent XOR
mask laws allow exact residual MEMBERSHIP queries without 2^m support
enumeration; symmetric orbit mask laws additionally permit polynomial
support counting for fixed k through BM-14's path-count orbits.

Special theorem: q=4, k=3, path gains 0,1,2 (all distinct). Any two
fully selected paths produce nonzero clean discrepancy. The full
three-path character differs except when exactly ONE length is even
and the other TWO are odd, where it cancels exactly. Thus

    |D| = sum_i (2**L_i-1) + 1[not exactly one even path].

For ALL THREE PATH LENGTHS EVEN, the complete state-aware correlated-
mask erasure cap is SHARP:

    eta* = max(1/sum_i L_i,
               1/(2*min_{i<j}(L_i+L_j))).

The lower bounds come from (a) exact full and complement-of-one-edge
Walsh zeros under the frustrated world, forcing E_Qflat |M|>=1,
and (b) BM-08's isolated cycle projection. A COMMON exact mask
attains the max: choose a three-path activation vector T with
distribution P(T=t)=[1+sum_i (1-2p_i)*(-1)^t_i]/8, where
p_i=min(eta*L_i,1/2) and sum p_i=1. For each active path flip one
uniformly chosen edge. All degree>=2 Walsh characters of T vanish,
which erases every Fourier support with >=2 fully selected paths,
even when the remaining path is partially observed.

The restricted complete erasure theorem is a finite symmetrization
result, not a general solution for interacting-cycle graph families.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb, prod, lcm


def _check(q:int,lengths:tuple[int,...],
           gains0:tuple[int,...],gains1:tuple[int,...])->None:
    if (not isinstance(q,int) or q<2 or q&(q-1) or
        len(lengths)<2 or len(gains0)!=len(lengths) or
        len(gains1)!=len(lengths) or
        any(not isinstance(L,int) or L<1 for L in lengths) or
        any(not isinstance(g,int) or not 0<=g<q
            for g in gains0+gains1)):
        raise ValueError("need q=2^s, >=2 positive paths and valid gains")


@lru_cache(maxsize=None)
def _full_path_average(q:int,lengths:tuple[int,...],
                       gains:tuple[int,...],J:int)->Fraction:
    """Exact terminal-averaged product over completely selected paths.

    Group the q endpoint differences by the at most |J| gain values.
    The computation uses NO loop over q or q^V and accepts huge alphabets.
    """
    if not 0<=J<(1<<len(lengths)):
        raise ValueError("invalid path-activation subset")
    alpha=Fraction(q-2,q)
    selected=[i for i in range(len(lengths)) if J&(1<<i)]
    if not selected:
        return Fraction(1)
    factors={}
    for i in selected:
        L=lengths[i]
        A=alpha**L-Fraction(-2,q)**L
        B=Fraction((-2)**L,q**(L-1))
        factors[i]=(A,B)
    base=prod((factors[i][0] for i in selected),start=Fraction(1))
    distinct=set(gains[i] for i in selected)
    total=(q-len(distinct))*base
    for gain in distinct:
        total+=prod((
            factors[i][0]+(factors[i][1] if gains[i]==gain else 0)
            for i in selected
        ),start=Fraction(1))
    return total/q


@dataclass(frozen=True)
class ThetaSupportCircuit:
    q:int
    lengths:tuple[int,...]
    gains0:tuple[int,...]
    gains1:tuple[int,...]

    def __post_init__(self):
        _check(self.q,self.lengths,self.gains0,self.gains1)

    @property
    def path_count(self)->int:
        return len(self.lengths)

    @property
    def edge_count(self)->int:
        return sum(self.lengths)

    @property
    def alpha(self)->Fraction:
        return Fraction(self.q-2,self.q)

    @property
    def path_masks(self)->tuple[int,...]:
        masks=[]
        offset=0
        for L in self.lengths:
            masks.append(((1<<L)-1)<<offset)
            offset+=L
        return tuple(masks)

    def signature(self,S:int)->tuple[int,...]:
        if not isinstance(S,int) or not 0<=S<(1<<self.edge_count):
            raise ValueError("Fourier mask outside theta edge space")
        return tuple((S&mask).bit_count() for mask in self.path_masks)

    def fully_selected(self,S:int)->tuple[int,int]:
        """Return path-mask J and number of selected proper-path edges."""
        sizes=self.signature(S)
        J=sum(1<<i for i,(L,s) in enumerate(zip(self.lengths,sizes))
              if s==L)
        b=sum(s for L,s in zip(self.lengths,sizes) if s<L)
        return J,b

    def full_delta(self,J:int)->Fraction:
        if not isinstance(J,int) or not 0<=J<1<<self.path_count:
            raise ValueError("invalid full path-selection mask")
        return (_full_path_average(self.q,self.lengths,self.gains0,J)-
                _full_path_average(self.q,self.lengths,self.gains1,J))

    def clean_walsh(self,S:int,h:int)->Fraction:
        if h not in (0,1):
            raise ValueError("hypothesis must be 0 or 1")
        J,b=self.fully_selected(S)
        return self.alpha**b*_full_path_average(
            self.q,self.lengths,self.gains0 if h==0 else self.gains1,J
        )

    def discrepancy(self,S:int)->Fraction:
        J,b=self.fully_selected(S)
        return self.alpha**b*self.full_delta(J)

    def contains_discrepancy(self,S:int)->bool:
        return bool(self.discrepancy(S))

    def support_count(self)->int:
        """Count clean residual indices via 2^k path choices."""
        m=self.edge_count
        result=0
        for J in range(1<<self.path_count):
            if not self.full_delta(J):
                continue
            choices=prod((
                1 if self.q==2 else (1<<L)-1
                for i,L in enumerate(self.lengths) if not J&(1<<i)
            ),start=1)
            result+=choices
        if not 0<=result<=1<<m:
            raise AssertionError("invalid clean support cardinality")
        return result

    def support_path_types(self)->tuple[int,...]:
        """Only the fully selected path classes with nonzero discrepancy."""
        return tuple(J for J in range(1<<self.path_count)
                     if self.full_delta(J))

    def masked_discrepancy(
        self,S:int,q0:dict[int,int],q1:dict[int,int],denominator:int
    )->Fraction:
        """Exact frozen mask-pair residual membership without full expansion."""
        self.signature(S)
        if not isinstance(denominator,int) or denominator<=0 or any(
            sum(mask.values())!=denominator or any(
                not isinstance(x,int) or not 0<=x<(1<<self.edge_count)
                or not isinstance(w,int) or w<0
                for x,w in mask.items())
            for mask in (q0,q1)
        ):
            raise ValueError("normalized integer correlated mask laws needed")
        def hat(weights):
            return Fraction(sum(
                (-w if (x&S).bit_count()%2 else w)
                for x,w in weights.items()
            ),denominator)
        return self.clean_walsh(S,0)*hat(q0)-self.clean_walsh(S,1)*hat(q1)

    def symmetric_masked_support_count(
        self,q0:dict[tuple[int,...],Fraction],
        q1:dict[tuple[int,...],Fraction],*,max_orbits:int=100000
    )->int:
        """Exact support count for BM-14 path-exchangeable mask channels.

        Pathwise symmetric masks have Fourier transforms depending only
        on signature s=(|S intersect path_i|). Every signature represents
        prod_i binom(L_i,s_i) actual Walsh supports.
        """
        from theta_orbit_lp_BM14 import (
            OrbitModel,mask_orbit_walsh
        )
        M=prod((L+1 for L in self.lengths),start=1)
        if M>max_orbits:
            raise ValueError("exceeds registered orbit-enumeration resource cap")
        model=OrbitModel(self.q,self.lengths,self.gains0,self.gains1)
        classes=set(model.classes)
        for mask in (q0,q1):
            if any(k not in classes or v<0 for k,v in mask.items()) or sum(
                mask.values(),Fraction(0)
            )!=1:
                raise ValueError("normalized path-weight orbit masks needed")
        result=0
        for s in model.classes:
            S=0
            for L,r,mask in zip(self.lengths,s,self.path_masks):
                S|=(mask&-mask)*((1<<r)-1)
            diff=self.clean_walsh(S,0)*mask_orbit_walsh(model,s,q0)-(
                self.clean_walsh(S,1)*mask_orbit_walsh(model,s,q1))
            if diff:
                result+=prod((comb(L,r) for L,r in zip(self.lengths,s)),
                             start=1)
        return result

    def q4_distinct_three_path_support_count(self)->int:
        """Closed clean support cardinality for q4 and 3 distinct gains."""
        if (self.q!=4 or self.path_count!=3 or
            len(set(self.gains0))!=1 or
            len(set(self.gains1))!=3):
            raise ValueError("need three paths, q4, flat vs distinct gains")
        even=sum(L%2==0 for L in self.lengths)
        return sum((1<<L)-1 for L in self.lengths)+int(even!=1)

    def q4_even_erasure_cap(self)->Fraction:
        """Sharp correlated hypothesis-aware optimum for 3 even paths."""
        if (self.q!=4 or self.path_count!=3 or
            any(L%2 for L in self.lengths) or
            len(set(self.gains0))!=1 or
            len(set(self.gains1))!=3):
            raise ValueError("requires q4 three even paths and distinct gains")
        m=self.edge_count
        shortest_pair=m-max(self.lengths)
        return max(Fraction(1,m),Fraction(1,2*shortest_pair))

    def q4_even_lower_proof(self)->dict[str,object]:
        """Symbolically check flat-vs-frustrated full/complement Walsh zeros.

        Under q4 all-even paths, the conditional full-path factor is
        positive B_i 1[d=g_i]. Pairwise distinct frustrating gains force
        the FULL clean Walsh character to vanish and also every E\\{e}
        character (two full distinct-gain paths remain). The corresponding
        flat-world clean characters stay positive.

        Thus an erasing Q_flat must make full and all complements
        have zero Walsh moment. If K=# flipped bits and B=1[K odd],
        the count T of odd complements obeys
           T=K (even K), or m-K (odd K),
           T<=K+(m-2)B.
        E T=m/2 and E B=1/2 force E K>=1, giving eta>=1/m.
        Any frustrated two-path cycle also projects to the BM-08
        lower bound eta>=1/[2(Li+Lj)].
        """
        eta=self.q4_even_erasure_cap()
        full=(1<<self.edge_count)-1
        if not self.clean_walsh(full,0)>0 or self.clean_walsh(full,1)!=0:
            raise AssertionError("full Walsh zero premise failed")
        for i in range(self.edge_count):
            S=full^(1<<i)
            if not self.clean_walsh(S,0)>0 or self.clean_walsh(S,1)!=0:
                raise AssertionError("complement Walsh zero premise failed")
        m=self.edge_count
        for k in range(m+1):
            B=k%2
            T=k if not B else m-k
            if T>k+(m-2)*B:
                raise AssertionError("universal parity/Hamming inequality failed")
        from sharp_erasure_optimality import critical_erasure_cap
        pair_lower=max(critical_erasure_cap(4,
                          self.lengths[i]+self.lengths[j])
                       for i in range(3) for j in range(i+1,3))
        if eta!=max(Fraction(1,m),pair_lower):
            raise AssertionError("sharp lower formula disagrees with BM08")
        return {
            "edge_total":m,
            "full_character_zero_frustrated":True,
            "all_complement_characters_zero_frustrated":True,
            "parity_lower_bound":Fraction(1,m),
            "projected_cycle_lower_bound":pair_lower,
            "combined_lower_bound":eta,
        }

    def q4_even_activation_law(self)->dict[int,Fraction]:
        """Eight-state exact path activation law attaining the sharp cap.

        Let p_i=min(eta*L_i,1/2), sum p_i=1,
        a_i=1-2p_i>=0, sum a_i=1.
        Then P(T=t)=(1+sum_i a_i (-1)^t_i)/8 is nonnegative,
        has P(T_i=1)=p_i, and its Walsh moments of all orders >=2
        are exactly zero.
        """
        eta=self.q4_even_erasure_cap()
        p=tuple(min(eta*L,Fraction(1,2)) for L in self.lengths)
        if sum(p)!=1:
            raise AssertionError("required path activation capacities fail")
        a=tuple(1-2*x for x in p)
        if any(x<0 for x in a) or sum(a)!=1:
            raise AssertionError("activation coefficients violate simplex")
        law={}
        for T in range(8):
            weight=Fraction(1,8)*(1+sum(
                (a[i]*(-1 if T&(1<<i) else 1) for i in range(3)),
                Fraction(0)
            ))
            if weight<0:
                raise AssertionError("negative path activation weight")
            if weight:
                law[T]=weight
        if sum(law.values(),Fraction(0))!=1:
            raise AssertionError("activation probabilities not normalized")
        for i,x in enumerate(p):
            if sum((w for T,w in law.items() if T&(1<<i)),
                   Fraction(0))!=x:
                raise AssertionError("path activation marginal mismatch")
        return law

    def q4_even_noise_walsh_signature(
        self,s:tuple[int,...]
    )->Fraction:
        """Selected edge count Walsh for the factored common noise law."""
        self.q4_even_erasure_cap()
        if len(s)!=3 or any(not 0<=r<=L for r,L in zip(s,self.lengths)):
            raise ValueError("invalid path count signature")
        total=Fraction(0)
        for T,weight in self.q4_even_activation_law().items():
            local=prod((
                1-Fraction(2*s[i],self.lengths[i]) if T&(1<<i)
                else Fraction(1)
                for i in range(3)
            ),start=Fraction(1))
            total+=weight*local
        return total

    def q4_even_verify_upper_symbolic(self)->Fraction:
        """Verify ALL path-count signatures, using polynomial orbit work."""
        eta=self.q4_even_erasure_cap()
        for s in product(*(range(L+1) for L in self.lengths)):
            S=sum(((1<<r)-1)*(mask&-mask)
                  for r,mask in zip(s,self.path_masks))
            diff=self.discrepancy(S)*self.q4_even_noise_walsh_signature(s)
            if diff:
                raise AssertionError("common noise left a nonzero Fourier support")
        p=tuple(sum((weight for T,weight in
                     self.q4_even_activation_law().items()
                     if T&(1<<i)),Fraction(0))/L
                for i,L in enumerate(self.lengths))
        if max(p)!=eta:
            raise AssertionError("upper witness does not attain cap")
        return eta

    def q4_even_explicit_mask_law(
        self,*,max_states:int=20000
    )->dict[int,Fraction]:
        """Exact correlated common XOR mask, one edge per activated path."""
        self.q4_even_erasure_cap()
        states=prod((1+L for L in self.lengths),start=1)
        if states>max_states:
            raise ValueError("explicit mask law exceeds resource cap")
        positions=[tuple(i for i in range(self.edge_count)
                         if mask&(1<<i)) for mask in self.path_masks]
        out={}
        for T,w in self.q4_even_activation_law().items():
            choices=[
                positions[i] if T&(1<<i) else (None,)
                for i in range(3)
            ]
            divisor=prod((self.lengths[i] for i in range(3)
                          if T&(1<<i)),start=1)
            for selection in product(*choices):
                mask=sum((1<<i for i in selection if i is not None),0)
                out[mask]=out.get(mask,Fraction(0))+w/divisor
        if sum(out.values(),Fraction(0))!=1:
            raise AssertionError("mask law normalization failure")
        return {k:v for k,v in out.items() if v}

    def q4_even_sampler(self,rng)->int:
        """Compact exact sampler for arbitrarily long three-path theta."""
        law=self.q4_even_activation_law()
        den=lcm(*(w.denominator for w in law.values()))
        ticket=rng.randrange(den)
        chosen=None
        for T,w in law.items():
            ticket-=int(w*den)
            if ticket<0:
                chosen=T
                break
        if chosen is None:
            raise AssertionError("random ticket failed to choose activation")
        result=0
        offset=0
        for i,L in enumerate(self.lengths):
            if chosen&(1<<i):
                result|=1<<(offset+rng.randrange(L))
            offset+=L
        return result

    def q4_even_receipt(self)->dict[str,object]:
        lower=self.q4_even_lower_proof()
        upper=self.q4_even_verify_upper_symbolic()
        if lower["combined_lower_bound"]!=upper:
            raise AssertionError("sharp theorem primal and lower mismatch")
        return {
            "q":self.q,"paths":self.lengths,
            "gains_flat":self.gains0,
            "gains_frustrated":self.gains1,
            "edges":self.edge_count,
            "exact_hypothesis_aware_erasure":str(upper),
            "support_count":self.support_count(),
            "activation_support":len(self.q4_even_activation_law()),
            "clean_support_table_materialized":False,
            "hypothesis_aware_lower_bound_verified":True,
            "common_mask_upper_verified":True,
        }
