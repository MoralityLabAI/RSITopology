# Robust public reset-atlas theorem v0.35

## 1. Registered connector data

Let `K` be an evaluator-safe subset of a metric plant state space and let `Q`
be a compact set of registered public source states.  A public state includes
the charged belief/reachable set and every sensor, controller, or actuator
memory that must be synchronized before another block begins.  Hidden plant
state is not public information.

Fix a registered reset cell `Z` contained in the interior of `K`.  A connector
word contains its finite control sequence, duration, decoder convention, and
terminal private-memory reset.  For one nominal word of length `L`, suppose
that along its nominal trajectory the plant obeys

```text
d(F(x,u,w), F(y,u,0)) <= A d(x,y) + D ||w||
```

on the registered tube.  The constants, metric, tube, disturbance radius
`omega`, and control authority are part of the certificate; they are not
inferred from an average trajectory.

If the source-cell radius is `eta`, define

```text
E_0 = eta,
E_(t+1) = A E_t + D omega.
```

For `A=1`,

```text
E_t = eta + t D omega.
```

For `A != 1`,

```text
E_t = A^t eta + D omega (A^t-1)/(A-1).
```

The formula remains valid for `0 <= A < 1`; the v0.35 exhaustive recurrence
census uses the expanding range `A >= 1` relevant to the sharp fixture.

## 2. Robust-word lemma

Assume the registered source cell is contained in `K`.  Let `delta_t` be the
distance of nominal post-step state `xbar_t` from the complement of `K`, and
let `rho` be the distance of `xbar_L` from the complement of `Z`.  If

```text
E_t < delta_t       for 1 <= t <= L,
E_L < rho,
```

then the same connector word keeps every source in that cell inside `K` for
every disturbance sequence with `||w_t|| <= omega`, and its terminal state is
inside `Z`.

Proof is by induction.  The registered Lipschitz inequality gives
`d(x_t,xbar_t) <= E_t`.  Each strict safe clearance contains the perturbed
post-step state, and the terminal reset clearance contains the last state in
`Z`.  The word is open loop after its charged selection; no future disturbance
or hidden state is consulted.

The strict inequalities are load-bearing.  They make validity open in the
source state and allow one nominal certificate to cover a public source basin.

## 3. Fixed-reset atlas theorem

Suppose every `z in Q` has a robust source basin `U_z` and a finite connector
word satisfying the robust-word lemma, ending in the same registered reset
cell and resetting all registered memories.  The basins form an open cover of
compact `Q`, so select a finite subcover

```text
U_1, ..., U_m.
```

Let `n` be the number of distinct words among the selected certificates and
let `L_max` be their maximum duration.  Resolve overlaps by a registered
deterministic rule.  The sensor sends the selected source-cell label, the
controller maps that label to a connector, and the actuator executes the
corresponding dictionary word.  A fixed-length realization has connector
bounds

```text
B_read  = ceil(log2 m),
B_write = ceil(log2 n),
L       = L_max.
```

The read label and write word are different transcripts and are charged
separately.  Word duration and private decoder memory are included in the
actuator dictionary rather than passed through an uncharged timing channel.

**Fixed-reset atlas theorem.** Under these hypotheses, every safe prefix whose
registered public endpoint lies in `Q` has a universally safe connector to
the common reset cell with uniform time and two-port costs `(L,B_read,B_write)`.
Consequently the connector correction divided by prefix horizon tends to
zero.  This is exactly the safe-closing hypothesis used by v0.33, so within
each registered recurrent component

```text
R_q = closure(upward(conv(P_q))).
```

Irreversible components still combine by an indexed union and outer closure;
the atlas does not convexify across them.

## 4. Relation to the v0.34 all-pairs premise

V0.34 assumes a stronger local certificate: every ordered pair of public
states in one cover element must be connected.  A fixed-reset atlas proves the
safe-closing conclusion directly, but it does not prove that all-pairs premise.

If, separately, robust connector basins are registered over the required
ordered public source/target pairs (including target belief-cell semantics and
memory reset), compactness of the registered pair set selects a finite
all-pairs atlas.  That stronger object instantiates v0.34.  The one-dimensional
fixture below constructs only the fixed-reset atlas and makes no all-pairs
claim.

## 5. Exact nonlinear uncertain fixture

Consider

```text
x_(t+1) = 2 x_t + u_t + x_t^2/4 + w_t,
K         = [-1,1],
Z         = [-1/8,1/8],
|w_t|    <= 1/128.
```

Use the 33 centers

```text
c_j = -1 + j/16,       0 <= j <= 32,
```

with cells of radius `1/32`, truncated at the endpoints of `K`.  The sensor
emits a nearest-center label, with a fixed tie rule.  For center `c`, the
controller selects the one-step word

```text
u_c = -2c - c^2/4.
```

Writing `x=c+e`, the exact successor is

```text
(2+c/2)e + e^2/4 + w.
```

Equivalently, the derivative of `g(x)=2x+x^2/4` is `2+x/2`, so `g` is
`5/2`-Lipschitz on `K`.  Hence

```text
|x_1| <= (5/2)(1/32) + 1/128 = 11/128 < 1/8.
```

Every labeled cell therefore reaches `Z` safely in one step for every allowed
disturbance.  The 33 actions are distinct and range from `-9/4` to `7/4`.
This construction uses six read bits and six write bits per closing event:

```text
ceil(log2 33) = 6.
```

These are constructive upper bounds, not claims of minimality.

## 6. Coordinate invariance

A registered bi-Lipschitz state conjugacy transports safe and reset sets,
source basins, nominal words, and strict robust tubes.  It changes numerical
Lipschitz constants and radii by finite distortion factors, but preserves the
existence of a finite robust atlas.  A causal transcript relabeling preserves
the read/write cardinalities exactly.  Thus atlas existence and the inherited
safe-closing region are coordinate invariant; a particular geometric radius
or Lipschitz constant is not.

An uncharged map from hidden plant state to a controller-visible coordinate is
not such a conjugacy of the registered architecture.

## 7. Sharp boundaries

### Nonlinear derivative

Using only the linear coefficient gives the false bound `9/128`.  At
`c=1`, `x=31/32`, `u=-9/4`, and `w=-1/128`, the exact successor is
`-351/4096`, whose magnitude exceeds `9/128 = 288/4096`.  The registered
`5/2` bound gives `11/128 = 352/4096` and covers it.

### Worst case versus mean

A symmetric disturbance with values `+/-1/16` has mean zero, but its robust
one-step bound is

```text
(5/2)(1/32) + 1/16 = 9/64 > 1/8.
```

Expected disturbance therefore cannot replace the universal quantifier.

### Unstable horizon and terminal margin

At fixed radius `1/32`, iterating the `A=5/2`, `omega=1/128` recurrence for
five steps gives `7281/2048`, far beyond the reset radius.  Long connector
words require finer cells or stronger margins.  A safe nominal path without a
terminal reset margin also supplies no reset certificate.

### Hidden observation and separate write authority

The observation `|x|` identifies `x=1` and `x=-1`.  Resetting `x=1` requires
an action in `[-19/8,-17/8]`, while resetting `x=-1` requires one in
`[13/8,15/8]`; the intervals are disjoint.  A read refinement is necessary,
and sensor knowledge does not make the actuator dictionary free.

### Dimension cost

A product cover with 33 centers per axis has `33^d` cells.  In dimension four
this is 1,185,921 cells and 21 label bits.  The finite-atlas theorem does not
suppress dimension-dependent cover growth.

## 8. Scope

This theorem constructs a quantitative plant-to-safe-closing bridge when
robust pointwise connector words, strict evaluator margins, a public labeling
rule, and memory reset are registered.  It does not prove that every object
described by the canonical phrase “normally hyperbolic, locally controllable
class” possesses those data.  That phrase still does not select a sensor
grammar, public belief semantics, uniform robust connector property, or
actuator dictionary.  Therefore v0.35 advances the sufficient formal class but
is not a full resolution of ASMP-4.
