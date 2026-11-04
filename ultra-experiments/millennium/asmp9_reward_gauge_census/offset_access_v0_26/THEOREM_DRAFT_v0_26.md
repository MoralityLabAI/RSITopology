# ASMP-9 v0.26 development theorem: offset access defeats an unknown link

Status: development-only; not registered and not claim-eligible.

## 1. Registered object

Fix an anchor item `0` and write the utility differences as

```text
d_i = u_i-u_0 in [-B,B], i=1,...,d.
```

The response link belongs to the entire class of strictly increasing symmetric
functions:

```text
F(-x)=1-F(x), F(0)=1/2.
```

An offset query `(i,c)` adds a known cardinal amount `c` to item `i` and
returns the population sign

```text
Q(i,c) = sign(F(d_i+c)-1/2).
```

The offset is part of the access model. It is a known reward-unit intervention,
not an ordinary uncalibrated preference comparison. Consequently it supplies a
cardinal yardstick and is allowed to break positive-scale gauge.

Strict monotonicity and the common midpoint imply the link-free identity

```text
Q(i,c) = sign(d_i+c).
```

## 2. Population upper bound

Assume offsets cover `[-B,B]`. Bisection on `c=-m`, where `m` is the midpoint
of the current interval for `d_i`, returns an estimate with absolute error at
most `eta` after

```text
T = ceil(log2(B/eta))
```

queries. A star rooted at item zero therefore reconstructs the complete
utility vector modulo translation with

```text
d ceil(log2(B/eta))
```

population midpoint-sign queries.

The guarantee is uniform over the entire registered link class. It does not
estimate `F`.

## 3. Matching information lower bound

On a non-tie transcript, each coordinate-threshold query has two outcomes.
Tie leaves have Lebesgue measure zero and cannot cover a continuum under a
uniform guarantee.

The anchored parameter cube has volume `(2B)^d`. Any leaf on which one output
is `eta`-accurate in max norm has volume at most `(2eta)^d`. Thus any decision
tree requires at least

```text
ceil(log2((B/eta)^d))
```

queries in the worst case.

When `B/eta` is a power of two, the star-bisection upper bound meets this lower
bound exactly. The access result is therefore sharp on the registered dyadic
grid.

## 4. Offset-range necessity

If offsets are restricted to `|c|<=C<B`, choose

```text
d  = (B+C)/2,
d' = B.
```

Every permitted query is strictly positive under both gaps. The complete
transcripts are identical, while the gaps are separated by `(B-C)/2`. No
estimator can approximate both with worst-case error below `(B-C)/4`.

Thus full threshold coverage is not cosmetic: a uniformly accurate access
theorem must place every admissible gap's indifference point inside the
queryable offset range, up to the requested error.

## 5. Finite-sample positive branch

Replace the population sign with repeated Bernoulli choices. A finite uniform
sample bound requires a registered margin envelope. Assume that, for
`|x|<=2B`,

```text
|F(x)-1/2| >= kappa |x|^alpha
```

with known `kappa>0`, `alpha>0`.

At each bisection midpoint estimate the response probability to error

```text
e = kappa eta^alpha / 2.
```

- If the estimate exceeds `1/2+e`, retain the positive half.
- If it is below `1/2-e`, retain the negative half.
- Otherwise stop and return the midpoint.

On the simultaneous estimation event, every directional decision is correct.
If the procedure stops, the true probability is within `2e` of one half, so
the margin envelope implies that the midpoint is within `eta` of the gap.

Hoeffding plus a union bound over `Q` population queries gives the sufficient
per-query repeat count

```text
m >= log(2Q/delta) / (2e^2)
  = 2 log(2Q/delta) / (kappa^2 eta^(2 alpha)).
```

This is a transparent sufficient bound, not a minimax claim.

## 6. No uniform finite-sample theorem without a margin condition

The unrestricted link class contains scaled logistic links

```text
F_a(x)=1/(1+exp(-a x))
```

for every `a>0`. On the compact registered query and utility ranges,
`F_a(x)` converges uniformly to `1/2` as `a` approaches zero.

For any fixed finite adaptive sample budget, the complete transcript laws for
two separated utility gaps can therefore be made arbitrarily close in total
variation by choosing `a` small enough. Le Cam's two-point argument then
precludes a uniform high-confidence recovery guarantee.

The population access theorem is link-robust; its finite-sample version is not
rate-free. A slope or margin floor is a necessary modeling commitment.

## 7. No-offset control

Version v0.8 already gives the exact three-item witness

```text
u  = (0,1,3),
u' = (0,1,4).
```

With separate admissible links, the complete population pairwise laws are
identical even though the two utility vectors are not positive-affine
equivalent. The offset access in v0.26 is the missing intervention: it locates
each indifference threshold in registered reward units rather than inferring
distance from an uncalibrated probability.

## 8. Claim boundary

This theorem characterizes one strong access channel. It is classical
threshold search specialized to an ASMP-9 reward-gauge problem, and no novelty
claim is made.

It does not show that:

- ordinary human preference queries expose known additive reward offsets;
- arbitrary environment interventions implement the declared scalar offset;
- unknown context-dependent or item-dependent links share one midpoint;
- the Hoeffding bound is minimax;
- finite samples identify utility without a margin condition;
- general MDP rewards are identified from policy behavior; or
- ASMP-9 is resolved.
