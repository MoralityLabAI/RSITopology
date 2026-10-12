# ASMP-9 v0.20: the finite access problem factorizes over blocks

## Result

The exact residual-liveness and finite comparison-allocation object developed
in ASMP-9 v0.17-v0.19 extends from cactus graphs to arbitrary
vertex-biconnected blocks.

For every ternary residual edge state:

```text
the reward-gauge quotient is fully live
iff
every nontrivial biconnected block is residual-strongly-connected.
```

Under the registered independent response model, exact availability is
therefore the product of block-local availabilities. A rectangular
endpoint-label worst case also factors. Once exact local block tables are
known, allocation between blocks is solved exactly by Bellman recursion.

## Evidence

The protocol and implementation were committed before the fresh cells were
run. The registered execution:

- passed all 10 gates;
- checked 262,440 fresh ternary residual states with zero mismatches across
  four direct/independent evaluation paths;
- matched two fixed-label exact rational products;
- exhaustively matched the global endpoint-label minimum to the product of
  block minima;
- verified bridge irrelevance both structurally and probabilistically;
- matched Bellman recursion to all 11 positive edge allocations, including
  the complete optimizer set;
- passed a one-block negative control that reports no false computational
  simplification; and
- finished CPU-only in 34.74 seconds using 30.7 MB peak resident memory.

An independent verifier passed all 14 checks.

## Mathematical point

The proof uses the block-cut forest. If a path leaves a block and re-enters at
a different articulation vertex, the outside path and an inside path form a
cycle spanning two blocks, a contradiction. Global mutual reachability can
therefore be projected into each block.

The result says exactly where the hard problem now lives: not in combining
blocks, but in exact finite design *inside one biconnected block with
overlapping cycles*.

## Claim boundary

The graph decomposition, reliability-product principle, and Bellman
allocation are classical and are not claimed as new. This result does not
classify the complexity of the local block problem, handle adaptive or
dependent responses, validate a behavioral choice model, establish
downstream decision utility, prove a general IRL theorem, or resolve ASMP-9.

## Receipts

```text
implementation 21da5b7aa04aa5f8ad1e70da0aff8da3f69b2bb0
registration   8487edad48ba302cbf3d71192df593f2480842ca
registration SHA-256
  a26ef3900087416df5ba92e5c85fd23006ea35f3677ebeb98f5f2cb4fd7ede60
result SHA-256
  bd626d1ad1da1299ff05fd0be415acdffd264b561278a941e094982f8ad9394c
```
