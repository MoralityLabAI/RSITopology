# ASMP-3 normative-closure reassessment and correction v2.19

## Corrected verdict

V2.18 does **not** prove that ASMP-3 is impossible to achieve and does not
complete a “resolve ASMP-3 or prove impossibility” goal.  Its valid content is
the following conditional lemma:

> If `FIX` and `ADM` are both legitimate completions, and soundness forbids
> excluding either legitimate completion, then no sound selector returns one
> of them uniquely.

The critical antecedent was not established.  In particular, v2.18 asserted
that `ADM` was clause-preserving after changing “frozen game” to “frozen within
the realized game.”  That qualifier is an interpretation favorable to `ADM`,
not a neutral consequence of v0.1.

The previous goal-completion conclusion is therefore withdrawn.  The v2.18
artifact remains reproducible historical evidence for the conditional lemma,
not an unconditional closure theorem.

## Source-order audit

The v0.1 text has this order:

1. the `Canonical mathematical setting` heading;
2. “For input length `n`, freeze” the decision relation, message order,
   stopping rule, atomic query language, oracles, and noise model;
3. transcript encodings, randomness, and adaptive query access “are part of the
   game”;
4. `Refute` is separately frozen;
5. only then does the `Weak-Verifier Characterization Conjecture` say that a
   task family “admits ... a protocol.”

Ordinary sequential scope therefore makes strict `FIX` the conservative and
natural reading: protocol algorithms operate inside the already specified
game.  This is stronger evidence for `FIX` than v2.18 acknowledged.

It is still not a formal entailment theorem.  V0.1 supplies no formal semantics
for its English, no explicit algorithm/interface quantifier, and no satisfaction
relation for candidate completions.  A machine harness can certify the source
order and token inventory; it cannot turn those facts into an authoritative
natural-language semantics.

## Why `ADM` is not certified clause-preserving

The typed successor introduces four objects absent from v0.1:

- a typed environment `E_n`;
- a game interface `G_n`;
- a declared class `Interfaces(E_n)`; and
- an admissible protocol package `Q_n=(G_n,Pi_n)`.

Those definitions make `ADM` a reasonable successor target.  They do not prove
that v0.1 already quantified that way.  The successor explicitly calls itself
nonnormative and says it does not amend the parent.  The correct v2.19 status is:

```text
ADM clause preservation = not established
FIX = conservative natural reading, not formally entailed
```

## Mathematical status under strict `FIX`

Two exact results survive the correction.

### Displayed sufficiency is false

V0.7 constructs a complete frozen parity game satisfying all three displayed
conditions:

- refutation dimension `d=Theta(log T)`;
- a uniform efficient honest refutation strategy; and
- single-atom noise profile at most `1/5`.

Nevertheless the exact optimal gap is

```text
(3/5)^d -> 0.
```

Thus the displayed sufficiency direction is false under strict `FIX`.

### Literal necessity is false

V2.5 holds a one-query gap-`3/5` protocol fixed while replacing the nonbinding
decidable `Refute` relation by singleton, padded sound-complete, and empty
variants.  The protocol value is unchanged while the displayed dimension is
respectively `1`, super-polylogarithmic, or infinite.  Thus the literal
necessity direction is also false.

Accordingly:

```text
strict-FIX displayed iff = internally refuted in both directions
```

This is a separation of the proposed criterion, not a proof that no weak-
verification class can be characterized.

## Why this is not full ASMP-3 resolution

The canonical two-sided rule says that refuting one proposed criterion does not
resolve a broader classification program unless that criterion is the entire
frozen statement.  ASMP-3 separately demands:

1. a formal protocol class and class equality, separation, or complete
   invariant;
2. a constructive adaptive protocol;
3. matching communication, semantic-query, and honest-work lower bounds;
4. a robust correlated-noise theorem; and
5. benign-encoding invariance with a full-answer macro firewall.

Existing packages solve substantial declared subclasses and exact resource
families, but not the unrestricted class.  A counterexample to the displayed
iff does not show those objectives are unattainable.  No theorem proves that a
replacement characterization cannot exist.

## Correct disposition

```text
v2.18 conditional selector lemma = valid
v2.18 completion of resolve-or-impossibility goal = withdrawn
ADM clause preservation = not established
strict-FIX displayed iff = internally false in both directions
unrestricted ASMP-3 classification = not established
ASMP-3 mathematical impossibility = not proved
prize-grade or community acceptance = not established; external gate 0/2
```

The strongest defensible operational conclusion is that v0.1 is not explicit
enough for prize-grade use.  A next version should either formalize strict
`FIX`, or publish `FIX` and `ADM` as separate problems.

## Claim boundary

This correction does not claim that further mathematical work should stop.  It
stops only the failed source-only selector/impossibility lane and further parity
sampling already subsumed by the symbolic v0.7 formula.  Work may continue on a
registered strict-FIX class, a new non-black-box structure theorem, uniform
resource bounds, or external reproduction.
