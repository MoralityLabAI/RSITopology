# ASMP-3 v0.3 resolution-obligation matrix

## Adjudication

```text
canonical_conjecture_status = conditional_obstruction_major_revision
protocol_quantifier_status = unresolved
complete_game_specification_status = missing
broader_repaired_program_status = open
empirical_resolution_claimed = false
```

## Negative-resolution requirements

| Frozen registry requirement | Evidence | Adjudication |
| --- | --- | --- |
| `separation_or_impossibility_in_the_frozen_message_game` | `INTERFACE_DICHOTOMY_THEOREM_v0_3.md`; stipulated parity-only grammar; exact nonbinding dimension rescaling; exact conditional gap `(3/5)^d -> 0` | **Conditional only:** legality and quantifier order of the restrictive grammar remain unresolved |
| `efficient_honest_prover_and_noise_model_must_remain_in_scope` | Honest advocate computes a `T`-leaf formal XOR trace in `Theta(T)` and explicitly lists the `d=log2(T)` semantic set in `O(d log d)=O(log T log log T)` bit time; noise has nonzero marginal `1/5`, a complete dependence law, and a constructive first-answer aggregator | Satisfied |

## Why the positive obligations are not separately required by this route

The repository permits a counterexample to the complete frozen universal
statement or a sharp impossibility as a two-sided resolution. This artifact
shows an exact obstruction inside one natural binding interpretation and a
separate syntactic instability in a nonbinding interpretation. The simulated
complexity review found that neither branch yet covers every canonical reading.

For completeness, the positive obligations fail in exactly the places exposed
by the theorem:

| Positive obligation | v0.3 finding |
| --- | --- |
| Formal complexity class | The verifier/`Refute` interface is unbound, so class membership is not determined by the displayed objects |
| Constructive protocol | Existing debate protocols do not repair an arbitrary nonbinding or joint-noise `Refute` predicate |
| Soundness and completeness | Single-atom constant advantage composes to a vanishing joint gap in the binding countermodel |
| Matching lower bounds | The countermodel is information-theoretic: its total-variation gap is optimal for every test |
| Robust noise theorem | Exact nonzero persistent-error law disproves the displayed single-atom-to-protocol implication |
| Encoding invariance/no full-answer atom | Meaning-preserving synonyms rescale `r_R` without placing a full answer in any atom |

## Independent-checkability status

- Producer: exact `Fraction` arithmetic plus exhaustive parity-class
  enumeration.
- Independent verifier: separate JSON consumer that does not import the
  producer and recomputes binomial tails, total variation, replica minima, and
  canonical-text closure checks.
- Independent Fourier verifier: separate channel-eigenvalue certificate that
  does not import either the producer or enumerative verifier.
- Review-gate verifier: validates receipt schema, release hash, distinct
  identities, required review tracks, verdict, and material-issue status.
  Synthetic fixtures prove both acceptance and rejection paths; live status is
  `0/2`.
- Simulated ultra review: probability core accepted conditionally; complexity
  and game semantics returned `major_revision`.
- External expert review: not yet obtained and not ready to solicit until the
  complete-game and protocol-quantifier gaps are repaired.

## Repair boundary

A successor must freeze:

1. whether and how verifier decisions are constrained by `Refute`;
2. soundness, completeness, and maximality/quotient axioms for `Refute`;
3. bit-cost accounting for a refuting set and its atom descriptions;
4. conditional error control after adversarial atom selection; and
5. a joint amplification invariant for the entire refutation predicate.

Those additions change load-bearing objects or quantifiers and therefore form a
new problem version rather than a threshold amendment to v0.1.
