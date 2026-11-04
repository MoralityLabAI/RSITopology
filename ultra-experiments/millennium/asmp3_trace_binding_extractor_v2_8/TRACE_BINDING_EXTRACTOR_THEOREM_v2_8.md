# ASMP-3 trace-binding extractor theorem v2.8

## Status and scope

```text
result_status = operational Refute-binding compiler and finder extractor
parent_result = ASMP-3-ADAPTIVE-TRANSCRIPT-COUPLING-v2.7
supporting_results = ASMP-3-WITNESS-TRANSPARENT-NORMAL-FORM-v2.5, ASMP-3-HONEST-SEARCH-BARRIER-v2.1
interface_mode = WV-FIX with trace-complete operational binding
changes_parent_problem = false
```

This theorem derives v2.5 witness transparency from a checkable implementation
contract. It does not infer that contract from the typed successor's weaker
phrase “rejection attributed to a local refutation.”

## 1. Trace-complete operational binding

Instrument an ideal-semantic verifier execution with canonical events:

```text
QUERY(class_id, ideal_answer)
REFUTE_CALL(tau, S, b, result)
TERMINAL(accept | reject)
```

The implementation is trace-completely bound when:

1. every semantic class in `S` was queried earlier on the same execution;
2. `S` is sorted, duplicate-free, and replication-quotiented;
3. `b` equals the logged ideal answers on `S`;
4. every terminal rejection is guarded by a successful declared
   `Refute(tau,S,b)` call; and
5. a purely formal rejection uses a successful empty-`S` call.

Failed calls may occur, but cannot authorize rejection. No event may occur after
the terminal instruction.

An implementation that already calls `Refute` can emit this log without
changing its decision distribution. The additive cost is the canonical call
record and a linear trace write/scan.

## 2. Extraction theorem

### Theorem 1

From any trace-completely bound ideal rejection, scan backward to the last
successful call and return its canonical `(S,b)`. Then:

```text
Refute(tau,S,b) = true,
|S| <= q,
extractor time
  <= C_honest + V + q Eval_H + TraceScan + Canonicalize.   (1)
```

### Proof

The validator has already checked that the logged call is the declared relation
evaluated on canonical classes and their ideal answers. The rejection guard
ensures at least one such call exists. Every returned class was queried, so at
most `q` distinct classes occur. Replaying the honest critic and verifier,
evaluating at most `q` ideal atoms, scanning the bounded trace, and
canonicalizing the call gives (1). QED.

Thus trace-complete binding implies v2.5 witness transparency constructively;
it need not be assumed again.

## 3. Composition with adaptive fresh noise

Under v2.7 fresh post-history replication blocks,

```text
delta_q <= 1-(1-e_d)^q.
```

If noisy false acceptance is at most `s`, ideal replay rejects and the trace
extractor succeeds with probability

```text
alpha >= 1-s-delta_q.                              (2)
```

Twelve exact compositions derive positive margins while charging block queries,
honest replay, ideal atom evaluation, trace scan, canonicalization, and witness
serialization. The only remaining normal-form premise in these rows is
efficient ideal-semantic replay with the honest role's declared information.

## 4. Exhaustive trace compiler

The producer enumerates more than 100,000 ideal trace programs over two through
five semantic classes. It crosses every world, vector claim, query sequence of
length at most three, and subset of distinct queried classes. Every valid
rejection yields exactly the logged witness; no witness exceeds the query
budget. Formal malformed transcripts separately exercise the empty witness.

Ten mutant traces test unbound rejection, unqueried classes, nonideal answers,
duplicate/unsorted witnesses, forged call results, terminal-order violations,
failed-only calls, missing terminals, and unknown instructions. Every mutant is
rejected by both producer and clean-room validator.

## 5. Decision-only firewall

An extensional label saying “the verifier is binding” is insufficient. In the
v2.1 unique-marker family, every false world can produce the same terminal bit
`reject` while requiring a different singleton witness. An extractor that sees
only that bit has worst-world success at most `1/N`; with `q` ideal atom probes
the exact bound is `q/N`.

The trace log changes this because it exposes the successful call inputs. It is
therefore a material operational contract, not bookkeeping that follows from a
decision bit.

## 6. Relation to the typed successor

The typed successor requires that any rejection *attributed* to a local
refutation use the declared relation. Trace-complete binding strengthens this in
two ways:

- every rejection, including formal rejection, has an explicit successful call;
- the call inputs are efficiently recoverable from the execution trace.

Without those clauses, the successor's binding sentence alone does not prove an
extractor. A future normative version must choose whether this stronger
operational rule is part of `WV-FIX`.

## 7. Completion boundary

For trace-completely bound, ideal-simulable protocols under v2.7 fresh blocks,
the v2.3-v2.8 chain now derives the quotient witness, randomized finder,
adaptive coupling, noise amplification, message, and query resources.

Still open are protocols lacking explicit call traces, roles unable to replay
ideal semantics efficiently, persistent/adversarial correlated noise, universal
interactive lower bounds, the normative FIX/ADM choice, and external review.

## 8. Novelty boundary

Proof logging and execution-trace extraction are standard. The contribution is
their precise ASMP-3 role: an operational binding axiom, exact witness/query
resource transport, adversarial mutant firewall, decision-only impossibility,
and composition with the adaptive noisy normal form.
