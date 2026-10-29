# Serial-collapse theorem for ASMP-4

## Status and claim

This document gives a negative resolution of the "two independent
transversal entropies" premise and a positive characterization of the
deterministic noiseless serial architecture stated in ASMP-4.

The proof, not the finite harness, carries the claim. The harness checks finite
instances, exact corrections, and assumption boundaries.

**Metric clarification.** The
[asmp4 metric-robust v0.3 successor](../asmp4_metric_robust_collapse_v0_3/RESULT.md)
proves the same diagonal collapse for both this document's literal
whole-language cardinality rate and the history-dependent causal branching
rate. Those scalar rates need not agree for uncertain systems.

## 1. Registered architecture

Let the uncertain plant be

```text
x_(t+1) in F(x_t,u_t)
```

or equivalently `x_(t+1)=F(x_t,u_t,w_t)` for an adversarial disturbance
`w_t`. Let `K_0` be the initial set and `K` the evaluator-safe set.
Assume both are nonempty and `K_0` is contained in `K`.

A deterministic causal length-`T` code has:

```text
r_t = E_t(o_0,...,o_t,r_0,...,r_(t-1))
w_t = G_t(r_0,...,r_t)
u_t = D_t(w_0,...,w_t),
```

where `o_t` is the sensor's registered observation of `x_t`. Internal states,
public time, block coding, and deterministic decoder memory can be folded into
`E_t,G_t,D_t`. A fixed FIFO delay is represented by shifting the filtration
available to the corresponding map; transcript indices refer to registered
delivery events. The code is safe if every allowed initial state and
disturbance path stays in `K` at every registered time.

The theorem assumes:

1. the controller receives no information other than the read transcript and
   public deterministic architecture state;
2. the actuator receives no information other than the write transcript and
   public deterministic architecture state;
3. component initialization is independent of the plant state;
4. channel delivery is noiseless and has zero delay or a fixed public FIFO
   schedule for which a controller output can be computed upstream by the
   deadline of the read symbol delivered at that output event;
5. the sensor may implement any registered causal computation of its
   observation history;
6. read and write costs are the cardinalities of *realized* transcripts, or
   minimal equivalent prefix-free descriptions;
7. the ports have no fixed port-specific symbol syntax or instantaneous
   alphabet restriction beyond the charged transcript language, so a finite
   write alphabet may be bijectively relabeled on the read port; and
8. the admissible plant controls and actuator authority do not change when a
   transcript budget changes.

For a constant read delay `d`, condition 4 is automatic: at physical emission
time `s`, the sensor has generated every original read symbol the controller
will possess at delivery time `s+d`, including the current one, and can
therefore compute that controller's output for the delivery event. The
plant-independent warm-up prefix is generated locally by the relay. Fixed
write delay is unchanged by the construction. A varying or private schedule
that reveals a controller input only after this upstream deadline does not
satisfy condition 4.

These are the literal no-side-channel, achieved-transcript conventions needed
for the rates written in ASMP-4. Private random channel state, actuator-local
plant observations, different symbol-cost functions, fixed non-nested
codebooks, noisy links, deadline-incompatible schedules, port-specific
peak/burst caps, or computationally restricted sensors are different
architectures and are treated as boundary cases below.

For a code `C`, let `M_r^C(T)` and `M_w^C(T)` be the sets of realized read and
write words of length `T` over all registered plant paths. Define the exact
finite budget region

```text
R_T(K_0,K) = {(B_r,B_w): some T-safe C has
                         log2 |M_r^C(T)| <= B_r and
                         log2 |M_w^C(T)| <= B_w}.
```

## 2. Causal data-processing lemma

**Lemma 1.** Every deterministic serial code satisfies

```text
|M_w^C(T)| <= |M_r^C(T)|
```

at every horizon.

**Proof.** The controller is initialized independently of the plant and its
only nonpublic input is the read word. Iterating its causal update and output
maps therefore defines a deterministic map

```text
Phi_T^C : M_r^C(T) -> M_w^C(T).
```

The realized write language is the image of this map. Image cardinality cannot
exceed domain cardinality. QED.

The same proof applies with fixed controller memory and the timing-compatible
fixed public delays of Section 1. A shared random seed does not improve a
universal pathwise guarantee: fix any seed for which the guarantee holds and
obtain a deterministic code with no larger realized languages. A
probability-of-safety objective is a different problem.

There are two unambiguous zero-error randomness conventions. If safety is
required for every seed, any seed can be fixed. If the code-level event
"safe for all initial states and disturbance paths" has probability one, fix a
seed in that event. The weaker pointwise statement

```text
for every plant path, safety holds for almost every seed
```

need not provide one seed that works for an uncountable path family; it is not
the universal confinement quantifier written in `R_K`. A stochastic successor
must register that distinction and a reliability coordinate.

## 3. Relay normal form

**Theorem 1 (serial relay normal form).** For every deterministic safe serial
code `C`, there is a safe serial code `C^=` with identical plant trajectories
and

```text
|M_r^(C^=)(T)| = |M_w^(C^=)(T)| = |M_w^C(T)|
```

simultaneously for every `T`. With zero delay, the three languages themselves
are equal up to bijective symbol relabeling. With fixed delay, they have
canonical bijections after insertion or deletion of a plant-independent
warm-up prefix.

**Construction.**

1. The new sensor runs the original sensor encoder internally, so at time `t`
   it knows the complete read word that the original controller would have
   received.
2. It also simulates the original deterministic controller and computes the
   original `w_t`. With fixed read delay, it performs this computation at the
   emission deadline described in Section 1.
3. It emits a bijective copy of `w_t` on the read port.
4. The new controller emits the fixed warm-up prefix and is then an identity
   relay emitting `w_t` on the write port.
5. The actuator runs the original decoder, including its memory.

**Proof.** At `t=0`, the new sensor has the same observation and independent
initialization as the original encoder, hence computes the original `r_0` and
then the original `w_0`. The relay delivers that symbol to the unchanged
actuator decoder, so both codes apply the same `u_0` and reach the same set of
successor states. Inductively, equal state/observation histories let the sensor
reconstruct the original read history and controller state, so the same write
symbol and control are applied at every later time. Thus all plant
trajectories and safety decisions agree. The read and write words of the new
code are bijective copies of the old write word, proving the language
identities. QED.

The induction above uses zero-delay event notation. For a constant read delay
`d`, shift it by `d`: at physical emission time `s`, the sensor has just
generated the last original read symbol available at controller event `s+d`
and computes the original `w_(s+d)`. The new controller emits the
plant-independent original outputs before the first delivery and relays the
shifted symbols thereafter. This preserves every controller-output time and
hence every actuator input. Adding or removing the fixed prefix changes no
language cardinality at any horizon.

This construction is not an analog side channel. It moves a registered
deterministic computation upstream; the only live cross-component value remains
the finite symbol.

## 4. Exact finite-horizon region

Define the **serial evaluator-transversal spanning number**

```text
nu_T(K_0,K) =
    min over T-safe deterministic serial codes C
        with finite M_w^C(T) of |M_w^C(T)|,
```

with `nu_T=+infinity` if no such finite-language safe code exists.
Equivalently, it is the minimum number of realized complete control words
needed by an observation-based safe policy. This terminal-language quantity is
not, in general, the history-dependent worst-path branching quantity used by
invariance feedback entropy for uncertain systems. The v0.3 successor gives an
exact comb safety game where their asymptotic rates are zero and one,
respectively, and proves that the two-port collapse holds for either metric.

More explicitly, let `Pi_T^safe` be the set of safe causal policies respecting
the registered observation-to-control timing. In the zero-delay notation,

```text
pi_t : (o_0,...,o_t) -> u_t
```

and let `L_T(pi)` be the set of control words realized by `pi` over all initial
states and disturbance paths. Then the code-free variational formula is

```text
nu_T(K_0,K) = min_(pi in Pi_T^safe) |L_T(pi)|.
```

To prove the equivalence, any serial code induces such a policy and its
deterministic actuator maps each write word to one control word, so
`|L_T(pi)|<=|M_w^C(T)|`. Conversely, for any finite-language policy the sensor
can compute each `u_t` by its registered emission deadline, emit a finite
symbol naming that control, and use the warm-up/identity controller plus a
decoder into the unchanged admissible control set. Its write words are in
bijection with `L_T(pi)`. Taking the two minima proves equality. This is a
variational problem over safe control trees, not over arbitrary padded
communication containers.

**Theorem 2 (finite diagonal-quadrant formula).**

```text
R_T(K_0,K)
  = {(B_r,B_w): B_r >= log2 nu_T(K_0,K)
                  and B_w >= log2 nu_T(K_0,K)}.
```

**Converse.** For every safe code,

```text
nu_T <= |M_w^C(T)| <= |M_r^C(T)|
```

by definition and Lemma 1.

**Achievability.** A nonempty subset of the positive integers has a least
element, so a code attaining `nu_T` exists whenever the finite problem is
feasible. Apply Theorem 1 to obtain a code with both language cardinalities
equal to `nu_T`. Larger budgets admit the same code. QED.

The formula is the complete finite region, not one lower bound. It also shows
why a nominal grid that is not upward closed cannot be `R_T`.

## 5. Asymptotic variational formula

Let `Pi_infinity^safe(K_0,K)` be the infinite-horizon, timing-admissible causal
policies that keep every registered path in `K`, and define

```text
h_perp(K_0,K) =
    inf_(pi in Pi_infinity^safe(K_0,K))
      limsup_(T->infinity) (1/T) log2 |L_T(pi)|.
```

Set `h_perp=+infinity` if no such finite-rate policy exists. This definition
allows an arbitrary nonempty `K_0` contained in `K`; it does not assume a
resettable transient.

For completeness, the canonical capacity region in this notation is

```text
R_K = {(R_r,R_w): some infinite safe code C has
                    limsup_T log2|M_r^C(T)|/T <= R_r and
                    limsup_T log2|M_w^C(T)|/T <= R_w}.
```

**Theorem 3 (asymptotic serial-capacity formula).** Under the registered
architecture,

```text
closure(R_K) =
    [h_perp(K_0,K),infinity) x [h_perp(K_0,K),infinity).
```

If `h_perp=+infinity`, the displayed right-hand side is interpreted as the
empty region in the finite-rate plane.

**Converse.** Every infinite safe serial code induces an infinite safe policy,
and its deterministic actuator maps each write word to one control word.
Thus `h_perp(K_0,K)<=r_w(C)`. Lemma 1 gives `r_w(C)<=r_r(C)`, so both
coordinates of every achievable rate pair are at least `h_perp(K_0,K)`.

**Achievability.** For every `epsilon>0`, choose a safe policy whose
control-language rate is below `h_perp(K_0,K)+epsilon`. The policy-to-code
construction of Section 4 and relay normal form give one infinite safe code
whose read, write, and control languages are in bijection at every horizon.
Finite rate implies that every `L_T` is finite; their countable union supplies
one consistent countable symbol dictionary for the infinite code.
Both rates are therefore below `h_perp(K_0,K)+epsilon`. Larger budgets admit
the same code, and taking closure proves the formula. QED.

In the important regenerative specialization, augment the plant by every
public architecture state affecting future delivery or decoding: clock phase,
fixed-delay queues, and registered component memory. Let `nu_T^reg(K)` minimize
the language of safe blocks that start in the registered augmented set and
return both it and the public architecture state to their registered
regeneration condition. Concatenating such blocks gives

```text
nu_(T+S)^reg(K) <= nu_T^reg(K) nu_S^reg(K).
```

Fekete's lemma then supplies the finite-block variational formula

```text
h_perp^reg(K) =
    lim_(T->infinity) (1/T) log2 nu_T^reg(K)
  = inf_(T>=1)        (1/T) log2 nu_T^reg(K).
```

The limit equality is Fekete's lemma. Repeating a minimizing regenerative
`T`-block policy in relay normal form realizes at most `(nu_T^reg)^n` words
over `n` blocks, while the definition of `nu_T^reg` gives the converse for
every registered block. Thus this is the exact entropy of the repeatable-block
class.

Zero-delay links have no queue to regenerate. A fixed-delay implementation has
this corollary only when an explicitly safe flush/guard or augmented-state
return actually restores the registered condition; it must not silently reset
an in-flight queue. Without regeneration, the general infinite-policy formula
above remains the applicable characterization. Nonresetting private channel
state is outside this theorem.

Thus the two quantities requested by ASMP-4 exist but coincide:

```text
h_read_perp(K_0,K) = h_write_perp(K_0,K) = h_perp(K_0,K).
```

There is no nonrectangular information-rate tradeoff in this architecture. A
nonrectangular or unequal frontier certifies an added constraint or source of
information, not a property of the stated serial achieved-transcript model.
In particular, a port-specific peak alphabet or burst cap is an additional
resource coordinate; two limsup transcript-growth rates alone do not record it.

## 6. Coordinate invariance and evaluator quotient

Let `phi:X->X'` be a bijective state-coordinate change carrying `K` to `K'`,
the observation relation to its transported relation, and every plant
transition to its conjugate. Transporting a policy through `phi` changes no
read, write, or control-word language. Therefore every `nu_T` and `h_perp` is
coordinate invariant.

For evaluator-relative safety, let `x~x'` mean that the evaluator identifies
the states. The quotient is valid when `~` is a **control congruence**:

```text
x~x' implies that for every admissible control,
the sets of successor equivalence classes agree
under every registered disturbance.
```

If the sensor observation and safe predicate also factor through the quotient,
safe policies lift and descend without changing transcript languages.
Consequently `nu_T` and `h_perp` computed on the quotient equal the full-system
values. This is the coordinate-free meaning of "transversal" here.

If tangent state feeds an evaluator-normal successor, the relation is not a
control congruence. Quotienting it out is then invalid; its uncertainty must
appear in `nu_T`. This exactly separates irrelevant tangent instability from
registered tangent-to-normal coupling.

## 7. Exact initial-margin correction

Consider

```text
x_(t+1) = a x_t + u_t,
a > 1,
x_0 in [-delta,delta],
K=[-L,L],
0 < delta <= L,
U=the real numbers.
```

Assume the sensor observes the state exactly with the zero-delay registered
ordering. (A delayed version applies to the corresponding predictive
safe-policy class, but need not have this same finite transient.)

**Theorem 4 (scalar finite-horizon formula).**

```text
nu_T([-delta,delta],[-L,L]) = ceil(a^T delta/L).
```

**Lower bound.** A fixed write word determines one control sequence. At time
`T`, the initial states kept safe by that sequence lie in an interval of
length at most `2L/a^T`. Covering an initial interval of length `2delta`
therefore needs at least `ceil(a^T delta/L)` write words.

**Construction.** Partition the initial interval into
`N=ceil(a^T delta/L)` intervals of radius at most `L/a^T`. For a cell centered
at `c`, use

```text
u_0=-a c,  u_1=...=u_(T-1)=0.
```

Then `x_t=a^t(x_0-c)` and `|x_t|<=L` for every `t<=T`. Index the `N` sequences
on both ports using relay normal form. QED.

The exact rate is

```text
(1/T) log2 ceil(a^T delta/L).
```

It is zero while the initial safety margin satisfies `a^T delta<=L`, and it
converges to `log2 a`. This is the requested exact coasting correction, not an
asymptotic approximation. The code uses the burst-permitted transcript metric
written in the canonical definition. If a successor freezes a per-prefix or
per-step peak alphabet, that peak constraint must be added to `R_T`; it cannot
be inferred from the terminal transcript count.

For a real diagonal plant with a box initial set, box safe set, and unrestricted
coordinate controls, the same packing/construction argument gives

```text
nu_T = product_i max(1,ceil(|lambda_i|^T delta_i/L_i)),
```

and therefore

```text
h_perp = sum_(|lambda_i|>1) log2 |lambda_i|.
```

This recovers the classical positive-exponent specialization while deriving
the same threshold on both serial ports.

For the disturbance-free stable scalar control `|a|<=1`, `K_0` contained in
`K=[-L,L]`, and `u_t=0`, a single open-loop word is safe, so `nu_T=1` and
`h_perp=0`. This is the stable zero-rate liveness arm.

## 8. Boundary counterexamples

All finite cases below are implemented exactly in `serial_capacity.py`.

### Partial observability

Two safe modes `L,R` require actions `l,r`, respectively, or transition to
`BAD`. With distinct observations, `nu_1=2`. If the sensor observation merges
`L` and `R`, no finite-rate code is safe. More bits cannot repair a
nonseparating observation map.

### Uncertainty timing

At safe state `S`, the action must equal a fresh adversarial disturbance bit
chosen after the action; otherwise the plant enters `BAD`. The task is
impossible at every rate. If the bit is announced before action selection, the
problem has changed by adding side information.

### Actuator authority

In the two-mode safety game, full observation and both mode-matching actions
give `nu_1=2`. Removing one required action makes one initial safe mode
uncontrollable at every information rate. The harness keeps this authority
failure separate from the transcript lower bound. In particular, varying the
finite action dictionary while holding sensor data fixed is the requested
split-port diagnostic, but it varies actuator authority rather than an
achieved-information coordinate.

### Nonhyperbolicity

For

```text
n_(t+1)=n_t+z_t+u_t,
z_(t+1)=z_t,
n_0=0,
|z_0|<=delta,
|n_t|<=L,
```

with full observation and unrestricted scalar control, the exact count is

```text
nu_T=ceil(T delta/L).
```

A fixed control word leaves `n_T=T z_0+constant`, so it covers an initial
`z_0` interval of length at most `2L/T`. Conversely, partition
`[-delta,delta]` into `ceil(T delta/L)` cells centered at `c` and apply
`u_t=-c`; then `n_t=t(z_0-c)` stays in `[-L,L]`. The count is unbounded but has
zero asymptotic entropy. This shows why the exact finite term cannot be
inferred from the Lyapunov sum at a nonhyperbolic boundary.

### Side information

Let an adversary choose a fresh binary mode each step and require the matching
binary action. In the strict serial architecture, every binary action word is
realized, so `nu_T=2^T` and `h_perp=1`. If the actuator observes the live mode
locally, one write word suffices and the write rate is zero. The unequal
frontier comes from actuator side information and is outside the no-side-
channel theorem.

### Decoder memory

A one-symbol, time-aware actuator can execute a registered open-loop schedule.
A fixed memoryless one-symbol action dictionary may fail on the same plant.
The relay theorem permits decoder memory and therefore does not confuse action
authority with transcript information.

### Tangent coupling

Uncoupled tangent motion is quotiented out by control congruence and changes no
`nu_T`. A tangent-to-normal shear produces the polynomial count above and
cannot be quotiented out. Hyperbolic coupling can produce exponential normal
covering growth and is charged automatically.

## 9. Prior-art and novelty boundary

Invariance entropy and invariance feedback entropy already characterize a
single coder-controller channel and supply invariant-cover/control-tree
variational quantities. Their uncertain-system transmission rate charges
history-dependent successor branching, not merely growth in the number of
complete realized words. This result therefore does not rename that theory.
Its ASMP-4 contribution is the serial relay theorem under the problem's own
achieved-transcript formula. The v0.3 bilateral extension shows that inserting
a deterministic controller-to-actuator link creates no second independent
entropy under either shared metric.

Relevant primary sources:

- Colonius and Kawan,
  [Invariance Entropy for Control Systems](https://doi.org/10.1137/080713902).
- Tomar, Rungger, and Zamani,
  [Invariance Feedback Entropy of Uncertain Control Systems](https://arxiv.org/abs/1706.05242).
- Tomar, Kawan, and Zamani,
  [Numerical over-approximation of invariance entropy via finite abstractions](https://arxiv.org/abs/2011.02916).
- Yuceel, Tchalakov, and Mitra,
  [Minimal Information Control Invariance via Vector Quantization](https://arxiv.org/abs/2604.03132).

No claim is made for noisy stochastic channels, error exponents, private random
delivery state, deadline-incompatible timing, actuator observations, unequal
symbol-cost metrics, or port-specific peak/burst constraints. Those objects
are not coordinates of the `R_K` defined in ASMP-4 v0.1.
