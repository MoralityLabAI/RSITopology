# ASMP-9 v0.46 coupled shared-channel result

## Verdict

**`coupled_image_conservatism_established_allocation_unchanged`**

All thirteen registered gates passed.  On the frozen horizon-two experiment,
the exact uncertainty image induced by three shared binary-channel parameters
has a strictly smaller robust-risk endpoint than the inherited
independent-generator rectangle.  The integer allocations selected by the two
uncertainty models nevertheless agree.

This closes the finite coupled-image target in the v0.45 resolution-obligation
matrix.  It does not establish a general nonrectangular robust-control theorem,
minimax confidence constants, strategic robustness, a valid real preference
channel, or resolution of ASMP-9.

## Frozen confirmation

- Four latent targets.
- Three binary queries: `(root,left,right)`.
- Horizon two and the complete adaptive policy class.
- One shared symmetric flip parameter per query.
- Zero observed known-target calibration errors.
- Simultaneous familywise level `alpha=0.05`.
- Exact method-of-types parameter endpoint:

  ```text
  p_max(n) = min(1/2, 1-exp(-ceil_1e-12(log(3(n+1)/0.05)/n))).
  ```

- Total calibration budget `N=66`, with at least one sample per query.
- Exactly `C(65,2)=2,080` labelled allocations per decision problem.
- A disjoint `N=60` development census was disclosed and burned before the
  confirmation was registered.

The exponential endpoint was enclosed by exact rational alternating-series
bounds and rounded outward.  No floating-point exponential entered a
scientific bound.

## Exact coupled results

The full horizon-two compiler produced exactly 3,748 distinct deterministic
four-class policy-risk polynomials.  Randomized policies are their convex
hull.  Finite minimax duality reduced each robust classification calculation
to a five-variable linear program; floating-point solutions proposed active
bases, while exact rational elimination checked the selected primal and dual
certificates against all policy constraints.

| Decision problem | Unique coupled optimum | Coupled upper endpoint | Uniform coupled upper | Relative improvement lower bound |
|---|---:|---:|---:|---:|
| four-class identification | `(28,19,19)` | `0.4725225142536221` | `0.4817295510465465` | `1.911246%` |
| root-group loss | `(64,1,1)` | `0.121200875641` | `0.280089971626` | `56.727877%` |

The certified four-class optimum interval was

```text
[472522514252167454047647 / 10^24,
 4725225142536220736103   / 10^22].
```

Its width was approximately `1.455e-12`, and the certified gap to the
second-best allocation was approximately `8.075e-4`.  No allocation required
post-selection sharpening.  The root-group optimum interval had width exactly
`1e-12`, with a certified uniqueness gap of approximately `1.585e-3`.

Canonical coupled-row hashes:

```text
four-class:
0276022876a654c2e1eb94b9f1b03b6d61d6d871db720814f80681d3e0bb3c6e

root-group:
94df3a12247c142d627e0bdbaccc9f800a75d3b29e314cda1cc238287a3eeed1
```

## Exact rectangular comparison

The inherited v0.45 rectangle was exhausted over the same allocations.

| Decision problem | Unique rectangular optimum | Rectangular endpoint at optimum | Rectangle minus coupled upper |
|---|---:|---:|---:|
| four-class identification | `(28,19,19)` | `0.565530324382` | `0.0930078101283779` |
| root-group loss | `(64,1,1)` | `0.254164252874` | `0.132963377233` |

Strict conservatism also held at the uniform allocation:

```text
four-class gap : 0.0915322001384535
root-group gap : 0.125267300032
```

The allocation comparison is therefore:

```text
shared coupling materially lowers the endpoint
but does not change either integer optimizer on this fixture.
```

For four-class loss, the convenient rectangular formula differed from the
exact rectangle on 1,739 of 2,080 allocations but underbounded it zero times
and selected the exact optimum.  Root-group loss matched exactly on every
allocation.  The conclusion uses the exact audit, not the convenient formula.

Canonical rectangular-row hashes:

```text
four-class:
791e83281a8adaea0fddfe30ed017476f0cf055e7437f9a3961a392b20079f52

root-group:
7f37d160a0453afdf3c80a18f3f5f8a4d6876cf63d0e9de1ae085a71f58ddee1
```

## Product-family control

The matched control independently varied four generator coordinates and
exhausted all 16 vertices.  Its exact coupled supremum and rectangular upper
were both

```text
23/40.
```

Thus the strict gap in the shared-channel fixture is attributable to parameter
coupling rather than a generic mismatch between the two implementations.

## Why the worst shared corner is exact

For `0 <= p <= q <= 1/2`, define

```text
r = (q-p)/(1-2p).
```

Then `BSC(q)` equals `BSC(p)` followed by the independent garbling `BSC(r)`.
Blackwell monotonicity, including adaptive simulation of this additional
garbling after each query output, moves the coupled supremum to the upper
corner of the three parameter intervals.  The continuous robust optimization
therefore reduces exactly to one finite channel evaluation.

## Gates and replay

| Gate | Result |
|---|---|
| `P0`: exactly 21 dedicated tests | pass |
| `S0`: all frozen and inherited source hashes | pass |
| `U0`: exact allocation universe and query order | pass |
| `E0`: 3,748 symbolic policies and compiler spot checks | pass |
| `X0`: outward exponential and probability enclosures | pass |
| `B0`: certified lower bounds and exact winning certificates | pass |
| `C0`: predicted unique four-class optimum | pass |
| `G0`: predicted unique root-group optimum | pass |
| `R0`: predicted unique rectangular optima | pass |
| `K0`: strict endpoint gaps at optima and uniform | pass |
| `O0`: exact allocation comparison reported | pass |
| `PC0`: 16-vertex product control exact | pass |
| `RESOURCE`: time, memory, and worker ceilings | pass |

The registered run used `574.156` seconds and a peak aggregate working set of
`428,048,384` bytes, below the frozen ceilings of 600 seconds and 1.5 GiB.
An independent full replay reproduced the coupled rows, rectangle payload,
scientific payload, gates, and every registered source hash exactly.

One operational incident is retained in provenance: a foreground launcher
timeout left a duplicate process alive.  It was detected and terminated,
together with its children, before any result artifact existed.  The tracked
registered run was the only process that wrote the sealed artifacts.

## Provenance

- Implementation commit:
  `b54283e4d82c591b86aa8ca8d2096318474f6b94`
- Registration commit:
  `1f010f6ff972c9162ad51511d87e8f1efb20970c`
- Registration SHA-256:
  `2242ffe6e287f112cd1ed99652252fcf8f30171c11aa5c465c5fdcaf96923598`
- Result SHA-256:
  `18a6a7b85093a1013dcb4d93ccbf449bbc8203843f2d5c368c4d48639fe5e915`
- Independent verification SHA-256:
  `ffbd6864b445caa576b0d87c047da5d217f3af3dd343bf228dcfb9c11da02334`

## Claim boundary

Version v0.46 proves an exact finite coupled-image and allocation result for
one iid, zero-error, three-parameter symmetric-flip grammar.  It composes
classical method-of-types, Blackwell comparison, finite minimax, and robust
optimization results into an executable audit.  It does not prove efficient
policy compilation, optimal simultaneous confidence constants, a matching
general deficiency lower bound, robustness to correlated, adaptive, or
strategic misspecification, validity of a real preference-query channel, or
resolution of ASMP-9.
