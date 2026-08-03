# Result v0.19

The v0.18 finite-state theorem extends exactly to a registered nonempty initial
uncertainty set `I`: start the subset observer at `B_0=I`. Feasibility holds if
and only if every reachable transition has a singleton current `q` class. If
`A_I` is the resulting observer matrix, exact counts are
`L_T(I) ceil(rho*2^T)` reads and `2^T ceil(rho*2^T)` writes, with read exponent
`1+log2(rho(A_I))`.

The initial state is load-bearing. The history-toggle sensor works from either
known state but fails from their unknown union. A synchronizing fixture shows
only a one-bit transient cost, while a union-dominant fixture raises the read
corner from 2 to 3.

Independent exhaustive implementations classify all 768 pairs of a two-state
deterministic binary transducer and a nonempty initial set: 192 are feasible
and 576 infeasible. Feasibility counts are 80 from `{0}`, 80 from `{1}`, and 32
from `{0,1}`. Exactly 32 transducers are feasible from both known singleton
states but fail under full initial uncertainty.

This does not address a probabilistic prior on initial state, active calibration
before safety begins, continuous state, raw compression, expected length, or
block error.

The complete 20-package chain passes all 234 focused tests in 271.32 seconds.

The v0.20 successor preserves the v0.19 feasibility theorem while proving
that arbitrary irrelevant raw-label refinements shift its read threshold. The
frozen v0.19 initial-state claim remains unchanged.
