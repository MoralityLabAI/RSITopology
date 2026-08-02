# ASMP-4 randomness-quantifier boundary result v0.8

## Result

Canonical ASMP-4 permits shared randomness independent of plant state and
requires safety for every disturbance sequence, but it never orders the
probability and disturbance quantifiers.  That omission changes feasibility.

For countable disturbance alphabets and finite-time-detectable safety,

~~~text
forall w P_r[safe(r,w)]=1
~~~

implies that almost every seed is safe for all disturbance paths.  A common
deterministic seed therefore exists, so randomization cannot improve a
support-cardinality region.

For an uncountable disturbance alphabet, the smooth plant

~~~text
x_(t+1)=(u_t-w_t)^2, K=(0,infinity), u_t=r_t~Uniform[0,1]
~~~

separates the readings.  Every fixed disturbance path is safe almost surely at
zero read and write rate, but every seed path has the defeating disturbance
`w=r`.  Uniform-almost-sure, support-zero-error, and seed-aware-adversary safety
all fail.

## Harness evidence

Central and independent implementations exhaust 484,524 finite-grid
seed/disturbance pairs over `N=2..5` and `T=1..4`.  In every cell they reproduce

~~~text
safe seeds per fixed disturbance = (N-1)^T,
safe pairs = (N(N-1))^T,
universal safe seeds = 0.
~~~

They also verify 60 exact formula cells through `N=1024` and `T=32`.  The
noncommuting limits are

~~~text
lim_T lim_N (1-1/N)^T = 1,
lim_N lim_T (1-1/N)^T = 0.
~~~

Finite grids can therefore suggest either behavior depending on which limit is
taken first.  Random Monte Carlo draws miss the continuous diagonal with
probability one even though a universal or adaptive adversary always finds it.

## Canonical disposition

This result does not declare the permissive per-disturbance reading canonical.
It shows why the choice must be registered.  The source's own graduation rule
requires explicit randomness, adversaries, and quantifier order, while ASMP-4
contains zero probability-order clauses.  No larger capacity harness can infer
whether the intended safety event is per-path almost sure, uniform almost sure,
support zero error, or seed-aware adversarial.

The [v0.9 completion atlas](../asmp4_completion_atlas_v0_9/RESULT.md) combines
this stochastic fork with the independent sensor-registration fork.  It maps
conditional evidence to all five canonical requirements, seals the predecessor
claims, and gives the four-condition contract for reopening local work.
