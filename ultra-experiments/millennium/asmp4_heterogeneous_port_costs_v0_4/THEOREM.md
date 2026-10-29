# Heterogeneous port-cost frontier for ASMP-4

## Status and scope

This note sharpens one boundary of the ASMP-4 metric-robust serial-collapse
theorem. It proves two complementary statements:

1. changing only the positive units used on the two ports cannot create a new
   tradeoff; and
2. genuinely different cost or risk functionals can create an unequal,
   nonrectangular frontier even when the architecture remains serial,
   no-side-channel, and closed under copying either admitted transcript tree
   onto both ports.

The second statement is a boundary result, not a counterexample to the frozen
ASMP-4 formula. The frozen formula charges both ports by the same worst-case
complete-transcript cardinality. The witness below deliberately charges
expected prefix length on the read port and worst-case prefix length on the
write port, as an explicitly registered heterogeneous successor problem.

## 1. Positive unit conversions preserve rectangularity

Let `J_T` be any common transcript-tree cost satisfying the bilateral
normal-form theorem in the v0.3 package. Write its scalar safe threshold as

~~~text
h_J = inf_C limsup_T J_T(L_q^C)/T,
~~~

which is independent of `q` in `{r,w}` by that theorem. Suppose the reported
port charges are

~~~text
J_(r,T)'(L) = a_r J_T(L) + e_(r,T)(L),
J_(w,T)'(L) = a_w J_T(L) + e_(w,T)(L),
~~~

where `a_r,a_w>0` and, uniformly over admitted safe transcript trees,

~~~text
sup_L |e_(q,T)(L)| / T -> 0.
~~~

**Theorem 1 (unit-rescaled collapse).** If `h_J` is finite, then

~~~text
closure(R_K') =
  [a_r h_J, infinity) x [a_w h_J, infinity).
~~~

If no finite-rate safe code exists, both regions are empty in the finite rate
plane.

**Proof.** Every safe code has base read and write rates at least `h_J`.
Positive scaling and the uniform sublinear errors give heterogeneous rates at
least `a_r h_J` and `a_w h_J`. Conversely, for every positive epsilon, the
v0.3 bilateral construction supplies one diagonal code with both base rates
below `h_J+epsilon`. Its heterogeneous rates approach the displayed lower
corner. Upward closure and then epsilon closure give the formula. QED.

At finite horizon, if both errors vanish exactly, the region is the rectangle
with thresholds `a_r h_(J,T)` and `a_w h_(J,T)`. Therefore numerical equality
of thresholds is not invariant to a change of units, but the normalized
identity is:

~~~text
h_r'/a_r = h_w'/a_w = h_J.
~~~

This corrects the overbroad phrase “different cost functions or units” in
v0.3. Positive unit conversion alone is harmless. A structural change needs
different orderings of candidate trees, a port-specific admissibility rule, or
another resource coordinate.

## 2. What bilateral copying implies for different costs

Let `J_r` and `J_w` now be arbitrary port-specific costs. Let `D_K` be the
class of safe diagonal relay codes: codes whose read and write transcript
trees are isomorphic at every horizon. Under both normal-form closures, every
read tree of an arbitrary safe code occurs as both trees of a member of `D_K`,
and the same is true of every write tree.

Define

~~~text
alpha = inf_(D in D_K) r^(J_r)(D),
beta  = inf_(D in D_K) r^(J_w)(D),

E_K = upward-closure closure of
      {(r^(J_r)(D), r^(J_w)(D)) : D in D_K}.
~~~

**Theorem 2 (heterogeneous diagonal sandwich).**

~~~text
E_K is a subset of closure(R_K^(J_r,J_w)),

closure(R_K^(J_r,J_w)) is a subset of
  [alpha,infinity) x [beta,infinity).
~~~

**Proof.** Every diagonal code is an admissible serial code, which proves the
first inclusion. For an arbitrary safe code, downstream normal form copies its
read tree onto both ports and upstream normal form copies its write tree onto
both ports. Its read cost is therefore at least `alpha`, and its write cost is
at least `beta`. QED.

The two inclusions need not meet. With one shared cost, a tree approaching the
single scalar infimum approaches both coordinates and v0.3 recovers the full
quadrant. With different costs, `alpha` and `beta` may be attained by different
safe trees. The missing lower corner is then a real multiobjective
factorization constraint, as the next exact game demonstrates.

If both port costs are monotone under every timing-admissible deterministic
causal factor map, every mixed code is dominated by a diagonal copy of its
safe control tree. In that additional case the full region equals the upward
closure of the cost pairs of safe control trees. This formula can still be
nonrectangular because different safe trees can minimize the two costs.

## 3. Four-plan synchronous prefix game

### Registered safe plant

Time is divided into public three-tick blocks. Before the disturbance for a
block is revealed, the registered code chooses arbitrary finite binary
prefix-free read and write codebooks for the four plans. The disturbance then
chooses a plan `theta` in `{0,1,2,3}`. The sensor observes
`theta`; neither the controller nor actuator does. At the block deadline, the
actuator must apply the corresponding one of four fixed terminal controls.
Wrong or missing control after tick three enters `BAD`, so a safe output
codebook must complete by that deadline. Intermediate communication symbols do
not change the physical state. Thus safety is universal over all four plans,
and control authority is identical for every codebook.

The plan law used only for the read-cost accounting is

~~~text
p = (1/2, 1/4, 1/8, 1/8).
~~~

Two extremal binary prefix shapes are

~~~text
H = {0, 10, 110, 111},
B = {00, 01, 10, 11}.
~~~

but the theorem does not restrict the code to these shapes. Every finite binary
prefix-free codebook and plan labelling is admitted. The controller is a
deterministic synchronous no-lag transducer. At tick `t`, its write prefix may
depend only on the read prefix visible through tick `t`. Completion of a
prefix-free word is visible. The actuator uses the chosen output decoder and
its original deadline. There is no analog value, correlated randomness,
controller-local plan information, or other side channel.

The read port is charged by expected completed prefix length under `p`. The
write port is charged by worst-case completed prefix length. These deliberately
different risk conventions are explicit.

### Exact causal-factor criterion

For input words `c_theta`, output words `d_theta`, a deterministic synchronous
transducer exists exactly when, for every tick `t`,

~~~text
c_theta restricted through t = c_phi restricted through t
implies
d_theta restricted through t = d_phi restricted through t.
~~~

Necessity is causality. For sufficiency, define the output prefix on each
realized input-prefix equivalence class; the implication makes this definition
single-valued and prefix-consistent.

At tick one the Huffman shape partitions the four plans into block sizes
`1+3`, while the balanced shape partitions them into `2+2`. An output-prefix
partition must be a coarsening of the input-prefix partition. Neither of these
two partitions coarsens the other, regardless of plan labelling. Hence neither
mixed direction is feasible. Identity relays make both matching directions
feasible.

Thus every admitted minimal tree can still be copied onto both ports: this
fixture retains bilateral copy closure. Rectangularity fails because the two
port costs select different diagonal trees, not because one of those trees
lacks a relay realization.

For the two extremal representative shapes, the exact exhaustive counts over
`24 x 24` labellings per format pair are

| Read format | Write format | Causal assignments |
| --- | --- | ---: |
| Huffman | Huffman | 48 |
| Huffman | balanced | 0 |
| balanced | Huffman | 0 |
| balanced | balanced | 192 |

The minimum expected Huffman length assigns the shortest words to the largest
probabilities and equals

~~~text
(1/2)1 + (1/4)2 + (1/8)3 + (1/8)3 = 7/4.
~~~

Every balanced assignment has expected length `2`. The exact Pareto points per
block are therefore

~~~text
(7/4, 3) and (2, 2).
~~~

The coordinatewise infimum `(7/4,2)` is not achievable.

### Unrestricted prefix-code theorem

**Theorem 3 (complete four-plan binary-prefix frontier).** Over all finite
binary prefix-free read and write codebooks, all plan labellings, and all
synchronous no-lag deterministic controller transducers meeting the
three-tick terminal deadline, the Pareto-minimal cost pairs are exactly

~~~text
(7/4,3) and (2,2).
~~~

**Proof.** For any binary prefix code with plan lengths `ell_i`, Kraft's
inequality and the Shannon lower bound give

~~~text
sum_i p_i ell_i >= H(p) = 7/4.
~~~

The Huffman shape has lengths `(1,2,3,3)=(-log2 p_i)_i`, so equality is
attained. Every binary prefix code for four plans has worst length at least
two, while safety requires write worst length at most three.

Suppose the write worst length is exactly two. Kraft's inequality then forces
all four write words to have length two, so their tick-one prefix partition has
block sizes `2+2`. Causality requires this output partition to be a coarsening
of the read tick-one partition. A binary read prefix has at most two nonempty
tick-one blocks; therefore feasibility forces its two blocks also to have
sizes `2+2` and to match the write partition up to relabelling. Neither read
block can contain a length-one word, because that word would prefix the other
word in the same block. Hence every read length is at least two and its
expected cost is at least two. The balanced identity relay attains `(2,2)`.

If the safe write worst length is three, the universal expected-read lower
bound gives a pair no better than `(7/4,3)`, which the Huffman identity relay
attains. Write codes longer than three miss the safety deadline. These cases
cover every candidate code and prove both optimality and completeness. QED.

The harness additionally enumerates every ordered full binary tree with four
leaves. There are five shapes, 120 plan-labelled codebooks, and 14,400 ordered
read/write pairs. Exactly 960 pairs are causal and all 3,840 plan-specific
terminal replays are safe. Their Pareto set is exactly the theorem's two
points. This census checks the tight full-tree cases; the proof above covers
arbitrary incomplete trees and unary slack as well.

### Probability phase and minimality

**Theorem 4 (four-plan skew-law phase).** Let
`p_1>=p_2>=p_3>=p_4>0` be any four-plan probability law. Under the same
binary-prefix and three-tick no-lag conventions, define

~~~text
E_H(p) = 3 - 2 p_1 - p_2.
~~~

If `2 p_1+p_2>1`, the exact Pareto minima are

~~~text
(E_H(p),3) and (2,2).
~~~

If `2 p_1+p_2<=1`, the balanced point `(2,2)` is the unique Pareto minimum.

**Proof.** An expected-length minimizer can be chosen as a full binary tree:
any unused unary edge can be contracted and strictly reduces the affected
lengths without violating prefix-freeness. A full binary tree with four leaves
has only two length profiles, `(2,2,2,2)` and `(1,2,3,3)`. The best labelling
of the latter assigns the shortest lengths to `p_1,p_2`, giving

~~~text
p_1 + 2p_2 + 3(p_3+p_4) = 3 - 2p_1 - p_2.
~~~

It beats balanced expected length two exactly when `2p_1+p_2>1`. The
write-length-two causal argument in Theorem 3 independently forces every read
length to be at least two, so the better unbalanced expected code cannot be
combined with write worst length two. If the inequality fails, balanced
simultaneously minimizes both objectives. QED.

Four plans are minimal for this phenomenon. With one or two plans the full
binary shape is unique. With three plans every full binary tree has length
profile `(1,2,2)`, so assigning length one to the most likely plan
simultaneously minimizes expected and worst length. The first competing full
profiles, balanced `(2,2,2,2)` and unbalanced `(1,2,3,3)`, appear at four
plans.

The harness checks Theorem 4 on all 34 positive nonincreasing integer laws with
denominator 16. It finds 27 strict-skew laws, two boundary laws, and five
balanced laws, with no discrepancy. A separate enumeration confirms frontier
sizes `1,1,1,2` for one through four plans under representative ordered laws.

## 4. Complete fixed-schedule repeated-block frontier

Freeze a public plant-independent codebook schedule. Theorem 3 shows that each
block using any finite binary prefix pair is dominated by either the Huffman
or balanced endpoint. If `k` of `n` blocks use the Huffman endpoint and the
rest use the balanced endpoint, additivity gives

~~~text
E[length_r] = (7/4)k + 2(n-k),
max length_w = 3k + 2(n-k).
~~~

Consequently every scheduled point satisfies

~~~text
4 E[length_r] + max length_w = 10n.
~~~

Conversely, identity relays attain both endpoints. Taking all fixed public
schedules and closure therefore yields the upward closure of the line segment
joining the two Pareto points. Per physical tick, the full registered
fixed-schedule frontier is

~~~text
upward-closure conv{(7/12,1), (2/3,2/3)},

R_w = 10/3 - 4 R_r
for 7/12 <= R_r <= 2/3.
~~~

This region is unequal and nonrectangular. Its coordinatewise lower corner
`(7/12,2/3)` is excluded. The obstruction is not a missing communication path;
it is the synchronous factorization deadline combined with two genuinely
different port-cost orderings.

**Successor scope note.** The v0.5 adaptive-history successor keeps this
one-block theorem unchanged but allows the next public code pair to depend on
common decoded history. It gives a strict two-block improvement and restores
the coordinatewise corner with logarithmic write slack. Thus this section is
complete for the fixed-schedule quantifier stated at its start, not for every
history-adaptive repeated-block strategy.

## 5. Consequence for the canonical ASMP-4 claim

The canonical v0.1 formulas use the same complete-transcript cardinality cost
on both ports. Theorem 1 shows that even positive port-specific unit scales
would preserve a rectangular frontier after normalization. The four-plan game
instead changes expected versus worst-case semantics and freezes a no-lag
prefix-decoder deadline. It therefore locates a successor boundary without
weakening the v0.3 negative resolution of the original symmetric premise.

The correct boundary statement is:

- positive rescaling of one common admitted tree cost preserves collapse;
- different costs that rank safe trees differently may create a Pareto
  frontier; and
- timing or syntax can prevent the controller from combining the separately
  cheapest read and write representations.
