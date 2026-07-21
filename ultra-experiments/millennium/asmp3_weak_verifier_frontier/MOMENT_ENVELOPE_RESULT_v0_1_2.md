# Two moments cannot certify nine-judge amplification

## Status and prior art

This is a post-result exact specialization of the classical discrete binomial
moment problem, particularly the two-sided bounds developed in the
Boros–Prékopa line. It is not a new probability inequality and was not a
preregistered empirical outcome.

## Result

Let nine exchangeable Bernoulli variables denote semantic-judgment errors.
Fix marginal error `1/5`, pairwise correlation `rho in [0,1]`, and majority
failure `P(S>=5)`, where `S` is the error count. The sharp lower envelope over
all compatible exchangeable laws is

```text
L(rho) = 0                         for 0 <= rho <= 7/32
L(rho) = (32 rho - 7)/125         for 7/32 <= rho <= 1.
```

Every feasible count distribution used below corresponds to a genuine
exchangeable joint law: conditional on `S=s`, distribute its probability
uniformly over the `C(9,s)` error vectors of weight `s`.

The inequality

```text
1{S>=5} >= [S(S-1)-3S]/45
```

is the dual certificate for the positive branch. Equality is attained by a law
supported on `{0,4,9}`. This law concentrates the tail as a common-mode event:
most panels make at most four errors, while a smaller mass makes all nine.
That is precisely the higher-order dependence hidden from the first two
binomial moments.

At `rho=0`, the sharp upper tail is `8/75`, certified by

```text
1{S>=5} <= 1/6 - S/6 + S(S-1)/12
```

with equality for support `{1,2,5}`. Thus pairwise-uncorrelated judgments can
still have 10.67% majority error.

## The missing continuum witness

The underdetermination claim requires a failing law at every `rho`, not merely
at the endpoints. Let `D_0` be the `{1,2,5}` law with weights

```text
13/25, 28/75, 8/75,
```

and let `D_1` be the common-shock `{0,9}` law with weights `4/5,1/5`.
Then

```text
D_rho = (1-rho) D_0 + rho D_1
```

has the frozen mean and pairwise correlation exactly, for every
`rho in [0,1]`, while

```text
P_Drho(S>=5) = 8/75 + 7 rho/75 > 1/20.
```

This supplies a continuous primal certificate that a failing exchangeable law
exists throughout the entire physical interval. No monotonicity or nesting of
the moment-feasible sets is assumed.

## Certified classification at a 5% error ceiling

The lower envelope crosses `1/20` at

```text
rho = 53/128 = 0.4140625.
```

Therefore:

| region | exact conclusion from marginal error and pairwise correlation |
|---|---|
| all `rho in [0,1]` | no universally certified pass exists |
| `0 <= rho <= 53/128` | underdetermined: both passing and failing laws exist |
| `53/128 < rho <= 1` | universal failure: every compatible exchangeable law exceeds 5% |

The beta-binomial critical value `rho*=0.059108...` from v0.1.1 lies inside the
underdetermined region. It is one selected joint-law trajectory through the
moment polytope, not a model-free threshold.

## Safety interpretation

Marginal accuracy plus pairwise error correlation is structurally incapable of
certifying majority amplification for this tuple. Those two moments can certify
universal failure above `53/128`, but they can never certify a universal pass.
Any positive soundness claim needs additional higher-order dependence
information or a stronger structural assumption such as the frozen
beta-binomial mixing law.

This says nothing directly about real judge ensembles: their exchangeability,
error event, higher moments, and selection process would all need measurement.
