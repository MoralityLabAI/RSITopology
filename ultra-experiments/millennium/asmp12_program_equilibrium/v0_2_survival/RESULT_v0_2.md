# ASMP-12 budget-by-temptation equilibrium survival result v0.2

## Verdict

`equilibrium_survival_phase_established_for_registered_finite_class`

All seven preregistered gates passed across 8,192 exact
catalog-family-temptation cells. An independent implementation reproduced the
primary Prisoner's-Dilemma cooperative-death counts at `T=2,3,4,5` as
`0,0,174,174`.

## Primary phase transition

For both registered payoff families, with cooperation reward `R=3`:

| temptation region | cooperative deaths | syntax-equivalence deaths | extensional catalogs with cooperative death |
|---|---:|---:|---:|
| every registered `T <= 3` | 0/512 | 0/512 | 0/374 |
| every registered `T > 3` | 174/512 | 16/512 | 134/374 |

The cooperative-survival phase boundary is therefore exactly the ordinal
comparison `T>R` in this finite class. At or below `R`, no newly admitted
program can improve on a mutually cooperative payoff. Above `R`, a program
that defects while inducing incumbent cooperation can profit, making
program-manufactured cooperation vulnerable to catalog growth.

The constancy of the counts over `T in {4,5,6}` is not a fitted scaling law.
No payoff ordering changes within that region, so the exact best-response graph
is constant.

## Exact boundary liveness

For the registered `DDD/DCC/DDD` witness at budget 3:

| temptation | deviation margin | `(p1,p1)` equilibrium? |
|---:|---:|---|
| `2.99` | `+0.01` | yes |
| `3.00` | `0` | yes, by the frozen no-strict-improvement rule |
| `3.01` | `-0.01` | no |

Thus the surface does not merely compare two distant payoff tables; it resolves
the registered boundary on both sides with exact rational arithmetic.

## The full payoff surface is more stratified

Cooperative survival has one sharp `T=R` transition, but the complete pure
equilibrium payoff correspondence changes at additional payoff-ordering cells:

| family | `T=0` | `T=1/2` | `T=1` | `T=2` | `T=3` | every `T>3` |
|---|---:|---:|---:|---:|---:|---:|
| `pd_order` payoff-death catalogs | 118 | 118 | 118 | 187 | 187 | 234 |
| `chicken_order` payoff-death catalogs | 195 | 258 | 258 | 258 | 272 | 313 |

This supports the survival-surface reframing while warning against reducing the
whole equilibrium correspondence to the single cooperation threshold.

## Extensionality result

The v0.1 decomposition survives throughout the live phase:

- 16/512 catalogs lose cooperation through different treatment of
  extensionally identical source programs;
- that mechanism is absent from every duplicate-extensional catalog; but
- 134/374 duplicate-extensional catalogs still lose cooperation through a
  genuinely different newly admitted program.

Quotienting literal source syntax repairs one brittle mechanism, not the
anti-monotone equilibrium correspondence itself.

## Margin stability certificate

The runner checked 32,064 cooperative-equilibrium margins with nontrivial
deviations. It produced 12,384 positive-margin certificates. For each positive
margin `m`, a sup-norm perturbation of every payoff entry by
`epsilon=m/4` leaves worst-case residual margin at least

`m - 2 epsilon = m/2 > 0`.

Boundary equilibria with zero margin receive no robustness certificate and are
allowed to change status under arbitrarily small adverse perturbations, as the
canonical `T=R` cell demonstrates.

## Mathematical object

The experiment does not claim that equilibrium sets form an ordinary
bifiltration. Its monotone substrate is the directed graph of admitted profiles
and profitable deviations; equilibrium status is a derived sink property.
The finite output is a constructible survival surface over budget and payoff
order. A future persistence-module claim would require explicit compatible maps
or a registered zigzag construction.

## Artifact binding

- prereveal source commit: `9416b63f6e3f061bc8fec5b29c54a877fa07934e`;
- registration commit: `0dc9235accfc5109906241b469ab48ec198de7a7`;
- registration SHA-256:
  `69dd2d03cf59159e6b7a970f76827664907cf7219037dd4e7c7add790abc96ca`;
- result SHA-256:
  `c1dedfe2b34903c5d3a01e7bfac0abf55ab5d9fa20addbc36de305317e999aae`;
- receipt SHA-256:
  `880a207619db15bb69ec78b8b9e3b54a4423f244e8a386b45630d90cdf4c8490`;
- tests: `4 passed`.

## Claim boundary

This establishes an exact pure-equilibrium survival phase only for the
registered three-program source-table language and two payoff families. It does
not characterize mixed or unrestricted program equilibria, prove a general
persistence theorem, model bounded proof search, predict a selection dynamic,
or establish language-model source conditioning.

