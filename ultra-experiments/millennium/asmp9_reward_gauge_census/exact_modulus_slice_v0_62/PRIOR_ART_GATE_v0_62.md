# ASMP-9 exact-modulus-slice prior-art gate v0.62

## Verdict

The mathematical ingredients are classical:

- finite random-utility polytopes and ranking-mixture representations;
- total variation and Huber contamination neighborhoods;
- likelihood-ratio neighborhoods; and
- primal/dual certificates for finite convex optimization.

The v0.62 calculation is an ASMP-9 calibration slice, not a novelty claim.

## Direct inherited anchors

Random-utility feasibility and finite stochastic rationalizability are in the
McFadden-Richter/ARSP lineage.  The exact three-alternative classifier and
ranking convention are inherited from the prospectively verified ASMP-9
v0.54 result.

Huber contamination and robust testing are classical:

- Peter J. Huber, “Robust Estimation of a Location Parameter,” 1964.
  <https://doi.org/10.1214/aoms/1177703732>
- Peter J. Huber and Volker Strassen, “Minimax Tests and the Neyman-Pearson
  Lemma for Capacities,” 1973.
  <https://doi.org/10.1214/aos/1176342363>

Outcome-dependent recording and inverse correction sit in the classical
missing-data and choice-based-sampling literatures cited in v0.60.

## Residual claim boundary

The only candidate residual is the exact specialization

```text
Delta=gamma,
Lambda=1+(5/2)gamma
```

for the frozen continuous two-segment slice, together with explicit
attainment and lower certificates.  Even if correct, it is not a new general
theory and does not resolve ASMP-9.

