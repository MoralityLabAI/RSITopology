# Exact finite-MDP access geometry separates soft policies from action identities

## Result

For a finite discounted MDP with known transition kernel `P`, discount
`0 < gamma < 1`, entropy temperature `tau`, and a full-support soft-optimal
policy `pi`, every compatible state-action reward has the form

```text
r(s,a) = tau log pi(a|s) + G_(P,gamma)V(s,a),

G_(P,gamma)V(s,a)
  = V(s) - gamma sum_t P(t|s,a)V(t).
```

The shaping operator is injective, so one exact soft policy leaves exactly
`S` reward dimensions ambiguous. For policies observed in several
environments, the common ambiguity is exactly

```text
intersection_e im G_e.
```

Global reward constants always survive. One-dimensional ambiguity is
therefore the strongest possible identification in this access model.

## Sharp structured access theorem

Use a self-loop reference environment, in which every action remains in its
current state. For a second transition kernel `P`, define

```text
A_P[(s,a),t] = P(t|s,a) - P(t|s,a_0).
```

Then

```text
dim(im G_0 intersect im G_P) = S - rank(A_P).
```

When `P` is deterministic, `A_P` is an incidence matrix. Join two successor
states whenever two actions available at one source state lead to those
successors. If this successor-difference graph has `c` connected components,
then

```text
dim(im G_0 intersect im G_P) = c.
```

Consequently, within this registered intervention grammar:

- one environment leaves `S` dimensions;
- two environments are necessary to reduce ambiguity below `S`; and
- the self-loop reference plus one second environment identify reward up to a
  global constant exactly when the successor-difference graph is connected.

For the cyclic two-action kernel, observing the same soft policy at two
distinct discounts also reduces the common ambiguity to one global constant.
Repeating the same discount does not.

These entropy-regularized identifiability facts sit below the more general
theory of Cao, Cohen, and Szpruch (2021). Novelty is not claimed. The
contribution here is an explicit access grammar, exact component formula,
prospectively registered census, and matched access counterexample.

## Matched deterministic-policy obstruction

The positive result depends on observing full stochastic policy
probabilities. It does not transfer to deterministic action identities.

In both the self-loop and cyclic environments, set

```text
r(s,a_0) = 1,
r(s,a_1) = 0.
```

Changing only `r(0,a_1)` from `0` to `1/2` preserves the same strict
action-zero policy in both environments. The reward difference is not a
global constant, even though the matched soft-policy access has only
one-dimensional common shaping ambiguity.

Thus two environments can be sufficient under exact soft-policy access and
insufficient under deterministic-policy access. The distinction is the
information content of the observation, not merely the number of
environments.

## Registered verification

The theorem, prior-art boundary, implementation, tests, environment, resource
limits, protocol, and runner were frozen at commit `5612622` and hash-sealed
in the separate registration commit `f54cbb1` before the fresh cells ran.

All eleven gates passed:

- all `65,536` deterministic four-state, two-action kernels matched both the
  rank formula and the successor-component formula;
- their ambiguity distribution was
  `{1: 27,264, 2: 31,776, 3: 6,240, 4: 256}`;
- all `4,096` fresh strictly positive rational stochastic kernels matched the
  rank formula and had injective shaping operators;
- the fresh stochastic sample exercised every registered state count
  `2..8`, action count `2..3`, and discount;
- all structured state counts `17..32` exhibited the registered
  one-environment, two-environment, same-discount, distinct-discount, and
  deterministic-policy outcomes;
- all `32,768` query graphs on six direct-return coordinates had ambiguity
  equal to graph component count;
- constant-only direct-return ambiguity first occurred at five comparisons,
  the sharp tree threshold `D-1`; and
- the run used no GPU, finished in `193.60` seconds, and peaked at
  `21,299,200` resident bytes under the registered `240`-second and `2`-GiB
  limits.

An independent artifact verifier passed. A second clean execution produced a
byte-identical report and identical scientific fields after excluding runtime
and peak-memory measurements. All `200` dedicated tests passed after the run;
the preregistration repository-wide check passed all `225` tests.

Because the frozen deterministic-policy helper encoded its analytic gaps
directly, a separately written post-run verifier also reconstructed both
transition kernels and solved all 64 fixed-policy Bellman systems with exact
rational arithmetic. Every gap was strictly positive, with minima `1` and
`1/2` in the base and perturbed arms. This check is explicitly diagnostic,
not represented as a preregistered gate.

## ASMP-9 contribution and remaining gap

This closes one finite-MDP access subproblem: it computes the exact residual
reward quotient for a registered family of transition and discount
interventions, proves sharp structured thresholds, and shows why those
thresholds fail for a weaker deterministic-policy observation.

It does **not** resolve ASMP-9. The result assumes:

- exact population policies;
- known entropy temperature;
- known finite transition kernels and discounts;
- state-action rewards;
- full-support entropy-regularized optimality; and
- deliberately chosen environments.

It does not cover finite-sample policy estimation, unknown temperature,
passive demonstrations, continuous MDPs, non-entropy-regularized policies,
contextual or history-sensitive preferences, or a general optimum for
environment design. The next load-bearing problem is a two-sided
contextual/history-sensitive scalar-existence classification.
