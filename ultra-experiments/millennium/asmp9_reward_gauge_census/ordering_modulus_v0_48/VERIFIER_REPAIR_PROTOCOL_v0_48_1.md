# ASMP-9 v0.48.1 verifier-only repair protocol

## Trigger

The prospectively registered v0.48 scientific prediction failed while every
instrument-validity gate passed. The original independent verifier reproduced
the scientific payload, experiment rows, subset bounds, registration, and
source hashes exactly, but set `ok=false` solely because it required
`all(result.gates.values())`.

That acceptance rule incorrectly conflates:

```text
scientific prediction not established
```

with:

```text
instrument or replay invalid.
```

The original verifier and its failed receipt remain immutable.

## Frozen repair

The repair changes only independent-verifier adjudication.

Let the instrument gate set be:

```text
P0,S0,U0,E0,D0,L0,C0,A0,RESOURCE.
```

The repaired verifier accepts a replay exactly when:

1. registration hash matches;
2. every registered source hash matches;
3. scientific payload matches;
4. experiment rows match;
5. subset-bound rows match;
6. every instrument gate is true; and
7. the recorded status equals the deterministic gate mapping:

   ```text
   instrument failure
     -> invalid_ordering_instrument

   valid instrument and X0=true
     -> decision_dependent_evidence_ordering_established

   valid instrument and X0=false
     -> decision_dependent_ordering_not_established.
   ```

The repaired verifier does not change `X0`, any scientific value, artifact, or
registered prediction.

## Prospective restriction

This protocol is written after outcomes and cannot strengthen the scientific
claim. It may only distinguish a valid registered null from an invalid replay.
Any scientific recomputation mismatch fails the repair.

## Claim boundary

v0.48.1 is provenance plumbing. It creates no new mathematical or empirical
evidence.
