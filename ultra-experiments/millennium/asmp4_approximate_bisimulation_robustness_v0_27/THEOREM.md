# ASMP-4 epsilon-cost transfer and zero-error margin theorem v0.27

## Registered games

Let `G` and `H` be public-history safety games. At each public state the
controller chooses a registered action type, after which an adversary chooses
a public successor transition. Every state and transition has an exact Boolean
safety status. A transition `e` also has a nonnegative additive two-port cost

`c(e) = (c_R(e), c_W(e))`.

Strategies may retain unrestricted causal public-history memory. A strategy is
safe when every compatible infinite play visits only safe states and safe
transitions. Its coordinate `i` cost is

`sup_play limsup_(T -> infinity) (1/T) sum_(t<T) c_i(e_t)`.

The achievable budget region `R_G` is the upward-closed set of vectors that
bound both coordinates for some safe strategy. The horizon-`T` region
`R_G(T)` is defined identically with cumulative rather than average costs.

## Epsilon-cost alternating bisimulation

A total relation `B` between the public states of `G` and `H` is an exact-
safety epsilon-cost alternating bisimulation when every related pair satisfies:

1. state safety statuses agree exactly;
2. enabled registered action types agree exactly;
3. for every transition of either game under a registered action, the other
   game has a transition under that action whose successor is related, whose
   transition safety status agrees exactly, and whose read and write costs
   each differ by at most `epsilon`;
4. clause 3 holds in both directions.

The full back-and-forth clause is required after every adversarial successor.
It is stronger than output closeness and stronger than a one-way simulation.

## Theorem 1: finite-horizon transfer

If initial states `x B y`, then for every horizon `T` and budget `b`,

`b in R_G(T)  implies  b + T epsilon (1,1) in R_H(T),`

and the converse holds with `G,H` exchanged.

### Proof

Fix a safe `G` strategy. A controller for `H` stores, in addition to the real
`H` history, a representative `G` history ending in a related state. It chooses
the action prescribed by the `G` strategy at that representative. When the
adversary selects an `H` successor, the backward half of clause 3 supplies a
matching `G` successor with related endpoint, identical safety status, and at
most `epsilon` error in each cost. Append that successor to the representative
history and repeat.

Every produced representative is a play compatible with the original `G`
strategy. Exact state and transition safety therefore make every real `H` play
safe. Along paired length-`T` histories, each cumulative coordinate differs by
at most `T epsilon`. Taking coordinatewise adversarial suprema gives the stated
budget shift. Reversing the games uses the forward half of clause 3 and proves
the converse. The representative construction is causal but need not be
finite-memory. QED.

## Theorem 2: asymptotic rate transfer

For each paired play and coordinate `i`,

`|(1/T) sum c_i^G - (1/T) sum c_i^H| <= epsilon`

at every positive horizon. Hence the paired limsups differ by at most
`epsilon`. Applying the two strategy transfers proves

`b in R_G  implies  b + epsilon (1,1) in R_H`

and conversely. If the regions are nonempty, their `l_infinity` Hausdorff
distance is at most `epsilon`. Exact safety also transfers existence of a safe
strategy, so one region is empty exactly when the other is empty.

The constant is sharp: one safe one-state game with loop cost `(0,0)` and a
second with loop cost `(epsilon,epsilon)` are epsilon-cost bisimilar and have
exact corner separation `epsilon`.

## Theorem 3: strict safety margin

Cost closeness does not make Boolean zero-error safety robust. Suppose instead
that safety is registered by a signed observation margin `m`, with `m>0` safe,
and `m` is `L`-Lipschitz. If related observations are at metric distance at
most `delta` and every reachable source observation satisfies the strict
safety margin

`m > L delta`,

then every related observation has positive margin and the exact state-safety
clause follows. The same statement applies to a registered transition margin.

The strict inequality is sharp. At equality, observations with margins
`L delta` and `0` can be `delta`-close while the first is safe and the second
is unsafe. For every `delta>0`, zero-cost self-loop games at those observations
therefore have a nonempty region and an empty region respectively. No finite
rate slack repairs that zero-error feasibility jump.

## Consequences and boundary

- Approximate additive costs cause at most the same per-step asymptotic error;
  the error does not accumulate after normalization.
- Exact safety, or a condition that implies it such as strict metric erosion,
  remains load-bearing.
- A deterministic finite approximate quotient may combine this theorem with
  v0.25, adding `epsilon` coordinate slack to its component cycle region.
- A supplied nondeterministic quotient also transfers, but computing its
  multidimensional adversarial mean-payoff region is a separate problem.
- No finite-quotient construction, nonadditive cost theorem, or canonical
  nonlinear registration is claimed.
