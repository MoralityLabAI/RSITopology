# ASMP-2 as a decision-specific deficiency problem

## Exact reduction

For a registered model class `M`, source experiment

```text
E = {Q_m : m in M},
```

action class `A`, and globally good relation

```text
G = {(m,a):
     sup_theta L_s(a,P^m_theta) <= epsilon
     and
     inf_theta U(a,P^m_theta) >= u_0},
```

define the safety deficiency

```text
D_G(E)
  = inf over Markov decision kernels K from source data to A
      sup_(m in M) [1 - integral K(G_m | x) dQ_m(x)].
```

This is the deficiency of the source experiment relative to an oracle that
reveals the model, restricted to the single registered safety/utility decision
problem.

If the infimum over decision kernels is attained—as it is in the finite
registered programs in this packet—the original certification goal holds at
confidence `1-delta` if and only if

```text
D_G(E) <= delta.
```

This is not an analogy: expanding the objective defining `D_G` gives exactly
the ASMP-2 probability of selecting a policy whose global safety and utility
constraints hold.

For arbitrary noncompact action/kernel spaces, the boundary needs an
attainment convention. Without one, a certificate at failure at most `delta`
always implies `D_G(E) <= delta`, and `D_G(E) < delta` always supplies such a
certificate, but `D_G(E) <= delta` need not supply a kernel at equality. Thus
the displayed iff is an attained/finite theorem, or equivalently a theorem for
the closure of achievable failure levels. Compactness, lower semicontinuity,
and the usual measurable-selection hypotheses are sufficient routes to an
attainment result in a registered infinite problem.

## Consequences

1. **Coordinate invariance.** `D_G` is unchanged by bijective model
   reparameterizations, sufficient-statistic replacements, or action
   relabelings preserving `G`.
2. **Population fibers.** When the complete source law is known, `1-D_G`
   reduces to the source-fiber value `alpha_*` in `THEOREM_v0_2.md`.
3. **Finite samples.** With `n` source samples, the exact minimax failure
   infimum is `D_G(E^n)`. Under attainment, exact sample complexity is

   ```text
   n*(delta) = inf {n: D_G(E^n) <= delta}.
   ```

   Without attainment, use strict crossing or define sample complexity from
   the achievable failure set rather than its closure.
4. **Active design.** If environment `e` supplies experiment `E_e`, and the
   registered design set admits a minimizer, the exact one-step minimax choice
   is

   ```text
   e* in argmin_e D_G(E tensor E_e).
   ```

   Otherwise the infimum and epsilon-optimal designs are the exact objects. A
   multi-step design is the Bellman recursion for the same terminal deficiency
   once the adaptive observation state, horizon, costs, and admissible design
   kernels are frozen. The existing ASMP-2 census shows that replacing a
   registered recursion by a myopic surrogate can incur large regret.
5. **No free lunch.** If two models have identical source laws and disjoint
   singleton good sets, `D_G(E^n)=1/2` for every `n`.

## Binary exact finite-sample case

For worlds `s in {-1,+1}`, suppose each observation equals `s` with probability
`1/2+eta`, and the safe action is `-s`. Symmetry and the monotone likelihood
ratio make randomized majority testing minimax. Therefore

```text
1-D_G(E_eta^n)
  = sum_(k>n/2) binom(n,k)(1/2+eta)^k(1/2-eta)^(n-k)
    + 1/2 * [tie probability when n is even].
```

The companion exact-rational harness checks this formula, the `eta=0`
all-sample obstruction, minimal sample-size inversion, and the active choice
of the environment with largest binary signal.

## Local limit

In a QMD/LAN model, differentiability of smooth scalar constraints supplies
the first-order approximation to `D_G`. The gradient must lie in the range of
the adjoint score operator for root-`n` regular estimation; this is established
semiparametric theory, not a new ASMP-2 theorem.

That local condition is not sufficient for safety deficiency to vanish. The
good relation must also be feasible and stable under local alternatives. At a
zero policy margin, an arbitrarily small, fully identifiable change can switch
the only good action, leaving a nonregular testing problem. The v0.1 local
conjecture omits this feasibility/margin condition.

## Prior-art adjudication

The reduction sits directly inside Blackwell comparison and Le Cam/Torgersen
decision-specific deficiency. Donoho-Liu moduli provide rate characterizations
for important convex functional-estimation classes, while adjoint-score theory
provides the local regularity criterion.

Therefore the abstract five-part ASMP-2 request has two possible
adjudications:

1. accepting `D_G` as the requested coordinate-invariant boundary makes the
   formal certification question an application of classical statistical
   decision theory, with class-specific computation left to registered
   instances; or
2. rejecting `D_G` as too operational or tautological means v0.1 must specify
   the structural form expected of a nontrivial replacement theorem.

The current wording does not choose between these standards. That ambiguity,
not a missing finite experiment, is now the remaining resolution blocker.
