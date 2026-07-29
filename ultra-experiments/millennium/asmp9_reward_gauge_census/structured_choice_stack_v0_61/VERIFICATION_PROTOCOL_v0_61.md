# ASMP-9 structured-choice-stack verification protocol v0.61

## Status and epistemic boundary

This protocol prospectively freezes a verification of the conditional
structured-choice stack developed in v0.57-v0.60.  Every development result,
test cell, and table in those versions is burned design evidence.

Passing supports the exact finite implementations and the proof handoffs
listed below.  Finite checks do not prove arbitrary-`n` theorems; the Boolean
interpolation, compactness, testing, contamination, and factorization
arguments remain the proof.  Passing is not evidence that human or model
preferences satisfy the premises, and it is not a resolution of ASMP-9.

## Frozen conventions

For `n` alternatives and contextual log-odds degree `r`,

```text
D_(r+2) = {A : 2 <= |A| <= r+2},

Q(n,r) = sum_(k=2)^(min(n,r+2)) k * choose(n,k).
```

`Q` counts observed probability coordinates, not menus.  This line supersedes
any typographically ambiguous rendering of `Q` in the v0.58 prose; the v0.58
source already uses this definition.

Kernel distance is maximum menuwise `L1`.  Distributional contamination uses
total variation.  Equality at every contamination, recording-ratio, model-set
distance, or resource boundary is never a scientific pass.

The compact class used by the class-level thresholds is the image of valid
`D_(r+2)` restrictions with observed coordinates at least `a>0` under the
degree-`r` reconstruction map, intersected with the closed margin-separated
tier fibers.  The compactness proof is frozen in `PROOF_AUDIT_v0_61.md`.

## Fresh verification cells

All cells are frozen in `verification_cells_v0_61.json`.  In particular:

- v0.57 uses universe sizes `9` through `12`, which were absent from the
  development witness census;
- v0.58 uses new rational boundary paths and new sample-bound cells;
- v0.59 uses a four-outcome rational simplex grid with denominator `8`;
- v0.60 uses a positive four-outcome grid with denominator `9`, new recording
  intervals, and new selection floors.

No gate threshold or cell may be changed after registration.

## Gates

### H0 — source and registration integrity

Every registered source hash, including the four burned theorem/source/prior-
art triples, must match.  The registration and verification outputs are
write-once.

### T0 — verifier tests

The exact registered pytest command must pass with the registered test count.
The test suite uses burned smoke cells only; it does not execute the fresh
verification matrix before registration.

### B57 — bounded-degree access and sharpness

For every frozen `(n,r,A0,x0)` cell:

1. the contextual-score witness is uniform on all menus through size `r+1`;
2. on `A0`, `p(x0|A0)=(r+2)/(2r+3)>1/2`, while every binary submenu gives
   `1/2`;
3. all pairwise Boolean Möbius coefficients above order `r` vanish and at
   least one order-`r` coefficient is nonzero;
4. reconstruction from contexts through order `r` recovers the held-out
   target values exactly; and
5. the enumerated interpolation operator norm equals

```text
K(s,r) =
  sum_(u=0)^r choose(s,u) choose(s-u-1,r-u)
```

for `s>r`, with the direct-observation value one when `s<=r`.

### M58 — separation, lower paths, and sample sufficiency

The fresh exact Luce/RUM and RUM/non-RUM paths must preserve their registered
tiers by explicit ranking-mixture, non-Luce, and regularity witnesses.

For every frozen sample cell, the independent computation must verify:

```text
t_gamma =
  a * [1-exp{-atanh(gamma/6)/K_star(n,r)}],

N =
  ceil[
    log{2Q(n,r)/delta}/(2 t_gamma^2)
  ],
```

and the resulting Hoeffding event must imply reconstructed full-kernel error
at most `gamma/3`.  The fresh lower-path cells must satisfy the registered
Le Cam inequality and expose the `gamma^-2` exponent without claiming a
general minimax constant.

### C59 — contamination radius

On the complete frozen rational simplex grid:

```text
N_epsilon(p) intersects N_epsilon(p')
iff
TV(p,p') <= epsilon/(1-epsilon).
```

Every admitted overlap must have an explicit common observation and two valid
contaminants.  The fresh RUM/non-RUM witnesses must meet exactly at
`epsilon=2gamma/(1+2gamma)`.

Every robust sample cell must treat contamination bias and sampling error as
separate additive consumers of the clean coordinate tolerance.  Equality
returns unavailable or inconclusive.

### S60 — selection timing, positivity, and recording

The fresh pre-response joint laws must recover every positive-support
conditional and leave zero-support conditionals unidentified.

On the complete positive rational grid:

1. unrestricted positive outcome-dependent recording must construct the same
   complete recorded law from every clean pair;
2. bounded recording neighborhoods overlap exactly when the symmetric
   coordinate ratio is at most `u/ell`;
3. every admitted overlap must construct valid recording probabilities and a
   common retained-response law; and
4. known positive recording weights must recover the clean distribution.

Fresh selection-floor cells must close the Chernoff/Hoeffding upper bound and
the `1/pi` Le Cam scaling handoff.

### X0 — cross-version convention handoff

The primary and replay implementations must agree on every registered `K_star`
and `Q` value, on the explicit v0.58 witness inherited by v0.59 and v0.60, and
on all equality semantics.  The compactness lower bound

```text
min full-kernel coordinate >= a^(2 K_star)/n > 0
```

must be positive in every frozen bounded-degree sample cell.

### I0 — import-independent replay

`independent_replay_v0_61.py` may not import the primary verifier or any
v0.57-v0.60 implementation.  Its canonical fact digest and gate-relevant
counts must equal the primary computation exactly.

### RESOURCE

One worker, less than 180 seconds, and strictly less than 768 MiB resident
memory.  Equality is failure.

## Verdict and stop rule

Every gate must pass.  The only passing verdict is:

```text
conditional_structured_choice_stack_verified
```

Any mismatch, failed exact identity, invalid witness, missing independent
agreement, or resource-bound equality yields `verification_failed`.  There is
no discretionary override.  Repairs require a new version, a new registration
commit, and fresh cells.

## Claim boundary

Passing verifies a conditional finite stochastic-choice access ledger:
bounded-degree exact reconstruction, separation-promised sampling, fixed
Huber robustness, and two registered selection timings.  The ingredients are
classical or elementary and novelty is not asserted.  The result does not
select `r`, validate any premise empirically, compute general class moduli
efficiently, handle zeros/ties/hidden menus/latent confounding/strategic or
nonstationary response, supply welfare semantics, or resolve ASMP-9.

