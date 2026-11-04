# ASMP-9 resolution-obligation matrix after v0.70 development

## Verdict

**ASMP-9 remains unresolved.**

Version v0.70 supplies a matching stochastic upper/lower theorem for the
finite linear quotient introduced in v0.69. Under independent Gaussian
queries with known variances, the information matrix exactly controls
identification, minimax quotient recovery, policy-margin estimation, and
fixed mean-bias amplification.

The theorem is a classical Gaussian linear-model and optimal-design
specialization. It is development-only and does not validate the model.

## Status against the five obligations

| Obligation | Strongest evidence after v0.70 | Status | Missing resolution evidence |
|---|---|---|---|
| 1. Maximal invariance or identifiability object | v0.69 gives `R/A^(-1)(N+A(G))`; v0.70 works in an orthonormal coordinate system on that quotient | **Exact for finite linear-Gaussian grammar; open broadly** | Nonlinear, context-varying, dynamic, strategic, relational, and non-scalar objects |
| 2. Necessary and sufficient access | Allocated Gaussian rows identify exactly when `M(n)` is positive definite | **Exact for nonadaptive Gaussian scalar access** | Adaptive interventions, unknown channels, target-changing access, and physical validation |
| 3. Sharp query, sample, and intervention bounds | Exact minimax quotient MSE `trace(M^-1)`, policy-margin MSE `c^T M^-1 c`, and complete integer allocation on the fixture | **Matched stochastic law in one declared family** | Unknown variance, dependence, heavy tails, context frequencies, adaptive allocation, computation, and general policy families |
| 4. Robustness to misspecification | Exact fixed mean-bias vector and MSE; rectangular bias class is vertex-enumerable | **Exact for fixed additive mean bias** | Unknown bias radius, nonlinear remainder, contamination, drift, dependence, adversarial or strategic corruption |
| 5. No-go without a coherent latent value object | Singular information supplies an unbounded indistinguishable non-gauge line | **Exact linear-Gaussian no-go only** | General replacement-object classification for incoherent or non-scalar demonstrators |

## What v0.70 adds

### Matching stochastic complexity

For information

```text
M(n)=sum_i (n_i/sigma_i^2)b_i b_i^T,
```

weighted least squares attains constant risk `trace(M^-1)`. A diffuse
Gaussian-prior lower bound converges to the same value, so this is minimax,
not merely a concentration upper bound.

### Decision-directed allocation

On the exact 12-sample fixture:

```text
parameter recovery:  (5,5,2), risk 14/45;
one policy margin:   (11,1,0) or (11,0,1), variance 1/11.
```

This is a clean finite demonstration that learning the entire quotient and
learning one downstream margin are different design problems.

### Misspecification ledger

Fixed query mean shifts produce an exact estimator bias. The registered
rectangular class is maximized over all sign vertices, keeping stochastic
variance and systematic error separate.

## Remaining load-bearing sequence

### A. Physical confirmation and channel audit

Map a prospectively frozen physical response experiment into quotient rows,
test Gaussian/linearity and variance assumptions on construction data, then
evaluate the untouched confirmation split without changing `G`, `N`, rows,
or margins.

### B. Non-Gaussian joint minimax theorem

Derive matching rates for a declared bounded or finite response channel that
includes context frequency, dependence, quotient conditioning, and policy
margin. Conservative upper bounds without a matching lower construction do
not close this item.

### C. Adaptive and target-changing access

Determine when adaptive allocation improves the quotient information region
and when elicitation changes the target being identified.

### D. General replacement-object classification

Classify when failure of scalar quotient identification requires a relation-,
kernel-, set-, or path-valued target rather than another scalar gauge.

## Claim boundary

Version v0.70 does not show that a real value-query channel is Gaussian,
linear, stationary, or semantically valid; that the chosen policy margin is
safe; that any human or model possesses a scalar value object; or that ASMP-9
is resolved.
