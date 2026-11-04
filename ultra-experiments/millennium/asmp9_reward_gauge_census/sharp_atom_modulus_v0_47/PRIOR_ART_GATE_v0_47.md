# ASMP-9 v0.47 prior-art gate

## Status

**Freeze decision complete for the v0.47 finite estimand.**

The confidence-set construction is classical.  No novelty is claimed for
Neyman coverage, exact binomial bounds, finite minimax decision theory,
Blackwell comparison, or the use of least-favourable parameters.

## Primary anchors

1. Jerzy Neyman, "Outline of a Theory of Statistical Estimation Based on the
   Classical Theory of Probability," *Philosophical Transactions of the Royal
   Society A* 236, 333-380 (1937).  Confidence regions are acceptance regions
   inverted under a uniform coverage requirement.
2. C. J. Clopper and E. S. Pearson, "The Use of Confidence or Fiducial Limits
   Illustrated in the Case of the Binomial," *Biometrika* 26(4), 404-413
   (1934), <https://doi.org/10.1093/biomet/26.4.404>.  The familiar zero-count
   binomial endpoint is an exact-inversion special case.
3. David Blackwell, "Equivalent Comparisons of Experiments," *Annals of
   Mathematical Statistics* 24(2), 265-272 (1953),
   <https://doi.org/10.1214/aoms/1177729032>.  Experiment comparison supplies
   the monotonicity used in v0.46 and inherited by the decision-risk table.
4. Robert J. Buehler, "Confidence Intervals for the Product of Two Binomial
   Parameters," *Journal of the American Statistical Association* 52(280),
   482-493 (1957),
   <https://doi.org/10.1080/01621459.1957.10501404>.  Buehler limits make an
   exact upper bound smallest subject to coverage and monotonicity in a
   designated statistic.  The v0.47 direct-risk table is an elementary finite
   specialization, not a new optimal-confidence theorem.

## Exact differentiation

The proposed v0.47 result is not a new confidence-interval theorem.  It:

- freezes the all-zero calibration atom of the ASMP-9 three-query experiment;
- identifies the complete parameter subset forced into every deterministic
  honest confidence set at that atom;
- exhibits the matching spike confidence procedure;
- replaces that pointwise but operationally vacuous witness with the
  Buehler-optimal nondecreasing risk bound for a frozen statistic;
- propagates the forced set through the complete horizon-two adaptive
  decision risk rather than through a parameter-radius surrogate; and
- compares the sharp finite atom modulus with the earlier method-of-types and
  rectangular upper constructions.

## Freeze decisions

- The mandatory-atom lemma is presented as an elementary consequence of
  Neyman coverage, not as a named or novel confidence theorem.
- The estimand class is deterministic confidence sets and deterministic
  nondecreasing direct upper bounds. Randomized procedures are outside v0.47.
- Total observed calibration error is the designated ordered statistic.
- Eligibility uses the strict rule `P_theta(T<=t)>alpha`. Exact equality is
  excluded from the mandatory set and is reported by a dedicated boundary
  gate.
- Buehler optimality is only relative to the registered ordering. Optimal
  choice of statistic, expected confidence-set size, admissibility under
  arbitrary orderings, and least-favourable-prior characterizations remain
  open.
- Blackwell comparison is used only for inherited decision-risk monotonicity;
  v0.47 does not claim a new statistical-experiment deficiency theorem.

## Claim boundary

At most, v0.47 can establish a sharp conditional modulus for one observed atom
on one finite channel grid.  It cannot claim a globally smallest confidence
procedure, a continuous-channel minimax rate, or a solution to general value
identifiability.
