# ASMP-3 witness-transparent normal-form theorem v2.5

## Status and scope

```text
result_status = conditional protocol-to-finder normal form plus literal iff separation
parent_result = ASMP-3-RANDOMIZED-FINDER-AMPLIFICATION-v2.4
supporting_results = ASMP-3-PROTOCOL-QUANTIFIER-v0.7, ASMP-3-ENCODING-INVARIANCE-v2.0
interface_mode = WV-FIX with an explicit witness-transparency contract
changes_parent_problem = false
```

This release proves the first converse from an admitted noisy protocol back to
the local-refutation objects used in v2.3-v2.4. It also proves why the converse
cannot hold for the literal v0.1 text without an operational binding axiom.

The normal form applies to witness-transparent, ideal-simulable protocols with
a positive ideal/noisy coupling margin. It does not cover arbitrary `WV-FIX` or
`WV-ADM` protocols.

## 1. Witness-transparent protocol class

Fix a frozen interface with an adequate replication-quotiented `Refute`. A
protocol is witness-transparent when every ideal-semantic execution path that
rejects a false advocate transcript can be mapped efficiently to a valid
witness `(S,H|S)` such that:

- `Refute(tau,S,H|S)` holds;
- `S` is contained in the quotient classes queried on that path; and
- the extractor uses only the honest critic's information and the public path.

The honest critic must also be able to simulate one verifier execution using
ideal semantic answers, with the same nonsemantic coins, messages, stopping,
and information as the noisy execution. This is the ideal-simulation contract.

Finally, couple the noisy and ideal executions so that their terminal decisions
differ with probability at most `delta`. A sufficient operational condition is
that all decoded semantic answers on the adaptive path agree except on an event
of probability `delta`.

## 2. Protocol-to-finder extraction theorem

Suppose noisy false acceptance is at most `s`, the verifier makes at most `q`
semantic queries, and the decision-coupling failure is at most `delta`.

### Theorem 1

One ideal simulation followed by path extraction is a Las Vegas-with-FAIL
finder with

```text
one-shot success alpha >= 1-s-delta,                 (1)
quotient witness size r <= q,                        (2)
trial time <= C_honest + V + q Eval_H + Ext.         (3)
```

If the protocol has completeness `c` and gap `g=c-s`, then

```text
alpha >= g-delta,                                   (4)
```

because `c<=1`.

### Proof

The noisy execution rejects a false transcript with probability at least
`1-s`. Coupled binary decisions differ with probability at most `delta`, so the
ideal execution rejects with probability at least `1-s-delta`. Every such
ideal rejection exposes a valid witness by transparency; every other path
returns `FAIL`. The path contains at most `q` queried quotient classes, proving
(2), and direct simulation plus extraction gives (3). Finally,
`1-s-delta >= c-s-delta = g-delta`. QED.

The bound is sharp. Put probability `delta` on “noisy rejects, ideal accepts,”
probability `1-s-delta` on “both reject,” and probability `s` on “both accept.”
Then noisy rejection is `1-s`, decision mismatch is `delta`, and ideal rejection
equals `1-s-delta` exactly.

## 3. Exact coupling harness

For every probability denominator `m=1,...,20`, the producer enumerates all

```text
binom(m+3,3)
```

joint tables of the noisy and ideal binary decisions. Across all denominators,
this is `binom(24,4)-1 = 10,625` tables. Every table satisfies

```text
P(ideal reject)
  >= max(0, P(noisy reject)-P(decisions differ)).    (5)
```

Every denominator contains equality cases. Denominators through 16 form the
registered audit; 17 through 20 are held-out confirmation. Canonical digests
bind the complete enumerations without storing thousands of redundant rows.

Nine rational joint tables separately attain (1) at the registered `s,delta`
operating points.

## 4. Canonical replacement protocol

When `delta<g`, Theorem 1 yields a uniformly positive randomized finder. The
v2.4 restart theorem amplifies it while charging every trial, and the v2.3
fresh-block protocol checks the selected witness. For constant `g-delta`, only
a constant number of retries is needed for constant finder failure.

Thus, subject to honest-budget slack and the registered fresh-noise contract,
every witness-transparent ideal-simulable positive protocol has a canonical
challenge/refutation replacement with:

- quotient dimension at most the original semantic-query budget;
- extracted honest finder time given by (3);
- explicit witness communication; and
- the v2.4 gap `1-f-2 epsilon+f epsilon`.

Together with v2.4 sufficiency, this is a normal-form characterization for this
declared subclass, up to the charged constant-factor resource transport.

## 5. Literal v0.1 two-sided separation

The v0.1 text freezes a decidable syntactic `Refute`, but never requires the
verifier's rejection paths to consult it, never requires coverage, and never
states witness transparency. Consequently protocol admission and the displayed
refutation dimension are logically independent under the literal text.

Start with the v0.7 vector-message protocol: it uses one noisy semantic query
and has completeness `4/5`, soundness `1/5`, and gap `3/5`. Pair its unchanged
protocol machinery with any of three decidable relations:

1. a transparent singleton relation, with dimension one;
2. a sound-complete padded relation requiring all `N=T` distinct local classes,
   with dimension `T`, far above a quartic polylog budget; or
3. the empty decidable relation, with dimension infinity.

The latter two are nonbinding: the verifier does not consult them. Atom IDs have
`log2(T)` bits and unit local evaluation cost, so the padded lane uses no hidden
full-answer macro or replication alias. The protocol fingerprint and value are
identical across all three variants.

The finite harness instantiates this construction with vector claims and two to
eight distinct semantic classes. It exhaustively evaluates every semantic
world, every terminal vector claim, and every atom subset. The transparent
relation has minimum one on every false claim, the padded relation is sound and
complete with minimum exactly `N`, and the empty relation recognizes nothing.
The one-query disagreement protocol has no `Refute` lookup and the same `3/5`
gap in all variants. The asymptotic rows then set `N=T` with `log2(T)`-bit local
atom IDs.

Therefore the literal conjecture's **only-if** direction fails: protocol
admission does not imply its arbitrary `r_R` is polylogarithmic. Requiring mere
soundness and coverage does not repair the padded counterexample; operational
binding is necessary.

The v0.7 frozen parity branch already proves the other direction fails: all
three displayed conditions hold while the optimal gap `(3/5)^d` vanishes.
Hence the displayed v0.1 iff is separated in both directions under its literal
nonbinding reading.

## 6. Benign encoding transport

Under the v2.0 bijections on transcripts and quotient classes, a transparent
rejection path, its queried classes, and its extracted witness transport
together. Dimension remains exact and extraction time changes only by the
declared encoding overhead.

The padded and empty variants are not benign encodings of the singleton
relation: they change the witness hypergraph. That is the point. The literal
v0.1 class permits a frozen arbitrary decidable relation but does not connect it
to protocol operation.

## 7. Completion boundary

This release closes:

- protocol-to-finder extraction for the witness-transparent subclass;
- its exact coupling loss and resource ledger;
- a canonical replacement protocol via v2.4; and
- both directions of the literal displayed v0.1 iff separation.

It does not prove every positive protocol is witness-transparent, efficiently
ideal-simulable, or separated from its ideal execution by `delta<g`. It also
does not settle unrestricted interactive communication lower bounds, optimize
over `WV-ADM` interfaces, or adjudicate whether the intended problem should be
the literal text or the repaired typed successor.

## 8. Novelty boundary

The coupling inequality is elementary and path-witness extraction is a standard
proof-normalization pattern. The contribution is their typed ASMP-3 synthesis:
an exact operational converse, charged honest simulation, exhaustive sharpness
receipts, benign-encoding transport, and an explicit proof that nonbinding
`Refute` metadata defeats the literal characterization in both directions.
