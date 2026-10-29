# ASMP-3 source-relative normative-closure impossibility theorem v2.18

## Result

The sealed ASMP-3 v0.1 text and the current authority record do not entail a
unique choice between the fixed-interface (`FIX`) and protocol-admissible
interface (`ADM`) readings.  Consequently, no source-only closure rule can be
both:

1. **entailment-sound**: it never excludes a completion that satisfies every
   explicit v0.1 clause; and
2. **decisive**: it returns exactly one of `FIX` or `ADM`.

This is a proof of source-relative semantic underdetermination.  It is not a
claim that a maintainer cannot make a normative choice.

## Objects and definitions

Let `S` be the ASMP-3 section of
`../AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md`, with its file hash sealed in the
producer artifact.  A **clause-preserving completion** of `S` supplies a typed
scope rule for the untyped phrase “a task family admits ... a protocol” while
retaining every explicit v0.1 game, resource, noise, and efficiency clause.

For the audited binary fork:

- `FIX`: the complete game interface `G`, including transcript encoding and
  atomic query language, is fixed before protocol algorithms are quantified;
- `ADM`: the environment and a declared class `Interfaces(E)` are fixed, and a
  protocol admission may choose `G` from that class; after the choice, all
  components of the realized game remain frozen.

A model-set claim is entailment-sound exactly when it contains every
clause-preserving completion.  A no-claim `ABSTAIN` action is epistemically safe
but is not closure.  A claim is decisive exactly when it names one mode.

## Lemma 1: the source leaves the scope rule untyped

The canonical setting says, in order:

- “For input length `n`, freeze” the decision relation, public-coin order and
  stopping rule, and atomic semantic-query language;
- admissible transcript encodings, randomness, and adaptive access “are part
  of the game”; and
- “A task family admits ... a protocol if and only if” the displayed
  conditions hold.

The text never types the relation between “freeze ... the game” and “admits a
protocol.”  In particular, it contains no quantifier equivalent to either
`forall G exists Pi` or `exists G in Interfaces(E) exists Pi`.  It names
neither `WV-FIX` nor `WV-ADM`.  This is a whole-section statement audit, not an
argument from the word `freeze` alone.

The absence matters because v0.1 itself says that changing quantifiers changes
the problem.  The later typed successor explicitly defines both modes and says
that it “does not decide v0.1 authorial intent.”

## Lemma 2: two incompatible clause-preserving completions exist

Construct `M_FIX` by applying all frozen-game clauses to `G` before selecting
the algorithms.  Construct `M_ADM` by applying those same clauses to the
realized `G` after a protocol package selects it from a declared interface
class.  Both constructions preserve:

- the decision relation;
- public-coin order and stopping;
- the atomic semantic-query language;
- transcript encoding, randomness, and adaptive access as game components;
- the verifier time, query, and transcript budgets;
- efficient honesty; and
- the complete nonzero noise model.

They differ only in the missing outer scope rule.  Their added axioms are
incompatible: `FIX` forbids protocol-time interface selection; `ADM` permits
it.  The producer records the obligations separately for both models, and the
clean-room checker reconstructs them without importing producer code.

## Lemma 3: the distinction changes a mathematical outcome

The exact v0.7 parity construction holds the task relation, semantic worlds,
oracle law, prover budget, and verifier resource scale fixed.  Under `G_fix`,
the best gap is

```text
(3/5)^d -> 0.
```

Under the admitted vector interface `G_admit`, the gap is

```text
3/5.
```

Thus the v0.1 displayed sufficiency criterion has a valid counterexample in
`M_FIX`, while the same witness is not a counterexample in `M_ADM`.  The fork
is material rather than terminological.

## Theorem: sound decisive source-only closure is impossible

Assume a source-only rule `C(S)` is entailment-sound and decisive.  Because it
is decisive, it returns either `{FIX}` or `{ADM}`.

- If `C(S) = {FIX}`, it excludes the clause-preserving completion `M_ADM`.
- If `C(S) = {ADM}`, it excludes the clause-preserving completion `M_FIX`.

Either case contradicts entailment soundness.  Therefore no such rule exists.
`BOTH` preserves both models but is nondecisive; `ABSTAIN` makes no normative
claim and is also nondecisive.  This exhausts the deterministic actions on the
audited binary fork.  QED.

## Randomized corollary

Suppose a forced-choice rule chooses `FIX` with probability `p`.  Its error is
`1-p` in `M_FIX` and `p` in `M_ADM`.  Hence

```text
max(p, 1-p) >= 1/2,
```

with equality only at `p=1/2`.  Randomization cannot create sound closure; its
best worst-completion error is exactly one half.  The harness exhaustively
checks every rational `p=k/n` for `1 <= n <= 64` as a finite witness and the
displayed inequality proves the general result.

## Authority-information corollary

Inside this audited two-mode fork, the zero-bit partition is `{FIX, ADM}` and
is nondecisive.  One authoritative binary scope choice partitions it into the
two singleton cells.  Thus one external normative bit is necessary and
sufficient *within this fork*.  This does not assert that all imaginable future
amendments form a two-element space.

## Current authority audit

Only v0.1 is authoritative for its own statement, and it supplies no selector.
The machine registry declares itself nonnormative.  The typed successor is a
nonnormative draft.  V0.7 proves the mathematical fork but disclaims authorial
intent.  V2.17 records `normative_definition=unclosed`.  The external gate is
still 0/2.  Therefore no current authority channel adds the missing bit.

## Exact repair and stopping rule

Adding only the `FIX` scope axiom leaves `{FIX}`.  Adding only the `ADM` scope
axiom leaves `{ADM}`.  Adding both incompatible axioms leaves no model.  The
minimal repair is therefore one explicit authorized scope axiom, or a successor
that deliberately publishes both questions.

The internal search should stop here: more computation over the unchanged
source cannot entail an absent normative selector.  It should resume only when
the authoritative source changes, authorial evidence with declared authority is
introduced, or a new completion is proposed that challenges the audited model
class.

## Claim boundary

`FIX` remains the natural strict-freeze reading.  The theorem does not downgrade
that interpretive fact; it distinguishes naturalness from entailment.  Selecting
`FIX` as canonical is an amendment unless an authorized maintainer adopts that
scope rule.  The result neither recovers authorial intent nor proves that
normative choice is metaphysically impossible.
