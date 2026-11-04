# Prior-art gate for ASMP-9 v0.31

Status: development-only. No novelty claim.

## Direct mathematical ancestors

1. Frisch, R. and Waugh, F. V. (1933), *Partial Time Regressions as Compared
   with Individual Trends*, Econometrica 1(4), 387-401.
   DOI: https://doi.org/10.2307/1907330

   The projection that removes the declared context nuisance is the
   Frisch-Waugh residualization identity in finite linear algebra.

2. El Ghaoui, L. and Lebret, H. (1997), *Robust Solutions to Least-Squares
   Problems with Uncertain Data*, SIAM Journal on Matrix Analysis and
   Applications 18(4), 1035-1064.
   DOI: https://doi.org/10.1137/S0895479896298130

   Matrix uncertainty, robust residuals, and conic formulations of uncertain
   least squares are established. The v0.31 contraction envelope is a simple
   bounded-error specialization, not a new robust-LS framework.

3. Milanese, M. and Vicino, A. (1991), *Optimal Estimation Theory for Dynamic
   Systems with Set Membership Uncertainty: An Overview*, Automatica 27(6),
   997-1009. DOI: https://doi.org/10.1016/0005-1098(91)90134-N

   Bai, E.-W., Cho, H., and Tempo, R. (1998), *Convergence
   Properties of the Membership Set*, Automatica 34(10), 1245-1249.
   DOI: https://doi.org/10.1016/S0005-1098(98)00065-X

   Returning a feasible parameter set under bounded errors is classical
   set-membership estimation.

4. Boyd, S. and Vandenberghe, L. (2004), *Convex Optimization*, sections on
   support functions, linear images, and robust optimization.
   https://web.stanford.edu/~boyd/cvxbook/

   The support-function and Minkowski-sum calculus is standard convex
   analysis.

## Reinforcement-learning ancestors

5. Abbeel, P. and Ng, A. Y. (2004), *Apprenticeship Learning via Inverse
   Reinforcement Learning*, ICML.
   DOI: https://doi.org/10.1145/1015330.1015430

   Linear reward performance controlled by feature-expectation differences
   is established.

6. Iyengar, G. N. (2005), *Robust Dynamic Programming*, Mathematics of
   Operations Research 30(2), 257-280.
   DOI: https://doi.org/10.1287/moor.1040.0129

7. Nilim, A. and El Ghaoui, L. (2005), *Robust Control of Markov Decision
   Processes with Uncertain Transition Matrices*, Operations Research 53(5),
   780-798.

   Robust MDPs under transition uncertainty are established. Version v0.31
   does not solve a robust MDP; it certifies one finite policy family after
   uncertainty has been translated into occupancy-row bounds.

## Internal predecessors

- v0.27: context-only midpoint nuisance and its liveness/spectral boundary;
- v0.28: calibrated occupancy quotient recovery;
- v0.29: quotient error to policy regret;
- v0.30: mechanical-versus-semantic consequence certification and the sharp
  factor-two semantic residual.

## Exact residual contribution

Version v0.31 is an ASMP access ledger and executable composition theorem. Its
specific contribution is to prevent four separately valid certificates from
being combined by an unjustified scalar error sum:

- exact context nuisance is projected out;
- semantic-cell reuse is retained through an incidence map;
- multiplicative mechanical drift receives a liveness gate;
- the resulting set, not only its radius, is propagated to policy margins.

No component is claimed novel. The result is not a general IRL, robust-MDP,
or measurement-theory theorem.
