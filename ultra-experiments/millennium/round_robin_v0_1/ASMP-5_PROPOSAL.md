# ASMP-5 proposal: bounded verifier-drift reachability

## Narrow subproblem

Test a necessary boundary for reflective safety: does a local certificate rule
remain sound when the checker that interprets the next certificate can itself be
replaced? The proposed experiment searches a complete finite universe for the
smallest certified sequence that reaches semantic unsafety, while requiring
genuine stepwise progress. It can produce a bounded counterexample or a bounded
positive classification; it cannot resolve open-ended self-modification over
partial computable programs.

## Mathematical object and frozen hypothesis

Use a finite transition system with states `z=(p,T,c,j)`: a proposer program
`p`, checker `T`, control state `c`, and task level `j`. Policies and checkers
are Boolean tables from a frozen, size-matched library. An update may replace
`p`, `T`, and `c`. An external semantic predicate `Safe(z)` supplies outcome
labels to the analysis only; neither proposer nor checker can query it.

Two regimes share the same initial state, update grammar, proof alphabet, and
description-length budget:

1. **Adaptive replacement:** the current checker `T_t` accepts the behavioral
   update and installation of `T_(t+1)` under the frozen local certificate rule.
2. **Frozen-root baseline:** `T_0` checks every update; proposer and behavior may
   still change, but the semantic root does not.

For regime `a`, define

```text
d_unsafe(a) = min {t : Safe(z_t)=0 and every preceding update was certified},
```

with infinity when exhaustive reachability through horizon `H` finds none. Also
report the number of reachable safe, behaviorally nonequivalent states and the
maximum progress level. Freeze `H=8`, table input width at most three, proof
alphabet size four, and equal checker/proposer bit budgets.

Hypothesis: adaptive replacement admits a certified unsafe path of depth at
most four in at least one nondegenerate universe cell where the matched
frozen-root system has no unsafe reachable state through `H`; a rooted
refinement rule requiring every successor acceptance set to remain within the
root-certified set removes that path without destroying an eight-step live
chain. This is a finite claim, not evidence for RSI.

## Smallest decisive experiment

Seal the universe generator, exact transition semantics, all truth tables,
canonical state encoding, and an independent reachability checker before the
census. Enumerate widths `N={4,6,8}`, checker mutation radii `{0,1,2}`, and
certificate rules: self-endorsement, pairwise agreement, and root refinement.
Breadth-first search returns the lexicographically first minimum-depth unsafe
path and a replayable certificate for every cell. A second implementation
replays each path and independently verifies any claimed empty reachable set.

The non-Zeno/liveness control requires each accepted step to increase integer
progress by at least one and change the policy's registered behavior vector;
the run must contain both an eight-step safe chain and an admissible unsafe
chain. Positive increments with a bounded convergent sum, identity updates, and
one hard-coded whitelist chain are excluded. Controls include immutable-checker
equivalence, an intentionally permissive checker, proof-token renaming, state
renaming, and matched libraries with verifier replacement disabled.

Kill the instrument if the semantic predicate leaks into `p` or `T`, state
renaming changes reachability, the two implementations disagree, resource
budgets differ between regimes, or either liveness witness is absent. Refute the
frozen hypothesis if the exhaustive adaptive census has no qualifying
separation or if root refinement also blocks the required progress chain.
Intermediate boundary-only differences are `not_established`.

Evidence class: exact finite-state/exhaustive-discretized, yielding at most a
counterexample and candidate finite lemma. It does not establish an infinite
progress theorem, stochastic robustness, or composition through an actually
self-modifying semantic evaluator.

## Optional scale-up: proposal-channel model test

Only after a separately registered causal edit family passes its own gate, run
the existing four-arm Qwen-1.7B design for five rounds: current edited model as
adaptive proposer, frozen `W_0` proposer, one-shot batch, and matched random.
All arms use the same frozen external selector; audit and outer-holdout scores
remain hidden from selection. The estimand is the paired outer-utility increment
of adaptive minus frozen proposal, not a derivative of a sampled text editor and
not a spectral radius. A frozen scorer isolates recursion through the proposal
channel only: evaluator/objective self-improvement remains unmeasured. Kill on
compute mismatch, differential truncation, holdout leakage, or selector gain
without audit/outer gain.

## Resources

| Run | Wall | CPU | RAM | Disk | GPU |
|---|---:|---:|---:|---:|---:|
| Exact pilot: `N={4,6}`, `H=6` | 1-4 min | 4 cores | <=0.5 GB | <=50 MB | none; 0 GPU-hours |
| Exact full: `N={4,6,8}`, `H=8` | 15-45 min | 8 cores | <=4 GB | <=0.5 GB | none; 0 GPU-hours |
| Qwen pilot: 1 family, 2 rounds | 20-45 min | <=4 cores | <=5.6 GB | <=2 GB | 3090, <=3.6 GB VRAM, 0.3-0.8 GPU-hours |
| Qwen full: 4 families, 5 rounds | 3-6 h | <=4 cores | <=9.2 GB commit | <=8 GB | 3090, <=3.6 GB VRAM, 3-6 GPU-hours |

## Consumer, artifact, and reason not to run

Consumers: the HRMmmm self-update gate and the proposal-recursion protocol.
Artifact: an `asmp5_verifier_drift_census` generator, exact checker, minimum-path
receipt, and frozen adaptive-versus-root phase table.

Reason not to run: the finite result may merely repackage the familiar need for
a trusted proof-checking kernel. Unless the census sharpens a necessary
condition or produces a genuinely minimal counterexample, formal prior-art work
on proof-carrying code and reflective proof hierarchies is higher value.
