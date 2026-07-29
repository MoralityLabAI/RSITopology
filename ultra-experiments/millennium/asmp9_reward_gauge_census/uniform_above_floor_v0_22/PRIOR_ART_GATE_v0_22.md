# ASMP-9 v0.22 prior-art gate

Status: development-only.

## Load-bearing prior art

1. Spencer Backman, ["Partial Graph Orientations and the Tutte
   Polynomial"](https://arxiv.org/abs/1408.3962), *Advances in Applied
   Mathematics* 94 (2018), 103-119.  The paper proves the
   `(k,l)`-chromatic strongly-connected partial-orientation formula.  The
   weighted Tutte identity used by v0.22 is its direct rational-weight
   specialization.
2. François Jaeger, Dirk L. Vertigan, and Dominic J. A. Welsh,
   ["On the computational complexity of the Jones and Tutte
   polynomials"](https://doi.org/10.1017/S0305004100068936),
   *Mathematical Proceedings of the Cambridge Philosophical Society* 108(1)
   (1990), 35-53.  Their dichotomy supplies #P-hardness at every registered
   point on `H_-1`.
3. Fourientation and partial-orientation Tutte expansions are an established
   literature.  No new weighted graph polynomial is claimed.

## Residual ASMP contribution

The candidate contribution is the access-model translation:

```text
r fair Bernoulli comparisons per edge
  -> ZERO/FULL weight 2^(-r)
  -> INTERIOR weight 1-2^(1-r)
  -> strongly connected partial orientation
  -> Backman Tutte point on H_-1
  -> fixed-r #P-hard exact availability.
```

The result would extend v0.21 from the forced count floor to every declared
uniform count, including the minimal above-floor cell `r=2`.

## Wording gate

Allowed:

- exact evaluation of a fixed uniform allocation is #P-hard;
- the fixed-`r` microtrial numerator is #P-complete under polynomial-time
  Turing reductions; and
- the ASMP objective is a classical weighted partial-orientation
  specialization.

Forbidden:

- the Backman formula or Tutte curve is new;
- maximin allocation is #P-hard;
- uniform allocation is optimal on general biconnected blocks;
- arbitrary nonuniform counts or endpoint probabilities are classified; or
- ASMP-9 is resolved.

