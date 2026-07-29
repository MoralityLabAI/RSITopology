# ASMP-9 v0.25 prior-art gate

Status: development-only.  This gate must close before registration.

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

Subject to further searching, the candidate-new lemma is the strict
within-path smoothing statement for this exact partial-orientation law.
The reduced path-total enumeration is then immediate.  Even if the lemma has
an exact prior-art match, the ASMP access translation remains useful but must
be attributed as a corollary.

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

## Searches required before freeze

Search primary reliability and operations-research sources for:

- optimal replication counts on parallel collections of series paths;
- Schur-concavity under identical active redundancies;
- generalized-theta or bridge-network allocation;
- pseudopolynomial series-parallel reliability allocation; and
- exact resource allocation for multi-state oriented networks.

Record an explicit disposition for every close match.
