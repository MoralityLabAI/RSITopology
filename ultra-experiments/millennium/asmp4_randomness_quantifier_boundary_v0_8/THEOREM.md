# ASMP-4 v0.8 randomness/disturbance quantifier theorem

## 1. Canonical scope audit

Canonical ASMP-4 permits “shared randomness independent of the plant state”
as an explicit architectural choice and requires safety “for every allowed
disturbance sequence.”  It does not say where probability over that randomness
sits relative to the disturbance quantifier.  This omission matters because
the document's own graduation rule requires “randomness, adversaries, and
quantifier order” to be explicit.

For a random seed or seed sequence `r`, disturbance path `w`, and safety event
`safe(r,w)`, distinguish:

~~~text
S_path:     forall w P_r[safe(r,w)]=1,
S_uniform:  P_r[forall w safe(r,w)]=1,
S_support:  forall r in supp(P_r) forall w safe(r,w),
S_adapt:    safe against a disturbance allowed to observe r causally.
~~~

`S_support` implies `S_uniform`, which implies `S_path`.  Without domain or
measurability restrictions, neither converse is automatic.

## 2. Countable disturbances collapse the first fork

Assume safety failure is witnessed at a finite time, as it is when a trajectory
first leaves `K`.  Let the disturbance alphabet be finite or countable.

**Theorem 1 (countable-disturbance collapse).** If

~~~text
forall w P_r[safe(r,w)]=1,
~~~

then

~~~text
P_r[forall w safe(r,w)]=1.
~~~

Consequently there exists a deterministic seed safe for every disturbance
path.  Fixing such a seed cannot enlarge either complete transcript support,
so per-path almost-sure randomization cannot improve a support-cardinality
ASMP-4 region in this countable setting.

**Proof.** For every finite disturbance prefix `p`, let `F_p` be the set of
seeds that have failed by the end of `p`.  If `F_p` had positive probability,
then every infinite extension of `p` would have positive failure probability,
contradicting the hypothesis.  Hence every `F_p` is null.  There are countably
many finite prefixes over a countable alphabet, and every safety failure lies
in one of their sets.  Their union is null, so every seed outside it is safe
for every path. QED.

This theorem yields an almost-everywhere deterministic seed.  It does not say
that every measure-zero point in the topological support is safe; that is why
`S_support` remains a stronger property of a particular randomized code.

## 3. Uncountable diagonal separation

Let `r_t` be iid uniform on `[0,1]`, registered as shared randomness independent
of plant state.  Use no read or write messages.  The actuator sets `u_t=r_t`.
Let `w_t` range over `[0,1]` and define the smooth bounded-input plant

~~~text
x_0=1,
x_(t+1)=(u_t-w_t)^2,
K=(0,infinity).
~~~

**Theorem 2 (uncountable diagonal separation).** This zero-rate code satisfies
`S_path` but fails `S_uniform`, `S_support`, and `S_adapt`.

**Proof.** Fix any disturbance path `w`.  Failure occurs only in
`union_t {r_t=w_t}`.  Each equality event is a Lebesgue-null singleton and the
union is countable, so its probability is zero.  Thus `S_path` holds.

For every realized seed path `r`, however, the allowed disturbance path `w=r`
makes `x_1=0`.  No seed is safe for all paths, so the uniform-safe seed set is
empty.  The diagonal branch lies in the support, and an adversary observing
`r_t` can choose `w_t=r_t` immediately. QED.

The separation is not caused by discontinuous dynamics: `(u-w)^2` is a
polynomial.  Controls and disturbances are bounded.  The safe set is open,
and the fixture is a quantifier-boundary counterexample rather than a claim
about the normally-hyperbolic subclass.

In fact, under `S_uniform` or `S_support`, the registered plant is infeasible
at every communication rate when the current disturbance is selected after
the control.  Whatever action a deterministic seed produces, an allowed
disturbance can equal it.  Under `S_path`, the displayed zero-message code puts
the origin in the region.  The probability order therefore changes
feasibility, not merely a finite correction.

## 4. Exact finite-grid audit

Replace `[0,1]` by an `N`-symbol grid and truncate at horizon `T`.  For every
fixed disturbance word, a uniform seed word is safe exactly when all `T`
coordinates differ.  Hence

~~~text
safe seed words for fixed w = (N-1)^T,
P[safe | fixed w] = ((N-1)/N)^T,
safe (seed,w) pairs = (N(N-1))^T.
~~~

No seed word is universally safe: the disturbance can copy its first symbol.

The central implementation enumerates every seed/disturbance pair for
`N=2,3,4,5` and `T=1,2,3,4`.  An independent verifier uses integer base-`N`
word decoding instead of Cartesian-product generation.  Across 16 cells and
484,524 pairs, both obtain the formulas exactly and find zero universally safe
seed words.

Finite grids therefore do not satisfy `S_path` exactly—the failure probability
is positive—but they converge to the continuous fixed-path value at every
fixed horizon.

## 5. Noncommuting limits

Let `s(N,T)=(1-1/N)^T`.  Then

~~~text
lim_(T->infinity) lim_(N->infinity) s(N,T) = 1,
lim_(N->infinity) lim_(T->infinity) s(N,T) = 0.
~~~

The harness evaluates 60 exact formula cells for ten powers-of-two alphabet
sizes through `1024` and six horizons through `32`.  Success increases strictly
with `N` at fixed `T` and decreases strictly with `T` at fixed finite `N`.
Thus neither a finite-alphabet asymptotic first nor a fixed-horizon continuum
approximation can stand in for the declared stochastic quantifier order.

## 6. Monte Carlo trap

For a random independent seed/disturbance pair on the continuous diagonal,
the probability of observing equality is zero, while an adaptive or universal
adversary finds the diagonal with probability one.  On an `N`-grid, the chance
that `S` one-step random trials see no failure is `(1-1/N)^S`, which can remain
large even though every seed has a worst-case defeating disturbance.

This instantiates the canonical warning that random nonfailure cannot establish
universal confinement.  The issue is not inadequate sample size; the random
test distribution assigns vanishing mass to the adversarial diagonal in the
continuous model.

## 7. Relation to v0.7

V0.7 proves a support-derandomization theorem: every zero-error randomized
support tree contains a deterministic safe subtree with no larger port
languages.  The present theorem does not contradict it.  Instead, it proves
that `S_path` can call a code safe even though its support contains an unsafe
diagonal branch.  The word “zero-error” is therefore load-bearing.

For countable disturbance alphabets, Theorem 1 closes the gap at the level of
achievable regions by producing a common deterministic seed.  The new fork
appears only when an uncountable disturbance domain prevents the null-set union
argument.

## 8. Canonical disposition

The canonical ASMP-4 region for randomized codes is not fully defined until a
registration states:

1. whether safety means `S_path`, `S_uniform`, or `S_support`;
2. whether the disturbance is oblivious, seed-aware, or causally adaptive;
3. the disturbance alphabet and relevant measurability/topology; and
4. whether transcript cost uses support, worst-seed, or an expectation.

The source supplies none of those probability-order clauses while expressly
allowing shared randomness.  The v0.8 harness therefore strengthens the
evidence-backed stop: further rate enumeration cannot select a missing
stochastic semantics.

The [v0.9 completion atlas](../asmp4_completion_atlas_v0_9/THEOREM.md) combines
this quantifier fork with the orthogonal sensor-registration fork and proves
the resulting semantic-underdetermination stopping theorem.
