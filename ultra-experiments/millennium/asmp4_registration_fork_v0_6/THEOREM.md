# Registration-dependent terminal-language regions for ASMP-4

## 1. Purpose and claim boundary

The canonical ASMP-4 statement optimizes over a “registered causal code” and
requires component memory, delays, and other architecture choices to be
explicit. It does not say whether registration always permits the sensor to
replace its observation by an arbitrary sufficient statistic, or whether a
sensor may instead be registered as a fixed raw transducer.

That distinction is load-bearing. This note gives one uncertain safety plant
with the same evaluator, control authority, noiseless serial channels, and
canonical complete-transcript cardinality metric under two sensor
registrations. Their exact rate regions differ.

This does not contradict the v0.3 bilateral relay theorem. Its computed-sensor
registration is closed under the upstream normal form; its raw-sensor
registration is not.

## 2. Exact uncertain safety fixture

The safe states are four modes `0,1,2,3`; `BAD` is unsafe. The action set is
`{0,1}`. At a safe mode `m`, the unique safe action is

~~~text
g(m) = floor(m/2).
~~~

After the correct action, the disturbance chooses any of the four next safe
modes. A wrong action enters `BAD`. The initial set and safe set are both the
four safe modes. The sensor observes the current mode before the action.

Thus every mode word in `{0,1,2,3}^T` is realized, and every required action
word in `{0,1}^T` is realized. There is no state-correlated initialization,
controller information, actuator information, randomness, timing variation,
or uncharged side channel.

The two registrations are:

1. **Computed sensor.** Any deterministic causal observation encoder is
   admitted. In particular, the sensor may emit `g(m)`.
2. **Forced raw sensor.** The sensor must emit an injective label of `m` at
   every step. The controller may still compute `g(m)` and the actuator has the
   same two controls.

Both ports are charged by the canonical finite cost `log2 |M_q(T)|`.

### Rational evaluator-transversal realization

The finite transition table is realized exactly inside the rational uncertain
plant

~~~text
n_(t+1) = (3/2)n_t + u_t - q(z_t),
z_(t+1) = w_t,
q(z) = (12+13z-z^3)/24,
~~~

where `z,w` range over `{-3,-1,1,3}` and evaluator safety is `n=0`. The
polynomial values are

~~~text
(q(-3),q(-1),q(1),q(3)) = (0,0,1,1).
~~~

Starting from `n=0`, the unique safe control is `u=q(z)`: the other registered
binary control sends the normal coordinate to `1` or `-1`. The uncontrolled
normal multiplier is `3/2`, the disturbance reset has tangent derivative zero,
and the normal input derivative is one. Thus the mode fork has an exact
unstable evaluator-normal, locally controllable realization rather than relying
only on an abstract transition table. The harness replays this realization in
exact rational arithmetic.

## 3. Complete partition certificate

**Lemma 1 (safe observation partitions).** A memoryless partition of the four
modes admits a safe one-step controller exactly when every partition cell is
contained in one fiber of `g`.

**Proof.** If a cell contains modes requiring both actions, the controller
receives the same symbol in those modes and must choose one action, which is
wrong for at least one mode. Conversely, if every cell fixes `g`, the
controller emits that action and is safe. QED.

There are 15 set partitions of four modes. Exactly four are safe. Their block
counts are `2,3,3,4`, and the unique coarsest safe partition is

~~~text
{{0,1},{2,3}}.
~~~

The central and independent harnesses enumerate all 15 partitions rather than
assuming this census.

**Lemma 1b (registry-lattice monotonicity).** Let `Gamma` be any subset of the
15 sensor partitions. If `Gamma` contains no safe partition, confinement is
infeasible. Otherwise let `kappa(Gamma)` be the minimum block count of a safe
partition in `Gamma`; its exact region is
`[log2 kappa(Gamma),infinity) x [1,infinity)`. If `Gamma` is contained in
`Delta`, then `kappa(Delta)<=kappa(Gamma)` whenever `Gamma` is feasible, so the
achievable region can only expand.

**Proof.** The exact corner is Theorem 4 with two required-action classes.
Taking a minimum over a superset cannot increase the minimum. QED.

There are 32,767 nonempty registries. Exactly 2,047 are infeasible; 16,384
have `kappa=2`, 12,288 have `kappa=3`, and 2,048 have `kappa=4`. Central and
independent implementations verify monotonicity on all 245,760 cover edges of
the complete 15-dimensional registry lattice, including 26,624 strict edges.
The raw-only registry is contained in the full computed registry, and their
`kappa` values are respectively four and two.

## 4. Exact finite and asymptotic regions

**Theorem 2 (computed-sensor region).** For every positive horizon `T`, the
complete finite budget region is

~~~text
B_read >= T,          B_write >= T.
~~~

Consequently its closed asymptotic rate region is

~~~text
[1,infinity) x [1,infinity).
~~~

**Converse.** All `2^T` required action words occur. A deterministic actuator
maps each realized write word to one action word, so `|M_write(T)|>=2^T`.
The controller’s write word is a deterministic image of its read word, so
`|M_read(T)|>=|M_write(T)|>=2^T`.

**Construction.** The sensor emits `g(m_t)`, the controller relays it, and the
actuator applies it. Both transcript languages are `{0,1}^T`. QED.

**Theorem 3 (forced-raw region).** For every positive horizon `T`, the complete
finite budget region is

~~~text
B_read >= 2T,         B_write >= T.
~~~

Consequently its closed asymptotic rate region is

~~~text
[2,infinity) x [1,infinity).
~~~

**Converse.** Every mode word occurs and the injective raw transducer preserves
it, so `|M_read(T)|=4^T`. The write lower bound is the same `2^T` required-action
argument as in Theorem 2.

**Construction.** Relay the raw mode on the read port, let the controller emit
`g(m_t)`, and let the actuator apply it. The read and write language sizes are
exactly `4^T` and `2^T`. QED.

The harness directly replays all `4^T` disturbance paths through `T=8` and the
rational continuous realization through `T=6`. The enumeration is regression
evidence; the displayed counting arguments prove the formulas for every
horizon.

## 5. General sensor-grammar variational formula

The fork extends to every finite full-reset mode plant. Let `X` be a finite
mode set, let `g:X->U` be the unique safe-action map, and write
`m=|g(X)|`. After every correct action, the disturbance may choose any next
mode in `X`. Let `Gamma` be the registered, history-independent collection of
sensor partitions permitted at every read node. A causal encoder may choose a
member of `Gamma` from public history.

Let `P` refine `g` when every cell of `P` lies within one fiber of `g`, and
define

~~~text
kappa(Gamma,g) = min{|P| : P in Gamma and P refines g}.
~~~

If the set is empty, put `kappa=infinity`.

**Theorem 4 (full-reset sensor-grammar region).** If `kappa` is finite, then at
every positive horizon `T` the exact region is

~~~text
B_read  >= T log2 kappa,
B_write >= T log2 m.
~~~

The closed asymptotic region is therefore

~~~text
[log2 kappa,infinity) x [log2 m,infinity).
~~~

If `kappa=infinity`, universal confinement is infeasible in the registered
grammar.

**Proof.** Fix any read history. Because the disturbance is a full reset, every
current mode in `X` remains possible after that history. A safe next sensor
partition must therefore refine `g`; otherwise one read cell contains modes
requiring different current actions. Every admitted safe partition has at
least `kappa` cells, so every read-tree node has at least `kappa` realized
children. Induction gives at least `kappa^T` complete read words even when the
partition is selected adaptively from history.

Every word in `g(X)^T` is a required action word. A deterministic actuator maps
one complete write word to one action word, so distinct required action words
need distinct write words and `|M_write(T)|>=m^T`.

For achievability, repeat a `kappa`-cell minimizing partition, map each cell to
its unique safe action, and transmit that action on the write port. This gives
exactly `kappa^T` read words and `m^T` write words. QED.

The central and independent implementations enumerate every action partition,
every sensor partition, and every refinement pair through five modes. The
numbers of safe action/sensor partition pairs are respectively
`1,3,12,60,358`; 340 threshold-grammar cells also reproduce
`kappa=max(m,q)` when registration requires at least `q` read cells.

**Corollary 4b (closed registry-lattice counting formula).** Suppose the
action fibers have sizes `n_1,...,n_m`, and let `B_n` be the `n`th Bell number.
The number of safe sensor partitions with exactly `k` cells is

~~~text
s_k = sum_(k_1+...+k_m=k) product_i S(n_i,k_i),
~~~

where `S(n,k)` is a Stirling number of the second kind. Put
`u=B_n-sum_k s_k`. Among all nonempty registries:

~~~text
infeasible count = 2^u-1,
exact-kappa count N_k = (2^s_k-1) 2^(u+sum_(j>k) s_j).
~~~

The number of strict inclusion-cover edges in the complete registry lattice is

~~~text
sum_k s_k 2^(u+sum_(j>k) s_j).
~~~

**Proof.** A safe partition is independently a partition of each action fiber,
which gives the Stirling convolution. An infeasible registry is a nonempty
subset of the `u` unsafe partitions. A registry has minimum safe block count
`k` exactly when it chooses no smaller safe partition, at least one of the
`s_k` partitions, and an arbitrary subset of unsafe and larger safe
partitions. A cover edge is strict exactly when its added `k`-cell partition
meets a registry containing no safe partition with at most `k` cells. QED.

Central and independent implementations verify this formula for all 18 action-
block shapes and all 75 action partitions through five modes. For the five-
mode shape `(2,3)`, `s_2,s_3,s_4,s_5=(1,4,4,1)` and the formula classifies all
`2^52` registries without enumerating them.

The computed four-mode branch is `Gamma=all partitions`, hence `kappa=m=2`.
The forced-raw branch has only the singleton partition, hence `kappa=4` and
`m=2`. Thus Theorems 2 and 3 are exact corollaries rather than isolated
counts.

## 6. Fixed transducers on constrained mode graphs

Full reset is not required when the sensor transducer is fixed. Let `G` be a
finite directed mode graph with no dead ends, let `I` be the nonempty initial
mode set, let `f:X->Y` be the forced sensor label, and let `g:X->U` be the
unique safe action. Write `L_f(T)` and `L_g(T)` for the length-`T` label
languages of graph paths starting in `I`.

For a sensor word prefix `y_0...y_t`, its subset-observer state is the set of
current modes reachable by a graph path with those labels. Call the observer
action-homogeneous when `g` is constant on every nonempty reachable observer
state.

**Theorem 5 (fixed-transducer graph region).** Universal confinement is
feasible exactly when the sensor subset observer is action-homogeneous. When it
is feasible, the exact finite region is

~~~text
B_read  >= log2 |L_f(T)|,
B_write >= log2 |L_g(T)|.
~~~

With

~~~text
h_f = limsup_T log2 |L_f(T)|/T,
h_g = limsup_T log2 |L_g(T)|/T,
~~~

the closed asymptotic region is

~~~text
[h_f,infinity) x [h_g,infinity).
~~~

**Proof.** If a reachable sensor belief contains modes with different required
actions, those modes have the same entire read history and the deterministic
controller must choose the same current write behavior for both. It fails on
at least one path. Conversely, homogeneity lets the controller recover the
unique current action from its observer state and apply it.

The forced transducer realizes exactly `L_f(T)`, giving the read equality and
lower bound. Every word in `L_g(T)` is a required action word. A deterministic
actuator maps each complete write word to one complete action word, so at least
`|L_g(T)|` write words are necessary. Emitting the recovered action itself
attains equality. Taking limsups proves the asymptotic rectangle. QED.

Both entropies have a finite spectral computation. Determinize the labeled
graph: its states are the reachable nonempty mode subsets, and its transition
on label `y` maps belief `B` to

~~~text
successors(B) intersect f^(-1)(y).
~~~

Give the deterministic adjacency entry the number of labels producing that
edge. The number of accepted label words is the corresponding path count, so
standard finite Perron-Frobenius growth gives `h_f=log2 rho(A_f)` on the
reachable automaton, and similarly `h_g=log2 rho(A_g)`.

The exhaustive audit covers every nonblocking graph, nonempty initial set,
sensor partition, and action partition through three modes: 60,134
transducer/action cases, of which 37,430 are causally feasible. Exact subset-
observer counts match direct state-path expansion in all 12,060 language
comparisons.

**Proposition 5b (exact finite/infinite separation).** Take

~~~text
0->{1}, 1->{2}, 2->{0,1},    I={0},
f^(-1)(*)={0,1,2},           g^(-1)(0)={0,1}, g^(-1)(1)={2}.
~~~

The constant sensor is safe for every horizon `T<=4` with one read word, but
is infeasible for every `T>=5` and is not infinitely viable.

**Proof.** The successive pre-action observer beliefs are
`{0},{1},{2},{0,1},{1,2}`. The first four are action-homogeneous; `{1,2}` is
not. With a constant transducer there is no alternative observation or policy,
so `V_T(I)=1` through four and `V_T(I)=infinity` thereafter. QED.

An independent first-failure census over all 60,134 fixed-transducer cases
through three modes finds 37,430 infinitely safe cases. The remaining cases
first fail at horizons one through five with exact histogram
`10642,8406,3110,534,12`; no case has a longer finite-safe prefix. The 12
maximal-delay cases are exactly the singleton-grammar transient cases exposed
by the full adaptive lattice.

An exact constrained fixture is the golden-mean graph

~~~text
0 -> {0,1},          1 -> {0}.
~~~

With a forced raw sensor and one constant safe action, the read-language counts
are `F_(T+2)`, the write-language count is one, and the deterministic adjacency
has characteristic polynomial `lambda^2-lambda-1`. Hence

~~~text
h_f = log2 phi,       h_g = 0,
region = [log2 phi,infinity) x [0,infinity),
phi = (1+sqrt(5))/2.
~~~

Allowing the sensor to emit the constant sufficient statistic instead gives
the zero-rate corner. This constrained-dynamics fork cannot be reduced to an
i.i.d. full-reset count.

## 7. Adaptive sensor grammars on constrained graphs

The fixed-transducer theorem extends at finite horizon when registration
admits a collection `Gamma` of sensor partitions and lets the sensor select a
partition from the public read history. At a pre-read belief `B`, a choice
`P in Gamma` has the nonempty cells `C=B intersect D`, where `D` ranges over
the blocks of `P`. Call the choice safe when `g` is constant on every such
cell, and put

~~~text
Succ(C) = union of G(x) over x in C.
~~~

Define `V_0(B)=1`, and use `V_t(B)=infinity` when no safe continuation of
length `t` exists.

**Theorem 6 (adaptive sensor-grammar entropy-game formula).** For every finite
horizon, the minimum number of complete read words from belief `B` obeys

~~~text
V_(t+1)(B) = min over safe P in Gamma of
             sum over nonempty cells C of P on B of V_t(Succ(C)).
~~~

If `V_T(I)` is finite, the exact finite budget region is

~~~text
B_read  >= log2 V_T(I),
B_write >= log2 |L_g(T)|.
~~~

If `V_T(I)=infinity`, universal confinement is infeasible at horizon `T`.

**Proof.** Once the public history fixes `B`, the registered sensor must choose
one partition before learning which cell contains the current mode. Safety
requires each realized cell to determine the current action. The cell symbols
are distinct children of the current read-tree node, and after cell `C` the
next pre-read belief is exactly `Succ(C)`. Therefore the sizes of the child
languages add, and the Bellman principle gives the displayed recurrence.
Induction also constructs a horizon-optimal causal tree.

Every required action word still needs a distinct complete write word. The
safe read history determines the required action at every step, so emitting
that action attains exactly `|L_g(T)|` write words without increasing the
read language. This proves both bounds and their joint achievability. QED.

There is also an exact infinite-horizon formula. Start with all nonempty
beliefs and repeatedly delete any belief `B` for which no safe partition has
all of its successor beliefs still present. Let `K_infinity` be the stabilized
greatest viable set. It is reached after at most `N` deletions, where `N` is
the number of nonempty beliefs. An infinite safe grammar policy exists from
`I` exactly when `I in K_infinity`.

For a stationary viable belief policy `pi`, define its nonnegative integer
matrix, indexed by `K_infinity`, by

~~~text
A_pi[B,B'] = number of cells C selected at B with Succ(C)=B'.
~~~

Let

~~~text
rho_I(pi) = limsup_T (e_I^T A_pi^T 1)^(1/T),
rho_I     = min over stationary viable pi of rho_I(pi),
h_g       = limsup_T log2 |L_g(T)| / T.
~~~

Then the finite values have the limit

~~~text
lim_T V_T(I)^(1/T) = rho_I,
~~~

and the exact closed asymptotic region for infinite safe codes in this
registered grammar is

~~~text
[log2 rho_I,infinity) x [h_g,infinity).
~~~

In particular, a stationary belief policy attains the optimal read rate.

**Asymptotic proof.** Let `W_T` be the same Bellman value after restricting
every choice to the viable set. A length-`T` policy cannot leave that set more
than `N` steps before its horizon, while every viable policy is also a finite
policy. Consequently, for all sufficiently large `T`,

~~~text
W_(T-N)(I) <= V_T(I) <= W_T(I).
~~~

The viable recursion is a one-player extended entropy game with prescribed
initial state: beliefs are game states, registered partitions are the
minimizer's actions, cells are nondeterministic branches, and coincident
successor beliefs give the integer transition weights in `A_pi`. The prescribed-
initial-state operator theorem of Akian, Gaubert, Grand-Clément, and Guillaud
proves both positional optimality and
`lim_T W_T(I)^(1/T)=min_pi rho_I(pi)`; see Theorems 2 and 3 of
[The Operator Approach to Entropy Games](https://drops.dagstuhl.de/opus/volltexte/2017/7026/pdf/LIPIcs-STACS-2017-6.pdf).
The sandwich transfers that limit to `V_T`.

Every infinite safe read language must have rate at least `log2 rho_I`, and
every write language must have rate at least `h_g`. The optimal stationary
belief policy, coupled with emission of the uniquely determined current
action, attains both bounds in one infinite code. Upward and topological
closure give the rectangle. QED.

The following fixture shows that history adaptation can improve entropy
strictly.

Let

~~~text
0 -> {0,1},          1 -> {0,2},          2 -> {0,1},
I = {0,2},           g^(-1)(0)={0,2},     g^(-1)(1)={1},
P_0 = {{0,1,2}},     P_1 = {{0},{1,2}}.
~~~

This graph is strongly connected and aperiodic (it has the self-loop `0->0`).
Write `A={0,2}` and `B={0,1}`. At `A`, select the constant partition `P_0`,
which is safe and has successor belief `B`. At `B`, select `P_1`; its two
cells have successor beliefs `B` and `A`. This is one stationary belief policy,
and its exact Bellman recurrence is

~~~text
(V_(t+1)(A),V_(t+1)(B))^T
    = [[0,1],[1,1]] (V_t(A),V_t(B))^T,
(V_0(A),V_0(B)) = (1,1).
~~~

Equivalently, the matrix is `[[0,1],[1,1]]`, so
`V_T(A)=F_(T+1)`. The required-action language has the same Fibonacci counts.
Thus the stationary adaptive policy has the exact closed asymptotic region

~~~text
[log2 phi,infinity) x [log2 phi,infinity).
~~~

The fixed constant partition is infeasible after reaching `B`. The only
feasible fixed member of the grammar is `P_1`, and it realizes every binary
read word, hence `2^T` read words. The best fixed-grammar region is therefore

~~~text
[1,infinity) x [log2 phi,infinity).
~~~

This is a strict asymptotic registration gap on a strongly connected and
aperiodic graph, not a transient or periodic artifact.

The central and import-independent implementations also exhaust all 120,050
three-mode cases formed from a nonblocking graph, nonempty initial set,
required-action partition, and two distinct registered sensor partitions at
horizon four. They agree on 99,524 adaptively feasible cases, 97,952 cases with
a feasible fixed grammar member, 1,572 adaptive-only feasible cases, and 4,863
cases where adaptation is strictly cheaper than the best fixed member. In
73,223 cases the adaptive read language attains the required-action lower
bound. No case violates that lower bound or the fact that adaptation can
imitate a feasible fixed member. The largest finite fixed/adaptive language-
size ratio is eight. Greatest-fixed-point iteration shows that all 99,524
finite-feasible cases are infinitely viable; there are no horizon-four-only
false positives in this complete two-partition three-mode universe.

**Corollary 6b (adaptive grammar-lattice monotonicity).** If registered grammar
`Gamma` is contained in `Delta`, then for every belief and horizon,
`V_T^Delta(B)<=V_T^Gamma(B)`, and the infinite viable belief set for `Gamma` is
contained in that for `Delta`.

**Proof.** At each Bellman update, `Delta` minimizes over a superset of the
safe partition choices available to `Gamma`; induction from `V_0=1` gives the
finite inequality. Every viable `Gamma` choice is also a `Delta` choice, so
greatest-fixed-point iteration gives viable-set inclusion. QED.

Central and independent implementations verify this corollary over the
complete five-partition grammar lattice for every three-mode nonblocking
graph, nonempty initial set, and action partition: 372,155 nonempty grammar
cases and 960,400 inclusion-cover edges. There are 320,930 horizon-four
feasible cases, 320,918 infinitely viable cases, 138,546 feasibility-gain
edges, 138,582 viability-gain edges, and 104,556 strict finite-value edges.
The maximum one-edge finite language ratio is 81. The 12 finite-only cases are
all singleton grammars; each is safe through horizon four and first fails at
horizon five. Thus they are explicitly separated from the zero-transient
two-partition result above.

## 8. Canonical scope consequence

The plant, evaluator, uncertainty, control set, component separation, and rate
functional do not determine one region until the sensor grammar is also
fixed. In particular, the phrase “registered causal code” has two materially
different readings here:

- if arbitrary sensor computation is part of code design, bilateral normal
  forms give the diagonal region; but
- if registration may freeze a raw sensor transducer, upstream copying is
  inadmissible and the exact thresholds are unequal.

The raw fixture is not evidence against the conditional v0.3 theorem: it
violates that theorem’s explicit code-class closure premise. It is evidence
against promoting that conditional theorem to a registration-independent
resolution of the broader canonical wording.

Both registrations remain closed under the downstream normal form, because the
actuator may simulate the mode-to-action map after the raw or computed read
symbol is relayed. The v0.3 one-sided criterion therefore correctly predicts
`h_write<=h_read` in both branches. Only the reverse inequality fails in the
raw branch.

Accordingly, the strongest internally justified status is:

- exact diagonal characterization for normal-form-closed serial classes;
- exact unequal characterization for the registered raw class above; and
- no unique canonical region until the admissible registration grammar is
  specified or a theorem parameterized by that grammar is requested.

This scope conclusion is machine-checked against the canonical source rather
than inferred from the word “registered” alone. Eight explicit clauses bind
the causal sensor, component separation, explicit architecture, registered
class, and architecture-dependent tradeoffs. Neither upstream sufficient-
statistic closure nor forced raw transduction appears. Both exact fixture
registrations satisfy the same eight obligations while their regions differ.

The stronger model-completion certificate extracts 13 obligations from the
full canonical setting, including finite charged transcripts, port-only
communication, component separation, absence of side channels, explicit
memory and delay, existential code choice, universal disturbance safety, and
the bounded normally-hyperbolic class. Both registries instantiate concrete
sensor/controller/actuator maps satisfying all 13 obligations, and independent
complete-language replay derives their respective corners. Hence these are two
models of the written source with different values of the existential region,
not two unchecked interpretations attached after the fact.

Finally, the ambiguity is not repaired elsewhere in the candidate set. Across
the entire normative Markdown, `registered` occurs 31 times but no sentence
defines the causal-code domain or grants all causal encoders admission. The
machine-readable index is explicitly non-normative, names the Markdown as the
normative statement, marks the candidate set as an ungraduated definition
draft, and gives ASMP-4 no registry or sensor-grammar field. This global audit
therefore preserves the two-model conclusion.

## 9. What remains outside this result

This finite-mode fork is an architecture-boundary theorem, not a closed-form
entropy for every normally hyperbolic nonlinear plant. It does not address
noisy channels, probabilistic safety, private schedules, computational
complexity, or heterogeneous port metrics. Its role is narrower and decisive:
it turns one previously external scope question into an exact mathematical
fork, so further enumeration inside either branch cannot choose between the
branches.
