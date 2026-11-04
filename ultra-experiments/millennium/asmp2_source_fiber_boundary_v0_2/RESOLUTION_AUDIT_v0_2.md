# ASMP-2 resolution audit after the source-fiber theorem

## Current verdict

**The literal local iff is refuted and the unrestricted global boundary is
proved; the broader ASMP-2 classification program is not yet adjudicated
resolved.**

The new theorem removes the main weakness of the v0.1 readiness witness. Both
hidden worlds now possess a globally safe policy with utility one, but their
good-action sets are disjoint. Exact source laws and scores coincide, local
Fisher information is positive, and every risk derivative factors through the
identified score. The best source-only randomized policy succeeds uniformly
with probability exactly `1/2`, for every sample size.

## Obligation ledger

| ASMP-2 obligation | Strongest evidence | Status |
| --- | --- | --- |
| Local semiparametric characterization | Van der Vaart 1991; Trabs 2015; Pérez-Izquierdo 2026; exact feasibility counterexample v0.5 | Adjoint-score part is prior art; v0.1's factorization-only sufficiency is false without robust feasibility/margin |
| Separate local-to-global theorem | Exact source-fiber theorem and sharp dense-source boundary for unrestricted continuous classes | Negative boundary proved |
| Minimax sample bounds | Decision-specific safety deficiency; exact binary rates; exact success `1/2` for all `n` in the hard pair | General variational characterization and sharp hard subclasses; no universal closed-form rate without a registered class |
| Active environment design | Deficiency-minimizing Bellman rule; finite-query packing lower bound; exact Lipschitz midpoint control | Exact decision rule and positive/negative special cases; computation remains class-specific |
| Matching no-free-lunch | Smooth full-support QMD opposite-action pair with utility one | Proved |

## Additional stress-test results

- An exact rational primal/dual solver verified the source-fiber minimax
  theorem over all `438` nonempty good-action hypergraphs with one to three
  worlds and two to three actions.
- A second exact primal/dual solver constructs the full observation-to-action
  Markov kernel for noisy finite experiments and verifies all `81` registered
  binary two-world law/good-set combinations.
- The decision-deficiency binary harness gives exact finite-sample minimax
  values and sample-size inversion; zero signal remains at deficiency `1/2`
  for every sample size.
- A positive-margin Lipschitz theorem supplies an exact continuation envelope.
  In the frozen interval cell, endpoint-only evaluation fails at `11/16`, while
  adding the midpoint certifies exactly at the `9/16` threshold.
- A separate dominated QMD counterexample satisfies derivative factorization,
  positive Fisher information, and the utility floor, but has no robustly safe
  registered action. This refutes the literal sufficiency direction of the
  local conjecture.

## Why resolution is not yet declared

The main v0.1 document describes a classification program rather than one
closed universal statement. Its acceptance policy says a criterion
counterexample does not resolve a broader classification program unless the
criterion is the entire frozen statement. The source-fiber theorem is an exact
replacement boundary, but two issues remain before a defensible resolution
claim:

1. external review must decide whether an exact decision-fiber criterion counts
   as the requested “sharp certification boundary” or is considered a
   tautological restatement of robust decision feasibility; and
2. the stated policy requires two independent expert reproductions, which this
   repository-local verifier does not supply.

## Resolution-directed next step

Stress-test the source-fiber theorem against:

- nonfinite model/action spaces and measurable-selection failures;
- approximate rather than exact source equivalence;
- positive-margin `C^{1,1}` classes, where finite covering becomes possible;
- finite-sample deficiency/modulus bounds outside the identical-law endpoint;
  and
- randomized adaptive designs with fixed curvature and fixed nonzero margin.

If those extensions yield one coordinate-invariant ambiguity modulus whose
zero, local derivative, finite-sample, and design forms match the five
obligations, the packet can be promoted from a negative hard-class theorem to
a genuine replacement characterization.
