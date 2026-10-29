# ASMP-9 resolution audit after v0.22.1

## New closed subproblem

For one finite simple biconnected block, `epsilon=1/2`, and every declared
fixed uniform integer count `r>=2`, exact quotient-liveness availability is a
known rational prefactor times

```text
T_G((2^r-2)/(2^r-1),2^r).
```

Every fixed point lies on the nonexceptional `H_-1` curve.  Exact rational
value evaluation is #P-hard, and its common-denominator trial-matrix numerator
is #P-complete under polynomial-time Turing reductions.  The result is a
direct specialization of Backman plus Jaeger-Vertigan-Welsh, localized to
biconnected blocks by classical Tutte factorization.

## What this resolves in the experiment chain

| question | status after v0.22.1 |
|---|---|
| count-floor exact value inside one block | closed by v0.21 |
| fixed-uniform above-floor exact value | closed by v0.22.1 |
| factorization between arbitrary blocks | closed by v0.20 |
| exact allocation between known local tables | closed by v0.20 |
| exact nonuniform local table in an overlapping-cycle block | open |
| maximin optimizer inside one overlapping-cycle block | open |
| approximation complexity | open |
| arbitrary `epsilon` and endpoint probabilities | open |
| adaptive allocation | open |
| dependent or misspecified responses | open |
| behavioral reward identification / general IRL | open |

## Correct complexity attribution

The proven barrier is **value computation for a declared allocation**.
Optimizer search is trivial at v0.21's positive-count floor and is not
classified by v0.22.1.  No statement that uniform allocation is optimal is
licensed.

## Next theorem target

The next version should address nonuniform counts without assuming an exact
local oracle.  The sharp alternatives are:

1. derive a multivariate Tutte/random-cluster representation and classify the
   exact value oracle for fixed count alphabets;
2. prove an optimizer lower bound that is not merely inherited from evaluating
   a chosen allocation; or
3. identify a tractable graph or parameter regime with a certified
   approximation or dynamic program.

No further uniform-count confirmation is needed.
