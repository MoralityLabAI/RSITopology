# ASMP-3 block-selection composition theorem v1.9

## Status and scope

```text
result_status = exact finite block-composition and selection risk
parent_result = ASMP-3-INDEPENDENT-NOISE-AMPLIFICATION-v1.8
interface_mode = WV-FIX
semantic_atoms = M predeclared binary atoms
replication = d iid responses per atom, disjoint independent blocks
atom_decoder = majority with uniform tie break
changes_parent_problem = false
```

The v1.8 theorem closes one-atom amplification.  This release composes `M`
amplified atom decisions, quantifies the risk of selecting a failed decoded
block, and charges the replication cost needed to retain a target joint risk.

## 1. Frozen composition interface

For each of `M` semantic atoms, ask `d` registered meaning-preserving copies
through the v1.8 i.i.d. class at worst legal rate `eta`.  Blocks use disjoint
error bits and are conditionally independent given the truth vector.  Decode
each atom by majority with a uniform tie break.

Write `e=e_d(eta)` for the exact v1.8 one-atom error.  Since the blocks and tie
coins are independent, the `M` decoded-error indicators are iid
`Bernoulli(e)`.

Two interfaces make joint failure tight:

1. `Refute_OR` applies OR to an all-zero truth vector.  It is wrong exactly when
   at least one decoded atom is one.
2. A truth-aware selector observes the decoded blocks and returns a failed block
   whenever one exists.  Its selected answer is wrong on the same event.

The second is a selection-risk harness, not a claim that the selector is a
benign verifier component.

## 2. Exact independent-block risk

The probability that no decoded block fails is `(1-e)^M`.  Therefore both tight
interfaces have exact risk

```text
R_ind(M,d,eta)=1-(1-e_d(eta))^M.                    (1)
```

This quantity can be much larger than the selected block's unconditional
one-atom error.  Conditioning on “the selector chose this block” destroys the
naive iid interpretation of that selected block even though all preselection
blocks were independent.

At `eta=1/5`, `d=9`, and `M=32`,

```text
single-block error = 7649/390625                    (about 0.01958),
selected/OR risk   = 1-(1-7649/390625)^32           (about 0.469).
```

Thus a transcript can amplify selection risk while leaving every preselection
block distribution unchanged.

## 3. Marginal-only extremal law

Suppose only that each decoded atom has error probability at most `e`, with no
block-dependence restriction.  The union bound gives

```text
Pr[any error] <= min(1,Me).                         (2)
```

This is sharp.  On a unit probability interval, arrange `M` events of measure
`e` disjointly while `Me<=1`; when `Me>=1`, place/cycle them so their union
covers the interval.  Hence

```text
sup_(all joint laws with marginals e) Pr[any error]=min(1,Me).  (3)
```

The block-independent law (1) lies below (3).  This is another reason a
marginal amplification number is not a complete joint-noise invariant.

## 4. Persistent comparison

If each atom instead has one independent persistent latent flip copied to all
of its `d` replications, replication does nothing and joint OR risk is

```text
1-(1-eta)^M.
```

If one global latent flip is copied across every atom and replication, OR risk
on the all-zero vector is just `eta`.  These laws share the same raw response
marginals but have different joint risks from (1) and (3).

## 5. Exact depth and query cost

For target joint risk `delta`, the release computes the least odd `d` satisfying

```text
1-(1-e_d(eta))^M <= delta.                          (4)
```

It also computes the least odd union-safe depth satisfying

```text
M e_d(eta) <= delta.                                (5)
```

The latter remains valid without block independence once every candidate error
event has the declared marginal bound.  It can be slightly conservative.

Every construction is charged

```text
q=M d
```

semantic queries.  Combining the v1.8 exponential certificate
`e_d <= (1/2)[2sqrt(eta(1-eta))]^d` with (5) gives

```text
d=O(log(M/delta)),
q=O(M log(M/delta))
```

for fixed `eta<1/2`.  Thus when `M` is polylogarithmic in prover computation and
`delta` is constant or inverse-polylogarithmic, the composed query cost remains
polylogarithmic, with all factors explicitly charged.

The exact table covers `eta in {1/5,1/3,2/5}`, `M in {1,4,16,64}`, and target
risks `1/10` and `1/100`.  The hardest registered case (`eta=2/5`, `M=64`,
`delta=1/100`) requires `d=319`, or 20,416 semantic queries.

## 6. Computational receipts

The producer certifies 744 exact composition rows across four rates, six atom
counts, and depths one through 31.  It enumerates every raw multi-block response
profile in 12 small cases, independently checks 24 minimal-depth requirements,
and records exact rational comparisons with persistent and marginal-only laws.

The clean-room checker rebuilds every binomial error, composition formula,
small response space, depth search, query count, and parent contract without
importing the producer.

## 7. Compositional firewall

Equation (1) requires disjoint independent blocks after the relevant transcript
and atom set have been fixed.  If an adaptive history can influence or inspect
the error bits before the candidate set is finalized, the theorem must instead
account for every selectable candidate, use a conditional independence
guarantee, or fall back to a valid joint bound such as (2).

The OR and failure-selector constructions prove tight risk for their declared
fixed majority interface.  They do not compute the value of every globally
optimized adaptive protocol, whose verifier may expose different information,
change decoders, allocate queries sequentially, or reject the selection rule.

## 8. Remaining ASMP-3 boundary

This release closes finite nonadaptive block composition with an explicit
selection breadth.  It does not characterize unbounded/adaptive candidate
generation, stopping-time query allocation, efficient honest refutation search,
communication and honest-prover lower bounds, or `WV-ADM` interface choice.

## 9. Novelty boundary

Independent-event composition, union bounds, and majority amplification are
standard.  The contribution is the typed ASMP-3 selection interface, exact
rational risk and query-depth receipts, sharp marginal-only comparison, and an
explicit firewall between preselection block independence and selected-history
conditional risk.
