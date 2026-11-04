# ASMP-9 controlled physical target-interface result v0.80

## Verdict

```text
finite_sample_target_recovery_not_established
```

The prospectively registered instrument was valid and replay-identical. The
fixed sequence stopped at R0 because the maximum absolute recovered-margin
error was `0.24483317010653805`, above the frozen `0.15` threshold.

ASMP-9 remains unresolved.

## Chronology and integrity

- prereveal commit:
  `231e7d3f618c97c4c705e5f72bd0706007c349a5`;
- prereveal commit time: `2026-07-29T21:27:52-04:00`;
- execution receipt creation: `2026-07-29T21:28:42-04:00`;
- registration SHA-256:
  `9afc80afa01d1fe3d6365a8fe4f65155abd8f12eead0f7a3deddf3e879a78df9`;
- all registered source hashes matched before execution;
- primary and replay rows were byte-identical; and
- primary and replay results were byte-identical.

## Fixed-sequence decisions

| Gate | Decision | Evidence |
|---|---|---|
| W0 | `pass` | shaping targets matched; non-gauge targets changed; both deltas had exact squared norm `2` |
| I0 | `pass` | primary/replay rows and results byte-identical |
| R0 | `fail` | maximum absolute margin error `0.24483317010653805 > 0.15`; all signs correct |
| L0 | `not_evaluated` | sequence stopped at R0 |
| M0 | `not_evaluated` | sequence stopped at R0 |

No downstream gate is promoted from its raw diagnostic.

## R0 details

All 20 context/arm margin estimates had the correct sign. The largest errors
were:

| Context | Arm | Target | Estimate | Absolute error |
|---|---|---:|---:|---:|
| `holdout_low` | `base` | -0.25 | -0.4948331701 | 0.2448331701 |
| `construction_high` | `nongauge_plus` | 2.75 | 2.5137844163 | 0.2362155837 |
| `holdout_low` | `nongauge_minus` | -2.25 | -2.4337675814 | 0.1837675814 |

The failure is therefore not a sign-classification failure. It is a uniform
cardinal-margin accuracy failure under the registered estimator and sample
budget.

## Secondary raw diagnostics

These values were computed by the runner but are **not gate decisions**:

- maximum empirical base-versus-shaped probability difference:
  `0.072265625` against the L0 threshold `0.12`;
- registered Hellinger union bound: `0.13200188923003764`;
- accumulated TV penalty at `epsilon=1e-5`: `0.01524271249739828`; and
- raw robustified bound: `0.14724460172743592` against the M0 threshold `0.05`.

Thus even if R0 had passed, the frozen raw M0 diagnostic would not have cleared
its threshold. Because the sequence stopped at R0, M0 remains
`not_evaluated`, not `fail`.

## Interpretation

The run validates three narrower facts:

1. the target/gauge construction is internally well-posed;
2. the acquisition and replay instrument is deterministic; and
3. the selected response channel carries the correct target sign in all
   registered cells.

It does **not** establish the registered cardinal recovery claim at 512 samples
per query. The negative result also demonstrates the distinction introduced in
v0.77: population separation of known response laws does not guarantee that a
particular finite-sample decoder clears a uniform practical-error gate.

## Successor constraint

Any successor must be a new version with:

- fresh seeds and a disjoint outcome artifact;
- a prospectively frozen sampling/allocation rule;
- either the same estimator with a justified larger sample budget or a new
  estimator justified from this burned run;
- R0 retained as a uniform cardinal-error target rather than replaced by sign
  accuracy; and
- M0 powered prospectively, since its v0.80 raw bound was also above threshold.

No v0.80 threshold or decision may be changed.

## Claim boundary

This is one controlled finite-MDP softmax response channel. It is not evidence
about human or language-model values, the validity of softmax planning as a
behavioral law, open-ended environments, moral adequacy, or ASMP-9 resolution.
