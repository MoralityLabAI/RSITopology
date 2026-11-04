# ASMP-9 contextual scalar-gluing protocol v0.11.2

## Status

Prospective implementation-repair protocol. The registered v0.11 and v0.11.1
attempts each exceeded the same 360-second wall-time cap and produced no
scientific artifact. This version changes only exact rank, cycle-basis, and
witness bookkeeping in the seeded-cell implementation. It does not change a
scientific cell, seed, status, gate, threshold, or resource limit.

The first sixteen cells of the already registered seed are burned
implementation-validation data. Their exact literal/optimized equality is
recorded in `REPAIR_NOTE_v0_11_2.md`. The scientific specification predates
that validation in v0.11 and remains unchanged.

## Frozen theorem

For context-labelled comparison graphs on one common item universe,
conditional on exact scalarity within each context, the dimension obstructing
one shared scalar is:

```text
q
  = rank(D_local)-rank(D_union)
  = beta_1(labelled union)-sum_context beta_1(context graph).
```

Exactly `q` independent mixed-context cycle checks are necessary and
sufficient in the registered exact-linear access model.

## Frozen scientific cells

The cells are byte-for-byte identical as machine-readable specifications to
v0.11 and v0.11.1:

- all `2^(3*choose(4,2)) = 262,144` ordered triples of simple graphs on four
  common items;
- seed `1101101`, with 4,096 graph families over item counts `5..9` and
  context counts `2..5`; and
- one-item, one-context, and minimal two-item/two-context controls.

The statuses remain:

- `local_scalar_failed`;
- `shared_scalar_forced_by_design`;
- `shared_scalar_verified`; and
- `shared_scalar_refuted`.

## Exact repair

The optimized implementation uses exact `GF(2)` bitset elimination for graph
incidence ranks and cycle-space independence. This is equality-preserving
because graph incidence and cycle-space ranks are field-independent between
the rationals and `GF(2)`.

The implementation still evaluates:

- shared controls;
- non-gluing witnesses;
- local-failure controls; and
- mixed-cycle decisions

with signed rational circulations. No unsigned support statistic can itself
produce a scalarity verdict.

## Gates

The ten scientific and resource gates are unchanged:

- **G0 registration binding**;
- **G1 exact census**;
- **G2 census liveness**;
- **G3 seeded coverage**;
- **G4 quotient and sharpness**;
- **G5 shared controls**;
- **G6 nongluing controls**;
- **G7 local-failure and status liveness**;
- **G8 minimality**; and
- **G9 resource envelope**: CPU only, at most 360 seconds and 2 GiB peak
  resident memory.

All passing yields:

```text
finite_contextual_scalar_gluing_geometry_verified_v0_11_2
```

## Claim boundary

This remains exact finite real-valued graph linear algebra beneath HodgeRank
and classical local-to-global theory. It is not ordinal rationalizability,
finite-sample preference estimation, human/model evidence, infinite-history
analysis, or an ASMP-9 resolution.
