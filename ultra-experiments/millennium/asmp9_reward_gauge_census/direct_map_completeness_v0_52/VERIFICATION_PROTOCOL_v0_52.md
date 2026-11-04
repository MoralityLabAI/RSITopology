# ASMP-9 v0.52 deterministic direct-map verification protocol

## Status

This protocol freezes an exact finite theorem check. The theorem is a
classical Buehler-optimality corollary and carries no novelty claim.

Development outputs are burned. Only the separately committed verifier,
prospective registration, and write-once verification result are
claim-eligible.

## Frozen universe

Enumerate every normalized monotone table

```text
B : 2^{ {0,1,2} } -> {0,1,2}
B(empty) = 0.
```

Registered counts:

```text
tables:                         148
direct report vectors/table:    27
candidate direct maps:        3,996
valid direct maps:            1,494
invalid direct maps:          2,502
report-consistent orders:     3,342
strict-dominance checks:      2,454.
```

A report vector `u` is valid exactly when

```text
B({x:u(x)<r}) < r
```

for `r=1,2`.

Every total-order refinement of every report tie is included.

## Frozen reference grid

For the global-optimum identity, use every strictly positive
denominator-six reference law:

```text
{(a,b,c)/6 : a,b,c positive integers and a+b+c=6}.
```

There are ten laws and therefore

```text
148 * 10 = 1,480
```

direct-versus-Buehler optimum comparisons.

## Registered controls

Use the two-outcome table

```text
B = (0,1,1,2).
```

Under order `(0,1)`:

```text
equality: (1,2) -> (1,2)
strict:   (2,2) -> (1,2).
```

Independently reconstruct this table from the finite experiment at
`alpha=1/2`:

```text
risk 1: P=(1,0)
risk 1: P=(0,1)
risk 2: P=(1/2,1/2).
```

## Gates

### H0: source integrity

Every source hash in the prospective registration must match.

### T0: tests

All seven scientific tests and four verifier tests must pass under the exact
registered command.

### U0: universe completeness

All registered universe counts must match exactly.

### D0: self-ordering dominance

For every valid direct map and every report-consistent total-order refinement:

- the induced Buehler map is valid;
- it is pointwise no larger than the input map; and
- all mismatch counts equal zero.

The registered strict-dominance count confirms that the verifier did not
collapse to equality-only cases.

### O0: global optimum identity

For every table and every registered positive reference law, the exact
minimum weighted report over all valid direct maps must equal the exact
minimum over all six total-order Buehler maps. All `1,480` comparisons must
execute with zero mismatches.

### C0: control separation

The equality and strict controls must match their frozen outputs exactly.

### X0: experiment realization

Independent reconstruction of the registered two-outcome probability
experiment must yield `(0,1,1,2)`.

### RESOURCE

The single verifier process must finish within 120 seconds and 512 MiB peak
working set, with one worker.

## Stop rule

The theorem is verified only if every gate passes. Equality with a threshold,
missing rows, source mismatch, or a failed test is failure. There is no
discretionary override.

The verification result is write-once. Any post-run defect requires an
additive, separately registered repair that preserves the original files.

## Claim boundary

Passing closes deterministic direct-map completeness in the finite
subset-bound grammar. It does not prove novelty, aggregate randomized
coverage optimality, two-sided confidence-set optimality, continuous or
strategic robustness, validity of any physical preference channel, or a
resolution of ASMP-9.
