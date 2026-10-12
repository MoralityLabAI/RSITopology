# ASMP-4 randomness-quantifier completion audit v0.8

## Audit decision

The registered stochastic-quantifier boundary is exact.  It strengthens the
canonical stopping argument but does not choose a missing probability order.

| Obligation | Evidence | Status |
|---|---|---|
| Audit literal source | Shared randomness and universal disturbance clauses are present; probability order is absent. | Reproduced |
| Treat countable disturbances | Countable union of finite-prefix null sets yields a common safe seed. | Proven |
| Locate failure of that proof | Uncountably many one-step prefixes defeat the null-union argument. | Proven |
| Give a smooth witness | `x_next=(u-w)^2` separates the four stochastic semantics. | Proven |
| Preserve bounded inputs | Both random controls and disturbances lie in `[0,1]`. | Exact |
| Give finite corrections | Grid success is exactly `((N-1)/N)^T`. | Proven |
| Exhaust a bounded grid | 484,524 seed/disturbance pairs match the formulas. | Independently reproduced |
| Audit asymptotic order | 60 exact formula cells verify monotonicities and noncommuting limits. | Reproduced |
| Test Monte Carlo claims | Independent sampling misses the continuous diagonal while adaptive failure is certain. | Proven and checked |
| Preserve v0.7 | Frozen relational claim and zero kernel-derandomization failures remain intact. | Firewalled |

## Scope firewall

The diagonal fixture is a stochastic-quantifier boundary example, not a
normally-hyperbolic classification or a positive-error noisy-channel capacity
theorem.  It uses state-independent shared randomness and does not permit the
state-correlated side channel forbidden by canonical ASMP-4.

## Completion position

The mathematics settles both the countable collapse and uncountable
separation.  Selecting which semantics defines canonical `R_K` remains a
normative specification task.

The [v0.9 completion audit](../asmp4_completion_atlas_v0_9/COMPLETION_AUDIT_v0_9.md)
places this result in the five-requirement ASMP-4 evidence matrix.
