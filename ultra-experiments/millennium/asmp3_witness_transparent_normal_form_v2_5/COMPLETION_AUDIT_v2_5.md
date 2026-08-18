# ASMP-3 witness-transparent normal-form completion audit v2.5

## Newly closed

```text
witness-transparency contract = frozen
ideal-simulation contract = frozen
decision-coupling margin = frozen
finder extraction alpha >= 1-s-delta = proved
dimension bound r<=q = proved
one-shot extraction time = fully charged
restart amplification time = fully charged
36 extraction/resource rows = certified
10,625 binary coupling tables = exhaustively audited
held-out coupling denominators 17..20 = confirmed
extraction lower-bound tightness = certified
canonical replacement via v2.4 = proved for declared subclass
literal nonbinding Refute necessity counterexample = certified
sound-complete padded Refute counterexample = certified
v0.7 frozen sufficiency counterexample = cross-checked
literal displayed iff = separated in both directions
```

## Still open

```text
unrestricted WV-FIX normal form without witness transparency = open
protocols lacking efficient ideal simulation = open
protocols with coupling loss at least their gap = open
interactive/adaptive communication lower bounds = open
WV-ADM interface infimum and attainment = open
universal natural-task characterization = open
v0.1 literal-versus-repaired normative scope = open
external mathematical review = absent
```

## Resolution effect

For the witness-transparent, ideal-simulable, positive-coupling-margin subclass,
the v2.5 extraction theorem and v2.4 construction give a two-way operational
normal form with explicit resource transport. For literal v0.1, the displayed
iff itself is false in both directions.

## Non-overclaim rule

The full problem asks for more than refuting its first proposed invariant. This
release does not characterize unrestricted WV-FIX or WV-ADM and does not decide
which repaired scope should replace the underbound literal definition.
