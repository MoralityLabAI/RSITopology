# Prior-art gate for ASMP-9 v0.33 development

## Status

This is a pre-registration literature boundary. Version v0.33 is not frozen
and has not been run.

The max-min information design and fixed-confidence lower bound proposed here
are established controlled-sensing and pure-exploration mathematics. No
novelty claim may attach to the characteristic-time formula, change-of-measure
argument, tracking allocation, or asymptotic achievability.

## Primary anchors

- Chernoff (1959), *Sequential Design of Experiments*, introduced adaptive
  experiment choice for sequential hypothesis testing.
- Nitinawarat, Atia, and Veeravalli (2013), *Controlled Sensing for
  Multihypothesis Testing*, analyzed fixed-sample and sequential controlled
  tests and first-order asymptotic optimality:
  <https://arxiv.org/abs/1205.0858>.
- Kaufmann, Cappé, and Garivier (2016), *On the Complexity of Best-Arm
  Identification in Multi-Armed Bandit Models*, gave general
  change-of-measure lower bounds:
  <https://jmlr.org/papers/v17/kaufman16a.html>.
- Garivier and Kaufmann (2016), *Optimal Best Arm Identification with Fixed
  Confidence*, characterized the one-parameter fixed-confidence complexity
  and proved Track-and-Stop asymptotically optimal:
  <https://proceedings.mlr.press/v49/garivier16a.html>.
- Degenne and Koolen (2019), *Pure Exploration with Multiple Correct
  Answers*, extended the characteristic-time game to answer sets:
  <https://arxiv.org/abs/1902.03475>.
- Jourdan, Mutný, Kirschner, and Krause (2021), *Efficient Pure Exploration
  for Combinatorial Bandits with Semi-Bandit Feedback*, explicitly separates
  sampling actions from answer structure:
  <https://arxiv.org/abs/2101.08534>.
- Cao, Cohen, and Szpruch (2021), *Identifiability in Inverse Reinforcement
  Learning*, characterizes reward ambiguity and environment variation in
  important IRL settings:
  <https://arxiv.org/abs/2106.03498>.
- Chen et al. (2022), *Human-in-the-loop: Provably Efficient
  Preference-based Reinforcement Learning with General Function
  Approximation*, gives near-optimal linear-setting regret bounds for a
  broader preference-RL problem:
  <https://arxiv.org/abs/2205.11140>.
- Li et al. (2024), *Policy Evaluation for Reinforcement Learning from Human
  Feedback: A Sample Complexity Analysis*, studies the reward-learning plus
  off-policy-evaluation pipeline:
  <https://proceedings.mlr.press/v238/li24l.html>.

## Residual ASMP-9 contribution

The plausible contribution is not a new pure-exploration theorem. It is an
access ledger that:

1. treats reward-gauge aliases as same-answer hypotheses;
2. combines behavioral, mixture-audit, and environment-intervention queries
   in one controlled observation family;
3. makes policy identity or regret class, rather than exact reward
   reconstruction, the answer map;
4. exposes which query channel is necessary through zero characteristic
   information; and
5. links that stochastic information geometry to the deterministic
   v0.28-v0.32 quotient certificates.

Any v0.33 theorem must be labelled a finite specialization and composition of
the cited theory unless a genuinely new restriction or sharp bound survives a
separate novelty review.

## Coupling-quotient attribution

The new observation-to-semantic coupling result uses only the classical
vectorization identity:

```text
vec(A K B) = (transpose(B) kron A) vec(K)
```

and the classical rank identity:

```text
rank(A kron B) = rank(A) rank(B).
```

The arbitrary-linear-query threshold is the corresponding row-space
dimension argument. These are standard matrix-analysis facts, not novelty
claims. The ASMP-9 contribution is their exact specialization to the sealed
v0.31 analysis/policy matrices and v0.32 semantic operator, plus the resulting
decision-access ledger: 18 relevant coupling coordinates versus 30
decision-null coordinates.
