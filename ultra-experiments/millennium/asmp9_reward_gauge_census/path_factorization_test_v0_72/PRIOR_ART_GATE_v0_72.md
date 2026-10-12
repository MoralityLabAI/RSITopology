# Prior-art gate for ASMP-9 path factorization test v0.72

Status: **classical Gaussian linear-model specialization**.

## Subsumption

The theorem is standard lack-of-fit testing:

- whitening a known-variance Gaussian linear model;
- orthogonal residual projection;
- Cochran-style chi-square decomposition; and
- noncentral chi-square power under a fixed alternative.

No new test, distribution theorem, or optimality result is claimed.

## Relation to existing ASMP-9 artifacts

- v0.71 supplies the path-incidence factorization object and exact left-kernel
  witnesses but no sampling law.
- v0.70 supplies exact Gaussian minimax recovery after a quotient but does not
  test whether the declared linear mean model is itself valid.
- v0.72 uses residual degrees of freedom to test that validity.

Parameter recovery and model falsifiability are complementary:

```text
rank(X)=d      identifies edge coordinates;
m-rank(X)>0   makes factorization falsifiable.
```

## Residual deliverable

The ASMP-9-specific contribution is the explicit liveness/sample ledger:

1. do not report factorization evidence when residual rank is zero;
2. preserve the v0.71 path-relation witness as the test direction;
3. compute a frozen exact power threshold rather than choosing repeat count
   after outcomes; and
4. hand a rejected Markov model to the v0.71 replacement object.

## Hostile-review questions

1. Were paths selected after inspecting residuals?
2. Are variances known or estimated from the same data?
3. Is Gaussian independence physically justified?
4. Is the registered alternative effect representative?
5. Does missing path support remove the only residual relation?
6. Is the chi-square test being described as proving moral validity rather
   than rejecting one Markov representation?

All remain outside the development claim.
