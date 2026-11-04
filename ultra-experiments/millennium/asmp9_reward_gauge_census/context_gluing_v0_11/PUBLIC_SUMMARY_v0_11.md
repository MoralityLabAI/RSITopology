# Context-local scalar preferences need not glue to one global value function

## Result

Suppose the same finite set of items is compared in several contexts or
histories. Each context has its own comparison graph. A reported edge
difference is **context-locally scalar** when, inside each context separately,
it is the gradient of some scalar utility. It is **shared-scalar** when one
context-independent utility generates every reported edge difference.

Let:

- `D_local` be the block-diagonal incidence operator with one utility copy per
  context;
- `D_union` be the incidence operator on the context-labelled multigraph, with
  one shared utility; and
- `beta_1` denote graph cycle rank.

Conditional on exact scalarity inside every context, the dimension of the
remaining obstruction to one shared scalar is exactly

```text
q
  = rank(D_local) - rank(D_union)
  = beta_1(context-labelled multigraph)
      - sum_context beta_1(context graph).
```

Exactly `q` independent mixed-context cycle circulations are necessary and
sufficient to decide whether the local scalar representations glue.

This is an existence theorem, not a uniqueness theorem. When `q=0`, local
scalarity forces a shared scalar by design, although disconnected comparison
graphs can still leave that scalar non-unique.

## Minimal incompatibility witness

Two items and two contexts are enough. Let each context contain the same
single comparison edge:

```text
context 0: u(1)-u(0) = 0
context 1: u(1)-u(0) = 1.
```

Each one-edge context is internally scalar. No single utility can satisfy both
edge differences. The context-labelled multigraph has one mixed cycle, so
`q=1`; one cross-context equality check is both necessary and sufficient.

The same construction also shows why checking each history separately is not
enough to establish a context-independent value representation.

## Registered verification

The scientific specification was first frozen in v0.11. Two registered
implementations exceeded the unchanged 360-second wall-time cap and were
terminated without producing scientific artifacts. Both failures remain
visible in:

- `EXECUTION_ATTEMPT_v0_11.md`; and
- `EXECUTION_ATTEMPT_v0_11_1.md`.

Version v0.11.2 changed only exact implementation bookkeeping. Graph-incidence
ranks and cycle-space independence were computed by exact `GF(2)` bitset
elimination, while all scalarity decisions continued to use signed rational
cycle circulations. On the pathological first sixteen registered-seed cells,
the literal and optimized scientific outputs had the identical canonical hash
and the optimized implementation was about 410 times faster.

The v0.11.2 implementation was frozen at commit `cbaa42a` and its 34 inputs
were hash-sealed in registration commit `899df09` before the full run.

All ten gates passed:

- all `262,144` ordered triples of simple graphs on four common items matched
  the rank and cycle formulas;
- the mixed-cycle obstruction ranks covered every value `0..6`;
- `261,408` tuples had a live obstruction and `736` were forced-compatible by
  design;
- all `4,096` seeded cells across 5–9 items and 2–5 contexts matched the
  quotient dimension and basis-size predictions;
- all independent-check deletion controls matched the sharp residual
  dimension;
- all shared-scalar, non-gluing, and local-failure controls returned their
  registered statuses;
- the minimal two-item/two-context witness passed; and
- the CPU-only run finished in `104.34` seconds with `22,274,048` peak
  resident bytes, below the registered 360-second and 2-GiB limits.

An independent artifact verifier passed. A second clean execution had
identical scientific fields and a byte-identical report. All 32 dedicated
tests and all 225 repository tests passed.

The authoritative artifacts are in
[`artifacts_v0_11_2`](artifacts_v0_11_2), and the compact verification record
is [`verification_v0_11_2.json`](verification_v0_11_2.json).

## Prior-art and novelty boundary

The linear algebra belongs to classical graph cohomology, HodgeRank-style
preference aggregation, and local-to-global consistency theory. Related
contextuality frameworks also use compatibility and gluing obstructions.
Novelty of the underlying mathematics is not claimed.

The contribution here is the exact finite access grammar, the distinction
between within-context scalarity and shared scalarity, the sharp number of
additional mixed-context checks, the minimal incompatibility witness, and a
prospectively registered exhaustive verification.

## ASMP-9 contribution and remaining gap

This closes the registered finite contextual scalar-gluing subproblem. It
proves that context-local coherence is not sufficient for a
context-independent value representation and characterizes exactly the
additional access required in the finite exact-linear model.

It does **not** resolve ASMP-9. The result assumes:

- a finite common item universe;
- exact real-valued edge differences;
- observed context labels;
- scalar representability within each context;
- no sampling noise;
- no hidden or uncertain context assignment; and
- no dynamic consistency requirement across an open-ended history process.

It does not classify inconsistent or non-expected-utility demonstrators,
finite-sample contextual tests, latent contexts, continuous state spaces,
history-dependent policies in general MDPs, or the maximal invariance group
under a unified observation model.
