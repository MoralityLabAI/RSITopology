# ASMP-8 v0.2 claim packet: dual-norm robust frontier

## Frozen mathematical object

Let `p0` have full support on a finite outcome set, let `pi` be an optimized
policy, let `y` be proxy reward, and write true reward as `r = y + e`. Define

```text
a_i = pi_i / p0_i - 1
proxy_gain = E_pi[y] - E_p0[y]
```

For `1 <= q <= infinity`, constrain the weighted error norm

```text
||e||_(q,p0) <= epsilon.
```

The registered identity is

```text
inf_e (E_pi[r] - E_p0[r])
  = proxy_gain - epsilon * ||a||_(q*,p0),
```

where `q*` is the dual exponent. The robust critical error radius is the ratio
of proxy gain to dual movement.

Special cases:

- `q = infinity`: dual movement is `sum_i |pi_i-p0_i| = 2 TV(pi,p0)`;
- `q = 2`: dual movement is `sqrt(chi^2(pi || p0))`; and
- `q = 1`: dual movement is `max_i |pi_i/p0_i - 1|`.

## Registered questions

1. Does the formula reproduce the exact worst-case margin and an attaining
   witness for every proxy-improving policy in the finite rational registry?
2. Is proxy gain alone insufficient because equal-gain policies can have
   different dual movement?
3. Is dual movement alone insufficient because equal-movement policies can
   have different proxy gain?
4. Does a near-tie deterministic optimization example attain the classical
   `2 epsilon` sup-norm regret bound exactly?
5. Does the weighted-L2 coordinate correctly expose the rare-tail failure that
   a small reference-distribution error can hide?

## Claim boundary

A pass validates a classical robust-optimization identity as a sharp Goodhart
instrument on one finite policy registry. It does not establish novelty for
the identity, estimate a real reward model's uncertainty set, describe RL
training dynamics, or resolve ASMP-8.

