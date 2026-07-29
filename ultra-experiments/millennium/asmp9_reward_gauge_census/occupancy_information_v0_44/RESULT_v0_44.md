# ASMP-9 v0.44 policy-specific information result

## Verdict

**Policy-specific information containment established for finite adaptive risk
polytopes.**

The scalar occupancy proposal from the v0.43 matrix is vacuous under
unrestricted repeatable queries:

```text
sup_pi I_pi(theta) = h max_q kappa(theta,q).
```

Version v0.44 instead retains each policy's information occupancy on the same
generator as its risk vector and propagates generator-specific uncertainty
through exact robust deficiency containment.

This is a finite instrument theorem, not an optimal statistical confidence
construction and not an ASMP-9 resolution.

## The theorem

Every deterministic policy generator carries:

```text
r_pi(theta) = center-channel terminal risk
I_pi(theta) = expected accumulated per-cell information toll
b_pi(theta) = loss_span(theta) min(1,sqrt(I_pi(theta)/2)).
```

If source generators have boxes `g_i +/- b_i` and reference generators have
boxes `f_j +/- c_j`, coordinate monotonicity of directed upper deficiency
gives:

```text
D(G_minus,F_plus)
  <= D(G_true,F_true)
  <= D(G_plus,F_minus).
```

Both endpoints are ordinary exact rational deficiency LPs. The implementation
uses:

```text
KL(P||Q) <= chi2(P||Q)
```

and rounds each square root outward to a rational `10^-12` grid.

## Matched query fixture

The four-target horizon-two tree has:

```text
root  : {0,1} versus {2,3}
left  : 0 versus 1
right : 2 versus 3.
```

The root channel remains exact. Left and right receive symmetric flip
probabilities `eta`.

### Four-class identification

| `eta` | Actual deficiency | Policy-specific upper | Uniform upper |
|---:|---:|---:|---:|
| 0.01 | 0.01 | 0.071066905452 | 0.100503781526 |
| 0.02 | 0.02 | 0.101015254456 | 0.142857142858 |
| 0.05 | 0.05 | 0.162221421131 | 0.229415733871 |
| 0.10 | 0.10 | 0.235702260396 | 0.333333333334 |

All four actual deficiencies lie inside the policy-specific intervals, and
every policy-specific upper endpoint is strictly below its uniform
counterpart.

At `eta=1/20`, the exact zero-risk center policy is:

```text
root(left(A0,A1),right(A2,A3)).
```

It visits one uncertain leaf query per target, so:

```text
I_pi(theta) = 1/19,
```

while the scalar horizon bound prices two:

```text
h max_q kappa(theta,q) = 2/19.
```

### Root-group decision

The same channel library has an exact root-only policy:

```text
root(A0,A1).
```

It has zero risk and zero information occupancy. For all four perturbation
levels:

```text
actual deficiency       = 0
policy-specific interval = [0,0]
uniform upper            > 0.
```

This is the load-bearing decision-relative control: unrelated uncertain
queries do not tax a decision problem whose optimal policy never uses them.

## Honesty and robustness controls

### Scalar-collapse control

For both registered decision problems, the maximum information over the
unrestricted policy class exactly equaled `h max kappa`. Merely renaming that
supremum “occupancy-aware” would not improve v0.43.

### Query-budget control

For one uncertain query at horizon two:

```text
repeatable maximum information = 2/19
one-use path-budget maximum    = 1/19.
```

### Box-universe control

- all eight selected source-box vertices were contained;
- all 64 source/reference-box vertices were contained; and
- center envelope risk sets were deficiency-equivalent to the inherited v0.41
  compiler for both decision problems.

## Gates

| Gate | Check | Result |
|---|---|---|
| `P0` | 20 preregistration tests | pass |
| `S0` | source, inherited compiler, environment, runner, and verifier hashes | pass |
| `C0` | center envelope/compiler equivalence | pass |
| `X0` | exact unrestricted scalar-collapse control | pass |
| `B0` | 72 robust-box vertices | pass |
| `Q0` | pathwise query-budget control | pass |
| `I0` | four classification containment/strictness rows | pass |
| `D0` | four root-group decision-relative rows | pass |
| `R0` | exact registered row universe | pass |
| `RESOURCE` | 120 seconds and 768 MiB ceilings | pass |

Execution used 12.657 seconds and a peak sampled working set of 276,942,848
bytes. Independent deterministic replay reproduced every scientific row and
gate.

## Provenance

- Implementation commit:
  `d87e78026c26b1cf50de96d79a3568324432569a`
- Registration commit:
  `ec7487b2137b5553a17e06316d686911ceceaabe`
- Registration SHA-256:
  `067690ee28cc38f69b70d8581f12fafaf1194a66b6b0b82d1af5854f774746e5`
- Result SHA-256:
  `76375faf5bad1d8c93fd78f2293fa0d9c79680ea8f8c945f476057d34b24cbf5`
- Independent verification SHA-256:
  `2913d3e405cdc0a162c073f8edc91fb3a50bfa1cbed2326f9b7d30dd4772eddd`

## Claim boundary

Version v0.44 proves exact generator-specific robust containment for finite
adaptive risk polytopes and demonstrates strict decision-relative improvement
over a uniform information radius. It does not produce optimal data-derived
KL regions, prove a sharp modulus for every finite channel library, make
policy enumeration efficient, cover nonrectangular or strategic uncertainty,
validate a real reward/value channel, or resolve ASMP-9.
