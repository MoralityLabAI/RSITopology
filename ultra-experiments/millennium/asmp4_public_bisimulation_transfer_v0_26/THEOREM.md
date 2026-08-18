# Public-history bisimulation transfer theorem

## 1. Costed public-history game

Let the states be reachable public histories, possibly infinitely many. At a
history the controller chooses a registered safe block action type; an
adversarial transition may then choose any registered successor. Each
transition carries an additive nonnegative read/write log-cost vector. Safety
is universal, and a policy's rate is the coordinatewise worst-path limsup
average cost. Policies retain unrestricted causal memory over their observed
history.

This is an additive abstraction of charged transcript growth, not a claim that
every transcript-tree functional is edge additive.

## 2. Exact costed alternating bisimulation

An equivalence relation on public histories is exact when histories in one
class have:

1. the same safety status;
2. the same enabled public action types;
3. for every action type, identical read/write cost vectors; and
4. for every action type, the same set of successor equivalence classes.

The last condition is back-and-forth, not one-way simulation. It preserves all
adversarial public outcomes after quotienting.

## 3. Capacity-region transfer

**Theorem.** The original public-history game and its exact costed alternating
quotient have the same achievable worst-path read/write limsup budget region.

**Proof.** Lift a quotient policy by replacing every raw public history with
its class history. Exact action, cost, safety, and successor matching makes
every lifted raw play project to a quotient play with the identical cost word.
Thus every quotient guarantee holds in the raw game.

Conversely, fix a raw policy. For each finite quotient play, maintain as
private controller memory one representative raw play projecting to it. Use
the raw policy's action at that representative. The back condition supplies a
matching raw successor for every quotient successor, so the representative can
be extended inductively. Every quotient cost word constructed this way is a
cost word of the raw policy. Hence every worst-path vector bound and safety
guarantee transfers to the quotient. Taking all policies proves equality of
the two upward budget regions.

This two-direction representative construction is the strategy transfer; it
uses the full back-and-forth clause at every adversarial step.

This representative strategy may use unbounded causal memory; the quotient is
a finite public sufficient state, not a claim that a memoryless controller is
always optimal.

## 4. Deterministic finite corollary

If the quotient has finitely many classes and every action type has one
successor class, it is the finite additive scheduler of v0.25. Its region is
the component-indexed union of cycle-mean polytopes. If quotient actions retain
several adversarial successor classes, the transfer theorem still holds, but a
separate multidimensional mean-payoff game theorem is required; the one-player
cycle formula cannot simply be reused.

## 5. Decorated-cover harness

Take the strongly connected v0.25 two-state scheduler and decorate every state
with one of `m` raw labels. Raw transitions permute decorations, while their
action type, cost, and target base class remain unchanged. Quotienting away the
decoration is an exact bisimulation for every `m`.

The central harness checks `m=1,...,32`, up to 64 raw states, and compares every
finite vector Pareto frontier through horizon eight. The independent verifier
checks `m=1,...,48`, up to 96 raw states, using five scalar support weights and
horizons through ten. There are zero transfer failures.

## 6. Infinite boundary: Thue-Morse

Consider the deterministic unary public chain `n -> n+1` with cost
`(t_n,t_n)`, where `t_n` is the parity of the number of one-bits in `n`. Its
Thue-Morse recursion is

`t_(2n)=t_n`, `t_(2n+1)=1-t_n`.

Adjacent pairs cancel in the signed sequence `(-1)^(t_n)`, so every partial
signed sum has absolute value at most one. The asymptotic read and write costs
therefore both equal `1/2`.

There is no finite exact stationary quotient. A deterministic unary quotient
with finitely many states eventually repeats a state, making its exact edge
cost sequence eventually periodic. Suppose Thue-Morse had eventual period
`p`. Choose arbitrarily large `k` with the parity of `k` equal to the bit-count
parity of `p-1`. The `k` low bits of `2^k-p` are the complement of the bits of
`p-1`, so `t_(2^k-p)=0`, while `t_(2^k)=1`. These arbitrarily late positions
are distance `p` apart, contradicting eventual periodicity.

For contrast, the parity chain with cost `n mod 2` has the same rate `1/2` and
an exact two-state quotient. Finite exact bisimulation is therefore a
checkable sufficient condition, not a necessary condition for a simple or
computable capacity region.

## 7. Scope

The theorem transfers regions after an exact additive public abstraction is
given. It does not construct such a quotient for arbitrary continuous beliefs,
prove approximate quotients preserve zero-error safety, handle nonadditive
transcript-tree costs, or solve nondeterministic multidimensional mean-payoff
games. Those are the remaining abstraction and robustness frontiers.
