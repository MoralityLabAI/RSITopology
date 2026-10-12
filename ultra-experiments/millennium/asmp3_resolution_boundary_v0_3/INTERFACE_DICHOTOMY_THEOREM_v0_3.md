# ASMP-3 v0.1 `Refute`-interface dichotomy theorem

## Statement

The Weak-Verifier Characterization Conjecture in
`AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md` is not closed as written. The canonical
text freezes a decidable relation `Refute_n(tau,S,b)` and defines `r_R` from it,
but does not state:

- that verifier decisions must be mediated by `Refute`;
- that `Refute` is sound and complete for every admissible semantic
  refutation; or
- that it is maximal or quotient-minimal under registered meaning-preserving
  query replications.

Under the two explicit interface completions below, one direction of the
proposed characterization fails. These completions do not exhaust the separate
choice of protocol quantifier described next.

This is a conditional interface theorem, not yet a full canonical-game
counterexample. The v0.1 phrase “admits a protocol” does not settle whether
admissible transcript encodings are frozen task-family data or are chosen by
the existential protocol. Branch B uses the first reading. Under the second,
advocates can send all `d=log2(T)` semantic bits and a one-query disagreement
test has gap `3/5`, so Branch B does not refute protocol admission.

## Branch A: nonbinding `Refute`

Suppose a verifier may use its semantic answers and transcript checks without
being constrained by the declared `Refute` relation. Take one genuinely local
semantic contradiction and register `m` synonymous meaning-preserving atoms
for it. They have identical ideal answers, description complexity
`O(log m)`, locality, and evaluation cost.

Two sound and complete decidable refutation relations are available:

```text
Refute_any  = one registered copy suffices;
Refute_all  = all registered copies are required.
```

The task, message game, verifier, prover strategies, oracle, and semantic
answers are identical. Nevertheless,

```text
r_any = 1,
r_all = m.
```

Choosing `m=T(n)` changes the proposed polylogarithmic-dimension condition
without changing whether the task admits the protocol. Hence `r_R` is not a
necessary protocol invariant unless adequacy and quotient rules bind
`Refute` to the verifier.

This is not the forbidden “one atom contains the full answer” construction.
Every atom is a synonym of the same local contradiction. The failure is
replication sensitivity in the syntactic relation itself.

## Branch B: binding `Refute`

Now suppose verifier semantic decisions must evaluate the declared refuting
set. Freeze the following nontrivial message game for `T=2^d` and `d>=2`.

The task output is the XOR of:

1. the root of a `T`-leaf formal XOR computation; and
2. the parity of `d=log2(T)` genuinely distinct local semantic bits.

The honest advocate computes the formal tree in `Theta(T)` time. Formal
disagreements are cross-examined down the tree: at each level, either the
dishonest child pair violates its claimed parent XOR or exactly one child
remains disputed. Thus the formal component uses `O(log T)` messages and ends
at one formal leaf.

For the semantic component, the frozen grammar lets each advocate send its
parity claim and the fixed refuting set of all `d` indices. It does not include
per-atom value claims. The set is encoded as an explicit sorted list, costing
`O(d log d)` bits (`O(d)` word-RAM operations), still
`O(log T log log T)`. Malformed sets lose formally. In the least-favourable
soundness pair, both advocates give the same correct formal root and differ only
on semantic parity. Their messages then contain no information beyond the two
opposite parity claims; all verifier evidence about the dispute comes from
semantic-oracle answers. The honest strategy remains efficient: `Theta(T)`
overall, with `O(d log d)=O(log T log log T)` bit work for the semantic list.

Each semantic atom is an indexed bit with `O(log d)` description, radius-one
locality, and `O(1)` ideal evaluation. Because `d>=2`, no atom contains the
semantic parity or the full task answer. Freeze

```text
Refute(tau,S,b) =
  [tau has a formal local XOR inconsistency]
  OR
  [S is all d semantic indices
   AND parity(b) contradicts tau's semantic-parity claim].
```

If a semantic index is missing from `S`, its two completions have opposite
parities, so neither parity claim is refuted. All `d` atoms suffice. Formal
faults have smaller refutations, but a formally consistent transcript with a
wrong semantic-parity claim exists. Therefore the max-min invariant is exactly

```text
r_R(T) = d = log2(T).
```

Against every dishonest strategy, an honest advocate either identifies a
formal cross-examination step or lists the fixed `d`-atom semantic set.

For atom `i`, draw one persistent error

```text
E_i ~ Bernoulli(1/5)
```

and return `H(i) xor E_i` on every registered replication of that atom.
Different atoms have independent latent errors. This is a complete,
nonadaptive, nonzero correlated-noise class: all within-atom replications are
perfectly correlated.

For every number of replications `k`, the first-answer aggregator has error

```text
1/5 <= 1/2 - 3/10.
```

Therefore `a_H(k)<=1/5`, which is all condition 3 requires. The refuting set
has size `d=log2(T)`, and an honest prover emits its explicit sorted list in
`O(d)` word-RAM operations or `O(d log d)` bit time, so conditions 1 and 2 hold
as well.

However, the parity of the observed vector differs from the ideal parity iff
an odd number of persistent errors occurred. Exact binomial expansion gives

```text
Pr[parity error] = (1-(3/5)^d)/2
```

and therefore the best possible decision gap is

```text
1 - 2 Pr[parity error]
= (3/5)^d
= T^(log2(3/5))
-> 0.
```

The optimality claim is minimax within the frozen message game, not an
assertion about the parity estimator alone. Label advocates by claim:
advocate 0 always claims semantic parity zero, advocate 1 always claims
semantic parity one, and the honest role switches with the true parity. Both
use the same canonical all-indices encoding and common formal transcript.
Put the uniform prior on each of the even- and odd-parity ideal vectors while
holding the formal component fixed. The complete non-oracle transcript is
therefore identical across the two class priors. Every adaptive query/stopping
transcript is a Markov kernel of the full persistent noisy vector and verifier
randomness, so data processing cannot increase total variation. Querying all
`d` atoms attains total variation exactly `(3/5)^d`. No test has a larger
prior-averaged gap, so no test has a larger worst-case gap.
The harness enumerates both distributions exactly through `d=9` and matches
the formula.

Explicitly, let `A` be the probability that any candidate verifier selects the
advocate of parity one after seeing the complete allowed transcript. Then

```text
| E_even[A] - E_odd[A] |
<= TV(P_even,P_odd)
= (3/5)^d.
```

If a protocol had uniform completeness minus soundness at least a fixed
`Delta>0`, averaging those pointwise guarantees over the two parity classes
would give `|E_even[A]-E_odd[A]|>=Delta`. Hence
`Delta<=(3/5)^d` for every `d`, contradicting a constant positive gap.

Thus a constant single-atom advantage does not imply the conjecture's constant
protocol gap when a binding refutation combines a growing number of atoms.

## Consequence

The v0.1 “if and only if” cannot be true under both interpretations:

- nonbinding `Refute` destroys necessity and encoding invariance;
- binding `Refute` destroys sufficiency because `a_H` is only a single-atom
  profile.

A repair must add both:

1. an adequate, verifier-binding, replication-quotiented refutation relation;
   and
2. a joint, selection-conditional amplification profile for the entire
   adaptive refutation game.

Replacing either object changes the quantifiers and therefore creates a new
problem version under the repository's resolution policy.

## Claim boundary

This is a conditional negative theorem about one frozen binding interpretation
of the v0.1 characterization plus a nonbinding invariance diagnosis. It does
not yet settle the canonical protocol quantifier, show that weak verification
is impossible, show that debate cannot work, or rule out a dynamic-refutation
characterization after the missing interface is formalized.
