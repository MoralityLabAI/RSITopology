# ASMP-9 v0.52 prior-art gate

## Verdict

**Directly subsumed as a corollary of classical Buehler optimality.**

The candidate statement is:

> Sort the finite outcomes by the values of any valid deterministic direct
> upper confidence map `u`, breaking ties arbitrarily. The Buehler map induced
> by that total order is pointwise no larger than `u`.

This is not a new statistical theorem. Buehler's construction is pointwise
minimal among valid upper confidence limits that are nondecreasing in a
pre-specified designated statistic. Taking the designated statistic to be
`u` itself, with any fixed total-order refinement of its ties, makes `u`
nondecreasing by construction. The proposed dominance result is therefore a
short self-ordering corollary.

## Primary sources

1. R. J. Buehler, “Confidence Intervals for the Product of Two Binomial
   Parameters,” *Journal of the American Statistical Association* 52 (1957),
   482–493. DOI:
   [10.1080/01621459.1957.10501404](https://doi.org/10.1080/01621459.1957.10501404).
   This is the original construction.
2. C. J. Lloyd and P. Kabaila, “On the Optimality and Limitations of Buehler
   Bounds,” *Australian & New Zealand Journal of Statistics* 45 (2003),
   167–174. DOI:
   [10.1111/1467-842X.00272](https://doi.org/10.1111/1467-842X.00272).
   This paper formalizes optimality under minimal conditions and identifies
   limitations of the unmodified general construction.
3. P. Kabaila and C. J. Lloyd, “A Simple Measure of the Efficiency of a
   Buehler Confidence Limit,” *Communications in Statistics—Theory and
   Methods* 34 (2005), 767–774. DOI:
   [10.1081/STA-200054404](https://doi.org/10.1081/STA-200054404).
   Its abstract states the relevant minimality property directly.

## What may still be contributed here

Only a consolidation and executable specialization:

- express classical Buehler minimality in the ASMP-9 decision-relative
  evidence-ordering grammar;
- make the “sort a valid direct map by itself” completeness corollary explicit;
- handle finite ties by checking every total-order refinement;
- verify the identity over a complete multilevel finite table universe; and
- close the repository's deterministic-direct obligation before treating
  aggregate randomized coverage separately.

No novelty claim should attach to the dominance theorem, finite-sample
optimality, or the all-order completeness consequence.

## Scope boundary

The cited theorem concerns individually valid deterministic limits monotone in
a designated statistic. It does not show that a mixture of individually
under-covering maps is dominated componentwise by a mixture of Buehler maps.
Aggregate randomized coverage remains outside v0.52.
