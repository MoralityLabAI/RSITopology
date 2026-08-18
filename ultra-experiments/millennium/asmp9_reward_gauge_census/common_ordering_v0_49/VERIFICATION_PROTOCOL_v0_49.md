# ASMP-9 v0.49 theorem-verification protocol

## Status

This is a verification protocol for an already-derived finite theorem. It is
not a prospective empirical registration and cannot convert the development
fixtures into new scientific confirmation evidence.

## Frozen checks

### H0 - provenance

The verification registration and every registered source hash must match.

### T0 - dedicated tests

All seven dedicated tests must pass without writing Python or pytest caches.

### M0 - minimal statistical obstruction

The exact two-outcome/two-parameter witness must reproduce:

```text
B_1 = (0,0,1,1)
B_2 = (0,1,0,1)
optimizer intersection = empty
cross-regrets = 1/2 and 1/2.
```

The verifier must also exhaust the registered one-parameter rational grid and
find a common optimum for every pair of nonnegative scalar decision risks.
The one-outcome lower boundary is structural because it has only one
permutation.

### D0 - tight-DAG characterization

Enumerate every monotone binary subset-bound table on four outcomes. For each
table, compare the tight-DAG optimizer count with exhaustive enumeration of
all `4!` orderings. For every ordered pair of tables, compare the common-path
count with the exact set intersection of exhaustive optimizer sets.

The expected table count is the classical four-variable Dedekind number:

```text
168.
```

This count is a test-universe check, not a novelty claim.

### G0 - ordering-gauge implication

For every ordered pair in the same four-outcome universe, solve the exact
square equations for a positive ordering-gauge scale. Whenever a positive
scale exists, verify directly across all `4!` orderings that:

```text
C_2(pi) = a C_1(pi) + constant
```

and that the exhaustive optimizer sets agree.

### V0 - v0.48 recovery

The independent common-chain implementation must recover:

```text
first optimizer count  = 1,451,520
second optimizer count = 4,354,560
common optimizer count = 1,451,520
```

It must also find that no positive ordering-gauge scale exists for that pair.

### RESOURCE

The verification must finish within 120 seconds and 512 MiB aggregate working
set on at most four worker processes. The registered implementation is
single-process.

## Decision rule

All checks pass:

```text
finite_common_ordering_theorem_verified
```

Any check fails:

```text
finite_common_ordering_theorem_not_verified
```

No threshold may be changed after execution.

## Claim boundary

Passing verifies finite code/proof consequences over the complete registered
binary table universe. Tests and enumeration do not replace the written
proof, establish novelty, validate continuous or strategic preference access,
or resolve ASMP-9.
