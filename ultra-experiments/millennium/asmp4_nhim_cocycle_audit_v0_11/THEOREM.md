# ASMP-4 bounded-authority cocycle repair theorem v0.11

## 1. Vulnerability addressed

The v0.6 rational fixture used the binary plant action set `{0,1}` and recorded
the algebraic derivative `dF_n/du=1`.  A derivative on a discrete input domain
does not alone establish local reachability.  Consequently that line was too
weak to carry the phrase "locally controllable" without another registered
control-domain convention.

## 2. Repaired same-plant fixture

Let

```text
n_(t+1)=(3/2)n_t+u_t-q(z_t),
z_(t+1)=w_t,
q(z)=(12+13z-z^3)/24,
z_t,w_t in {-3,-1,1,3},
u_t in [-1,2].
```

The initial and safe set is

```text
K_0=K={0} x {-3,-1,1,3}.
```

The four polynomial values are `0,0,1,1`.  At `n=0`, the successor is safe if
and only if `u=q(z)`, so the interval authority adds no new safe action.  Both
required values lie at distance at least one from the authority boundary.

Local normal control is now explicit.  For `|n|<=1/6` and a desired successor
`|eta|<=3/4`, choose

```text
u=q(z)+eta-(3/2)n.
```

Then `u` remains in `[-1,2]` and the next normal state is exactly `eta`.

## 3. Full-shift cocycle NHIM

Put the bi-infinite mode sequence in the base
`Omega={-3,-1,1,3}^Z`, with invertible shift `theta`, and retain the normal
coordinate in the smooth fiber `X=R`.  The sensor observes the current base
symbol `z_t=omega_t`.  Safe feedback cancels `q(z_t)`, giving

```text
phi(k,omega,n)=(3/2)^k n,  k in Z.
```

This is a cocycle.  The random manifold `M(omega)={0}` satisfies
`phi(k,omega,M(omega))=M(theta^k omega)`.  With

```text
E^u=R, E^c={0}, E^s={0},
exp(alpha)=4/3, exp(beta)=3/2,
```

the unstable restriction is an isomorphism, the center equals the tangent of
the point, the unstable backward bound is equality, and the stable/center
bounds are vacuous.  These conditions hold uniformly for every disturbance
sequence.  They instantiate Definitions 2.1-2.4 of the checked Li-Lu-Bates
random-NHIM source.

The harness checks the cocycle and base-shift group laws for positive and
negative integer times and verifies uniform Bernoulli cylinder-mass invariance.
It also rejects a one-sided-base mutation, which cannot supply the registered
integer-time invertible base used here.

## 4. Causal schedule

At each time the sensor observes `(n_t,z_t)`, emits the read symbol, the
controller emits the current write symbol from reads through time `t`, the
actuator applies `u_t`, and only then does the disturbance select `z_(t+1)`.
No read, write, or control depends on `z_(t+1)` or any later mode.  A one-step
stale controller is infeasible because no one initial control is safe for both
required-action fibers; this counterfactual is separated from the registered
zero-delay schedule.

## 5. Exact regions survive

Under the computed registry the sensor emits `q(z_t)`.  Under the raw registry
it emits an injective label of `z_t`; the controller then computes `q`.  The
plant, interval authority, timing, evaluator, disturbance class, and downstream
maps are identical.  Every mode word occurs, hence for every horizon `T`

```text
computed read words = 2^T,
raw read words      = 4^T,
write words         = 2^T.
```

The exact closed regions remain

```text
computed: [1,infinity) x [1,infinity),
raw:      [2,infinity) x [1,infinity).
```

Thus the v0.6 category gap is repairable without collapsing the same-plant
registry fork.

The audit is mutation-sensitive: discrete-only authority destroys the local
target box, a stale controller fails at the initial modes, closing the
`exp(alpha)<exp(beta)` gap violates normal hyperbolicity, and encoding the next
mode violates causality.

## 6. Consequence and nonclaim

The repaired witness strengthens the harness-backed stopping argument: even a
registered full-shift cocycle NHIM with genuine bounded local control has two
exact capacity regions when the sensor registry is left open.

ASMP-4 does not itself select the random-cocycle NHIM formalism, interval
authority, zero delay, or either sensor registry.  This remains a negative
well-posedness result, not a full variational characterization or canonical
solution.
