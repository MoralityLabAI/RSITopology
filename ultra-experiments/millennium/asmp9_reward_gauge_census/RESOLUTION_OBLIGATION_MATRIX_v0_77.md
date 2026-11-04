# ASMP-9 resolution-obligation matrix after v0.77 development

## Verdict

**ASMP-9 remains unresolved.**

Version v0.77 extends the v0.76 target-interface distinction to known finite
iid observation laws and adds one explicit finite-sample/misspecification
certificate.

## Status against the five obligations

| Obligation | Strongest evidence after v0.77 | Status | Missing resolution evidence |
|---|---|---|---|
| 1. Maximal invariance or identifiability object | Observation-law equality classes are separated from target classes and representative leakage | **Exact for finite known laws** | Behavioral derivation of target, gauge, and law classes |
| 2. Necessary and sufficient access | Cross-target law equality is the exact population obstruction; positive Hellinger gap activates finite iid recovery | **Exact population condition; sufficient finite bound** | Adaptive environments, continuous classes, dependent data, and physical acquisition |
| 3. Sharp query/sample/intervention bounds | Hellinger union bound is explicit; exact binary fixture needs 3 samples versus bound 6 | **One calibrated finite stochastic cell** | General sharp minimax rates, query design, unknown laws, and interventions |
| 4. Robustness to misspecification | Per-sample TV error incurs `1-(1-epsilon)^n`; the frozen nominal certificate fails its 0.1% stress | **One worst-case iid robustness bound** | Structured misspecification, drift, contamination, dependence, and strategic response |
| 5. No-go without a coherent latent value object | v0.71-v0.73 provide deterministic history replacements and finite-prefix limits | **One deterministic replacement branch** | Stochastic-kernel, relation-, set-, continuous-process-, and multi-agent replacements |

## New reporting rule

Finite stochastic access claims must state:

```text
population identifiability status;
cross-target distributional gap;
registered finite-sample bound and whether it is sharp;
representative leakage;
misspecification radius and accumulated penalty.
```

## Claim boundary

Version v0.77 assumes a known finite iid registry. It does not validate human
or model behavior, generalize to open-ended environments, or resolve ASMP-9.
