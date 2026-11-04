# ASMP-9 v0.44 prior-art gate

## Disposition

Every general ingredient in v0.44 is classical:

- Blackwell/Le Cam/Torgersen comparison of statistical experiments;
- the KL chain rule and Pinsker inequality;
- finite-horizon dynamic programming;
- occupancy measures;
- robust optimization under coordinate-wise uncertainty; and
- rectangular robust Markov decision processes.

The repository-specific contribution is an exact composition inside the
ASMP-9 risk-polytope compiler. No novelty is claimed for the ingredients.

## Primary and load-bearing sources

1. David Blackwell, “Comparison of Experiments,” *Proceedings of the Second
   Berkeley Symposium on Mathematical Statistics and Probability* (1951),
   pp. 93-102,
   <https://digicoll.lib.berkeley.edu/record/112749>.
2. Erik Torgersen, *Comparison of Statistical Experiments* (Cambridge
   University Press, 1991), especially the deficiency chapter,
   <https://doi.org/10.1017/CBO9780511666353.007>.
3. Michael Kearns and Satinder Singh, “Near-Optimal Reinforcement Learning in
   Polynomial Time,” *Machine Learning* 49 (2002), 209-232,
   <https://www.cis.upenn.edu/~mkearns/papers/KearnsSinghE3.pdf>.
4. Garud N. Iyengar, “Robust Dynamic Programming,” *Mathematics of Operations
   Research* 30(2), 257-280 (2005),
   <https://doi.org/10.1287/moor.1040.0129>.
5. Arnab Nilim and Laurent El Ghaoui, “Robust Control of Markov Decision
   Processes with Uncertain Transition Matrices,” *Operations Research*
   53(5), 780-798 (2005),
   <https://people.eecs.berkeley.edu/~elghaoui/Pubs/RobMDP_OR2005.pdf>.

Iyengar and Nilim-El Ghaoui already establish robust dynamic programming for
rectangular uncertainty. Version v0.44 does not claim that uncertainty-aware
policy evaluation or robust Bellman recursion is new.

## Subsumption and surviving role

The following tempting statement is vacuous in the repeatable-query grammar:

```text
sup_pi E_pi sum_t kappa(theta,q_t)
  = h max_q kappa(theta,q).
```

The equality holds because the policy can repeat the maximally uncertain query
at every step. Calling that scalar an “occupancy-aware” improvement would
merely rename the v0.43 worst-cell bound.

The surviving object keeps the information load attached to each risk
generator:

```text
policy pi
  -> center risk vector r_pi
  -> information occupancy I_pi
  -> generator-specific risk radius b_pi.
```

Robust deficiency is then compiled over these generator-specific boxes. A
decision problem may use a low-information policy even though unrelated
admissible policies visit high-uncertainty cells. This is the
decision-relative composition specific to the ASMP-9 ledger.

## Frozen novelty sentence

> ASMP-9 v0.44 augments each finite adaptive risk-polytope generator with its
> policy-specific information occupancy and proves an exact robust-containment
> interval from the resulting generator-wise boxes, retaining
> decision-relative uncertainty that is erased by a pre-optimization
> worst-policy supremum.

This is an instrument theorem and exact implementation specialization, not a
new robust-MDP or comparison-of-experiments theorem.
