# Prior-art gate for ASMP-9 history stabilization v0.73

Status: **classical automata specialization**.

## Subsumption

The mathematical ingredients are classical:

- Myhill-Nerode equivalence and right-congruence quotients;
- deterministic Mealy/sequential transducer minimization;
- partition refinement for finite-state behavioral equivalence;
- product-automaton equivalence testing; and
- reward machines as finite automata carrying transition rewards.

The finite-index criterion, `K-1` refinement bound, and product-state
distinguishing construction are not claimed as novel.

## Relation to v0.71

Version v0.71 constructed a minimal history quotient for one complete bounded
path table. Version v0.73 makes the horizon boundary explicit:

1. the infinite future-increment quotient is the canonical object;
2. a finite index is an assumption or result that must be established, not
   inferred from a finite prefix;
3. a registered `K`-state restriction permits finite certification internal
   to that class; and
4. delayed-pulse witnesses defeat unrestricted finite-prefix claims.

## Residual contribution

The ASMP-9-specific deliverable is an access/claim ledger:

```text
finite-prefix agreement
    is not
open-ended reward-object stabilization;

finite distinguishing horizon
    requires
a declared finite-state or regularity bound.
```

The exact censuses are implementation controls, not novelty evidence.

## Prior-art review still required before circulation

A circulation version should pin primary citations for:

1. Nerode equivalence and minimal deterministic automata;
2. Mealy/sequential transducer equivalence and minimization;
3. weighted or additive-output automata;
4. modern reward-machine definitions; and
5. finite-horizon identification lower bounds for unknown automata.

## Hostile-review questions

1. Is the registered state bound independently justified or chosen after the
   observed horizon?
2. Are cumulative values observed exactly, or inferred with noise?
3. Does the alphabet omit context that would make the process Markov?
4. Are unreachable internal states being counted as empirical complexity?
5. Does stochasticity require probabilistic automata rather than a
   deterministic reward machine?
6. Is a finite-prefix fit being misreported as evidence of moral or semantic
   validity?

All remain outside this development claim.
