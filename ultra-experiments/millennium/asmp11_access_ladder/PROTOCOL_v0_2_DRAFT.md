# ASMP-11 finite-sample access ladder v0.2 — preregistration draft

## Status

Design draft only. This file is not registered and authorizes no
claim-eligible run. Prior-art review, independent hostile review, numeric pilot
calibration, and a separate registration commit are required before outcomes.

## Question

Does the exact population boundary `r+s=k` remain a useful predictor of
finite-sample detectability, and can a frozen adaptive value-injection strategy
reverse the v0.1 cost ordering against nonadaptive exhaustive access?

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

## Primary endpoints

- held-out detection power at frozen familywise false-positive rate;
- queries and total oracle samples needed to reach the target power;
- power as a function of signed boundary distance `r+s-k`;
- adaptive-versus-random and adaptive-versus-exhaustive cost ratios within
  `(k, noise, target-power)` strata.

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
- `C0 cost accounting`: query count, oracle samples, CPU time, and intervention
  assignments are reported separately. No scalar “access budget” is formed
  post hoc.

## Claim boundary

Even a positive v0.2 result would concern a noisy parity SQ/value-injection
oracle, not arbitrary white-box detectors, LPN hardness, obfuscated networks,
or language-model backdoors. Failure of the adaptive arm would reject one
strategy, not prove causal interventions inefficient. The exact v0.1 result
remains unchanged.
