# ASMP-9 bounded context-degree prior-art gate v0.57

## Verdict

**The contextual log-odds expansion and its truncation hierarchy are
classical.** No novelty may be claimed for the model class, Mobius
decomposition, or the idea that low-order context effects can be estimated
from choice data.

The candidate residual contribution is narrower:

1. state the maximum-menu-size access threshold for exact full-kernel recovery
   inside the bounded log-odds-degree class;
2. make the recovery map explicit by Boolean Mobius inversion; and
3. give a fixed-universe sharp witness showing that one lower menu order cannot
   distinguish a Luce kernel from a regularity-violating non-RUM kernel.

Novelty of that residual theorem is not established. An exact prior theorem
would subsume it.

## Direct classical anchors

Richard R. Batsell and John C. Polking introduce a hierarchy of market-share
models based on additive expansions of log choice-probability ratios.

- Richard R. Batsell and John C. Polking, "A New Class of Market Share
  Models", *Marketing Science* 4(3), 1985, pp. 177-198.
  <https://doi.org/10.1287/mksc.4.3.177>

The paper is the direct attribution anchor for the pairwise log-odds object
used here.

Seshadri, Peysakhovich, and Ugander give a modern universal-logit Mobius
decomposition, define a nested order hierarchy, and prove identifiability and
finite-sample results for the second-order context-dependent random utility
model. They explicitly distinguish their contextual-utility expansion from
the Batsell-Polking log-ratio expansion and describe CDM as an alternative
parameterization of a third-order Batsell-Polking model.

- Arjun Seshadri, Alex Peysakhovich, and Johan Ugander, "Discovering Context
  Effects from Raw Choice Data", *Proceedings of Machine Learning Research*
  97, 2019, pp. 5660-5669.
  <https://proceedings.mlr.press/v97/seshadri19a.html>

Their Theorem 2 also shows that observing choices from only one set size is
insufficient to identify a CDM. The v0.57 nested domain contains every menu
size through a frozen maximum and therefore studies a different access
question.

Louviere's extended-logit work is another application of the
Batsell-Polking expansion and confirms that the hierarchy was developed to
relax Luce/IIA context independence.

- Jordan J. Louviere, "Effect of Choice Set Size on Choice Probabilities: An
  Extended Logit Model", *International Journal of Research in Marketing*
  6(1), 1989, pp. 1-11.
  <https://doi.org/10.1016/0167-8116(89)90043-8>

## Access and rationalizability anchors inherited from v0.56

Limited-domain RUM feasibility is classical McFadden-Richter/ARSP territory;
Turansick makes unobserved menu probabilities explicit extension variables.
Alos-Ferrer and Mihm characterize Luce choice and prediction on arbitrary menu
collections. Version v0.57 must not rebrand those existential tests as new.

- Christopher Turansick, "An Alternative Approach for Nonparametric Analysis
  of Random Utility Models", *Journal of Economic Theory* 226, 2025, 105998.
  <https://doi.org/10.1016/j.jet.2025.105998>
- Carlos Alos-Ferrer and Maximilian Mihm, "A Characterization of the Luce
  Choice Rule for an Arbitrary Collection of Menus", accepted version, 2024.
  <https://eprints.lancs.ac.uk/226172/1/LogitCharacterizationJET.pdf>

## Differentiation

The development theorem does not claim a new contextual-choice representation.
It uses the classical bounded-order log-odds hierarchy as a declared completion
class and asks an ASMP-9 access question:

```text
How large must queried menus be before every unqueried response, and hence the
full-kernel tier, is forced?
```

The proposed answer is `r+2` for full-kernel recovery in degree `r`, with a
Luce-versus-non-RUM ambiguity witness below that threshold for every `r>=1`.

## Claim boundary

Even if the proof survives review, the result is an exact finite
positive-kernel theorem under a prospectively declared structural model. It
does not establish that human or model preferences have bounded context
degree, select `r` from data, provide minimax sample rates, handle zeros or
ties, justify welfare comparisons, or resolve ASMP-9.
