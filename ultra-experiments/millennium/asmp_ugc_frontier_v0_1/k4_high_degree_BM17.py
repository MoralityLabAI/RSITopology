"""BM-17: fully rational K4 high-degree erasure obstruction data.

Exact q=4, four-vertex complete graph, edges ordered
  (01,02,03,12,13,23).
Flat gains are all zero, frustrated gains (0,0,0,1,2,1).
All four triangles are frustrated. Exact degree-d LP optimum:
  d=0,1,2: 0; d=3:1/6; d=4:1/5; d=5:4/19; d=6:3/14.

The d=3..6 certificate data were DISCOVERED using finite numerical LP
and reconstructed in exact rational arithmetic. They are checked
independently from scratch using generic_fourier_erasure_BM17.
No floating-point solver or high-risk external computation is required
to verify any of the exact claims.

The degree-five primal DOES NOT erase the degree-six full observation,
giving a concrete 2-connected width-three counterexample to the idea
that degree-(m-1) Fourier constraints always suffice.
"""
from __future__ import annotations

from fractions import Fraction

try:
    from .finite_seed import Game
    from .generic_fourier_erasure_BM17 import Pair,Primal,Dual,certify
except ImportError:
    from finite_seed import Game
    from generic_fourier_erasure_BM17 import Pair,Primal,Dual,certify


EDGES=((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))
FLAT_GAINS=(0,0,0,0,0,0)
OTHER_GAINS=(0,0,0,1,2,1)


def k4_pair()->Pair:
    return Pair(
        Game(4,2,tuple((u,v,g) for (u,v),g in zip(EDGES,FLAT_GAINS))),
        Game(4,2,tuple((u,v,g) for (u,v),g in zip(EDGES,OTHER_GAINS))),
    )


def _primal(D:int,q0:dict[int,int],q1:dict[int,int],cap:Fraction):
    return Primal(D,q0,q1,cap)


# Each table is an integer numerator distribution normalized by the
# declared denominator. Different worlds may use different distributions.
DEGREE_PRIMALS={
    3:_primal(
        6,{0:2,2:1,12:1,16:1,33:1},
          {0:2,2:1,12:1,16:1,33:1},
        Fraction(1,6),
    ),
    4:_primal(
        20,
        {0:4,1:1,2:2,4:1,5:1,8:1,9:1,12:1,16:2,18:2,
         32:1,33:1,36:1,40:1},
        {0:4,1:1,2:2,4:1,5:1,8:1,9:1,12:1,16:2,18:2,
         32:1,33:1,36:1,40:1},
        Fraction(1,5),
    ),
    5:_primal(
        152,
        {0:32,1:10,2:13,3:1,4:10,5:4,6:1,8:10,9:4,
         10:1,12:6,14:1,16:13,17:1,18:8,20:1,23:1,
         24:1,27:1,28:1,32:10,33:6,34:1,35:1,36:4,
         40:4,47:1,48:1,49:1,54:1,58:1,61:1},
        {0:28,1:12,2:14,4:12,5:2,8:12,9:2,11:3,
         12:8,16:14,18:10,21:3,32:12,33:8,36:2,
         38:3,40:2,56:3,63:2},
        Fraction(4,19),
    ),
    6:_primal(
        56,
        {0:10,1:3,2:6,4:3,5:2,8:3,9:2,12:2,13:1,
         16:6,18:6,32:3,33:2,36:2,37:1,40:2,41:1,44:1},
        {0:10,1:3,2:6,4:3,5:2,8:3,9:2,12:2,13:1,
         16:6,18:6,32:3,33:2,36:2,37:1,40:2,41:1,44:1},
        Fraction(3,14),
    ),
}


DEGREE_DUALS={
    3:Dual(
        12,{11:4},(1,1),
        6,(-1,-1,0,-1,0,0,-1,-1,0,-1,0,0),
    ),
    4:Dual(
        20,
        {11:3,15:-2,18:2,21:4,22:2,23:-4,
         27:-2,28:4,30:-4,35:4,38:3,43:-2,
         50:2,51:-4,53:-2,54:-2,56:2,60:-2},
        (1,3),
        40,(-3,-2,-2,-3,-2,-2,-3,-6,-4,-3,-6,-4),
    ),
    5:Dual(
        190,
        {5:2,6:-7,9:10,10:-8,11:40,13:-20,14:8,15:-22,
         17:-7,20:-16,21:25,22:30,23:-6,24:-15,
         27:-20,28:40,29:-6,30:-44,31:-16,34:-5,
         35:32,37:-8,38:20,39:-2,40:8,41:-40,
         43:-14,44:-12,46:-2,48:-2,49:40,50:10,
         51:-56,53:-30,55:-8,56:35,57:-18,
         58:-14,59:-24,60:-26,61:20,62:-12},
        (25,15),
        380,(-27,-40,-28,-43,-40,-22,-33,-40,-16,-17,-40,-34),
    ),
    6:Dual(
        56,
        {7:-8,10:-2,11:8,12:-8,13:-4,14:12,
         17:-2,20:-2,21:8,25:-8,28:12,29:-4,
         30:-16,31:-12,33:-8,34:-2,35:12,37:-4,
         38:8,41:-4,42:-8,43:-4,44:-4,45:4,
         46:-4,49:12,51:-16,52:-8,53:-4,55:-12,
         56:8,59:-12,62:-12,63:8},
        (11,1),
        56,(-7,-6,-7,-7,-6,-7,-1,-6,-1,-1,-6,-1),
    ),
}


DEGREE_ZERO_PRIMAL=Primal(1,{0:1},{0:1},Fraction(0))
DEGREE_ZERO_DUAL=Dual(1,{},(0,0),1,(-1,0,0,0,0,0,0,0,0,0,0,0))


def degree_certificate(d:int):
    """For d>=3 exact proof. For smaller d all small Fourier laws agree."""
    if not 0<=d<=6:
        raise ValueError("K4 has six observed edges")
    if d<=2:
        return DEGREE_ZERO_PRIMAL,DEGREE_ZERO_DUAL
    return DEGREE_PRIMALS[d], DEGREE_DUALS[d]


def degree_receipt():
    model=k4_pair()
    records={}
    for d in range(7):
        report=certify(model,d,*degree_certificate(d))
        records[d]={
            "optimum":str(report.optimum),
            "certificate":"exact matched primal-dual",
            "watched":report.walsh_terms,
            "full_output_equal":report.full_output_equal,
        }
    return records
