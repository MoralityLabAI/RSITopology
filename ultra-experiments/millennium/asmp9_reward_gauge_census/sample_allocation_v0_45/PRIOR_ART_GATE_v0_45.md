# ASMP-9 v0.45 prior-art gate

## Gate conclusion

The general ideas in this experiment are classical. Choosing experiments by
their decision relevance, allocating a finite sensing budget, controlling
multihypothesis error through information, and bounding empirical laws through
the method of types are not claimed as new.

The surviving contribution is a narrow finite specialization: attach a
simultaneous empirical KL toll to every query used by each generator of the
ASMP-9 adaptive upper-risk polytope, then exhaustively choose integer query
counts to minimize the inherited exact robust-deficiency endpoint. The
decision loss is changed while the channel library and total sample count are
held fixed. This is an instrument theorem and exact census, not a new theory
of optimal experimental design.

## Primary anchors

1. H. Chernoff, “Sequential Design of Experiments,” *Annals of Mathematical
   Statistics* 30(3), 755–770 (1959),
   <https://doi.org/10.1214/aoms/1177706205>. Chernoff establishes the
   classical decision-directed sequential-design setting.
2. S. Nitinawarat, G. K. Atia, and V. V. Veeravalli, “Controlled Sensing for
   Multihypothesis Testing,” *IEEE Transactions on Automatic Control* 58(10),
   2451–2464 (2013), <https://doi.org/10.1109/TAC.2013.2261188>. Controlled
   sensing can change multihypothesis testing performance, and causal sensing
   may outperform open-loop sensing.
3. M. Naghshvar and T. Javidi, “Active Sequential Hypothesis Testing,”
   <https://arxiv.org/abs/1203.4626>. The paper derives information-rate lower
   bounds and asymptotically optimal active policies. Version v0.45 is not an
   asymptotic-optimality claim.
4. I. Csiszár, “The Method of Types,” *IEEE Transactions on Information
   Theory* 44(6), 2505–2523 (1998). The registered bound

   ```text
   Pr[KL(P_hat || P) >= epsilon]
     <= (n+1) exp(-n epsilon)
   ```

   is the binary finite-type bound, unioned over three shared query
   parameters.
5. G. Elfving, “Optimum Allocation in Linear Regression Theory,” *Annals of
   Mathematical Statistics* 23, 255–262 (1952). This is a foundational
   optimal-allocation reference. The v0.45 criterion is not `c`-optimality:
   it minimizes a robust directed-deficiency endpoint over a finite adaptive
   risk polytope.

## What is inherited rather than novel

- KL chain rules and Pinsker’s inequality;
- simultaneous finite-alphabet confidence regions;
- allocation of observations to decision-relevant experiments;
- exact rational linear programming;
- Le Cam/two-point testing lower bounds; and
- exhaustive integer design over a finite registry.

## What is specific to this package

The package composes those ingredients with the exact v0.41 adaptive
risk-polytope compiler and the v0.44 generator-specific occupancy boxes.
The same three-query library is evaluated under two losses:

- four-way classification, which uses root and branch information; and
- root-group loss, whose optimal policy ignores both branch queries.

The matched serial control uses every query once and should recover uniform
allocation. The two-point certificate is included specifically to prevent the
constructive KL radius from being described as minimax.

## Access-model qualification

Each query has one shared symmetric flip parameter. Known-target calibration
draws from all four target/query cells can therefore be pooled into a query
error count. The full target-by-query design quotients to three totals
`n_root,n_left,n_right`; target labels are ancillary inside a query under this
registered parametric grammar. This pooling is not valid for arbitrary
target-dependent channel rows. Cell-specific and nonparametric allocation
remain open.

## Claim boundary

The result may establish an exact allocation optimum for one finite,
shared-parameter, iid calibration grammar. It cannot establish a general
optimal-design theorem, minimax sample complexity, efficient policy search,
strategic-source robustness, real preference-query validity, or resolution of
ASMP-9.
