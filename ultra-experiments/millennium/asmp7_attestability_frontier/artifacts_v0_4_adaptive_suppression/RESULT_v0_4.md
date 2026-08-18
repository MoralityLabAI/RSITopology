# ASMP-7 causal adaptive suppression v0.4 result

## Outcome

The registered finite model result passed all primary and independent gates.
Within the frozen product-stream causal model, allowing an exact-size mask to
depend on the complete past does not move the extrema of any rational
coordinatewise-monotone finite-horizon report payoff beyond constant endpoint
masks. The inherited v0.3 selective-suppression frontier and its exact sample
minima therefore transfer to this causal adaptive class.

This is a verified model-only proof/experiment attempt. It is not an ASMP-7
resolution and authorizes no deployment.

## Frozen evidence chain

- Source commit: `aa04de72bbef401f16637cb78b2f8eac8da0c507`
- Primary-result commit: `861cf1f6dcbeedac3382ce5651563802cd908520`
- Independent-verification commit: `943eca8f573a0b71f0037fd9d38ceca407bafd0e`
- Canonical manifest SHA-256:
  `c3c9430257645e5709ce3c838c124e021ad293d750d7bd1afb75c0eaaed4a1d3`
- Raw primary-result SHA-256:
  `ce249931bf3721bc84014fa34571b2a8a47941b532b2cc0521ae244782040902`
- Raw verification SHA-256:
  `2768ce3f59d6b401287e43d4307e990b27b3f8505d47290b859522bfdeaf3243`

The machine-readable artifacts are `result_v0_4.json` and
`verification_v0_4.json` in this directory.

## What passed

- All 72 registered `(k,c)` concrete-mask quotients matched the independent
  combinatorial multiplicity formula.
- All 48 inherited selective rows transferred exactly: 21 are
  `feasible_exact` and 27 are `common_law_impossible`.
- Every feasible randomized-binomial test and immediate infeasible predecessor
  was recomputed exactly by the independent verifier.
- All 144 registered upper-tail Bellman rows matched their constant iid
  endpoints.
- All 11,520 generic-terminal comparisons passed. These cover all 20 monotone
  Boolean terminal tables at horizon three, including all 15 nonsymmetric
  tables, over the frozen action-law universe. The primary used recursive
  full-prefix dynamic programming; the verifier independently generated
  terminals from antichains and used a bottom-up recurrence.
- All six controls, five robustness probes, nine primary gates, and twelve
  independent gates passed. Every mismatch list is empty, and the independent
  verifier imported no primary implementation.

The horizon-three census is a machine check of the proof structure. The
arbitrary rational terminal and deterministic `m<=8192` statement rests on the
registered finite backward-induction argument: terminal monotonicity preserves
the continuation order, Bellman values are affine in the next-report
probability, that probability is monotone in the attainable mask action, and
private randomized policies are convex mixtures. Rational monotone terminals
also decompose into nonnegative layers of Boolean upper sets.

## Scope breakers

The negative controls show why the restrictions matter.

- If the mask may share or observe current-challenge information at
  `(k0,k1,theta,c)=(8,14,1,12)`, the causal ordering `5/8 < 3/4` reverses to
  `3/4 > 7/16`.
- For the excluded nonmonotone two-step exactly-one payoff, a history-dependent
  policy attains `5/8`, while the best fixed policy attains `1/2`.

## Resources

- Primary: 17.297 seconds, 828,495-byte peak traced Python allocation,
  267,653 canonical result bytes.
- Independent verifier: 16.266 seconds, 2,625,076-byte peak traced Python
  allocation, 15,695 canonical verification bytes.
- Both stages stayed below the frozen 30-second, 64-MiB traced-Python, and
  one-MiB artifact ceilings. Process RSS and native allocations were not
  measured.

## Claim boundary

The supported language is only
`finite_registered_causal_adaptation_equivalence_supported`. It assumes the
fixed 16-point Boolean execution, exact-size masks, mutually independent fresh
challenge/report/policy/auditor streams, challenge uniformity conditional on
the frozen filtration, a report-only monitor, deterministic finite horizons,
and coordinatewise-monotone terminal payoffs.

It establishes no current-challenge-aware result, nonmonotone audit theorem,
random stopping-time or infinite-horizon result, stateful execution result,
nonuniform/dependent-challenge result, real-meter guarantee,
transformation-universal attestability, deployment decision, or ASMP-7
resolution.
