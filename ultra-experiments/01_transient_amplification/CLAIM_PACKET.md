# Claim packet: `ultra.transient_amplification` v0.1

## Plain-language claim

Eigenvalues describe asymptotic behavior, not the largest finite-time response.
For a fixed linear response map and physical metric, a singular-value
calculation gives the exact worst-case finite-horizon boundary test.

## Formal statement

Let `A` be a real `d x d` matrix, `M=M^T` a positive-definite matrix,
`T` a nonnegative integer, and `delta,b>=0`. Define

```text
||x||_M = sqrt(x^T M x),
G_T(A;M) = max_(0 <= t <= T) ||M^(1/2) A^t M^(-1/2)||_2.
```

For the zero-input system `x_(t+1)=A x_t`,

```text
sup_(||x_0||_M<=delta) max_(0<=t<=T) ||A^t x_0||_M
  = delta * G_T(A;M).
```

Consequently the declared closed-radius condition passes exactly when
`delta*G_T(A;M)<=b`. The statement covers a finite integer horizon, closed
balls, exact real arithmetic, and zero exogenous input. When `delta=0`, both
sides of the identity are zero. Affine forcing, stochastic disturbances,
time-varying maps, and nonlinear rollout validity are excluded.

## Proof

Set `z=M^(1/2)x`. Then

```text
z_t = M^(1/2) A^t M^(-1/2) z_0.
```

For every `t`, the induced Euclidean operator norm gives

```text
||z_t||_2 <= ||M^(1/2) A^t M^(-1/2)||_2 ||z_0||_2
          <= G_T(A;M) delta.
```

This proves the upper bound. Because the maximum is over a finite time set, a
maximizing time `t*` exists. A top right singular vector of the corresponding
whitened power has norm one and attains the operator norm. Mapping it back by
`M^(-1/2)` and scaling by `delta` attains the upper bound. The `delta=0` case
is immediate.

## Liveness certificate

- Positive case: `A=0.9 I` gives `G_T=1`, so radii `delta=0.05`, `b=0.5`
  pass.
- Negative case: at coupling `0.2`, choose `x_0=0.05 e_8` and `t=40`.
  Exact rational binomial evaluation of only the `j=6,7` components gives
  `||A^40 e_8||_2^2>101`, hence `||A^40 x_0||_2>0.5`.
- The separation is analytically planted. The run calibrates implementation
  polarity; it does not discover the mathematical separation.

## Smallest example

For a two-dimensional Jordan block,

```text
A = [[a, k], [0, a]],
A^t = [[a^t, t k a^(t-1)], [0, a^t]].
```

Thus `|a|<1` can coexist with a large off-diagonal transient term.

## Challenger obligations

1. Verify that eigenvalue matching is exact to the registered tolerance.
2. Verify the singular-vector witness directly in the physical metric.
3. Apply joint coordinate/metric changes; the gain must remain invariant.
4. Confirm that changing coordinates without changing the metric is correctly
   treated as changing the physical question.
5. Reject any real-model use whose edit magnitude exceeds the measured
   linearization-validity radius.
6. Demonstrate metric relativity: the registered diagonal metric changes the
   coupling `0.2` decision from fail to pass, while joint coordinate/metric
   reframing preserves the original decision.

## Application boundary

Named consumers are a candidate HRMmmm finite-horizon declared-radius gate and
a target-blind VPD delayed-effect score. The theorem is exact; the fixture is a
deterministic implementation calibration; application to a fitted model map is
only a hypothesis. This result is not pseudospectral, does not beat a one-step
norm baseline, and does not show that a model self-editor exists, that its
response map is stationary, or that the synthetic Jordan structure occurs in a
transformer. The ball is not called a safety set without a separate argument.
