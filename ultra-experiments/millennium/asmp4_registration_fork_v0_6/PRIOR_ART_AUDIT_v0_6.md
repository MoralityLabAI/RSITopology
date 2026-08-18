# ASMP-4 v0.6 adaptive-grammar prior-art audit

## Decision

The positional infinite-horizon step in Theorem 6 is an application of an
existing entropy-game theorem, not a new general result about nonlinear
Perron-Frobenius operators. The local contribution is the exact reduction of
registered sensor grammars to that theorem, its integration with the two-port
write converse, and the explicit ASMP-4 registration witnesses and censuses.

## Primary sources

1. Marianne Akian, Stéphane Gaubert, Julien Grand-Clément, and Jérémie
   Guillaud, [The Operator Approach to Entropy
   Games](https://drops.dagstuhl.de/opus/volltexte/2017/7026/pdf/LIPIcs-STACS-2017-6.pdf),
   STACS 2017. Their extended model prescribes the initial state. Proposition 1
   gives the finite dynamic-programming recursion; Theorem 2 proves existence
   of the infinite-horizon value, equality with the limit of finite value
   roots, and optimal positional strategies; Theorem 3 gives the positional
   minimax formula state by state.
2. Eugene Asarin, Julien Cervelle, Aldric Degorre, Cătălin Dima, Florian Horn,
   and Victor Kozyakin, [Entropy Games and Matrix Multiplication
   Games](https://drops.dagstuhl.de/storage/00lipics/lipics-vol047-stacs2016/LIPIcs.STACS.2016.11/LIPIcs.STACS.2016.11.pdf),
   STACS 2016. This supplies the entropy-game/independent-row-uncertainty
   background and positional/constant optimality for the original all-initial-
   states model.

## Exact reduction used here

The state of the extended entropy game is a nonempty pre-read subset-observer
belief. A minimizing action is a safe registered sensor partition. People’s
nondeterministic branches are the nonempty cells of that partition on the
belief. A cell moves to its graph-successor belief; multiple cells reaching the
same successor produce the integer matrix multiplicity. Thus the entropy-game
dynamic operator is exactly

~~~text
V_(t+1)(B) = min_P sum_C V_t(Succ(C)).
~~~

The initial belief is prescribed, matching the 2017 extension rather than the
worst-initial-state convention of the 2016 paper. Removing beliefs without an
infinite safe continuation makes the arena nonblocking. The finite values on
the unrestricted and viable arenas have the same exponential rate by the
bounded-deletion sandwich in Theorem 6.

## Claim boundary

This package may claim:

- the exact ASMP-4 belief/partition reduction;
- the finite read and write rectangles;
- the resulting stationary-policy spectral formula for the registered finite
  graph class;
- the exact strongly connected aperiodic registration gap; and
- the independently reproduced bounded censuses.

It must not claim invention of entropy games, the prescribed-initial-state
operator theorem, positional optimality in that game class, or the general
independent-row-uncertainty spectral theorem.
