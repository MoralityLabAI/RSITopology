# ASMP-9 next physical target-interface gate v0.79

Status: **protocol design only; unregistered and unrun**.

## Purpose

Test whether the finite target/interface theorem stack survives contact with a
physically executed but exactly auditable demonstrator. The experiment is not
authorized by this document; registration must occur before execution.

## Controlled system

Freeze:

- a small finite MDP family with exact transition tables;
- a finite policy family and exact occupancy vectors;
- a base reward `r`;
- potential functions producing licensed shaping variants;
- matched non-gauge reward perturbations changing at least one policy margin;
- a declared learning/control algorithm;
- environment interventions divided into construction and disjoint holdout
  sets; and
- repeated seeds sufficient for response-law estimation.

The primary target is the complete vector of registered policy margins. Policy
identity is secondary and must not be substituted post hoc.

## Arms

1. **Gauge arm:** base reward plus potential-based shaping variants whose exact
   dynamic-programming policy margins match the licensed target.
2. **Non-gauge arm:** matched-norm reward perturbations with an exact,
   preregistered policy-margin change.
3. **Null arm:** byte-identical replay and seed-repeat controls.
4. **Misspecification arm:** held-out environments and context/transition
   perturbations not used to construct the decoder.

## Registered gates

### W0 — target/gauge well-posedness

Exact dynamic programming must confirm:

```text
all gauge variants share the registered decision target;
every non-gauge positive control changes a registered margin.
```

Failure means `invalid_target_or_gauge`; no access claim proceeds.

### I0 — instrument replay

Byte-identical inputs and seeds must reproduce exact deterministic controls and
registered stochastic summaries within the frozen numerical tolerance.

### R0 — held-out target recovery

Fit the target decoder on construction environments only. On held-out
environments, report:

```text
target_recoverable;
underidentification witnesses;
cross-target Hellinger lower confidence bound;
finite-sample error bound.
```

The scientific margin and simultaneous confidence method must be frozen in the
registration.

### L0 — representative leakage

Within the gauge arm, test whether response laws differ across shaping
representatives. Leakage is reported separately:

```text
recoverable_with_representative_leakage
```

is not underidentification, but it prohibits a representative-insensitive
certificate unless a frozen target decoder removes the leaked field.

### M0 — misspecification stress

Estimate construction-to-holdout law discrepancy without outcome-label reuse.
Apply the v0.77 accumulated TV penalty. A nominal recovery pass cannot survive
when its robustified bound crosses the frozen error margin.

### C0 — access-cost accounting

For the frozen small query registry, compute the exact minimum separating
family. Report exhaustive/certified status. Do not generalize the optimum to
larger registries; v0.78 establishes worst-case NP-hardness.

## Required artifacts before execution

1. protocol and machine-readable registration;
2. exact MDP/environment tables;
3. base, gauge, and non-gauge reward manifests;
4. policy/occupancy and target-margin tables;
5. query/intervention universe;
6. construction/holdout assignment;
7. seed schedule and sample budget;
8. decoder source and environment lock;
9. simultaneous confidence and practical margins;
10. gate evaluator source;
11. prereveal hashes; and
12. post-run receipt and joined outcome hashes.

## Fixed decision procedure

Each gate reports:

```text
instrument_status in {valid, unavailable, invalid};
gate_decision in {pass, fail, inconclusive, not_evaluated}.
```

Any non-valid instrument forces `not_evaluated` for that gate. Only pass opens
the next gate. There is no discretionary near-pass override.

## Claim boundary

A passing run would validate one controlled finite-MDP acquisition channel. It
would not establish human value identifiability, open-ended model value
identifiability, general IRL correctness, or ASMP-9 resolution. A failing run
would falsify the registered channel or premise, not every possible access
scheme.
