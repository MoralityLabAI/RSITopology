# ASMP-9 aggregate randomized coverage result v0.53

## Verdict

**`subset_table_insufficient_for_aggregate_randomization`**

The thresholded subset-bound table that is information-complete for
deterministic Buehler optimization is not sufficient to determine the optimum
under aggregate randomized coverage.

Ten finite experiments had:

```text
the same deterministic subset table,
the same valid deterministic optimum,
and ten distinct aggregate-randomized optima.
```

Randomized confidence procedures are classical. The durable ASMP-9 result is
the exact boundary of the deterministic compression: fractional failure
allocation requires probability magnitudes, not only threshold crossings.

## General finite LP

For outcome `x`, report `r`, external randomizer `Z`, and

```text
q_xr = P(U(x,Z)=r),
```

aggregate randomized optimization is:

```text
minimize  sum_x w_x sum_r r q_xr

subject to
  sum_r q_xr = 1
  sum_x P_theta(x) sum_{r>=d(theta)} q_xr >= 1-alpha
  q_xr >= 0.
```

Every constraint and objective is linear. With rational inputs this is a
rational LP. A basic feasible solution has at most `n+k` positive report atoms
for `n` outcomes and `k` coverage constraints.

Any conditional report law is a mixture of deterministic maps, but its
components need not be individually valid. That is the distinction from
v0.51, which randomized only over valid Buehler orderings.

## Minimal strict-gain control

With one outcome, risk `1`, reports `{0,1}`, and `alpha=1/2`:

```text
deterministic optimum = 1
randomized optimum    = 1/2.
```

The randomized procedure reports `1` with probability `1/2`. This is the
standard discrete-confidence use of randomization, not a new construction.

## Subset-table insufficiency theorem

Fix:

```text
alpha = 1/2
reports = {0,1}
reference weights = (1/2,1/2)
risk = 1.
```

Compare:

```text
P_A = (3/5, 2/5)
P_B = (9/10, 1/10).
```

Both induce:

```text
B(empty) = 0
B({x_0}) = 1
B({x_1}) = 0
B(X) = 1.
```

Both have deterministic optimizer `(1,0)` and deterministic value `1/2`.
Their randomized optima differ:

```text
A: success probabilities (5/6,0), value 5/12
B: success probabilities (5/9,0), value 5/18.
```

For a general `P=(p,1-p)` with `p>1/2`, the same table persists while

```text
randomized value = 1/(4p).
```

Thus the same deterministic sufficient statistic admits a continuum of
randomized values.

## Exact dual certificate

Set:

```text
lambda = 1/(2p).
```

For both outcomes:

```text
lambda P(x_i) <= 1/2 = w_i.
```

Every feasible success vector `s` therefore satisfies:

```text
w dot s >= lambda P dot s >= lambda/2 = 1/(4p).
```

The displayed randomized procedure attains the bound.

## Prospective verification

Verification source commit:

```text
029622fbe6e4dc00bd06b7c542a464d2ff81d836
```

Registration commit:

```text
ae833f6779ea9b11b85ff32db73587c9528edcdf
```

Registration SHA-256:

```text
5cce4cfeb73b0debe3c7a7d7691c26cde602eacf21708e492dd38ee17a890ca1
```

Write-once result commit:

```text
e95f563f10fa7a881e57feb6c661bff38ab70f8e
```

Verification SHA-256:

```text
e337544214ff94861cccb15929318be77c07a6db3cfe81e0cde76794f5db0349
```

## Exact family result

The independent verifier swept:

```text
p = 11/20, 12/20, ..., 20/20.
```

| Quantity | Result |
|---|---:|
| Experiments | `10` |
| Common subset-table matches | `10/10` |
| Deterministic value matches | `10/10` |
| Distinct randomized values | `10` |
| Primal formula mismatches | `0` |
| Dual certificate mismatches | `0` |
| Support-bound failures | `0` |

The invalid-component control represented the `p=3/5` optimum as:

```text
5/6 * map (1,0)
+ 1/6 * map (0,0).
```

The second map is individually invalid, while the mixture has aggregate
coverage exactly `1/2`.

A two-constraint control used four positive report atoms, exactly saturating
the registered `n+k=4` basic-feasible support bound.

## Prior-art boundary

Randomized and fuzzy confidence procedures for discrete data are established
statistics. Primary anchors include:

- Geyer and Meeden, *Statistical Science* 20 (2005), DOI
  `10.1214/088342305000000340`;
- Kabaila, arXiv `1302.6659` (2013); and
- Thulin, *Statistics & Probability Letters* 92 (2014), DOI
  `10.1016/j.spl.2014.05.005`.

The LP formulation, strict randomization gain, and sparse extreme-point fact
are not novelty claims.

## ASMP-9 consequence

The finite inference stack now has two different sufficient inputs:

```text
deterministic direct confidence:
  thresholded subset-bound table B

aggregate randomized confidence:
  full probability experiment P_theta.
```

The latter cannot be reconstructed from the former.

## Remaining load-bearing target

The finite known-response access grammar is now highly characterized. The next
canonical obligation is demonstrator well-posedness:

> When does a finite stochastic choice kernel admit a coherent scalar value,
> when does only a preference relation or random-utility object exist, and
> when is no object in the declared class compatible with the observations?

That successor must begin with revealed-preference and stochastic-choice prior
art, not with another confidence-table census.

## Claim boundary

This is a finite exact witness within classical randomized confidence theory.
It does not recommend randomized safety certification, establish novelty,
handle continuous or strategic uncertainty, validate a physical preference
channel, prove a scalar value exists, or resolve ASMP-9.
