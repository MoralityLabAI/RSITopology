# ASMP-9 v0.38 formulation draft: decision-relative access

## Status

`development_only_not_registered`

This document chooses the next resolution-directed object after v0.37. It does
not freeze an experiment or consume a confirmation grid.

## Three comparison levels

Let `E_A` be the experiment induced by query/intervention family `A`, and let
`E_full` be a frozen full-access reference. The parameter of interest is a
reward-gauge or downstream-decision class; all remaining response variation is
declared nuisance.

### Level 1: optimized value gap

```text
G_D(E_A,E_full)
  = sup_(L in D) [V_A(L) - V_full(L)]_+.
```

This asks whether the best registered rule under access `A` loses value for
one finite loss registry. It is useful operationally but can hide differences
between nonoptimal rules, priors, and unregistered losses.

### Level 2: target-relative deficiency

Use the classical deficiency relative to the frozen family of target-only
policy-regret decision problems. This is the primary v0.38 instrument. Its
zero set means that every full-access rule in the registered decision type has
an access-`A` counterpart with no greater registered risk.

The exact finite definition and normalization are now pinned in
[`DEFINITION_AUDIT_v0_38.md`](DEFINITION_AUDIT_v0_38.md). For losses in
`[0,1]`, `delta_D(E_A,E_full)` is the least additive `epsilon` such that every
full-access rule in every registered problem has an access-`A` rule whose
target-risk vector is at most `epsilon` worse componentwise.

### Level 3: expanded-parameter deficiency

Treat `(reward class,nuisance)` as the full statistical parameter and compute
ordinary directional deficiency. This remains a valid sufficient transfer
bound, but v0.37 shows why it can charge nuisance distinctions that one frozen
target-only minimax value ignores.

## Frozen-class candidate

The smallest useful class should reuse the finite-MDP objects already audited
in v0.28-v0.31:

- a finite reward hypothesis registry with the declared shaping/scale gauge;
- a finite policy family;
- policy-regret loss, with positive scale handled explicitly rather than
  silently normalized;
- candidate occupancy or behavioral queries;
- a full-access experiment using every registered query;
- shared response nuisance fixed across the query batch; and
- exact rational response probabilities.

Version v0.38 uses a frozen conditional nuisance law and compares the
resulting marginal target experiments. It reports ordinary deficiency on the
expanded `(target,nuisance)` experiment separately. It does not silently
switch between marginal, revealed, or adversarial nuisance semantics.

The access estimand is the smallest query family `A` satisfying

```text
relative_deficiency_D(E_A, E_full) <= epsilon.
```

Both `epsilon=0` and one positive rational tolerance must be registered.

## Development witness already located

A burned exact search over binary experiments found that equal optimized
minimax error does not imply experiment equivalence. For the symmetric
binary-identification loss, the channels

```text
E: P(Y=1|theta=0,1) = (1, 1/2)
F: P(Y=1|theta=0,1) = (1/2, 0)
```

both have exact minimax error `1/3`, while ordinary directional deficiency is
`1/6` in both directions. This is a control showing that Level 1 cannot stand
in for Level 2. It is burned development evidence and will not be used as an
unseen confirmation result.

The burned reward fixture in
[`DEVELOPMENT_RESULT_v0_38.md`](DEVELOPMENT_RESULT_v0_38.md) also separates
all three comparison levels inside an explicit policy-regret grammar. Two
target queries attain zero target-relative deficiency while omitting a
gauge-only query; expanded deficiency charges the omitted gauge bit by `1/2`.
Each target-query deletion has exact target-relative deficiency `1/4`.

## Gates to define before registration

1. **P0 prior-art fidelity:** the implemented Level-2 LP matches the cited
   finite relative-deficiency definition on hand-derived anchors.
2. **B0 Blackwell anchors:** equivalence, strict garbling, and incomparable
   controls return their exact expected values.
3. **V0 value-gap separation:** a burned or freshly registered control has
   equal `G_D` but positive Level-2 deficiency.
4. **N0 nuisance separation:** target-relative and expanded-parameter results
   differ on a declared nuisance-only control under the frozen nuisance
   semantics.
5. **G0 gauge null:** adding a query that observes only a licensed gauge
   direction does not improve target-relative deficiency.
6. **D0 decision sufficiency:** an access family may pass without full reward
   reconstruction only when every residual direction is null for the frozen
   policy-loss family.
7. **A0 access threshold:** the exact minimum passing family and every
   one-query deletion are certified.

## Kill conditions

- If Level 2 cannot be implemented directly from a primary formal definition,
  v0.38 does not register.
- If the reward/MDP registry makes target-relative and full deficiency
  identical by construction, the fixture is non-discriminating and does not
  register.
- If policy-regret loss is insensitive to every candidate reward direction,
  the target is vacuous.
- If the minimum access family is selected after looking at confirmation
  outcomes, the result is exploratory only.

## Claim boundary

This successor aims at one finite access threshold using a classical
decision-relative comparison object. It is not a new deficiency theorem,
general reward identifiability, evidence about a real model, or an ASMP-9
resolution.
