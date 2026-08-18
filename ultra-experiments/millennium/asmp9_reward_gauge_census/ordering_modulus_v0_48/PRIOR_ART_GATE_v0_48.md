# ASMP-9 v0.48 evidence-ordering prior-art gate

## Status

**Development attribution complete; confirmation claim must remain a finite
specialization.**

The central ingredients are classical. No novelty is claimed for Buehler
confidence limits, dependence on a designated statistic, loss-dependent
decision procedures, or subset dynamic programming.

## Primary anchors

1. Robert J. Buehler, "Confidence Intervals for the Product of Two Binomial
   Parameters," *Journal of the American Statistical Association* 52(280),
   482-493 (1957),
   <https://doi.org/10.1080/01621459.1957.10501404>. This is the original
   designated-order confidence-limit construction.
2. Paul Kabaila, "Better Buehler Confidence Limits," *Statistics &
   Probability Letters* 52(2), 145-154 (2001),
   <https://doi.org/10.1016/S0167-7152(00)00199-1>. The paper explicitly
   improves a Buehler limit by improving the ordering supplied by the
   designated statistic.
3. Chris J. Lloyd and Paul Kabaila, "On the Optimality and Limitations of
   Buehler Bounds," *Australian & New Zealand Journal of Statistics* 45(2),
   167-174 (2003),
   <https://doi.org/10.1111/1467-842X.00272>. The optimality is conditional on
   a prespecified ordering, and the paper records limitations of the general
   construction.
4. David Blackwell, "Equivalent Comparisons of Experiments," *Annals of
   Mathematical Statistics* 24(2), 265-272 (1953),
   <https://doi.org/10.1214/aoms/1177729032>. The decision problem is part of
   the operational value of a statistical experiment; v0.48 does not claim a
   new comparison theorem.

## Exact differentiation

The candidate v0.48 result is not that Buehler limits depend on their
designated statistic. It:

- freezes one complete finite ASMP-9 calibration experiment;
- propagates the same experiment into two exact downstream decision risks;
- defines one exact reference-law cost for reported upper bounds;
- exhausts or dynamically optimizes the complete evidence-ordering universe;
- certifies that the two optimizer sets are disjoint; and
- measures strict cross-regret in both directions.

The durable ASMP-9 point is architectural: an access certificate that reports
a full confidence procedure must name not only observations and coverage, but
also the decision-relative ordering used to spend the noncoverage budget.

## Freeze decisions

- The expected-bound objective uses the uniform mixture over the registered
  finite parameter laws. This reference law is part of the estimand, not an
  assertion about deployment prevalence.
- A positive result requires disjoint complete optimizer sets and positive
  cross-regrets. Different lexicographic representatives do not suffice.
- The confirmation uses exact subset dynamic programming and checks it
  against exhaustive enumeration on the burned eight-outcome fixture.
- Optimality is relative to deterministic nondecreasing Buehler bounds.
  Randomized bounds, other confidence criteria, and choice of reference law
  remain outside the claim.

## Claim boundary

At most, v0.48 can establish decision-dependent optimal evidence ordering in
one finite shared-BSC experiment. It cannot claim that every value-learning
problem lacks a universal statistic, that the registered reference law is
behaviorally correct, or that ASMP-9 is resolved.
