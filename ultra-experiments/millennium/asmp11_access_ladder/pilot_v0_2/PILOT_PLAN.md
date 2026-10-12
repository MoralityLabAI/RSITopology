# ASMP-11 v0.2 exact-power construction pilot

## Status

Non-claim-eligible construction pilot. It may refine the v0.2 draft but cannot
pass a scientific gate, establish a crossover, or be pooled with a later
registered run.

## Purpose

Before freezing an adaptive intervention hypothesis, determine whether the
apparent sample-cost inversion survives explicit accounting for intervention
width. The pilot compares complete support coverage under:

- pure degree-`k` observation;
- every nonadaptive boundary allocation with `r+s=k`; and
- order-zero containment queries that fix `s>=k` parents, including the
  universal width-`n` clamp.

For each query count, the pilot computes the minimum samples per query whose
two-sided binomial test has:

- exact union-bound familywise error at most `0.05`; and
- exact signal power at least `0.90`.

Flip rates are `{0.05,0.15,0.25}`, dimensions are `{8,12,16,20}`, and planted
degrees are `{3,4,5,6}`. Probabilities are exact rational binomial sums. The
union bound is conservative but certified; no Monte Carlo confidence interval
is used.

## Interpretation rule

A lower sample count with a larger intervention width is a resource trade, not
unqualified cost dominance. The key pilot outputs are:

1. whether any `r+s=k` plan beats pure observation; and
2. the smallest intervention width at which a containment plan uses fewer
   total oracle samples than pure observation.
