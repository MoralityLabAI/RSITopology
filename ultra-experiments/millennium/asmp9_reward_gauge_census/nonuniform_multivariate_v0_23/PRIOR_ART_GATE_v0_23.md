# ASMP-9 v0.23 prior-art gate

Status: development-only; must be frozen before any claim-eligible run.

## Classical ingredients

1. Alan D. Sokal, ["The multivariate Tutte polynomial (alias Potts model)
   for graphs and matroids"](https://arxiv.org/abs/math/0503607),
   arXiv:math/0503607, *Surveys in Combinatorics 2005*, defines

   ```text
   Z_G(q,{v_e}) = sum_{A subset E} q^k(A) product_{e in A} v_e
   ```

   and develops its edge-multivariate deletion-contraction calculus.  The
   polynomial, its `q=-1` specialization, and multiaffinity are classical.

2. Spencer Backman, ["Partial Graph Orientations and the Tutte
   Polynomial"](https://arxiv.org/abs/1408.3962), *Advances in Applied
   Mathematics* 94 (2018), 103-119, arXiv:1408.3962, proves that
   `(k,l)`-chromatic strongly
   connected partial orientations are counted by

   ```text
   (k+l)^(|V|-1) k^(|E|-|V|+1)
   T_G(l/(k+l),(2k+l)/k).
   ```

   The present edge-dependent expression is a direct multivariate lift of
   this weighted deletion-contraction identity.  It is not presented as a new
   graph polynomial.

3. Spencer Backman and Sam Hopkins,
   ["Fourientations and the Tutte Polynomial"](https://arxiv.org/abs/1503.05885),
   *Research in the Mathematical Sciences* 4:18 (2017), develops a broader
   weighted cut/cycle fourientation calculus.  This is the immediate
   neighboring literature for treating the ASMP ternary residual states as
   orientation objects.

4. Kazuo Murota,
   ["Exchange Properties of M-natural-concave Set Functions and Valuated
   Matroids"](https://arxiv.org/abs/2105.14228), surveys the exchange
   properties and local-to-global optimality of M-concave functions
   (arXiv:2105.14228).  The
   proposed K4 witness uses the standard exchange axiom; neither M-concavity
   nor its local-to-global theorem is new.

5. Reliability and redundancy allocation are established optimization
   literatures.  Relevant anchors include Boland, El-Neweihi, and Proschan's
   component-interchange principles and later coherent-system allocation
   work.  General nonconvexity and local optima in redundancy allocation are
   not novelty claims here.

## Exact ASMP specialization

At `epsilon=1/2`, put `z_e=2^(-n_e)`.  Each oriented boundary status has
weight `z_e`, and the bidirected `INTERIOR` status has weight `1-2z_e`.
Coefficientwise weighted deletion-contraction gives

```text
F_G(n)
  = - product_e z_e
      Z_G(-1,{z_e^(-1)-1})
  = - 2^(-sum_e n_e)
      Z_G(-1,{2^(n_e)-1}).
```

For a fixed bidirected set `B`, the coefficient identity is

```text
number of strong oriented completions with bidirected set B
  = - sum_{A superset B} (-1)^k(A).
```

This is a consolidation of classical ingredients into the ASMP-9 access
ledger, not a novelty claim for the multivariate Tutte polynomial or partial
orientations.

## Candidate-new finite obstruction

The candidate contribution is an exact infinite K4 family showing that the
fixed-total nonuniform objective is not governed by the simplest exchange
geometry.

With K4 edge order

```text
(01,02,03,12,13,23),
```

let

```text
x_s = (s-1,s,s+1,s+1,s,s-1)
y_s = (s,s,s,s,s,s),  s>=2.
```

The development calculation indicates:

- every feasible one-unit transfer from `x_s` strictly decreases exact
  availability;
- `y_s` has strictly larger exact availability; and
- `x_s,y_s` give an explicit violation of the M-concavity exchange axiom.

Before circulation, a further literature search must test whether this exact
K4 family or an equivalent weighted-reliability counterexample is already
known.  Absence from the present search is not evidence of novelty.

## Allowed claim language

- arbitrary positive integer edge counts at `epsilon=1/2` admit the stated
  exact edge-multivariate representation on a bridgeless block;
- the K4 family is a strict suboptimal one-exchange local maximum for every
  `s>=2`;
- the K4 objective is not M-concave on the fixed-total positive integer
  simplex; and
- one-unit exchange ascent has no general global-optimality guarantee for
  the frozen ASMP objective.

## Forbidden claim language

- the multivariate Tutte identity, weighted orientation calculus, or
  M-concavity theory is new;
- the K4 family is globally optimal or gives an approximation lower bound;
- exact optimizer search is NP-hard;
- no polynomial-time optimizer or approximation exists;
- the result covers arbitrary `epsilon`, dependent responses, adaptive
  allocation, behavioral IRL, or real model judgments; or
- ASMP-9 is resolved.
