# ASMP-9 incomplete-menu prior-art gate v0.55

## Verdict

**Existential rationalizability on arbitrary finite observed choice problems
is classical.**

McFadden and Richter formulate stochastic rationalizability for an arbitrary
finite family of observed choice situations. The observed probability vector
is rationalizable exactly when it lies in the convex hull of the admissible
deterministic choice types; their Axiom of Revealed Stochastic Preference
gives an equivalent inequality system. Stoye gives a short modern proof and
explicitly uses an arbitrary fixed collection of observable choice problems.

Primary and direct sources:

- Daniel McFadden and Marcel K. Richter, "Stochastic Rationality and Revealed
  Stochastic Preference", in *Preferences, Uncertainty, and Optimality*, 1990,
  pp. 161-186.
- Daniel McFadden, "Revealed Stochastic Preference: A Synthesis", 2004,
  <https://eml.berkeley.edu/wp/mcfadden0204/stochastic.pdf>.
- Jorg Stoye, "Revealed Stochastic Preference: A One-Paragraph Proof and
  Generalization", *Economics Letters* 177, 2019, pp. 66-68,
  <https://doi.org/10.1016/j.econlet.2018.12.023>.

For complete finite menu systems, the random-ordering representation and
Block-Marschak inequalities are due to Block-Marschak and Falmagne:

- Jean-Claude Falmagne, "A Representation Theorem for Finite Random Scale
  Systems", *Journal of Mathematical Psychology* 18(1), 1978, pp. 52-72,
  <https://doi.org/10.1016/0022-2496(78)90048-2>.

Recent work also studies partial observability *within* offered menus:

- Haruki Kono, Kota Saito, and Alec Sandroni, "Random Utility with
  Unobservable Alternatives", *American Economic Review*, forthcoming,
  <https://doi.org/10.1257/aer.20240712>.

That is adjacent but distinct from leaving entire menus unqueried.

## Residual question

This package does not re-prove ARSP as a new result. It asks a stronger
identification question:

```text
Across all complete positive kernels agreeing with the observed menus,
which latent-object tiers remain possible?
```

Existence of one RUM completion does not imply that the unobserved response
law is certified as RUM. The exact distinction is:

- existential model compatibility;
- versus identification of the full-kernel object class.

## Claim boundary

No novelty is claimed for convex-hull rationalizability, Luce ratio-scale
recovery, regularity, or random-utility extension. The contribution is an
exact finite access ledger and an elementary completion-ambiguity theorem for
the ASMP-9 object hierarchy.

The package does not address noisy estimates, menu endogeneity, unobservable
alternatives within a menu, dynamic or strategic choice, human/model evidence,
moral value, or ASMP-9 resolution.

