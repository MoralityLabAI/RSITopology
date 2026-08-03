# ASMP-4 causal transcript-fiber entropy theorem v0.28

## 1. Nonadditive port cost

For a safe public-history strategy `sigma`, let `L_i^G(sigma,T)` be the set of
realized length-`T` transcripts on port `i` in game `G`, where `i` is read or
write. Register the horizon cost and rate

`J_i^G(sigma,T) = log2 |L_i^G(sigma,T)|,`

`h_i^G(sigma) = limsup_(T -> infinity) J_i^G(sigma,T)/T.`

This is a whole-language cost. It need not decompose into edge costs. The
achievable region is the upward closure of rate vectors of universally safe
strategies.

## 2. Port-compatible causal factors

Suppose a representative-history construction transfers every safe source
strategy `sigma` in `G` to a safe target strategy `tau` in `H`. For each port
and horizon, also register a total port-compatible map

`phi_(i,T): L_i^H(tau,T) -> L_i^G(sigma,T).`

The map must depend causally on the registered transcript factor, not on hidden
future information. Define its maximum fiber

`M_i^(G->H)(T) = max_u |phi_(i,T)^(-1)({u})|,`

using a uniform bound over the strategies under consideration. A reverse
strategy transfer requires its own maps and fiber profile. One direction does
not imply the other.

## 3. Finite-horizon theorem

For every source strategy and its target transfer,

`|L_i^H(tau,T)| <= M_i^(G->H)(T) |L_i^G(sigma,T)|.`

Therefore

`J_i^H(tau,T) <= J_i^G(sigma,T) + log2 M_i^(G->H)(T).`

### Proof

Partition the target language into fibers of `phi_(i,T)`. There are at most
`|L_i^G|` nonempty fibers, and every fiber has at most `M_i(T)` elements.
Summing their cardinalities gives the first inequality; applying `log2` gives
the second. QED.

The maximum is load-bearing. A map with two source words and target fiber
sizes `2^T` and `1` has target size `2^T+1`; its minimum fiber is one but its
rate gap tends to one.

## 4. Relative fiber-entropy theorem

Define the directional port-fiber entropy

`mu_i^(G->H) = limsup_(T -> infinity) log2 M_i^(G->H)(T)/T.`

Taking normalized limsups in the finite-horizon inequality gives

`h_i^H(tau) <= h_i^G(sigma) + mu_i^(G->H).`

Thus every source budget `b` transfers to target budget

`b + (mu_R^(G->H), mu_W^(G->H)).`

The reverse factor gives the reverse directed inclusion with its own vector.
If both port fibers are subexponential in both directions, all four `mu`
values vanish and the complete upward capacity regions are equal. Uniformly
bounded fibers are sufficient but not necessary.

The `limsup` cannot be replaced by `liminf`. Alternate increasingly long
nonbranching rests with branching blocks as long as the preceding rest. At
rest endpoints the branching fraction tends to zero; at branch endpoints it
tends to one half. The relative fiber entropy is governed by the latter
subsequence.

## 5. Sharp exponential clone obstruction

Take a safe finite raw game with `r*w` public states labelled by a read symbol
in `{1,...,r}` and a write symbol in `{1,...,w}`. From every state, one fixed
controller action permits every labelled successor. Give all transitions zero
additive cost and quotient all raw states to one safe state with one successor
class.

The quotient is an exact state-safety/action/successor-class abstraction in the
v0.26 sense: successor-class sets and zero edge costs agree. Nevertheless,

`|L_R^raw(T)|=r^T,   |L_W^raw(T)|=w^T,`

while both quotient languages are singletons. The raw-to-quotient transcript
fibers are exactly `r^T` and `w^T`, so the corner shift

`(log2 r, log2 w)`

attains the theorem. A finite one-class state quotient can therefore hide
positive history-fiber entropy. State-class size is not a substitute for
history-fiber growth.

This is the quotient-level generalization of the v0.20 raw-label clone
obstruction. Bijective alphabet relabeling preserves language cardinality;
cloning is many-to-one and is not a relabeling.

## 6. Unbounded zero-entropy fibers

Let extra binary or ternary branching occur only at times `1,2,4,8,...`. By
horizon `T` there are `T.bit_length()` branching events. Hence

`M_R(T)=2^{bit_length(T)},   M_W(T)=3^{bit_length(T)}.`

The fibers are unbounded and polynomial in `T`, but

`log2 M_i(T)/T -> 0.`

The exact-region corollary therefore requires subexponential, not uniformly
bounded, fibers.

## 7. Scope

The theorem covers nonadditive log-cardinality of realized port languages. A
different transcript-tree functional transfers when it has its own registered
distortion modulus under the causal factor maps; no such property is inferred
from bisimulation alone. The theorem does not construct a quotient for an
arbitrary nonlinear plant and does not compute multidimensional adversarial
mean-payoff regions.
