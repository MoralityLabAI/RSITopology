# Post-run audit addendum — ASMP-9 reward-gauge census v0.1

## Integrity

- The registered run bound itself to commit
  `7ee30353af8db7e9d8d246afcffbe500348a7256` with an empty tracked diff.
- The verifier reproduced every output hash and the ordinal-counterexample
  polarity.
- The full census ran in 7.13 seconds with 1.72 MB traced peak Python memory.

## What passed

Across all 33,866 labelled simple graphs on two through six vertices:

- the lexicographic spanning-forest construction produced exactly
  `beta_1 = m-n+c` fundamental cycles;
- each cycle had zero incidence boundary;
- each loop-query matrix annihilated every potential-shaping coboundary;
- its kernel dimension equaled the shaping dimension `n-c`; and
- removing one independent cycle query increased the unidentified quotient
  dimension by one.

The triangle counterexample also behaved as registered: exact loop returns 3
and 6 are distinguishable, whereas a sign-only oracle returns `+1` for both;
their difference is not a coboundary.

## Epistemic classification

This is a consolidation and implementation theorem, not evidence of a newly
discovered graph-cohomology result. Once a fundamental cycle basis is chosen,
the dimension gate is close to structural by construction: every non-tree edge
supplies one row with a unique chord coordinate. The exhaustive census validates
the implementation and the exact access boundary; it does not make the
underlying algebra novel.

The live finding for the ASMP portfolio is the access-model separation. Exact
real-valued returns identify a quotient that sign-only feedback does not. The
result does not establish a threshold for noisy pairwise human preferences,
whose inequalities and normalization assumptions require a different theorem.

## Scope omissions for a successor

- Positive affine reward transformations were not included in the registered
  gauge; only potential coboundaries were.
- Discounted shaping requires a separately frozen twisted operator.
- Behavior-policy observations are absent. This experiment queries rewards
  directly and therefore is not an IRL identifiability result.
- A successor preference experiment must state whether scale, translation, and
  stochastic response parameters are fixed, queried, or quotiented.
