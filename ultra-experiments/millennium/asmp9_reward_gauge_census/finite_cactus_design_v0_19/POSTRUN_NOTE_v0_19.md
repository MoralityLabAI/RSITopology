# ASMP-9 v0.19 post-run note

## Frozen verdict

```text
finite_budget_cactus_dp_not_established
```

The registered run completed in `261.413` seconds against a frozen
`180`-second wall-time cap. Gate `G8_resource_and_scope` therefore failed.
The cap is not relaxed and the verdict is not reinterpreted.

Peak resident memory was `23,552,000` bytes and no GPU was used.

## Scientific payload

The other eight gates passed:

- exact direct residual-state availability equaled the cactus cycle product;
- bridge counts were irrelevant and optimized bridges stayed at their
  mandatory floor;
- the Bellman recurrence matched independent exhaustive cycle-total
  enumeration on all three fresh cells;
- a 330-allocation full positive edge census matched the Bellman optimum,
  with all 12 edge-level optimizers balanced within cycles;
- the frozen nonconcavity and finite-uniform counterexamples reproduced; and
- all three outcome-neutral fresh comparator classifications completed.

Those cells are now burned. Their arithmetic may be used as regression
evidence, but not as fresh confirmation in a successor.

## Bottleneck

The direct residual check recomputed strongly connected components for every
endpoint-label/status pair:

```text
2^|E| endpoint labels times 3^|E| residual states.
```

Liveness depends only on the graph and ternary status, not on endpoint labels
or trial counts. A versioned successor may therefore:

1. precompute the live ternary status table once per graph;
2. evaluate each Bernoulli status law using integer numerators under its
   common exact denominator; and
3. retain the same direct residual definition and exact-rational equality
   gates.

That is a computation-only optimization, but it must be frozen before new
cells and must not reuse v0.19 outcomes as fresh evidence.

## Independent-verifier defect

The sealed v0.19 verifier recomputed ten checks. Nine passed: the sealed-file
hashes, protocol and registration bindings, factorization, bridge
irrelevance, Bellman cells, full edge census, regression witnesses, and
comparator classifications. Its sole failed check, `registered_gates`, was
written to require every scientific and resource gate to pass and the
positive verdict to appear. It therefore cannot represent a valid negative
registered outcome.

The emitted `verification_v0_19.json` is retained unchanged with
`pass=false`. This is a verifier-schema defect, not independent confirmation
of the v0.19 theorem. Version 0.19.1 corrects the verifier prospectively by
checking the total mapping from the registered gate vector to either the
positive or negative verdict.

## Claim boundary

This failed-cap execution is not an established v0.19 theorem. It is a
complete mathematical payload under an invalid registered resource outcome
and a design input for a versioned successor.
