# ASMP-11 covering-mediated finite-sample frontier result v0.2

## Verdict

`finite_covering_frontier_with_sample_crossover_established`

All seven frozen gates passed. The claim-grid run completed 21
solver-certified covering cells and 63 exact finite-sample cells in 52.4
seconds. The three claim dimensions `{13,15,17}` were disjoint from the
construction-pilot dimensions `{8,12,16,20}`.

## Structural result

For an order-zero parent-fixing query on block `I`, a planted parity support
`T` produces a nonzero population response exactly when `T` is contained in
`I`. Along the clean all-negative transcript, any uncovered support remains
indistinguishable from clean. Hence worst-case uniformly sound intervention
families must be `(n,s,k)` coverings.

The certified covering numbers on the frozen high-width grid were:

| Degree | Intervention width | Certified covering number |
|---:|---:|---:|
| 3 | `n-3` | 4 |
| 3 | `n-2` | 4 |
| 3 | `n-1` | 4 |
| 3 | `n` | 1 |
| 4 | `n-2` | 5 |
| 4 | `n-1` | 5 |
| 4 | `n` | 1 |

These values held at all three registered dimensions. Every solver cell
reported optimal status, zero MIP gap, objective/dual-bound agreement, and an
independently verified covering witness. This is solver certification, not a
new covering-design theorem.

## Exact finite-sample crossover

Every query used an exact two-sided binomial design with conservative
familywise error at most `1/20` and signal power at least `9/10`. The
probabilities were rational sums, not estimates from a realized Monte Carlo
sample.

The covering design beat pure degree-`k` observation at the first registered
width in every `(k, flip-rate)` stratum and at all three dimensions. Thus all
six crossover strata satisfied the requirement that the inversion persist
across at least two registered dimensions.

At flip rate `3/20`:

| `(n,k)` | First width | Cover samples | Pure-observation samples | Ratio |
|---:|---:|---:|---:|---:|
| (13,3) | 10 | 104 | 13,156 | 0.7905% |
| (15,3) | 12 | 104 | 21,385 | 0.4863% |
| (17,3) | 14 | 104 | 32,640 | 0.3186% |
| (13,4) | 11 | 130 | 34,320 | 0.3788% |
| (15,4) | 13 | 130 | 70,980 | 0.1832% |
| (17,4) | 15 | 130 | 133,280 | 0.0975% |

Across every frozen flip rate, the first-width covering arm used between
`0.0975%` and `0.9536%` of the pure-observation oracle samples.

## Why the design—not merely width—matters

Matched random block families at the first crossover width rarely covered the
support universe:

- degree 3: completion rates `0`, `1/128`, and `0` at dimensions 13, 15, and
  17;
- degree 4: completion rates `3/256`, `3/128`, and `9/256`.

The optimized covering families passed uniform support coverage in every
cell. This separates “wide interventions exist” from “the intervention plan
actually certifies every possible planted support.”

## Interpretation

The v0.1 conclusion is now refined:

- on the matched algebraic boundary `r+s=k`, the construction pilot found no
  sample-cost advantage over pure observation;
- beyond that boundary, designed high-width interventions cover many possible
  supports per query and can reduce required oracle samples sharply;
- adaptivity cannot evade worst-case coverage along the clean all-negative
  path; it can only change how a covering is constructed or how average-case
  supports are treated.

Thus interventions are sample-cheaper in a precisely declared regime, but the
win is purchased with intervention width. It is not overall resource
dominance, and no scalar conversion between width and samples is inferred.

## Gate record

- `G0_registration_binding`: pass.
- `G1_covering_validity`: pass for all 21 solver cells.
- `G2_endpoint_controls`: pass.
- `G3_lower_bound_and_monotonicity`: pass.
- `G4_exact_finite_sample_calibration`: pass for all 63 probability cells.
- `G5_all_negative_path_liveness`: pass.
- `G6_crossover`: pass in all six `(k,flip-rate)` strata.

## Claim boundary

This is a finite transparent-parity result on dimensions 13, 15, and 17. It
does not establish a new covering number theorem, general adaptive group-
testing bounds, LPN hardness, detectability of obfuscated mechanisms, or a
neural-network backdoor result. The registered widths are intentionally high
because harder middle-width construction cells failed the pre-registration
resource preflight. No current result resolves proposed `ASMP-11`.
