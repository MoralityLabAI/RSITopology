# ASMP-10 exact finite-prefix obstruction result v0.1

## Verdict

`finite_prefix_obstruction_established_for_registered_class`

All four preregistered gates passed. The census used exact rational arithmetic
for 60 confluent-Vandermonde systems and 15 explicit future-divergence
witnesses.

| gate | result |
|---|---|
| R0: exact rank | pass |
| I0: identification below threshold | pass |
| O0: indistinguishable-prefix obstruction at threshold | pass |
| C0: positive and negative controls | pass |

## Mathematical result

Let `n` distinct training states be observed, with derivatives of a polynomial
loss through order `k` at every state. Set

`J = n(k+1)`.

For losses of degree at most `D`, the exact observation map has rank

`rank H(n,k,D) = min(D+1, J)`.

Consequently:

- when `D < J`, the observation map has zero nullity and identifies the loss
  inside the registered degree class;
- when `D >= J`, it has nullity `D+1-J`, so at least one nonzero continuation
  is invisible to the allowed prefix observables.

The threshold witness is

`q(x) = product_(i=0)^(n-1) (x-i)^(k+1)`.

It has degree `J` and its derivatives through order `k` vanish at every
registered node. With unit-step gradient descent and

`L_plus(x) = -x + q(x)/q'(n)`,

`L_minus(x) = -x - q(x)/q'(n)`,

the two runs have the same jets and the same observed trajectory
`0,1,...,n`. At the first update using an unobserved jet, the future states are
`n` and `n+2`. Against the frozen continuous score `S(x)=x-(n+1)`, their scores
are exactly `-1` and `+1`.

## Why the threshold is exact

If two degree-at-most-`D` losses have identical registered jets, their
difference has a zero of multiplicity at least `k+1` at each of the `n`
distinct nodes. A nonzero polynomial with those zeros has degree at least
`n(k+1)=J`. Thus no nonzero difference exists for `D<J`.

At `D=J`, the displayed product has exactly the required roots and
multiplicities. Multiplying it by any polynomial of degree at most `D-J`
generates the full invisible subspace, whose dimension is `D-J+1`.

This is classical Hermite interpolation expressed as an ASMP-10
identifiability boundary. Novelty is not claimed for the theorem.

## Census details

- nodes: `n in {1,2,3,4,6}`;
- jet orders: `k in {1,2,3}`;
- degrees around every boundary: `J-2`, `J-1`, `J`, and `J+1`, with the
  nonnegative and duplicate rules from the protocol;
- rank/nullity outcomes: 30 zero-nullity rows, 15 nullity-one rows, and 15
  nullity-two rows;
- all 15 threshold witnesses were exact kernel elements;
- all 15 pairs retained identical prefixes and produced opposite future
  capability predicates with unit score margin.

## What this adds to ASMP-10

The result formalizes the problem's negative liveness example. A finite prefix
cannot uniformly predict a later capability over a family that permits
unidentified continuations. Prediction becomes possible only after the
observable budget identifies the declared dynamics or after extra regularity
rules out the invisible kernel.

This also clarifies what a future neural experiment must establish. Beating a
loss-only predictor is not enough by itself; the claimed training family needs
a stated regularity assumption explaining why adversarial prefix-matched
continuations are inadmissible.

## Artifact binding

- prereveal source commit: `a99c17fa8f8ed4fe1fcc5713d934f965744d9914`;
- registration commit: `49f6a896d4c0169fa442f3047c54fccedfb57b38`;
- registration SHA-256:
  `bc3005a820858902e6bac965fac68cdcedf114e92443144136d241b12fd2e63e`;
- result SHA-256:
  `639c2eddc7f8814b7af07bcbc708c7b0f72ec8f0d121bb9a84b512978570fe0c`;
- receipt SHA-256:
  `d6373c456784e3d07cc9a6a77b5ab51b2e702d0e164d3df18a4b3e4196b309d2`;
- test command: `python -m pytest ultra-experiments/millennium/asmp10_capability_transition/prefix_obstruction/test_prefix_obstruction.py -q`;
- test result: `4 passed`.

## Claim boundary

This establishes the exact identification/obstruction boundary only for the
registered one-dimensional bounded-degree polynomial loss class and finite
local-jet filtration. It does not show that neural-network capabilities are
unpredictable, that spectral or SLT observables are uninformative, or that a
recursive system can or cannot improve itself. It is an exact theorem seed and
instrument calibration for ASMP-10, not a resolution of the full problem.
