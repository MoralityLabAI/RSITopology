# Prior-art gate for ASMP-9 v0.32

Status: development-only. No novelty claim.

## Primary foundations

1. Herstein, I. N. and Milnor, J. (1953), *An Axiomatic Approach to
   Measurable Utility*, Econometrica 21(2), 291-297.
   DOI: https://doi.org/10.2307/1905540

   The mixture-space representation and affine uniqueness are classical. The
   v0.32 global-anchor normalization is a direct specialization.

2. Luce, R. D. and Tukey, J. W. (1964), *Simultaneous Conjoint Measurement:
   A New Type of Fundamental Measurement*, Journal of Mathematical
   Psychology 1(1), 1-27.
   DOI: https://doi.org/10.1016/0022-2496(64)90015-X

   Additive representation from conjoint structure is classical. The finite
   rectangle cross-difference test is elementary linear algebra beneath the
   full axiomatic theory.

3. Krantz, D. H., Luce, R. D., Suppes, P., and Tversky, A. (1971),
   *Foundations of Measurement, Volume I: Additive and Polynomial
   Representations*.

   Cancellation, Archimedean conditions, finite structures, and uniqueness
   are treated systematically. Version v0.32 must not present rectangle
   additivity as a new measurement theorem.

4. Torrance, G. W. (1986), *Measurement of Health State Utilities for
   Economic Appraisal*, Journal of Health Economics 5(1), 1-30.
   DOI: https://doi.org/10.1016/0167-6296(86)90020-2

   The standard-gamble method is an established utility-elicitation
   procedure.

5. Wakker, P. and Stiggelbout, A. (1995), *Explaining Distortions in Utility
   Elicitation through the Rank-dependent Model for Risky Choices*, Medical
   Decision Making 15(2).
   DOI: https://doi.org/10.1177/0272989X9501500212

   Standard-gamble values can be distorted when expected utility fails.
   This is not a minor empirical caveat: it is the reason the v0.32
   mixture-affinity assumption must be a gate and not background prose.

6. Chen, B. and Liu, J. (2026), *Eliciting Von Neumann-Morgenstern Utility
   from Discrete Choices with Response Error*, arXiv:2603.26065.
   https://arxiv.org/abs/2603.26065

   Modern finite-sample VNM elicitation with response errors reaches beyond
   the proposed exact majority-bound specialization. Version v0.32 must not
   claim a new statistical utility estimator or general finite-sample theory.

## Internal predecessors

- v0.26 supplies the unknown-link midpoint/bisection and flat-link boundary;
- v0.27 supplies context-scale gluing and midpoint nuisance;
- v0.30 defines the scalar semantic rectangle and additive residual; and
- v0.31 propagates shared-cell deterministic uncertainty into policy
  decisions.

## Residual contribution

The prospective contribution is not a new expected-utility or conjoint-
measurement theorem. It is an explicit ASMP-9 interface boundary:

```text
global standard-gamble access
  -> normalized behavioral scalar cells;

redundant compound lotteries
  -> finite mixture-affinity falsification checks;

rectangle cross-differences
  -> additive semantic test;

shared cell intervals
  -> exact residual zonotope for v0.31;

ordinal-only or row-local access
  -> exact indistinguishability witnesses.
```

The query-count and exact binomial controls make the interface executable.

## Required wording

Any frozen protocol must state that:

- the positive result recovers the scalar object defined by the assumed
  mixture-space response model;
- global anchors and objective mixture probabilities are substantive access;
- standard-gamble validity is not established for humans or models;
- deterministic ordinal comparisons cannot certify additive cardinal
  structure;
- finite-sample guarantees require a registered response margin and
  independence; and
- ASMP-9 remains unresolved.
