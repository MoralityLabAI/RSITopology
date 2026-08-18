# ASMP-11 finite-sample access ladder v0.2 — preregistration draft

## Status

Design draft only. This file is not registered and authorizes no
claim-eligible run. Prior-art review, independent hostile review, numeric pilot
calibration, and a separate registration commit are required before outcomes.

The construction pilot in `pilot_v0_2/` is complete and non-claim-eligible. It
found no sample-cost inversion on the matched boundary `r+s=k`; inversion
appeared only after purchasing larger intervention width. The successor target
is therefore the exact covering-number frontier described below.

## Question

Does the exact population boundary `r+s=k` remain a useful predictor of
finite-sample detectability, and at what intervention width does a complete
covering design reverse the sample-cost ordering against pure observation?

The primary quantitative hypothesis is a **covering-mediated sample-cost
inversion**: on at least one prospectively frozen scaling sequence, an exact
or solver-certified `(n,s,k)` covering design reaches the same false-positive
and power targets using fewer total oracle samples than pure order-`k`
observation. The first intervention width where this occurs is the crossover.
No crossover yields `cost_inversion_not_established`; it is not repaired by
changing the grid after reveal.

## Statistical object

- Parent dimension: `n=12`.
- Planted parity degrees: `k in {3,4,5,6}`.
- Clean oracle: labels are independent unbiased signs.
- Planted oracle: `y = sigma * chi_T(x) * noise`, where `T` is a uniformly
  frozen `k`-support, `sigma` is a frozen sign, and the independent label-flip
  rate is selected from a prospectively frozen grid.
- A query `(I,a,S)` fixes coordinates `I` to assignment `a` and estimates
  `E[y * chi_S(x) | x_I=a]`, with `|I|<=s` and `|S|<=r`.
- Raw examples are not returned. Otherwise a client could compute higher-order
  statistics and silently escape the registered access class.

## Arms

1. **Pure-observation baseline:** query every degree-`k` Walsh coordinate and
   threshold the maximum absolute correlation using the registered exact
   familywise bound.
2. **Covering-design intervention:** query a minimum or certified-bounded
   family of width-`s` fixed sets covering every possible `k`-support.
3. **Matched random-cover control:** draw the same number of width-`s` blocks;
   report uncovered support mass and never treat an incomplete random family
   as a uniform detector.
4. **Population oracle control:** exact expectations reproduce the v0.1
   boundary and separate implementation failure from sampling failure.

Any additional adaptive heuristic must be selected on disjoint construction
supports and evaluated on held-out supports/signs/seeds. It is secondary to the
covering optimum and cannot pass uniform detection without covering every
support along its all-negative transcript.

## Important access-model qualification

Parity's statistical-query hardness makes the sampled observation arm a live
hard regime. It does **not** imply that the registered parent-fixing oracle has
a polynomial adaptive algorithm. Fixing unknown input coordinates induces a
covering problem. Before registration, any adaptive-efficiency claim must
therefore provide either:

1. a checked query-complexity bound under the exact parent-fixing grammar; or
2. a separately labelled Angluin-style internal-wire value-injection arm with
   its circuit-topology assumptions frozen.

These access classes may not be pooled. An internal-wire positive control can
show that value injection helps when the circuit exposes the required
structure, but cannot establish that parent fixing is efficient. The
polynomial-versus-exponential interpretation is prohibited unless the relevant
bounds are proved for the registered grammar.

## Gate semantics under finite sampling

The synthetic registry has known Bernoulli laws, so finite sampling does not
force the primary gates to depend on realized Monte Carlo estimates. The
protocol uses three evidence types and never conflates them:

- **Exact anchor gates** (`P0`, structural portions of `B0` and `S0`) are
  deterministic population statements. They retain exact arithmetic and
  byte-identical replay requirements.
- **Exact finite-sample design gates** compute the null tail, conservative
  familywise-error bound, and planted power as rational binomial sums under the
  frozen synthetic law. These probabilities describe a finite-sample test but
  are not estimated from one realized sample.
- **Monte Carlo replay**, if run, is calibration evidence only. It uses frozen
  independent replicates and simultaneous confidence bounds, but cannot
  override or replace the analytic gate.

The registration must freeze the test statistic, familywise level,
multiplicity bound, power floor, sample cap, and every numerical margin. A
future real-model successor must additionally freeze its estimator, replicate
unit, confidence procedure, and stopping rule. Byte hashes certify which code
and samples ran; they do not turn an empirical confidence statement into an
exact theorem. An invalid exact anchor makes the instrument invalid.

## Primary endpoints

- held-out detection power at frozen familywise false-positive rate;
- queries and total oracle samples needed to reach the target power;
- power as a function of signed boundary distance `r+s-k`;
- covering-versus-random and covering-versus-pure-observation cost ratios within
  `(k, noise, target-power)` strata.
- the exact or solver-certified covering number `C(n,s,k)` and its elementary
  counting lower bound `ceil(binom(n,k)/binom(s,k))`;
- the first prospectively frozen intervention width at which the covering
  design clears the pure-observation sample cost for two consecutive scaling
  cells; this is the primary crossover endpoint.

## Required gates before the claim-eligible run

- `P0 population replay`: v0.1 `r+s=k` boundary is reproduced exactly.
- `N0 null calibration`: the exact rational union-bound familywise error does
  not exceed the frozen ceiling.
- `L0 finite-sample liveness`: the exact rational planted power reaches the
  target within the sample cap in every registered primary cell.
- `B0 blindness control`: below-boundary power remains at the null level for
  every arm; failure means the implementation leaked forbidden statistics.
- `S0 simulator audit`: every query made by an arm belongs to its declared
  access class, and stronger-class simulation is checked mechanically.
- `A0 covering validity`: every selected block family covers every registered
  `k`-support; solver optimality or gap status is reported exactly as emitted.
  An incomplete family cannot support a uniform detection claim.
- `X0 cost-ordering inversion`: at matched false-positive and power control,
  the covering arm's certified total oracle samples lie below pure observation
  for two consecutive scaling cells. A single-cell crossing is reported
  descriptively and cannot pass `X0`.
- `C0 cost accounting`: query count, oracle samples, CPU time, and intervention
  assignments are reported separately. No scalar “access budget” is formed
  post hoc.

## Claim boundary

Even a positive v0.2 result would concern a noisy parity SQ/value-injection
oracle, not arbitrary white-box detectors, LPN hardness, obfuscated networks,
or language-model backdoors. Failure of the covering crossover would reject a
sample-cost inversion on the registered grid, not prove causal interventions
inefficient. The exact v0.1 result remains unchanged.
