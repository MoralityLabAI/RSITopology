# Registered sensor-partition theorem v0.16

## Contract

Use the positive-volume collar plant

`theta_next=theta+1/4 mod 1`,

`n_next=2n+u-q(z)`,

`z_next=w`,

with modes `{-3,-1,1,3}`, `q=(-3,-1,1,3) -> (0,0,8,8)`, authority `[-2,10]`, and safe normal interval `[-1,1]`.

A registered sensor experiment is a fixed partition `P` of the four modes. At each step the sensor observes `(n,g_P(z))`; `g_P(z)` is the block containing `z`. The charged read transcript must retain every current `g_P(z)` symbol injectively, in addition to whatever normal-cell information safety requires. The tangent phase is evaluator-irrelevant and unreported. The current read precedes the current write, and the controller does not see the next disturbance.

Let `k=|P|`.

## Theorem

The registered experiment is feasible exactly when `P` refines the two-block `q`-fiber partition `{{-3,-1},{1,3}}`. For every feasible `P`, the exact full-collar region is

`[1+log2(k),infinity) x [2,infinity)`.

For an initial normal collar `[-rho,rho]`, `0<rho<=1`, the exact horizon-`T` counts are

- read words: `k^T ceil(rho*2^T)`;
- write words: `2^T ceil(rho*2^T)`.

There are 15 partitions of four modes. Four are feasible: one with `k=2`, two with `k=3`, and one with `k=4`. The remaining eleven have empty safety-capacity region.

## Feasible construction

When `P` refines the `q` fibers, the controller recovers `q(z)` from `g_P(z)`. For the full collar, use residual control `a=u-q(z)` equal to `+1` on the negative normal branch and `-1` on the nonnegative branch. The normal dynamics is the two-branch doubling map of `[-1,1]` onto itself, so its depth-`T` cells realize exactly `2^T` normal branch words.

Every one of the `k^T` registered sensor-symbol words is possible under arbitrary mode reset, and the charging rule keeps those words distinct. Their product with the normal branch words gives `(2k)^T` read words. The write depends only on the two `q` classes and two normal branches, producing exactly `4^T` write words. All controls lie in `{-1,1,7,9}`.

For radius `rho`, partition `[-rho,rho]` into `N=ceil(rho*2^T)` cells of width at most `2/2^T`. If a cell has center `c`, use first residual `-2c` and later residual controls zero. The entire cell remains safe. Multiplication by the possible registered sensor words gives `k^T N` reads; multiplication by the two possible `q` classes per time gives `2^T N` writes.

## Matching converses

A fixed control word sends differences between two initial normals to `2^T` times their initial difference. Since final safe diameter is 2, one word covers initial length at most `2/2^T`; therefore at least `ceil(rho*2^T)` normal words are necessary.

The registered charging rule requires the `k^T` sensor-symbol words to remain distinct, so the read lower bound is their product with the normal covering number. At the first differing `q` class, a common write would make successor normals differ by at least `8-2*2=4`, greater than safe diameter 2. Thus distinct `q` words require distinct write languages, giving the factor `2^T`.

If `P` does not refine the `q` fibers, some block contains one mode with `q=0` and one with `q=8`. Choose both initial states with `n=0`; they have the same sensor symbol. At the first step the safe controls are respectively `[-1,1]` and `[7,9]`. These intervals are disjoint, so no causal controller can protect both states. This proves infeasibility without an asymptotic argument.

## Complete four-mode census

The four feasible partitions form a Boolean square under refinement. Refining either `q` fiber raises `k` from 2 to 3, and refining both raises it to 4. Along every cover edge the read threshold strictly increases while the write threshold remains 2. The resulting read thresholds are `log2(4)=2`, `log2(6)`, and `log2(8)=3`.

## Scope

This theorem supplies the missing registered sensor parameter for the v0.13 plant and classifies its entire finite partition grammar. It is not the universal registered-class grammar and does not prove the nonlinear variational characterization requested by ASMP-4.
