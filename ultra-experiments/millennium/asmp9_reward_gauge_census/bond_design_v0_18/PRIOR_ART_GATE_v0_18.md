# ASMP-9 v0.18 prior-art gate

Status: development-only; complete before any v0.18 registration.

## Binding decision

Do not claim novelty for:

- bonds as inclusion-minimal cuts;
- bonds as circuits of the cographic matroid;
- strong connectivity characterized by directed cuts;
- budget allocation that maximizes a minimum cut;
- generic max-min design problems;
- fractional packing/covering LP duality; or
- polynomial solution by optimization/separation or min-cut oracles.

## Direct anchors

### Budgeted capacity and max-min cut design

- D. R. Fulkerson, "Increasing the Capacity of a Network: The Parametric
  Budget Problem," *Management Science* 5(4), 1959, 472-483:
  <https://doi.org/10.1287/mnsc.5.4.472>.
  This is the classical budget-allocation ancestry for increasing a network
  minimum cut / maximum flow.

- Alpar Juttner, "On Budgeted Optimization Problems," *SIAM Journal on
  Discrete Mathematics* 20(4), 2006, 880-892:
  <https://doi.org/10.1137/S0895480104445071>.
  Its abstract formulation explicitly includes
  `max_y min_{A in B} (w+y)(A)` under a linear budget.

- Deeparnab Chakrabarty, Aranyak Mehta, and Vijay V. Vazirani, "Design is as
  Easy as Optimization," *SIAM Journal on Discrete Mathematics* 24(1), 2010:
  <https://doi.org/10.1137/080735898>.
  This paper systematizes max-min design problems under a global budget and
  relates them to fractional packing. Its introduction explicitly locates
  the history in Fulkerson's minimum-cut capacity augmentation.

These sources make the v0.18 allocation LP and its polynomial solvability
classical. The repository must describe the LP as an identified classical
object, not as a new graph-optimization theorem.

### Bonds and cographic circuits

- James Oxley, *Matroid Theory*, 2nd ed., Oxford University Press, 2011,
  Chapters 2 and 5:
  <https://doi.org/10.1093/acprof:oso/9780198566946.001.0001>.
  Bonds are cocircuits of the graphic matroid and circuits of the cographic
  matroid.

- P. D. Seymour, "Packing and covering with matroid circuits," *Journal of
  Combinatorial Theory, Series B* 28(2), 1980, 237-242:
  <https://doi.org/10.1016/0095-8956(80)90067-2>.
  This is adjacent classical circuit-packing literature. It is not cited as
  proving the exact unit-capacity fractional bond parameter used here.

## Surviving contribution

The candidate ASMP-9 contribution is the exact interface composition:

```text
conditional count fiber
  -> residual-cycle quotient rank
  -> ternary boundary failure
  -> one-way residual cut
  -> bond clutter of the cyclic core
  -> classical max-min cut design.
```

The useful advance over v0.17 is the first exact identification of its
previously enumerated bad-support hypergraph. It removes a `3^|E|` structural
search from this access model and exposes the correct classical optimizer.

The cactus formula is an elementary specialization and should be described as
a closed-form control, not as established novelty.

## Novelty language permitted after a passing registration

Permitted:

> In the frozen independent-binomial reward-access model, the minimal events
> destroying full conditional-fiber quotient rank are exactly the bonds of
> the cyclic core. Consequently the leading access-allocation exponent is a
> classical max-min cut design objective.

Not permitted:

> We introduce or solve max-min cut design.

Not permitted:

> Fractional bond packing is new.

Not permitted:

> This resolves reward identifiability or ASMP-9.
