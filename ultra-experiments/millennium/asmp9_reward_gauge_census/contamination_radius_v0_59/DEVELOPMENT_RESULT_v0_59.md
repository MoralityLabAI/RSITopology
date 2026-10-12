# ASMP-9 adversarial-contamination radius development result v0.59

Status: **unregistered development result; not claim eligible**.

## Verdict

The next misspecification cell has an exact population boundary.

For fixed per-menu Huber contamination

```text
observed = (1-epsilon) clean + epsilon contaminant,
```

two finite categorical laws have a common observed law exactly when

```text
TV(clean_1,clean_2) <= epsilon/(1-epsilon).
```

For a compact value-object class with compact tier fibers, the minimum
maximum-menu TV distance `Delta` between different tiers therefore gives the
exact population threshold

```text
epsilon_star = Delta/(1+Delta).
```

This is classical robust-testing geometry specialized to the ASMP-9 tier
object. It is not a new contamination theorem.

## Exact positive and negative sides

Let `D` be the registered observed menu family. Define

```text
Delta(C,D)
  = min_(tier(p) != tier(p'))
      max_(A in D) TV(p_A,p'_A).
```

Then:

- `epsilon < Delta/(1+Delta)`: contaminated population laws retain a unique
  clean tier;
- `epsilon = Delta/(1+Delta)`: return `boundary_inconclusive`;
- `epsilon > Delta/(1+Delta)`: at least one cross-tier pair is observationally
  confusable.

The equality convention is deliberately non-adjudicative.

The proof is constructive. A common observed categorical law assigns

```text
(1-epsilon) max(p_i,p'_i)
```

to each coordinate and puts the remaining mass on any coordinate. Subtracting
each clean component recovers valid contaminants exactly when the displayed
TV condition holds.

## Bounded-context bracket

For the compact probability-floor slice of the v0.57 bounded-context class
and the v0.58 separation promise, the interpolation norm gives

```text
Delta
  >=
  a {
    1-exp[
      -atanh(gamma/2)/K_star(n,r)
    ]
  }.
```

Hence a certified population-identifiability region is

```text
epsilon/(1-epsilon)
  <
  a {
    1-exp[
      -atanh(gamma/2)/K_star(n,r)
    ]
  }.
```

This is a lower bracket on the exact modulus, not an assertion that the bound
is attained.

An explicit three-alternative `BP_1` pair supplies the opposite direction.
For `0 < gamma <= 1/125`, a RUM boundary kernel and a regularity-violating
non-RUM kernel differ only on the full menu:

```text
(2/5,           2/5,           1/5)
(2/5+2 gamma,   2/5-2 gamma,   1/5).
```

Their observed-menu TV distance is `2 gamma`, and they have a common
contaminated law at

```text
epsilon = 2 gamma/(1+2 gamma).
```

The contaminants are point masses on the first and second alternatives,
respectively. The frozen v0.54 classifier independently verifies that the
clean kernels occupy different tiers.

Representative exact witness thresholds are:

| `gamma` | ambiguity `epsilon` |
|---:|---:|
| `1/1000` | `1/501` |
| `1/250` | `1/126` |
| `1/125` | `2/127` |

The lower bracket and upper witness do not coincide. Computing or tightly
bounding `Delta` for the full bounded-context class remains open.

## Contamination and sampling consume separate budget

The conservative v0.58 plug-in certificate has clean coordinate tolerance

```text
t_clean
  = a {
      1-exp[
        -atanh(gamma/6)/K_star(n,r)
      ]
    }.
```

Huber contamination contributes deterministic coordinate bias at most
`epsilon`. Sampling receives only

```text
t_sample = t_clean - epsilon.
```

If `epsilon >= t_clean`, this particular certificate is unavailable,
regardless of sample size. Otherwise the strict sufficient per-menu count is

```text
N >
  log{2 Q(n,r)/delta}
  / {2 t_sample^2}.
```

The table shows how quickly the transparent bound deteriorates. `N0`, `N25`,
and `N75` spend 0%, 25%, and 75% of `t_clean` on contamination.

| `n` | `r` | `a` | `gamma` | `K_star` | population `epsilon` ceiling | `N0` | `N25` | `N75` |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 1 | 0.20 | 0.20 | 1 | 0.0187355 | 68,407 | 121,613 | 1,094,512 |
| 5 | 1 | 0.05 | 0.10 | 5 | 0.000497674 | 166,308,762 | 295,660,022 | 2,660,940,192 |
| 6 | 2 | 0.02 | 0.05 | 17 | 0.0000293954 | 45,274,968,354 | 80,488,832,628 | 724,399,493,649 |
| 8 | 4 | 0.01 | 0.02 | 129 | 0.000000775189 | 91,037,884,048,966 | 161,845,127,198,162 | 1,456,606,144,783,453 |

These are conservative sufficient counts, not lower bounds or practical
recommendations. The population ceiling uses the `gamma/2` cross-tier
separation; the finite-sample certificate uses the stricter `gamma/6`
reconstruction tolerance. They answer different questions and must not be
identified.

## Verification

Development tests:

```text
7 passed
```

The tests include:

- exhaustive exact overlap and contaminant construction on a rational
  three-category simplex grid;
- the independently contaminated multi-menu maximum-TV rule;
- the frozen v0.54 RUM/non-RUM tier witness;
- the bounded-context inverse modulus;
- the additive contamination-plus-sampling ledger; and
- an explicit non-pass at equality.

Import-independent verifier:

```json
{
  "construction_checks": 861,
  "kernel_checks": 3,
  "modulus_checks": 88,
  "overlap_checks": 1764,
  "registered": false,
  "sampling_checks": 3,
  "status": "development_checks_passed",
  "table_checks": 4,
  "witness_checks": 3
}
```

## Prior-art verdict

Huber contamination, contamination neighborhoods, least-favorable robust
tests, and finite-alphabet robust distinguishability are classical. The
candidate residual is only the explicit composition with:

1. the nested Luce/RUM/non-RUM value-object tiers;
2. the bounded-context interpolation modulus;
3. the exact cross-tier equality witness; and
4. a ledger separating structural conditioning, adversarial bias, and
   sampling error.

Novelty is not established.

## Freeze decision

Do **not** register v0.59 yet. Before a claim-eligible version:

1. externally review the compact-tier and modulus-attainment assumptions;
2. decide whether to bind only the sharp population theorem or also the
   conservative plug-in corollary;
3. seek a sharper robust estimator that approaches the population radius
   without inheriting the full deterministic interpolation condition number;
4. review whether the exact class modulus can be computed or dual-certified
   for useful finite instances; and
5. keep fixed-mixture contamination distinct from adaptive sample
   replacement and menu endogeneity.

## Claim boundary

This result assumes a known contamination fraction, fixed per-menu Huber
mixtures, iid samples, exogenous menus, known context degree, a positive clean
probability floor, compact tier fibers, and a declared separation promise. It
does not cover strategic or adaptive replacement, correlated responses,
unknown contamination, endogenous menus, context drift, nonstationarity,
efficient class-modulus optimization, or the semantic correctness of any
recovered value object. ASMP-9 remains unresolved.
