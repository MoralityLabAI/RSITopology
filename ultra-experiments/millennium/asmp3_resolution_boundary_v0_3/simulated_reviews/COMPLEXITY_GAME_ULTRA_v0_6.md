# Simulated ultra review: complexity and game semantics

```text
review_kind = model_generated_internal_stress_test
qualifies_as_external_expert_receipt = false
verdict = major_revision
material_issue_found = true
```

The conditional parity-channel theorem is credible, but the release does not
yet prove that its parity-only transcript projection is the complete canonical
game.

## Decisive objections

1. The canonical conjecture says that a task family “admits” a protocol. If that
   quantifier ranges over transcript encodings/protocols, the binding
   counterfamily admits a richer constant-gap protocol: each advocate sends
   the `d=log2(T)` semantic bits, the verifier chooses a differing coordinate,
   and one semantic query selects the truthful value with gap `3/5`. The current
   countermodel excludes this only by making per-atom claims illegal.
2. The release does not define one complete family `G_n`: input domain,
   `R_n`, `T(n)`, non-power-of-two padding, exact message alphabet and canonical
   serialization, round machine, stopping rule, payoff, information sets,
   malformed/abort behavior, and the verifier/prover oracle access.
3. The proof of `r_R=d` enumerates static false-parity claims, not every false
   admissible transcript required by the canonical max-min definition.
4. The one-level XOR lemma does not establish one uniform honest strategy
   against randomized, adaptive, equivocating, malformed, and aborting
   strategies, nor specify how the honest prover learns the ideal semantic
   facts.
5. The total-variation computation is over the noisy answer vector. A full
   theorem needs a noninterference lemma covering every message, coin, query
   label, encoding, stopping event, alias, ordering, and input observation.
6. The replica branch must establish that registered replicas are distinct
   members of `A_n` counted by `S`, rather than repeated evaluations of one
   atom.
7. The top-level completion obligations ask for the full characterization
   program. The current result is a conditional refutation of one displayed
   criterion, not yet an unqualified ASMP-3 resolution.

## Simulated answers to questions 1-6

1. Frozen grammar legal: `unclear`.
2. `r_R=log T`: `unclear` outside the reduced transcript class.
3. Uniform honest strategy against every legal strategy: `no proof supplied`.
4. Complete-transcript TV reduction: `unclear`.
5. Nonbinding replica construction legal: `unclear`.
6. One countermodel resolves full v0.1: `no` on the present formalization.

## Required repair

Freeze a complete game, prove both quantifier orders or select the canonical one
with authoritative scope justification, prove `r_R` and the honest-strategy
claim over every admissible transcript/strategy, and prove full-transcript
noninterference. Only then should genuine external review begin.
