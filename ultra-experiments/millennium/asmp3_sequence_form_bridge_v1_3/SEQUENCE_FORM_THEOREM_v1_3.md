# ASMP-3 perfect-recall sequence-form bridge v1.3

## Status and scope

```text
result_status = exact perfect-recall sequence-form bridge
parent_result = ASMP-3-MATRIX-GAME-BRIDGE-v1.2
interface_mode = WV-FIX
interaction_model = finite rational two-player zero-sum extensive tree
information_condition = typed information sets with perfect recall
changes_parent_problem = false
```

The v1.2 matrix theorem handles simultaneous hidden actions only after an
explicit normal-form payoff matrix is supplied.  A compact extensive protocol
can have exponentially many complete pure strategies.  This theorem constructs
and certifies the sequence form directly from histories and information sets.

## 1. Typed extensive game

A frozen game contains:

- a finite rooted history tree;
- chance nodes with rational transition probabilities;
- maximizing and minimizing player nodes;
- an action registry and information-set identifier at every player node;
- rational zero-sum terminal payoffs; and
- the exact information available to each role through its information sets.

Nodes in one information set must belong to the same player and have identical
action registries.

For player `i`, the own-action sequence at a history records every earlier pair

```text
(information set, selected action)
```

for that player.  Perfect recall requires every node in one information set to
have the same preceding own sequence.  The compiler rejects a merged
information set when those sequences differ.

## 2. Realization constraints

Let `Q_i` contain the empty sequence and every sequence obtained by appending
one action at one information set.  A realization plan `r_i` assigns
nonnegative weight to every sequence.

For the empty sequence:

```text
r_i(empty)=1.
```

For every information set `I` with parent sequence `sigma(I)`:

```text
sum_(a in A(I)) r_i(sigma(I),I:a) = r_i(sigma(I)).
```

Collect these equations as

```text
E_i r_i = e_i,  r_i >= 0.
```

### Lemma 1 (behavior-realization equivalence)

Every behavioral strategy induces a feasible realization plan by multiplying
conditional action probabilities along own sequences.  Conversely, normalize
the child realization weights by their parent weight.  At a zero-weight parent,
choose any registered action distribution.  Perfect recall makes this mapping
well-defined, and it reproduces the original realization plan exactly.

## 3. Chance-weighted sequence payoff

For each terminal history `z`, let:

- `pi_c(z)` be its chance reach probability;
- `sigma_max(z)` and `sigma_min(z)` be the two terminal own sequences; and
- `u(z)` be its maximizing payoff.

The compiler accumulates

```text
A[sigma_max(z),sigma_min(z)] += pi_c(z)u(z).
```

For realization plans `x,y`, the expected payoff is exactly

```text
x^T A y.
```

The chance factor appears in `A`; behavioral reach factors appear once each in
`x` and `y`.

## 4. Compact saddle programs

The maximizing sequence-form program is

```text
maximize    e_min^T p
subject to  E_max x = e_max,
            x >= 0,
            E_min^T p <= A^T x,
```

where `p` is free.  The minimizing dual is

```text
minimize    e_max^T q
subject to  E_min y = e_min,
            y >= 0,
            E_max^T q >= A y,
```

where `q` is free.

### Theorem 1 (perfect-recall sequence saddle)

The programs have equal value.  Matching feasible rational tuples `(x,p)` and
`(y,q)` certify an exact behavioral saddle without enumerating normal-form pure
strategies.

### Proof

For fixed `x`, minimizing `x^T A y` over `E_min y=e_min,y>=0` has LP dual

```text
maximize e_min^T p subject to E_min^T p <= A^T x.
```

Substituting this dual produces the maximizing program.  Reversing the roles
produces the minimizing program.  Feasibility and bounded terminal payoffs give
strong LP duality.  Lemma 1 maps the optimal realization plans to behavioral
strategies.  QED.

The release builds dual potentials bottom-up on the sequence forest and checks
every inequality with exact fractions.

## 5. Information-boundary reproduction

The compiler represents matching pennies in two ways.

### Hidden second action

The two minimizing decision nodes share one information set.  Neither action
is revealed before the minimizer chooses.  Uniform realization plans and
matching dual potentials certify value zero, agreeing with v1.2.

### Revealed second action

The minimizing nodes are separate information sets.  The minimizer conditions
on the first action and forces value `-1`, agreeing with v1.1.

The payoff tree is otherwise the same.  This confirms that the value change is
caused by the registered information structure.

## 6. Nested perfect-recall fixture

A max-min-max game gives the maximizing role a later information set after each
of its own first actions.  Nodes reached after different minimizing actions are
merged only when the maximizer's own prior sequence agrees.

The resulting maximizing realization form contains length-two sequences.  An
exact value-one saddle checks recursive flow constraints, recursive dual
potentials, zero-reach behavior recovery, and the full chance-weighted payoff
calculation.  This prevents the release from testing only one-level matrix
games.

## 7. Signaling-concealment family

For size `k`:

1. chance chooses hidden type `t` uniformly;
2. the maximizer observes `t` and sends signal `s`;
3. the minimizer observes `s` but not `t`, and guesses `g`;
4. payoff is one when `g!=t` and zero otherwise.

The maximizer has one information set per type; the minimizer has one per
signal.  Both have `k` actions at every information set.

Uniform signals hide the type, so every guess succeeds with probability `1/k`.
Uniform guessing caps concealment at the same level.  The exact value is

```text
1 - 1/k.
```

Representation sizes are

```text
pure strategies per role       = k^k,
normal-form payoff entries      = k^(2k),
sequences per role              = 1+k^2,
sequence-payoff entries         = (1+k^2)^2,
explicit terminal histories     = k^3.
```

The release certifies `k=2,...,8` and independently reconstructs every
realization and dual potential.  For `k=2,3`, complete normal-form enumeration
matches the sequence value.

## 8. Imperfect-recall firewall

The negative fixture lets one role choose `L/R`, then merges its later nodes
into one information set as though it forgot its own first action.  The two
nodes have different parent own sequences, so compilation fails with an
explicit perfect-recall error.

The sequence theorem is not silently extended to absent-minded or
imperfect-recall games, where behavioral and mixed strategies can differ.

## 9. Remaining representation boundary

Sequence form is polynomial in the explicit tree, sequence registry, and
information-set registry.  It does not compact an exponentially large history
tree that has only been given implicitly by code or an oracle.

The theorem also assumes:

- two-player zero-sum incentives;
- finite horizons and rational chance;
- fixed information sets and message encodings;
- no interface optimization; and
- a supplied payoff that correctly represents the oversight gap.

General correlated semantic noise can be incorporated only when it is
registered as chance state in the explicit tree or via a separately justified
compact extension.

## 10. Next target

The next ASMP-3 bridge should combine sequence form with a compact registered
noise polytope or finite-state noise controller, then state conditions under
which the robust saddle remains a polynomial-size LP.  This is the direct route
from typed interaction to transcript-conditional joint-noise robustness.

## 11. Claim and novelty boundary

Sequence form and perfect-recall realization plans are standard game theory.
The contribution here is the executable ASMP-3 compiler, exact rational
saddles, information-structure comparison, concealment compression census, and
strict recall firewall.  The package is a closed finite bridge, not a complete
characterization of weak verification or `WV-ADM`.
