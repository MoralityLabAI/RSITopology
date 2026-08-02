# ASMP-4 v0.7 relational-action frontier theorem

## 1. Registered uncertain plant

Let the safe modes be `X={0,1,2,3}` and the registered controls be
`U={a,d,e}`.  The safe-action correspondence is

~~~text
S(0)={a,d},   S(1)={a,e},   S(2)={d},   S(3)={e}.
~~~

After every safe action the disturbance may select any next mode in `X`; an
action outside `S(x)` enters `BAD`.  The initial and evaluator-safe mode sets
are both `X`.  The sensor observes the current mode before the action.  Thus
the uncertainty is a full adversarial reset, but the safe control is no longer
unique.

The registered sensor grammar contains exactly

~~~text
P_c = {{0,1},{2},{3}},
P_r = {{0},{1},{2},{3}}.
~~~

At every read node the sensor may select either partition using arbitrary
public read-history adaptation.  The controller receives only the emitted
cell label and selects an action safe for every mode in that cell.  There is no
state-correlated initialization, analog side channel, or uncharged plant
information.  Complete read and write transcript languages are charged by
their base-two log cardinalities.

For `P_c`, the three cells force actions `a,d,e`, giving local count pair
`(3,3)`.  For `P_r`, there are four safe controllers.  The assignment
`(d,e,d,e)` uses two actions and gives `(4,2)`; the other three assignments use
three actions and give `(4,3)`.  Hence the nondominated local pairs are

~~~text
(3,3), (4,2).
~~~

## 2. Finite-horizon multiplicity representation

Fix a deterministic safe code tree of remaining horizon `T` and first quotient
each write transcript by its decoded action word.  For each decoded action word
`w`, let `c_w` be the number of complete read words mapped to `w`.  Put

~~~text
R_T = sum_w c_w,
W_T = |{w:c_w>0}|.
~~~

Here `R_T` is exactly the read-language cardinality, while `W_T` is the decoded
action-language cardinality and is no larger than the charged write-language
cardinality.  A lower bound using this quotient is therefore also a write-port
converse.  At a coarse node, the child multiplicity vectors are placed under the three
distinct action prefixes `a,d,e`.  At a raw node, vectors whose cells receive
the same action are added coordinatewise before being placed under that
action prefix.  This representation therefore includes every registered
history-adaptive code tree; it is not a fixed-schedule relaxation.

Let

~~~text
theta = log2(3/2),       so 0<theta<1 and 2^theta=3/2,
Phi_theta(c)=sum_w c_w^theta.
~~~

**Lemma 1 (local concave-moment growth).** Every registered local scheme
multiplies the minimum possible `Phi_theta` by at least three.

**Proof.** For nonnegative `x_1,...,x_k`, concavity gives

~~~text
(x_1+...+x_k)^theta >= k^(theta-1) sum_i x_i^theta.
~~~

If each child has moment at least `Q`, an action receiving `k` sensor cells
therefore contributes at least `k^theta Q`.  The action multiplicities of the
five safe schemes are

~~~text
(1,1,1),  (2,2),  (2,1,1),  (2,1,1),  (2,1,1).
~~~

Their factors are respectively

~~~text
3,  2*2^theta=3,  2^theta+2=7/2,  7/2,  7/2.
~~~

All are at least three. QED.

**Lemma 2 (coordinate growth).** Every safe registered horizon-`T` tree has
`R_T>=3^T` and `W_T>=2^T`.

**Proof.** Every local sensor has at least three realized cells, so the read
tree has at least three children per node.  Every safe local controller uses
at least two distinct action prefixes.  Under each such prefix, the union of
one or more child write languages has at least the size of one child language.
Induction gives the two bounds. QED.

**Theorem 3 (exact finite relational converse).** Every safe registered code
of positive horizon `T` satisfies

~~~text
R_T >= 3^T,
W_T >= 2^T,
R_T^theta W_T^(1-theta) >= 3^T.
~~~

**Proof.** Starting from `Phi_theta((1))=1`, Lemma 1 gives
`Phi_theta(c)>=3^T`.  Since `x^theta` is concave, Jensen's inequality gives

~~~text
Phi_theta(c) <= W_T (R_T/W_T)^theta
             = R_T^theta W_T^(1-theta).
~~~

Combine the inequalities with Lemma 2. QED.

This converse covers node-by-node choices based on the complete public read
history and arbitrary safe controller assignments.  It does not infer an
infinite theorem from a truncated census.

## 3. Exact asymptotic region

Write `L=log2 3`.  Since `theta=L-1`, dividing Theorem 3 by `T` and taking
limsup yields

~~~text
r_read >= log2 3,
r_write >= 1,
theta r_read + (1-theta) r_write >= log2 3.
~~~

**Theorem 4 (complete nonrectangular region).** The three displayed
inequalities define the exact closed achievable region of the registered
history-adaptive grammar.

**Proof.** The converse is Theorem 3.  For achievability, choose a public
schedule with `k` coarse steps and `T-k` raw steps, using `(a,d,e)` at each
coarse step and `(d,e,d,e)` at each raw step.  Full reset realizes exactly

~~~text
R_T = 3^k 4^(T-k),
W_T = 3^k 2^(T-k).
~~~

Every such point saturates the joint inequality because
`4^theta 2^(1-theta)=2^(1+theta)=3`.  Schedules with asymptotic coarse-step
frequency `lambda` fill the segment between

~~~text
(log2 3,log2 3) and (2,1).
~~~

Taking the upward closure gives exactly the three-inequality region. QED.

The coordinatewise lower corner `(log2 3,1)` violates the joint inequality.
Consequently the region is genuinely nonrectangular; the tradeoff is not a
finite-horizon scheduling artifact.

## 4. Exact bounded adaptive census

The central harness represents each write language as an integer support mask
and prunes a subtree only when another has no more read leaves and a subset of
its write language.  The import-independent verifier constructs explicit sets
of action words.  Both enumerate every safe controller assignment and agree
on the exact Pareto count frontiers:

~~~text
T=1: (3,3),(4,2)
T=2: (9,9),(10,8),(11,7),(12,6),(14,5),(16,4)
T=3: (27,27),(28,26),(29,25),(30,24),(31,23),(32,22),
     (33,21),(34,20),(35,19),(36,18),(38,17),(40,16),
     (42,15),(44,14),(46,13),(48,12),(52,11),(56,10),
     (60,9),(64,8).
~~~

At horizon three, 84,672 candidate trees reduce to 1,872 undominated
read-count/write-language states.  Every frontier point satisfies Theorem 3,
while all fixed-schedule points lie on its joint boundary.

## 5. Four modes are minimal

For a finite safe-action relation and sensor partition `P`, define its local
signature `(p,q)` by

~~~text
p = number of cells of P,
q = minimum number of distinct actions assigning one common-safe action
    to every cell.
~~~

A strict registered tradeoff needs two feasible partitions with
`p_1<p_2` but `q_1>q_2`.

**Proposition 5 (minimal relational tradeoff).** With three registered
actions, no safe-action relation on at most three modes admits a strict local
tradeoff.  Four modes suffice, and the fixture above has signature pair
`(3,3)->(4,2)`.

**Proof.** A strict reduction cannot end at `q_2=1`: one action would then be
safe in every mode and would also serve every cell of the first partition.
Thus `q_1>=3`, which forces `p_1>=3`.  Since `p_2>p_1`, at least four modes are
necessary.  The displayed fixture attains the bound. QED.

The harness independently exhausts all 2,800 nonempty safe-action relations
with three actions through four modes and every partition: `24,221` feasible
relation/partition cells.  It finds zero strict-tradeoff relations through
three modes and exactly 72 four-mode relations.  There are exactly 72 witness
partition pairs, all with signature `(3,3)->(4,2)`.

## 6. Three exact regions on one plant

Keep the plant, action relation, evaluator, uncertainty, and transcript metric
fixed while changing only the admitted sensor grammar.

1. If every computed partition is admitted, the sensor may use
   `{{0,2},{1,3}}` and emit the sufficient action class `d/e`.  No one-action
   controller is safe in all modes, so the exact region is
   `[1,infinity) x [1,infinity)`.
2. If the registered grammar is `{P_c,P_r}` with arbitrary public-history
   selection, Theorem 4 gives the exact nonrectangular wedge.
3. If only the raw singleton partition is admitted, every read node has four
   labels while `(d,e,d,e)` uses two actions.  The exact region is
   `[2,infinity) x [1,infinity)`.

These regions are pairwise distinct.  They turn the v0.6 two-branch fork into
a three-branch fork containing the architecture-dependent tradeoff inequality
explicitly anticipated by the canonical ASMP-4 statement.

## 7. Rational evaluator-transversal realization

Let the mode coordinates be `z_i=-3,-1,1,3`, the registered numeric controls
be `a=0,d=1,e=2`, and `L_i(z)` the rational Lagrange basis on those four
points.  Define

~~~text
h_0(u)=u(u-1),   h_1(u)=u(u-2),
h_2(u)=u-1,      h_3(u)=u-2,
H(z,u)=sum_i L_i(z)h_i(u),
n_(t+1)=(3/2)n_t+H(z_t,u_t),
z_(t+1)=w_t.
~~~

At each registered grid point, `H(z_i,u)=0` exactly for `u in S(i)` and is
nonzero for every unsafe registered pair.  The control derivative at every
safe pair is one of `-2,-1,1,2`, hence nonzero.  The evaluator-safe condition
is `n=0`, the evaluator-normal multiplier is the unstable rational number
`3/2`, and disturbance reset has tangent derivative zero.  Exact rational
replay covers all `6^5=7,776` safe mode/action paths.

## 8. Zero-error support derandomization

The canonical rate definition charges complete transcript alphabets.  For a
randomized causal kernel, interpret that alphabet as the positive-probability
support over every allowed plant path.  Universal confinement remains
zero-error: every positive-probability branch must stay safe.

**Theorem 6 (support-derandomization theorem).** For finite or countable
positive-probability transcript supports, every zero-error randomized causal
sensor/controller/actuator code contains a deterministic safe subtree whose
complete read and write languages are subsets of the randomized support
languages.  Randomization therefore cannot enlarge a support-cardinality
ASMP-4 region.

**Proof.** At a reachable public history, let `Y(x)` be the nonempty support of
the sensor's next symbol in plant information state `x`.  For a symbol `y`,
every action in the controller/actuator support following `y` must be safe for
every state with `y in Y(x)`; otherwise an allowed state path and a
positive-probability random branch reach `BAD`.

Choose one symbol `y(x) in Y(x)` for each state, then choose one supported
write/action continuation for each selected public history.  Every chosen
edge had positive conditional probability in the randomized code, so
induction keeps the deterministic history inside the original support tree.
The preceding common-safety observation makes every chosen action safe.  The
selected read and write languages are literal subsets of the original support
languages, hence neither cardinality increases.  Repeat at every reachable
node. QED.

The same argument conditions first on any positive-probability shared seed
independent of the plant state.  It does not permit an uncharged random object
correlated with the state, which the canonical architecture expressly forbids.

The central bitmask census and an explicit-set verifier independently exhaust
all labeled sensor-support kernels with one through four labels on the
four-mode fixture.  Among 53,108 kernels, 43,744 use every declared label,
994 are zero-error feasible, and 950 are genuinely randomized.  They check
all 4,280 deterministic sensor selections and 3,058 nonempty controller-
support kernels, with zero derandomization failures.  The per-alphabet rows
are

~~~text
labels     support kernels     feasible     genuinely randomized
1                 1                0                  0
2                81                2                  0
3             2,401               66                 48
4            50,625              926                902
~~~

This bounded census is a falsification check for the local selection argument;
Theorem 6 applies to every finite/countable support alphabet and every horizon.

## 9. Prefix-free and independent-randomness robustness

For `N` complete transcripts, any binary prefix-free representation has
worst-case length at least `ceil(log2 N)`, and a fixed-length representation
attains that value.  The per-horizon correction is therefore less than one
bit on each port and vanishes asymptotically.

State-independent shared randomness also cannot improve the zero-error region
under the usual declared conventions.  A worst-seed budget inherits the
deterministic converse for every seed.  Seed-averaged log budgets preserve the
three linear rate inequalities under expectation.  A union-alphabet budget is
no smaller than each seeded alphabet.  Positive-error safety or
state-correlated side information would be a different registration and is
not claimed here.

## 10. Canonical disposition

The theorem closes the nonunique-safe-action seam for one exact registered
grammar, including the entire adaptive rate region, finite corrections,
constructive schedules, a converse, minimality, and a rational transversal
embedding.  It does not choose which sensor grammar the phrase “registered
causal code” in canonical v0.1 denotes.  The three exact regions therefore
strengthen, rather than remove, the v0.6 specification stopping argument.

The v0.8 successor audits a separate stochastic quantifier. It preserves this
section's support-zero-error theorem, proves that per-disturbance almost-sure
safety collapses to a common seed for countable disturbance alphabets, and
constructs an uncountable smooth diagonal where the two semantics separate.
