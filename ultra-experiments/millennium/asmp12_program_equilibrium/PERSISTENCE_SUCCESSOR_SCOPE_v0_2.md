# ASMP-12 budget-by-payoff persistence scope v0.2

## Status

Candidate successor statement only. It is not registered and authorizes no
run. Prior-art review must precede any v0.2 freeze.

## Why ordinary bifiltration language is not automatic

The admitted program sets are nested in budget, but the equilibrium sets are
not. Therefore `E(b)` does not itself supply inclusion maps and is not, without
additional construction, an ordinary persistence module or bifiltration.

The natural monotone substrate is the profitable-deviation graph. At parameter
point `(b,t)`:

- vertices are admitted program profiles;
- a directed edge connects a profile to a unilateral deviation with positive
  payoff gain; and
- pure equilibria are vertices with no outgoing profitable-deviation edge.

Increasing budget adds profiles and possible deviation edges. Varying a payoff
parameter changes which potential edges have positive weight. Equilibrium
birth/death is then a derived sink-status process over this graph family.

If the graph family lacks compatible inclusion maps across both axes, the
correct formal object is a zigzag module, constructible correspondence, or
stratified survival region—not an ordinary two-parameter persistence module by
assertion.

## Frozen-statement candidate

Fix:

1. one maximal program catalog and its cost encoding;
2. a budget axis `b`;
3. a symmetric 2x2 payoff family with cooperation reward `R`, punishment `P`,
   sucker payoff `S`, and varying temptation `T`;
4. strict-deviation semantics with ties reported separately; and
5. the complete directed deviation graph at every `(b,T)` cell.

Compute:

- survival regions of cooperative equilibrium profiles;
- payoff-vector birth/death regions;
- syntax-equivalent versus extensional death labels;
- minimum deviation margin at each equilibrium; and
- discontinuity cells where a strict payoff comparison changes sign.

The first theorem target is a stability bound. If every current-versus-deviant
payoff comparison at an equilibrium has margin at least `m>0`, and every base
payoff entry is perturbed by at most `epsilon`, then each comparison changes by
at most `2 epsilon`. Hence the equilibrium status is unchanged whenever
`2 epsilon < m`. Boundary cells with zero margin are allowed to jump.

This margin result is elementary, but it supplies the certificate needed before
using bottleneck-distance or diagram-stability language.

## Registered controls required before execution

- base-game-Nash cooperation control: Stag Hunt should have no cooperative
  death while `R` strictly exceeds every unilateral-deviation payoff;
- manufactured-cooperation conditions: Prisoner's-Dilemma/Chicken cells with
  `T>R` make exploit deaths live;
- equality/tie cells reported separately rather than assigned by floating-point
  accident;
- rational payoff grid and exact arithmetic;
- source-label permutation control;
- additive encoding-padding replay; and
- a null catalog family with source-blind programs.

## Claim boundary

The successor could characterize a finite equilibrium-survival surface and its
margin stability. It would not prove a general persistence theorem for program
equilibria or predict language-model cooperation without a separately validated
behavioral bridge.

