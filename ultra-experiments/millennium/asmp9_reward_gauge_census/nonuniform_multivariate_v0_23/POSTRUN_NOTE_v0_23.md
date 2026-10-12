# ASMP-9 v0.23 post-run note

## What changed

The exact nonuniform local-value table is no longer missing as a mathematical
object:

```text
F_G(n) = -2^(-N) Z_G(-1,{2^(n_e)-1}).
```

The representation is exact but not automatically tractable.  Uniform inputs
are already #P-hard by v0.22.1.

The simplest optimizer conjecture is now false.  The K4 family contains strict
suboptimal one-exchange local maxima for every `s>=2` and violates the
M-concavity exchange axiom.

## What did not change

The result does not prove optimizer-search hardness.  Value-oracle hardness
does not by itself classify the search problem, and a local trap does not
exclude a different global polynomial-time algorithm.

## Next load-bearing target

Do not run another finite allocation census merely to find more traps.
The next version should choose one of:

1. classify optimizer-search complexity by a reduction whose output requires
   an optimizer rather than only a declared-allocation value;
2. derive a tractable global algorithm on a nontrivial overlapping-cycle
   graph class despite failure of one-exchange ascent; or
3. establish a certified approximation scheme or approximation obstruction
   for a precisely frozen graph/count regime.

Arbitrary `epsilon`, adaptive allocation, and behavioral misspecification
remain later axes.  They should not be mixed into the optimizer-complexity
question before its access model is settled.
