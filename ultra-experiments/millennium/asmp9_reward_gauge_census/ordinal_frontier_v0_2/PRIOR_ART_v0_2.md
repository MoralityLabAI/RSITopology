# ASMP-9 ordinal access frontier: prior-art boundary

## Placement

This experiment is a finite specialization of known mathematics, not a claim
that preference learning, one-bit recovery, or reward-gauge identifiability is
new.

- Ng, Harada, and Russell (1999), *Policy Invariance Under Reward
  Transformations*, establishes potential-based shaping and positive affine
  reward transformations as policy-invariant transformations in the relevant
  settings.
- Skalse et al. (2022), *Invariance in Policy Optimisation and Partial
  Identifiability in Reward Learning*, systematically characterizes
  invariances induced by several reward-learning data sources.
- Skalse and Abate (2024), *Partial Identifiability and Misspecification in
  Inverse Reinforcement Learning*, treats partial identifiability and
  behavioral-model misspecification directly.
- Plan and Vershynin (2013), *One-Bit Compressed Sensing by Linear
  Programming*, studies recovery from signs of linear measurements through
  hyperplane tessellations.
- Preference-based reinforcement-learning and reward-learning work studies
  sample-efficient recovery from pairwise trajectory comparisons under
  declared response models. The present experiment does not improve those
  sample-complexity results.

Primary links:

- <https://www.cs.utexas.edu/~shivaram/readings/b2hd-NgHR1999.html>
- <https://arxiv.org/abs/2203.07475>
- <https://arxiv.org/abs/2411.15951>
- <https://arxiv.org/abs/1109.4299>
- <https://proceedings.iclr.cc/paper_files/paper/2024/hash/1a10956f2cd9b41c0283a7af34b9c728-Abstract-Conference.html>

## Residual contribution

Version 0.1 reduced exact loop-return access to a cycle-space coordinate and
verified the classical `beta_1` query threshold. Version 0.2 asks a narrower
access-design question on a frozen finite registry:

> Given only signs of integer linear comparisons, what coefficient width and
> how many nonadaptive comparisons are required to separate every registered
> reward ray modulo positive scale, and how does that frontier change under a
> bounded adversarial response-threshold perturbation?

The answer is a finite hyperplane-arrangement and set-cover census. Its useful
outputs are:

1. an explicit separation or collision witness for every reward-ray pair;
2. a solver-certified minimum comparison family whenever the registered query
   grammar is complete; and
3. an exact distinction between lack of query count and lack of query
   expressivity.

The finite counts and the ASMP access interpretation may be useful. The general
geometry is classical.

## Deliberate omissions

- No policy or demonstration is observed; the experiment starts after v0.1 has
  reduced potential shaping to cycle coordinates.
- No claim is made about human consistency, Bradley-Terry correctness, active
  preference learning, or finite-sample estimation.
- The additive perturbation is an adversarial threshold model, not a model of
  human psychology.
- Positive scale is quotiented. Translation and potential shaping have already
  vanished in loop coordinates. Discounted shaping is not represented.
- A SciPy/HiGHS optimum with zero reported MIP gap is called
  `solver_certified`, not an independently checkable formal proof of
  optimality.

