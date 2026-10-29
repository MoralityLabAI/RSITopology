# ASMP-9 v0.53 development result

## Status

**Development-only; not claim-eligible.**

The aggregate-randomization LP and the subset-table insufficiency witness are
ready for prospective independent verification.

## Headline witness

At `alpha=1/2`, binary reports, and uniform reference weights:

```text
P_A=(3/5,2/5)
P_B=(9/10,1/10)
```

induce the same deterministic subset table:

```text
(0,1,0,1).
```

Both have deterministic optimum `1/2`, but their exact aggregate-randomized
optima differ:

```text
A: 5/12
B: 5/18.
```

Matching one-variable dual certificates attained both lower bounds.

## Development family

The exact solver swept

```text
p = 11/20, 12/20, ..., 20/20
P_p=(p,1-p).
```

All ten experiments had the same subset table and deterministic optimum, but
all ten randomized optima were distinct:

```text
randomized value = 1/(4p).
```

Checks:

```text
subset-table mismatches:       0
closed-form mismatches:        0
dual-certificate mismatches:   0
LP support-bound failures:     0.
```

The one-outcome strict-gain control had deterministic value `1` and randomized
value `1/2`.

## Interpretation

Deterministic Buehler inference depends only on whether a subset probability
crosses `alpha`. Fractional failure allocation depends on how far it lies from
that threshold. Thresholding the experiment into `B(S)` therefore destroys
information required by aggregate randomized optimization.

Randomization itself is classical. The durable ASMP-9 finding is the exact
boundary of the deterministic sufficient statistic.

## Next step

Freeze an independently implemented LP verifier, the ten-point family, primal
and dual controls, basic-feasible support bound, and a one-outcome minimal
strict-gain control before any claim-eligible execution.

## Claim boundary

The result does not establish novelty, recommend randomized safety
certificates, address continuous or strategic uncertainty, validate a
preference channel, or resolve ASMP-9.
