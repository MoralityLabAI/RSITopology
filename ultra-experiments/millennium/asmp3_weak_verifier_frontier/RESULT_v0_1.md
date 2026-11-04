# ASMP-3 correlated-noise weak-verifier result v0.1

## Verdict

`exact_finite_correlation_diversity_frontier_established`

All seven registered gates passed under exact rational arithmetic. This is an
instrument result for the frozen semantic-bit game, not evidence that a real
weak verifier can judge superhuman work.

## Headline result

The marginal error of every weak judgment was fixed at `1/5`. A transcript was
accepted or rejected by strict majority after `q` judgments. The operational
criterion required both false acceptance and false rejection to be at most
`1/20`.

Under independent errors, the first registered query budget to clear the
criterion was `q=7`:

| independent query budget | exact error | admissible? |
|---:|---:|---|
| 1 | `1/5` | no |
| 3 | `13/125` | no |
| 5 | `181/3125` | no |
| 7 | `521/15625` | yes |
| 9 | `7649/390625` | yes |

For nine calls to one exchangeable verifier family, the registered correlation
boundary lay between intraclass correlations `1/20` and `1/10`:

| `q` | independent families | within-family `rho` | exact FP = FN | admissible? |
|---:|---:|---:|---:|---|
| 9 | 1 | `1/20` | `560253581/12353515625` = 4.5352% | yes |
| 9 | 1 | `1/10` | `15009791/214843750` = 6.9864% | no |

At the more strongly correlated `rho=1/5` cell, reallocating the same nine
judgments across independent families changed the decision:

| family allocation | exact FP = FN | admissible? |
|---|---:|---|
| one family of 9 | `11805289/107421875` = 10.9897% | no |
| three families of 3 | `2145069/48828125` = 4.3931% | yes |
| nine families of 1 | `7649/390625` = 1.9581% | yes |

The `nine families of 1` row is insensitive to the registered within-family
correlation because no family is queried twice. This is a consequence of the
frozen independence model, not evidence that differently named real verifiers
provide independent errors.

## Exact grid frontier

The values below are grid boundaries, not continuous critical-point estimates.

| `q` | independent families | maximum passing `rho` on grid | first failing `rho` on grid |
|---:|---:|---:|---:|
| 1 | 1 | none | 0 |
| 3 | 1 | none | 0 |
| 3 | 3 | none | 0 |
| 5 | 1 | none | 0 |
| 5 | 3 | none | 0 |
| 5 | 5 | none | 0 |
| 7 | 1 | `1/50` | `1/20` |
| 7 | 3 | `1/10` | `1/5` |
| 7 | 7 | `1/2` | none on grid |
| 9 | 1 | `1/20` | `1/10` |
| 9 | 3 | `1/5` | `1/3` |
| 9 | 9 | `1/2` | none on grid |

## Why an average accuracy statement is insufficient

The atom-targeted control makes the strongest safety point in the experiment.
Let a semantic universe contain `N` atoms. One canonical refuting atom is
always judged incorrectly and every other atom is judged correctly. The
atom-averaged error is then `1/N`, while a false transcript whose refutation
depends on that atom is accepted with probability one.

| atoms | atom-averaged error | worst-case false acceptance |
|---:|---:|---:|
| 16 | 6.25% | 100% |
| 64 | 1.5625% | 100% |
| 256 | 0.390625% | 100% |
| 1024 | 0.09765625% | 100% |

Thus even apparently excellent average semantic accuracy cannot replace a
uniform or refutation-conditioned error guarantee. Replication cannot repair a
deterministic blind spot repeatedly selected by the protocol.

The global-flip control makes the related correlation point: when all answers
flip together with probability `1/5`, false acceptance and false rejection stay
at 20% for every registered query budget. More calls do nothing.

## What the experiment established

1. The repaired instrument reports false acceptance and false rejection
   separately; no paired-gap shortcut can conceal unusable completeness.
2. Under the registered exchangeable-error model, the operational outcome is
   controlled jointly by query count, within-family correlation, and the
   number of independent families.
3. A marginal error guarantee averaged over semantic atoms gives no uniform
   soundness guarantee on challenger-selected refutations.
4. The frozen positive model contains both passing and failing cells, so the
   result was not forced by a universally favorable noise class.

## What it did not establish

The beta-binomial calculation is classical, and the directional gates are
consequences of the frozen finite model. The run did not measure real human or
model-judge correlations, demonstrate independence across verifier families,
test an adversarial refutation locator, or establish a scalable-oversight
protocol. The challenger was assumed to have already located the decisive
semantic atom.

Accordingly, ASMP-3 is now **exploratorily investigated and formally
unresolved**. A real-model successor would first estimate held-out
refutation-conditioned error correlations; it should not infer them from
aggregate benchmark accuracy.

## Reproducibility

- Prereveal source commit: `ef9913dc15c9b630b8956e52625dc64ab1936770`
- Registration commit: `f868728b3d0dd2d89cdd5c282651a24fe5d5e24b`
- Result SHA-256: `de1f4319326e8fc88df4f702a937b58e29c1f35f298345941ca7dbbb37111cdc`
- Receipt SHA-256: `35e61f3ed8b6ad02a2c2cbad742f3dce73a8d63df0cc82fcc4370a9636195f9b`
- Arithmetic: Python standard-library `Fraction`; no stochastic sampling
- Tests: 7/7 passed
