# ASMP-3 critical-correlation characterization v0.1.1

The v0.1 frontier table reports registered grid endpoints. It does not claim
that `rho=0.05` or `rho=0.10` is the continuous crossing point.

For the frozen configuration

```text
q = 9
independent verifier families = 1
marginal error = 1/5
FP limit = FN limit = 1/20
```

the beta-binomial majority error equals `1/20` at a unique critical correlation
`rho*` in `[0,1]`.

## Exact algebraic definition

Let

```text
P(rho) =
  23595264 rho^7
- 39111828 rho^6
- 110905976 rho^5
- 67432815 rho^4
- 15144160 rho^3
- 1046494 rho^2
+ 40728 rho
+ 5281.
```

Exact symbolic reduction gives

```text
majority_error(rho) - 1/20
= -9 P(rho)
  / [1562500 (rho+1)(2rho+1)(3rho+1)(5rho+1)(6rho+1)(7rho+1)].
```

The denominator is positive for `rho in [0,1]`. A standard-library rational
Sturm calculation certifies that `P` has exactly one root on that interval and
exactly one root in

```text
59108062397/10^12 < rho* < 59108062398/10^12,
```

or numerically

```text
0.059108062397 < rho* < 0.059108062398.
```

The cell passes at and below `rho*` and fails above it. Thus the original
`[0.05,0.10]` statement was a grid bracket; the exact algebraic crossing is
approximately `0.0591080623971`.

## Interpretation

This number is conditional on the registered beta-binomial exchangeability
model, 20% marginal error, nine majority-voted calls, one verifier family, and
a 5% error ceiling. It is not a universal correlation threshold for oversight.
Concretely, the frozen family uses
`kappa=(1-rho)/rho`, `alpha=(1/5)kappa`, and `beta=(4/5)kappa`.
Pairwise `rho` alone does not determine the joint law of nine exchangeable
Bernoulli judgments; another joint distribution with the same marginal error
and pairwise correlation can have a different majority-error threshold.

The characterization is post-result mathematics, not a preregistered outcome.
Its value is to turn the coarse frontier row into a reproducible algebraic
object with a certified rational isolating interval.
