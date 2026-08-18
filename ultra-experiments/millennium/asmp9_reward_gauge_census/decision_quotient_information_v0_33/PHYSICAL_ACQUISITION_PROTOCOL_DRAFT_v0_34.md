# ASMP-9 physical coupling-acquisition protocol v0.34

## Status

**Draft only. Not registered. Not authorized to read outcomes.**

This successor would test whether the exact 18-dimensional coupling quotient
is measurable through end-to-end interventions. The numeric calibration
thresholds remain deliberately unset until a disjoint burned pilot is
specified; this document must not be represented as frozen.

## Primary object

The target remains:

```text
M vec(K) = vec(Q L K C),
```

where `L`, `Q`, and `C` are the sealed v0.31-v0.32 matrices. The preferred
factorized design uses policy contrasts `(0,1,2)` and behavioral cells
`(0,1,2,4,5,7)`, producing 18 scalar composite probes.

Each probe must be operationalized before outcome capture as:

```text
one declared behavioral-cell perturbation
  -> model execution under one frozen environment
  -> one declared analyzed policy-contrast readout.
```

No outcome-dependent redefinition of a perturbation, readout, site, prompt
family, or sign convention is permitted.

## Required prereveal artifacts

1. Exact source hashes for the v0.31 analysis/policy matrices and v0.32
   cross-difference operator.
2. A machine-readable list of all 18 perturbation/readout pairs.
3. Model, tokenizer, checkpoint, precision, prompt-family, site, and seed
   manifests.
4. A disjoint burned-pilot receipt defining the empirical error estimator and
   intervention-norm grid.
5. The query-span evaluator source and environment hash.
6. A sealed outcome join keyed one-to-one by probe, prompt group, norm,
   replicate, and run.

## Frozen structural gates

### S0 — provenance

All source, protocol, runner, environment, and prompt hashes match. Any
missing, extra, duplicate, or noncanonical ID makes the instrument invalid.

### S1 — target liveness

The canonical decision operator has rank 18. The preferred query operator has
rank 18 and satisfies `rank(stack(H,M)) = rank(H)`. All 18 leave-one-out
controls must fail with one exact missing dimension.

### S2 — negative controls

The six-diagonal shortcut must report twelve missing dimensions. Every
47-of-48 entrywise control must report one missing dimension. Any false pass
invalidates the span evaluator.

## Empirical gates requiring pilot-derived numbers

### E0 — intervention liveness

Every selected perturbation produces a nonzero, finite, repeatable readout
above its matched sham-intervention null on construction prompts. Missing
cells remain missing; no replacement is chosen after outcomes.

### E1 — local linearity

For every admitted norm, estimate a simultaneous upper bound
`epsilon_secant` on the absolute difference between the observed composite
response and the registered local linear prediction. Norms failing the bound
are excluded individually; no pooled norm claim is permitted.

### E2 — held-out reconstruction

Apply the exact reconstruction operator `R` on held-out prompt groups. The
observed maximum decision-effect error must lie below both:

```text
8 epsilon_secant
```

and a separately registered practical margin. Failure of either bound returns
`not_established`.

### E3 — direct comparator

On held-out probes not used to fit nuisance parameters, compare reconstructed
decision effects with direct policy-contrast measurements. Splits must be
grouped by prompt family and run replicate.

## Decisions

```text
quotient_spanned_physical
  all structural and empirical gates pass;

decision_access_insufficient
  the admitted physical query operator fails the exact span gate and an
  invisible decision-changing witness is returned;

not_established_by_linearity
  the intended operator spans algebraically but the secant/reconstruction
  bounds fail;

not_evaluated
  provenance, liveness, coverage, or outcome-join validity fails.
```

Only `quotient_spanned_physical` may feed the later stochastic policy
experiment. No status here establishes behavioral validity outside the
registered model, maximal reward invariance, or an ASMP-9 resolution.

## Before registration

The following choices still require a burned pilot and a versioned amendment:

- intervention norms and the norm-specific secant ceiling;
- prompt families and minimum independent replicate count;
- confidence construction and familywise error level;
- practical policy-margin threshold;
- query costs and the direct-comparator allocation; and
- model/checkpoint/site selection.

Until those values are frozen, this remains a design document.
