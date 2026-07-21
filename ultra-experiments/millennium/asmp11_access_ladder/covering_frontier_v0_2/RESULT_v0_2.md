# ASMP-11 covering-mediated finite-sample frontier result v0.2

## Verdict

`finite_covering_frontier_with_sample_crossover_established`

All seven frozen gates passed. The claim-grid run completed 21
solver-certified covering cells and 63 exact finite-sample cells in 51.3
seconds. The three claim dimensions `{13,15,17}` were disjoint from the
construction-pilot dimensions `{8,12,16,20}`.

## Structural result

For an order-zero parent-fixing query on block `I`, a planted parity support
`T` produces a nonzero population response exactly when `T` is contained in
`I`. Along the clean all-negative transcript, any uncovered support remains
indistinguishable from clean. Hence worst-case uniformly sound intervention
families must be `(n,s,k)` coverings.

In plain text, the combinatorial quantity is:

```text
C(n,s,k) = the minimum number of s-element blocks needed to contain every
           k-element support.
```

The adaptive reduction uses only the all-negative path. On that path, the
decision tree selects one fixed sequence of blocks; if those blocks fail to
cover a support, clean and planted mechanisms give the same transcript.

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
independently verified covering witness.

The optimization was a local binary set-cover ILP solved through
`scipy.optimize.milp` in SciPy 1.16.2, whose bundled solver identified itself
as HiGHS 1.8.0. The independent verifier checks that the emitted blocks really
cover every registered support, so it independently certifies each upper
bound. The matching lower bound rests on the recorded HiGHS optimal status,
zero MIP gap, and objective/dual-bound agreement; no standalone branch-and-
bound proof object was exported. The La Jolla Covering Repository was not used
to obtain or validate these cells. This is solver-backed finite enumeration,
not a new covering-design theorem.

## Exact finite-sample crossover

Every query used an exact two-sided binomial design with conservative
familywise error at most `1/20` and signal power at least `9/10`. The
probabilities were rational sums, not estimates from a realized Monte Carlo
sample.

The covering design beat the frozen nonadaptive exhaustive degree-`k` Walsh
estimator at the first registered width in every `(k, flip-rate)` stratum and
at all three dimensions. Thus all six crossover strata satisfied the
requirement that the estimator-to-estimator inversion persist across at least
two registered dimensions.

At flip rate `3/20`:

| `(n,k)` | First width | Cover samples | Frozen observational-estimator samples | Ratio |
|---:|---:|---:|---:|---:|
| (13,3) | 10 | 104 | 13,156 | 0.7905% |
| (15,3) | 12 | 104 | 21,385 | 0.4863% |
| (17,3) | 14 | 104 | 32,640 | 0.3186% |
| (13,4) | 11 | 130 | 34,320 | 0.3788% |
| (15,4) | 13 | 130 | 70,980 | 0.1832% |
| (17,4) | 15 | 130 | 133,280 | 0.0975% |

Across every frozen flip rate, the first-width covering arm used between
`0.0975%` and `0.9536%` of the samples used by that frozen observational
estimator. In particular, the `133,280` baseline is not a lower bound over all
observational strategies. It is the exact sample cost of the registered
nonadaptive exhaustive estimator, which queries every degree-4 Walsh support
at the frozen familywise-error and power targets. The ratios in this section
are therefore estimator-versus-estimator comparisons under two access
grammars, not an access-class lower-bound separation.

## Why the design -- not merely width -- matters

For each `(n,k,s,q)` cell, the control drew 256 seeded, uniformly random
`q`-block families without replacement from the block universe, where `q` was
the certified covering number. At the first crossover width, exact completion
counts were:

- degree 3: `0/256`, `2/256`, and `0/256` at dimensions 13, 15, and 17;
- degree 4: `3/256`, `6/256`, and `9/256` at dimensions 13, 15, and 17.

The optimized covering families passed uniform support coverage in every
cell. This says designed placement attains exact worst-case coverage at the
extremal block budget much more reliably than the registered matched-random
control. It does not say random placement is qualitatively incapable of
coverage: larger random families acquire coupon-collector-like overhead and
eventually cover. That overhead curve was not estimated in v0.2.

## Interpretation

The v0.1 conclusion is now refined:

- on the matched algebraic boundary `r+s=k`, the construction pilot found no
  sample-cost advantage over the frozen observational estimator;
- beyond that boundary, designed high-width interventions cover many possible
  supports per query and can reduce required oracle samples sharply;
- adaptivity cannot evade worst-case coverage along the clean all-negative
  path; it can only change how a covering is constructed or how average-case
  supports are treated.

Thus interventions are sample-cheaper in a precisely declared regime, but the
win is purchased with intervention width. It is not overall resource
dominance, and no scalar conversion between width and samples is inferred.

The registered grid contains high-width endpoints, not the whole curve. It
establishes that a crossover has occurred by widths 15 and 17 in the widest
strata; it does not establish whether the approach to that crossover is a
cliff or a slope. The additive v0.2.1 draft specifies the missing
intermediate-width characterization.

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

## Artifact integrity

The registration bound the source at commit
`87fe8fbf7e6be8c81c48ad77cd1b81d909725e2b`. The receipt records:

| Artifact | SHA-256 |
|---|---|
| `PROTOCOL_v0_2.md` | `91e6c75ed1b5a95211b0579d9978072975359a8edf48a23aae69c88f504e66eb` |
| `registration_v0_2.json` | `e96b3651005ccab9b921ba0da11c6f6409f54a30924aaf114678db632b09d713` |
| `artifacts_v0_2/covering_witnesses.json` | `32566411b42b71271beb1ed478c5e12fb8f1d0dccb89b0cca066d786018ad990` |
| `artifacts_v0_2/crossovers.csv` | `2d0f0280399d7245db197547b64dda8057b3023ab797801e2fd6486622f50e72` |
| `artifacts_v0_2/frontier.csv` | `2551f33e8de92f720e25006c843306c65dcf06d78053d052a68a7412812c10f3` |
| `artifacts_v0_2/result.json` | `7b958c25b181ba4318b014ec770221c50ce6c619686891e67d8ea1bd6bb5df8c` |

The result uses fenced plain text and code spans for its defining formula and
parameters, so its mathematical content does not depend on GitHub LaTeX
rendering.
