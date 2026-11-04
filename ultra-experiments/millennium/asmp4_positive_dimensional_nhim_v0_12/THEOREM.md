# ASMP-4 positive-dimensional NHIM fork theorem v0.12

## Theorem

There is a bounded-authority uncertain plant whose evaluator-safe set contains
a compact connected one-dimensional classical NHIM and whose exact two-port
capacity region still depends on the unspecified sensor registry.

## Plant

Let

```text
theta_next=theta+1/4 mod 1,
n_next=(3/2)n+u-q(z),
z_next=w,
q(z)=(12+13z-z^3)/24,
u in [-1,2],
z,w in {-3,-1,1,3}.
```

Set `K_0=K=S^1 x {0} x {-3,-1,1,3}`.  Since the four `q` values are
`0,0,1,1`, the unique safe control at each mode is `u=q(z)`.  The interval
authority supplies uniform local evaluator-normal control via
`u=q(z)+eta-(3/2)n` for `|n|<=1/6`, `|eta|<=3/4`.

## Classical NHIM certificate

Under safe feedback, the smooth cylinder component is

```text
f(theta,n)=(theta+1/4 mod 1,(3/2)n).
```

This is a global smooth diffeomorphism.  Its invariant circle
`N=S^1 x {0}` has dimension one.  With

```text
E^s={0}, E^u=span(d/dn), TN=span(d/dtheta), lambda=3/4,
```

the unstable inverse norm is `2/3`, the tangent norm is `1`, and both
Definition 1 inequalities are `2/3<3/4`.  Thus `N` is a normally expanded
classical NHIM, not a hyperbolic point relabeled as a manifold.

## Capacity fork

The registered sensor observes the current exogenous mode `z`; the neutral
tangent phase is evaluator-irrelevant and does not cross either interface.
Computed sensing emits `q(z)`, whereas raw sensing emits an injective label of
`z`.  Every mode word occurs and the tangent rotation is independent, so at
every horizon `T`

```text
computed read words = 2^T,
raw read words      = 4^T,
write words         = 2^T.
```

The exact regions remain

```text
[1,infinity) x [1,infinity),
[2,infinity) x [1,infinity).
```

The controller uses the current read before the next disturbance reset and no
future mode.  Both registries share the plant, interval authority, timing,
evaluator, and disturbance class.

## Consequence

The zero-dimensional objection does not collapse the stopping theorem.  Even
a positive-dimensional compact classical NHIM supports the same exact registry
fork.  The safe circle still has zero ambient volume, and ASMP-4 still does not
select this NHIM class or a sensor registry; this is not a full canonical
solution.
