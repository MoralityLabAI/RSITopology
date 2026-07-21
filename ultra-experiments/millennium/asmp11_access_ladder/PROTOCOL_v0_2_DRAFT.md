# ASMP-11 finite-sample access ladder v0.2 — preregistration draft

## Status

Design draft only. This file is not registered and authorizes no
claim-eligible run. Prior-art review, independent hostile review, numeric pilot
calibration, and a separate registration commit are required before outcomes.

## Question

Does the exact population boundary `r+s=k` remain a useful predictor of
finite-sample detectability, and can a frozen adaptive value-injection strategy
reverse the v0.1 cost ordering against nonadaptive exhaustive access?

The primary quantitative hypothesis is a **cost-ordering inversion**: on at
least one prospectively frozen scaling sequence, the adaptive intervention arm
reaches the same held-out power and familywise false-positive target using
strictly fewer total oracle samples than the nonadaptive exhaustive arm. The
first dimension at which the simultaneous confidence bound clears the frozen
practical margin is the crossover point. No crossover yields
`cost_inversion_not_established`; it is not repaired by changing the strategy
or grid after reveal.

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

1. **Nonadaptive exhaustive:** query every registered `(I,a,S)` coordinate and
   threshold the maximum absolute held-out correlation using a familywise null
   calibration.
2. **Adaptive value injection:** a source-frozen strategy selects the next
   `(I,a,S)` from prior prereveal responses. Its stopping and tie-breaking
   rules, maximum queries, and sample allocation are sealed.
3. **Matched random-query control:** same query and sample budget as the
   adaptive arm, with seeded draws from the identical admissible universe.
4. **Population oracle control:** exact expectations reproduce the v0.1
   boundary and separate implementation failure from sampling failure.

The adaptive algorithm must be selected on disjoint construction supports and
evaluated on held-out supports/signs/seeds. If no adaptive policy survives the
pilot without outcome-conditioned tuning, the adaptive claim is unavailable;
the nonadaptive finite-sample surface may still run.

## Important access-model qualification

Parity's statistical-query hardness makes the sampled observation arm a live
hard regime. It does **not** imply that the registered parent-fixing oracle has
a polynomial adaptive algorithm. Fixing unknown input coordinates may still
require a combinatorial support search. Before registration, the adaptive
strategy must therefore provide either:

1. a checked query-complexity bound under the exact parent-fixing grammar; or
2. a separately labelled Angluin-style internal-wire value-injection arm with
   its circuit-topology assumptions frozen.

These access classes may not be pooled. An internal-wire positive control can
show that value injection helps when the circuit exposes the required
structure, but cannot establish that parent fixing is efficient. The
polynomial-versus-exponential interpretation is prohibited unless the relevant
bounds are proved for the registered grammar.

## Gate semantics under finite sampling

The protocol uses two evidence types and never conflates them:

- **Exact anchor gates** (`P0`, structural portions of `B0` and `S0`) are
  deterministic population statements. They retain exact arithmetic and
  byte-identical replay requirements.
- **Sampled decision gates** (`N0`, `L0`, `A0`, and the crossover decision) use
  a preregistered estimator, independent mechanism/seed replicates, one-sided
  simultaneous confidence bounds, and frozen practical margins. Their outputs
  are `pass`, `fail`, or `inconclusive`; equality is inconclusive.

The registration must freeze the estimator, familywise level, multiplicity
method, replicate unit, stopping rule, and every numerical margin. Byte hashes
certify which code and samples ran; they do not turn a confidence statement
into an exact theorem. An invalid exact anchor makes the instrument invalid.
A statistically inconclusive sampled arm leaves that arm not established but
does not rewrite the exact population result.

## Primary endpoints

- held-out detection power at frozen familywise false-positive rate;
- queries and total oracle samples needed to reach the target power;
- power as a function of signed boundary distance `r+s-k`;
- adaptive-versus-random and adaptive-versus-exhaustive cost ratios within
  `(k, noise, target-power)` strata.
- the first prospectively frozen dimension at which adaptive intervention
  clears the cost-inversion margin for two consecutive scaling cells; this is
  the primary crossover endpoint.

## Required gates before the claim-eligible run

- `P0 population replay`: v0.1 `r+s=k` boundary is reproduced exactly.
- `N0 null calibration`: the simultaneous false-positive upper confidence
  bound clears the frozen ceiling on disjoint null seeds.
- `L0 finite-sample liveness`: at least one above-boundary cell reaches the
  target power within the resource cap.
- `B0 blindness control`: below-boundary power remains at the null level for
  every arm; failure means the implementation leaked forbidden statistics.
- `S0 simulator audit`: every query made by an arm belongs to its declared
  access class, and stronger-class simulation is checked mechanically.
- `A0 adaptive validity`: adaptive selection beats matched random queries on
  held-out supports by the frozen practical and simultaneous-confidence
  margins. Failure makes adaptive efficiency `not_established`; it does not
  invalidate the nonadaptive surface.
- `X0 cost-ordering inversion`: at matched held-out power and familywise false-
  positive control, the adaptive arm's upper confidence bound on total oracle
  samples lies below the exhaustive arm's lower bound by the frozen practical
  ratio for two consecutive scaling cells. A single-cell crossing is reported
  descriptively and cannot pass `X0`.
- `C0 cost accounting`: query count, oracle samples, CPU time, and intervention
  assignments are reported separately. No scalar “access budget” is formed
  post hoc.

## Claim boundary

Even a positive v0.2 result would concern a noisy parity SQ/value-injection
oracle, not arbitrary white-box detectors, LPN hardness, obfuscated networks,
or language-model backdoors. Failure of the adaptive arm would reject one
strategy, not prove causal interventions inefficient. The exact v0.1 result
remains unchanged.
