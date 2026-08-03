# Causal encoder collapse theorem v0.22

## Encoder-optimized registration

Use the v0.13 positive-volume collar and any finite two-`q`-class sensor
transducer from v0.18/v0.19. The raw sensor output is now an internal
observation available to a causal sensor encoder; it is not forced to remain
recoverable in the charged read transcript.

The encoder observes the current raw symbol before the current write and has
finite internal memory. Its state is the reachable subset belief `B`,
initialized at the registered initial set `I`. On raw symbol `y`, it performs

`emit c_t = the unique element of Q(B,y)`,

`B_next = Delta(B,y)`.

The normal-cell component remains separately injective and cannot carry mode
or sensor-state information.

## Feasibility equivalence

A universally safe causal encoder-controller exists if and only if every
reachable raw observer transition is current-`q` homogeneous.

### Sufficiency

When the raw observer is homogeneous, the finite belief-tracking encoder emits
the exact current `q` class at every supported step. The controller combines
that bit with the v0.13 normal-cell policy. Raw refinements, probabilities, and
hidden sensor state never cross the charged interface.

### Necessity

Suppose an earliest reachable raw transition has the same raw history and
current symbol under opposite `q` classes. Earlier homogeneous transitions fix
one common prior `q` history, so the two executions can share the same normal
transcript and pre-step normal value `n`. Any downstream causal encoder sees
the same raw and normal histories and must emit the same charged transcript.
One current write would need to lie in both `[-1-2n,1-2n]` and
`[7-2n,9-2n]`, which is impossible. Randomization independent of the plant
cannot repair this worst-case collision.

Thus downstream encoding can discard resolved raw information, but it cannot
create information absent from a mixed raw observation.

## Exact encoder-optimized region

Every binary `q` word is possible under arbitrary mode disturbance. Therefore
the causal encoded language has exactly `2^T` words. For an initial normal
radius `0<rho<=1`, the normal spanning number is
`ceil(rho*2^T)`. The `q` word and normal cell vary independently, giving exact
counts

- reads: `2^T ceil(rho*2^T)`;
- writes: `2^T ceil(rho*2^T)`.

Every feasible finite sensor experiment consequently has exact region

`[2,infinity) x [2,infinity)`.

Every infeasible raw observer has an empty region under this registration.

## Static-versus-causal separation

Consider the two-state, three-output support

- `(state 0,q=0) -> (y=0,state 1)`;
- `(state 0,q=1) -> (y=1,state 0)` or `(y=2,state 0)`;
- `(state 1,q=0) -> (y=0,state 0)` or `(y=1,state 0)`;
- `(state 1,q=1) -> (y=2,state 0)`.

From belief `{0}`, `y=1` means `q=1`; from belief `{1}`, the same `y=1`
means `q=0`. All five static partitions of three raw symbols are exhausted.
Only the discrete three-block partition is feasible, with observer adjacency
`[[2,1],[3,0]]`, spectral radius 3, and raw language `3^T`.

The causal encoder tracks the two beliefs and emits the contextual `q` value,
so its language is `2^T`. Static memoryless coarsening is therefore strictly
weaker than causal encoder optimization.

## Exhaustive inheritance checks

- Among the 256 deterministic two-state binary-output transducers, the same 80
  raw-feasible members all encode to `2^T`; the 176 mixed members remain
  impossible.
- Among the 53,108 memoryless support relations through four outputs, all 724
  feasible kernels collapse to the computed region and all 52,384 infeasible
  kernels remain impossible.
- Computed, raw, golden, history-toggle, and contextual fixtures have different
  forced-raw spectral radii but the same encoder-optimized read corner 2.

Central frozenset and independent integer-mask implementations reproduce the
theorem and both censuses.

## Relation to v0.20 and v0.21

V0.20 showed that forced-raw entropy is not plant-only. V0.21 removed exact
duplicate support labels but deliberately retained other raw distinctions.
V0.22 executes the stronger encoder-optimized route: once causal processing is
allowed, the sensor sends only the control-relevant current `q` class. This
resolves the declared finite local family under encoder-optimized semantics,
not the source's entire nonlinear class.

## Scope

The theorem requires finite sensor state, two arbitrary current `q` classes,
same-step raw observation before writing, sufficient encoder memory, universal
support safety, and the v0.13 collar plant. It does not cover delayed sensing,
restricted or absent encoder memory, forced-raw retention, continuous
observations, more general control statistics, or the global nonlinear ASMP-4
variational problem.
