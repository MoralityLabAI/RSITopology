# ASMP-3 two-role backward bridge theorem v1.1

## Status and scope

```text
result_status = exact perfect-information two-role bridge
parent_result = ASMP-3-REALIZATION-FLOW-BRIDGE-v1.0
interface_mode = WV-FIX
interaction_model = finite acyclic turn-based perfect-information zero-sum game
changes_parent_problem = false
```

The v1.0 realization-flow bridge uses one strategic controller.  Treating
several independent roles as that controller would incorrectly convexify their
strategy products.  This theorem handles two opposed roles without that step,
under public perfect information and turn-based play.

## 1. Frozen zero-sum protocol game

Let nonterminal states be topologically ordered.  Each state belongs to either
the maximizing role `V` or minimizing role `D`.  The owner chooses a registered
action, after which a rational chance channel moves to a later state or a
terminal.  A terminal `z` has rational payoff `u(z)` to `V` and `-u(z)` to `D`.

Both roles observe the full current state and all earlier public actions.  The
message alphabet, state graph, stopping behavior, transitions, information,
and payoff are frozen game data.

For an oversight interpretation, `u` must already encode the declared
completeness-versus-soundness objective.  The theorem solves the resulting
game; it does not decide how an ambiguous ASMP-3 instance should be compiled
into that payoff.

## 2. Exact backward recursion

Set `v(z)=u(z)` at terminals.  In reverse topological order define

```text
v(s) = max_(a in A(s)) sum_w K(w|s,a)v(w)  if owner(s)=V,

v(s) = min_(a in A(s)) sum_w K(w|s,a)v(w)  if owner(s)=D.
```

Choose any registered optimizing action at each state.  Let `sigma*` and
`tau*` be the resulting deterministic strategies for `V` and `D`.

### Theorem 1 (perfect-information saddle)

The initial backward value `v*` satisfies

```text
E[u | sigma*, tau] >= v*  for every minimizing strategy tau,

E[u | sigma, tau*] <= v*  for every maximizing strategy sigma.
```

Consequently `(sigma*,tau*)` is a saddle, the game value is `v*`, and pure
state-based strategies suffice.

### Proof

Induct backward over states.  At a maximizing state, the selected action has
expected continuation value at least that of every alternative, assuming the
inductive continuation guarantees.  At a minimizing state, the selected
action has expected continuation value at most every alternative.  Rational
chance averaging preserves the inequalities.  The terminal case is equality.

Applying the two inductive inequalities from the initial distribution gives
the displayed deviation bounds.  Their intersection gives equality at the
selected pair and proves the saddle.  QED.

The algorithm uses one rational expectation per state-action transition; it
does not enumerate complete pure strategies.

## 3. Exponential challenger family

The certified family has one maximizing verifier state with `k` candidate
tests.  Test `i` moves to its own minimizing challenge state with two attacks.
The last test guarantees win probability `3/5`; every earlier test has a lower
worst-case probability.

At size `k`:

```text
maximizer pure strategies = k,
minimizer pure strategies = 2^k,
states = k+1,
registered action evaluations = 3k,
game value = 3/5.
```

The artifact checks `k=1,...,12`.  It enumerates every strategy deviation
through `k=8`; beyond that, the exact backward certificate proves the same
saddle without exponential enumeration.

This is the multi-role analogue of the v1.0 flow compression: strategy spaces
may be exponential while the frozen public game has a linear recursion.

## 4. Alternating three-stage fixture

The second game alternates

```text
max -> min -> max -> rational terminal channel.
```

Backward induction gives exact value `7/10`.  The release enumerates all 32
maximizer strategies and four minimizer strategies, verifying both reciprocal
deviation inequalities against the constructed saddle.

## 5. Information-structure boundary

Perfect information is not cosmetic.  The release compares matching pennies
under two information structures.

### Revealed sequential play

The maximizing role chooses `H/T`; the minimizing role observes that action
and then chooses.  Backward induction gives value `-1` to the maximizer because
the minimizer always mismatches.

### Hidden simultaneous play

For the same payoff matrix

```text
[[ 1,-1],
 [-1, 1]],
```

the maximizer's pure maximin is `-1`, but a half/half hidden mixed strategy has
value zero.  The sequential perfect-information graph is therefore not a
valid representation of the simultaneous game.

This countercheck prevents the backward theorem from being applied to private
messages, simultaneous advocate moves, or nontrivial information sets merely
by imposing an arbitrary public order.

## 6. Relation to ASMP-3

The theorem closes a two-role `WV-FIX` lane when all of the following are part
of the frozen specification:

1. a finite acyclic public state graph;
2. turn-based perfect information;
3. rational registered chance/noise channels;
4. a zero-sum payoff equal to the target verifier gap; and
5. polynomial graph size relative to the declared resource parameter.

Under those assumptions, a constant positive backward value is exactly a
constant guaranteed gap, and the optimizing strategy is constructive.

The theorem does not cover general debate or oversight protocols with hidden
semantic information, simultaneous messages, private randomness that changes
information sets, imperfect recall, or interface selection.

## 7. Next target

The next extension must use sequence form for finite perfect-recall
imperfect-information games.  It must type each information set, realization
constraint, chance/noise coefficient, and payoff entry, and must compare the
sequence-form saddle against normal-form enumeration on small games.  The
matching-pennies boundary is the first mandatory fixture.

## 8. Claim and novelty boundary

Backward induction for finite perfect-information zero-sum games is standard.
The contribution here is its exact typed placement in the ASMP-3 chain, the
rational saddle receipts, the exponential-strategy audit, and the explicit
information boundary.  This is not a general characterization of interactive
weak verification.
