# ASMP-7 excluded-band degradation result v0.2.1

## Verdict

`exact_boundary_degradation_surface_established`

All five instrument gates and the registered surface-liveness gate passed. The
run computed exact minimum challenge counts for all 48 registered
`forbidden-boundary × truth-report-probability` cells. All 40 nonzero-gap cells
were feasible below the uniform `m=32,768` cap; the eight `theta=1/2` cells
were exactly uninformative as registered.

V0.2 first stopped without an outcome because CPython refused to serialize an
exact fraction exceeding its default 4,300-digit limit. V0.2.1 was separately
registered and changed only trusted exact-integer serialization. The failure
is preserved in `FAILURE_v0_2.md` and `artifacts_v0_2/failure_receipt.json`.

## Exact surface

Each entry is the exact minimum `m*` for separately enforcing
`FP<=1/20` and `FN<=1/20` with the registered randomized UMP test.

| Forbidden boundary `k1` | Class size | `theta=3/5` | `2/3` | `3/4` | `4/5` | `1` |
|---:|---:|---:|---:|---:|---:|---:|
| 9 | 26,333 | 17,312 | 6,230 | 2,767 | 1,921 | 690 |
| 10 | 14,893 | 4,325 | 1,555 | 690 | 477 | 170 |
| 11 | 6,885 | 1,921 | 690 | 304 | 211 | 73 |
| 12 | 2,517 | 1,079 | 386 | 170 | 117 | 40 |
| 13 | 697 | 690 | 246 | 108 | 73 | 23 |
| 14 | 137 | 477 | 170 | 73 | 50 | 15 |
| 15 | 17 | 350 | 124 | 53 | 35 | 10 |
| 16* | 1 | 267 | 94 | 40 | 26 | 5 |

`* k1=16` is the preregistered `singleton_boundary_control`, not a
representative capability class. At `theta=1/2`, every row is infeasible at
every finite `m` because the two report laws are both `Binomial(m,1/2)`.

The v0.1 slice at `k1=14` reproduced exactly: `m*=73,50,15` for
`theta=3/4,4/5,1`, while `theta<=2/3` remained infeasible under the old
`m<=128` cap.

## Why the surface is simple

The compliant boundary is independent of channel truthfulness:

```text
q(8,theta) = 1/2.
```

Every cell is therefore controlled by the single exact separation

```text
delta(k1,theta) = (2*theta-1)*(k1-8)/16.
```

Class cardinality affects how many executions occupy the forbidden composite
class, but not the uniform worst-case law: the boundary value `k=k1` is always
least distinguishable.

## Descriptive inverse-square calibration

On the frozen subset of feasible, non-singleton cells with `m*>=100`, the
preregistered descriptive regression gave

```text
log(m*) = 0.955407 - 2.011203*log(delta)
R^2 = 0.999989
n = 25 cells.
```

Across all 40 feasible cells, the exact minimum exceeded the registered normal
reference by only `1.04` to `2.80` challenges. This makes the inverse-square
relationship an excellent explanation of this finite surface. It remains a
descriptive calibration of a classical approximation, not evidence for a new
asymptotic theorem.

## Exact certificates

For every feasible cell:

- the false-positive probability equals exactly `1/20`;
- the false-negative probability at `m*` is at most `1/20`; and
- the exact false-negative probability at `m*-1` is greater than `1/20`.

The full numerator/denominator certificates are stored in
`artifacts_v0_2_1/result.json`. SciPy was used only to propose candidate
locations. Integer binomial numerators and `fractions.Fraction` determined
every cutoff, minimum, and gate.

## Gates

| Gate | Result |
|---|---|
| E0 exact adjacency | pass; zero failures |
| R0 v0.1 reproduction | pass; zero failures |
| C0 class census | pass; zero failures |
| O0 monotone order | pass; zero failures |
| S0 surface liveness | pass; zero missing nonzero-gap cells |
| B0 singleton boundary label | pass; zero failures |

## Interpretation

V0.1 showed that semantic challenges can restore attestability when trace laws
overlap. V0.2.1 shows exactly how rapidly their cost grows as the policy margin
shrinks. At the narrowest registered boundary, moving from fully truthful
reports to `theta=3/5` raises the minimum from 690 to 17,312 challenges. Thus a
small semantic separation and a weakly truthful channel can make a formally
attestable predicate operationally expensive even in this tiny registry.

The result also closes the omitted-band objection only as a measurement: it
does not decide where a real policy should place the compliant/forbidden
boundary. That remains normative and deployment-specific.

## Claim boundary

This is exact finite rational evidence for the frozen 16-point Boolean
registry, independent with-replacement challenges, fresh randomized response,
and assumed meter coverage. It does not establish real-model capability
attestability, a universal compression theorem, an asymptotic sample-complexity
theorem, or correctness of any real policy boundary.

## Reproducibility

- prereveal v0.2 source commit:
  `7c2a2b3ecba63739f883b54a23e0a78fa965e47a`
- v0.2 failed registration commit:
  `12ef776b1ccf5c060968c5b3dfc3f4cc3e173340`
- v0.2.1 repair source commit:
  `afcb2c9e22e4bba306eb1839bd4d9ef3a27e7cc5`
- v0.2.1 registration commit:
  `4e730570b39d20bb1f58d74d9d4c0e7f042d718b`
- v0.2.1 registration SHA-256:
  `7a56a4a90c7b4d7e48960c417a1a6b5e0e702720d8caba9f9c6818f0dcd91647`
- result SHA-256:
  `39e8c12267a4a0e4ec2397960b00e63eed590c4ae30b15e21052b52b37e0af78`
- frontier CSV SHA-256:
  `850b59175876bbc413cbd1fdb0c7abbff9e74069b21ba852147a315014230468`
- dedicated tests: 7 passed
- compute: CPU only; no GPU

