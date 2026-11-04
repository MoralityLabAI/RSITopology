# Prior-art gate for ASMP-9 history replacement v0.71

Status: **classical consolidation; no novelty claim**.

## Subsumption

Every mathematical ingredient has established antecedents:

1. path-edge factorization is an ordinary linear inverse problem;
2. additivity under concatenation is the homomorphism condition for a path
   monoid/category;
3. future-equivalence minimization follows the Myhill–Nerode template;
4. weighted automata and subsequential transducer minimization generalize this
   construction; and
5. reward machines explicitly augment environment state to represent
   non-Markovian rewards.

The v0.71 theorem is therefore not presented as a new automata or reward
representation result.

## Relevant lineages

- Myhill and Nerode supply the canonical future-equivalence/minimal-state
  pattern.
- Weighted finite automata and subsequential transducers supply the
  value-output generalization.
- Reward-machine work, including Icarte et al., uses automata states to encode
  non-Markovian reward structure for reinforcement learning.
- Potential-based reward shaping remains a separate gauge question; it does
  not turn a non-factorizing path valuation into a Markov reward on the
  original state graph.

## Residual ASMP-9 contribution

The deliverable is a total, auditable handoff inside the existing suite:

```text
path table
  -> exact Markov factorization or left-kernel witness
  -> minimal bounded-horizon augmented-state replacement
  -> separate v0.69 access/gauge test.
```

This directly instantiates one branch of the open replacement-object
classification without claiming to solve the general branch.

## Hostile-review questions

1. Is the complete prefix-closed path table physically observable?
2. Does the finite horizon manufacture finiteness of the replacement?
3. Are state and edge labels themselves stable across contexts?
4. Is the path valuation stationary, or is time-to-go carrying the effect?
5. Is an augmented reward machine an explanatory value object or merely a
   lossless encoding of the observations?
6. Does the access kernel identify the replacement, or only prove it exists?

The claim boundary keeps all six questions open outside the exact finite
grammar.
