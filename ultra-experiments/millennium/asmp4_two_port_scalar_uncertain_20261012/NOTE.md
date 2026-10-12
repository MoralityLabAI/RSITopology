# ASMP-4 under the canonical text: the two-port region collapses, with a continuous uncertain example

Status: theorem note, 2026-10-12. Not a registered package. Everything proved
here is proved in full; everything cited is marked as cited; one question is
left open and marked as such. Companion to
[`../ASMP_V0_2_STATEMENT_REPAIRS_DRAFT_20261012.md`](../ASMP_V0_2_STATEMENT_REPAIRS_DRAFT_20261012.md)
item R2.

Revision record: a first draft of §4 claimed that the greedy per-step
schedule attains the lower bound `log2(a/(1-delta))`. Its telescoping step
used an inequality in the wrong direction; the exact replay in
`scalar_uncertain_check.py` caught the error (the greedy schedule runs at
about 1.512 bits per step against a 1.474 lower bound). The corrected
statement is a two-sided bound with two exact families and an open gap.

## 1. What the repository already proved

`asmp4_serial_collapse_theorem_v0_2/THEOREM.md` (Theorem 1, serial relay
normal form) and `asmp4_metric_robust_collapse_v0_3/THEOREM.md` (Theorems
1–3, upstream and downstream normal forms, metric-robust collapse) prove, for
the deterministic noiseless serial architecture of ASMP-4 and for every
symmetric transcript-tree cost including the canonical terminal-language rate
`limsup (1/T) log2 |M(T)|`:

```text
h_r(K_0,K) = h_w(K_0,K) =: h(K_0,K),
closure(R_K) = [h, infinity) x [h, infinity).
```

The proof moves controller computation upstream into the sensor or
downstream into the actuator and relays symbols unchanged. It uses the
assumption (v0.2 §1, item 5) that "the sensor may implement any registered
causal computation of its observation history".

`asmp4_registration_fork_v0_6` then asked whether the phrase "registered
causal code" licenses item 5, exhibited a *forced raw sensor* registration
that violates upstream closure (region `[2,inf) x [1,inf)` against
`[1,inf) x [1,inf)` on one four-mode plant), and the chain stopped at v0.36
pending "normative registration or attributable semantic adjudication".

So the mathematics of the collapse is the repository's. This note adds
three things: the reading that settles the fork (§2), the identification of
the common threshold with the one-port invariance data rate (§3), and a
continuous-state uncertain plant for which the threshold is bounded on both
sides, computed exactly in two parameter families, and shown to be a
quantized quantity rather than a closed-form entropy (§4).

## 2. The canonical text grants item 5

`AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md`, ASMP-4:

> `R_K = {(R_r,R_w): there exists a registered causal code C with r_r(C) <= R_r and r_w(C) <= R_w such that every x_0 in K_0 remains in K for every allowed disturbance sequence}`

> A causal sensor encoder emits only the read transcript; a controller receives only those symbols and emits the write transcript; an actuator decoder maps write symbols to controls.

> The plant, sensor, controller, and actuator are separate components. No analog state, shared object reference, common random variable correlated with the state, or uncharged side channel may cross either interface. Internal memory, delays, block coding, and shared randomness independent of the plant state are explicit parts of the architecture.

The code `C` is the triple (sensor encoder, controller, actuator decoder);
`R_K` is an existential over codes; the only constraints on the encoder are
on what crosses the interface (symbols) and on side information (none). No
clause restricts what the encoder computes from the plant state before
emitting a symbol. A "forced raw sensor" is therefore an additional
constraint, and v0.2's item 5 is the plain reading. The split-port liveness
example in the statement ("hold the sensor experiment fixed while varying
the finite actuator dictionary") is live only *because* it fixes the sensor,
which is exactly such an added constraint; v0.15's semantic audit already
labelled that clause `selects_parameterized`.

Consequently, for the canonical architecture:

- the v0.3 collapse theorem applies as stated;
- the Two-Port Capacity Conjecture's clauses "two possibly different
  evaluator-transversal invariance quantities" and "does not assume the
  region is rectangular in general" are false: the quantities coincide and
  the region is a quadrant;
- there are no "architecture-dependent tradeoff inequalities";
- unequal or non-rectangular regions exist only for explicitly asymmetric
  component classes (raw sensors, fixed sensor grammars, memoryless
  constraints), which a v0.2 statement must freeze if it wants them.
  Everything in `asmp4_*_v0_6` through `asmp4_*_v0_31` is a theorem about
  such restricted classes and remains correct as such.

## 3. The common threshold is the one-port invariance data rate

By the v0.3 proof, `h(K_0,K)` equals the infimal rate of a single
coder–decoder pair (a coder that sees the observation history and emits
symbols; a decoder that maps symbol histories to controls) rendering
`K_0 -> K` invariant for all disturbances. That is the quantity of the
invariance-entropy data-rate theorems:

- deterministic plants: the invariance entropy of Colonius and Kawan
  (*Invariance entropy for control systems*, SIAM J. Control Optim. 2009)
  [cited];
- linear deterministic plants with `K` compact with nonempty interior and
  the unstable subspace controllable: `sum_(|lambda|>1) log2 |lambda|`
  (Colonius–Kawan 2009; Nair, Evans, Mareels, Moran 2004) [cited]; this is
  the ASMP-4 clause "read-only specializations must recover the classical
  sum", and by the collapse it holds for the write port as well;
- uncertain plants: the invariance feedback entropy of Tomar, Rungger, and
  Zamani (*Invariance feedback entropy of uncertain control systems*, IEEE
  TAC 2021) for the history-dependent branching cost [cited]; v0.3 §1
  already records that the canonical terminal-language rate can be strictly
  smaller than that branching rate on uncertain plants.

Hence what ASMP-4 asks beyond the literature, under its own text, is the
invariance-entropy program (variational formulas, converses, finite-horizon
corrections, partial-observation boundaries) for nonlinear evaluator-relative
uncertain plants. That is a real program, but it is a one-port program and it
has owners. §4 shows that even its simplest uncertain instance is not a
closed-form quantity.

## 4. Example: a scalar uncertain plant

### 4.1 Setting

```text
x_(t+1) = a x_t + u_t + w_t,   a > 1,   |w_t| <= delta,   0 <= delta < 1,
K = K_0 = [-1, 1],   u_t in R,   the sensor observes x_t exactly.
```

Write `rho = a / (1 - delta)`.

A single-port code consists of finite alphabets `Sigma_t`, Borel encoders
`E_t : R^(t+1) -> Sigma_t`, and decoders `D_t : Sigma_0 x ... x Sigma_t -> R`.
Its realized transcript language `L(T)` is the set of words
`(s_0, ..., s_(T-1))` produced by some `x_0 in K_0` and some disturbance path;
its canonical rate is `limsup_T (1/T) log2 |L(T)|`. The code is safe if every
closed-loop trajectory from `K_0` stays in `K` for every disturbance path.
Let `h*` be the infimum of the rates of safe codes. By §1–§2,
`closure(R_K) = [h*, inf)^2` for the two-port architecture.

### 4.2 Theorem

```text
log2 rho  <=  h*  <=  log2 ceil(rho).
```

Moreover `h* = log2 rho` in each of the following cases:

1. `rho = a / (1 - delta)` is an integer (then the uniform `rho`-cell scheme
   attains it);
2. `delta = 0` (then `h* = log2 a` for every `a > 1`, attained by a
   time-varying schedule).

For every `T`, every safe code has `|L(T)| >= rho^T`.

Sanity limits: at `delta = 0` the value is the classical data-rate
threshold; as `delta -> 1`, `log2 rho -> infinity`, matching the fact that
with `|w| = 1` confinement requires exact knowledge of `x_t`. By the scaling
`x -> x / kappa`, for `K = [-kappa, kappa]` the lower bound is
`log2 (a / (1 - delta / kappa))`: the threshold depends on `(K, W)` jointly
and is not a function of the spectrum.

### 4.3 Lower bound

Fix a safe code. For a realized prefix `tau = (s_0, ..., s_t)` let `S_t(tau)`
be the set of states `x_t` that occur at time `t` along some admissible
closed-loop history producing `tau`. These sets are projections of Borel
sets, hence analytic, hence Lebesgue measurable; write `lambda` for Lebesgue
measure.

*(i) Cells are short.* On `S_t(tau)` the control `u_t = D_t(tau)` is fixed.
Safety for every `x in S_t(tau)` and every `w in [-delta, delta]` gives
`a S_t(tau) + u_t + [-delta, delta] subset [-1, 1]`, hence
`a diam S_t(tau) + 2 delta <= 2`, hence

```text
lambda(S_t(tau)) <= diam S_t(tau) <= 2 (1 - delta) / a = 2 / rho.
```

*(ii) Continuations are long.* The states reachable at time `t+1` from
prefix `tau` form `S^+(tau) = a S_t(tau) + u_t + [-delta, delta]`. Every
`x_(t+1) in S^+(tau)` is produced by some admissible history extending one
that produced `tau`, and that history emits some symbol `s`, so
`S^+(tau) subset union_s S_(t+1)(tau s)`. By the one-dimensional
Brunn–Minkowski inequality `lambda(A + B) >= lambda(A) + lambda(B)` for
nonempty measurable `A, B` with measurable sum,

```text
lambda(S^+(tau)) >= a lambda(S_t(tau)) + 2 delta.
```

*(iii) Mass recursion.* Let `N_t` be the number of realized prefixes of
length `t+1` and `M_t = sum_tau lambda(S_t(tau))`. Grouping the prefixes of
length `t+2` by parent and using subadditivity,

```text
M_(t+1) >= sum_tau lambda(S^+(tau)) >= a M_t + 2 delta N_t,
```

and by (i), `N_t >= (rho / 2) M_t`. Therefore

```text
M_(t+1) >= (a + delta rho) M_t = rho M_t,
```

because `a + delta rho = rho (1 - delta) + rho delta`. The initial cells
`S_0(s) = {x_0 in K_0 : E_0(x_0) = s}` partition `K_0`, so `M_0 = 2`. Hence
`M_t >= 2 rho^t` and

```text
|L(t+1)| = N_t >= (rho / 2) M_t >= rho^(t+1).
```

So every safe code has rate at least `log2 rho`. ∎

Where the bound is loose: equality in (i) and (iii) requires every cell to be
an interval of length exactly `2 / rho`, and equality in the recursion
requires the continuation of every cell (an interval of length exactly 2) to
be partitioned into such cells, which needs `rho` cells. For non-integer
`rho` this is impossible at every node, so the bound is not attained by
any interval scheme; whether some other code attains it is the open question
in §4.6.

### 4.4 Upper bounds

*Uniform scheme.* Let `m = ceil(rho)`. Keep an interval `I_t` of half-length
`ell_t` and known centre containing `x_t`, with `I_0 = K_0`, `ell_0 = 1`.
The sensor sends the index of the one of `m` equal cells of `I_t` containing
`x_t`; the decoder applies `u_t = -a c` with `c` that cell's centre. Then
`x_(t+1)` lies in an interval of half-length `ell_(t+1) = a ell_t / m + delta`
centred at 0, and `ell_t <= 1` implies `ell_(t+1) <= a / rho + delta = 1`.
The scheme is safe with `|L(T)| = m^T`, so `h* <= log2 ceil(rho)`. If `rho`
is an integer, `m = rho`, `ell_t = 1` for all `t`, and the rate equals the
lower bound: case 1 of the theorem.

*Deterministic case.* If `delta = 0`, use time-varying cell counts `m_t`
with `ell_(t+1) = a ell_t / m_t`, i.e. `ell_t = a^t / P_t` with
`P_t = prod_(s<t) m_s`; safety is `P_t >= a^t`. Choose `m_t = 1` when
`P_t >= a^(t+1)` and `m_t = ceil(a^(t+1) / P_t)` otherwise. Then
`a^(t+1) <= P_(t+1) < a^(t+1) + P_t`, and by induction
`P_t < (a / (a - 1)) a^t` for all `t`. Hence `|L(T)| = P_T = Theta(a^T)` and
the rate is exactly `log2 a`: case 2 of the theorem. ∎

*Interval-cell schemes in general.* An interval-cell scheme is any scheme in
which every realized consistent set is an interval; it is determined by how
each node's interval is partitioned into cells of half-length at most
`1 / rho` (in units where the node has half-length 1 this is the safety
condition of §4.3(i)). Writing a cell's *fullness* as `theta = rho * (its
half-length) in (0, 1]`, the continuation of a cell of fullness `theta` is
an interval of fullness-mass `f(theta) = a theta + rho delta` cell units,
which must again be partitioned. The minimal leaf count `V_T(theta)` of a
`T`-step scheme from a cell of fullness `theta` satisfies

```text
V_0 = 1,
V_T(theta) = min { sum_i V_(T-1)(theta_i) : theta_i in (0,1], sum_i theta_i = f(theta) },
```

and, since `V_T` is nondecreasing in `theta`, restarting a `T`-step scheme
every `T` steps (treating every leaf cell as full) gives a safe infinite
scheme with rate at most `(1/T) log2 V_T(1)`. A full cell has
`f(1) = a + rho delta = rho`, so the whole structure is driven by the affine
map `theta -> a theta + rho delta` modulo the integer parts removed as full
cells: a beta-expansion-like recursion whose growth rate equals `rho`
exactly when the orbit stays on integers.

### 4.5 Numeric bounds

`scalar_uncertain_check.py` computes `V_T(1)` by dynamic programming on a
fullness grid of `1/G` (continuation masses rounded *up* to the grid, so
every scheme the program finds is a genuine safe scheme and every printed
rate is a valid upper bound on `h*`), replays the greedy per-step schedule
`m_t = ceil(rho ell_t)`, and checks the two exact cases. With `G = 240`,
`T = 80`:

| `a = 5/2`, `delta = 1/10`, `rho = 25/9` | bits per step |
|---|---:|
| proved lower bound `log2 rho` | 1.473931 |
| best interval-cell scheme found (DP, horizon 80) | 1.490482 |
| greedy per-step schedule (T = 2000) | 1.511842 |
| uniform scheme `log2 ceil(rho)` | 1.584963 |

The DP bound decreases slowly with the horizon (1.4948 at 10, 1.4923 at 20,
1.4911 at 40, 1.4905 at 80) and appears to converge well above the lower
bound. Checks: for `a = 2`, `delta = 1/3` (`rho = 3`) the DP returns exactly
`3^T` leaves, rate `log2 3`; for `a = 5/2`, `delta = 0` it returns 1.3220 at
horizon 60 against `log2 a = 1.3219`.

### 4.6 What is open

For non-integer `rho` with `delta > 0`, the exact value of `h*` is open. The
proved bracket for the example is `[1.4739, 1.4905]`. Two remarks bound the
question:

- Any scheme attaining `log2 rho` must have negligible total emptiness
  (`N_t - (rho/2) M_t = o(rho^t)` in the notation of §4.3), so almost all of
  its cells must be nearly full intervals whose continuations partition
  almost exactly into further nearly full intervals. Interval schemes cannot
  do this when `rho` is not an integer; non-interval cells have measure
  strictly below their diameter and lose at step (i). I expect
  `h* > log2 rho` for every non-integer `rho` with `delta > 0`, but have not
  proved it.
- The invariance feedback entropy of Tomar–Rungger–Zamani is defined through
  finite invariant covers and is exactly this kind of combinatorial growth
  rate; they prove it is a tight lower bound on the data rate for the
  history-dependent branching cost [cited]. If the terminal-language and
  branching rates coincide on this plant, `h*` equals their quantity and is
  computable by their cover recursion; v0.3 §4 shows the two rates can differ
  on other uncertain plants, so this is not automatic.

Either way the conclusion for ASMP-4 stands: the canonical threshold of the
simplest uncertain continuous plant is a quantized combinatorial number that
depends on `(K, W)` and on the arithmetic of `a / (1 - delta)`, not a
Lyapunov-exponent sum. The repository's finite-plant corners such as
`2 + log2 phi` (v0.18) are the same phenomenon on finite alphabets.

## 5. Claim boundary

Proved here: §4.3 (lower bound for all Borel codes), §4.4 (two upper bounds
and the two exact families), and the validity of the DP rates in §4.5 as
upper bounds. Argued here: §2 (a reading of the canonical text; a reader who
holds that "registered" licenses restricted encoder classes gets a parametric
problem instead, which the v0.6–v0.31 chain studies). Cited, not reproved:
the v0.2/v0.3 collapse theorems and the invariance-entropy values in §3. Open:
§4.6. Not claimed: any result for nonlinear, partially observed, or
evaluator-quotient plants beyond what the cited theorems state. Novelty is
not claimed for the lower bound: Tomar, Rungger, and Zamani (IEEE TAC 66(12),
2021, doi 10.1109/TAC.2020.3038702; arXiv 1706.05242) give, for uncertain
linear systems, a lower bound on invariance feedback entropy in terms of
`|det A|` and the ratio of the volumes of the invariant set and the
uncertainty set, of which §4.3 is the scalar case (`a` and `2/(2-2delta)`)
with a self-contained proof; they also show that static memoryless
coder-controllers can lose up to one bit per step against the entropy, which
is why the schedules in §4.4 carry memory. Nothing here is evidence about
recursive self-improvement.
