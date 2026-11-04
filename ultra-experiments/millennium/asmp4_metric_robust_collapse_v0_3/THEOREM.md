# Metric-robust bilateral relay theorem for ASMP-4

## Status

This theorem strengthens the ASMP-4 v0.2 serial-collapse result and corrects
one over-identification in its interpretation.

The v0.1 canonical rate

~~~text
limsup_T log2 |M(T)| / T
~~~

counts the growth of complete realized transcript languages. For uncertain
systems, that quantity can be strictly smaller than the history-dependent
causal branching rate used by invariance feedback entropy. The diagonal
two-port conclusion nevertheless survives for either metric. Its robust reason
is not merely data processing; deterministic controller computation can be
moved in either direction across the serial architecture.

## 1. Transcript trees and two rate metrics

For a deterministic safe code C, let L_r^C(T) and L_w^C(T) be its realized read
and write words of length T. Their prefix closures are the corresponding
transcript trees.

The canonical ASMP-4 terminal-language cost is

~~~text
C_T(L) = log2 |L(T)|.
~~~

For a realized prefix p of length t, let deg_L(p) be the number of symbols that
can follow p in the tree. The history-dependent worst-path branching cost is

~~~text
B_T(L) =
  max_(ell in L(T)) sum_(t=0)^(T-1) log2 deg_L(ell restricted to [0,t)).
~~~

This is the finite-horizon form of the successor-symbol rate used in the
uncertain-system invariance-feedback data-rate theorem.

For the prefix-free worst-case variant mentioned by ASMP-4, define the exact
minimax binary length recursively on each realized prefix p:

~~~text
P_T(p) = 0                                      if p is a leaf,
P_T(p) = ceil(log2 sum_(a after p) 2^P_T(pa))  otherwise,
P_T(L) = P_T(empty prefix).
~~~

To see the recurrence, suppose a child subtree needs worst-case future length
c_a. A total bound q is feasible exactly when binary prefix lengths l_a can
satisfy l_a+c_a <= q. By Kraft's inequality this is possible exactly when

~~~text
sum_a 2^(-(q-c_a)) <= 1,
~~~

whose smallest integer solution is the displayed ceiling. Thus P_T is the
minimum worst-case cumulative binary prefix-code length, not an approximation.

**Lemma 1 (tree domination).** Every finite transcript tree satisfies

~~~text
C_T(L) <= B_T(L).
~~~

**Proof.** Induct on the tree depth. If the root has d nonempty child
subtrees with leaf counts n_1,...,n_d, the induction hypothesis gives a path
in child i with branch product at least n_i. Choose a largest child. The full
path product is at least d max_i n_i, which is at least sum_i n_i, the total
number of leaves. Taking logarithms proves the claim. QED.

The inequality can be exponentially loose. Section 4 gives an exact safety
game with T+1 terminal words but branch product 2^T.

**Lemma 2 (prefix lower bound).** Every binary prefix code for the terminal
words satisfies

~~~text
C_T(L) <= P_T(L).
~~~

This is the usual Kraft lower bound on worst-case length. There is no universal
ordering between B_T and P_T: the sequential-rounding tree and skew tree in
Section 4 give strict opposite three-way orderings.

More generally, let J_T be any port cost on realized prefix trees satisfying:

1. nonnegativity and symbol-relabel invariance;
2. deterministic-prefix invariance: inserting or deleting a fixed
   plant-independent prefix `p_d` obeys
   `J_(T+d)(p_d L)=J_T(L)`, or the absolute difference is `o(T)` uniformly
   over admitted trees for the asymptotic version;
3. the read and write ports use the same cost convention; and
4. a tree admitted on one port may be copied onto the other port.

C_T, B_T, and P_T all satisfy these requirements.

## 2. Bilateral relay normal forms

Use the deterministic noiseless serial architecture

~~~text
sensor -> controller -> actuator,
~~~

with plant-independent initialization, no controller or actuator side
information, arbitrary registered component memory/computation, fixed control
authority, and zero delay or timing-compatible fixed public FIFO delay.

**Theorem 1 (upstream normal form).** Every safe code C has a behaviorally
identical safe code U(C) whose read and write transcript trees are both
isomorphic to the original write tree:

~~~text
L_r^(U(C)) isomorphic to L_w^C,
L_w^(U(C)) isomorphic to L_w^C.
~~~

**Construction.** The sensor runs the original sensor and controller, emits
the original controller symbol on the read port, and the controller relays it.
The original actuator decoder is unchanged. With fixed FIFO read delay d, the
sensor computes the controller output for delivery event s+d at physical
emission time s; it has then generated every read symbol used at that event.
The plant-independent warm-up prefix is generated locally. This preserves
every actuator input and plant trajectory. QED.

**Theorem 2 (downstream normal form).** Every safe code C has a behaviorally
identical safe code D(C) whose read and write transcript trees are both
isomorphic to the original read tree:

~~~text
L_r^(D(C)) isomorphic to L_r^C,
L_w^(D(C)) isomorphic to L_r^C.
~~~

**Construction.** Keep the sensor unchanged. The controller becomes an
identity relay and forwards each read symbol on the write port. The actuator
simulates the original controller from that relayed read history and then runs
the original decoder. At the instant the original write symbol would have
reached the actuator, the new actuator has the same read prefix that generated
it, so it computes the same control. Fixed public write delay is unchanged.
Thus every plant trajectory and both transcript-tree isomorphisms follow. QED.

The downstream theorem is the missing robustness step in v0.2. A deterministic
causal map need not reduce every history-dependent branching cost pointwise,
because it may hide an early distinction and disclose it through several later
symbols. Bilateral normal forms avoid needing that false general
data-processing claim.

## 3. Complete region for every symmetric tree cost

For q in {r,w}, define the best safe q-port rate

~~~text
h_q^J(K_0,K) =
  inf_(infinite safe C) limsup_T J_T(L_q^C) / T.
~~~

The infimum is infinity if there is no finite-rate safe code.

Define the corresponding achievable region by

~~~text
R_K^J = {(R_r,R_w): some infinite safe code C has
  limsup_T J_T(L_r^C)/T <= R_r and
  limsup_T J_T(L_w^C)/T <= R_w}.
~~~

**Theorem 3 (metric-robust serial collapse).**

~~~text
h_r^J(K_0,K) = h_w^J(K_0,K) =: h_J(K_0,K),

closure(R_K^J) =
  [h_J(K_0,K), infinity) x [h_J(K_0,K), infinity).
~~~

If `h_J=infinity`, the displayed right-hand side means the empty region in the
finite-rate plane.

**Proof.** Apply upstream normal form to codes approaching h_w^J. The
transcript-tree isomorphisms, deterministic-prefix invariance, and relabel
invariance give
h_r^J <= h_w^J. Apply downstream normal form to codes approaching h_r^J to
obtain h_w^J <= h_r^J. Hence the two coordinate infima coincide.

Every safe code has each coordinate at least its corresponding infimum, proving
the quadrant converse. Conversely, choose a code within epsilon of either
coordinate infimum and apply the normal form that copies that cheaper tree onto
both ports. The resulting diagonal code has both rates below h_J+epsilon.
Upward closure and epsilon closure prove the region formula. QED.

At finite horizon, replace limsup rates by J_T costs. Under exact
deterministic-prefix invariance, if the finite minima are attained, the same
argument gives an exact diagonal quadrant. If only infima exist, it gives the
closure. The uniform `o(T)` alternative is sufficient only for the asymptotic
rate statement.

The entropy is coordinate invariant. A bijective state-coordinate conjugacy
that transports the plant, safe set, observation relation, and uncertainty
paths induces a bijection between safe codes without changing either
transcript tree. Hence it changes no J_T cost, coordinate infimum, or capacity
pair. An evaluator quotient is valid under the control-congruence and
observation-factor conditions stated in the v0.2 theorem; otherwise tangent
state can alter the transcript trees and may not be discarded.

For J=C, Theorem 3 contains the canonical v0.1 ASMP-4 rate formula proved in
v0.2. For J=B, it gives the same structural region with a generally larger
scalar entropy compatible with the history-dependent uncertain-system
data-rate theorem.

### One-sided normal-form criterion

**Theorem 4.** If the registered code class is closed under upstream normal
form, then

~~~text
h_r^J <= h_w^J.
~~~

If it is closed under downstream normal form, then

~~~text
h_w^J <= h_r^J.
~~~

If it is closed under both, equality follows as in Theorem 3.

**Proof.** Upstream copying turns every write-tree candidate into a read-tree
candidate of identical cost, so taking infima gives the first inequality.
Downstream copying gives the second. QED.

Neither one-sided inequality can be reversed without the missing closure.
Exact strict witnesses appear in Section 5 and in the metric harness.

## 4. Exact causal-metric separation

Consider the full-observation safety game with safe states WAIT, EVENT, DONE
and an unsafe state BAD. The required actions are:

- at WAIT, output 0; the disturbance chooses WAIT or EVENT next;
- at EVENT, output 1 and move to DONE; and
- at DONE, output 0 forever.

A wrong action enters BAD. Starting from WAIT or EVENT, the exact safe
length-T control language is

~~~text
L_T = {0^T} union {0^k 1 0^(T-k-1) : 0 <= k < T}.
~~~

Therefore

~~~text
|L_T| = T+1,
C_T(L_T)/T = log2(T+1)/T -> 0.
~~~

Along the all-zero path, however, both 0 and 1 remain possible after every
prefix, so

~~~text
B_T(L_T) = T,
B_T(L_T)/T = 1.
~~~

This is not a side channel or Monte Carlo artifact. It is an exact
no-side-channel uncertain safety game. It proves that terminal transcript
growth and causal transmission rate are different mathematical objects even
though Theorem 3 makes either object's two serial port thresholds equal.

The three registered metrics can also be pairwise numerically distinct.
Consider a depth-(d+1) tree whose root has three symbols. One child contains a
complete binary subtree of depth d; the other two have deterministic tails.
For d>=2,

~~~text
C_T = log2(2^d+2),
P_T = d+1,
B_T = d+log2(3),

C_T < P_T < B_T.
~~~

The metric harness checks this exact identity through d=12. The bilateral
normal forms preserve the complete tree, so Theorem 3 applies to each metric
without asserting that their scalar entropy values coincide.

The opposite strict ordering already occurs at depth two. Let the root have a
`heavy` child with three leaf symbols and a `light` child with one deterministic
leaf. There are four leaves, the worst branch product is `2*3=6`, and the
minimax prefix recurrence rounds first in the three-leaf child and then again
at the root:

~~~text
C_T = 2,
B_T = log2(6),
P_T = ceil(log2(2^2+2^0)) = 3,

C_T < B_T < P_T.
~~~

Together the skew and sequential-rounding trees prove that neither `B_T` nor
`P_T` universally dominates the other. The harness and independent verifier
recompute both strict orderings.

## 5. Boundaries

The collapse can fail when a normal-form copy is not admissible or when the
ports rank the same admitted trees by genuinely different cost functionals.
Examples are:

- different cost or risk functionals on the two ports;
- fixed port-specific peak alphabets or symbol syntax;
- computational restrictions that prevent upstream or downstream simulation;
- actuator-local or controller-local plant information;
- private or deadline-incompatible delivery state;
- noisy links with distinct reliability or anytime-capacity requirements; and
- restricted actuator decoder memory that cannot simulate the controller.

These are genuine additional resource coordinates. They should be registered
explicitly rather than inferred from two symmetric transcript-tree rates.

Two exact witnesses show that both strict threshold orderings are possible:

1. **Forced raw sensor, read above write.** Four fully observed initial modes
   are forced by the sensor grammar to use four distinct read symbols, while
   the safe action depends only on which of two mode pairs contains the state.
   The controller groups the four reads into two write/action symbols. The
   one-step branching costs are two read bits and one write bit. Upstream
   computation is forbidden by the fixed raw-sensor grammar.
2. **Fixed direct-action decoder, write above read.** At time zero the sensor
   observes which one of T possible event times, or no event, determines the
   required binary action schedule. It announces the T+1-way plan once, so its
   read-tree branch cost is log2(T+1). The controller remembers the plan and
   emits the binary comb action word. A fixed time-independent direct-action
   decoder cannot accept a plan symbol and replay it, so the write-tree branch
   cost is T. Downstream computation is forbidden by the decoder syntax.

Both witnesses keep the plant controls fixed. The strict gaps come from
registered computation/syntax restrictions, exactly the conditions absent
from the canonical arbitrary-computation architecture.

A positive conversion of units by itself is not a structural exception. If
the charges are `a_r J_T+o(T)` and `a_w J_T+o(T)` for positive constants and
one shared base cost, the region remains the rectangle with thresholds
`a_r h_J` and `a_w h_J`. The v0.4 heterogeneous-cost successor proves this and
gives an exact synchronous prefix game where expected read length versus
worst-case write length instead produces a nonrectangular frontier. Thus the
load-bearing distinction is a change in how candidate trees are ordered, not
the numerical units printed on the axes.

## 6. Prior-art boundary

Tomar, Rungger, and Zamani define a history-dependent successor-symbol rate and
prove it equals invariance feedback entropy for uncertain systems. They also
give an example where whole-language zero-error growth is zero although the
causal rate is one bit per step:

- https://arxiv.org/abs/1706.05242

Kawan and Delvenne obtain genuinely multidimensional rate regions for networks
of distinct controlled subsystems. That architecture has multiple information
owners and cannot be reduced by moving one deterministic serial computation:

- https://arxiv.org/abs/1409.6037

The repository-specific contribution here is the bilateral normal-form
diagnosis of the frozen ASMP-4 single serial chain. The individual ingredients
are classical data-processing, functional relay, and component-simulation
ideas; no claim of literature-level novelty is made without external review.
The diagnosis explains why this particular symmetric achieved-transcript
region collapses while true networked or side-informed architectures can
retain nonrectangular rate tradeoffs.
