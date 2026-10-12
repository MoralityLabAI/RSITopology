# ASMP v0.2 statement repairs — draft, 2026-10-12

Status: proposal. Nothing here edits `ASMP-CANDIDATE-SET-v0.1`. Each item
names the defect in the v0.1 or v0.2-draft statement, gives the argument, and
proposes replacement wording. Proofs are complete where a proof is claimed;
sketches are labelled sketches. Companion to
[`docs/CRITIQUE_NOTES_20261012.md`](../../docs/CRITIQUE_NOTES_20261012.md).

---

## R1. Resolution rule 10: the undecidability clause is vacuous for program-encoded instances

### Defect

Rule 10 accepts "an undecidability result for the frozen uniform decision
family" as a resolution. Graduation standard 3 requires liveness. Together
they make every problem whose instances are presented as programs resolvable
by a content-free argument. ASMP-3 v2.20/v2.21 and ASMP-1 v0.2 are instances.

### Lemma R (index sets of tail-determined live properties)

Let instances be indices `e` of total computable generators `G_e`, where
`G_e(d)` is the depth-`d` object of the family (a finite game, a rational
approximation, a finite SCM). Let `P` be a set of families such that

1. (extensional) membership of `G_e` depends only on the function
   `d -> G_e(d)`;
2. (tail-determined) if `G(d) = G'(d)` for all `d >= N` then
   `G in P iff G' in P`;
3. (live) there exist `e_in` with `G_(e_in) in P` and `e_out` with
   `G_(e_out) not in P`.

Then `{e : G_e in P}` is undecidable, and `NONHALT` many-one reduces to it.

*Proof.* Given a Turing machine `M`, let `e_M` be the index of the total
generator

```text
G_(e_M)(d) = G_(e_in)(d)   if M has not halted within d steps,
             G_(e_out)(d)  otherwise.
```

It is total and computable because the halting test is bounded. If `M` never
halts, `G_(e_M) = G_(e_in)`, so `G_(e_M) in P` by (1). If `M` halts at `t`,
then `G_(e_M)(d) = G_(e_out)(d)` for all `d >= t`, so `G_(e_M) not in P` by
(2). The map `M -> e_M` is computable, so a decider for the index set decides
`NONHALT`. ∎

*Remark.* If `P` is `Sigma_2`-definable (`exists c,N forall d>=N ...`, as in
`WV-FIX-UCOMP`), the same reduction shows the positive index set is not
recursively enumerable, since `NONHALT` is not. Both v2.20 and v0.2 state
exactly these corollaries.

### Application

- ASMP-3 v2.20 (`UNIFORM_MEMBERSHIP_UNDECIDABILITY_THEOREM_v2_20.md`): the
  class is tail-determined by its own §1 ("finite prefixes are ignored"),
  live by the problem's positive/negative examples, and the reduction in its
  §2 is the lemma's with `e_in` the parity game with a working oracle and
  `e_out` the same game with a constant-zero oracle.
- ASMP-1 v0.2 (`asmp1_resolution_boundary_v0_2/RESULT_v0_2.md`): `c_e = 0`
  if `e` never halts, else `2^-t`; `P` = "the two mechanisms are
  observationally equivalent". Tail-determined (a computable real is
  determined by its tail), live (`c = 0` versus `c = 1`).
- ASMP-5: "`z_t in S` for all `t`" over partial computable updates is the
  halting problem by the same construction.

None of these says anything about weak verification, identifiability, or
reflective safety. They say that the instance language was too rich.

### Proposed amendment to rule 10

> 10. **Two-sided resolution rule.** [...] An undecidability result for the
> frozen uniform decision family resolves the problem only when the
> problem's instance grammar is the one frozen in the statement and that
> grammar is *finitely presented with certified margins*: instances are
> given by explicit finite data (rational numbers, explicit circuits, finite
> tables) together with rational lower bounds on every margin the statement
> names (`kappa`, `gamma`, `eta`, `c`). Undecidability obtained by admitting
> program-named objects (computable reals without certified gaps,
> program-generated families, partial computable update programs) does not
> count; by Lemma R it holds for every live tail-determined property and
> carries no information about the problem.

### Proposed grammar clauses

- ASMP-1: `F` consists of polynomial (or rational) mechanisms with rational
  coefficients of bit-length at most `b`; `kappa, gamma` are given as
  rationals. The problem becomes the intervention-query and arithmetic
  complexity of recovering `Q/G`, which is the question v0.1 actually asks.
- ASMP-3: `R_n` is given by a circuit of size `T(n)`; the oracle `H` is a
  fixed function of the instance; the class is a complexity class; the
  negative route is a lower bound under a stated assumption (one-way
  functions, iO), not undecidability.
- ASMP-5: updates range over a decidable grammar `U` with a proof budget;
  the negative route is a Löb/consistency-strength obstruction, which is the
  problem's own named frontier (see R6).

---

## R2. ASMP-4: the "registration fork" is resolved by the quantifier

### Text

> `R_K = {(R_r,R_w): there exists a registered causal code C with r_r(C) <= R_r and r_w(C) <= R_w such that every x_0 in K_0 remains in K for every allowed disturbance sequence}`

> A causal sensor encoder emits only the read transcript; a controller receives only those symbols and emits the write transcript; an actuator decoder maps write symbols to controls.

### Argument

The code `C` is the triple (sensor encoder, controller, actuator decoder).
`R_K` is defined by an existential quantifier over codes. A "forced raw
sensor" (v0.6) is a restriction of the encoder's computation that the text
does not impose; the architecture paragraph constrains what crosses the
interface (symbols only; no analog state, no shared object references, no
uncharged side channels), not what the encoder computes from the plant
state. Under the text, the computed-sensor branch is the problem, and `R_K`
is the infimal region over all admissible encoders.

The v0.6 parametric theorem (`[log2 kappa, inf) x [log2 m, inf)` for a
sensor grammar `Gamma`) remains a correct theorem about the restricted class
`C_Gamma`; it should be filed as such. The stop certificates v0.14, v0.32,
v0.36 rest on treating the ambiguity as open; under this reading they are
withdrawn as stop conditions, though their mathematics stands.

### Proposed wording (v0.2)

> The code `C = (phi, gamma, psi)` consists of a causal sensor encoder
> `phi`, a causal controller `gamma`, and a causal actuator decoder `psi`.
> Each may be any causal map subject to the architecture constraints; in
> particular the encoder may compute any causal function of the plant state
> before emitting symbols. `R_K` is the set of rate pairs achieved by some
> admissible `C`. Theorems for restricted encoder classes `C_Gamma` are
> partial results and must name `Gamma`.

### Consequence under this reading (2026-10-12)

The repository's own `asmp4_serial_collapse_theorem_v0_2` and
`asmp4_metric_robust_collapse_v0_3` prove, under exactly the item-5
assumption that the text grants, that the two single-port thresholds
coincide and `closure(R_K)` is the quadrant `[h, inf)^2` for every symmetric
transcript cost. So under the canonical text the Two-Port Capacity
Conjecture's "two possibly different quantities" and "not rectangular in
general" clauses are false, there are no architecture-dependent tradeoff
inequalities, and `h` is the one-port invariance data rate (invariance
entropy; invariance feedback entropy for uncertain plants). Unequal or
non-rectangular regions require asymmetric component classes, which v0.2
must freeze explicitly if it wants them.

A continuous uncertain example is worked in
[`asmp4_two_port_scalar_uncertain_20261012/NOTE.md`](asmp4_two_port_scalar_uncertain_20261012/NOTE.md):
for `x' = a x + u + w`, `|w| <= delta < 1`, `K = K_0 = [-1, 1]`, with
`rho = a / (1 - delta)`, the common corner `h*` satisfies

```text
log2 rho <= h* <= log2 ceil(rho),
```

with `h* = log2 rho` exactly when `rho` is an integer or `delta = 0`, and in
general a quantized combinatorial value strictly inside the bracket
(numerically bounded in the note). The threshold therefore depends on
`(K, W)` jointly, recovers `log2 a` only as `delta -> 0`, and is not a
closed-form entropy; v0.2 should name the invariance (feedback) entropy, not a
sum of Lyapunov exponents, as the read-only specialization target, and should
expect quantization effects of the kind the finite ASMP-4 censuses already
exhibit.

---

## R3. ASMP-8: the frontier is the tail class of the proxy error; the KL slice is mostly known

### Defect

With `D_eps` uniform over `Pi_lambda`, `Regret <= 2 eps` is a triangle
inequality (the statement's own positive example). With `D_eps` a
reference-measure condition, regret is unbounded (its own negative example).
The hostile-referee question in the v0.2 draft ("can pressure be defined
without collapsing to uniform accuracy?") is the whole problem and no package
addresses it. The draft's proposed "registered slice" (KL pressure,
best-of-`n`) is the subject of Beirami et al. (2024) and Kwa, Thomas,
Garriga-Alonso (2024).

### Setting for the KL slice

Reference distribution `p_0` on outcomes `Omega` (the base policy's
trajectory law). Reachable set `Pi_lambda = {pi << p_0 : KL(pi || p_0) <= lambda}`.
True reward `R`, proxy `R_hat`, error `delta = R - R_hat`, all real functions
on `Omega`. `R(pi) = E_pi[R]`. A proxy maximizer is any
`pi_hat in argmax_(pi in Pi_lambda) E_pi[R_hat]`.

```text
Regret(lambda) = sup_(pi' in Pi_lambda) E_(pi')[R] - E_(pi_hat)[R].
```

### Theorem (light tails)

Suppose `delta` is `sigma`-sub-Gaussian under `p_0`:
`log E_(p_0) exp(t (delta - E_(p_0) delta)) <= sigma^2 t^2 / 2` for all real
`t`. Then for every proxy maximizer,

```text
Regret(lambda) <= 2 sigma sqrt(2 lambda).
```

*Proof.* For any `pi' in Pi_lambda`, since `pi_hat` maximizes the proxy,

```text
E_(pi_hat)[R] = E_(pi_hat)[R_hat] + E_(pi_hat)[delta]
             >= E_(pi')[R_hat] + E_(pi_hat)[delta]
             =  E_(pi')[R] - E_(pi')[delta] + E_(pi_hat)[delta].
```

Hence `Regret <= sup_(pi in Pi_lambda) E_pi[delta] + sup_(pi in Pi_lambda) E_pi[-delta]`.
By the Donsker–Varadhan variational formula, for `pi << p_0` and any `t > 0`,
`E_pi[t f] <= KL(pi || p_0) + log E_(p_0) exp(t f)`. With
`f = delta - E_(p_0) delta` and `KL <= lambda`,

```text
E_pi[delta] - E_(p_0)[delta] <= inf_(t>0) (lambda + sigma^2 t^2 / 2) / t = sigma sqrt(2 lambda),
```

attained at `t = sqrt(2 lambda) / sigma`. The same bound holds for `-delta`
with the sign of the bias reversed, so the biases cancel in the sum. ∎

### Sharpness

`Omega = R^2`, `p_0 = N(0, I)`, `R(omega) = u . omega` with `|u| = 1`,
`R_hat(omega) = -s u . omega` for small `s > 0`. Then `delta = (1+s) u . omega`
is `(1+s)`-sub-Gaussian. The maximizer of a linear functional `w . omega`
over the KL ball is the exponential tilt with mean `sqrt(2 lambda) w / |w|`
and value `sqrt(2 lambda) |w|`. So the proxy maximizer tilts toward `-u` and
`E_(pi_hat)[R] = -sqrt(2 lambda)`, while `sup_(pi') E_(pi')[R] = sqrt(2 lambda)`.
`Regret = 2 sqrt(2 lambda)`, and the bound is `2 (1+s) sqrt(2 lambda)`. The
ratio tends to 1 as `s -> 0`: the constant `2 sqrt 2` is sharp, and a proxy
of arbitrarily small magnitude anti-aligned with the true reward attains it.

### Heavy tails (sketch, with the known result)

If `delta` has only polynomial tails under `p_0`
(`p_0(delta > a) ~ a^(-p)`), concentrate `pi` on `{delta > a}`:
`KL = -log p_0(delta > a) ~ p log a`, so within budget `lambda` one reaches
`a ~ exp(lambda / p)` and `E_pi[delta]` of that order. Regret is then
exponential in `lambda` rather than `sqrt(lambda)`. Kwa et al. (2024) show
the operational consequence: under heavy-tailed proxy error, KL regularization
does not prevent the proxy-optimal policy from achieving no true-reward gain.
So in the KL slice, the Goodhart frontier is the tail class of the proxy error
under the base distribution: sub-Gaussian gives `Theta(sigma sqrt(lambda))`
regret with sharp constant; polynomial tails give exponential regret.

### Proposed v0.2 statement

> **ASMP-8 (KL-pressure Goodhart frontier).** Freeze `p_0`, the reachable
> family `Pi_lambda = {KL(pi||p_0) <= lambda}`, and a tail class `T` for the
> proxy error `delta = R - R_hat` under `p_0` (Orlicz norm `||delta||_psi`
> for a Young function `psi`). Determine the exact function
> `G_T(lambda, ||delta||_psi) = sup Regret(lambda)` over the class, its
> sharp constants, and the finite-sample version in which `R_hat` is learned
> from `n` comparisons. Known: the sub-Gaussian case (above) and the
> polynomial-tail catastrophe (Kwa et al.). Open: sub-exponential and Weibull
> tails, the finite-sample proxy-training frontier, and reachable families
> other than KL balls (best-of-`n` is the special case
> `KL <= log n - (n-1)/n`, Beirami et al.).

The deterministic audit certificate packages (`v0_6_adaptive_reuse` etc.)
are unaffected but should be filed as audit-design instruments, not as
Goodhart-frontier results.

---

## R4. ASMP-10: no model class, no problem

### Defect

As stated, for *any* observation class that does not identify the training
dynamics there are two admissible processes with identical prefix
observables and different futures. The repo's own
`prefix_obstruction/RESULT_v0_1.md` says this: "the claimed training family
needs a stated regularity assumption explaining why adversarial
prefix-matched continuations are inadmissible". The negative half is
therefore trivially true for unrestricted `T`, and the positive half is an
empirical program (developmental interpretability), not a theorem frontier.

### Proposed v0.2 statement

> **ASMP-10 (forecast information of training observables).** Freeze a
> *prior* `mu` over training processes (architecture family, data
> distribution, optimizer, hyperparameter set, seed distribution), the
> observable filtration `F_s`, the target scale `s' > s`, and a frozen
> continuous capability functional `C` with a metric-robustness
> neighbourhood. Let `B(F_s) = inf_Phi E_mu[loss(Phi(F_s), C(W_(s')))]` be
> the Bayes error of forecasting `C(W_(s'))` from `F_s`. Determine (i)
> which observables are sufficient (`B(F_s) = B(F_s^full)`), (ii) lower
> bounds on `B(F_s)` for stated `mu`, and (iii) whether candidate statistics
> (LLC, spectral summaries) close the gap on held-out seeds.

Under this statement the "mirage pair" is a lower bound on `B` for a specific
prior, which is a real theorem target; under unrestricted `mu` the Bayes
error is maximal and the problem is correctly classified as vacuous.

---

## R5. ASMP-11: simulation closure collapses the access lattice to white-box

### Lemma S

Let a detector with access class `A` be a probabilistic polynomial-time
algorithm with oracle access to functionals `O_1, ..., O_m`, where each
`O_j(W, S, x)` (activations, gradients, Jacobians, ablations, weight edits
with re-evaluation, adaptively chosen inputs `x`) is computable in time
polynomial in `|W| + |S| + |x|`. Then for every such detector `D^A` there is
a plain white-box detector `D'(W, S)` with the same running-time class and
the same distinguishing advantage.

*Proof.* `D'` runs `D` and answers each oracle call by computing `O_j`
itself. `D` makes polynomially many calls, each polynomial, so `D'` is
polynomial. Its output distribution equals `D`'s. ∎

### Consequences

- For every model class in which white-box undetectable backdoors exist
  (random Fourier features and random ReLU networks, Goldwasser et al. 2022;
  obfuscated networks, Kalavasis et al. 2024), the backdoors are undetectable
  under every polynomial-time interpretability or intervention access class.
  The lattice's negative region is all of it, at or below white-box.
- The lattice is nontrivial only (a) strictly below white-box (bounded
  black-box query budgets, sub-polynomial computation), which is the
  black-box side of Goldwasser et al.; (b) for model distributions in which
  the cryptographic constructions are atypical, which is an empirical premise
  about training; or (c) for access that reveals information *not computable
  from `(W, S)`*: the training seed and trajectory. With a reproducible
  training procedure and the seed, a verifier retrains and compares; any
  planted deviation is detected. That access class is the subject of
  proof-of-learning and verifiable-training work, i.e. ASMP-7.

### Proposed v0.2 statement

> **ASMP-11 (detectability relative to natural training).** Freeze a
> training procedure `Train(S, r)` with randomness `r`, the induced
> distribution `M_clean` over models, a backdoor-planting adversary class,
> and an access class `A` *including or excluding* `r` and the training
> trajectory. Characterize the minimax distinguishing advantage between
> `M_clean` and backdoored models as a function of what `A` reveals beyond
> `(W, S)`. Interpretability queries computable from `(W, S)` add nothing
> (Lemma S); the problem is about provenance access and about whether
> natural training distributions admit in-distribution backdoors.

The rank–nullity "access ladder" (`r + s = k`) is an instrument for planted
Boolean mechanisms and should be filed as such.

---

## R6. ASMP-5: promote ASMP-5A to the main statement

The dichotomy's negative half (no uniformly sound architecture for all
partial computable self-modifiers and any nontrivial extensional `S`) is
Lemma R. The positive half (proof-carrying updates preserving an inductive
invariant in an assumed-sound kernel) is proof-carrying code. The named
frontier (verifier replacement, Löb) is exactly ASMP-5A's object.

> **ASMP-5 (v0.2).** Fix a reflective hierarchy `T_0 subset T_1 subset ...`
> of verifiers (for instance iterated consistency extensions of a base theory
> with a decidable proof checker), a successor grammar in which an agent at
> level `i` may install a successor at level `j` only with a `T_i`-proof of
> the successor's safety relative to `S`, proof budgets `B_0, ..., B_k`, and
> a nonzero progress index. Determine the sharp degradation functions
> `g_lower(k) <= S_0 - S_k <= g_upper(k)` of certifiable safety margin along
> any admissible chain of length `k`, or prove no uniform bound exists for the
> declared scheme class. Critch's bounded Löb theorem is the known positive
> seed; the direct-simulation scheme with overhead `c` per step is the
> baseline `proof_length <= L - c k`.

The v0.3 inductive-root census (`asmp5_verifier_drift/v0_3_inductive_root`)
is a positive control for a fixed root and does not bear on this.

---

## R7. ASMP-2: attribute the local part, pose the global part

The local conjecture (a regular first-order certificate exists iff the
derivatives of the safety and utility functionals on `T_adv` factor
continuously through the identified score experiment with positive
conditioning margin) is close to the classical characterization of regular
estimability: a functional admits a regular estimator iff it is pathwise
differentiable with its derivative continuous on the tangent set (van der
Vaart, *Asymptotic Statistics*, ch. 25). The v0.2 statement should cite this
and drop the local conjecture as a resolution target. The global problem:

> Fix a parametric family with compact `Theta_adv`, a safety loss `L_s`
> with a known curvature bound `H` on `Theta_adv`, and source designs
> `theta_1..theta_m` with sample sizes `n_i`. Determine the minimal design
> (in `m`, in `sum n_i`, and in placement) such that
> `sup_(theta in Theta_adv) L_s(h, P_theta) <= eps` is certifiable with
> confidence `1 - delta`, and the matching lower bound.

This is an optimal design and covering problem; the repo's crossed-shift
fixture is a two-parameter instance of it.

---

## R8. Holonomy liveness precondition (identity program, not ASMP)

From Theorem 1 of `reports/QWEN08_PRECISION_GEOMETRY_PAPER_V0_1.md`: a
rank-one cycle with edge principal angles `alpha_i` has negative holonomy
only if `sum alpha_i >= pi`. With a per-edge retention floor `tau`,
`alpha_i <= arccos(sqrt tau)`. Registration precondition for any rank-one
holonomy claim on a graph with longest admitted cycle length `L`:

```text
L * arccos(sqrt tau) >= pi.
```

| `tau` | `arccos(sqrt tau)` | minimum live cycle length |
|---:|---:|---:|
| 0.50 | 45.0° | 4 |
| 0.75 | 30.0° | 6 |
| 0.90 | 18.4° | 10 |
| 0.95 | 12.9° | 14 |

The registered-not-run `qwen08_dense_local_holonomy_v0_1` (lineage floor
0.90, 2×4 cells, longest simple cycle 8 edges) cannot produce a negative
rank-one holonomy on any cycle. Its rank-1 `w1` channel should be removed
before it runs; ranks 2–8 stay live and should be compared against the
prompt-resample noise null, as already registered. The graded angle-budget
observable (frustration margin) should carry the explicit caveat that it is
live only when lineage is already degraded or cycles are long.

---

## R9. Smaller items

- **Novelty ledger.** One page listing every claim the authors consider
  `candidate_new`, with its package and the nearest prior result. Currently
  two occurrences in 1,203 files; a reviewer cannot find them.
- **Reductions between problems.** The referee audit lists three plausible
  reductions (ASMP-6 into ASMP-7; ASMP-7 interactive telemetry resembling
  ASMP-3; ASMP-2 as a composite experiment). Lemma S adds ASMP-11 into
  ASMP-7 for the known constructions. Proving or refuting these is cheap and
  decides whether there are twelve problems or six.
- **Prior-art additions** before any external review: van der Vaart ch. 25
  (ASMP-2); prover–estimator debate (ASMP-3; verify citation); Jia et al.
  2021, Shavit 2023, Choi et al. 2023 (ASMP-7); Beirami et al. 2024, Kwa et
  al. 2024 (ASMP-8); natural-distribution undetectability follow-ups
  (ASMP-11); Barasz et al. 2014, Oesterheld 2019 (ASMP-12); Cachin 1998
  (ASMP-6).
