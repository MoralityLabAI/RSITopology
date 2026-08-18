# ASMP-9 finite-history stabilization boundary v0.73

Status: **unregistered classical theorem development**.

## Object

Let `Sigma` be a finite alphabet and let a path valuation

```text
F : Sigma* -> R,   F(empty)=0
```

assign a cumulative value to every finite history. For histories `h,h'`, define
future-increment equivalence by

```text
h ~F h'
iff
F(hw)-F(h) = F(h'w)-F(h') for every suffix w.
```

This relation asks whether two histories have exactly the same future reward
increments. It does not assert that `F` is morally correct or behaviorally
identified.

## Theorem 1: minimal history replacement

The quotient by `~F` is the canonical deterministic additive reward machine:

```text
state after h       = [h]~F
transition([h], a)  = [ha]
reward([h], a)      = F(ha)-F(h).
```

The transition and reward are well-defined. Every deterministic additive
reward machine realizing `F` maps histories with the same internal state into
one `~F` class. Consequently:

1. `F` has a finite deterministic reward-machine realization iff `~F` has
   finite index; and
2. the number of `~F` classes is the minimum number of states.

This is the additive-output Myhill-Nerode construction, not a new automata
theorem.

## Theorem 2: conditional finite distinguishing horizons

For a declared deterministic Mealy reward machine with `K` internal states,
start with all states in one class and repeatedly refine by the tuple

```text
(immediate reward on a, class of successor on a) for every a in Sigma.
```

The fixed behavioral partition is reached after at most `K-1` suffix symbols.
Each strict refinement increases the number of classes, so at most `K-1`
strict refinements are possible.

For two declared machines with `K1` and `K2` states, inequivalent registered
start states have a distinguishing word of length at most `K1*K2`. Breadth-first
search in the product state space is constructive: a shortest path reaches a
state pair with unequal outgoing reward, and the mismatching symbol completes
the witness.

These bounds are **conditional on the registered finite-state class**. They do
not establish that an unknown human, model, or environment belongs to it.

## Theorem 3: no unrestricted finite-prefix certificate

For every observation horizon `H >= 0`, consider one observed self-loop symbol
`a` and the two cumulative valuations

```text
F0(a^n) = 0  for all n;
FH(a^n) = 0  for n <= H, and 1 for n >= H+1.
```

They agree on every observed history of length at most `H`. `F0` is a
stationary one-state reward. `FH` is not a stationary reward on the observed
one-state environment: its first increment is zero but its increment at step
`H+1` is one.

The incremental word for `FH` is

```text
0 repeated H times, then 1, then 0 forever.
```

Its residual suffixes give exactly `H+2` future-increment classes: one for each
remaining pulse distance and one post-pulse class. Hence its minimal unary
reward machine has `H+2` states.

Therefore no finite prefix, without an independently registered state bound or
regularity class, can certify open-ended stationarity or a horizon-independent
finite memory bound. Apparent stabilization at a finite horizon is evidence
only relative to a declared class.

## Exhaustive finite verification

The development verifier exhausts:

| Registry | Exact result |
|---|---:|
| All labelled binary-output, binary-input 2-state machines | 256 |
| Depth 0 / depth 1 | 64 / 192 |
| All labelled binary-output, binary-input 3-state machines | 46,656 |
| Depth 0 / depth 1 / depth 2 | 2,916 / 25,596 / 18,144 |
| Unordered 2-state machine pairs with repetition | 32,896 |
| Equivalent / distinguishable pairs | 1,768 / 31,128 |
| Largest observed shortest witness | 3 symbols |
| General product bound in that census | 4 symbols |
| Delayed-prefix controls | every `H=0,...,12` |

The census verifies the finite algorithms and sharp occurrence of depth
`K-1`; it is not the proof of the general theorems.

## ASMP-9 consequence

Version v0.71 supplied a minimal endpoint/time-respecting history replacement
for a bounded path table. Version v0.73 states the open-ended object that table
approximates and separates two claims:

```text
inside a registered K-state class:
    finite distinguishing horizons exist;

without a state/regularity bound:
    every finite prefix has a delayed nonstationary continuation.
```

This closes one finite-prefix overclaim. It does not resolve whether real
values admit a coherent scalar, finite reward machine, stochastic kernel,
relation, or another replacement object.

## Claim boundary

No human preferences, language-model values, causal interventions, stochastic
processes, continuous state spaces, strategic reports, or physical acquisition
are studied. The result does not establish a finite memory bound in nature and
does not resolve ASMP-9.
