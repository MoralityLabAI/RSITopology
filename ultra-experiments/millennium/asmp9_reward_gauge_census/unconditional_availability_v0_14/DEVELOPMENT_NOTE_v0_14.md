# ASMP-9 v0.14 development note

## Burned registry

The unregistered CPU census covered 135 cells:

```text
k in {3,4,5}
n in {1,2,3}
R in {3/2,2,3}
q in {1,2,4,16,256}
alpha = 1/20.
```

Here `R` is the circulation odds ratio and:

```text
s(q)=(q^(k-1),q^(-1),...,q^(-1))
```

is an exact scalar-gradient nuisance.

Across all cells:

- the closed availability formula matched exhaustive outcome enumeration;
- every conditional test had exact size `1/20`;
- the unconditional excess-power factorization was exact;
- the availability upper bound and interior lower bound both held; and
- the `q=256` endpoint had lower informative-fiber probability and lower
  unconditional excess power than `q=1`.

There were no monotonicity reversals over the five burned `q` values, but
monotonicity is not claimed as a theorem or proposed as a confirmation gate.

## Magnitude of the nuisance collapse

For every `(k,n,R)` cell, compare `q=256` with the balanced `q=1` condition.
The largest endpoint ratio was:

```text
excess_power(q=256) / excess_power(q=1)
  = 0.00010093413754207105.
```

The smallest ratios were below `1e-9`.

For the illustrative `k=4`, `n=3`, `R=2` cell:

| `q` | informative probability | unconditional power | gain above 0.05 |
|---:|---:|---:|---:|
| 1 | 0.835286 | 0.072161 | 0.022161 |
| 2 | 0.447683 | 0.057351 | 0.007351 |
| 4 | 0.136189 | 0.051130 | 0.001130 |
| 16 | 0.004963 | 0.050018 | 0.0000183 |
| 256 | 0.00000166 | 0.0500000045 | 0.00000000447 |

The conditional law and exact test are unchanged by `q`; only the probability
of reaching each fiber moves.

## Positive arm

The second development pass added the matched sufficiency statement. If all
alternative edge probabilities lie in `[epsilon,1-epsilon]`, the no-zero
event gives:

```text
P(informative) >= [1-(1-epsilon)^n]^k.
```

Multiplying by the exact minimum informative-fiber power gain yields a
strictly positive uniform lower bound at every fixed finite
`(k,n,R,alpha)` with `R>1`. All 135 cells verified it exactly.

The lower bound is intentionally conservative. Its ratio to observed excess
power ranged from approximately `9.2e-42` in extreme nuisance cells to
`0.256` in the best burned cell. It is a validity guarantee, not a tight
finite-sample approximation.

## Development artifacts

The first census, before adding the positive interior arm, has SHA-256:

```text
6bd76453d6947e168b9b805eeddf1ef61b63de00a068435732cdcd339be12f3e
```

The superseding development census has SHA-256:

```text
d53700ad0594a6c135a4a27f54a6ffa68817e40a2c3f77e5cf26c4a437eb5045
```

Both are burned design evidence only.

## Freeze decision

The result merits prospective verification because it closes the exact seam
left open by v0.13:

- conditional nuisance cancellation remains valid;
- unconditional informativeness can nevertheless vanish;
- a declared probability interior restores a positive finite guarantee.

The fresh registry must use new cycle lengths, odds ratios, and nuisance
values. It must not reinterpret exact conditional size as unconditional
scalarity certification or claim novelty for conditional likelihood theory.
