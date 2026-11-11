"""BM-19 exact finite residual-support primal/dual certificate fixtures.

Each declared distribution is an integer mask table; every dual inequality
is checked from scratch by support_aware_completion_BM19. These examples
were found with a finite LP and rational reconstruction. No numerical
optimizer is used in the submitted verification suite.

K4 d4 is a particularly short analytic theorem:
  D={47,61,63}; both 47 and 61 contain five edges.
  Any R with E chi_47=0 obeys P(odd intersection 47)=1/2, so
  5 max_i P(R_i=1) >=1/2, giving r>=1/10.
  The 8-mask exact witness reaches 1/10 while nulling all three D.
"""
from __future__ import annotations

from fractions import Fraction

try:
    from .generic_fourier_erasure_BM17 import Pair,Primal
    from .k4_high_degree_BM17 import k4_pair,DEGREE_PRIMALS
    from .finite_seed import Game
    from .diamond_weighted_fourier_BM10 import EDGES as DE,SHIFT as DS
    from .theta_shared_cycle_erasure import THETA_EDGES as TE,THETA_SHIFTS as TS
    from .sparse_fourier_degree_BM13 import primal_for_fourier_degree
    from .support_aware_completion_BM19 import (
        PostprocessorPrimal,PostprocessorDual,
        remaining_fourier_support,certify_support_optimum,
        postprocess_partial_pair,
    )
except ImportError:
    from generic_fourier_erasure_BM17 import Pair,Primal
    from k4_high_degree_BM17 import k4_pair,DEGREE_PRIMALS
    from finite_seed import Game
    from diamond_weighted_fourier_BM10 import EDGES as DE,SHIFT as DS
    from theta_shared_cycle_erasure import THETA_EDGES as TE,THETA_SHIFTS as TS
    from sparse_fourier_degree_BM13 import primal_for_fourier_degree
    from support_aware_completion_BM19 import (
        PostprocessorPrimal,PostprocessorDual,
        remaining_fourier_support,certify_support_optimum,
        postprocess_partial_pair,
    )


def _f(n:int,d:int)->Fraction:
    return Fraction(n,d)


def _same_pair(edges,shifts,vertices):
    return Pair(
        Game(vertices,2,tuple((u,v,0) for u,v in edges)),
        Game(vertices,2,tuple((u,v,g) for (u,v),g in zip(edges,shifts)))
    )


# Dictionary keys are (instance, partial Fourier degree).
# (expected residual indices, optimal extra flip, attaining primal, exact dual).
FIXTURES={
    ("k4",3):(
        (15,23,27,29,30,39,43,46,47,51,53,54,57,58,60,61,63),
        _f(7,38),
        PostprocessorPrimal(76,{
            0:15,1:6,2:7,3:1,4:6,5:2,6:1,8:6,9:2,10:1,
            12:2,16:7,17:1,18:3,20:1,24:1,32:6,33:2,
            34:1,36:2,40:2,48:1,
        }),
        PostprocessorDual(
            _f(7,38),
            {23:_f(-1,38),27:_f(-1,38),29:_f(-1,38),30:_f(-1,38),
             47:_f(-3,38),51:_f(-1,38),53:_f(-1,38),54:_f(-1,38),
             57:_f(-1,38),58:_f(-1,38),60:_f(-1,38),63:_f(6,38)},
            (_f(-3,19),_f(-3,19),_f(-3,19),
             _f(-3,19),_f(-4,19),_f(-3,19)),
        )
    ),
    ("k4",4):(
        (47,61,63),
        _f(1,10),
        PostprocessorPrimal(20,{
            0:9,1:2,2:1,4:2,8:2,16:1,18:1,32:2,
        }),
        PostprocessorDual(
            _f(1,10),{61:_f(-1,10)},
            (_f(-1,5),Fraction(0),_f(-1,5),
             _f(-1,5),_f(-1,5),_f(-1,5)),
        )
    ),
    ("k4",5):(
        (63,),
        _f(1,12),
        PostprocessorPrimal(12,{0:6,1:1,2:1,4:1,8:1,16:1,32:1}),
        PostprocessorDual(_f(1,12),{63:_f(-1,12)},(_f(-1,6),)*6),
    ),
    ("diamond",3):(
        (15,23,27,29,30,31),
        _f(1,5),
        PostprocessorPrimal(20,{
            0:5,1:2,2:2,4:2,5:1,8:2,10:2,16:2,17:1,20:1,
        }),
        PostprocessorDual(
            _f(1,5),
            {15:_f(-1,10),23:_f(-1,10),27:_f(-1,10),
             29:_f(-1,10),30:_f(-1,10),31:_f(3,10)},
            (_f(-1,5),)*5,
        )
    ),
    ("theta",4):(
        (31,47,55,59,61,62,63),
        _f(1,6),
        PostprocessorPrimal(12,{
            0:4,1:1,2:1,4:1,8:1,16:1,23:1,32:1,40:1,
        }),
        PostprocessorDual(
            _f(1,6),
            {31:_f(-1,12),47:_f(-1,12),55:_f(-1,12),
             59:_f(-1,12),61:_f(-1,12),62:_f(-1,12),
             63:_f(1,3)},
            (_f(-1,6),)*6,
        ),
    ),
}


def frozen_partial(instance:str,degree:int)->tuple[Pair,Primal]:
    if instance=="k4":
        pair=k4_pair()
        if degree not in DEGREE_PRIMALS:
            raise ValueError("unsupported K4 partial degree")
        return pair,DEGREE_PRIMALS[degree]
    if instance=="diamond":
        pair=_same_pair(DE,DS,4)
    elif instance=="theta":
        pair=_same_pair(TE,TS,5)
    else:
        raise ValueError("unknown graph fixture")
    masses,D=primal_for_fourier_degree(instance,degree)
    marginal=max(
        Fraction(sum(w for mask,w in masses.items() if mask&(1<<i)),D)
        for i in range(pair.m)
    )
    return pair,Primal(D,masses,masses,marginal)


def fixture_receipt(instance:str,degree:int):
    key=(instance,degree)
    if key not in FIXTURES:
        raise ValueError("unregistered graph/partial-degree fixture")
    expected,optimum,upper,lower=FIXTURES[key]
    pair,partial=frozen_partial(instance,degree)
    actual=remaining_fourier_support(pair,degree,partial)
    if actual!=expected:
        raise AssertionError("frozen Fourier discrepancy set changed")
    if certify_support_optimum(pair.m,actual,upper,lower)!=optimum:
        raise AssertionError("support-aware primal/dual bound mismatch")
    receipt=postprocess_partial_pair(pair,degree,partial,upper,lower)
    if receipt.optimal_extra_flip!=optimum:
        raise AssertionError("wrong attained rate")
    return receipt


def certificate_manifest():
    return {
        f"{instance}-d{degree}":{
            "residual_support_count":len(support),
            "optimal_postprocessing_rate":str(optimum),
            "mask_atoms":len(primal.weights),
            "nonzero_dual_characters":len(dual.characters),
            "completed_max_marginal":str(
                fixture_receipt(instance,degree).completed_max_flip
            ),
        } for (instance,degree),(support,optimum,primal,dual)
        in FIXTURES.items()
    }
