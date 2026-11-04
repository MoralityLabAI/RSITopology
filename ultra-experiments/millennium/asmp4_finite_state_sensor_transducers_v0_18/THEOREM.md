# Finite-state support-zero-error sensor theorem v0.18

## Registered architecture

Use the v0.13 positive-volume collar. The physical mode contribution is
`q(z) in {0,8}`; write `c(z)=q(z)/8 in {0,1}` for its control-relevant class.
The disturbance may choose every mode at every time.

A registered sensor transducer consists of a finite hidden state set `S`, a
known initial state `s0`, a finite raw-output alphabet `Y`, and a nonempty
event support

`E(s,z) subseteq Y x S`

for every `(s,z)`. At a step, an event `(y,s_next)` in `E(s,z)` emits `y` and
updates the hidden sensor state. The controller sees the raw-output history
before writing, but it never sees the sensor state.

The read transcript is the pair of two separately charged components:

1. the raw output word, which remains injectively recoverable; and
2. the normal-cell symbol, which depends only on the initial normal coordinate
   and cannot encode the mode, sensor state, or transducer event.

Thus all possible raw words cross with all required normal cells. Safety is
universal over every disturbance word and every supported event word. This is
a support-zero-error contract, not an average-error channel model.

## Reachable subset observer

Let `B subseteq S` be the controller's set of possible pre-step sensor states,
starting at `B_0={s0}`. For a raw symbol `y`, define

`Delta(B,y)={s_next : s in B, z allowed, (y,s_next) in E(s,z)}`

and

`Q(B,y)={c(z) : s in B, (y,s_next) in E(s,z) for some z,s_next}`.

Ignore symbols with empty `Delta(B,y)`. A belief is reachable when repeated
nonempty `Delta` transitions reach it from `B_0`.

## Feasibility theorem

The registered transducer is feasible if and only if every reachable
subset-observer transition `(B,y)` has a singleton current `q`-class set
`Q(B,y)`.

### Sufficiency

At every reachable transition, the singleton value decodes the current
`q=8c` from the observed raw history. Combine it with the v0.13 normal-cell
controller. The raw sensor history may leave the hidden state ambiguous, but
the hidden state is irrelevant once the current `q` class is known. The
controls stay in `[-2,10]`, and every supported execution stays in the collar.

### Necessity

Suppose a reachable transition has two witnesses with the same observed `y`
and opposite current classes. Choose the earliest mixed transition on a raw
history reaching such a witness. Every earlier transition on that history is
homogeneous, so the shared earlier raw history fixes one earlier `q` history.
Choose the same normal cell in both executions. Because the normal symbol has
no mode or sensor-state side channel, the controller has issued the same
residual policy and the two executions have the same pre-step normal value
`n`.

The current read transcripts are identical. One causal write must therefore
serve both witnesses. Safety for `q=0` requires
`u in [-1-2n,1-2n]`, while safety for `q=8` requires
`u in [7-2n,9-2n]`. These intervals are disjoint for every common `n`.
Universal support safety is impossible. This earliest-violation argument also
shows why checking only global current-symbol overlap is too strong: a raw
history can resolve the hidden sensor state before an otherwise ambiguous
symbol is interpreted.

## Exact language and spectral formula

The reachable subset observer is a deterministic labeled graph. Let

`A_(B,B') = |{y in Y : Delta(B,y)=B'}|`

be its multiplicity adjacency matrix, and let `L_T` be the number of accepted
raw output words of length `T` from `B_0`. Exactly,

`L_T = e_(B_0)^T A^T 1`.

Every observer state is reachable by construction and has an outgoing edge
because every event support is nonempty. Standard finite nonnegative-matrix
growth therefore gives

`lim_(T->infinity) (1/T) log2 L_T = log2(rho(A))`.

For an initial normal collar `[-rho,rho]`, `0<rho<=1`, the exact number of
normal cells remains `N_T(rho)=ceil(rho*2^T)`. Raw-output charging and the
separate normal component make every `(raw word, normal cell)` pair distinct,
so exact read words are

`L_T ceil(rho*2^T)`.

All `2^T` current `q`-class words remain possible. The v0.13 first-difference
argument makes their write languages disjoint, while normal expansion needs
`ceil(rho*2^T)` cells for each class word. Exact write words are

`2^T ceil(rho*2^T)`.

Consequently every feasible transducer has the exact full-collar region

`[1+log2(rho(A)),infinity) x [2,infinity)`.

An infeasible transducer has an empty safety-capacity region under this
registered universal-support contract.

## Separating fixtures

- The computed memoryless sensor has `L_T=2^T`, `rho(A)=2`, and read corner 2.
- The raw memoryless sensor has `L_T=4^T`, `rho(A)=4`, and read corner 3.
- The golden-refinement transducer has adjacency
  `[[2,2],[2,0]]`, hence `L_T=2^T F_(T+2)`,
  `rho(A)=2 phi`, and read corner `2+log2(phi)`.
- The history-toggle transducer has globally overlapping current output
  supports, but its known alternating hidden state makes every reachable
  transition homogeneous. It has `L_T=2^T` and is feasible.
- The one-symbol overlap transducer has a reachable mixed transition and is
  infeasible at the first step.

## Complete two-state deterministic census

For two hidden states, two `q` classes, binary raw output, fixed initial state
zero, and one deterministic `(output,next-state)` choice for each of the four
`(state,q)` pairs, there are `4^4=256` transducers. Exhaustion gives:

- 80 feasible and 176 infeasible;
- 32 feasible by globally disjoint output supports;
- 48 additional history-essential feasible transducers whose global supports
  overlap but whose reachable beliefs decode `q`;
- feasible observer-belief histogram `{1:32,2:48}`; and
- every feasible member has `L_T=2^T` and `rho(A)=2`.

The central frozenset observer and an import-independent integer-bitmask
observer reproduce the same census.

## Scope

The result classifies fixed finite registered transducers with a known initial
sensor state, raw-output charging, arbitrary mode disturbances, and universal
support safety. It does not cover an unknown initial sensor state, continuous
or infinite sensor memory, controller-side compression of raw outputs,
expected length, average or block error, or asymptotically vanishing failure.
It is a complete theorem for this registered local family, not the global
coordinate-invariant nonlinear variational characterization requested by
ASMP-4.
