# ASMP-3 resolution disposition v2.6

## Executive disposition

Four statements must remain separate:

```text
named v0.1 Weak-Verifier Characterization Conjecture
  = refuted internally and exactly under both principal protocol readings

nonnormative registry negative-route mathematical conditions
  = satisfied internally

witness-transparent repaired subclass
  = conditionally characterized by v2.4-v2.5

full ASMP-3 classification program / community acceptance
  = not resolved / not established
```

This is the strongest disposition supported by the current evidence. Calling
the result merely “open” would ignore two exact counterfamilies. Calling ASMP-3
fully solved would ignore its definition-draft status, broader class obligations,
and `0/2` external-review gate.

## Named conjecture

The displayed v0.1 iff fails in both directions.

1. Under the frozen-message reading, v0.7 supplies a complete game in which all
   three displayed conditions hold but the optimal gap is exactly `(3/5)^d`,
   which vanishes. The honest strategy performs `Theta(T)` work and the semantic
   noise has persistent nonzero error `1/5`.
2. Under the literal nonbinding-`Refute` reading, v2.5 keeps a one-query,
   gap-`3/5` protocol fixed while replacing `Refute` by singleton, padded
   sound-complete, or empty decidable relations. The refutation dimension moves
   from `1` to `T` to infinity without changing admission or protocol value.

The earlier FIX-versus-ADM ambiguity no longer changes whether the displayed
universal iff is true under the literal v0.1 objects: frozen FIX has the v0.7
counterexample, while existential admission still cannot make an arbitrary
nonbinding frozen `r_R` necessary. An ADM repair that replaces `r_R` by a
best-interface binding invariant is the changed, nonnormative v0.2 successor,
not the displayed v0.1 sentence.

## Negative-route status

The machine-readable registry asks a negative result to retain:

- a separation or impossibility in the frozen message game; and
- an efficient honest prover and legal noise model.

v0.7 satisfies both internally. However, the same registry declares itself
nonnormative. The normative Markdown also warns that refuting one criterion does
not resolve a broader classification program unless the criterion is the entire
frozen statement.

The correct label is therefore `negative conjecture result`, not an
unqualified community-accepted resolution of the broader frontier.

## Repaired positive/converse result

For witness-transparent, ideal-simulable protocols with coupling loss below the
protocol gap, v2.5 extracts a randomized finder with success `1-s-delta`,
dimension at most the original query budget, and fully charged simulation time.
v2.4 amplifies the finder and v2.3 constructs the canonical fresh-noise
challenge/refutation protocol.

This gives a two-way normal form for that declared subclass. It does not imply
that every unrestricted `WV-FIX` or `WV-ADM` protocol is witness-transparent or
admits efficient ideal simulation.

## Why this is not a full ASMP-3 resolution

The authoritative source describes v0.1 as a research-agenda artifact ready for
external definition review, not a settled prize specification. The following
remain open:

- a normative FIX/ADM and `Refute`-binding choice;
- a formal unrestricted class equality or complete invariant;
- universal interactive communication/query/honest-prover lower bounds;
- the full declared correlated-noise frontier outside registered subclasses;
- two independent expert reproductions, including one independent checker.

The current expert gate is exactly `0/2`, with `0/1` independent team checkers.

## Recommended label

Use:

```text
ASMP-3 v0.1 named conjecture: internally refuted, exact, independently machine-checked.
ASMP-3 repaired witness-transparent subclass: conditionally characterized.
ASMP-3 full classification / prize-style acceptance: not established.
```

Do not use “ASMP-3 fully solved” until the definition, universal scope, and
external acceptance layers are independently cleared.
