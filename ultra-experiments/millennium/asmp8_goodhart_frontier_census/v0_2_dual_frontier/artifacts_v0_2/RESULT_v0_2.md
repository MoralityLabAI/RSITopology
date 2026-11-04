# ASMP-8 v0.2 registered dual-norm frontier result

**Verdict:** `dual_frontier_validated`

## Result

The census enumerated 3,876 rational policies; 1,863 strictly improved the proxy.

For every improving policy under q in {1, 2, infinity}, the worst-case true-reward gain matched:

```text
proxy_gain - epsilon * dual_movement
```

Polyhedral cases were independently checked by extreme-point enumeration; the q=2 case used exact squared algebra. Every cell had an attaining witness.

## Coordinate result

For each registered error geometry, the census found both an equal-proxy-gain pair with unequal movement and an equal-movement pair with unequal proxy gain. Neither coordinate alone determines the robust frontier on this registry; the pair does.

## Controls

- Near-tie sup-norm regret: 1/2 = 2 epsilon (pass).
- Rare-tail weighted-L2 error squared: 1/250000; true gain: -999999/1000000 (pass).

## Interpretation

The v0.1 failure of scalar KL does not imply that no optimizer-independent robust certificate exists. Under a declared reward-error norm, proxy gain and the corresponding dual policy movement form a sharp certificate. This is classical robust optimization specialized and audited on the Goodhart registry, not a new convex-duality theorem.

## Claim boundary

Classical dual-norm robust counterpart validated on a finite rational Goodhart registry; no novelty claim for convex duality, no learned reward model, no RL trajectory, and no ASMP-8 resolution.
