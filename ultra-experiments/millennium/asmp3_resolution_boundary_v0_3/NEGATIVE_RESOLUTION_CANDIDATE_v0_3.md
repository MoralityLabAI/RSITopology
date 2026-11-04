# ASMP-3 v0.1 negative-resolution candidate

## Verdict

```text
named_characterization_conjecture = conditional_refutation_under_binding_frozen_grammar
canonical_protocol_quantifier = unresolved
complete_game_specification = missing
simulated_complexity_review = major_revision
broader_repaired_program = open
empirical_claim = none
external_acceptance_review = on_hold
```

The exact countermodel in `INTERFACE_DICHOTOMY_THEOREM_v0_3.md` satisfies all
three displayed conditions of the Weak-Verifier Characterization Conjecture
but has no constant-gap protocol in its stipulated binding parity-only message
game. This conditionally falsifies the conjecture's sufficiency direction when
admissible transcript encodings are frozen task data.

The simulated ultra complexity review identified a material unresolved
quantifier: if “admits a protocol” ranges existentially over message encodings,
the advocates may send all `d=log T` semantic values and the verifier can query
one differing coordinate, yielding gap `3/5`. The current release therefore
does not establish an unqualified v0.1 refutation.

The nonbinding branch separately proves that, without a verifier-interface
axiom, `r_R` is not a necessary or encoding-invariant protocol quantity.

## Binding countermodel in one table

| Frozen object | Choice |
| --- | --- |
| Prover budget | `T=2^d`, with `d>=2` |
| Nontrivial formal work | A `T`-leaf XOR computation, evaluated by the honest advocate in `Theta(T)` |
| Formal oversight | Local cross-examination in `O(log T)` messages |
| Semantic language | `d=log2(T)` indexed radius-one bits; no full-answer atom |
| Semantic refutation | All `d` answers are required; their parity must contradict the transcript claim |
| Honest semantic strategy | List the fixed `d`-atom set in `O(d)` word operations / `O(d log d)` bit time |
| Noise | One persistent `Bernoulli(1/5)` flip per atom; independent between atoms |
| Registered replications | Perfectly correlated within an atom |
| Single-atom aggregator | Return the first answer; error `1/5` |
| Best joint gap | `(3/5)^d = T^log2(3/5) -> 0` |

Thus:

```text
r_R(T) = log2(T)                         condition 1 passes
honest refutation bits = O(log T log log T) condition 2 passes
a_H(polylog T) <= 1/5 = 1/2 - 3/10       condition 3 passes
constant protocol gap                    fails
```

The optimality statement covers every verifier in the frozen grammar, not only
majority or parity decoding. Holding the formal component fixed and averaging
uniformly over each ideal parity class produces two exact observed
distributions with total variation `(3/5)^d`. Prover messages are fixed by the
two advocated parities and the canonical all-indices set. Repeated queries add
no information because each atom reuses its latent flip. By the testing
variational bound, no decision rule has a larger worst-case gap. A pointwise
completeness-soundness gap `Delta` would survive averaging, forcing
`Delta<=(3/5)^d`; therefore no fixed positive `Delta` exists.

## Why this qualifies as the repository's negative route

This section records the intended route, not a completed adjudication. The
major-revision findings below must be resolved before the route can qualify.

The normative v0.1 document names one “Weak-Verifier Characterization
Conjecture.” The machine-readable registry allows negative resolution and
requires:

1. a separation or impossibility in the frozen message game; and
2. retention of an efficient honest prover and a legal noise model.

The countermodel is an asymptotic family in the stipulated message grammar, not a
finite benchmark. Its honest strategy performs genuine `Theta(T)` formal work,
and its nonzero correlated-noise law is completely specified. It therefore
does not obtain failure by deleting either required object.

The top-level two-sided policy warns that refuting one proposed criterion does
not settle a broader classification program unless it is the entire frozen
statement. This result is scoped accordingly: it refutes the only named
universal characterization in ASMP-3 v0.1. It does not claim that every
possible repaired characterization is impossible.

## Why the obvious repairs are new problem versions

Either repair changes a load-bearing object:

- Letting advocates transmit and cross-examine per-atom semantic values changes
  the frozen message grammar and the `Refute` interface.
- Replacing `a_H(k)` by a joint selection-conditional profile changes the
  conjecture's third condition and its quantifiers.
- Quotienting `Refute` by all semantically sufficient evidence changes `r_R`.

The repository policy explicitly states that changing objects, quantifiers, or
adversaries creates a new version.

## Reproduction

```powershell
python ultra-experiments/millennium/asmp3_resolution_boundary_v0_3/run_harness.py
python ultra-experiments/millennium/asmp3_resolution_boundary_v0_3/verify_result.py
python -m pytest ultra-experiments/millennium/asmp3_resolution_boundary_v0_3 -q
```

All decision quantities use exact rational arithmetic. Exhaustive
parity-class enumeration through `d=9` independently matches the asymptotic
closed form.

## Remaining acceptance boundary

The parity-channel certificate is internally exact and independently
machine-checked. The complete canonical game and protocol quantifier are not
yet settled, so qualifying external acceptance review is on hold. After that
material repair, the repository will still require two independent end-to-end
expert reproductions, including one independently implemented checker. Until
both layers are cleared, this artifact is a conditional obstruction, not a
community-accepted resolution or a graduated prize claim.
