# ASMP-9 resolution-obligation matrix after v0.76 development

## Verdict

**ASMP-9 remains unresolved.**

Version v0.76 separates decoder-based target recovery from the stronger
requirement that observations themselves be representative-insensitive. Exact
partition equality requires both.

## Status against the five obligations

| Obligation | Strongest evidence after v0.76 | Status | Missing resolution evidence |
|---|---|---|---|
| 1. Maximal invariance or identifiability object | v0.74 separates observation fibers from licensed orbits; v0.76 distinguishes target sufficiency from nuisance invariance | **Canonical target grammar corrected** | Behavioral justification of targets and gauges across real data sources |
| 2. Necessary and sufficient access | `O`-fibers refining target fibers is necessary and sufficient for recovery; reverse refinement is representative insensitivity; equality is exact interface | **Exact for arbitrary finite deterministic maps** | Approximate stochastic laws, continuous classes, adaptive physical access, and computable decoders |
| 3. Sharp query/sample/intervention bounds | v0.70-v0.72 provide restricted Gaussian cells; v0.74 supplies finite deterministic set cover | **Restricted exact cells** | General minimax rates and physical acquisition costs |
| 4. Robustness to misspecification | Cross-cut interfaces now distinguish simultaneous leakage and underidentification | **Exact interface misspecification taxonomy** | Approximate equality, drift, dependence, contamination, and strategic response |
| 5. No-go without a coherent latent value object | v0.71-v0.73 provide deterministic history replacements and finite-prefix limits | **One deterministic replacement branch** | Relation-, stochastic-kernel-, set-, continuous-process-, and multi-agent replacements |

## Required reporting fields

Every successor access certificate should report separately:

```text
target_recoverable
representative_insensitive
exact_partition_match
```

Invalidity or failure of one field must not be silently substituted for
another.

## Claim boundary

Version v0.76 is an exact finite formulation correction. It does not validate
the target, gauge, response channel, or behavioral premises and does not
resolve ASMP-9.
