# ASMP-9 v0.46 theorem draft

## 1. Registered channel family

There are four targets and three binary queries `root`, `left`, and `right`.
The deterministic query signatures are

```text
root  = (0,0,1,1)
left  = (0,1,0,0)
right = (0,0,0,1).
```

Query `q` is followed by a binary symmetric channel `BSC(p_q)`. The same
`p_q` moves every target row and every adaptive policy using that query.
The registered orientation uses `0 <= p_q <= 1/2`.

## 2. Exact confidence image after a zero-error type

For `n_q` known-target calibration draws with zero observed errors, the
method-of-types event is

```text
KL(delta_0 || Bernoulli(p_q)) <= kappa(n_q).
```

Because

```text
KL(delta_0 || Bernoulli(p_q)) = -log(1-p_q),
```

the exact parameter image is

```text
0 <= p_q <= 1-exp(-kappa(n_q)).
```

If this endpoint exceeds `1/2`, the pointwise worst experiment in the full
interval is still `p_q=1/2`; rates above one half become more informative
again after output relabelling. The implementation therefore clips the
worst-case endpoint at `1/2`.

The exponential endpoint is transcendental. The implementation scales
`kappa` by a power of two, brackets `exp(-kappa/2^j)` with odd/even
alternating Taylor sums, raises both rational bounds to `2^j`, and rounds
outward to the registered `1e-12` grid. No floating-point exponential enters
a scientific bound.

## 3. Worst-case corner theorem

For `0 <= p <= q <= 1/2`, define

```text
r = (q-p)/(1-2p).
```

Then `0 <= r <= 1/2` and

```text
p+r-2pr = q.
```

Thus `BSC(q)` is `BSC(p)` followed by the independent garbling `BSC(r)`.
Blackwell monotonicity implies that increasing any registered flip rate cannot
improve any decision problem. The property is preserved under adaptive
composition because the controller may simulate the extra garbling after each
query output. Therefore

```text
sup_{p in product_q [0,p_q^max]} D(E_p,F)
  = D(E_{p^max},F).
```

This eliminates continuous optimization over the confidence image.

## 4. Complete symbolic policy compiler

For horizon two, every deterministic policy risk is a polynomial of total
degree at most two in `(p_root,p_left,p_right)`. The frozen monomial basis is

```text
1,
p_root, p_left, p_right,
p_root^2, p_root*p_left, p_root*p_right,
p_left^2, p_left*p_right, p_right^2.
```

The recursion includes:

1. every terminal action;
2. every first query;
3. an independently selected continuation after each binary outcome; and
4. every second query or terminal action in each continuation.

After exact symbolic deduplication the four-class library contains 3,748
distinct policy-risk polynomials. Randomized policies form their convex hull.

## 5. Exact minimax certificate

Let `r_pi(theta)` be the four-target risk vector of deterministic policy `pi`.
The robust classification risk at a frozen channel is

```text
R(p) = min_{mu in simplex(Policies)}
         max_theta sum_pi mu_pi r_pi(theta).
```

By finite minimax duality,

```text
R(p) = max_{lambda in simplex(Targets)}
         min_pi sum_theta lambda_theta r_pi(theta).
```

The implementation solves the five-variable dual by setting `u=1-R`:

```text
minimize u
subject to
  -lambda . r_pi - u <= -1  for every pi,
  sum_theta lambda_theta = 1,
  lambda >= 0, u >= 0.
```

A floating solver proposes the active basis. Exact rational elimination then
checks the primal and dual certificate against every one of the 3,748 policy
constraints. For the allocation census, any rational target prior supplies a
certified lower bound. Only allocations not separated from the proposed
winner by those bounds require a full exact solve.

## 6. Relation to the v0.45 rectangle

Version v0.45 propagates query-wise KL tolls through policy occupancy and
Pinsker, then permits the resulting policy/target risk coordinates to vary
independently. The shared-channel image above is contained in that relaxation,
but generally occupies a strict lower-dimensional subset. Consequently the
rectangular endpoint cannot be smaller than the exact coupled endpoint.

Strict inequality is a finite finding, not a new general theorem about robust
MDPs. The product-family control independently varies every registered
generator coordinate and exhausts all 16 vertices; its exact supremum must
equal the rectangular upper endpoint.

## 7. Claim boundary

The theorem is an exact finite composition of classical method-of-types,
Blackwell-garbling, finite minimax, and robust-optimization ideas. Its narrow
contribution is an executable coupled-image audit for the inherited ASMP-9
risk-access fixture. It does not make policy compilation efficient, establish
minimax confidence constants, cover strategic or history-dependent reward
sources, validate a real value-query channel, or resolve ASMP-9.

