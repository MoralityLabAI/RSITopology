# ASMP-9 v0.51 prior-art gate

## Verdict

**The central randomized-minmax construction is directly subsumed. Proceed
only as an application-specific finite specialization and audit instrument.**

## Directly load-bearing prior art

Mastin, Jaillet, and Chin already formulate randomized minmax regret for
combinatorial optimization as a zero-sum game in which the optimizer chooses
a distribution over feasible solutions and the adversary chooses the cost
scenario after seeing that distribution but before its realization:

- A. Mastin, P. Jaillet, and S. Chin, "Randomized Minmax Regret for
  Combinatorial Optimization Under Uncertainty," in *Algorithms and
  Computation (ISAAC 2015)*, 491-501. DOI:
  [10.1007/978-3-662-48971-0_42](https://doi.org/10.1007/978-3-662-48971-0_42).

They prove substantially stronger algorithmic results than v0.51 proposes,
including polynomial solvability of randomized minmax regret when the base
combinatorial problem is polynomially solvable under discrete and interval
scenario models.

Therefore the following are not novel:

- mixing feasible orderings;
- the primal/dual zero-sum game;
- strict benefit from randomization;
- integrality-gap language; or
- scenario-based randomized regret optimization.

## Classical game duality

Equality of the finite primal and dual values is von Neumann minimax/linear
programming duality. Complementary slackness and least-favorable scenario
mixtures are standard.

No theorem in v0.51 should be framed as a new minimax or statistical-decision
result.

## Buehler specialization

The residual contribution is the specialization:

1. rows are complete direct-Buehler evidence orderings;
2. columns are decision-objective/reference-law scenarios;
3. payoff is excess expected certificate cost;
4. zero regret is tied exactly to the v0.49-v0.50 common-chain certificate;
   and
5. the result is emitted as a hash-bound ASMP-9 instrument with explicit
   separation between exact certification and approximate compromise.

The zero-regret support theorem is an elementary nonnegativity corollary. The
two-by-two witness is a smallest control, not a novelty-bearing theorem.

## Durable contribution

The useful result is not "randomization helps." It is:

> Randomization may lower worst-case certificate regret, but cannot repair a
> missing common semantic/evidence identity; zero regret still requires
> support entirely inside the deterministic common-optimum intersection.

That statement closes the randomized-procedure seam in the finite ASMP-9
grammar without confusing minimax compromise with identifiability.

## Claim boundary

Any circulation must cite Mastin, Jaillet, and Chin prominently. Version
v0.51 cannot support a general novelty claim, a large-width efficiency claim,
or an inference from randomized finite evidence ordering to real preference
access.
