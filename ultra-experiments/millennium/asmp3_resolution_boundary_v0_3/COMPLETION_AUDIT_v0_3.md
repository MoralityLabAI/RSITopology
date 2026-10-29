# ASMP-3 v0.3 completion audit

## Current adjudication

The release has an exact parity-channel obstruction under a stipulated binding
grammar. A simulated ultra complexity review found a material gap between that
stipulation and the canonical existential phrase “admits a protocol,” plus a
missing complete interactive-game specification. External acceptance review is
therefore on hold rather than merely pending.

```text
conditional_probability_lower_bound_complete = true
complete_canonical_game_specification = false
protocol_quantifier_scope_resolved = false
mathematical_countermodel_complete = false
independent_machine_verification_of_reduced_channel = true
independent_expert_checks_obtained = 0
required_independent_expert_checks = 2
goal_status = blocked_major_revision_then_external_review
```

## Requirement-by-requirement evidence

| Requirement | Authoritative evidence | Audit |
| --- | --- | --- |
| Exact problem version | `ASMP-CANDIDATE-SET-v0.1`; named Weak-Verifier Characterization Conjecture | Present, though the set remains a definition draft |
| No narrow-subclass substitution | The restrictive grammar may be one protocol rather than frozen task data | **Unresolved** |
| Frozen message-game separation | Explicit stipulated grammar and least-favourable parity pair in `INTERFACE_DICHOTOMY_THEOREM_v0_3.md` | Conditional theorem proved; canonical scope unresolved |
| Efficient honest prover | `Theta(T)` formal XOR evaluation plus `O(log T log log T)` bit cost for the explicit semantic set | Proved constructively |
| Legal nonzero noise | Marginal `1/5`; persistent within-atom correlation; independent between atoms; no adaptivity | Fully specified |
| Condition 1 retained | `r_R=log2(T)` in the reduced transcript class | Full admissible-transcript universe missing |
| Condition 2 retained | Fixed set found/listed in `O(log T log log T)` bit time; one-level formal lemma checked | Full uniform-strategy proof over all legal/malformed/adaptive transcripts missing |
| Condition 3 retained | First-answer aggregator gives `a_H(k)<=1/5` for every `k>=1` | Proved |
| No constant protocol gap | Exact minimax total variation `(3/5)^d -> 0` for the reduced parity transcript | Full-transcript noninterference not yet proved |
| No full-answer semantic atom | The counterfamily starts at `d>=2`; each atom is one indexed bit with radius-one locality | Explicit |
| Encoding-invariance audit | Nonbinding synonymous replicas rescale `r_R` from 1 to `m` | Exact counterexample |
| Empirical firewall | No samples, benchmarks, fitted curves, or real-judge claim | Satisfied |
| Certified computer assistance | `Fraction` producer, exhaustive enumerative verifier, and separate Fourier/eigenvalue verifier | Satisfied |
| Simulated ultra reviews | Probability core: conditional accept; complexity/game semantics: major revision | **Material hold** |
| Independent expert checks | Repository policy requires two end-to-end reproductions after repair | **Missing; not yet ready to solicit** |

## Verification receipts

- Producer gates: all pass.
- Independent enumerative verifier: all checks pass.
- Independent Fourier/eigenvalue verifier: all checks pass.
- Expert-review receipt validator: synthetic positive and negative fixtures
  pass; it requires two distinct tracks plus at least one hash-validated checker
  independently implemented by a review team. The live status artifact records
  `0/2` qualifying receipts, `0/1` qualifying external checkers, and
  `completion_gate_satisfied=false`.
- Targeted tests: all pass.
- Existing ASMP-3 regression suite: must remain green before release.
- Candidate-set validator: known checkout-baseline failure on the sealed
  millennium `README.md` hash; the tracked file is unmodified by this work.

## Hostile-objection audit

### “The provers can just reveal every ideal semantic bit.”

Not in the stipulated grammar. Whether the canonical word “admits” allows a
richer encoding is precisely the unresolved material issue. If it does, the
advocates can send all `d` bits, a differing coordinate can be queried once,
and this counterfamily has gap `3/5`.

### “The verifier can repeat each query.”

All repetitions of atom `i` reuse the same latent `E_i`. Repetition produces no
new information. This is a legal complete correlated-noise law with marginal
error below one half.

### “The parity estimator may be suboptimal.”

The total-variation calculation is over the full observed vector and therefore
bounds every randomized decision rule. Exact enumeration independently matches
the closed form.

### “The prover budget is artificially inflated.”

The task includes a genuine `T`-leaf formal XOR computation. The honest
advocate evaluates it in `Theta(T)`; cross-examination makes only that formal
component cheap for the verifier. The semantic parity obstruction is then
composed with, not substituted for, the long computation.

### “This only attacks a malformed `Refute` relation.”

The binding relation is sound, complete, local at the atom level, and has
dimension `log T`. The failure is that a single-atom noise bound does not
control its joint predicate. The nonbinding replica construction separately
shows why an adequacy/quotient axiom is needed.

### “Existing debate theorems already solve this.”

They solve richer transcript games in which disagreements can be recursively
localized. That is exactly the interface missing from v0.1. Importing such a
game changes the frozen grammar or replaces the static `Refute` invariant.

## Release decision

Do not mark the thread goal complete. First define the complete game and settle
whether transcript grammar is frozen task data or existential protocol choice.
Then reseal and obtain two end-to-end expert reproductions. Further parity-grid
enumeration cannot settle the first layer, and model-generated reviews cannot
settle the second.
