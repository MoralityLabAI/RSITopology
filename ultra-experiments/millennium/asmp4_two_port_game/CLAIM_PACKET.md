# Claim packet: `asmp4.two_port_finite_game` v0.1

## Plain-language claim

Within one finite rational control architecture, read and write capacity can
both be necessary for evaluator-relative confinement. A single controller must
work for the whole initial set; choosing a controller after seeing the initial
cell would be an uncharged side channel.

## Frozen finite game

The plant is

```text
n_(t+1) = a_n n_t + c z_t + u_t + w_t,
z_(t+1) = a_z z_t,
```

with the rational grids in `protocol_v0_1.json`. The safety condition is
`|n_t|<=1`. The sensor quantizes `q=a_n*n+c*z` using the registered ordered
thresholds. A controller receives only that finite symbol and emits a finite
write symbol decoded by the registered action dictionary.

For each `(T,r,w,c,a_z)`, define

```text
F_T = 1{there exists one time-indexed memoryless policy C such that
        for every registered initial state and every disturbance sequence,
        |n_t|<=1 for all t<=T}.
```

The read and write charges are the worst-case fixed alphabet sizes: `r` and
`w` bits per step, with cumulative charges `Tr` and `Tw`.

## Exact finite solver

At each time the solver groups the complete reachable rational state set by
read symbol, enumerates every action assignment to the nonempty symbols, and
propagates both disturbances. One assignment is shared by every state in a
symbol and every initial state. Memoization merges identical rational belief
sets but does not remove policies with distinct effects. A feasible witness is
replayed from all nine initial states; infeasibility means the complete finite
policy grammar was exhausted.

## Liveness and controls

- With `a_n=4/5,c=0,u=0`, zero-rate confinement holds through the registered
  stable horizon.
- With full state and continuous action `u=-q`, the next normal state equals
  the bounded disturbance, separating information scarcity from authority.
- A quantifier-trap fixture has two initial states, one read symbol, and two
  actions: each state is individually controllable, but no universal action
  controls both.
- At zero coupling, tangent growth cannot affect the normal coordinate, so the
  complete feasibility table must be invariant to `a_z`.

## Claim boundary

A pass produces an exact phase map for this finite point grid, sensor grammar,
action grammar, and memoryless policy class. It may calibrate the HRMmmm
interface-budget gate and the Confinement Width numerical suite. It does not
establish a continuous-plant capacity theorem, a general no-compensation law,
or a solution to ASMP-4.
