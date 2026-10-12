# ASMP-9 v0.42 prior-art gate

## Verdict

`classical_multinomial_concentration_and_simulation_bound_specialization`

No concentration inequality, simulation lemma, or robust-control theorem is
presented as novel.

## Primary anchors

1. Tsachy Weissman, Erik Ordentlich, Gadiel Seroussi, Sergio Verdu, and
   Marcelo J. Weinberger, "Inequalities for the L1 Deviation of the Empirical
   Distribution," HP Laboratories technical report HPL-2003-97R1, 2003.
   <https://shiftleft.com/mirrors/www.hpl.hp.com/techreports/2003/HPL-2003-97R1.pdf>
2. Michael Kearns and Satinder Singh, "Near-Optimal Reinforcement Learning in
   Polynomial Time," *Machine Learning* 49(2-3), 2002, pp. 209-232.
   <https://doi.org/10.1023/A:1017984413808>
3. David Blackwell, "Equivalent Comparisons of Experiments," *The Annals of
   Mathematical Statistics* 24(2), 1953.
   <https://doi.org/10.1214/aoms/1177729032>
4. Erik Torgersen, *Comparison of Statistical Experiments*, Chapter 6,
   "Deficiencies," 1991.
   <https://doi.org/10.1017/CBO9780511666353.007>
5. Matthew L. Malloy, Ardhendu S. Tripathy, and Robert D. Nowak, "Optimal
   Confidence Sets for the Multinomial Parameter," IEEE International
   Symposium on Information Theory, 2021.
   <https://doi.org/10.1109/ISIT45174.2021.9517964>

## Attribution boundary

- The L1/TV empirical-distribution bound is Weissman et al.
- Policy-uniform finite-horizon model perturbation is a simulation-lemma
  argument.
- Directed upper-risk-set comparison is classical Blackwell/Le Cam/Torgersen.
- The candidate contribution is the explicit composition of these ingredients
  into a confidence-valid ASMP-9 adaptive-access certificate with a total
  three-state gate.

The Weissman/Bonferroni interval is conservative and is not claimed optimal.
