# ASMP-9 v0.20 post-run note

## Outcome

The preregistered result was positive: 10/10 gates passed. The independent
verifier passed 14/14 checks.

No threshold, cell, graph, label universe, resource cap, gate, claim boundary,
or verdict rule was changed after registration.

## What changed scientifically

Version v0.19.2 solved exact finite allocation on cactus cyclic cores. Version
v0.20 shows that the factorization and between-component Bellman layer extends
to arbitrary vertex-biconnected blocks.

The true remaining combinatorial obstruction is now local:

```text
exact finite maximin access design inside one biconnected block
with genuinely overlapping cycles.
```

The registered one-block negative control prevents v0.20 from being read as a
solution to that obstruction.

## Unexpected finite-cell detail

On the chorded-cycle-plus-triangle cell, the extra trial went to any one of
the seven rim edges. It never went to the chord and never went to the
triangle. This was not a frozen hypothesis and is reported only as a
registered-cell observation.

## Next legitimate step

Do not add another factorization layer. The block-cut decomposition is
complete at this level. The next load-bearing question is the complexity of
the exact local block objective:

1. identify a graph-width or cycle-rank parameter supporting an exact
   fixed-parameter algorithm; or
2. give a reduction establishing hardness for the frozen maximin objective;
   and
3. preserve a direct exhaustive verifier on small blocks.

Adaptive allocation, response dependence, and the behavioral bridge remain
separate ASMP-9 obligations.
