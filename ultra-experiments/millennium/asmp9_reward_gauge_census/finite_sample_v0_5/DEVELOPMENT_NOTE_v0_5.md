# ASMP-9 finite-sample development note v0.5

## Status

Unregistered development result. The theorem and numeric cells below were
obtained before any prospective v0.5 protocol was frozen. They may be used to
design that protocol but not as confirmatory evidence.

## Candidate theorem structure

For the known independent sign-and-tie response channel:

```text
P(Y=1 | +) = 1-eta,
P(Y=1 | 0) = 1/2,
P(Y=1 | -) = eta,
```

the exact v0.4 coefficient-width threshold remains the liveness boundary:

```text
W*(B) = 1 for B<=2, and B-1 for B>=3.
```

Below it, some reward-ray pair has identical response laws under every adaptive
experiment, so infinite sampling cannot identify the ray. At it, an adaptive
coordinate/Farey search has finite worst-case sample complexity.

The current proof draft gives:

- a repeated-query upper bound of
  `O(d log(B) log(d log(B)/alpha)/(1-2eta)^2)`;
- a Fano lower bound of
  `Omega(d log(B)/(1-h2(eta)))`; and
- at the critical width in two dimensions, a nonadaptive lower bound growing
  as `Omega(|F_B|)=Omega(B^2)` for fixed channel and confidence.

The last bound follows because every adjacent pair in the Farey path can be
separated only by an admissible endpoint threshold, and each threshold covers
at most two adjacent pairs. Adaptive search follows one logarithmic branch;
nonadaptive allocation must cover the path.

## Development checks

- 52 tests pass.
- Exhaustive small ray universes recover every primitive ray at the theorem
  width.
- The lower-witness signatures are identical below the width and different at
  it for `B=3..9`.
- Seeded noisy recovery passes on 64 three-dimensional rays at `B=4`,
  `eta=0.1`.
- A direct grid calculation verifies that the tie input never increases the
  channel capacity above `1-h2(eta)`.
- Small nonadaptive information-design LPs at `d=2`, `B=3..6` return zero
  minimum pair information one width below the theorem and positive
  information exactly at the theorem width.

## Quantitative caution

The simple Hoeffding/union-bound estimator is conservative. On the development
cells its certified response upper bound is tens of times the generic Fano
lower bound. The v0.5 protocol should therefore test:

1. the exact width-liveness transition;
2. the derived nonadaptive Farey lower bound;
3. the constructor's correctness and query-width accounting; and
4. empirical error only as calibration, not as proof that the loose upper
   bound is sharp.

## Claim boundary

This is not Bradley-Terry reward learning, a result about human consistency,
policy-based IRL, discounted shaping, or an ASMP-9 resolution. It identifies a
tractable finite-sample bridge and an adaptivity separation inside one frozen
response model.
