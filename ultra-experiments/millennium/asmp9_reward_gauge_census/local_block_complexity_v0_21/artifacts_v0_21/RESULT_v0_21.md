# ASMP-9 v0.21 result: count-floor value is a #P-hard Tutte evaluation

## Verdict

```text
count_floor_local_value_complexity_classified_v0_21
```

All 10 registered gates passed.  The import-independent verifier passed all
11 checks.

## The exact identity

On one finite simple biconnected comparison block, freeze:

```text
epsilon = 1/2
total budget N = |E|
positive integer counts n_e >= 1.
```

The allocation is uniquely `n_e=1`.  Each edge then has one fair binary
orientation, independent of its endpoint label, and the ASMP residual
quotient is live exactly when the orientation is totally cyclic.  Therefore:

```text
F_G = T_G(0,2) / 2^|E|.
```

This identity translates the frozen ASMP access object into classical graph
enumeration.

## Complexity consequence

Las Vergnas's classical orientation interpretation identifies `T_G(0,2)` as
the number of totally cyclic orientations.  The Jaeger-Vertigan-Welsh
Tutte-plane dichotomy makes evaluation at `(0,2)` #P-hard for graphic
matroids under polynomial-time Turing reductions.  The count is in #P
because an orientation is an `|E|`-bit witness and directed reachability
checks total cyclicity in polynomial time.

Consequently:

- the count-floor numerator problem is #P-complete under polynomial-time
  Turing reductions;
- exact rational value computation is #P-hard; and
- the restriction to biconnected blocks is #P-hard under a polynomial-time
  Turing reduction.

The last item follows because a graph with a bridge has zero totally cyclic
orientations, while a bridgeless graph decomposes into polynomially many
biconnected edge blocks whose orientation counts multiply.

This is not a hardness result for optimizer search.  At the count floor the
optimizer is forced and therefore trivial to find.

## Prospectively registered exact checks

| Fresh biconnected graph | Edges | `T_G(0,2)` | Exact availability |
|---|---:|---:|---:|
| wheel on 7 vertices | 12 | 726 | `363/2048` |
| Petersen | 15 | 1,920 | `15/256` |
| pentagonal prism | 15 | 1,800 | `225/4096` |
| subdivided `K4` star | 9 | 24 | `3/64` |

On every cell, three routes returned the same integer:

1. multigraph-safe deletion-contraction at `(0,2)`;
2. explicit enumeration of every total orientation; and
3. the inherited ASMP quotient-liveness predicate.

The smallest cell also reproduced `3/64` under all-zero, all-one, and
alternating endpoint labels using the inherited exact ternary-status
evaluator.

## Controls

### Bridge scope

On the wheel plus one leaf bridge:

```text
T_G(0,2) = 0
totally cyclic orientations = 0
ASMP quotient-live orientations = 1,452
ASMP quotient availability = 363/2048
```

The classical count is zero because a bridge cannot lie on a directed cycle.
The ASMP quotient deliberately ignores original bridges, so the bridge's two
directions cancel in the normalized availability and the wheel value is
preserved.  This control prevents the theorem from being overextended from a
biconnected block to an arbitrary bridged graph.

### Block localization

On the one-point union of the wheel and a pentagon:

```text
direct T_G(0,2)
= exhaustive orientation count
= ASMP numerator
= block product
= 1,452
= 726 * 2.
```

This is the finite check corresponding to the biconnected-oracle reduction.

## Integrity

```text
development implementation
  ca7ca070dc614ea5f38a364b2df100cdf3c839fb

protocol/source freeze
  c7672b74024004a28601433de35b4d1f678553b4

registration commit
  e45d2b9f844e0275442770d182fc17c0efea7ef1

protocol SHA-256
  5b1a62e5c28444fe78b663913510d40e88f6724fc6f808d15b71fd73e8cf8c4a

registration SHA-256
  6e79a421c1551e07d44fdaadff5a4967f2cf92371ac0434ce2460ae001aad6c1

result SHA-256
  b92f7b68547cbd84a7629ea270bd789a4b01087a70f62f43f94c08e3a43336aa

independent verification SHA-256
  dbe651faeebf53cc9a421fa405882ae1bd3c535d0d08678b95098660d212d680
```

The registered run used no GPU, completed in `36.493267` seconds, and peaked
at `39,137,280` resident bytes.

## Claim boundary

Version v0.21 classifies exact value computation at one frozen boundary of
the v0.20 local problem.  The finite cells verify the translation and
implementation; they are not the proof of the classical complexity theorem.

The result does not classify:

- optimizer search or exact design for `N>|E|`;
- arbitrary-`epsilon` weighted partial orientations;
- approximation or the full parameterized complexity landscape;
- adaptive allocation;
- dependent, contaminated, strategic, or misspecified responses;
- behavioral reward identification;
- general inverse reinforcement learning; or
- ASMP-9 at its full frozen scope.

