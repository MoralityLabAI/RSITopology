# Four moments are necessary and sufficient for the frozen reference panel

## Result

Consider every exchangeable nine-judgment error law whose first `m`
falling-factorial moments match those of nine independent judgments with 20%
error. Let `U_m` be the worst compatible probability that at least five judges
err. Under a 5% admissibility standard, the minimum certifying moment order is
exactly four.

| known moment order | sharp worst compatible majority error | certifies <=5%? |
|---:|---:|---|
| 1 | `9/25` = 36% | no |
| 2 | `8/75` = 10.6667% | no |
| 3 | `39/625` = 6.24% | no |
| 4 | `126/3125` = 4.032% | yes |

## Necessity: three moments do not suffice

The law

```text
P(S=0,2,3,5)
= (136/625, 84/125, 6/125, 39/625)
```

matches the independent `Binomial(9,1/5)` reference moments through order
three, but has majority error

```text
P(S>=5)=39/625=6.24%.
```

It is therefore an exact counterexample to certification from the first three
binomial moments.

## Sufficiency and sharpness at order four

For every count `S in {0,...,9}`,

```text
1{S>=5} <= (S)_4/120.
```

Taking expectations under any law matching the fourth reference moment gives

```text
P(S>=5)
<= E[(S)_4]/120
= (9)_4 (1/5)^4 / 120
= 126/3125
= 4.032%.
```

The bound is sharp. Equality is attained by

```text
P(S=0,1,2,3,5)
= (404/3125, 207/625, 144/625, 168/625, 126/3125),
```

which matches all four frozen moments.

## Interpretation

For this independent reference panel, means and pairwise correlations are
insufficient, and adding the third factorial moment remains insufficient. The
fourth factorial moment is the first amount of exact higher-order dependence
information that can certify the panel under a 5% majority-error standard.

This quantifies information required for *this tuple*. It does not establish
that fourth-order measurement is sufficient for other panel sizes, marginal
errors, decision rules, thresholds, nonexchangeable errors, or selected-query
regimes. Measuring a fourth moment reliably may itself require substantial
data, which this exact calculation does not price.

## Attribution

The probability mathematics is a specialization of the classical discrete
binomial moment problem. The contribution is the executable frozen-tuple
certificate and its oversight interpretation, not a new moment inequality.

