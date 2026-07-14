# Control-risk red-team results

The registered v0.1 population contains 6,000 CPU-synthetic signed-coordinate chains. The gate uses a conservative cumulative lineage-plus-holonomy operator bound with explicit denial on orientation reversal or missing loop measurement.

## Result

- Authorized precision: `1.000` (`792/792` authorized fixtures were inside the control-loss budget).
- False-authorization rate: `0.000`.
- Authorization coverage: `0.132`.
- Full-vector AUROC: `0.900827`.
- Holonomy-only AUROC: `0.954639`, but it has planted lineage-only false-safe cases.
- Lineage-only AUROC: `0.329252`, with planted curvature false-safe cases.
- All orientation reversals were denied and all unmeasured loops abstained.
- The 2,800-point analytic boundary grid produced zero unsafe authorizations.

The result distinguishes ranking from certification. Holonomy alone ranks this planted population better, because holonomy dominates its loss variation. The complete vector is more conservative and has lower AUROC, but closes both single-feature blind spots and supplies the proved false-authorization guarantee. “High accuracy” is therefore justified for selective authorization precision, not as universal behavioral prediction.

## Boundary thresholds

With error budget `epsilon=0.5`, pure rank-two holonomy loses control at

`alpha > 2 asin(epsilon/2) = 28.955 degrees`.

At zero holonomy and `m` identical contraction edges, actual loss crosses the budget when

`W < 0.5^(2/m)`.

For `m = 1, 2, 4, 6`, those retention thresholds are `0.25`, `0.50`, `0.7071`, and `0.7937`. The conservative cumulative gate requires `W >= (1-0.5/m)^2`, giving `0.25`, `0.5625`, `0.7656`, and `0.8403`. The growing gap is the measurable price of safe composition over longer paths.

## Red-team integrity finding

Before hardening, scalar receipts outside geometric domains could authorize, and sectioning trusted a reported plaquette loss without composing its boundary transports. The implementation now range-checks edge and loop metrics, requires directed closed loops, checks measured loss intervals, and recomputes sectioning determinant and loss from ordered transports. Attestation matrices remain upstream hash-bound rather than embedded, so a trusted sealed registry root remains an assumption.

## Claim boundary

These results concern synthetic loss of signed-coordinate identity. Identity measurements alone cannot prove general self-improvement risk: downstream systems with identical identity geometry can attach different behavior to the same coordinate. Real behavioral prediction requires grouped held-out outcomes and nuisance baselines.

