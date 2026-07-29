# Prior-art gate for ASMP-9 decision-relative access v0.38

## Disposition

`general_comparison_theorem_subsumed; reward_access_specialization_retained`

Version v0.38 must not present a target-only deficiency or a restricted
decision comparison as a new theorem. Its surviving role is to specialize
those classical objects to a frozen reward-gauge quotient, downstream policy
loss family, and query/intervention grammar, then derive an access threshold
inside that grammar.

## General results already owned

- Blackwell's comparison theorem characterizes decision-uniform finite
  experiment dominance by stochastic garbling:
  <https://doi.org/10.1214/aoms/1177729032>.
- Le Cam deficiency gives approximate experiment comparison.
- Torgersen explicitly treats deficiencies and distances relative to
  restricted types of decision problems:
  <https://doi.org/10.1017/CBO9780511666353.007>.
- Goel and DeGroot study comparison and marginal information in the presence
  of nuisance parameters:
  <https://doi.org/10.1214/aos/1176344790>.
- Rosenthal's prior-free Blackwell order gives a more recent robust
  value-comparison formalism and a null-space characterization for its
  declared setup:
  <https://doi.org/10.1007/s40505-026-00307-6>.
- Skalse et al. characterize invariance and partial identifiability for
  reward-learning data sources:
  <https://arxiv.org/abs/2203.07475>.
- Skalse and Abate treat partial identifiability under misspecification:
  <https://arxiv.org/abs/2411.15951>.

## Terminology correction

For a frozen loss registry `D`, define

```text
G_D(A,B)
  = sup_(L in D) [V_A(L) - V_B(L)]_+,
```

where `V` is one optimized worst-case decision value. This is a registered
value-gap statistic. It is not a relative deficiency unless an independent
theorem identifies it with the relevant risk-set comparison.

A relative deficiency quantifies uniform transfer over the entire registered
type of decision problems and rules. Ordinary expanded-parameter deficiency
does the same while charging distinctions in nuisance as well as target. The
three quantities must be named separately.

## What survives for ASMP-9

The unresolved specialization is:

1. freeze a finite reward/MDP class and its scientifically licensed gauge;
2. freeze a downstream policy-regret loss family;
3. treat each query/intervention family as a statistical experiment on the
   reward quotient with declared nuisance coupling;
4. compute classical deficiency relative to that loss family against a
   full-access reference; and
5. characterize the minimum query/intervention family attaining zero or
   epsilon relative deficiency.

The desired result is a necessary-and-sufficient access theorem in this
grammar, plus matching lower and upper bounds. It is not the observation that
relative deficiencies exist.

## Nuisance semantics that must be frozen

These are different experiments and cannot be swapped after outcomes:

- a known conditional nuisance law marginalized into each target row;
- nuisance revealed as part of the observation;
- cellwise uniform risk over the expanded `(target,nuisance)` parameter;
- adversarial worst-case nuisance in one optimized value; and
- one latent nuisance shared across repeated queries versus independently
  reset nuisance.

Version v0.36 already proves that shared and reset nuisance can reverse target
identification. Version v0.37 proves that zero-error components, a finite
minimax value profile, and full expanded deficiency need not coincide.

## Required pre-registration controls

- an exact Blackwell-equivalent pair;
- a pair with equal registered minimax value but positive ordinary
  deficiency, showing that one optimized value is too coarse;
- a nuisance-only pair where expanded-state comparison charges information
  irrelevant under the frozen target-only minimax criterion;
- a gauge-null query that cannot reduce relative deficiency;
- a decision-relevant query that does reduce it; and
- an access family whose full-rank reward reconstruction is unnecessary
  because every residual ambiguity is policy-loss null.

## Claim boundary

A passing v0.38 result may establish an exact access threshold for one frozen
finite reward/MDP/loss grammar and validate its relative-deficiency
instrument. It may not claim a new Blackwell/Le Cam/Torgersen theorem, a
general theory of nuisance, a human-value result, or resolution of ASMP-9.
