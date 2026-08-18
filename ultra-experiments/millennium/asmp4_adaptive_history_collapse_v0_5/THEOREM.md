# Adaptive-history collapse for ASMP-4

## Status and scope

This successor keeps the exact four-plan plant, binary prefix interfaces,
three-tick block deadline, fixed control authority, and expected-read versus
worst-write costs of v0.4. It changes one scheduling quantifier that v0.4
explicitly froze: before the current plan is revealed, both ports may choose
the current code pair as a deterministic function of their **common decoded
history**.

There is no private schedule information, timing channel, shared random seed,
or lookahead. The plan in each block is independently distributed as

~~~text
p = (1/2, 1/4, 1/8, 1/8).
~~~

The current code pair is public once the common history is fixed. A strategy
over `n` blocks is therefore a finite decision tree whose outgoing edges are
the four decoded plans. Read cost is expected total input length. Write cost
is the maximum total output length over all `4^n` plan histories. Physical
time is `T=3n` ticks. Every block occupies exactly three public clock ticks;
early codeword completion never advances the next block and carries no free
timing information.

The result has two parts:

1. an exact Bellman characterization of every finite adaptive frontier; and
2. a constructive proof that logarithmic worst-write slack restores the
   coordinatewise lower corner asymptotically.

## 1. Complete deadline action universe

At one history node, an action is a causal read/write prefix-code pair. Write
words must finish by tick three. Read words longer than three add no useful
deadline information: causality and four distinct terminal write words imply
that the four read prefixes visible at tick three are distinct. Truncating a
longer read word to that visible prefix preserves every partition through the
deadline, preserves prefix-freeness, and weakly lowers read cost. It therefore
suffices to enumerate words of lengths one through three on both ports.

There are 207 unlabelled four-word binary prefix codes within that deadline
and 4,968 plan-labelled codebooks. Grouping them by the information partition
visible at each of ticks one, two, and three gives:

~~~text
27 reveal signatures
121 (read signature, expected-cost) keys
150 (write signature, length-vector) keys
72 causal read/write signature pairs
250 distinct actions (expected read, plan-specific write lengths).
~~~

Synchronous causality is exactly the condition that, at every tick, the read
information partition refines the write information partition.

**Theorem 1 (thirteen-action reduction).** Every one of the 250 deadline
actions is coordinatewise dominated by one of the following 13 actions:

~~~text
(7/4,  (1,2,3,3))
(15/8, (1,3,2,3))   (15/8, (1,3,3,2))
(2,    (2,1,3,3))   (2,    (2,2,2,2))
(9/4,  (2,3,1,3))   (9/4,  (2,3,3,1))
(19/8, (3,1,2,3))   (19/8, (3,1,3,2))
(5/2,  (3,2,1,3))   (5/2,  (3,2,3,1))
(21/8, (3,3,1,2))   (21/8, (3,3,2,1)).
~~~

Here the scalar is conditional expected read length and the vector lists
write lengths for plans zero through three.

**Proof.** The finite census applies the partition-refinement criterion to
every deadline codebook and retains the coordinatewise minima. If action
`a'` has no greater read cost and no greater write length on any plan than
action `a`, replace `a` by `a'` at the same decision-tree node and retain all
four continuation strategies. Conditional expected read does not increase,
and no pathwise write total increases. Repeating this replacement reduces any
adaptive strategy to the 13 listed actions. The harness stores a causal
codebook representative for every minimum. QED.

## 2. Exact finite adaptive frontier

Let `V_n(b)` be the minimum expected read total among common-history adaptive
strategies for `n` remaining blocks whose worst write total is at most the
integer budget `b`. Set `V_0(b)=0` for `b>=0` and `V_0(b)=infinity` otherwise.
For an action `a`, write `r(a)` for expected read cost and `w_i(a)` for the
write length on current plan `i`.

**Theorem 2 (Bellman frontier).** For every `n>=1`,

~~~text
V_n(b) = min_a [ r(a) + sum_i p_i V_{n-1}(b-w_i(a)) ],
~~~

where the minimum ranges over the 13 actions in Theorem 1 and a term with an
infeasible child budget is discarded. The upward closure of

~~~text
{(V_n(b),b) : 2n <= b <= 3n}
~~~

is the exact finite-horizon adaptive region.

**Proof.** Fix the root action. On plan `i`, every safe continuation receives
exactly the residual write budget `b-w_i(a)`. Common decoded history reveals
`i`, so the four child strategies may be optimized independently. Their
conditional read expectations average with weights `p_i`, giving the displayed
upper bound. Conversely, any strategy has one root action and four child
strategies satisfying those same residual budgets, so the expression is also
a lower bound. Theorem 1 makes the action reduction lossless. QED.

**Theorem 2A (exact guarded optimizer).** Write `b=2n+k`, where
`0<=k<=n`. The Bellman optimum uses the canonical Huffman action
`(7/4,(1,2,3,3))` at every history with positive residual slack and the
balanced action `(2,(2,2,2,2))` exactly when residual slack is zero.

Let `Y_t` be i.i.d. with values `-1,0,+1` and probabilities `1/2,1/4,1/4`,
let `S_t=sum_(j<=t)Y_j`, and let `tau_k` be the first time `S_t=k`, with
`tau_0=0`. Then the exact finite value is

~~~text
V_n(2n+k) = (7/4)n + (1/4) E[(n-tau_k)_+].
~~~

Equivalently, if

~~~text
D_n(k) = V_n(2n+k) - (7/4)n,
~~~

then `D_n(0)=n/4`, `D_n(k)=0` for `k>=n`, and for `1<=k<n`,

~~~text
D_n(k) = (1/2)D_(n-1)(k+1)
       + (1/4)D_(n-1)(k)
       + (1/4)D_(n-1)(k-1).
~~~

**Proof.** The 13 actions are the balanced profile and the 12 distinct
labellings of `(1,2,3,3)`. For an unbalanced action, put `y_i=w_i-2`, so the
values to assign to the four plan probabilities are `-1,0,+1,+1`. At residual
slack `k>0`, its current-plus-continuation objective differs by a constant from

~~~text
sum_i p_i [y_i + V_(n-1)(2(n-1)+k-y_i)].
~~~

Because `V_(n-1)` is nonincreasing in its budget, the bracketed function is
strictly increasing in `y_i`. The rearrangement inequality therefore assigns
`-1` to probability `1/2`, zero to `1/4`, and the two `+1` values to the two
`1/8` atoms: exactly the canonical Huffman labelling.

It remains to compare Huffman with balanced. Under the guarded policy, every
post-hit block costs `2-7/4=1/4` more expected read than Huffman, and the number
of post-hit blocks is `(n-tau_k)_+`, proving the displayed stopping-time value.
Choosing balanced immediately and then guarding for `n-1` blocks has excess

~~~text
(1/4)[1 + E[((n-1)-tau_k)_+]].
~~~

This is no smaller than the guarded Huffman excess because
`(n-tau_k)_+ <= 1+((n-1)-tau_k)_+`. At `k=0`, every unbalanced action has a
length-three branch and is infeasible, so balanced is forced. Induction on `n`
proves optimality; conditioning on the first increment gives the scalar
recurrence. QED.

The first four exact rows, ordered by write budget, are:

| blocks `n` | budgets `b` | exact `V_n(b)` |
| ---: | --- | --- |
| 1 | 2, 3 | `2, 7/4` |
| 2 | 4, 5, 6 | `4, 57/16, 7/2` |
| 3 | 6, 7, 8, 9 | `6, 345/64, 337/64, 21/4` |
| 4 | 8, 9, 10, 11, 12 | `8, 1851/256, 901/128, 1793/256, 7` |

The central harness evaluates all horizons through 12 blocks using exact
rational arithmetic. Every interior adaptive point strictly beats the
corresponding fixed public-schedule minimum.

### Smallest strict counterexample to fixed scheduling

For two blocks, use the Huffman identity relay first. After plan zero or one,
use Huffman again; after plan two or three, use balanced. All 16 histories are
safe, and

~~~text
expected read = 7/4 + (1/2+1/4)(7/4) + (1/8+1/8)2
              = 57/16,
worst write  = 5.
~~~

Every fixed two-block schedule with worst write at most five uses at most one
Huffman block and has expected read at least `15/4`. Adaptation gains exactly

~~~text
15/4 - 57/16 = 3/16.
~~~

Thus the v0.4 fixed-schedule line is exact under its stated restriction but is
not the full common-history adaptive frontier.

As a recurrence-independent check, the harness enumerates all
`13^5=371,293` two-block trees over the minimal action signatures. They induce
188 distinct aggregate cost points and exactly the three Pareto minima
`(7/2,6)`, `(57/16,5)`, and `(4,4)`; each minimum has one action-signature
realization.

## 3. The finite zero-slack obstruction

**Theorem 3 (exact finite corner remains excluded).** For every finite `n`,

~~~text
V_n(2n) = 2n.
~~~

**Proof.** Every four-word binary output code has a word of length at least
two. At any history, an adversary can choose such a plan and repeat this
choice recursively, so worst write is at least `2n`. If a root action has a
write word of length three, choosing that word and then a length-at-least-two
word at every child gives total at least `3+2(n-1)>2n`. Hence a strategy with
budget exactly `2n` must use four length-two output words at the root and,
inductively, at every reachable node. The v0.4 no-lag partition argument then
forces all four read lengths to be at least two at every node. Expected read
is at least `2n`, and the balanced identity relay attains equality. QED.

This is a finite-size obstruction, not an asymptotic rate obstruction.

## 4. Logarithmic-slack corner construction

Use only two identity relays:

~~~text
H: lengths (1,2,3,3), expected read 7/4;
B: lengths (2,2,2,2), expected read 2.
~~~

Fix an integer slack `k>=1`. Start with cumulative surplus `S_0=0`. Use `H`
until `S_t` first reaches `k`, updating

~~~text
S_{t+1} = S_t + length_H(theta_t) - 2.
~~~

After the first hit, use `B` forever. This schedule is a public deterministic
function of common decoded history. Before the hit, the surplus increment has
law

~~~text
-1 with probability 1/2,
 0 with probability 1/4,
+1 with probability 1/4.
~~~

Its mean is `-1/4`, and

~~~text
E[2^increment] = (1/2)(1/2) + (1/4)1 + (1/4)2 = 1.
~~~

Therefore, before stopping,

~~~text
M_t = 2^{S_t}
~~~

is a nonnegative martingale.

**Theorem 4 (adaptive asymptotic rectangle).** The guarded policy satisfies

~~~text
worst write <= 2n+k,
P(hit k by time n) <= 2^{-k},
expected read <= (7/4)n + n/(4*2^k).
~~~

With `k_n=ceil(log2 n)`, its rates converge to

~~~text
expected read per block -> 7/4,
worst write per block   -> 2.
~~~

Consequently, per physical tick, the exact closed adaptive asymptotic region
is

~~~text
[7/12,infinity) x [2/3,infinity).
~~~

**Proof.** An `H` step starts below `k` and increases surplus by at most one;
after the first hit, `B` leaves surplus unchanged. Thus `S_t<=k` on every
history and total write is at most `2n+k`. Doob's maximal inequality applied
to the stopped nonnegative martingale gives the hitting bound. A block costs
only `7/4` expected read before the hit and `2` after it, so relative to using
`H` throughout, the total excess is at most `(n/4)` times the hit indicator.
Taking expectations proves the read bound.

For `k_n=ceil(log2 n)`, the total read excess is at most `1/4`, while write
slack is `O(log n)=o(n)`. Universal source-coding lower bounds give expected
read at least `(7/4)n`: conditional on any past, the current plan retains law
`p` and has entropy `7/4`. Recursive selection of an output word of length at
least two gives worst write at least `2n`. The construction attains both lower
bounds in rate, and the usual upward closure gives the stated rectangle.
Dividing block totals by three converts to physical-tick rates. QED.

## 5. Every positive sorted four-plan law

The martingale construction is not special to the registered dyadic masses.
Let `p_1>=p_2>=p_3>=p_4>0`, and assign the unbalanced lengths `(1,2,3,3)` in
that probability order. As in v0.4, its expected length is

~~~text
E_H(p) = 3-2p_1-p_2.
~~~

It beats balanced exactly when `2p_1+p_2>1`. Put `q=p_3+p_4`. This strict-skew
condition is equivalent to `p_1>q`. For the surplus increment distribution
`(-1,0,+1)` with probabilities `(p_1,p_2,q)`, set

~~~text
lambda = p_1/(p_3+p_4) = p_1/q > 1.
~~~

Then

~~~text
E[lambda^increment]
  = p_1/lambda + p_2 + q lambda
  = q + p_2 + p_1
  = 1.
~~~

**Theorem 5 (general four-plan adaptive phase).** For every positive sorted
four-plan law, the closed common-history adaptive asymptotic region per block
is rectangular. Its lower corner is

~~~text
(E_H(p),2),  if 2p_1+p_2>1;
(2,2),       if 2p_1+p_2<=1.
~~~

Equivalently, the read threshold is `min{E_H(p),2}` and the write threshold is
two. Per tick, divide both coordinates by three.

**Proof.** In the strict-skew phase, the `lambda^{S_t}` martingale and the same
guard give

~~~text
P(hit k) <= lambda^{-k},
expected read <= E_H(p)n + (2-E_H(p))n lambda^{-k},
worst write <= 2n+k.
~~~

Choosing `k_n=ceil(log_lambda n)` makes total read excess bounded and write
slack logarithmic. The v0.4 four-leaf source-coding theorem gives the matching
read lower bound `E_H(p)n`, and recursive maximum-word selection gives the
write lower bound `2n`. If the skew inequality fails, balanced already
simultaneously attains both lower bounds `(2,2)` without adaptation. QED.

The harness checks the algebra on all 34 positive nonincreasing denominator-16
laws: 27 strict-skew, two boundary, and five balanced laws, with zero failures.
The independent verifier reproduces the same phase counts and martingale
identity.

## 6. Arbitrary finite i.i.d. plan alphabets

The guard does not depend on the special four-leaf tree. Let an i.i.d. source
have `m>=2` positive-probability plans. Let `mu` be the minimum expected length
of a binary prefix code for one plan, attained by a finite code `C` with
lengths `ell_i`. Define

~~~text
q=ceil(log2 m).
~~~

A fixed code `B` assigning every plan a distinct binary word of length `q`
exists, and no binary prefix code for `m` plans can have maximum length below
`q`.

**Theorem 6 (finite-i.i.d.-alphabet adaptive rectangle).** On a fixed public
block clock long enough for `C` and `B`, with expected read length, worst-history
write length, identity no-lag relays, and public common-history code selection,
the closed adaptive asymptotic region per block is

~~~text
[mu,infinity) x [q,infinity).
~~~

The clock duration `D` is an externally registered part of the instance, not a
rate-optimization variable. One fresh plan arrives per block. If physical-tick
rates are desired, both thresholds are divided by that fixed `D`; the v0.4
fixture is the special case `D=3`.

**Proof.** Conditional on every common past, the current plan has the same
i.i.d. law, so every selected read prefix code costs at least `mu` in
conditional expectation. Every selected write code has a word of length at
least `q`; recursively selecting such a word gives a history with write total
at least `qn`. These are universal lower bounds.

If an expected-optimal code `C` has maximum length at most `q`, use its identity
relay on every block and attain both bounds directly. Otherwise put

~~~text
Y = ell_C(Theta)-q,
y_max = max_i(ell_i-q) > 0.
~~~

If `mu=q`, the fixed code `B` already attains the corner. If `mu<q`, then
`E[Y]=mu-q<0`. For

~~~text
phi(lambda)=E[lambda^Y],
~~~

we have `phi(1)=1` and `phi'(1)=E[Y]<0`. Hence some `lambda>1` satisfies
`phi(lambda)<1`, and `lambda^{S_t}` for `S_t=sum_(j<=t)Y_j` is a nonnegative
supermartingale.

Fix an integer threshold `a>=1`. Use `C` while `S_t<a`; after the first step
with `S_t>=a`, use `B` forever. Immediately before a crossing, integer surplus
is at most `a-1`, so after it surplus is at most

~~~text
k = a+y_max-1.
~~~

It then stays fixed. Thus worst write is at most `qn+k`. Ville's inequality
gives crossing probability at most `lambda^{-a}`. Relative to using `C`
throughout, fallback increases expected read by at most `q-mu` per remaining
block, so

~~~text
expected read <= mu*n + (q-mu)n lambda^{-a}.
~~~

Choose `a_n=ceil(log_lambda n)`. Total expected-read excess stays bounded and
write slack `k_n=O(log n)=o(n)`. Both rates converge to the universal lower
bounds `(mu,q)`, proving the rectangle. QED.

The harness independently enumerates every full binary leaf-depth profile for
two through six plans and all 57 positive nonincreasing integer laws of total
mass 12. The profile counts are `1,1,2,3,5`. Ten laws use the fixed code because
`mu=q`, 21 attain the corner directly with an expected-optimal code of maximum
length at most `q`, and 26 require a guard. Every guarded cell finds an exact
rational `lambda>1` with `E[lambda^Y]<1`. The independent verifier rebuilds the
same profiles, laws, and `10/21/26` split.

## 7. A conditional-MGF criterion beyond i.i.d. sources

Let `F_(t-1)` be common decoded history for an exogenous finite-plan process.
Suppose a public causal identity-code policy `A`, chosen before the current
plan, has lengths `ell_t<=L`, asymptotic expected read rate `h`, and for some
integer baseline `q` and some `lambda>1` satisfies

~~~text
E[lambda^(ell_t-q) | F_(t-1)] <= 1
~~~

at every history. Assume a fixed-length identity fallback `B` of length `q`
is available. If `L<=q`, policy `A` already has worst write rate at most `q`,
so no guard is needed. The nontrivial guarded case below therefore has `L>q`.

**Theorem 7 (uniform conditional-MGF guard).** The guarded policy attains
expected read rate at most `h` and worst write rate at most `q`. If `h` is the
optimal expected-read threshold and `q` is the universal write lower bound,
the closed adaptive region is the rectangle

~~~text
[h,infinity) x [q,infinity).
~~~

**Proof.** While using `A`, put `S_t=sum_(j<=t)(ell_j-q)`. The conditional-MGF
assumption makes `lambda^{S_t}` a nonnegative supermartingale. Let
`y_max=L-q`, choose a threshold `a`, use `A` while `S_t<a`, and switch forever
to `B` after the first crossing. Exactly as in Theorem 6, pathwise surplus is
at most `a+y_max-1` in the nontrivial `L>q` case, and crossing probability is
at most `lambda^{-a}`.

Couple the guarded policy with an unguarded run of `A` on the same plan path.
They agree before crossing. On a crossing path, replacing all later `A`
codewords by length `q` changes total read by at most `qn` in the unfavorable
direction. Hence

~~~text
E[guarded read through n]
  <= E[A read through n] + qn lambda^{-a}.
~~~

With `a_n=ceil(log_lambda n)`, the additive read penalty is at most `q` and
write slack is `O(log n)`. Rate normalization gives `(h,q)`; matching lower
bounds give the rectangle. QED.

This criterion covers correlated sources when decoded history determines the
current conditional code. The harness includes a four-state Markov chain: from
state `s`, the next plans `(s,s+1,s+2,s+3) mod 4` have probabilities
`(1/2,1/4,1/8,1/8)`, and the Huffman labels rotate with the state. Thus
`P(next=0|state=0)=1/2` but `P(next=0|state=1)=1/8`, while every conditional
length MGF at `lambda=2` equals one. An exact 32-block state-distribution replay
matches the i.i.d. length-surplus process and its guard bound. The independent
verifier reproduces the Markov calculation.

## 8. A negative-drift guard without a uniform MGF

The exponential certificate is sufficient but not necessary. Let `A` be a
public causal identity-code policy with integer lengths `0<=ell_t<=L`, let a
fixed identity fallback of length `q` be available, and put

~~~text
S_t = sum_(j<=t)(ell_j-q).
~~~

Assume that for some `h<q`,

~~~text
S_t/t -> h-q < 0 almost surely.
~~~

No one-step conditional-MGF bound is assumed.

**Theorem 8 (vanishing-maximum guard).** Let `a_n` be any integer sequence
with `a_n->infinity` and `a_n=o(n)`. For the length-`n` policy, use `A` until
`S_t` first reaches `a_n`, then use the length-`q` fallback. Its rates satisfy

~~~text
worst write / n -> q,
expected read / n -> h.
~~~

If `h` is the expected-read lower threshold and `q` is the universal write
lower threshold, the closed adaptive region is

~~~text
[h,infinity) x [q,infinity).
~~~

**Proof.** If `L<=q`, policy `A` itself has the claimed write bound. Otherwise
put `y_max=L-q>0`. Negative almost-sure drift implies `S_t->-infinity`, so

~~~text
M = sup_(t>=1) S_t
~~~

is finite almost surely. Hence

~~~text
p_n = P(M>=a_n) -> 0.
~~~

Before a crossing the integer surplus is at most `a_n-1`; the crossing step
adds at most `y_max`; fallback then freezes the surplus. Thus

~~~text
worst write <= qn+a_n+y_max-1 = qn+o(n).
~~~

Couple guarded and unguarded runs on the same plan path. They agree before a
crossing, and replacing the remaining nonnegative `A` lengths by `q` can
increase read by at most `qn`. Therefore

~~~text
E[guarded read] <= E[A read] + qn p_n.
~~~

Because `S_t/t` is uniformly bounded by the length bounds, bounded convergence
gives `E[A read]/n->h`. Dividing the last display by `n` proves the read limit;
matching lower bounds give the rectangle. QED.

A stationary ergodic bounded length process with mean below `q` satisfies the
almost-sure premise by the ergodic theorem. More generally, independent
non-identically distributed bounded increments satisfy it whenever their
average means converge below zero, by the strong law for bounded centered
increments.

The harness registers an exact time-varying fixture showing that Theorem 8 is
strictly more permissive than Theorem 7. On even rounds use

~~~text
p^S = (1/2,1/4,1/8,1/8).
~~~

On odd round `2j+1`, put `epsilon_j=2^(-(j+4))` and use

~~~text
p^j = (3/8+epsilon_j/2, 1/4,
       3/16-epsilon_j/4, 3/16-epsilon_j/4).
~~~

Use Huffman lengths `(1,2,3,3)` on every round. Their surplus means are
`-1/4` on strong rounds and `-epsilon_j` on weak rounds, so the average surplus
converges to `-1/8` and expected read converges to `15/8`. The lengths are
conditionally expected-optimal: on every weak round
`2p_1+p_2=1+epsilon_j>1`, while the strong rounds are the canonical Huffman
law. The bounded independent-increment strong law supplies the almost-sure
premise of Theorem 8.

For a fixed `lambda>1`, the limiting weak-round conditional factor is

~~~text
f_0(lambda) = 3/(8lambda) + 1/4 + 3lambda/8 > 1.
~~~

The actual weak factor is

~~~text
f_j(lambda)
  = f_0(lambda) - (epsilon_j/2)(lambda-1/lambda)
  -> f_0(lambda)>1.
~~~

Thus every fixed multiplier eventually violates Theorem 7's one-step
condition. Nevertheless Theorem 8 with `a_n=ceil(sqrt(n))` proves the exact
closed per-block rectangle

~~~text
[15/8,infinity) x [2,infinity).
~~~

Central and independent exact rational propagations at horizons
`16,32,64,128` reproduce the decreasing guard-hit probabilities and the
coupling bound.

The separation does not depend on nonstationarity. Let the renewal-age state
`J_t` be the number of consecutive nonzero plans since the latest plan zero.
Conditional on `J_t=j`, use the law from the last fixture at round `j`: the
canonical strong law at even `j` and the `epsilon_((j-1)/2)` weak law at odd
`j`. After drawing plan `theta_t`, update

~~~text
J_(t+1) = 0       if theta_t=0,
J_(t+1) = J_t+1   otherwise.
~~~

Starting from `J_0=0`, the state is a deterministic function of common decoded
history. Starting from the stationary law defined below makes the joint source
strictly stationary; the same fixed Huffman code is used at every state, the
guard depends only on decoded lengths, and the first observed zero reveals the
age thereafter. Thus stationary initialization supplies no codebook side
information. Both initializations have the same asymptotic rates.

**Theorem 9 (stationary-ergodic MGF separator).** The renewal-age chain is
irreducible, aperiodic, and positive recurrent. Initialized in its unique
stationary law `pi`, it is a stationary ergodic finite-plan source. Its
conditional Huffman policy has stationary expected read threshold

~~~text
h_* = sum_(j>=0) pi_j E_j[ell_H] < 2,
~~~

but fails the uniform conditional-MGF hypothesis for every `lambda>1`.
Theorem 8 gives the closed adaptive per-block region

~~~text
[h_*,infinity) x [2,infinity).
~~~

**Proof.** Every state resets to zero with probability at least `3/8`, every
nonzero transition advances the age by one with positive probability, and
state zero has a self-loop of probability `1/2`. These facts give positive
recurrence, irreducibility, and aperiodicity. Put

~~~text
r_j = 1-P_j(theta=0),
w_0 = 1,
w_j = product_(i<j) r_i,
Z = sum_(j>=0) w_j.
~~~

Since `r_j<=5/8`, `Z<infinity`, and the stationary probabilities are
`pi_j=w_j/Z`. The Huffman surplus drift is `-1/4` at every even state and
`-epsilon_((j-1)/2)` at every odd state. It is strictly negative everywhere;
in particular `pi_0>0`, so the stationary mean drift `h_*-2` is negative.
The Markov ergodic theorem supplies Theorem 8's almost-sure premise from every
initial state.

Every conditional law obeys `2p_1+p_2>1`, so the displayed Huffman code is
conditionally expected-optimal. All state laws have the same probability
ordering and the same optimal code; therefore any posterior mixture before the
first observed reset has that code as an optimum as well. The weak-state MGF
factors approach the same strictly-superunit `f_0(lambda)` from the
time-varying fixture, proving failure
of every uniform multiplier. Conditional Huffman optimality gives the read
converse, and recursive maximum-word selection gives the write converse.
Theorem 8 supplies the matching construction. QED.

For an exact numerical certificate, truncate the stationary weights before
state `N`. The omitted weight is at most

~~~text
(8/3) w_N.
~~~

At `N=32`, central and independent rational calculations enclose the threshold
as

~~~text
1.8161864422 < h_* < 1.8161864463,
~~~

with tail weight below `2.0e-8`. This interval is evidence for the registered
fixture; the analytic recurrence and tail bound prove the infinite-state
claim.

## 10. Arbitrary stationary ergodic public predictors

Let the finite plan alphabet have size `m>=2` and put

~~~text
q = ceil(log2 m).
~~~

Let `(Z_t,Theta_t)` be a stationary ergodic process. Before `Theta_t` is
drawn, `Z_t` is an admitted common causal predictive state, and it is
sufficient for the full common history:

~~~text
P(Theta_t=i | full common history) = p_i(Z_t).
~~~

Assume every `p_i(z)>0`. Let `mu(z)` be the minimum expected binary prefix
length for `p(z)`, with a fixed deterministic tie-break among optimal codes,
and define

~~~text
h_H = E[mu(Z_0)].
~~~

The public block clock is fixed and long enough for binary Huffman codes with
`m` leaves and for a fixed `q`-bit code.

**Theorem 10 (stationary-ergodic public-predictor rectangle).** With expected
read length, worst-history write length, identity no-lag relays, and public
common-state code selection, the closed adaptive asymptotic region per source
block is

~~~text
[h_H,infinity) x [q,infinity).
~~~

**Proof.** There are finitely many labelled full binary tree shapes for `m`
leaves. Choose the first expected-optimal shape under a fixed ordering. This
is a measurable function of `p(z)`, and every selected Huffman code has maximum
length at most `m-1`. Its realized length

~~~text
ell_t = ell_(Z_t)(Theta_t)
~~~

is therefore a bounded stationary ergodic process. The ergodic theorem gives

~~~text
(1/n) sum_(t=1)^n ell_t -> E[ell_0] = h_H
~~~

almost surely. A fixed code with `m` distinct `q`-bit words exists, so
`mu(z)<=q` for every state and `h_H<=q`.

For the read converse, condition on the full common history. Any admissible
read prefix code must distinguish the current plans and has conditional
expected length at least `mu(Z_t)`. Averaging gives threshold `h_H`. For the
write converse, full support permits recursively selecting a current plan with
a maximum-length output word. Every `m`-word binary prefix code has such a word
of length at least `q`, so some allowed history costs at least `qn`.

If `h_H=q`, use the fixed `q`-bit identity code and attain both bounds. If
`h_H<q`, the Huffman length surplus satisfies Theorem 8's bounded negative
almost-sure drift premise; its vanishing-maximum guard attains `(h_H,q)`.
Upward closure proves the rectangle. QED.

The central and independent harnesses enumerate every full binary leaf-depth
profile through `m=8`. The counts are

~~~text
1,1,2,3,5,9,16,
~~~

the minimum worst depths equal `ceil(log2 m)`, and every Huffman depth is at
most `m-1`. Registered i.i.d., rotating Markov, renewal-age, and uniform
fixtures exercise respectively the negative-drift, uniform-MGF,
vanishing-maximum, and fixed-equality proof branches.

## 11. Variable support and the write mean-payoff game

Let `S` be a finite public predictor-state set. At state `s`, an enabled plan
set `I_s` of size at least two has a positive conditional law `p_s`, and plan
`i` deterministically moves the predictor to `f(s,i)`. Assume the enabled
transition graph is strongly connected. The resulting finite Markov source is
initialized in its stationary law.

At each state the write coder first selects a labelled binary prefix tree for
`I_s`; the worst-history player then selects an enabled plan and incurs its
codeword length before moving to `f(s,i)`. This is a finite perfect-information
mean-payoff game. Let

~~~text
rho = its minimax worst asymptotic average length.
~~~

Positional determinacy supplies a stationary deterministic write-code selector
`B(s)` attaining `rho`. Let `H(s)` be a conditionally expected-optimal Huffman
code and let

~~~text
h = sum_s pi_s sum_(i in I_s) p_s(i) ell_H(s,i),
b = sum_s pi_s sum_(i in I_s) p_s(i) ell_B(s,i).
~~~

Statewise Huffman optimality gives `h<=b`.

**Theorem 11 (finite-state variable-support rectangle).** Under the same
expected-read, worst-write, identity-relay, and fixed-clock conventions, the
closed adaptive asymptotic region per source block is

~~~text
[h,infinity) x [rho,infinity).
~~~

**Proof.** Any prefix code can have unary internal vertices contracted without
increasing a labelled word length. It is therefore enough to use labelled full
binary trees, of which there are finitely many at every state. The prefix-code
write problem is consequently the finite turn-based mean-payoff game above.
Memoryless determinacy gives the positional selector `B` and the converse
threshold `rho` against arbitrary history-dependent write policies.

For fixed `B`, its finite weighted graph has no cycle of mean above `rho`.
Deleting cycles from a path leaves a simple prefix of bounded length, so for
some finite constant `C_B`, every allowed history obeys

~~~text
sum_(t=1)^n ell_B(s_t,i_t) <= rho n + C_B.
~~~

The read converse follows statewise from conditional Huffman optimality and
averages to `h` under `pi`.

If `b=h`, use `B` on both ports. Its expected read is `h` and its worst write
rate is `rho`. If `b>h`, run `H` and define the bounded stationary ergodic
difference process

~~~text
Y_t = ell_H(s_t,i_t)-ell_B(s_t,i_t).
~~~

Its mean is `h-b<0`. Apply the vanishing-maximum guard to cumulative difference:
use `H` until its surplus over the reference `B` path reaches a diverging
sublinear threshold, then use `B`. The reference path bound and bounded
overshoot give worst write `rho n+o(n)`. The hit probability vanishes, while
switching the remaining bounded codewords to `B` changes expected read by at
most `O(n)` on the hit event. Thus expected read rate converges to `h`.
Together with the two converses and upward closure, this proves the rectangle.
QED.

The registered exact fixture has two alternating public states:

- state `A` has four plans with probabilities `(1/2,1/4,1/8,1/8)` and every
  plan moves to `B`; and
- state `B` has two plans with probabilities `(3/4,1/4)` and every plan moves
  to `A`.

There are 13 labelled full-tree write actions at `A` and one at `B`. The
balanced action has cycle mean `(2+1)/2=3/2`; all 12 Huffman-profile labellings
have worst cycle mean `(3+1)/2=2`. Hence `rho=3/2`. Conditional Huffman read is

~~~text
h = ((7/4)+1)/2 = 11/8,
~~~

and its mean difference from the balanced worst-optimal baseline is `-1/8`.
The guarded region is exactly

~~~text
[11/8,infinity) x [3/2,infinity).
~~~

Central and independent implementations enumerate all 13 policies and replay
a 64-block exact guard whose active rounds match the canonical i.i.d. guard.

A second exact fixture makes the cycle optimization and guard both
load-bearing. State `A` has plan probabilities `(1/4,1/2,1/8,1/8)`. Plan zero
self-loops at `A`; the other plans enter a two-step binary-state detour before
returning. The stationary state law is `(2/5,3/10,3/10)`. For an `A`-state
length vector `ell`, the competing cycle means are

~~~text
ell_0,
(ell_1+2)/3,
(ell_2+2)/3,
(ell_3+2)/3.
~~~

The 13-policy census has three policies of value `5/3`, four of value `2`, and
six of value `3`. The expected-optimal Huffman vector is `(2,1,3,3)`, while the
least-expected-cost worst-optimal vector is `(1,2,3,3)`. Thus the read and
write optimizers are genuinely different. Their stationary expected rates are
`13/10` and `7/5`, so the difference drift is `-1/10`; its conditional MGF at
`lambda=2` equals one. The exact guarded region is

~~~text
[13/10,infinity) x [5/3,infinity).
~~~

The policy census admits a direct two-sided Shapley certificate. In state order
`(A,B,C)`, set

~~~text
rho = 5/3,             v = (0,-4/3,-2/3).
~~~

At `A`, every available length vector `ell` has Bellman score

~~~text
max{ell_0+v_A, ell_1+v_B, ell_2+v_B, ell_3+v_B},
~~~

and the minimum of these 13 scores is `5/3=rho+v_A`. At `B` and `C`, the
forced-edge scores are respectively `1+v_C=1/3=rho+v_B` and
`1+v_A=1=rho+v_C`. For the selected baseline `(1,2,3,3)`, every edge score is
at most the corresponding `rho+v_s`. Conversely, after every action of an
arbitrary history-dependent coder, the adversary can choose an enabled edge
whose score is at least `rho+v_s`. Summing the edge inequalities telescopes:

~~~text
baseline path cost <= rho n + v(s_0)-v(s_n) <= rho n + 4/3,
worst path cost    >= rho n + v(s_0)-v(s_n) >= rho n - 4/3.
~~~

Thus `rho=5/3` is certified against arbitrary history dependence, not merely
against the 13 positional rows. The potential span is exactly `4/3`; at 64
blocks the baseline worst cost is `108`, attaining that excess above the
linear mean-payoff term. Central and independent state/surplus propagations
also verify the Doob hitting bound and guarded coupling with distinct fast and
baseline codes.

## 12. Consequence for the ASMP-4 boundary

The evidence now separates three quantifiers cleanly:

- one block has the exact nonrectangular Pareto pair from v0.4;
- repeated fixed public schedules have the exact v0.4 line segment; and
- repeated common-history adaptive schedules have a rectangular closed
  asymptotic region, even under different expected-read and worst-write costs.

The new mechanism is not another communication path. It is causal budget
banking: short high-probability Huffman outputs create pathwise slack, rare
long outputs spend it, and a public guard prevents every history from crossing
the worst-write budget. The sublinear slack disappears after rate
normalization.

This successor does not change the canonical v0.1 same-metric formulas or the
v0.3 shared-cost collapse theorem. It shows that heterogeneous cost orderings
alone are insufficient to sustain an asymptotic two-port tradeoff when the
architecture permits its natural common-history adaptation.

## 13. Scope firewall

The exact registered Bellman theorem depends on:

- i.i.d. current plans whose conditional law remains `p` after every history;
- expected read cost but worst-case write cost;
- a public deterministic schedule chosen before the current plan;
- a three-tick prefix deadline and charged codeword lengths; and
- asymptotic rates that permit `o(n)` additive slack.

The conditional-MGF theorem permits correlated exogenous plans under a uniform
exponential certificate. The vanishing-maximum theorem also permits bounded
nonstationary or ergodic length processes with a negative almost-sure surplus
rate, and Theorem 10 classifies stationary ergodic full-support sources with a
common sufficient predictor. Theorem 11 replaces the full-support worst
threshold by a finite positional mean-payoff value when support varies by
public predictor state. No rectangle is claimed for adversarial read cost,
endogenous plans, hidden or insufficient predictive state, infinite-state
variable-support mean-payoff games, length processes lacking either a uniform
MGF or negative-drift certificate, private/event-triggered schedules, zero
additive slack at every finite horizon, nonbinary communication alphabets, or
every heterogeneous metric. The finite Bellman theorem is exact for the
registered fixture; the guard arguments are the analytic certificates for its
asymptotic collapse.

Theorem 6 is a per-source-block coding statement on a fixed registered clock.
Allowing the designer to slow plan arrivals by increasing the block duration
would change the problem and is not an admitted way to reduce physical-time
rates.
