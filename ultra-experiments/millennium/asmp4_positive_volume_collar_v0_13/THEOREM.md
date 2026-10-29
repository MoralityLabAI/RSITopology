# Positive-volume collar theorem

## Registered system

Let `z` take values in `{-3,-1,1,3}` and let an arbitrary allowed disturbance set `z_next=w`. Define

`q(z)=(12+13z-z^3)/3`, so `q(-3)=q(-1)=0` and `q(1)=q(3)=8`.

On `S^1 x R x modes`, use

`theta_next=theta+1/4 mod 1`,

`n_next=2n+u-q(z)`, with `u in [-2,10]`.

The safe initial and target set is

`K=K_0=S^1 x [-1,1] x modes`.

Lebesgue measure on the circle and normal coordinate, with normalized counting measure on the modes, gives `K` normalized volume 2. Thus this is a positive volume collar, not an invariant point or a zero-width slice.

Under the feedback `u=q(z)`, the cylinder map is the diffeomorphism `(theta,n) -> (theta+1/4,2n)`. The circle `N=S^1 x {0}` is closed, compact, connected, invariant, and one-dimensional. Its tangent norm is 1 and its unstable inverse norm is `1/2`; choosing `lambda=3/4` gives `1/2 < 3/4 < 1` and `(1/2)*1 < 3/4`. It is therefore a normally expanded NHIM under the classical definition audited in v0.12. Bounded local authority is genuine: for `|n|<=1/4` and `|eta|<=3/2`, `u=q(z)+eta-2n` lies in `[-2,10]` and sends `n` exactly to `eta`.

## Exact full-collar theorem

Fix a horizon `T>=1`. A computed registry reports the current `q`-fiber and the normal branch; a forced raw registry reports the current raw mode and the normal branch. Controls are causal: the current report precedes the current write, and no future disturbance is reported.

For every initial point in `K` and every disturbance word, safety is maintainable. One stationary policy uses residual control `a=u-q(z)` equal to `+1` for `n<0` and `-1` for `n>=0`. The normal map is then the two-branch doubling map of `[-1,1]` onto itself. Its depth-`T` dyadic cells realize all `2^T` branch words. Combining those words with the `2^T` `q`-fiber words gives exactly `4^T` computed-read words and `4^T` write words. Combining them with the `4^T` raw-mode words gives exactly `8^T` raw-read words. The four writes at each time are `{-1,1,7,9}` and all lie in the authority interval.

These upper counts are also lower bounds. Under a fixed control word and a fixed `q` word, two normal trajectories separate by `2^T`; because their final values must both lie in an interval of diameter 2, one word can serve an initial interval of length at most `2/2^T`. Covering `[-1,1]` therefore needs at least `2^T` normal words. Moreover, one write word cannot serve two different `q`-fiber words. At their first differing `q`, equal controls and two pre-step normals in `[-1,1]` produce successor separation at least `8-2*2=4`, greater than the safe diameter 2. Finally, a deterministic causal controller maps each read transcript to one write transcript, so the computed read count cannot be smaller than the write count; the forced raw registry distinguishes all four modes.

Consequently, in bits per step, the exact upward-closed full-collar regions are

- computed registry: `[2,infinity) x [2,infinity)`;
- forced raw registry: `[3,infinity) x [2,infinity)`.

The coordinates are `(read capacity, write capacity)`.

## Exact finite-margin correction

Now restrict the initial normal collar to `[-rho,rho]`, where `0<rho<=1`, while all later states must remain in `[-1,1]`. Then the exact normal spanning number is

`N_T(rho)=ceil(rho*2^T)`.

For the construction, partition `[-rho,rho]` into `N_T(rho)` intervals of length at most `2/2^T`. If one cell has center `c`, use first control residual `a_0=-2c` and later residual controls `a_t=0`. After `t` actions the centered cell has expanded by `2^t`, so it remains in `[-1,1]` through time `T`. The residual authority is valid because `|a_0|<=2` and `q` is 0 or 8.

For the converse, the same final-time diameter calculation says that any one fixed control word covers initial length at most `2/2^T`. An interval of length `2rho` therefore requires at least `ceil(rho*2^T)` words. The mode-separation argument above makes the multiplication by mode words exact. Hence

- computed read words and write words: `2^T ceil(rho*2^T)`;
- forced raw read words: `4^T ceil(rho*2^T)`.

For each fixed `rho>0`, the ceiling is the exact finite-horizon correction and its normalized logarithm tends to one normal bit per step. The asymptotic regions are therefore the same as for the full collar.

## Scope

This theorem is exact for the stated plant, authority, timing, safe collar, and two registered sensor conventions. It does not establish perturbation/noise robustness, determine a canonical sensor registry for ASMP-4, or prove the requested global variational classification.
