# Exact positive continuation boundary for a Lipschitz risk class

## Registered class

Let `Theta` be a compact metric space, `F` a finite source set, and for each
action `a` let safety loss `l_a` and utility `u_a` range independently over
functions satisfying frozen Lipschitz bounds `K_L` and `K_U`. Assume their
population values are known on `F`.

Define the exact envelopes

```text
Upper_L(a,x) = min_(z in F) [l_a(z) + K_L d(x,z)],
Lower_U(a,x) = max_(z in F) [u_a(z) - K_U d(x,z)].
```

## Theorem

An action is uniformly safe and useful for **every** continuation consistent
with the registered source values if and only if

```text
sup_(x in Theta) Upper_L(a,x) <= epsilon
and
inf_(x in Theta) Lower_U(a,x) >= u_0.
```

### Proof

Every admissible Lipschitz continuation lies below `Upper_L` and above
`Lower_U` by the Lipschitz inequalities. Conversely, the McShane upper
extension and Whitney lower extension interpolate the source values with the
same Lipschitz constants. Since the registered loss and utility classes are an
independent product, either failed envelope inequality is attained by an
admissible continuation and defeats the certificate.

This is an exact necessary-and-sufficient local-to-global theorem for the
registered class, not merely a union-bound sufficient condition.

## Covering corollary

Let

```text
h(F) = sup_(x in Theta) min_(z in F) d(x,z)
```

be the fill distance. If every source loss is at most `epsilon-gamma_L` and
every source utility is at least `u_0+gamma_U`, then certification follows from

```text
K_L h(F) <= gamma_L,
K_U h(F) <= gamma_U.
```

These inequalities are worst-case sharp for constant source values because
the envelope at a farthest point equals the source boundary plus the
corresponding Lipschitz radius.

Thus the positive-margin environment complexity is the covering number of
`Theta` at radius

```text
min(gamma_L/K_L, gamma_U/K_U).
```

Without a positive margin this radius is zero, recovering the dense-source
impossibility in `THEOREM_v0_2.md`.

## Active design

For the frozen class, an exact next environment minimizes the post-query
worst envelope, or equivalently in the constant-margin control minimizes the
new fill distance:

```text
x* in argmin_x h(F union {x}).
```

This is the decision-specific active rule. Greedy selection by another
surrogate need not be multi-step optimal, consistent with the existing
ASMP-2 active-design census.

## Finite samples

If each source value is estimated with simultaneous error at most `eta`, the
same theorem applies after replacing source losses by upper confidence values
and source utilities by lower confidence values. For independent bounded
observations, Hoeffding gives the sufficient per-cell size

```text
n >= log(4 |F| |A| / delta) / (2 eta^2).
```

Binary testing supplies the matching `eta^-2 log(1/delta)` order. Exact
constants and dependence corrections remain properties of the registered
source experiment, captured by the safety deficiency in
`DECISION_DEFICIENCY_REDUCTION_v0_3.md`.

## Exact harness cell

On `Theta=[-1,1]`, take `K_L=1/4`, source losses `7/16`, and threshold `9/16`.

- With endpoint sources only, `h=1` and the exact upper envelope at zero is
  `11/16`: certification fails.
- Adding the midpoint gives `h=1/2` and worst upper envelope `9/16`:
  certification holds exactly at the registered margin.

The rational harness checks both envelope values and the margin-cover identity.

## Scope

This theorem supplies a complete positive continuation result for a broad
metric Lipschitz class. It is classical optimal-recovery machinery and is not,
by itself, a novel resolution of the whole semiparametric ASMP-2 program. Its
role is to show precisely which missing quantitative inputs—metric,
smoothness, and margin—turn the negative density theorem into a finite
certificate.
