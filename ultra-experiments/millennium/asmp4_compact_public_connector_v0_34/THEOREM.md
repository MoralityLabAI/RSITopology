# Compact public local-to-global connector theorem

## 1. Registered public information state

Fix the complete two-port architecture.  Its **public information state** `z`
contains exactly the information jointly registered at a block boundary: the
current public belief/reachable set and every sensor, controller, and actuator
memory value that must be synchronized before another block can start.  Hidden
plant state is not inserted for free.  If a private memory value is unknown,
`z` contains its reachable belief set rather than the value itself.

Let `Q_q` be a compact connected recurrent component of safe public states,
contained in the registered evaluator-safe core.  A local public connector
certificate on a relatively open set `U subset Q_q` consists of constants

`L_U`, `B_r,U`, and `B_w,U`

such that every ordered pair `z,z' in U` has a causal connector which:

1. remains inside the safe public component;
2. moves the public information state from `z` to `z'` in at most `L_U` steps;
3. realizes at most `B_r,U` read log-cost and `B_w,U` write log-cost; and
4. resets every registered private memory represented in `z'`.

The certificate is operational.  Ordinary controllability of a hidden plant
state does not imply it unless the sensor/controller/actuator architecture can
select the connector using only charged public information.

## 2. Finite safe subcover and overlap nerve

Assume every `z in Q_q` lies in some locally certified `U_z`.  Compactness gives
a finite subcover `U_1,...,U_m`.  Its **safe overlap nerve** has vertex `j` and
an edge `j-k` exactly when

`U_j intersection U_k intersection Q_q` is nonempty.

Because `Q_q` is connected, this finite nerve is connected.  Otherwise the
unions of the cover elements in two graph components, intersected with `Q_q`,
would be two disjoint nonempty relatively open sets covering `Q_q`, a
separation.

Define the coarse uniform bounds

`L_q = sum_j L_j`,

`B_r,q = sum_j B_r,j`, and `B_w,q = sum_j B_w,j`.

## 3. Local-to-global connector theorem

**Theorem 1.** Every ordered pair `z,z' in Q_q` has a safe public connector of
time at most `L_q` and cost at most `(B_r,q,B_w,q)`.

**Proof.** Choose cover vertices containing `z` and `z'`, then choose a simple
path between them in the connected nerve.  For every consecutive pair on the
path, select one public state in their safe overlap.  The first local
certificate connects `z` to the first overlap state; each intermediate local
certificate connects consecutive overlap states; the last connects to `z'`.
Every point used by one segment lies in that segment's cover element.  A simple
nerve path visits each cover vertex at most once, so summing the local time and
the two port costs is bounded componentwise by the displayed totals.  Every
segment is safe and the last resets the registered boundary memories.

The proof is constructive once a finite cover, overlap witnesses, and local
connector library are supplied.  A shortest nerve path can replace the coarse
sum by a sharper route-dependent vector bound.

## 4. Discharge of v0.33 safe closing

Fix a reset state `z_q in Q_q`.  Any safe prefix ending at `z in Q_q` can be
followed by Theorem 1's connector from `z` to `z_q`.  Thus every prefix is
closable with constant time overhead `L_q` and constant cost overhead
`(B_r,q,B_w,q)`.  Both are sublinear in the prefix horizon, so all v0.33
safe-closing hypotheses hold inside `q`.

Therefore the complete infinite-code region is

`R_q = closure(upward(conv(P_q)))`

and equivalently

`R_q = intersection_lambda`

`{(r,w):lambda r+(1-lambda)w >= h_q(lambda)}`.

Across irreversible components, the full closed region remains

`closure(union_q R_q)`.

This conclusion uses no finite exact quotient of the plant, belief dynamics,
or cost sequence.

## 5. Exact finite-horizon correction

For a safe prefix of length `T` and cost `(a_r,a_w)`, the closed block has
length at most `T+L_q` and cost at most

`(a_r+B_r,q, a_w+B_w,q)`.

Hence its exact coordinate rates are bounded by

`((a_r+B_r,q)/(T+L_q), (a_w+B_w,q)/(T+L_q))`

and, more coarsely, by

`(a_r/T+B_r,q/T, a_w/T+B_w,q/T)`.

The correction is vector-valued.  A free read connector does not erase a
positive write connector charge, or conversely.

## 6. Coordinate invariance

A registered causal conjugacy transports the public information state, safe
components, local cover, overlap witnesses, connector protocols, memories, and
transcript alphabets.  It therefore transports the finite nerve and preserves
all realized transcript counts.  The existence of local certificates, the
uniform connector conclusion, and the inherited v0.33 region are invariant
under such conjugacies.  An uncharged map from hidden state to public state is
not a conjugacy of the registered experiment.

## 7. Sharp boundaries

### Noncompact ladder

On `Q=N`, suppose each neighboring pair has a unit-cost local connector.  A
prefix ending at public state `T` needs return cost `T`; the overhead rate is
one.  Local connectors therefore do not imply uniform or sublinear closing
without compactness (or a separate uniform-return hypothesis).

### Disconnected or unsafe overlap

Disconnected cover nerves yield separate recurrent components, not one convex
region.  An intersection of ambient neighborhoods outside `Q_q` is not a safe
nerve edge: using it can leave the evaluator-safe set.

### Hidden mode

Two hidden modes require opposite first connector actions.  Each physical mode
is locally controllable, but no zero-read public policy is safe for both.  One
charged read bit resolves the mode and restores a connector.  This is why the
theorem is stated on public belief state rather than physical state.

### Private memory

A block that toggles an actuator-memory bit may be safe once and unsafe when
repeated.  The local certificate must return every registered memory to the
declared reset section; state return alone is insufficient.

## 8. Relation to normally hyperbolic control sets

Hyperbolic shadowing, complete approximate controllability, and local
accessibility are established routes to periodic or connecting trajectories.
For ASMP-4 they must additionally provide a uniform evaluator collar, a causal
public realization, finite two-port connector counts, and memory reset.  If a
formal normally hyperbolic registration supplies those local certificates on a
compact connected public core, Theorem 1 completes the global region formula.

The canonical prose does not currently specify that public-state implication.
Accordingly, this theorem closes the compact local-to-global step but does not
claim that ordinary hidden-state local controllability automatically satisfies
its hypotheses.
