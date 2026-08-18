# When preference signs need wider questions

## Exact finite ASMP-9 access frontier

Version 0.1 showed that exact real-valued returns on a cycle basis identify an
edge-reward quotient modulo potential shaping. Version 0.2 asks what survives
when the interface returns only pairwise preference signs.

The answer is that two resources separate:

1. **query count** — how many comparisons may be asked; and
2. **query width** — how large the integer coefficients in a trajectory-bundle
   comparison may be.

Increasing the number of comparisons cannot repair a grammar whose admitted
hyperplanes never place two candidate reward rays robustly on opposite sides.

## Result

Every registered reward is a primitive integer cycle-return vector modulo
positive scale. Each comparison returns the sign of an integer linear
functional. The robust arm permits an adversarial half-unit perturbation of the
comparison threshold.

All eight preregistered gates passed.

| quotient dimension | reward bound | response model | first complete coefficient width | minimum comparisons |
|---:|---:|---|---:|---:|
| 1 | 1 | exact sign | 1 | 1 |
| 1 | 1 | half-unit ambiguity | 1 | 1 |
| 2 | 1 | exact sign | 1 | 2 |
| 2 | 1 | half-unit ambiguity | 2 | 4 |
| 3 | 1 | exact sign | 1 | 3 |
| 3 | 1 | half-unit ambiguity | 2 | 9 |
| 2 | 2 | exact sign | 1 | 4 |
| 2 | 2 | half-unit ambiguity | 3 | 8 |

At coefficient width one, the robust arm left:

- 8 of 28 candidate pairs unresolved in the two-dimensional, bound-one
  registry;
- 48 of 325 unresolved in the three-dimensional, bound-one registry; and
- 24 of 120 unresolved in the two-dimensional, bound-two registry.

No number of width-one queries can separate those pairs because the table
already includes every primitive width-one comparison. Wider questions, not
repetition, close the gap.

## Mechanism

The exact-sign oracle has three outputs: negative, tie, and positive. Ties
locate a reward ray on a comparison hyperplane and therefore carry exact
geometric information. Under the frozen half-unit threshold perturbation, a
zero-margin comparison can return any of the three signs. Identification then
requires a comparison with a strict margin on opposite sides for the two
candidates.

This is why the robust query families use normals such as `[1,-2]` and
`[1,-3]`: coefficient width buys angular resolution. The observed penalties
are not sampling error and cannot be removed by asking the same narrow class
more often.

## Verification

- Implementation commit:
  `3c99eab311fd5111a49cf161f9125e9bfd5f7797`
- Registration commit:
  `5e645f3d2e609dc5a755d97da4eea6c2ab4785ef`
- Registration SHA-256:
  `418198c27024bb0ec30e9ac7e6977ffd44729a65a16c4ed284c8329cdffb9782`
- Claim cells: 32
- Prereveal tests: 14 passed
- Run time: 5.17 seconds
- Independent verifier: input hashes, output hashes, verdict, all gates,
  thresholds, and cell count reproduced.

Every reported minimum has HiGHS optimal status, zero reported MIP gap,
objective/dual-bound agreement, integral selected queries, and an independently
replayed full pair cover.

## Claim boundary

This is a finite, nonadaptive, population-oracle comparison census after the
potential-shaping quotient has already been constructed. It does not identify
human values, recover rewards from behavior, analyze finite-sample preference
noise, prove an adaptive query bound, or establish a general reward-learning
theorem. The threshold perturbation is one frozen adversarial
misspecification model. The result is a bounded ASMP-9 instrument result, not
an ASMP-9 resolution.

