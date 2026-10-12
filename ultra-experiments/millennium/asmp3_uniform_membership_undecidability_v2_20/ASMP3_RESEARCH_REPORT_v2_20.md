# ASMP-3 research report through v2.20

## Executive summary

ASMP-3 is not unconditionally resolved, but the principal mathematical block
has been narrowed substantially. The research now establishes three exact
layers:

1. supplied finite fixed-interface games have an exact terminal-law frontier,
   computable through rational LP or sequence form;
2. several constructive, noise, encoding, and resource subclasses have exact
   theorems and matching harnesses; and
3. membership in a newly registered arbitrary-program strict-FIX class,
   `WV-FIX-UCOMP`, is undecidable and its positive index set is not recursively
   enumerable.

The third result is the important advance in v2.20. For a machine `e`, the
package builds a uniform family whose exact gap is `3/5` at every depth iff
`e` never halts, and is eventually zero if `e` halts. The construction retains
fixed vector messages, one local semantic query, `BSC(1/5)` noise, an efficient
honest prover, and `polylog(T)` weak-verifier resources.

This is a candidate negative resolution only under a representation premise:
v0.1's “associated frozen uniform decision family” must include arbitrary
computable task-family generators. The source allows undecidability as a route
but does not freeze that representation. External acceptance remains absent.

## 1. The problem being studied

ASMP-3 asks which tasks admit constant-gap oversight by a much weaker verifier
using few noisy human-semantic judgments against adaptive, obfuscating provers.
The source freezes a relation, message order and stopping rule, atom language,
semantic oracle and complete noise model, and intends verifier time, query
count, and transcript length to be `polylog(T)`. It separately requires an
efficient honest strategy and prohibits hiding full verification in one atom.

The displayed v0.1 conjecture proposes three conditions involving local
refutation dimension, efficient honest refutation search, and noise
amplification. A complete positive resolution additionally demands a formal
class, constructive protocol, matching resource lower bounds, a correlated
noise theorem, and encoding invariance.

## 2. Results before v2.20

### 2.1 The displayed iff is false under strict FIX

V0.7 gives a frozen parity family satisfying the displayed local-dimension,
honest-search, and marginal-noise conditions while its exact gap decays as
`(3/5)^d`. This refutes sufficiency in the fixed interface. A separate
nonbinding-`Refute` construction refutes necessity. Thus the literal displayed
criterion is internally refuted in both directions.

This does not characterize the broader weak-verification class. If protocol
admission may add vector messages, the same parity task has a one-query gap of
`3/5`; that is why `FIX` versus `ADM` must not be blurred.

### 2.2 Exact finite game frontier

V0.8 proves that for finite truthful terminal laws `H` and false terminal laws
`F`, the optimal terminal-selection gap is

```text
distance_TV(conv(H), conv(F)).
```

V0.9 converts rational H-polytopes to exact LP certificates. V1.0--v1.3 bridge
the result through realization flows, perfect-information games, matrix games,
and perfect-recall sequence form. These results exactly settle supplied finite
games in their declared scopes.

### 2.3 Noise, construction, encoding, and resources

V1.4--v1.9 separate marginal accuracy from joint selected-path risk and prove
exact amplification/composition results under explicitly registered dependence
models. V2.0 supplies benign-encoding and replication-quotient checks.

V2.1--v2.17 develop an online trace-extraction subclass and an unstructured
unique-marker family. The repaired online subclass is constructive and
black-box minimal under its six-clause contract. The marker family has exact
search, transcript, and adaptive-query frontiers through arbitrary public-coin
rounds and bounded soundness:

```text
C* - s = (1-s) min(1,Kq/N).
```

These are strong subclass theorems, not a universal cross-task
characterization.

### 2.4 The v2.18 error and v2.19 correction

V2.18 promoted a conditional set-theoretic selector lemma into a claimed
normative impossibility. The promotion depended on treating an `ADM`
interface-selection object as clause-preserving, but that premise was encoded
rather than semantically proved. The attached critique correctly identifies
this failure.

V2.19 withdrew the overclaim. Its safe state was: strict FIX is the conservative
natural reading but not formally entailed; the displayed iff is refuted; the
unrestricted classification and mathematical impossibility remain open.

## 3. V2.20: uniform membership undecidability

V2.20 registers `WV-FIX-UCOMP`, whose inputs are programs generating strict
fixed-interface families. Membership asks whether uniform in-interface
algorithms achieve a constant gap at every sufficiently large depth.

For machine `e` and depth `d`, the hidden world is a `d`-bit string `z`, and
the correct answer is its parity. Claim-labelled advocates send opposite-parity
vectors. The verifier receives one noisy coordinate answer. The ideal oracle
returns the actual coordinate until `e` halts within `d` steps and returns a
world-independent zero afterward.

While active, first-difference checking attains gap `3/5`; paired opposite
worlds and total variation prove no verifier can do better. After halting, the
same paired worlds produce identical verifier observations but require opposite
answers, so every verifier has gap zero. Hence

```text
G_e in WV-FIX-UCOMP  iff  e does not halt.
```

This proves undecidability, non-recursive-enumerability of positive membership,
and the absence of any sound-complete computably checkable finite positive
certificate system.

## 4. Why finite certification does not defeat the theorem

At any fixed `e,d`, bounded simulation determines which oracle is present. The
finite game then has an elementary exact certificate. The undecidable question
is whether a constant lower bound persists eventually across every depth of an
arbitrary program-generated family.

This cleanly explains why the extensive finite harness could continue passing
without resolving the uniform class: it certified rows, not the infinite
eventual-gap quantifier.

## 5. Current requirement ledger

- **Formal class/invariant:** exact for finite games; `WV-FIX-UCOMP` is formal
  and has an undecidable membership boundary. Parent representation remains
  unspecified.
- **Constructive protocol:** exact for the v2.20 positive reduction lane and
  the repaired online subclass, not universal.
- **Matching resources:** exact for the v2.20 family and marker families, not
  for an unrestricted cross-task class.
- **Robust noise:** exact for the v2.20 BSC and selected-path-risk subclasses,
  not every possible registered correlation class at once.
- **Encoding invariance:** proved for declared benign transformations, with a
  local-atom firewall in v2.20; the parent generator grammar remains open.

## 6. Resolution judgment

The current defensible statement is:

> Strict-FIX constant-gap membership is undecidable for arbitrary computable
> uniform generators, even under a one-query local interface with nonzero
> noise and efficient honest work. This is a candidate ASMP-3 negative
> resolution if that generator representation is accepted as the associated
> frozen uniform decision family.

The current indefensible statements are that all weak-verification
formulations are impossible, that no noncomputable characterization exists, or
that v0.1 has been unconditionally closed.

## 7. Recommended next action

Do not spend further compute enumerating bounded parity or marker fixtures to
settle the parent-level question. The productive next step is representation
closure: obtain an authoritative encoding specification, prove a reduction
from this registered class into it, or obtain external review accepting the
registered class. If a narrower structured representation is chosen, study
that restriction as a separate successor problem.

## 8. Reproducibility

The package contains a deterministic producer, an independently written
reconstructor, focused tests, a requirement audit, a prior-art boundary, and a
sealed release manifest. The producer exhaustively checks all opposite-parity
vector pairs through depth nine, symbolic local-atom witnesses through depth
64, resource rows through depth 64, and 432 finite halting-transition fixtures.
Those fixtures validate mechanics; the universal conclusion rests on the proof
above, not extrapolation from finite samples.

The final release run passed:

```text
producer gates = 10/10
clean-room checks = 10/10
focused tests = 12/12
full ASMP-3 regression = 470/470 across 41 test files
standalone ASMP-3 checkers = 37/37
external expert gate = 0/2; complete=false
```

## Conclusion

V2.20 does not repeat the v2.18 mistake. It proves a real undecidability theorem
under an explicit strict-FIX representation and labels the remaining premise.
The research program now has a sharp stopping point: finite games are exactly
certifiable, arbitrary computable uniform membership is undecidable, and only
the parent's missing representation choice prevents an unconditional
resolution claim.
