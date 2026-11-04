# ASMP-9 v0.22.1: uniform above-floor evaluation remains #P-hard

The v0.21 boundary result was not a one-count accident.

For any fixed uniform trial count `r>=2` on every edge of one finite simple
biconnected comparison block, at `epsilon=1/2`, exact quotient-liveness
availability is

```text
F_G(r)
  = (1-2^(-r))^(|V|-1)
    2^(-r(|E|-|V|+1))
    T_G((2^r-2)/(2^r-1), 2^r).
```

Every evaluation point satisfies

```text
(x_r-1)(y_r-1)=-1
```

and avoids the Jaeger-Vertigan-Welsh easy points.  Consequently:

- exact rational availability for a declared fixed uniform allocation is
  #P-hard under polynomial-time Turing reductions;
- the common-denominator microtrial numerator is #P-complete under that
  reduction convention; and
- hardness already occurs inside one biconnected block, by Tutte
  multiplicativity over graph blocks.

The minimal above-floor count `r=2` evaluates the hard point `(2/3,4)`.

The registered implementation checked three new graphs at `r in {2,3,5}`.
All nine direct status censuses equaled the weighted Tutte formula.  A separate
`2^20` binary-microtrial enumeration on `K5` also agreed exactly.  All ten
gates and all 17 independent-verifier checks passed.

The initial v0.22 attempt is preserved as failed: a case-sensitive
claim-attribution check stopped its verdict despite nine other gates passing.
v0.22.1 hash-bound that failure, repaired only the mechanical evaluator, and
used new graph cells.

This closes the exact **declared-uniform value-evaluation** question above the
count floor.  It does not classify the actual maximin design problem:
nonuniform allocations, arbitrary response probabilities, approximation,
adaptive allocation, and behavioral value identification remain open.

Full record: [RESULT_v0_22_1.md](artifacts_v0_22_1/RESULT_v0_22_1.md).
