# ASMP-3 realization-flow bridge theorem v1.0

## Status and scope

```text
result_status = exact acyclic single-controller bridge
parent_result = ASMP-3-POLYHEDRAL-TV-FRONTIER-v0.9
interface_mode = WV-FIX
interaction_model = frozen finite acyclic fully observed controlled graph
changes_parent_problem = false
```

The v0.9 theorem is efficient when the complete truthful and false terminal-law
sets have compact rational polyhedral descriptions.  This theorem derives such
a description directly from one nontrivial protocol model: a frozen acyclic
controlled stochastic graph.

The model has one fully observed strategic controller.  It does not cover two
independently strategic advocates or an adaptive verifier whose choices are
optimized jointly with theirs.

## 1. Frozen controlled graph

Let:

- `S={s_1,...,s_k}` be nonterminal states in topological order;
- `Z` be terminal observations;
- `A(s)` be the finite action registry at state `s`;
- `mu(s)` be a rational initial distribution;
- `K(v | s,a)` be a rational transition channel to a later state or terminal;
- the current state be exactly the information available to the controller.

Every channel is normalized, and transitions between nonterminal states move
strictly forward in the order.  A randomized policy gives a distribution
`pi(a|s)` at every state.

Define the state-action occupancy

```text
x(s,a) = Pr[the process reaches s and chooses a].
```

## 2. Realization-flow polytope

The occupancy variables satisfy

```text
x(s,a) >= 0,

sum_(a in A(s)) x(s,a)
  = mu(s)
    + sum_(r before s) sum_(b in A(r)) K(s|r,b)x(r,b).
```

The terminal law is the linear image

```text
p(z) = sum_s sum_(a in A(s)) K(z|s,a)x(s,a).
```

### Theorem 1 (policy-flow equivalence)

The terminal laws induced by all randomized policies are exactly the linear
image of the nonnegative realization-flow polytope above.

### Proof: policy to flow

Propagate reach probabilities in topological order and set

```text
x(s,a)=reach(s)pi(a|s).
```

Conservation of probability gives every flow equality.  Summing the terminal
transition mass gives the displayed terminal law.

### Proof: flow to policy

For a feasible flow, let

```text
u(s)=sum_a x(s,a).
```

If `u(s)>0`, define `pi(a|s)=x(s,a)/u(s)`.  If `u(s)=0`, choose any registered
action distribution.  Induct in topological order.  The flow equality makes
the process's reach probability at `s` equal to `u(s)`, so the reconstructed
occupancy at a positive-flow state is

```text
u(s)pi(a|s)=x(s,a).
```

At a zero-flow state, nonnegativity gives `x(s,a)=0` for every action, and the
state remains unreachable.  Thus the policy reproduces all occupancies and the
terminal law exactly.  QED.

This also shows that allowing additional history dependence cannot enlarge the
terminal-law set when the registered state is the complete allowed information:
normalizing its occupancy produces an equivalent state-based randomized policy.

## 3. Extended polyhedral formulation

The law set need not be projected into an explicit H-representation.  Retain
`x` and `p` together:

```text
x >= 0,
Flow x = mu,
p = TerminalMap x.
```

This is a rational extended formulation with:

- one variable per registered state-action pair;
- one flow equality per nonterminal state; and
- one terminal-map equality per terminal observation.

Substitute one truthful and one false copy of these constraints into the v0.9
TV-distance LP.  The resulting LP minimizes

```text
(1/2)||p_H-p_F||_1
```

without enumerating pure policies or projecting the realization flows.  Its
size is polynomial in the explicit graph and terminal alphabet.

## 4. Exponential policy registry, linear flow registry

The certified band family has `k` initially equiprobable controlled states and
two actions at each.  Each action immediately produces binary terminal output.

For the truthful class, the two actions produce zero with probabilities

```text
4/5 and 9/10.
```

For the false class, they produce zero with probabilities

```text
1/10 and 1/5.
```

At size `k`:

```text
pure policies per class = 2^k,
occupancy variables per class = 2k,
flow equalities per class = k.
```

Randomized policies realize every zero-probability in the two intervals

```text
P_zero=[4/5,9/10],
Q_zero=[1/10,1/5].
```

Accepting on zero therefore has exact gap `4/5-1/5=3/5`.  The artifact checks
flow reconstruction for `k=1,...,12` and enumerates all pure policies through
`k=8`, where the extrema match exactly.

## 5. Adaptive multi-stage fixture

The second fixture contains a root action, a rational chance transition to one
of two later observed states, and state-dependent terminal actions.  It checks:

1. forward policy-to-occupancy propagation;
2. every state-flow equality;
3. normalization back to a policy;
4. exact reproduction of occupancy and terminal law; and
5. the complete eight-policy deterministic registry.

This demonstrates an adaptive graph rather than only a one-step mixture.

## 6. Complexity and representation boundary

The theorem avoids pure-policy enumeration, but it is polynomial only in the
explicit controlled graph.  It does not compress an exponentially large
history tree whose states have not already been represented compactly.

The one-controller assumption is also material.  With multiple independently
strategic roles, terminal probabilities can be multilinear in separate
behavior strategies, and the set of jointly induced laws need not be one
convex flow polytope.  Zero-sum sequence form, correlated-strategy registries,
or stronger saddle-point arguments are then required.

Similarly, the theorem does not cover:

- imperfect recall or hidden controller information;
- endogenous changes to the message alphabet or stopping rule;
- nonconvex restrictions on randomized policies;
- unregistered history-dependent noise; or
- optimization over admissible interfaces in `WV-ADM`.

## 7. Next target

The next safe extension is a frozen two-role zero-sum extensive-form lane with
perfect recall.  A successful bridge must retain separate realization plans,
show exactly how chance/noise enters the bilinear payoff, and prove that the
terminal-verifier objective has a valid sequence-form saddle-point LP.  It must
not silently replace independent strategies by a correlated joint controller.

## 8. Claim and novelty boundary

Occupancy measures and flow formulations for finite controlled stochastic
processes are standard.  The contribution here is the exact ASMP-3 bridge from
protocol execution to the v0.9 terminal-law LP, the rational reconstruction
receipts, and the explicit point where the single-controller convexity argument
stops.  This is not a characterization of general interactive oversight.
