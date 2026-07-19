# Prior-art and novelty audit for interaction-order tomography

## Status and purpose

This is a non-normative insertion beside the sealed v0.1 theorem and result.
It does not alter the registered experiment, its gates, or its outcome. Its
purpose is to separate classical ingredients, application-specific
consolidation, and the one lemma for which this audit did not find a direct
published antecedent.

The conservative external description is:

> The v0.1 result consolidates classical Boolean Fourier, factorial-design,
> and Mobius-inversion facts into a preregistered intervention-order
> instrument. Its candidate-new mathematical component is the exact
> labelled-versus-signed-parent-gauge identifiability split. That component is
> an elementary finite lemma, not evidence that ASMP-1 is resolved.

This is a positioning statement, not a claim of exhaustive literature search.

## Claim-by-claim assessment

### 1. Order-`r` interventions recover degree-at-most-`r` Walsh coordinates

**Prior-art status: classical corollary.**

The identity

```text
E[f(X) | X_S=a] = sum_(T subseteq S) f_hat(T) chi_T(a)
```

is the standard restriction/projection calculation for the Fourier expansion
of a function on the Boolean cube. Fourier inversion on each restricted cube
then recovers exactly the coefficients supported inside `S`. Consequently,
the degree threshold and the invisibility of higher-order parity are direct
finite corollaries, not new Boolean-analysis theorems.

The same phenomenon is adjacent to classical design-of-experiments language.
Orthogonal-array strength and fractional-factorial resolution describe which
interaction orders are estimable or aliased. The present intervention design
is not asserted to be identical to every classical fractional-factorial
design, but its order/aliasing interpretation belongs to that established
tradition.

Combinatorial interventions have also already been represented as Boolean
Fourier functions in causal inference. Synthetic Combinations models potential
outcomes over intervention combinations using a sparse Fourier expansion.

**What remains useful here:** the registered resource is maximum intervention
order rather than only query count, and the failure is expressed as an exact
kernel. Repeating singleton probes cannot recover a coefficient that lies in
that kernel. `interaction-order blindness` is therefore useful instrument
language, but not a claim that Boolean restriction theory is new.

### 2. Labelled threshold `n` versus signed-parent-gauge threshold `n-1`

**Prior-art status: candidate-new elementary lemma; novelty not established.**

The exact gauge is

```text
B_n = Sym(n) semidirect (Z/2)^n,
```

acting by input permutation and input negation. Output complementation is not
gauge. The bounded proof shows that the only labelled collision at order
`n-1` is top parity versus negative top parity and that one input flip joins
that pair, while distinct parity degrees obstruct every lower order.

This audit did not locate a source stating the resulting uniform
identifiability threshold modulo this gauge. The proof is short enough that an
external reviewer may reasonably classify it as a lemma or exercise rather
than a standalone theorem. It should therefore be described as
`candidate-new`, never as established novelty.

The enumeration itself is classical. The registered orbit counts

```text
n=2: 6
n=3: 22
n=4: 402
```

match OEIS A000616 and Harrison's enumeration of NP-equivalence classes:
permuting and complementing inputs while holding the output label fixed. An
independent Burnside calculation also reproduces `6/22/402` by averaging
`2^(number of vertex cycles)` over the hyperoctahedral action. The census is an
implementation cross-check, not a novel count.

The open mathematical direction suggested by this lemma is whether an exact
one-order gain survives other registered quotients, including feature
permutations combined with richer basis-change groups. No such generalization
is claimed here.

### 3. Rank, minimum-cost zeta basis, and conditioning comparison

**Prior-art status: classical ingredients and a specialized consolidation.**

The rank

```text
D(n,r) = sum_(j=0)^r binomial(n,j)
```

is the dimension of the degree-at-most-`r` multilinear subspace. The
all-positive subset design is the Boolean-lattice zeta matrix, and its inverse
is Mobius inversion. The representation of order-limited interactions through
vanishing higher-order Mobius coefficients is also the established language of
`k`-additive capacities and pseudo-Boolean functions.

The proof's filtration argument packages these ingredients under the chosen
structural cost `|S|`. This audit does not claim a published source for that
exact cost objective, but neither the rank formula nor the invertible zeta
basis should be presented as novel. Likewise, the poor conditioning of a
saturated non-orthogonal basis relative to a redundant orthogonal design is a
classical estimability-versus-stability distinction. The reported numerical
condition numbers are diagnostics for this implementation.

Recent interaction-recovery work is especially important adjacent art.
Kang et al. recover sparse Mobius coefficients in sublinear-query regimes and
give a noise-robust low-order group-testing construction. SPEX applies sparse
Fourier/channel-decoding machinery to feature-interaction explanations for
large language models. Those papers address stronger noisy and query-efficient
regimes than v0.1. The defensible distinction is access model:

- their principal resource is the number and coding of function queries under
  sparsity assumptions;
- v0.1 budgets the maximum order of a perfect intervention and characterizes
  the resulting exact measurement kernel; and
- v0.1 additionally asks what changes after quotienting a registered parent
  symmetry.

That difference should be stated explicitly; it does not imply superiority.

## External claim boundary

The durable contributions currently supported are:

1. a preregistered, executable consolidation that turns interaction order into
   an intervention-design audit;
2. the exact-kernel diagnosis called `interaction-order blindness`;
3. a cost/conditioning comparison that prevents exact identifiability from
   being mistaken for stable estimation; and
4. the candidate-new signed-parent-gauge threshold lemma.

The work does **not** establish novelty for the classical Fourier, rank,
Mobius, orthogonal-array, or factorial-resolution facts. It does not improve
the sparse/noisy query complexities of the cited methods. It does not show that
transformer mechanisms obey a Boolean local model. The completed Qwen
experiment is a falsification attempt of that approximation, not validation of
the finite theorem's relevance to arbitrary neural mechanisms.

## References

- Ryan O'Donnell, *Analysis of Boolean Functions*, especially Chapters 1 and
  3 on the Fourier expansion and restrictions:
  <https://www.cs.cmu.edu/~odonnell/papers/Analysis-of-Boolean-Functions-by-Ryan-ODonnell.pdf>
- C. R. Rao, "Factorial Experiments Derivable from Combinatorial Arrangements
  of Arrays," *Journal of the Royal Statistical Society, Supplement* 9(1),
  1947, 128-139. DOI: <https://doi.org/10.2307/2983576>
- G. E. P. Box and J. S. Hunter, "The 2^(k-p) Fractional Factorial Designs,
  Part I," *Technometrics* 3(3), 1961, 311-351.
  DOI: <https://doi.org/10.1080/00401706.1961.10489951>
- Gian-Carlo Rota, "On the Foundations of Combinatorial Theory I: Theory of
  Mobius Functions," *Zeitschrift fur Wahrscheinlichkeitstheorie und
  Verwandte Gebiete* 2, 1964, 340-368.
  DOI: <https://doi.org/10.1007/BF00531932>
- Michel Grabisch, Jean-Luc Marichal, and Marc Roubens, "Equivalent
  Representations of Set Functions," *Mathematics of Operations Research*
  25(2), 2000, 157-178. DOI: <https://doi.org/10.1287/moor.25.2.157.12225>
- Pedro Miranda, Michel Grabisch, and Pedro Gil, "Axiomatic Structure of
  k-Additive Capacities," *Mathematical Social Sciences* 49(2), 2005,
  153-178. DOI: <https://doi.org/10.1016/j.mathsocsci.2004.06.001>
- Abhineet Agarwal, Anish Agarwal, and Suhas Vijaykumar, "Synthetic
  Combinations: A Causal Inference Framework for Combinatorial Interventions,"
  2023: <https://arxiv.org/abs/2303.14226>
- Justin S. Kang, Yigit E. Erginbas, Landon Butler, Ramtin Pedarsani, and
  Kannan Ramchandran, "Learning to Understand: Identifying Interactions via the
  Mobius Transform," NeurIPS 2024: <https://arxiv.org/abs/2402.02631>
- Justin Singh Kang et al., "SPEX: Scaling Feature Interaction Explanations for
  LLMs," 2025: <https://arxiv.org/abs/2502.13870>
- Michael A. Harrison, "The Number of Transitivity Sets of Boolean Functions,"
  *Journal of the Society for Industrial and Applied Mathematics* 11(3), 1963,
  806-828: <https://www.jstor.org/stable/2946322>
- OEIS A000616, NP-equivalence orbit counts for Boolean functions under input
  permutation and negation: <https://oeis.org/A000616>

## Audit notes

- Literature checked: 2026-07-19.
- The author list for *Synthetic Combinations* is Abhineet Agarwal, Anish
  Agarwal, and Suhas Vijaykumar; it is not an Agarwal/Squires paper.
- `6/22/402` is now treated as a cited classical cross-check.
- No direct antecedent was found for the exact quotient-threshold lemma during
  this bounded search. Absence from this search is not proof of novelty.
