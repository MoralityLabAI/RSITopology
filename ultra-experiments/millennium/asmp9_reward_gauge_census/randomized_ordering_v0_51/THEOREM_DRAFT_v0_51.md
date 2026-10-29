# ASMP-9 v0.51 randomized evidence-ordering theorem draft

## Setup

Let `Pi` be the finite set of outcome orderings and let `S` be the finite set
of registered `(decision objective, reference vertex)` scenarios. For
ordering `pi` and scenario `s=(d,v)`, define regret

```text
A(pi,s)
  = C_d(pi;v) - min_sigma C_d(sigma;v).
```

Every entry is nonnegative and every column has at least one zero.

A randomized evidence-ordering procedure chooses a distribution `p` over
`Pi` before the scenario is selected and before the order is realized. Its
worst-case expected regret is

```text
max_s sum_pi p(pi) A(pi,s).
```

## Theorem 1: exact primal/dual game

The minimum randomized worst-case regret is the finite linear program

```text
minimize    t
subject to  sum_pi p(pi) A(pi,s) <= t  for every s
            sum_pi p(pi) = 1
            p(pi) >= 0.
```

Its dual is the adversarial scenario game

```text
maximize    z
subject to  sum_s q(s) A(pi,s) >= z  for every pi
            sum_s q(s) = 1
            q(s) >= 0.
```

The two exact rational values agree. Complementary slackness identifies the
active orderings and least-favorable objective/reference scenarios.

This is the classical finite zero-sum-game formulation of randomized minmax
regret, not a new theorem.

## Theorem 2: zero-regret support

The randomized value is zero if and only if a deterministic ordering is
optimal in every scenario.

More strongly, a randomized procedure has zero regret if and only if every
ordering in its support lies in

```text
intersection_s argmin_pi C_s(pi).
```

*Proof.* If the support lies in the intersection, every payoff entry on the
support is zero. Conversely, suppose every scenario expectation is zero.
All payoff entries and probabilities are nonnegative. Therefore every
positive-probability ordering has zero payoff in every scenario and belongs
to the intersection. QED.

Randomization can reduce positive regret, but it cannot manufacture an exact
certificate when the deterministic common-chain intersection is empty.

## Theorem 3: smallest strict-gain witness

Use the v0.50 one-objective, two-outcome reference-switch table:

```text
B(empty,x,y,X) = (0,0,0,1),
```

with reference vertices `(3/4,1/4)` and `(1/4,3/4)`. The regret matrix is

```text
          left   right
(x,y)       0     1/2
(y,x)      1/2     0.
```

Every deterministic ordering has worst-case regret `1/2`. The equal mixture
has expected regret `1/4` in both scenarios, and the equal adversarial mixture
certifies the matching lower bound. Hence:

```text
deterministic value = 1/2
randomized value    = 1/4
strict gain         = 1/4.
```

Two orderings and two scenarios are minimal for a strict randomization gain:
with one ordering there is no choice; with one scenario a deterministic
scenario optimum has zero regret.

## Finite census target

Use the same complete three-outcome universe and two reference vertices as
v0.50:

```text
19 admissible monotone tables
361 ordered objective pairs
6 orderings
4 scenarios per pair.
```

For every pair, solve both exact LPs and audit:

- primal/dual equality;
- complementary slackness;
- zero randomized value exactly when the v0.50 robust set is nonempty;
- randomized value no greater than deterministic value; and
- the count and magnitude of strict randomization gains.

The strict-gain count is an outcome, not a gate.

## Claim boundary

Randomized minmax regret for combinatorial optimization is established prior
art. This draft specializes it to decision-relative Buehler evidence
ordering and records the zero-regret support boundary. It does not establish
novelty, operationally justify randomized confidence reporting, give an
efficient large-width algorithm, handle continuous or strategic uncertainty,
validate a physical preference channel, or resolve ASMP-9.
