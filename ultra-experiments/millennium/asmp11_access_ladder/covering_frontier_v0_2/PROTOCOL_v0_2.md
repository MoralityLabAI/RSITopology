# ASMP-11 covering-mediated finite-sample frontier protocol v0.2

## Status

Prospective protocol. The claim grid is disjoint from the construction pilot:
the pilot used dimensions `{8,12,16,20}`, while this protocol uses
`{13,15,17}`. No claim-grid covering optimum or crossover may be read before the
registration commit.

## Mathematical object

The clean population oracle returns zero for every parent-fixing query. A
planted degree-`k` parity with support `T` returns a nonzero order-zero response
to a fixed set `I` exactly when `T subseteq I`.

On the all-negative adaptive path, any support not contained in a queried block
produces the same transcript as clean. Consequently every worst-case uniformly
sound detector must query an `(n,s,k)` covering, and a minimum covering is
sufficient at population level. The registered structural cost is therefore
`C(n,s,k)`.

## Frozen grid

- dimensions: `n in {13,15,17}`;
- planted degrees: `k in {3,4}`;
- intervention widths: `{n-3,n-2,n-1,n}` for `k=3` and
  `{n-2,n-1,n}` for `k=4`;
- flip rates: `{1/20, 3/20, 1/4}`;
- familywise-error ceiling: `1/20`;
- planted-power floor: `9/10`;
- samples-per-query cap: `4096`.

The grid is intentionally restricted by a disjoint resource preflight:
middle-width construction cells could not certify within 120 seconds, while
the registered high-width family remained tractable. Harder widths are future
bounds-only work and cannot be added after reveal.

Each covering number is solved as a binary covering MILP with SciPy/HiGHS,
zero requested MIP gap, and a 120-second per-cell time cap. Status `optimal`, a
zero reported gap, objective/dual-bound agreement, and an independently checked
cover witness are all required. A timed-out or gapped cell is
`solver_unavailable`, never rounded into an optimum.

## Finite-sample test

Every block receives fresh samples. The null statistic is a fair-sign count;
the live planted block has plus probability `1-flip_rate` up to an unknown sign,
so the test is two-sided. For each query count `q`, choose the smallest samples
per query and most permissive integer cutoff satisfying:

```text
q * exact_null_tail <= 1/20
exact_signal_tail >= 9/10.
```

Both tails are exact rational binomial sums. The first inequality is a
conservative union-bound familywise certificate. Total oracle samples are
`q * samples_per_query`.

The pure-observation baseline has `q=binom(n,k)` degree-`k` coefficients. The
primary crossover is the smallest `s` at which the certified covering design
uses fewer total oracle samples than pure observation. A crossover is
established only if it occurs at two consecutive registered dimensions for the
same `(k,flip_rate)`; otherwise it is descriptive.

## Gates

- `G0 registration binding`: protocol, prior art, runner, library, tests,
  verifier, and README match their registered hashes.
- `G1 covering validity`: every primary cell has solver status optimal, zero
  reported gap, objective/dual agreement, and an independently verified cover.
- `G2 endpoint controls`: the analytic pure-observation boundary uses
  `q=binom(n,k)`, and the registered full clamp satisfies `C(n,n,k)=1`.
- `G3 lower-bound sanity`: counting and Schoenheim lower bounds never exceed
  the certified optimum; the optimum never increases with intervention width.
- `G4 exact finite-sample calibration`: every design satisfies the rational
  FWER ceiling and power floor within the sample cap.
- `G5 all-negative-path liveness`: removing blocks until some support is
  uncovered makes that planted transcript identical to clean in the exact
  oracle fixture.
- `G6 crossover`: the covering arm beats pure-observation total samples at two
  consecutive dimensions for at least one frozen `(k,flip_rate)` stratum.

`G0-G5` passing establishes the finite covering frontier. `G6` is a separable
sample-cost result: failure yields `cost_inversion_not_established` without
invalidating the covering census.

## Claim boundary

This is solver-certified finite combinatorics and exact probability for a
transparent parity oracle. It is not a new covering-design theorem, an adaptive
group-testing theorem beyond the stated all-negative-path lemma, an LPN lower
bound, or evidence about neural-network backdoors. Intervention width and
sample cost remain separate resources; a sample crossover is never called
overall resource dominance.

## Resource ceiling

CPU only; 120 seconds per covering cell; 20 minutes total wall time; 4 GiB RAM;
no GPU.
