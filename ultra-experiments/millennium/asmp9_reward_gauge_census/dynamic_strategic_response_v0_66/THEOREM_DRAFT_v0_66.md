# ASMP-9 dynamic response theorem draft v0.66

Status: **unregistered theorem development; not claim eligible**.

## 1. Frozen finite grammar

Let `S={0,...,n-1}` be finite latent states and `Q` finite queries.  A
deterministic response transducer supplies

```text
lambda:S x Q -> Y
delta:S x Q -> S.
```

At current state `s`, query `q` emits `lambda(s,q)` and changes the current
state to `delta(s,q)`.  This is read-then-update chronology.  A
write-before-read system is represented by putting its post-update response
directly in `lambda`; chronology is part of the declared object.

The experimenter knows the transducer but not the initial state.  Queries may
adapt to observed outputs.  The target is the initial state label, not merely
the final state reached by the experiment.

Let

```text
d:S x S -> nonnegative integers
```

be a frozen terminal distortion.  A leaf succeeds at budget `b` only if it
identifies one initial state `s0` and terminates in current state `s` with
`d(s0,s)<=b`.

The special cases are:

- unconstrained identification: `d=0` everywhere;
- exact terminal restoration: `d(s0,s)=1{s0!=s}` with budget zero.

Terminal restoration is weaker than pathwise noninterference.  The latent
state may change transiently and later return.  No stronger interpretation is
authorized.

## 2. Labelled belief dynamics

After one observed history, retain the labelled belief

```text
B = {(initial state, current state)}.
```

Initial labels remain attached because the objective is to identify the
pre-experiment state.  For query `q` and output `y`, define the nonempty branch

```text
T_(q,y)(B)
  = {
      (s0, delta(s,q)):
      (s0,s) in B and lambda(s,q)=y
    }.
```

If a branch contains `(i,s)` and `(j,s)` with `i!=j`, those initial labels have
merged into one current state under the same observed history.  Every future
response is identical for them.

## 3. Exact least-fixed-point theorem

For distortion budget `b`, initialize

```text
W_0(b)
  = {
      {(s0,s)}:
      d(s0,s)<=b
    }.
```

Recursively define

```text
W_(k+1)(b)
  = W_k(b)
    union
    {
      B:
      there exists q such that
      every nonempty T_(q,y)(B) lies in W_k(b)
    }.
```

### Theorem 1

A labelled belief `B` admits an adaptive experiment of worst-case depth at
most `k` that identifies the initial state and terminates within distortion
budget `b` if and only if

```text
B in W_k(b).
```

### Proof

The claim is immediate at depth zero from the terminal definition.  For the
inductive step, an adaptive experiment chooses one root query.  Each possible
observed output produces exactly one labelled successor belief and must admit
a depth-`k` continuation.  Conversely, a query whose every branch is in
`W_k(b)` can attach the corresponding continuation tree to each output edge.

This is the standard adaptive experiment recursion with an ASMP-9
terminal-distortion predicate.

### Corollary 1: finite termination

For `n` initial labels, a labelled belief assigns each label either no current
state or one of `n` current states.  Thus at most

```text
(n+1)^n - 1
```

nonempty labelled beliefs exist.  The least fixed point terminates after
finitely many additions.  The implementation explores only beliefs reachable
from the registered initial set.

### Corollary 2: merge obstruction

Any branch containing two different initial labels at the same current state
is losing for every finite identification experiment, regardless of terminal
budget.  State synchronization without an earlier separating output can make
the final state certain while erasing the initial target.

## 4. Three distinct outcomes

The fixed point yields a total three-way classification:

```text
unidentifiable
  initial labels cannot all be separated;

identify_only_altering
  initial labels can be separated, but no experiment returns every branch to
  its initial state;

identify_and_restore
  one adaptive experiment both separates and terminally restores every branch.
```

The middle class is the dynamic failure mode omitted by static preference
elicitation: the protocol can truthfully report what the value state was while
leaving a different value state behind.

## 5. Pairwise separation is not enough

There is a three-state, two-query transducer in which every pair of initial
states is distinguished by one query, yet no adaptive experiment identifies
all three.

For query `x`, outputs split `{A}` from `{B,C}` and then merge `B,C`.  For
query `y`, outputs split `{C}` from `{A,B}` and then merge `A,B`.  Every state
pair has an immediate separating query, but either possible first query has
one irrecoverably merged branch.

Thus pairwise existence of different experiments is weaker than one globally
valid adaptive experiment.  This is a standard distinguishing-sequence
phenomenon, included to prevent an invalid ASMP-9 access criterion.

## 6. Reversible positive condition

### Theorem 2

Suppose:

1. an ordinary adaptive initial-state identifying tree exists;
2. every query transition used on a root-to-leaf path is a permutation of
   `S`; and
3. an inverse query word for the composed transition on each leaf path is
   available.

Then an identify-and-restore experiment exists.

### Proof

At an identifying leaf, both the initial state and the exact query path are
known.  Append the registered inverse word for that path's composed
permutation.  It returns the current state to the initial state.  Outputs
during restoration need not distinguish anything further because the initial
label is already known.

The condition is sufficient, not necessary.  A noninvertible transition may
still be harmless on a particular identified branch.

## 7. Sharp diagnostic fixtures

Four finite fixtures separate the claims:

1. **Read-only:** emit the current state and leave it fixed.  Identification
   and restoration both take one query.
2. **Read then reset:** emit the current state and map every state to zero.
   Initial state is identified in one query, but exact terminal restoration is
   impossible for nonzero states.
3. **Reset then read:** emit a constant and map every state to zero.  The final
   state is perfectly predictable, but the initial state is unidentifiable.
4. **Reversible probe:** emit the current bit and flip it.  One query
   identifies; a second application restores, so safe depth is two.

These distinguish measurement, destructive measurement, and construction.

## 8. Exhaustive finite census

Across every complete two-state, two-query deterministic transducer with
binary outputs—`256` machines total—the independent audit obtains:

```text
unidentifiable             64
identify_only_altering     40
identify_and_restore      152
```

Among the `64` machines whose two query transitions are both permutations:

```text
unidentifiable             16
identify_and_restore       48
identify_only_altering      0
```

For two states every permutation is self-inverse, so this is an exhaustive
finite check of Theorem 2 in the inverse-closed case.

## 9. Relation to v0.65

Version v0.65 assumed one static strategic type and priced consequence access.
Version v0.66 changes the object: a query is simultaneously a read and a write
on the latent target.  A rich transcript can therefore:

- reveal an initial value and alter it;
- erase all initial information while creating a stable final value; or
- identify and restore under a declared reversible access class.

These are different estimands and must not be pooled.

## ASMP-9 consequence

A complete value-identifiability statement must name:

1. whether the target is initial, terminal, or path-valued;
2. whether responses are emitted before or after each update;
3. which update law is known, estimated, or adversarial;
4. the permitted terminal or pathwise disturbance; and
5. whether one global adaptive experiment exists, rather than a separate
   experiment for each pair of hypotheses.

Without those choices, "elicitation identified the value" is not a
well-defined claim.

## Claim boundary

The fixed-point construction and state-identification ingredients are
classical.  Version v0.66 does not cover unknown or stochastic transitions,
strategic model choice, continuous states, pathwise noninterference,
approximate identification, multiple agents, empirical human/model dynamics,
or the moral validity of the distortion.  It does not resolve ASMP-9.
