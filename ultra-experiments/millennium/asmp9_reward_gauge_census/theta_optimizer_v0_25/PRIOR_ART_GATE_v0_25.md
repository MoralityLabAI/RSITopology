# ASMP-9 v0.25 prior-art gate

Status: primary-source audit completed 2026-07-28.  The result may be
registered only with the conservative attribution boundary below.

## Classical neighborhood

1. Reliability formulas and allocation algorithms for series-parallel and
   parallel-series systems are classical.  In particular, the literature
   includes pseudopolynomial dynamic programs, majorization/Schur-convex
   assignment rules, and nonlinear integer formulations.
2. Emad El-Neweihi, Frank Proschan, and Jayaram Sethuraman,
   ["Optimal allocation of components in parallel-series and series-parallel
   systems"](https://doi.org/10.2307/3214014), *Journal of Applied
   Probability* 23(3) (1986), 770-777, explicitly uses majorization and
   Schur-convexity to characterize or partially order allocations in
   ordinary binary reliability systems.  This is the closest structural
   prior-art hit located so far and requires full-text comparison before
   freeze.
3. V. Rajendra Prasad, K. P. K. Nair, and Y. P. Aneja,
   ["Optimal Assignment of Components to Parallel-Series and Series-Parallel
   Systems"](https://doi.org/10.1287/opre.39.3.407), *Operations Research*
   39(3) (1991), 407-414, is direct prior art for majorization-based component
   allocation in ordinary reliability systems.
4. Alice Yalaoui, Chengbin Chu, and Eric Châtelet,
   ["Reliability allocation problem in a series-parallel
   system"](https://doi.org/10.1016/j.ress.2004.10.007),
   *Reliability Engineering & System Safety* 90(1) (2005), 55-61, develops
   theoretical and computational allocation results for a different
   series-parallel reliability model.
5. Alice Yalaoui, Eric Châtelet, and Chengbin Chu,
   ["Series-parallel Systems Design: Reliability
   Allocation"](https://doi.org/10.3166/jds.14.473-487), *Journal of
   Decision Systems* 14(4) (2005), 473-487, gives a pseudopolynomial
   algorithm for a finite-choice component-reliability allocation problem.
6. F. Castro, J. Gago, I. Hartillo, J. Puerto, and J. M. Ucha,
   ["Exact cost minimization of a series-parallel
   system"](https://arxiv.org/abs/1203.3307), studies a different
   multiple-component-choice and reliability-constraint problem.
7. The v0.23 multivariate `q=-1` representation and the earlier single-cycle
   balancing theorem are predecessor results inside this repository.

## Primary-source dispositions

The closest sources were compared at the level of their optimized objects,
not merely their titles.

| Source | Object actually optimized | Disposition for v0.25 |
|---|---|---|
| El-Neweihi, Proschan, and Sethuraman (1986), journal paper and 1984 FSU report M690 | Assignment of a fixed list of heterogeneous binary components to disjoint minimum path or cut sets in ordinary parallel-series/series-parallel reliability. Theorem 2.1 assigns the most reliable components to the shortest paths; Theorem 3.1 gives a majorization partial order for cut-set assignments. | Supplies the classical majorization template. It does not allocate repeated microtrials to edges, use four directional edge states, optimize strong connectivity, or reduce a theta objective to path totals. |
| El-Neweihi, Proschan, and Sethuraman (1985), FSU report M699; later *Handbook of Statistics* chapter | Extension of the component-assignment result to stochastically ordered multistate component values in disjoint parallel-series path sets. | Multistate in the reliability sense, but still an assignment theorem for component state quality. It is not the ASMP partial-orientation law. |
| Boland, El-Neweihi, and Proschan (1988), FSU report M780 / PEIS paper | Placement of one or several active spare components in coherent systems, including `k`-out-of-`n`, parallel-series, and series-parallel modules, using redundancy importance and arrangement order. | Direct prior art for spare-placement and local redundancy decisions. It neither states the frozen fixed-total integer count problem nor the theta path-internal smoothing inequality. |
| Prasad, Nair, and Aneja (1991) | Assignment of heterogeneous components with position-dependent reliabilities; a complete rule for parallel-series and a special two-position series-parallel rule. | Same assignment neighborhood, different decision variables and success event. |
| Yalaoui, Châtelet, and Chu (2005), two papers | Cost-minimizing selection of component reliabilities from finite technology sets under an ordinary series-parallel reliability constraint; one paper gives a pseudopolynomial dynamic program. | Establishes that pseudopolynomial reliability-allocation algorithms are classical. It does not contain the frozen orientation formula or smoothing statement. |
| Castro et al. (2012) | Multiple-component-choice cost minimization under a reliability constraint. | Algorithmic neighbor only; different objective, variables, and system law. |

The archived M690, M699, and M780 scans were inspected directly.  The public
catalogue records and final journal metadata are linked above; the archive
copies were used only to read the primary text.

## Important distinction

Ordinary two-terminal reliability declares a path successful when every
component on it is up.  The frozen ASMP object instead asks whether a random
partial orientation of the entire theta block is strongly connected.  Each
path can be forward only, reverse only, bidirectional, or unusable.  The
formula

```text
product_j(2A_j-B_j) - 2 product_j(A_j-B_j)
```

is a translation for that four-state orientation event.  It must not be
presented as a new formula for standard binary component reliability.

## Proposed narrow contribution

The registered contribution is a specialized exact theorem for the frozen
ASMP access model: the four-state path formula, strict path-internal
smoothing, and the resulting path-total optimizer.  Majorization,
Schur-convex allocation, spare placement, and pseudopolynomial
series-parallel optimization are classical and must be cited as the
methodological neighborhood.

No novelty claim is registered.  The search found no exact statement of the
four-state directional smoothing lemma, but absence from this bounded search
does not establish novelty.  If an exact prior-art match is later found, the
result remains an attributed specialization/corollary.

## Allowed language

- exact global optimization is reduced from edge counts to path totals on
  generalized theta blocks;
- every optimizer balances counts within each path;
- fixed-path-count enumeration is polynomial in the numerical budget and
  pseudopolynomial for binary-encoded `N`;
- the class contains overlapping cycles when `k>=3`; and
- the result supplies a nontrivial tractable boundary next to v0.23.

## Forbidden language

- all series-parallel graphs are solved;
- the algorithm is polynomial in binary input length;
- all edges are globally balanced;
- arbitrary biconnected-block optimization is tractable;
- the reliability-allocation literature has no equivalent theorem; or
- ASMP-9 is resolved.

## Freeze decision

The gate is closed for a conservative prospective registration:

- the closest primary sources have explicit dispositions;
- the protocol must cite the classical allocation lineage;
- the structured claims must make no novelty assertion; and
- the result must remain restricted to the independent fair-microtrial
  generalized-theta class at `epsilon=1/2`.
