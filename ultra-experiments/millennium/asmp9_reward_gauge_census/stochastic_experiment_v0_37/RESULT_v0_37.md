# Stochastic-experiment result v0.37

## Verdict

`finite_stochastic_access_ledger_established`

All five prospectively registered gates passed on the disjoint confirmation
grid. The exact finite result separates three objects that ASMP-9 must not
conflate:

1. the connected-component quotient governing zero-error decisions;
2. the quantitative minimax-risk profile for a declared target-only decision;
   and
3. full Blackwell/Le Cam comparison on the expanded target-by-nuisance
   parameter.

The first does not determine the second, while the third can strictly
overprice nuisance information irrelevant to the target. This corrects the
resolution ledger; it does not resolve ASMP-9 or establish a new comparison
theorem.

## Registered experiment class

Each binary experiment has three targets, two nuisance states, and one
Bernoulli response:

```text
P(Y=1 | theta, xi), theta in {0,1,2}, xi in {0,1}.
```

The confirmation census evaluated every table in

```text
{1/4, 1/3, 2/3, 3/4}^6,
```

for exactly `4,096` experiments. The burned development values
`{0,1/2,1}` were excluded. Four target decisions were frozen: the three
nontrivial binary cuts and target identity. Two observation semantics were
evaluated:

- one sampled Bernoulli transcript; and
- exact access to the population response law, with nuisance still unknown.

Floating-point optimization proposed active constraints only. Every accepted
minimax value carried matching exact rational primal and dual certificates.

## Zero-error quotients do not determine approximate risk

| Oracle | Distinct component quotients | Heterogeneous quotients | Maximum risk spread inside one quotient |
| --- | ---: | ---: | ---: |
| one sampled transcript | 1 | 1 | `1/4` |
| exact population law | 5 | 1 | `1/6` |

For one sampled transcript, every confirmation probability is strictly
between zero and one. Every target can therefore emit both response symbols,
so all `4,096` experiments have the same complete zero-error component
quotient. Their minimax decision risks nevertheless differ.

The maximum sampled-transcript witness uses the decision
`cut_0_vs_12`. The constant table

```text
[1/4, 1/4, 1/4, 1/4, 1/4, 1/4]
```

has exact minimax risk `1/2`, while

```text
[1/4, 1/4, 3/4, 3/4, 3/4, 3/4]
```

has risk `1/4`. Both have the same single connected component.

For the population-law oracle, the maximum witness uses target identity. The
same constant table has risk `2/3`, while

```text
[1/4, 1/4, 1/4, 1/3, 1/3, 1/3]
```

has risk `1/2`. Both again have the same single connected component.

Consequently, no statistic that factors only through the registered
zero-error component quotient can recover quantitative minimax risk on this
finite class. Components remain exact for the yes/no question of zero-error
decodability; they are not an approximate-risk sufficient statistic.

## Expanded-parameter deficiency can be conservative

The classical directional-deficiency anchors were reproduced exactly:

| Comparison | Exact deficiency |
| --- | ---: |
| informative to uninformative | `0` |
| uninformative to informative | `1/4` |

Across the `100` frozen source, target, and decision comparisons, the
target-risk gap never exceeded directional deficiency. There were zero
violations and the minimum bound-minus-gap slack was `0`.

The nuisance-only witness exposes the other direction. Comparing a
constant-zero experiment with an experiment that reveals nuisance but carries
no target information gives:

```text
expanded target-by-nuisance deficiency = 1/2
maximum target-only risk gap           = 0
```

for every registered nontrivial target partition. Full expanded-state
deficiency therefore remains a valid sufficient risk-transfer bound, but it
is not an exact characterization of target-only decision value in the
presence of nuisance.

## Gate record

| Gate | Requirement | Decision |
| --- | --- | --- |
| E0 | complete 4,096-table, four-decision, two-oracle census | pass |
| B0 | exact Blackwell anchor values | pass |
| R0 | 100 risk-transfer comparisons without violation | pass |
| S0 | positive within-quotient risk spread under both oracles | pass |
| C0 | strict expanded-deficiency conservatism witness | pass |

## Consequence for ASMP-9

Versions v0.36 and v0.37 now establish a corrected hierarchy:

1. nuisance-conditioned pairwise confusability is generally a graph and can
   be nontransitive;
2. its connected components are the minimal forced-equality quotient for
   zero-error decision feasibility;
3. a quantitative target-risk profile does not generally factor through that
   quotient;
4. full expanded-parameter deficiency controls all bounded losses but can be
   conservative when nuisance information has no target value; and
5. a scientifically meaningful gauge action remains a separate claim that
   requires an actual transformation model.

The next load-bearing mathematical object is therefore a decision-relative
comparison preorder for experiments with nuisance, together with necessary
and sufficient conditions under which it admits a tractable channel or
quotient representation. Repeating zero-error component censuses cannot close
that obligation.

## Integrity and resource record

The implementation was committed as `906ff48` and the registration was
committed and pushed as `2148cad` before execution. The producing run took
`611.7678792` seconds, below the registered `900`-second validity ceiling. Its
maximum sampled process peak working set was `74.32 MiB`, far below the
`1 GiB` reporting ceiling. The process was sampled through second `579`; no
operating-system hard memory cap or final-interval peak capture was installed,
so the receipt does not mislabel this as a continuously enforced RSS maximum.

The separate replay took `727.0764879` seconds and recomputed all quotient
class counts, heterogeneous-class counts, maximum spreads, anchors, and gate
conditions. All `12` replay checks passed and the result content hash matched.

## Prior art and claim boundary

Blackwell comparison, Le Cam deficiency, zero-error confusability, and
nuisance-parameter comparison are classical. The prior-art audit classifies
this result as `subsumed_instrument_consolidation`. Its contribution to this
program is the exact finite counterexample ledger and the correction it forces
in ASMP-9's resolution obligations.

Nothing here identifies a real reward or value model, characterizes arbitrary
stochastic or strategic demonstrators, proves a general nuisance-comparison
theorem, or resolves ASMP-9.
