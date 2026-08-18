# Raw-symbol refinement inflation theorem v0.20

## Construction

Start with any feasible finite registered sensor transducer from v0.18/v0.19.
Let its raw alphabet be `Y`, its event support be `E`, its reachable observer
matrix be `A`, and its exact length-`T` raw language size be `L_T`.

For any positive integer `m`, replace each raw symbol `y` by `m` registered
colors `(y,j)`, `0<=j<m`. Define

`E_m(s,z)={((y,j),s_next):(y,s_next) in E(s,z), 0<=j<m}`.

The color changes neither the plant, current `q` class, sensor successor,
control authority, safe set, nor actuator. Under forced-raw charging it is
still part of the injectively recoverable read transcript.

## Refinement theorem

Raw-symbol cloning preserves feasibility and the reachable belief graph after
colors are forgotten. Exactly,

`A_m=mA`,

`L_T(m)=m^T L_T`,

`rho(A_m)=m rho(A)`.

Therefore the forced-raw read corner increases by `log2(m)`, while every exact
write count and the write corner are unchanged.

### Proof

Every colored output `(y,j)` has the same successor belief and current `q` set
as its base output `y`. A base homogeneous transition produces `m` homogeneous
clones; a base mixed transition produces `m` mixed clones. Feasibility is
therefore invariant. Each observer edge label is copied `m` times, giving
`A_m=mA`. Every supported base word has exactly `m^T` independent colorings,
which proves the language identity directly. Matrix scaling proves the
spectral-radius identity.

The controller can forget `j` and use the original policy, so refinement adds
no write. Conversely, the v0.13 normal and first-differing-`q` lower bounds are
unchanged because colors do not affect either object. Thus the exact write
language is the base write language.

## Exact coarsening

The sufficient-statistic map

`pi(y,j)=y`

is a left inverse of the refinement at the level of support relations. If the
sensor encoder may discard irrelevant colors before charging the read port,
the base transducer, base language, and base read corner are recovered exactly.
If the registered experiment instead forces raw retention, the `m^T` factor is
load-bearing.

## Computed family

Apply the construction to the one-state computed `q` sensor. Its base raw
language is `2^T`. With `m` colors per `q` symbol, exact inner-collar counts are

- forced-raw reads: `(2m)^T ceil(rho*2^T)`;
- coarsened reads: `2^T ceil(rho*2^T)`;
- writes: `2^T ceil(rho*2^T)`.

The corresponding full-collar regions are

- forced raw: `[2+log2(m),infinity) x [2,infinity)`;
- coarsened: `[2,infinity) x [2,infinity)`.

The plant, evaluator-transversal normal dynamics, control-relevant `q`
statistic, and write requirement are identical for every `m`, but the
forced-raw read corner is unbounded.

## Exhaustive small-transducer check

Clone every one of the 256 deterministic two-state binary transducers by
`m=1,2,3`, giving 768 clone instances. For every `m`, exactly 80 remain
feasible and 176 remain infeasible. Every feasible clone has
`L_T=(2m)^T` and spectral radius `2m`; every infeasible mixed transition
persists. Thus cloning changes raw multiplicity, not safety classification.

The central frozenset/eigenvalue implementation and an import-independent
integer-mask implementation reproduce these results.

## Consequence for ASMP-4

No quantity determined only by this plant and its evaluator-transversal
dynamics can equal the forced-raw read threshold for all registered sensor
refinements: the plant data are fixed while the threshold moves by arbitrary
`log2(m)`.

A canonical theorem must therefore choose at least one of these registrations:

1. take the fixed sensor experiment, including raw-label multiplicity, as an
   explicit parameter;
2. optimize over sensor encoders, in which case irrelevant colors may be
   discarded; or
3. define an allowed sufficient-statistic quotient before measuring read
   entropy.

Without that choice, further local forced-raw fixtures cannot identify a
plant-only `h_read_perp`.

## Scope

This is a scoped stopping theorem against a plant-only forced-raw reading. It
does not refute a variational theorem parameterized by the registered sensor
experiment. It also does not refute the canonical achievable region if that
region optimizes over sensor encoders or quotients irrelevant labels. It does
not prove the full nonlinear coordinate-invariant ASMP-4 theorem.
