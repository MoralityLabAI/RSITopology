# ASMP-2 active-design census v0.2.2 result

## Decision

**VALID NEGATIVE — `active_design_not_supported`.**

The registered one-step minimax selector failed the frozen support criterion in all three deployment families. This rejects that selector as a generally efficient multi-step source-design policy in the registered degree-two, four-dimensional polynomial class. It does not reject active environment selection as a program.

## Registered results

All AUC values are the arithmetic mean of `R^2/11` over budgets 2 through 10; lower is better.

| Deployment family | Active AUC | Random median AUC | Space-filling AUC | Active improvement vs random | Active improvement vs space | Maximum normalized regret | Support gate |
|---|---:|---:|---:|---:|---:|---:|:---:|
| full cube | 0.80718 | 0.82508 | 0.78002 | +2.17% | -3.48% | 24.24% | fail |
| nonnegative sum | 0.80718 | 0.81187 | 0.78002 | +0.58% | -3.48% | 42.89% | fail |
| even parity | 0.60518 | 0.79585 | 0.62514 | +23.96% | +3.19% | 39.67% | fail |

The frozen family-level rule required at least 5% improvement over both median random and space filling, plus no more than 5% normalized regret relative to the globally minimal subset under the registered ten-decimal ordering contract. No family passed all three conditions.

## Mechanistic interpretation

The one-step objective is not a reliable proxy for the multi-step design objective in this finite class.

- For full-cube and nonnegative-sum threats, the active selector followed the same radius curve and was worse than geometry-only space filling over the scientific budgets.
- For even-parity threats, the active selector was meaningfully better than random, but its greedy path incurred large regret and missed the registered 5% advantage over space filling.
- At budget eight, the globally minimal even-parity design reached zero ambiguity while the greedy design retained `R^2 = 48/11 ≈ 4.364`.

The result motivates lookahead, exchange, or submodular-surrogate selectors rather than another claim for the frozen myopic rule. Such successors require new registrations.

## Instrument validity

- Complete source-subset census: 65,536/65,536.
- One-edge monotonicity checks: 1,572,864/1,572,864 passed.
- Exact-rational deterministic witnesses: 90/90 agreed with numerical scores.
- Signed coordinate reframings: 1,152/1,152 passed.
- Random sequences: 256, frozen seed root `20402026`.
- Independent verification: opposite-parent projector traversal reproduced the complete quantized census digest, selector curves, controls, and evidence label.
- Operational runtime: 41.98 seconds.
- Peak process RSS: 145,117,184 bytes.

## Version history and integrity

v0.2 exceeded its resource ceiling before emitting an outcome. v0.2.1 emitted after its total-wall ceiling and was quarantined without scientific inspection. v0.2.2 changed only resource measurement, inherited the scientific contract by hash, and completed within both margins.

- Preregistered v0.2.2 commit: `a3f0ce7b54e19cd3543469bc5382c509f65637ae`
- Result SHA-256: `a35d6e3a5a2aa5ba1063d3bb1419ca60c97950a03260f1b6460497667d3cd6a0`
- Receipt SHA-256: `79116283e172e7dbaf08ed0e86d7cb536f69bbc19b5db0f416e3ca8d6df95c5b`
- Verification SHA-256: `6da742100ddd524dceac6faab1455c0429f740d2f65bd0c9c75db073879c6abb`

## Claim boundary

This is one exhaustive finite numerical census with exact selected witnesses. It does not resolve ASMP-2, prove a semiparametric certification boundary, establish exact ordering inside numerical tie bins, supply noisy finite-sample guarantees, or show that active design is generally ineffective.
