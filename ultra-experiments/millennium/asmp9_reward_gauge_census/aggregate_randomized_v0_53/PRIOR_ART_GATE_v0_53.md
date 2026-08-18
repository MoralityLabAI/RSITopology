# ASMP-9 v0.53 aggregate-randomization prior-art gate

## Verdict

**Randomized confidence procedures and their gains for discrete data are
classical.**

External randomization has long been used to remove coverage conservatism in
discrete models. The finite linear-program formulation and basic-feasible
solution sparsity are standard decision theory and linear programming.

The ASMP-9 contribution must therefore be limited to an executable
specialization and one information-loss statement:

> The thresholded subset-bound table that is sufficient for deterministic
> Buehler optimization is not sufficient to determine the optimum under
> aggregate randomized coverage.

The two-outcome witness is elementary. No novelty claim should attach without
a much broader literature review.

## Primary sources

1. C. J. Geyer and G. D. Meeden, “Fuzzy and Randomized Confidence Intervals
   and P-Values,” *Statistical Science* 20 (2005), 358–366. DOI:
   [10.1214/088342305000000340](https://doi.org/10.1214/088342305000000340).
   The paper develops confidence procedures dual to randomized tests for
   discrete distributions.
2. P. Kabaila, “On randomized confidence intervals for the binomial
   probability,” arXiv:
   [1302.6659](https://arxiv.org/abs/1302.6659) (2013). It reviews the
   Stevens randomized interval and extensions.
3. M. Thulin, “On split sample and randomized confidence intervals for
   binomial proportions,” *Statistics & Probability Letters* 92 (2014),
   65–71. DOI:
   [10.1016/j.spl.2014.05.005](https://doi.org/10.1016/j.spl.2014.05.005).
   It compares external and data randomization and discusses their practical
   interpretation.

## Residual claim boundary

The finite witness below is not a new randomized-confidence construction. It
shows that ASMP-9's deterministic compression

```text
experiment -> subset threshold table B
```

ceases to be information-complete when coverage is averaged over a report
randomizer. Exact probability magnitudes must re-enter.

The result says nothing about whether randomized certification is
operationally acceptable for safety decisions.
