# ASMP-9 selection-channel prior-art gate v0.60

## Verdict

**Ignorable selection, nonignorable missingness, choice-based sampling, and
endogenous or unobserved choice sets are classical.**

Version v0.60 must not claim novelty for:

- recovering a conditional law after observing its stratum;
- positivity as a support and rate condition;
- inverse-probability correction with known selection weights;
- nonidentification under unrestricted outcome-dependent selection; or
- modeling choice-set formation.

The residual ASMP-9 contribution is only the exact composition of those
classical distinctions with the verified finite Luce/RUM/non-RUM access
ledger.

## Missing-data ignorability

Rubin formalized conditions under which a missingness mechanism may be
ignored and distinguished them from nonignorable missingness:

- Donald B. Rubin, "Inference and Missing Data," *Biometrika* 63(3), 1976,
  pp. 581-592.
  <https://doi.org/10.1093/biomet/63.3.581>

The v0.60 pre-response factorization is a finite elementary specialization.
The outcome-dependent recording witness is a direct nonignorable-selection
construction. Neither is a new missing-data theorem.

## Choice-based sampling

Choice- or response-based sampling and correction for the sampling mechanism
are longstanding:

- Charles F. Manski and Steven R. Lerman, "The Estimation of Choice
  Probabilities from Choice Based Samples," *Econometrica* 45(8), 1977,
  pp. 1977-1988.
  <https://doi.org/10.2307/1914121>

Version v0.60 differs only in its frozen object: it asks whether the recovered
conditional menu laws determine one of three structural choice tiers. It does
not advance general choice-based-sampling theory.

## Endogenous and unobserved choice sets

Endogenous choice-set formation is explicitly modeled by:

- Joel L. Horowitz, "Modeling the Choice of Choice Set in Discrete-Choice
  Random-Utility Models," *Environment and Planning A* 23(9), 1991,
  pp. 1237-1246.
  <https://doi.org/10.1068/a231237>

Modern work gives identification results for latent choice sets under panel,
sparsity, rank, bounds, or monotonicity assumptions:

- Victor H. Aguiar and Nail Kashaev, "Identification and Estimation of
  Discrete Choice Models with Unobserved Choice Sets," *Journal of Business &
  Economic Statistics* 43(1), 2025, pp. 204-215.
  <https://doi.org/10.1080/07350015.2024.2342731>
- Nail Lu, "Estimating Multinomial Choice Models with Unobserved Choice
  Sets," *Journal of Econometrics* 226(2), 2022, pp. 368-398.
  <https://doi.org/10.1016/j.jeconom.2021.06.004>

Version v0.60 does **not** subsume those models. It records the actual menu in
the positive theorem and treats unknown outcome-dependent recording in the
negative theorem. Hidden consideration sets remain open.

## Internal prior work

ASMP-9 v0.39 already proved that target-correlated selection of a
decision-equivalent reward representative can leak target information, and
that randomizing the representative assignment erases that leakage.

Version v0.60 concerns a different selection object:

```text
v0.39: which reward representative is observed;
v0.60: which response menu is sampled, and whether the response is retained.
```

The two must not be pooled. The shared lesson is merely that a semantic gauge
or a recorded label does not determine whether its assignment mechanism is
ancillary.

## Residual claim boundary

The candidate residual is:

1. exact reduction of arbitrary recorded pre-response selection to its menu
   support;
2. transfer of the v0.56 compatible-tier theorem to that support;
3. matching `1/pi` selection-floor dependence for the v0.58 positive and
   negative sample bounds on one slice; and
4. an exact complete-support confounding witness under unknown
   outcome-dependent recording, with a known-weight correction.

This is an access ledger, not a novelty claim, a general missing-data theorem,
an identification result for latent choice sets, evidence about real
demonstrators, or a resolution of ASMP-9.
