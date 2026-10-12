# ASMP-9 v0.52 deterministic direct-map completeness

## Status

Development theorem. The result is a finite self-ordering corollary of
classical Buehler optimality. It is registered here to close an ASMP-9
obligation, not to claim mathematical novelty.

## Finite object

Let `X={x_1,...,x_n}` be a finite outcome set. Let `Theta` be a parameter set,
`d(theta)` a scalar risk, `P_theta` a probability law on `X`, and
`alpha in (0,1)`.

For every subset `S` define

```text
B(S) = sup { d(theta) : P_theta(S) > alpha },
```

with the normalized bottom value when the set is empty. A deterministic
direct upper map `u:X->R` is valid when

```text
P_theta(u(X) < d(theta)) <= alpha
```

for every `theta`.

For a total order `pi=(x_(1),...,x_(n))`, define the direct Buehler map

```text
U_pi(x_(j)) = B({x_(1),...,x_(j)}).
```

## Theorem: self-ordering dominance

Sort `X` by nondecreasing `u(x)` and break every tie by any fixed total order.
Then:

1. `U_pi` is a valid direct upper map;
2. `U_pi(x) <= u(x)` for every outcome `x`; and
3. the claim holds for every total-order refinement of every tie block.

### Proof

Monotonicity of `B` makes `U_pi` nondecreasing along `pi`. For a registered
risk level `r`, the failure set `{x:U_pi(x)<r}` is a prefix `S` satisfying
`B(S)<r`; therefore no parameter with risk at least `r` puts more than
`alpha` mass on that failure prefix. Hence `U_pi` is valid.

Now fix prefix index `j`. If `U_pi(x_(j))>u(x_(j))`, the definition of `B`
gives a parameter `theta` such that

```text
d(theta) > u(x_(j))
and
P_theta({x_(1),...,x_(j)}) > alpha.
```

Every member of that prefix has report at most `u(x_(j))`, including under an
arbitrary refinement of equal reports. The entire prefix is therefore
contained in `{x:u(x)<d(theta)}`, contradicting validity of `u`. Thus
`U_pi<=u` pointwise.

## Corollary: all-order deterministic completeness

For every coordinatewise nondecreasing loss functional `L`,

```text
min_{valid direct u} L(u)
  =
min_{total orders pi} L(U_pi),
```

whenever either minimum exists. In particular this holds for every strictly
positive reference-weighted expected bound.

One direction holds because every `U_pi` is a valid direct map. The other
holds because every valid `u` is pointwise dominated by the Buehler map
induced by a report-sorted order.

## Exact finite verification target

The prospective verifier should enumerate:

- all normalized monotone three-valued subset-bound tables on three outcomes;
- all `3^3=27` direct maps with reports in `{0,1,2}`;
- every report-consistent tie refinement;
- all six Buehler orders; and
- several strictly positive rational reference laws.

For every valid direct map, every consistent Buehlerization must be valid and
pointwise no larger. For every table and reference law, the minimum over all
valid direct maps must equal the minimum over all total-order Buehler maps.

The registered controls are:

```text
B = (0,1,1,2)
u_equal  = (1,2)
u_slack  = (2,2).
```

Under order `(0,1)`, `u_equal` is unchanged while `u_slack` is strictly
improved to `(1,2)`.

## Claim boundary

This theorem closes completeness only for deterministic direct upper maps in a
finite experiment. It does not cover aggregate randomized coverage,
two-sided confidence sets, conditional inference, continuous sample spaces,
strategic data sources, or the physical validity of a preference channel. It
does not resolve ASMP-9.
