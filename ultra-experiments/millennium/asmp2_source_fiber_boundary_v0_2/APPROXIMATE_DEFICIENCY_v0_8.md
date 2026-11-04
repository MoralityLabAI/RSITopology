# Approximate source equivalence and infinite-class extension

## Two-world robust lower bound

Let two models have disjoint singleton good actions and source laws `Q_0,Q_1`.
For any randomized source-only decision rule, average success under the uniform
prior is at most the Bayes testing success

```text
(1 + TV(Q_0,Q_1))/2.
```

The worst-world success is no larger than the average. Therefore

```text
safety deficiency >= (1 - TV(Q_0,Q_1))/2.
```

For `n` samples, replace the laws by `Q_0^n,Q_1^n`. Standard Hellinger, KL, or
chi-square inequalities can upper-bound their total variation and produce
finite-sample impossibility bounds. At total variation zero this reduces to
the exact `1/2` obstruction in the smooth QMD witness.

The exact finite LP verifies this inequality over all registered binary law
pairs in `{1/8,1/4,1/2,3/4,7/8}`.

## Arbitrary registered experiments

For standard Borel model, observation, and action spaces, define safety
deficiency by taking the infimum over Markov kernels:

```text
D_G(E)
  = inf_K sup_m [1 - integral K(G_m|x) Q_m(dx)].
```

This remains an exact necessary-and-sufficient variational characterization
whether or not an optimal kernel exists. Under the usual compact-action,
closed-good-relation, continuity, and tightness hypotheses, standard minimax
and measurable-selection results provide optimizers. When those hypotheses
fail, the infimum still supplies the sharp attainable boundary, while lack of
attainment is itself a certificate obstruction.

The definition is invariant under:

- measurable isomorphisms of the observation experiment;
- bijective reparameterizations of the model;
- action relabelings preserving the good relation; and
- replacement by a Blackwell-equivalent experiment.

## Relation to local semiparametric theory

Along QMD local alternatives, Hellinger distance has the Fisher quadratic
expansion. The total-variation lower bound therefore connects approximate
source fibers to local testing. For smooth scalar constraints, the adjoint-score
range condition determines root-`n` regular estimability. For policy
certification, however, the good relation can change discontinuously when the
safety margin is zero. The local v0.5 counterexample isolates this missing
margin condition.

## Consequence

Exact source equality is not a fragile special case. Approximate
indistinguishability yields a quantitative certification lower bound, and the
same safety deficiency handles finite, infinite, exact, and approximate source
experiments. What remains class-specific is evaluating or bounding that
deficiency—not defining a different certification object.
