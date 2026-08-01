# Exact finite-experiment safety-deficiency LP

For finite models `m`, observations `x`, and actions `a`, let `q[m,x]` be the
complete source experiment and `g[m,a]` indicate whether action `a` satisfies
the registered global safety and utility constraints in model `m`.

The exact uniform certification success is the linear program

```text
maximize t
over K[x,a] >= 0

subject to
  sum_a K[x,a] = 1                         for every x,
  sum_x q[m,x] sum_a g[m,a] K[x,a] >= t   for every m.
```

Its exact dual is

```text
minimize sum_x z[x]
over lambda[m] >= 0

subject to
  sum_m lambda[m] = 1,
  z[x] >= sum_m lambda[m] q[m,x] g[m,a]   for every x,a.
```

The primal variable is the constructive observation-to-policy kernel. The dual
variable is a least-favorable distribution over models, and each `z[x]` is the
Bayes-optimal good-action mass after observing `x`.

The exact-rational implementation enumerates all basic feasible vertices. Its
tests establish:

- value `1/2` for identical binary experiments with opposite good actions;
- value `3/4` for the symmetric one-sample experiment with probabilities
  `1/4` and `3/4`;
- equality with the exact randomized-majority formula for product experiments
  through two samples; and
- primal/dual equality over all `81` combinations of two binary model laws
  from `{1/4,1/2,3/4}` and two nonempty good-action sets.

This removes the main constructive gap in the decision-deficiency reduction
for finite registrations: both the finite-sample certificate and its
least-favorable countercertificate are algorithmically explicit and exactly
checkable.
