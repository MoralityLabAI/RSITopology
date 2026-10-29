# ASMP-9 v0.27 development note

## Burned fixtures

The implementation and tests use only these design fixtures:

- one item in two contexts;
- a two-item/two-context square;
- a three-item/two-context tree;
- a disconnected path plus isolated vertices; and
- fixed deterministic perturbation vectors on the square.

These fixtures are burned and may not appear as fresh validation cells in a
later registration.

## Prospective target

A registration may use fresh bipartite graphs to verify:

1. link-shape invariance at a shared midpoint;
2. arbitrary-midpoint reparameterization;
3. component gauge and incidence-rank identities;
4. the spanning-forest/chord ledger;
5. factorable and nonfactorable live-cycle controls; and
6. the Laplacian pseudoinverse error bound.

Fresh values and graph cells must be sealed before the runner reads their
outcomes.

## Claim discipline

Finite implementation checks validate the translation from the theorem to the
instrument. They do not prove the classical incidence or spectral theorems.

