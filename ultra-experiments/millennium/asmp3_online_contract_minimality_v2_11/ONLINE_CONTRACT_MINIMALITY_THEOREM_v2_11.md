# ASMP-3 online-contract minimality theorem v2.11

## Status and scope

```text
result_status = black-box Las Vegas minimality of the v2.10 online contract
parent_result = ASMP-3-ONLINE-NOISY-TRACE-EXTRACTOR-v2.10
supporting_results = ASMP-3-TRACE-BINDING-EXTRACTOR-v2.8, ASMP-3-HONEST-SEARCH-BARRIER-v2.1
interface_mode = registered unique-marker observation model
changes_parent_problem = false
```

The v2.10 contract is sufficient for one-shot protocol-to-finder extraction.
This release proves that each of its informational and probabilistic premises
is necessary for the corresponding **black-box Las Vegas** reduction.

Minimality is not claimed against task-specific non-black-box proofs, stronger
prior information, or a future normative interface.  The theorem classifies
what can be derived uniformly from the registered online observations.

## 1. Zero-invalid-output observation model

Let the semantic world contain a unique marker `m` among `N` quotient classes.
The false claim says that every marker is zero, so the only valid singleton
witness is `m` with ideal answer one.

An extractor may output a witness or `FAIL`.  Las Vegas validity requires every
non-`FAIL` output to be valid in every world consistent with its observation.
Equivalently, an output must lie in the intersection of the valid-witness sets
over that observation class.

The harness compares three observation regimes:

```text
decision only:             reject
bound trace only:          reject, candidate c, noisy answer 1
bound trace plus H(c):     reject, candidate c, H(c)
```

Positive noise gives every candidate log positive probability both when `c=m`
and when a decoy `c!=m` was flipped to one.

## 2. Decision-only impossibility and probe frontier

### Theorem 1

For `N>=2`, a decision-only observation has no common valid witness.  Therefore
its black-box Las Vegas success is zero.

If the extractor may make `k` candidate-independent ideal probes and may output
only a probed positive class, its exact minimax success is

```text
k/N.                                                            (1)
```

### Proof

All `N` worlds produce the same decision, while their singleton witness sets
are pairwise disjoint.  Their intersection is empty, proving the first claim.

For the upper bound in (1), average the probability that each marker is probed:
the sum is at most `k`, so some marker is probed with probability at most
`k/N`.  For the lower bound, select a uniformly random `k`-subset.  Every marker
belongs to exactly `C(N-1,k-1)` of the `C(N,k)` subsets, whose ratio is `k/N`.
QED.

The harness enumerates all uniform subset schedules for `N=2,...,20` and
`k<=4`: 73 exact frontiers with equal hit counts for every world.

## 3. Why a candidate trace is not enough

### Theorem 2

Under any positive decoy probability, a bound candidate log without access to
`H(c)` has zero black-box Las Vegas success.

### Proof

Fix a logged candidate `c`.  The same observation occurs in world `m=c`, where
`c` is valid, and in every world `m!=c`, where noise forged the candidate and
`c` is invalid.  No candidate is valid in every compatible world.  Because each
case has positive support, zero-invalid-output extraction must return `FAIL` on
the entire observation class.  QED.

This is a support-level discontinuity: an arbitrarily small positive decoy mass
forces trace-only Las Vegas success from one to zero.  Seventy-six rows cross
`N=2,...,20` with decoy probabilities `1/100`, `1/10`, `1/5`, and `1/3`.

Trusting the noisy candidate instead succeeds with probability `1-e` but emits
an invalid witness with exact probability `e`.  Evaluating `H(c)` and failing
closed preserves success `1-e` while reducing invalid-output probability to
zero.  Thus both candidate-only ideal access and mandatory `Refute` rechecking
are material, not bookkeeping.

## 4. Necessity and sharpness of path-error control

Noisy soundness alone does not imply finder success.  A protocol can reject a
false claim on every execution using a forged noisy candidate.  Its false
acceptance is zero, yet ideal revalidation fails everywhere and the safe finder
success is zero.

More generally, let noisy false acceptance be `s` and let the adaptive path
error probability be `delta`.  The v2.10 guarantee

```text
alpha >= max(0,1-s-delta)                                      (2)
```

is sharp.  Assign mass

```text
good reject = max(0,1-s-delta),
bad reject  = (1-s) - good reject,
bad accept  = delta - bad reject,
good accept = s - bad accept.
```

All four masses are nonnegative, sum to one, and attain equality in (2).
The producer enumerates 270 exact tables for `s` in `{0,1/5,1/3}` and every
rational `delta` with denominator at most twelve.  Every bound is attained.
The `s=0, delta=1` row explicitly has finder success zero.

Therefore a joint adaptive bound on `Pr[Bad]` cannot be replaced by single-atom
marginals or by terminal soundness.

## 5. Queried quotient scope and resource necessity

Restricting the logged candidate to previously queried replication-quotient
classes is what transports the verifier query bound `q` into witness dimension
and ideal-validation cost.  If arbitrary unlogged identifiers are allowed, the
online trace no longer proves `|S|<=q` or a bounded `H|S` evaluation charge.

Likewise, omitting trace scan, candidate ideal evaluation, canonicalization, or
`Refute` rechecking makes the doubly efficient claim unsupported.  These are
resource-typing requirements rather than information-theoretic lower bounds,
but they are necessary for the stated complexity conclusion.

## 6. Minimal black-box online contract

Within this observation model, the v2.10 reduction needs exactly:

1. a public successful bound candidate call on actual noisy rejection;
2. candidate-only charged access to `H`;
3. mandatory ideal-answer `Refute` rechecking with `FAIL` on mismatch;
4. a joint adaptive path-error bound;
5. restriction to previously queried quotient classes; and
6. a complete extraction resource ledger.

Six registered counterfamilies remove these premises one at a time.  The first
four destroy Las Vegas success or validity; the last two destroy the dimension
or complexity transport.  All 12 positive v2.10 operating rows satisfy the
full contract and retain their exact success margins.

This is a minimality result for the **reduction architecture**, not an assertion
that every ASMP-3 task must literally implement the same log format.

## 7. Relation to the literal conjecture and typed successor

The literal v0.1 conjecture remains refuted by the earlier nonbinding-`Refute`
and fixed-interface counterfamilies.  The repaired typed successor remains
nonnormative and does not require the six clauses above.

The v2.3-v2.11 chain supplies a constructive characterization for the declared
online-contract subclass and proves why its clauses cannot be erased by a
black-box argument.  Extending that characterization now requires at least one
of:

- a normative successor adopting a concrete operational interface;
- a task-specific or non-black-box theorem that uses additional structure;
- a genuinely stronger joint-noise model or lower-bound technique; or
- attributable independent expert adjudication.

## 8. Completion boundary

This release closes the remaining online-extractor contract audit.  More marker
counts, probability denominators, or repeated copies cannot alter empty witness
intersections, the exact `k/N` identity, or the sharp construction in (2).

It does not resolve the normative `FIX`/`ADM` choice, prove universal interactive
communication or honest-prover lower bounds, cover correlation classes without
an adaptive path bound, or satisfy the external-review gate.

## 9. Novelty boundary

Observation partitions, unique-marker search, and the event bound are standard.
The contribution is their exact ASMP-3 synthesis: a zero-error information
frontier for noisy bound traces, proof that ideal candidate revalidation is
indispensable, sharp separation of soundness from extractability, and a
premise-by-premise minimality audit for the one-shot normal form.
