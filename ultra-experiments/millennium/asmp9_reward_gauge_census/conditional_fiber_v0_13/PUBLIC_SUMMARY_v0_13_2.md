# Conditional fibers expose exactly the data-supported value quotient

## Result

Consider independent fixed-count binary comparisons on an oriented graph.
Let `Y_e` be the target-win count on edge `e`, let `D` be the edge-vertex
incidence matrix, and let `lambda_e` be the edge log odds. Under a scalar
Bradley-Terry model:

```text
lambda = D theta.
```

Conditioning on the vertex win-balance statistic:

```text
T = D^T Y = t
```

removes `theta` exactly. On the finite count fiber:

```text
F_t = {y : 0 <= y_e <= N_e and D^T y=t},
```

the scalar-model law is proportional only to:

```text
product_e choose(N_e,y_e).
```

This is classical conditional exponential-family mathematics. Its useful
ASMP-9 consequence is a mandatory finite-sample liveness rule.

## The visible quotient is data-dependent

Define the fiber-difference span:

```text
S_t = span {y-z : y,z in F_t}.
```

Two edge-logit vectors induce the same conditional law exactly when their
difference is orthogonal to `S_t`. Because every fiber difference lies in the
cycle space `ker(D^T)`, the conditional experiment sees the full quotient
modulo scalar gradients if and only if:

```text
dim(S_t) = beta_1(G).
```

A rank-deficient fiber exposes only a lower-dimensional quotient. A singleton
fiber exposes none. Neither may be reported as evidence that a scalar value
model exists.

## Exact one-cycle test

On a consistently oriented `k`-cycle with `n` trials per edge, conditioning
on zero vertex balance leaves only:

```text
y=(z,...,z),  z=0,...,n.
```

If `Delta=sum_e lambda_e` is the cycle circulation, then:

```text
P_Delta(Z=z | T=0)
  proportional to choose(n,z)^k exp(Delta z).
```

The likelihood ratio is monotone in `z`, so the randomized upper-tail
size-`alpha` test is exactly uniformly most powerful for the one-sided
conditional alternative `Delta>0`. Rational odds ratios give exact rational
size, randomization, and power calculations.

## Registered verification

The scientific protocol was frozen at commit `f1311be`; the two
resource-unavailable attempts and implementation-only repairs were preserved.
The final direct-fiber implementation was frozen at `f458e81`. Registration
commit `b11ddca` sealed 39 inputs before the fresh cells were exposed.

All ten registered gates passed:

- five fresh graph families and fifteen graph/sample cells reproduced the
  exact graph arithmetic;
- scalar gauge factors and normalized conditional laws had zero mismatches;
- conditional-fiber rank never exceeded `beta_1`;
- every graph exhibited both full-rank and deficient fibers with positive
  flat-null mass;
- the direct simple-cycle fiber agreed with the closed form;
- likelihood-ratio, exact-size, and positive-power checks had zero
  mismatches; and
- all nine fresh power-calibration cells landed inside the frozen
  `[0.78,0.82]` band.

The full-quotient flat-null masses were:

| graph | `beta_1` | `n=1` | `n=2` | `n=3` |
|---|---:|---:|---:|---:|
| cycle 5 | 1 | `1/16` | `227/512` | `12919/16384` |
| cycle 7 | 1 | `1/64` | `2123/8192` | `683575/1048576` |
| theta 6 | 2 | `3/32` | `1247/2048` | `116967/131072` |
| square plus diagonal | 2 | `3/16` | `367/512` | `15207/16384` |
| bowtie 6 | 2 | `1/16` | `529/1024` | `55225/65536` |

These are exact probabilities under each registered flat-null graph, not
universal probabilities over comparison tasks.

The fresh exact powers ranged from:

```text
0.798185497278160338353896751089
```

to:

```text
0.803371546224424059961817019089.
```

The sample counts are calibration points, not monotone critical thresholds:
finite-lattice exact-size power can move non-monotonically with `n`.

The CPU-only run completed in `11.14` seconds at `28,110,848` peak resident
bytes. The artifact verifier passed, and a clean replay reproduced every
scientific field. All 16 dedicated tests passed; all 225 repository tests
passed across fresh-process batches.

The authoritative outputs are in
[`artifacts_v0_13_2`](artifacts_v0_13_2), with the compact audit record in
[`verification_v0_13_2.json`](verification_v0_13_2.json).

## Prior-art and novelty boundary

Conditional inference for discrete exponential families, toric
Bradley-Terry models, graph-Hodge ranking decompositions, and broader minimax
Bradley-Terry testing are established. Novelty of those foundations is not
claimed.

The contribution is their specialization into a prospectively registered
ASMP-9 access ledger:

1. the sufficient statistic that removes the scalar-value nuisance;
2. the exact quotient visible after conditioning;
3. fiber rank as a mandatory finite-sample liveness condition; and
4. an exact one-cycle calibration with unavailable states kept explicit.

## ASMP-9 contribution and remaining gap

Version v0.13.2 closes a finite-sample gauge-bookkeeping gap left by the
earlier simultaneous-band certificate. It shows exactly what a realized
conditional experiment can and cannot identify after scalar nuisance
elimination.

It does **not** resolve ASMP-9. It assumes independent fixed-count Bernoulli
comparisons, a known logistic link, observed item identities, a fixed graph,
and conditional rather than unconditional inference. It does not validate
Bradley-Terry behavior, turn non-rejection into proof of scalarity, handle
unknown links, dependent or strategic responses, latent contexts, adaptive
graph selection, sequential policies, or give a general IRL theorem.
