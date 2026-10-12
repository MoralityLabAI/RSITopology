# ASMP-9 contamination-radius prior-art gate v0.59

## Verdict

**Huber contamination neighborhoods and minimax robust testing are classical.**
The exact finite-alphabet overlap calculation is an elementary specialization,
not a candidate novelty claim.

The only residual contribution considered here is the composition with the
ASMP-9 tier object:

```text
Huber neighborhood overlap
  + bounded-context inverse modulus
  + Luce/RUM separation promise
  -> a tier-identification contamination ledger.
```

Novelty is not established.

## Classical contamination model

Huber's gross-error model introduces observations from

```text
(1-epsilon)P + epsilon Q
```

with arbitrary `Q`:

- Peter J. Huber, "Robust Estimation of a Location Parameter",
  *Annals of Mathematical Statistics* 35(1), 1964, pp. 73-101.
  <https://doi.org/10.1214/aoms/1177703732>

Version v0.59 applies that classical model independently to each registered
menu. It does not claim to introduce distributional contamination.

## Robust testing

Composite robust tests, least-favorable pairs, and neighborhood-based minimax
testing predate this project:

- Peter J. Huber and Volker Strassen, "Minimax Tests and the Neyman-Pearson
  Lemma for Capacities", *Annals of Statistics* 1(2), 1973, pp. 251-263.
  <https://doi.org/10.1214/aos/1176342363>
- Mengjie Chen, Chao Gao, and Zhao Ren, "A General Decision Theory for
  Huber's epsilon-Contamination Model", *Electronic Journal of Statistics*
  10(2), 2016, pp. 3752-3774.
  <https://doi.org/10.1214/16-EJS1216>

The class-modulus threshold in v0.59 is a finite categorical restatement of
robust distinguishability. It is not a new minimax-testing theory.

## Model distinction

The registered model randomizes each observation from a fixed mixture law. It
is weaker than strong contamination or sample-manipulation models in which an
adversary replaces realized samples:

- Jayadev Acharya, Ziteng Sun, and Huanyu Zhang, "Robust Testing and
  Estimation under Manipulation Attacks", ICML 2021, PMLR 139:43-53.
  <https://proceedings.mlr.press/v139/acharya21a.html>

No result may be transferred from v0.59 to that stronger model without a
separate proof.

## Choice-model inheritance

The Luce/RUM tiers, bounded-context class, reconstruction norm, and clean
finite-sample classifier are inherited from v0.54-v0.58 and their cited
stochastic-choice literature. Version v0.59 does not claim novelty for Luce,
ARSP, contextual-choice models, Mobius interpolation, Hoeffding, or
likelihood-ratio oscillation.

## Residual claim boundary

The candidate residual is:

1. an exact per-menu contamination-overlap certificate;
2. the induced exact cross-tier class modulus;
3. a constructive RUM/non-RUM equality witness;
4. a bounded-context lower bracket on the modulus; and
5. an explicit sampling corollary showing contamination and statistical error
   consuming separate parts of the clean margin.

This is not a minimax robust-testing theorem, an efficient modulus algorithm,
a strategic-corruption result, an empirical finding, or an ASMP-9 resolution.
