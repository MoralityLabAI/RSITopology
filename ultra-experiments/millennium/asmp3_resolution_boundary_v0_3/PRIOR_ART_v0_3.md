# ASMP-3 v0.3 prior-art boundary

The probability identity in the binding branch is classical. For independent
Bernoulli errors with rate `eta`, the parity correlation after `d` bits is
`(1-2 eta)^d`. The total-variation certificate is the corresponding binary
symmetric-channel calculation. No novelty is claimed for either fact.

The protocol-side comparison is closest to Brown-Cohen et al.,
[*Debate is Efficient with Your Time*](https://arxiv.org/abs/2602.08630).
That paper defines Debate Query Complexity, proves that functions depending on
all input bits require `Omega(log n)` queries, gives logarithmic upper bounds
from circuit size, and characterizes logarithmic-query efficient debate as
`PSPACE/poly`. These results emphasize that an interactive disagreement game
can be much smaller than a static global certificate.

Brown-Cohen, Irving, and Piliouras,
[*Scalable AI Safety via Doubly-Efficient Debate*](https://arxiv.org/abs/2311.14125),
give constructive deterministic and stochastic debate protocols with efficient
honest strategies. The present result does not extend those protocols. It
identifies a mismatch between the repository's static `Refute` invariant, its
single-atom noise profile, and the unstated interface connecting them.

The repository's v0.1.2 and v0.1.3 ASMP-3 moment calculations already show that
low-order dependence summaries may not certify majority amplification. The new
point is orthogonal: even exact knowledge of every single-atom minimax error is
insufficient for a binding multi-atom predicate without a joint composition
condition.

The contribution claimed here is limited to:

1. the explicit two-branch closure audit of the frozen v0.1 conjecture;
2. a complete nonzero persistent-noise countermodel satisfying the three
   displayed conditions on the binding reading;
3. exact rational and exhaustive certificates for the vanishing joint gap; and
4. a mechanically checkable repair obligation.
