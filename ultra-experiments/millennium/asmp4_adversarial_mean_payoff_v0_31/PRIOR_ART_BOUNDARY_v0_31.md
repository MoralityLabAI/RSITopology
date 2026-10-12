# Prior-art boundary v0.31

The underlying game theorem is classical. Velner, Chatterjee, Doyen,
Henzinger, Rabinovich, and Raskin prove that conjunctive mean-payoff-`inf`
games may require infinite memory for the protagonist, admit memoryless
spoilers, and have a coNP-complete threshold problem:
[The Complexity of Multi-Mean-Payoff and Multi-Energy Games](https://doi.org/10.1016/j.ic.2015.03.001)
([open preprint](https://arxiv.org/abs/1209.3234)).

Chatterjee, Doyen, Henzinger, and Raskin establish the finite-memory
mean-payoff/energy correspondence and coNP-completeness of the finite-memory
problem in the preceding development:
[Generalized Mean-payoff and Energy Games](https://doi.org/10.4230/LIPIcs.FSTTCS.2010.505).

No novelty is claimed for multi-mean-payoff determinacy, memoryless spoiling,
the nonnegative multicycle criterion, finite-memory approximation, or their
complexity classification.

The repository contribution is a precise integration and audit:

1. The registered ASMP-4 `limsup` cost upper bound is mapped with the correct
   sign to mean-payoff-`inf`, rather than to mean-payoff-`sup`.
2. The classical threshold theorem is rewritten as an entire two-port region
   formula: intersection over adversary policies, union over reachable SCCs,
   and upward closure of cycle polytopes.
3. v0.25 appears exactly as the empty-adversary special case, and v0.26's
   previously open nondeterministic finite-quotient corollary becomes
   executable.
4. Exact rational central and import-independent implementations issue
   component witnesses or memoryless spoiler certificates and check the
   infinite-memory boundary.

The package does not claim a new graph-game algorithm or solve the missing
nonlinear quotient-construction problem.
