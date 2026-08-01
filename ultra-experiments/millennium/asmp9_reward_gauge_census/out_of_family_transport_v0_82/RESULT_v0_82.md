# ASMP-9 v0.82 result: local response structure transports; one global coefficient does not

## Registered verdict

> `out_of_family_response_transport_not_established`

The fixed sequence stopped at `G0`.  No threshold, family, prompt, or
calibration quantity was changed after the 528-score holdout began.

## Gate results

| Gate | Result | Receipt |
| --- | --- | --- |
| `N0` new-family and score universe | **pass** | 12 family labels disjoint from v0.68; 528/528 registered rows |
| `I0` repeat/render/quotient integrity | **pass** | exact repeat identity and zero-sum quotient mechanics |
| `L0` local response liveness | **pass** | 12/12 scenarios passed; requirement 10 |
| `T0` construction-envelope transport | **pass** | 11/12 scenario means inside the frozen envelope; requirement 10 |
| `G0` single-coefficient transport | **fail** | 21/24 target cells intersected the frozen construction interval; requirement 24 |
| `R0` owned-process resource and cleanup | **pass** | runner and analysis exit 0; cleanup passed; no lingering owned PID |

The independent audit recomputed every scientific gate from the sealed JSONL
without importing the registered analyzer.

## What failed

The construction common-coefficient interval was

```text
[0.7343614199407966, 0.750013550256881]
```

Three new-family target cells lay entirely above it after the registered
endpoint guard was applied:

| Family | Target | New interval lower | Interpretation |
| --- | ---: | ---: | --- |
| conflict of interest | 1 | 0.8281136271 | positive response stronger than the global band |
| consent/autonomy | 0 | 0.8124885973 | positive response stronger than the global band |
| consent/autonomy | 1 | 0.8906135377 | positive response stronger than the global band |

This was not a loss of the directed effect.  Every one of the twelve new
families passed local liveness.  The failure is specifically the hypothesis
that one narrow construction coefficient can describe all target cells across
unseen behavior families.

## What survived

- Mean new-family scenario mean: `0.9547526137903333`.
- Frozen construction center: `0.9381510370100538`.
- Median new-family scenario mean: `0.9316406417638063`.
- Eleven of twelve scenario means were inside the prospectively frozen
  max-construction-residual envelope
  `[0.5208333500971378, 1.3554687239229698]`.
- The sole envelope miss was consent/autonomy at `1.3789062798023224`, above
  the upper endpoint by about `0.02344`.

Thus the direction and coarse magnitude of the quotient response transported,
while the stronger context-independent coefficient claim did not.

## Resource record

The Qwen3.5-0.8B holdout used singleton float16 next-token scoring:

- runner elapsed: `402.09 s`;
- analysis elapsed: `15.32 s`;
- peak GPU memory: `1797 MB`;
- peak temperature: `84 C` under the registered `88 C` abort;
- peak owned working set: `2037.04 MB`; and
- cleanup: passed, zero lingering owned PIDs, GPU returned to `0 MB`.

The inherited v0.68 wrapper emitted its native `cleanup_invalid` label because
system-wide page-file use moved by 20 MB.  V0.82 prospectively registered that
quantity as telemetry rather than owned-process evidence.  The independent
R0 evaluator therefore passed because both phases exited zero, all owned hard
caps held, cleanup passed, and no owned process survived.  This does not revise
the old v0.68.2.1 receipt.

## Scientific consequence

V0.81 showed that exact known offsets can repair a synthetic cardinal decoder.
V0.82 now gives the physical-channel boundary: a nuisance-quotiented response
direction is repeatable and broadly portable across new families, but treating
its amplitude as one global scalar is too strong.  Any successor must either:

1. prospectively model family-conditioned coefficients and pay the resulting
   access/complexity cost; or
2. prove a theorem showing what additional intervention structure makes a
   global coefficient identifiable.

Refitting a wider band to these outcomes would only restate the observed
heterogeneity and is not an admissible confirmation.

## Claim boundary

This result concerns expressed A/B response contrasts in one frozen Qwen0.8B
registry.  It does not identify model or human values, prove that natural
systems expose calibrated intervention offsets, identify a reward-shaping
orbit, establish population generalization, authorize recursive improvement,
or resolve ASMP-9.

