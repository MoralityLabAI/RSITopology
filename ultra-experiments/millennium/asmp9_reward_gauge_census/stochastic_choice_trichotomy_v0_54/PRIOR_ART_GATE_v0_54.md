# ASMP-9 stochastic-choice prior-art gate v0.54

## Verdict

**The mathematical representation results are classical. Novelty is not
claimed.**

This package combines two established nested models into an exact ASMP-9
well-posedness instrument.

## Scalar tier

Luce's choice axiom characterizes positive stochastic choice rules admitting
a positive ratio scale

```text
p(x | S) = v(x) / sum_{y in S} v(y).
```

The scale is unique up to multiplication by a positive constant; equivalently
`log v` is unique up to an additive constant. The package calls this the
`scalar_luce` tier.

Primary source:

- R. Duncan Luce, *Individual Choice Behavior: A Theoretical Analysis*,
  Wiley, 1959, especially the ratio-scale representation theorem.

Author retrospective:

- R. Duncan Luce, "Luce's choice axiom", Scholarpedia 3(12):8077, 2008,
  <https://doi.org/10.4249/scholarpedia.8077>.

## Random-utility tier

Block and Marschak introduced random orderings and the alternating
choice-probability quantities now called Block-Marschak polynomials. Falmagne
proved that, for a complete finite choice system, nonnegativity of these
polynomials is necessary and sufficient for representation by a probability
distribution over strict rankings. McFadden and Richter later formulated the
finite stochastic-rationality problem through revealed stochastic preference.

Primary sources:

- H. D. Block and Jacob Marschak, "Random Orderings and Stochastic Theories of
  Responses", in *Contributions to Probability and Statistics*, Stanford
  University Press, 1960, pp. 97-132.
- Jean-Claude Falmagne, "A Representation Theorem for Finite Random Scale
  Systems", *Journal of Mathematical Psychology* 18(1), 1978, pp. 52-72,
  <https://doi.org/10.1016/0022-2496(78)90048-2>.
- Daniel McFadden and Marcel K. Richter, "Stochastic Rationality and Revealed
  Stochastic Preference", in *Preferences, Uncertainty, and Optimality*, 1990,
  pp. 161-186.
- Daniel McFadden, "Revealed Stochastic Preference: A Synthesis", 2004,
  <https://eml.berkeley.edu/wp/mcfadden0204/stochastic.pdf>.

## Exact claim boundary

The package does **not** claim:

- a new Luce, Block-Marschak, Falmagne, or McFadden-Richter theorem;
- identification from incomplete menus in general universes;
- finite-sample testing or minimax sample complexity;
- a model of human inconsistency;
- recovery of morally correct or welfare-relevant value;
- general MDP reward identification; or
- resolution of ASMP-9.

The contribution is a finite, auditable classification grammar that makes the
ASMP-9 "scalar / weaker object / no coherent object" distinction executable.
The binary-menu insufficiency witness is elementary and is not claimed as a
new revealed-preference result.

