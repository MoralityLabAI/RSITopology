# Prior-art gate for ASMP-9 joint linear quotient v0.69

Status: **classical consolidation; no novelty claim**.

## Subsumption decision

The mathematical core is standard finite-dimensional linear algebra:

- quotient maps and the first isomorphism theorem give the maximal object
  `R / ker(pi_J A)`;
- rank-nullity gives the exact access criterion;
- annihilators characterize identifiable linear functionals; and
- the smallest singular value gives the sharp inverse-problem conditioning
  constant.

Accordingly, v0.69 is not presented as a new theorem in linear inverse
problems. Its role is to compose two previously separate ASMP-9 ledgers:
licensed reward gauge and physical measurement nuisance.

## Adjacent ASMP-9 sources

1. Ng, Harada, and Russell (1999), *Policy invariance under reward
   transformations: Theory and application to reward shaping*. This is the
   canonical source for potential-based shaping as a policy-invariant reward
   transformation.
2. Skalse et al. (2023), *Invariance in Policy Optimisation and Partial
   Identifiability in Reward Learning*. This supplies the stronger modern
   warning that identifiability depends on the data source and its invariance.
3. The ASMP-9 v0.28 occupancy result already checks whether an observation
   kernel contains only the licensed gauge for one finite MDP grammar.
4. The v0.36 nuisance result distinguishes scientifically licensed gauge
   orbits from arbitrary nuisance confusability.
5. The v0.39 result shows that gauge semantics do not imply observational
   ancillarity when representative assignment is target-correlated.
6. The v0.68 result gives the maximal invariant for blockwise common-mode
   score nuisance but explicitly does not compose it with reward shaping.

## Residual contribution

The deliverable is an exact admission theorem for a finite linear physical
bridge:

```text
joint output nuisance J = N + A(G);
joint kernel K = A^(-1)(J);
reward quotient identified iff K = G.
```

It also records visible gauge leakage, emits a non-gauge kernel witness, and
attaches the sharp deterministic condition number. This is useful
specification and audit machinery, not a claim to have discovered quotient
linear algebra.

## Hostile-review questions

1. **Was the gauge chosen after seeing the measurement kernel?** If so, the
   theorem is tautological and the scientific target is unfrozen.
2. **Does `G` preserve the declared downstream decision?** Linear membership
   alone cannot license a reward transformation.
3. **Is `N` physically complete?** Unmodelled nuisance projected onto
   `J^perp` appears as substantive signal.
4. **Is gauge leakage being used as target information?** That changes the
   target from a reward orbit to a joint reward/assignment model.
5. **Is a deterministic condition number being reported as a sample rate?**
   Version v0.69 proves no stochastic complexity result.
