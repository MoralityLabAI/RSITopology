# Nuisance-confusability result v0.36

## Verdict

`bounded_confusability_theorem_verified`

All five preregistered gates passed. The exact census establishes, for the
registered finite deterministic channel class, that raw pairwise
confusability under unknown nuisance is not always representable by a
reward-gauge quotient. Its exact zero-error access object is generally a
confusability graph.

This refines ASMP-9's first resolution obligation. It does not resolve ASMP-9.

## Central result

For a query family `A`, target `theta`, and one nuisance value `h` shared
across queries, define the signature set

```text
S_A(theta) = {(f_q(theta,h))_(q in A) : h in H}.
```

Two targets are confusable when their signature sets intersect. This relation
is always reflexive and symmetric, but it need not be transitive. Since every
group-orbit relation is an equivalence relation, a nontransitive
confusability relation cannot equal the orbit relation of any group action.

The complete one-query census contains:

| quantity | exact count |
| --- | ---: |
| binary tables on `Theta x H`, with `|Theta|=3`, `|H|=2` | 64 |
| tables with nontransitive confusability | 12 |
| registered smaller-cardinality tables with nontransitive confusability | 0 |
| direct-decoder theorem mismatches | 0 |

The nontransitive cases are the three labelled path graphs. Each occurs four
times.

## Exact decision criterion

For any declared decision map `d`, a uniform decoder exists if and only if no
confusability edge joins two targets with different decisions. The runner
checked this against direct transcript-fiber decoding for:

```text
64 * 27 + 4096 * 2 * 27 = 222,912
```

registered channel-decision combinations, with zero mismatches.

Thus the graph is decision-relative in the useful sense: identification does
not require recovering `theta` when every still-confusable target induces the
same downstream decision.

For one fixed query family, a decision is decodable exactly when it is
constant on every connected component of the confusability graph. The
component partition—the finest equivalence relation containing all
confusability edges—is therefore sufficient for the yes/no
decision-feasibility question. It is not the raw pairwise relation: it forgets
which individual edges must be removed, and therefore loses information
needed to compare or design additional queries.

## Shared nuisance can carry calibrating information

The two-query census covered all 4,096 ordered binary-table pairs.

| outcome | exact count |
| --- | ---: |
| joint identity under shared nuisance | 96 |
| joint identity under independently reset nuisance | 72 |
| identity only under shared nuisance | 24 |
| two-query synergy under shared nuisance | 96 |
| query-monotonicity failures | 0 |
| shared-to-reset inclusion failures | 0 |

The planted mirrored-threshold pair is one of the 24 shared-only cases. Each
query alone has path confusability `0--1--2`; together, a stable shared
nuisance makes their joint signature sets disjoint. Resetting nuisance
independently enlarges those sets and destroys identification.

Consequently, nuisance stability is sometimes an information resource rather
than merely an assumption to be survived.

## Gate record

| Gate | Requirement | Decision |
| --- | --- | --- |
| N0 | minimal planted nontransitive path witness | pass |
| M0 | no registered smaller-cardinality witness | pass |
| D0 | graph criterion equals direct decoder criterion | pass |
| Q0 | queries only remove shared confusability; reset cannot help | pass |
| W0 | shared-only identification occurs in the witness and census | pass |

The run completed in `6.0335222` seconds with `351,452` peak traced Python
bytes, inside the registered reporting envelope of 120 seconds and 512 MiB.
These resource limits were reporting bounds, not operating-system hard caps.

## Consequence for the ASMP-9 statement

The phrase “maximal invariance group” is too narrow if it is meant to encode
raw nuisance confusability. The corrected hierarchy is:

1. define the target, query family, and nuisance coupling;
2. compute the signature sets and their confusability graph;
3. test whether every edge lies inside one downstream-decision class;
4. use connected components as the coarsest quotient governing fixed
   decision feasibility; and
5. call that quotient a gauge quotient only when it is induced by a
   scientifically meaningful transformation action.

Taking the transitive closure does preserve the set of uniformly decodable
decision maps, because decisions must already agree along every path. It does
not preserve the pairwise geometry or reveal which query removes which edge.
The v0.36 correction is therefore a distinction between three objects:
pairwise confusability, its decision quotient, and a scientifically grounded
reward-symmetry group.

## Integrity and scope

The implementation and scientific documents were committed before the
registration. The registration was then committed and pushed as `31f0c0a`
before the census ran. The import-independent verifier recomputed the four
headline counts without importing the experiment module and passed every
check.

Confusability graphs, zero-error decoding, and compound-channel reasoning are
classical. This result is a finite access ledger and a correction to the
ASMP-9 resolution object. It does not characterize stochastic demonstrators,
adaptive queries, continuous target classes, misspecification neighborhoods,
human preferences, or any real model's reward.
