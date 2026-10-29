# ASMP-9 finite-sample tier prior-art gate v0.58

## Verdict

**The statistical ingredients are classical.** Le Cam's two-point method,
Pinsker's inequality, multinomial concentration, Hoeffding bounds, and
likelihood-ratio oscillation bounds for total variation, and
distance-to-model-set classification are not candidate contributions.

The bounded contextual-choice hierarchy and its estimation literature also
predate this project. Version v0.58 can claim only an explicit ASMP-9
composition:

```text
bounded context degree
  + exact interpolation conditioning
  + Luce/RUM boundary geometry
  -> one finite-sample access ledger with a matching no-margin obstruction.
```

Novelty is not established.

## Statistical lower-bound anchors

Le Cam's two-point method is the direct basis of the no-uniform-classifier
argument. A standard modern reference comparing Le Cam, Assouad, and Fano
methods is:

- Bin Yu, "Assouad, Fano, and Le Cam", in *Festschrift for Lucien Le Cam*,
  1997, pp. 423-435.
  <https://doi.org/10.1007/978-1-4612-1880-7_29>

The v0.58 family makes the two points explicit inside the stochastic-choice
object; it does not contribute a new testing inequality.

## Concentration anchors

The registered development upper bound uses only coordinatewise Hoeffding plus
a union bound. Stronger multinomial `L1` inequalities are classical and could
improve constants:

- Tsachy Weissman, Erik Ordentlich, Gadiel Seroussi, Sergio Verdu, and Marcelo
  J. Weinberger, "Inequalities for the L1 Deviation of the Empirical
  Distribution", HP Laboratories Technical Report HPL-2003-97, 2003.
- Jay Mardia, Jiantao Jiao, Ervin Tanczos, Robert D. Nowak, and Tsachy
  Weissman, "Concentration Inequalities for the Empirical Distribution",
  2018. <https://arxiv.org/abs/1809.06522>

The proposed sample count is therefore a transparent sufficient bound, not a
minimax constant.

## Context-model and choice anchors

The v0.57 Batsell-Polking/Seshadri attribution carries forward. Seshadri,
Peysakhovich, and Ugander already give identifiability and finite-sample
analysis for CDM. Version v0.58 does not claim that sampling contextual-choice
models is new.

- Arjun Seshadri, Alex Peysakhovich, and Johan Ugander, "Discovering Context
  Effects from Raw Choice Data", PMLR 97, 2019.
  <https://proceedings.mlr.press/v97/seshadri19a.html>

Random-utility feasibility and the Luce identities remain the classical model
sets documented in the v0.54-v0.56 prior-art gates.

The computational-access note uses only standard real algebraic geometry:
finite-dimensional semialgebraic sets have semialgebraic closures, and their
first-order decision problems are decidable by quantifier elimination.

- Saugata Basu, Richard Pollack, and Marie-Francoise Roy, *Algorithms in Real
  Algebraic Geometry*, second edition, Springer, 2006.

## Residual claim boundary

The candidate residual is:

1. two exact positive-kernel paths witnessing both adjacent tier boundaries;
2. a proof that exact three-tier classification has no uniform finite sample
   bound, even with complete menu access;
3. a total, margin-promised classifier; and
4. an explicit sufficient sample count containing the exact v0.57
   interpolation norm; and
5. a matching `gamma^-2` necessary exponent on one three-alternative
   RUM/non-RUM slice.

It is not an optimal test, efficient distance algorithm, minimax-rate theorem,
empirical validation, or ASMP-9 resolution.
