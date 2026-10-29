# ASMP-3 online noisy-trace extractor theorem v2.10

## Status and scope

```text
result_status = one-shot protocol-to-finder normal form without strategy restart
parent_result = ASMP-3-ORACLE-PARAMETRIC-REPLAY-v2.9
supporting_results = ASMP-3-TRACE-BINDING-EXTRACTOR-v2.8, ASMP-3-ADAPTIVE-TRANSCRIPT-COUPLING-v2.7
interface_mode = WV-FIX with public trace-complete noisy rejection binding
changes_parent_problem = false
```

This theorem removes the restartability premise from v2.9's finder extraction.
It uses the single actual noisy interaction: extract the candidate named by a
bound noisy rejection, re-evaluate only that candidate under `H`, and return it
only when the declared `Refute` relation remains true.

Ideal replay remains a valid construction for restartable runtimes, but it is
not necessary for this one-shot normal form.

## 1. Online noisy-trace contract

Instrument the actual noisy verifier execution with the v2.8 canonical events:

```text
QUERY(class_id, decoded_noisy_answer)
REFUTE_CALL(tau,S,b,result)
TERMINAL(accept | reject)
```

The online contract requires:

1. the actual trace is canonical and available to the honest extractor;
2. every noisy terminal rejection is guarded by a successful `Refute` call;
3. the call uses only previously queried replication-quotient classes and their
   logged decoded answers;
4. the extractor can evaluate `H` on those candidate classes and call `Refute`;
5. a failed ideal revalidation returns `FAIL`, never the noisy candidate;
6. the adaptive probability that any decoded answer differs from `H` is at most
   the declared `delta_q`; and
7. interaction, tracing, ideal candidate evaluation, rechecking, and
   canonicalization are all charged.

The strategic kernels may be one-shot, stateful, and nonrestartable.  No
snapshot, rewind, seed recovery, or counterfactual ideal interaction is used.

## 2. Online extraction theorem

For a noisy execution trace, define `OnlineExtract` as follows:

```text
if the terminal decision is accept: return FAIL;
scan backward to the last successful bound Refute(tau,S,b) call;
evaluate b* = H restricted to S;
if Refute(tau,S,b*) is false: return FAIL;
return (S,b*).
```

### Theorem 1 (validity, dimension, and success)

Against a fixed false advocate strategy, suppose noisy false acceptance is at
most `s`, at most `q` quotient classes are queried, and the adaptive path-error
event `Bad` has probability at most `delta_q`.  Then `OnlineExtract` is a
Las Vegas-with-`FAIL` finder satisfying

```text
every non-FAIL output is a valid Refute(tau,S,H|S) witness,        (1)
|S| <= q,                                                         (2)
alpha >= 1-s-delta_q.                                             (3)
```

Its charged time is

```text
ActualInteraction + TraceWrite + TraceScan + Canonicalize
  + |S| Eval_H + RefuteRecheck.                                   (4)
```

### Proof

The algorithm returns only after directly evaluating `H|S` and rerunning the
declared decidable relation, proving (1).  No call may contain an unqueried
quotient class, so (2) follows from the semantic-query budget.

Let `R` be the event that the noisy execution rejects.  On `R` intersected with
`Bad`'s complement, every logged decoded answer equals its ideal answer.  The
successful bound call is therefore already a valid ideal-answer witness, so
the extractor succeeds.  Hence

```text
Pr[success]
  >= Pr[R and not Bad]
  >= Pr[R] - Pr[Bad]
  >= 1-s-delta_q.
```

The listed operations give (4).  QED.

The proof is pointwise in all stateful strategy behavior.  It never asks what
the strategy would have done under a counterfactual answer.

## 3. Exact probability audit and sharpness

Partition executions into five events:

```text
reject-good,
reject-bad-success,
reject-bad-fail,
accept-good,
accept-bad.
```

For rational probability denominator `m`, enumerate every five-part weak
composition of `m`.  Across denominators one through twenty, this gives

```text
C(25,5)-1 = 53,129
```

joint tables.  All satisfy

```text
Pr[success] >= Pr[reject] - Pr[Bad].                              (5)
```

There are 1,770 equality tables.  Denominators one through sixteen are the
registered audit; seventeen through twenty are held-out confirmation.  Thus
the subtraction in (3) is best possible given only noisy rejection and the
path-error probability.

## 4. Exhaustive adaptive noisy-trace compiler

For two and three semantic classes and query depths one through three, the
producer crosses every complete binary adaptive query policy, semantic world,
vector claim, and decoded-error pattern.  It covers:

```text
2,355 adaptive query policies,
1,144,000 noisy executions,
3,423,680 decoded semantic queries,
889,856 repeated-class executions,
999,904 noisy rejections.
```

The online extractor emits 499,952 valid witnesses and no invalid witness.  All
499,952 noisy candidates that fail ideal revalidation are contained as `FAIL`.
Every one of the 107,728 all-correct rejecting executions extracts
successfully.  Both producer and clean-room checker reconstruct the canonical
digest and all counts independently.

Formal malformed rejection is separately exercised with the v2.8 empty
witness; a well-formed accepting control returns `FAIL`.

## 5. One-shot erased-state family

The harness also instantiates `N` hidden-marker strategy states.  The strategy
uses its marker during the single interaction and erases it before termination,
so every post-interaction private state is identical and restart is unavailable.
The verifier first queries a gate and, on a correct gate answer, receives and
queries the marker.  A correct two-query path yields a bound rejection.

For independent decoded error `e`, the online extractor succeeds with

```text
(1-e)^2,
```

emits no invalid witness, and needs no post-run strategy state.  Eighteen rows
cross six marker counts with `e` in `{1/10,1/5,1/3}`.  This establishes that
one-shot state erasure blocks counterfactual replay but does not block online
trace extraction.

## 6. Why ideal revalidation is necessary

A noisy successful call need not be a valid ideal witness.  In a unique-marker
world, noise can forge a mismatch at a decoy class while the genuinely false
claim lies elsewhere.  Trusting the logged noisy answer would emit an invalid
witness.  Re-evaluating `H` at the decoy detects the failure and safely returns
`FAIL`.

Eight contract mutants test decision-only logging, binding only ideal traces,
unqueried candidates, missing `H` access, trusting the noisy call, emitting a
failed candidate, marginal-only noise control, and hidden validation costs.
Every mutant is rejected.  Both one-shot stateful and restartable positive
controls are accepted.

## 7. Composition with v2.7 and v2.8

Under v2.7 fresh post-history blocks,

```text
delta_q <= 1-(1-e_d)^q.
```

All 12 v2.8 operating rows retain the same exact positive finder margin.  The
v2.10 ledger replaces ideal replay, seed sampling, and strategy restart with the
actual interaction plus candidate-only ideal revalidation and `Refute`
rechecking.  No unexecuted counterfactual branch is charged or assumed.

Consequently v2.9 restartable replay is sufficient but not necessary.  Public
trace-complete binding on actual noisy rejections is the more general
operational route.

## 8. Relation to the typed successor

The current typed successor requires only that rejections *attributed* to local
refutation use `Refute`.  It does not require every noisy rejection to expose a
public successful call, grant the honest role candidate-only `H` access, or
freeze a conditional adaptive path-error bound.  Those clauses therefore
remain explicit premises, not consequences of `WV-FIX` admission.

A normative successor can adopt the one-shot normal form by specifying:

- public trace-complete binding for actual noisy executions;
- charged ideal evaluation of the logged candidate classes;
- mandatory `Refute` rechecking with `FAIL` on mismatch; and
- the joint adaptive error law needed to bound `Pr[Bad]`.

## 9. Completion boundary

For trace-completely bound actual executions with candidate-only `H` access and
v2.7 fresh blocks, the v2.3-v2.10 chain now handles one-shot and stateful
strategies without ideal replay.  It derives the witness, randomized finder,
adaptive noise loss, amplification, and all registered resources.

Still open are protocols without public bound rejection traces, honest roles
without candidate `H` access, persistent/adversarial correlation outside the
registered path bound, universal interactive lower bounds, the normative
`FIX`/`ADM` choice, and attributable external review.

## 10. Novelty boundary

Validate-after-noisy-execution and the event inequality are elementary.  The
contribution is their ASMP-3 synthesis: a one-shot protocol-to-finder normal
form, exact Las Vegas safety under semantic errors, removal of restartability,
complete adaptive/error enumeration, sharp probability tables, and explicit
state-erasure coverage.
