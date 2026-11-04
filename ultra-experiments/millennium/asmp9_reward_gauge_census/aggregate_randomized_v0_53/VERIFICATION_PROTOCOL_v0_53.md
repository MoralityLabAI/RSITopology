# ASMP-9 v0.53 aggregate-randomization verification protocol

## Status

This protocol freezes an exact finite theorem check. Randomized confidence
procedures are classical. The claim-eligible target is the insufficiency of
the deterministic subset-bound table for aggregate randomized optimization.

Development outputs are burned. Only the separately committed verifier,
prospective registration, and write-once result are claim-eligible.

## Frozen family

Use:

```text
alpha = 1/2
reports = {0,1}
reference weights = (1/2,1/2)
risk = 1
P_p = (p,1-p)
p in {11/20,12/20,...,20/20}.
```

For each of the ten experiments verify:

```text
subset table = (0,1,0,1)
deterministic optimum = 1/2
aggregate randomized optimum = 1/(4p)
dual multiplier = 1/(2p)
positive support <= n+k = 3.
```

The primary witness is `p=3/5` against `p=9/10`, with randomized values
`5/12` and `5/18`.

## Independent optimizer

The verifier must not import the development solver. In the frozen binary
one-parameter family, enumerate every vertex of

```text
p s_0 + (1-p) s_1 >= 1/2
0 <= s_i <= 1
```

from intersections of the coverage boundary and the four box boundaries.
Minimize `(s_0+s_1)/2` exactly in rational arithmetic.

The dual lower certificate is:

```text
lambda = 1/(2p)
lambda P_p(x_i) <= 1/2 = w_i
value >= lambda/2 = 1/(4p).
```

## Controls

### Minimal strict gain

One outcome with risk `1` and `alpha=1/2` must have:

```text
deterministic value = 1
randomized value = 1/2.
```

### Invalid-component mixture

For `p=3/5`, the optimal randomized procedure is the mixture:

```text
5/6 * deterministic map (1,0)
+ 1/6 * deterministic map (0,0).
```

The second component is individually invalid, while the mixture has exact
aggregate coverage `1/2`. This distinguishes v0.53 from v0.51.

### Support-bound saturation

Under two crossing coverage constraints

```text
P_1=(3/4,1/4)
P_2=(1/4,3/4)
alpha=1/4,
```

the symmetric optimizer `s=(3/4,3/4)` has four positive conditional report
atoms, saturating `n+k=4`.

## Gates

### H0: source integrity

Every registered source hash must match.

### T0: tests

All five scientific tests and four verifier tests must pass.

### F0: family completeness

All ten registered `p` values must execute, all ten subset tables must match,
and all ten randomized values must be distinct.

### P0: primal identity

Every independently enumerated optimum must equal `1/(4p)` with zero
mismatches.

### D0: dual identity

Every multiplier must be feasible and attain the primal value exactly.

### I0: information-loss witness

The primary pair must have identical subset tables and deterministic optima
but randomized values exactly `5/12` and `5/18`.

### M0: invalid-component mixture

The frozen mixture must reconstruct the optimal marginals, contain one
individually invalid component, and attain aggregate coverage exactly.

### S0: support bounds

Every one-constraint family optimizer must use at most three positive atoms.
The two-constraint control must use four and equal `n+k`.

### C0: one-outcome control

The frozen minimal strict-gain values must match.

### RESOURCE

The verifier must finish within 60 seconds and 256 MiB peak working set with
one worker.

## Stop rule

Every gate must pass exactly. Missing cells, equality with a cap, source
mismatch, or any primal/dual discrepancy is failure. There is no discretionary
override.

The verification result is write-once. Repairs must be additive and separately
registered.

## Claim boundary

Passing verifies a finite information-loss theorem inside classical
randomized confidence theory. It does not establish novelty, operational
desirability of randomized safety certificates, continuous or strategic
robustness, a physical preference channel, or an ASMP-9 resolution.
