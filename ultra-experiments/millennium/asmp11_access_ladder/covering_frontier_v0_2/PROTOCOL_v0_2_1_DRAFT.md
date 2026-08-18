# ASMP-11 intermediate-width crossover protocol v0.2.1 DRAFT

Status: unregistered design draft. Do not treat this file as prospective
evidence until its sources, solver policy, resource limits, and registration
receipt are frozen in a separate commit.

## Question

For each frozen stratum `(n,k,eta)`, what is the smallest intervention width
`s` at which a designed parent-fixing estimator is certified to use fewer
samples than the v0.2 frozen nonadaptive exhaustive degree-`k` Walsh
estimator?

This fills the widths between the exact endpoint `s=k` studied in v0.1 and the
high-width v0.2 cells. It asks whether the crossover is a cliff or a slope. It
does not compare intervention harm, implementation cost, or total resources.

## Frozen candidate grid

- dimensions: `n in {13,15,17}`;
- parity degrees: `k in {3,4}`;
- flip rates: `eta in {1/20,3/20,1/4}`;
- widths: every previously unmeasured integer `s` with `k < s < s_high`,
  where `s_high=n-3` for `k=3` and `s_high=n-2` for `k=4`;
- familywise error ceiling: `1/20`;
- power floor: `9/10`;
- observational baseline: byte-identical v0.2 estimator and costs.

The v0.2 outcomes are prior information and must be named as such. The
v0.2.1 claim grid is only the previously unmeasured intermediate widths.

## Covering-number bounds

For every `(n,s,k)` cell, emit:

1. a verified covering witness of size `U(n,s,k)`;
2. a certified combinatorial or solver lower bound `L(n,s,k)`;
3. the exact optimum only when `L=U`;
4. solver status, primal objective, dual bound, MIP gap, elapsed time, and
   environment;
5. a provenance field stating whether any external covering repository was
   used.

La Jolla data, if used, may supply a hashed upper-bound witness only. It may
not be silently treated as proof of optimality.

## Cost envelopes

Let `cost(q,eta)` be the exact registered binomial sample cost for `q`
simultaneous queries at flip rate `eta`. For each cell report:

```text
best_certified_cost   = cost(U(n,s,k), eta)
optimistic_cost_floor = min cost(q,eta) over integer q >= L(n,s,k)
```

The minimum is evaluated exhaustively over the finite registered query-count
range rather than assuming monotonicity through integer cutoff changes.

Against observational baseline `B(n,k,eta)`, classify the width:

- `crossover_certified` if `best_certified_cost < B`;
- `crossover_impossible_under_bounds` if `optimistic_cost_floor >= B`;
- `unresolved_covering_gap` otherwise.

## Primary output

For each `(n,k,eta)` stratum return:

- `s_yes`: the smallest width with `crossover_certified`;
- `s_no`: the largest smaller width with
  `crossover_impossible_under_bounds`;
- `s_star=s_yes` only when every width below `s_yes` is certified not to
  cross;
- otherwise the bracket `(s_no,s_yes]` plus every unresolved cell.

No point estimate may replace this interval when covering optimality is not
closed.

## Frozen gates proposed for registration

- `B0_binding`: registration and all source hashes match.
- `B1_witness_validity`: every upper-bound block family covers the complete
  support universe.
- `B2_lower_bound_validity`: every reported lower bound names and replays its
  derivation; solver bounds carry full termination fields.
- `B3_probability_exactness`: sample costs and error/power checks use exact
  rational binomial sums.
- `B4_total_classification`: every grid cell receives exactly one of the
  three statuses above.
- `B5_minimum_width`: a minimum `s_star` is claimed only when all smaller
  widths are certified non-crossovers.
- `B6_resource_honesty`: timeout cells retain their bound interval and are not
  rerun selectively under a larger budget after cost outcomes are inspected.

## Resource policy to freeze

Use resumable, deterministic CPU work units. Freeze one uniform per-cell wall
clock and one total CPU-hour ceiling before execution. A time limit is an
allowed scientific outcome (`unresolved_covering_gap`), not permission to
relax the claim. Exact solving at middle widths is expected to dominate cost;
probability evaluation and witness verification are minor.

## Claim boundary

This successor can characterize a finite estimator crossover curve and its
uncertainty from unresolved covering numbers. It cannot prove a general
adaptive group-testing rate, an observational minimax lower bound, or a
white-box backdoor detection theorem.
