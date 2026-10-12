# ASMP-9 v0.46 prior-art gate

## Gate conclusion

Rectangularity, nonrectangular parameter coupling, experiment comparison,
garbling, minimax decision rules, likelihood regions, and exact finite
optimization are established mathematics. Version v0.46 claims no novelty for
those ingredients.

The surviving package contribution is a narrow specialization: compute the
exact shared-channel image of the v0.45 confidence region, propagate it
through a complete horizon-two adaptive policy class, and compare its
decision-relative integer allocation with the inherited independent-generator
rectangle. This is an instrument theorem and exact finite census.

## Primary anchors

1. D. Blackwell, “Equivalent Comparisons of Experiments,” *Annals of
   Mathematical Statistics* 24(2), 265–272 (1953),
   <https://doi.org/10.1214/aoms/1177729032>. Blackwell comparison supplies
   the garbling order used to move the coupled supremum to the largest
   symmetric-flip rates.
2. G. N. Iyengar, “Robust Dynamic Programming,” *Mathematics of Operations
   Research* 30(2), 257–280 (2005),
   <https://doi.org/10.1287/moor.1040.0129>. Iyengar states the
   rectangularity condition under which robust dynamic-programming
   counterparts retain the classical structure.
3. A. Nilim and L. El Ghaoui, “Robust Control of Markov Decision Processes
   with Uncertain Transition Matrices,” *Operations Research* 53(5), 780–798
   (2005), <https://doi.org/10.1287/opre.1050.0216>. This is a primary robust
   control and likelihood/entropy uncertainty-set anchor.
4. W. Wiesemann, D. Kuhn, and B. Rustem, “Robust Markov Decision Processes,”
   *Mathematics of Operations Research* 38(1), 153–183 (2013). The paper
   constructs statistically motivated confidence regions and robust
   policies; v0.46 is not a general robust-MDP algorithm.
5. V. Goyal and J. Grand-Clément, “Robust Markov Decision Processes: Beyond
   Rectangularity,” *Mathematics of Operations Research* 48(1), 203–226
   (2023), <https://doi.org/10.1287/moor.2022.1259>. Their factor model
   explicitly couples transitions and addresses conservatism from uncoupled
   uncertainty. The general insight that coupling can reduce conservatism is
   therefore prior art.
6. I. Csiszár, “The Method of Types,” *IEEE Transactions on Information
   Theory* 44(6), 2505–2523 (1998). Version v0.46 inherits v0.45’s
   simultaneous finite-type likelihood toll; it does not claim a new
   confidence theorem.

## Specific differentiation

The registered object is not a general MDP transition kernel. It is the
finite adaptive risk experiment already built in ASMP-9 v0.41–v0.45:

- four latent targets;
- three binary shared-parameter queries;
- two adaptive query steps;
- two distinct decision losses; and
- an integer calibration allocation.

The experiment asks whether replacing a policy-risk rectangle by the exact
shared-channel image changes either the robust endpoint or the selected
integer acquisition design. The answer is determined prospectively at a
disjoint budget, rather than inferred from the burned v0.45 run.

## Inherited rather than novel

- finite minimax and LP duality;
- Blackwell comparison and data processing;
- binary symmetric-channel ordering;
- method-of-types likelihood regions;
- robust optimization under coupled uncertainty;
- exact rational arithmetic; and
- exhaustive finite integer design.

## Claim boundary

The result may characterize one exact coupled confidence image and quantify
the conservatism of one rectangular relaxation. It cannot establish a general
nonrectangular robust-control theorem, efficient policy search, optimal
confidence constants, strategic robustness, real preference-query validity,
or resolution of ASMP-9.

