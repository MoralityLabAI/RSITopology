# ASMP-11 intermediate-width crossover protocol v0.2.1, release v0.2.1.2

## Status

Source-hardening checkpoint only. Claim-grid execution is forbidden until these
v0.2.1.2 sources are committed and a separate prospective registration binds
their full source commit, SHA-256 commit-blob hashes, and Git blob OIDs. That
registration must then be committed separately before execution into a new
non-aliasing artifact directory. The v0.2 and v0.2.1.1 artifacts are immutable
prior information, not v0.2.1.2 observations.

## Knowledge contract

- Primary benefit: measurement and robustness mapping.
- Claim scope: model-only, for the transparent finite parity oracle.
- Experimental unit: one deterministic `(n,k,s)` covering cell. Flip-rate
  rows are repeated exact cost views of that cell, not independent replicates.
- Question: for each `(n,k,eta)`, what is the smallest intervention width at
  which an incumbent covering is certified to use fewer total oracle samples
  than the frozen exhaustive observational estimator?
- Falsifier: no width is certified before the sealed v0.2 high-width anchor,
  or an independent verifier rejects any witness, lower bound, exact tail,
  classification, or bracket.

## Claim grid

- `n in {13,15,17}`;
- `k in {3,4}`;
- `eta in {1/20,3/20,1/4}`;
- every integer `s` satisfying `k < s < n-3` for `k=3`, or
  `k < s < n-2` for `k=4`;
- familywise error ceiling `1/20`;
- power floor `9/10`; and
- samples-per-query cap `4096`.

This is exactly the previously unmeasured intermediate-width grid from the
draft: 48 covering cells and 144 finite-sample views. The analytic boundary
`s=k` and six high-width v0.2 anchors are controls, not claim-grid cells.

Tests may use smaller fixtures, but such fixtures are development-only and
cannot enter the result layer.

## Deterministic certified-bound method

For each `(n,k,s)` cell, enumerate the complete `k`-support universe and all
`s`-blocks in lexicographic order. A deterministic greedy set-cover pass picks
the block with maximum uncovered gain, breaking ties lexicographically, then
performs deterministic reverse deletion.

The incumbent is independently checkable by enumerating every support. The
lower bound is

```text
L = max(counting bound, recursive Schoenheim bound).
```

Both components use exact integers and are replayable without the construction
code. If `L=U`, the optimum is certified. Otherwise the interval `[L,U]` is
retained. No floating-point solver status is promoted into a proof.

The scientific construction stop is a uniform maximum of 4096 greedy rounds
per cell. The candidate-family cap is 30,000 blocks. A 15-second per-cell wall
limit is an operational fail-safe, and the total wall ceiling is 900 seconds.
On either stop, the complete family of `s`-blocks is retained as a valid
incumbent and the exact lower bound is still emitted. A stop can widen an
interval; it cannot create an optimum or a crossover.

Wall, round, candidate, event, and stop observations are checked against the
registered operation record. Peak RAM is not measured by this instrument, so
the registered RAM ceiling is reported as `compliance=not_established`, never
as a passing resource gate.

## Exact finite-sample cost

The observational baseline is byte-for-byte equivalent in mathematical rule
to v0.2: `q=binom(n,k)` exact two-sided sign tests with Bonferroni familywise
control. For every integer `q in [L,U]`, choose the smallest samples per query
and most permissive cutoff satisfying

```text
q * exact_null_tail <= 1/20
exact_signal_tail >= 9/10.
```

All probabilities are `Fraction` values. The optimistic cost floor is the
minimum exact total cost over every integer `q in [L,U]`; monotonicity is not
assumed. The certified cost uses `q=U`.

Each cell receives exactly one status:

- `crossover_certified` if the incumbent cost is below baseline;
- `crossover_impossible_under_bounds` if even the optimistic floor is not
  below baseline; or
- `unresolved_covering_gap` otherwise.

For each `(n,k,eta)` stratum, `s_yes` is the smallest certified width. Because
cost monotonicity is not assumed, `s_no` is the end of the contiguous certified
non-crossover prefix beginning at the analytic `s=k` control; a later
non-crossover after an unresolved width cannot raise this lower endpoint.
`s_star=s_yes` only when every smaller width is certified not to cross.
Otherwise the result is the honest bracket `(s_no,s_yes]` plus the unresolved
widths.

## Metric firewall, four alternatives, and one identity diagnostic

The greedy uncovered-gain score is a selection metric only. Evidence metrics
are witness validity, exact lower and upper bounds, exact total sample costs,
and the three-way status. Stop reasons, elapsed time, interval width, and
sample-cap failures are hazards. These groups do not overlap.

Five predeclared records are non-binding and cannot repair a failed primary
gate. The first is an identity replay diagnostic and is excluded from every
robustness denominator:

1. `D1_primary_bound_interval_replay`: replay the primary interval rule. This
   is a diagnostic identity check, not robustness evidence.
2. `P2_query_count_only`: repeat the comparison without replicate cost.
3. `P3_stricter_familywise_error`: use Bonferroni `alpha=1/40`.
4. `P4_stricter_power`: use power floor `19/20`.
5. `P5_exact_independent_fwer`: use exact independent-query familywise error
   instead of the Bonferroni upper bound.

Alternative-metric disagreement is reported as sensitivity, not hidden or
voted away. Version 0.2.1.2 does not relabel these four alternatives as the
five-family invariance/sensitivity/monotonicity/anti-gaming/clean-control pack.

## Evidence layers

Outputs are deliberately separated:

- **result layer:** raw covering/cost cells and minimum-width brackets;
- **reliability layer:** binding gates, interval coverage, the identity
  diagnostic, and all four alternative-metric probes;
- **claim layer:** observed, inferred, not-supported, robustness, confounds,
  and a provisional verdict pending independent verification; and
- **operation layer:** registration, environment, resource use, stop reasons,
  and partial-run status.

The independent verifier writes a separate verification receipt. A final
synthesis writer fresh-replays that verifier, requires exact equality with its
stored receipt, and then binds the committed registration, primary receipt,
independent verification, and the five conclusion layers: metric robustness,
task result, measurement reliability, claim support, and operational decision.
Alternative metric disagreement is reported as sensitivity but remains
non-binding for the task result. Operational success alone cannot promote the
claim layer.

## Binding gates

- `B0_binding`: the exact source-name set, full source and registration commit
  chain, commit-blob hashes/OIDs, manifest, and prior anchor match. Receipt-link
  closure is checked independently after the primary layers are written.
- `B1_witness_validity`: every incumbent covers the complete support universe.
- `B2_lower_bound_replay`: counting and Schoenheim bounds replay exactly and
  never exceed the incumbent.
- `B3_probability_exactness`: every primary baseline, incumbent, and optimistic
  design replays with exact rational tails.
- `B4_total_classification`: exact Cartesian `Counter` equality proves all 144
  claim-grid views occur exactly once and receive one status.
- `B5_minimum_width`: `s_star` appears only when every smaller width is a
  certified non-crossover.
- `B6_resource_honesty_ram_unmeasured`: registered measured caps, events, and
  stops are internally consistent; stopped cells retain bounds and witnesses;
  RAM compliance is explicitly unestablished.
- `B7_metric_probe_completeness`: every cost cell has one excluded identity
  diagnostic and four complete non-binding alternative-metric records, with
  full records and summaries independently replayed.

## Claim boundary

This package can establish a finite, bounds-aware estimator crossover surface
for one transparent parity oracle. It cannot prove a general adaptive
group-testing rate, an observational minimax lower bound, a white-box backdoor
detection theorem, or overall intervention-resource dominance. A sample-cost
crossover does not price intervention width, harm, latency, or implementation
cost.
