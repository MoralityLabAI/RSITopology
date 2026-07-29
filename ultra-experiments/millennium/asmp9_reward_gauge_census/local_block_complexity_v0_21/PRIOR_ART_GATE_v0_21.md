# ASMP-9 v0.21 prior-art gate

Status: development-only.

## Classical results that own the mathematics

1. Michel Las Vergnas, ["Acyclic and totally cyclic orientations of
   combinatorial geometries"](https://doi.org/10.1016/0012-365X(77)90042-5),
   *Discrete Mathematics* 20 (1977), 51-61.  The orientation interpretation
   underlying `T_G(0,2)` is classical and is not claimed here.
2. François Jaeger, Dirk L. Vertigan, and Dominic J. A. Welsh,
   ["On the computational complexity of the Jones and Tutte
   polynomials"](https://doi.org/10.1017/S0305004100068936),
   *Mathematical Proceedings of the Cambridge Philosophical Society* 108(1)
   (1990), 35-53.  Their graphic-matroid dichotomy makes `(0,2)` a #P-hard
   evaluation point under polynomial-time Turing reductions.
3. Farley Soares Oliveira, Hidefumi Hiraishi, and Hiroshi Imai,
   ["FPT Algorithms to Enumerate and Count Acyclic and Totally Cyclic
   Orientations"](https://doi.org/10.1016/j.entcs.2019.08.057),
   *Electronic Notes in Theoretical Computer Science* 346 (2019), 655-666.
   This paper explicitly treats totally cyclic counting as known #P-hard and
   supplies fixed-parameter algorithms in pathwidth/branchwidth for the
   classical total-orientation problem.
4. Biconnected decomposition and multiplicativity of the Tutte polynomial
   across one-point unions are classical.

## Narrow ASMP-9 contribution

The only proposed contribution is the exact access-model translation:

```text
positive count floor + epsilon 1/2
  -> unique one-trial allocation
  -> uniformly random total orientation
  -> ASMP quotient liveness on one biconnected block
  -> total cyclicity
  -> T_G(0,2) / 2^|E|.
```

This closes the v0.20 request for a complexity classification at one exact
boundary.  It is a corollary of classical graph-orientation/Tutte results
after the ASMP access object is translated correctly.

## Hardness language gate

Allowed:

- the numerator problem is #P-complete under polynomial-time Turing
  reductions;
- exact rational value computation is #P-hard;
- the restriction to biconnected blocks is #P-hard under a block-decomposition
  Turing reduction; and
- v0.21 classifies a frozen boundary of the ASMP local value problem.

Forbidden:

- "the optimization problem is #P-complete";
- optimizer search is hard at `N=|E|`;
- arbitrary-epsilon or above-floor design is classified;
- the 2019 FPT algorithms automatically solve ternary partial-orientation
  availability with arbitrary edge counts; or
- any novelty claim for `T_G(0,2)`, totally cyclic orientations, the Tutte
  dichotomy, or block multiplicativity.

## Prior-art disposition

The gate passes only for the narrow translation and explicit localization.
The central mathematics is prior art.  A registered finite run may validate
the implementation and the access-object equality but cannot serve as
evidence for #P-hardness.

