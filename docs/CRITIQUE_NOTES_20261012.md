# RSITopology critique notes — 2026-10-12

Author: Claude (Fable 5.1), at Patrick's request, as the first step before
working on the problems. These are review notes, not a result. Every claim
below names the file it is about; where I computed something, the computation
is shown so it can be checked.

## 0. What was read and how

- Clone of `MoralityLabAI/RSITopology`, branch
  `feat/spectral-bundle-v0.3-bifiltration` at `74feaef` (2026-08-18). It is
  678 commits ahead of `main` (`659b5b1`, 2026-07-15). PR #1 against `main`
  has been open since 2026-07-15. All 683 commits carry one author; the
  workflow described in `ultra-experiments/COLLABORATION_PROTOCOL.md` and
  `ultra-experiments/millennium/STALE_ASMP_WORKPLAN_20260803.md` is
  agent-driven (disjoint directories per agent, serialized commits).
- Two programs live here. **(A)** Identity geometry: spectral bundle, lineage,
  holonomy, control-risk gate, edit sectioning, attestation API
  (`rsi_topology/`, `reports/`, `godel-globe/`, `protocols/`). **(B)** The AI
  Safety Millennium Problems, ASMP-1..12 plus 5A
  (`ultra-experiments/millennium/`, 3,451 tracked files).
- Read in full: `AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md`,
  `V0_2_SCOPE_EXPANSION_DRAFT.md`, `REFEREE_AUDIT_v0_1.md`,
  `PROBLEM_PROGRESS_SUMMARY_v0_1.md`, `ASMP_ATTEMPT_COVERAGE_AUDIT_20260803.md`,
  `STALE_ASMP_WORKPLAN_20260803.md`, the ASMP-9 README (v0.1–v0.82), ASMP-3
  v2.20/v2.21, ASMP-1 v0.2, ASMP-4 v0.6 and the v0.36 stop certificate, the
  headline RESULT of every other ASMP, the three Qwen reports, the grant
  application, the mathematical program, and the July progress report.
- Not yet redone: the exact censuses themselves. A venv was built
  (`.venv`, gitignored); the test baseline is in §7.

Volume, for calibration (feature branch, `ultra-experiments/millennium/`):

| Artifact kind | Count |
|---|---:|
| `RESULT*.md` | 135 |
| `*THEOREM*.md` | 140 |
| `*AUDIT*.md` | 132 |
| `*PRIOR_ART*` | 123 |
| `*REGISTRATION*` | 122 |
| obligation matrices | 47 |
| stop certificates | 8 |
| `verify*.py` / `run*.py` / `test_*.py` | 200 / 191 / 303 |
| Markdown / Python / JSON bytes | 4.2 MB / 8.8 MB / 76 MB |
| files containing "does not resolve" or "remains unresolved" | 233 |
| occurrences of the word "classical" | 659 |
| occurrences of `candidate_new` | 2 |

## 1. Summary verdict

1. **The ASMP set is an atlas of problem templates, not a set of problems.**
   Every statement opens with a "Freeze:" list of six to twelve objects the
   solver must choose. Clay problems are one sentence with no free
   parameters. The ASMP-4 history is the demonstration: 37 versions
   (`asmp4_*`) were spent discovering that the template did not determine a
   problem, followed by a stop certificate asking for "normative
   registration". A template whose instantiation is adjudicated by its own
   authors cannot carry a prize, and the referee audit's graduation criteria
   (closed formal core, invariance, two-sided rule) are not met by any entry
   under the document's own standard.
2. **Resolution rule 10 has a loophole and the work has already walked
   through it twice.** "Undecidability of the frozen uniform decision family"
   is automatic for any program-encoded, tail-determined, live class (Lemma
   in §2.2; it is Rice's theorem). ASMP-3 v2.20/v2.21 and ASMP-1 v0.2 are
   "candidate negative resolutions" obtained exactly this way. They teach
   nothing about weak verification or mechanism identifiability. Both
   packages notice that the force of the result depends on the encoding
   grammar (`UNIFORM_MEMBERSHIP_UNDECIDABILITY_THEOREM_v2_20.md` §7,
   `asmp1_resolution_boundary_v0_2/RESULT_v0_2.md` "Claim boundary") but do
   not draw the general conclusion: the rule, not the problems, is at fault.
3. **The mathematics produced is almost entirely exact finite census of
   classical facts, and the repo says so itself.** The structured
   observation-kernel motif note deflates the ASMP-1/9/10/11 seeds to
   rank–nullity; the ASMP-4 chain credits Karp, Kraft, Ziemian, entropy
   games; ASMP-9 credits Buehler, Tutte, Azrieli–Chambers–Healy, Set Cover.
   This is honest and the instruments are correct, but it means the 678
   commits contain no progress on any problem as stated. The two occurrences
   of `candidate_new` in 1,203 Markdown files are the repository's own
   measure of this.
4. **Every real-model result is negative, forced, or synthetic-positive.**
   ASMP-1 Qwen tomography: live directions, no stable interaction algebra,
   specificity gate failed in the wrong direction. ASMP-8 Qwen gates (two):
   not established. ASMP-9 v0.80: negative; v0.82 transport: negative; v0.81:
   positive on an exact finite-MDP softmax demonstrator built by the
   protocol. Holonomy on Qwen3.5-0.8B: no supported identity rank, so no
   graph. Qwen0.8B precision paper: the holonomy sign was geometrically
   forced (its own Theorem 1). The reporting is scrupulous; the pattern is
   the repo's real scientific finding and should be stated as such in the
   README rather than buried under instrument validations.
5. **The flagship holonomy experiment violated the repo's own liveness
   rule.** `COLLABORATION_PROTOCOL.md` requires a liveness certificate (one
   admissible case where the conclusion holds and one where it fails) before
   a primary outcome is read. The rank-one `w1` test on the 2×4 ladder could
   not fail: under the registered lineage floor the angle budget of every
   cycle is below 180° (§3.3). This was computable from the protocol before
   capture.
6. **The obligation-matrix mechanism is a treadmill.** ASMP-9 has 87
   sub-packages; each ends "ASMP-9 remains unresolved; the obligation matrix
   moves next to …". The chain went from value identifiability to graph
   cohomology, Bradley–Terry conditional fibers, Tutte-polynomial
   #P-hardness, Buehler confidence tables, Set Cover, and Luce/RUM
   trichotomies. Each step is correct; none is on a path to the problem. Stop
   certificates (8) are the best device in the repo; obligation matrices (47)
   are the worst.
7. **Specific conceptual faults in individual statements** (§4): ASMP-8's
   frontier is close to tautological as written and its KL slice is largely
   settled in the literature; ASMP-10 is vacuous without a model class, as
   its own prefix-obstruction result states; ASMP-11's negative region is
   closed for every polynomial-time interpretability access class by a
   simulation argument, so what remains is an empirical premise about natural
   models; ASMP-4's "registration fork" is resolved by the existential
   quantifier already in the definition of `R_K`; ASMP-5's negative half is
   Rice again; ASMP-2's local conjecture is close to the classical
   regular-estimability characterization; ASMP-6 and ASMP-7 are the best
   posed, and their work is toy-scale.
8. **Engineering:** no CI and no `.github/`; `main` is 678 commits stale;
   17 zip bundles (4.1 MB) in the root; 76 MB of JSON receipts; `artifacts/`
   is gitignored yet 38 artifact files are tracked; duplicate flat module
   names prevent one pytest invocation (acknowledged in the stale workplan);
   23 protocols are `registered_not_run`; `torch`, `sympy`, `networkx`,
   `scikit-learn` are used but not declared in `pyproject.toml`; receipts bind
   to `D:\Download\...` and `D:\Research_Engine\...` paths that are not in the
   repo.

## 2. The concept: the problem set

### 2.1 Templates versus problems

Take ASMP-4. The region is defined as

> `R_K = {(R_r,R_w): there exists a registered causal code C with r_r(C) <= R_r and r_w(C) <= R_w such that every x_0 in K_0 remains in K for every allowed disturbance sequence}`

and the architecture paragraph says "A causal sensor encoder emits only the
read transcript; a controller receives only those symbols and emits the write
transcript; an actuator decoder maps write symbols to controls." The code `C`
therefore *contains* the sensor encoder, and `R_K` is an infimum over all
admissible codes. The v0.6 "forced raw sensor" branch
(`asmp4_registration_fork_v0_6/RESULT.md`) adds a constraint that the text
does not contain. Under the plain reading the "computed sensor" branch is the
problem, the fork disappears, and v0.6's parametric theorem
(`[log2 kappa, inf) x [log2 m, inf)` for a sensor grammar `Gamma`) survives as
a theorem about a *restricted* class. Thirty subsequent versions and two stop
certificates (v0.14, v0.32, v0.36) rest on treating the ambiguity as
unresolvable without "attributable semantic adjudication". A human
mathematician would have resolved it by reading the quantifier, or proved the
parametric theorem and moved on. The harness could do neither because the
governance rules forbid it from choosing an interpretation. That is a design
flaw in the process, not a property of ASMP-4.

The same structure appears everywhere: ASMP-1 freezes `E, I, O, Q, G, F, B,
kappa, gamma`; ASMP-3 freezes `R_n, A_n, H, H_tilde, Refute_n`, the noise
class, three budgets; ASMP-6 freezes seven objects; ASMP-7 freezes `P, G,
K_adm, G_j`. These are research programs. Their "resolutions" are relative to
the choices. The set would be better presented as "verification-theoretic
frontiers for AI oversight: an atlas with worked finite instances", which is
what it is, and the Millennium framing dropped until at least one entry has a
one-paragraph parameter-free statement that two outside mathematicians agree
is open.

### 2.2 The undecidability loophole

**Lemma (program-encoded index sets).** Let instances be given by indices `e`
of total computable generators producing a family indexed by depth `d`
(this is the convention of `WV-FIX-UCOMP` in ASMP-3 v2.20 and of the
computable-real Cauchy names in ASMP-1 v0.2). Let `P` be a property of
generated families that is (i) extensional, (ii) tail-determined (membership
depends only on behaviour for all sufficiently large `d`; v2.20 §1 states
this explicitly: "finite prefixes are ignored, as in ordinary asymptotic
complexity classes"), and (iii) live (some generator is in `P`, some is not).
Then the index set of `P` is undecidable, and if `P` is `Sigma_2`-definable
the positive index set is not recursively enumerable.

*Proof.* Pick `e_in` in `P` and `e_out` not in `P`. For a Turing machine `M`
define the total generator that behaves as `e_in` at depth `d` if `M` has not
halted within `d` steps and as `e_out` otherwise. If `M` never halts the
generated family equals `e_in`'s, hence is in `P`. If `M` halts at `t`, the
family agrees with `e_out`'s for all `d >= t`, hence by tail-determination is
not in `P`. Thus `NONHALT` many-one reduces to the index set. This is the
standard proof of Rice's theorem; the v2.20 reduction (oracle answers `z_i`
until `e` halts, then `0`) and the v0.2 reduction (`c_e = 0` if `e` never
halts, else `2^-t`) are this construction with `e_in` and `e_out` chosen as
the problem's own liveness examples. ∎

Consequences:

- Graduation standard 3 (liveness) plus resolution rule 10 (undecidability of
  the frozen uniform decision family) make every program-encoded ASMP
  "negatively resolvable" by a three-line argument that never mentions the
  problem's content. ASMP-3, ASMP-1, and ASMP-5 (whose "safe forever"
  predicate is explicitly Rice) are all in this position; ASMP-10 would be if
  training processes were program-encoded.
- The v2.20 game is otherwise trivial: parity of a `d`-bit string, one
  coordinate query, `BSC(1/5)`. All of the hardness lives in the halting
  test. Likewise v0.2's two mechanisms `(1+c_e)X+A` and `X+A` differ by a
  computable real whose equality to zero is undecidable; this is Specker-era
  computable analysis, not identifiability theory.
- The repair is a grammar clause, not a new problem: instances must be
  finitely presented with certified gaps (rational data, explicit circuits,
  margins `kappa, gamma` given as rationals), so that the uniform decision
  family is decidable and the content becomes *complexity*. The ASMP-1 v0.2
  package already shows the decidable lane (rational semialgebraic via
  quantifier elimination). A draft amendment is in
  `ultra-experiments/millennium/ASMP_V0_2_STATEMENT_REPAIRS_DRAFT_20261012.md`.

### 2.3 Safety reduction is asserted, not met

Graduation standard 8 requires "a proved implication for the declared risk
functional". Every "Safety consequence" section is conditional on the frozen
predicate capturing the intended risk, and the preamble says plainly that the
mathematics "cannot prove that the object captures all human values". That is
the right epistemic stance, but it means the problems are verification and
identification theory, and the title overclaims. The stack diagram
(ASMP-1 → … → ASMP-7) is labelled "conceptual workflow, not pairwise
mathematical independence"; the referee audit lists plausible reductions
(ASMP-6 into ASMP-7, ASMP-7 telemetry resembling ASMP-3, ASMP-2 as a
composite experiment). None has been attempted, which is the cheapest
mathematics on offer and the most useful for deciding whether there are seven
problems or three.

### 2.4 Novelty posture and prior-art gaps

The prior-art-before-freeze standard and the universal "classical" labelling
are good practice. Two problems remain. First, a reader cannot find the two
`candidate_new` items among 1,203 files; the repository needs a single
page listing every claim the authors believe is new, with its package. Second,
the prior-art lists in the canonical statements miss work that bears directly
on the frontier being claimed:

| Problem | Missing reference | Why it matters |
|---|---|---|
| ASMP-2 | van der Vaart, *Asymptotic Statistics*, ch. 25 (regular estimability iff pathwise differentiability on the tangent set) | the local conjecture is close to this theorem applied to the risk derivative along `T_adv`; the novelty must be the global continuation, which nothing in the repo touches |
| ASMP-3 | Brown-Cohen, Irving, Piliouras, *Avoiding obfuscation with prover-estimator debate* (2025; verify citation) | directly addresses the obfuscated-argument frontier the statement names as its open content |
| ASMP-7 | Jia et al., *Proof-of-Learning* (S&P 2021); Shavit, *What does it take to catch a Chinchilla?* (2023); Choi et al., *Tools for verifying neural models' training data* (2023) | ASMP-7 is a compute-governance attestation problem and cites none of the compute-governance verification literature |
| ASMP-8 | Beirami et al., *Theoretical guarantees on the best-of-n alignment policy* (2024); Kwa, Thomas, Garriga-Alonso, *Catastrophic Goodhart* (2024) | the v0.2 draft's proposed KL/best-of-n "registered slice" is the subject of both; the heavy-tailed side of the KL frontier is already settled |
| ASMP-11 | follow-ups to Goldwasser et al. on distinguishability from *naturally trained* models | the only non-collapsed region of the access lattice (§4, ASMP-11) |
| ASMP-12 | Barasz et al., *Robust cooperation via provability logic* (2014); Oesterheld, *Robust program equilibrium* (2019) | the modal-agent proof-budget census the v0.2 draft proposes is set up by the first; the second is the robustness notion the statement asks for |
| ASMP-6 | Cachin, *An information-theoretic model for steganography* (1998) | the "monitor advantage" is Cachin's epsilon-security; should be named |

### 2.5 Internal "independence"

The protocol language (prospective registration, sealed hashes, independent
verifier, hostile referee, 0/2 external reproductions) describes a review
system. What exists is one author's agent pipeline writing the registration,
the runner, the "independent" verifier, and the referee note in the same
directory within hours. Sealed hashes bind bytes; they do not bind judgment.
The 415 commits in the week ending 2026-08-03 (stale workplan) cannot have
been reviewed by anyone. This is reproducibility, which is valuable, labelled
as independence, which it is not. Until an outside reader has reproduced one
package, every "verified" in the repo should be read as "replayed".

## 3. The concept: identity geometry

### 3.1 What is sound

The synthetic chain is coherent: band-occupancy consensus
(`reports/mathematical_program.md`), lineage as chordal overlap and
worst-direction retention (`reports/bundle_lineage_hypothesis.md`), holonomy
as the discarded polar factor (`reports/monitor_holonomy_insight.md`), the
control-risk bound `||M-I|| <= sum_e (1-sqrt(W_e)) + ||H-I||`
(`docs/CONTROL_RISK_THEOREM.md`), edit sectioning with fixtures built to lose
(`docs/EDIT_SECTIONING_V03_RESULTS.md`). The band-failover finding
(`reports/files4_mechanism_review.md`) is a genuinely useful lesson about
summary layers hiding categorical selection changes. The identity-rotation
unit control (occupancy equal to `8.9e-16`, lineage `0.00123`, gates flip) is
a clean instrument validation.

### 3.2 The real-model record

| Run | Report | Outcome |
|---|---|---|
| Qwen3.5-0.8B holonomy, four states | `reports/QWEN08_HOLONOMY_FALSIFICATION_V0_1.md` | 0/512 nodes supported any rank at 2 prompts per cell; no graph built; pooled diagnostic recovers a global object |
| Qwen0.8B precision ladder | `reports/QWEN08_PRECISION_GEOMETRY_PAPER_V0_1.md` | margins compress under NF4; sentinel not precision-specific; every `w1` sign `+1`, proved forced |
| Qwen0.8B projector tomography (ASMP-1) | `asmp1_qwen_projector_tomography/RESULT.md` | directions causally live (median effect 4× matched random); degree-two terms hurt held-out prediction in 9/9 subconditions; specificity gate failed in the opposite direction |
| Qwen3-1.7B identity prereveal | `reports/qwen3_1p7b_identity_prereveal_result.md` | (not re-read in detail) listed as failure localization |
| Dense local holonomy follow-up | `protocols/qwen08_dense_local_holonomy_v0_1` | registered, not run |

The grant application's three bets are therefore untested rather than failed,
but the premise under all three (a context-stable, transportable low-rank
identity object at 0.8B scale with 2–16 prompts per cell) has taken three
hits. The honest summary is: the instruments work on planted fixtures; on
models the object they measure has not been shown to exist at the sample
sizes used.

### 3.3 Rank-one holonomy liveness is a protocol-level constraint

Theorem 1 of the precision paper: a rank-one cycle with edge principal angles
`alpha_i` can have negative holonomy only if `sum_i alpha_i >= pi`. With
retention floor `tau` per edge, `alpha_i <= arccos(sqrt(tau))`, so a cycle of
length `L` is live only if

```text
L * arccos(sqrt(tau)) >= pi.
```

Numbers: `tau = 0.90` gives `arccos(sqrt 0.90) = 18.4 deg`, so `L >= 10`;
`tau = 0.50` gives `45 deg`, so `L >= 4`. The 2×4 ladder's longest simple
cycle has 8 edges. The registered-not-run dense local follow-up (PR #1 text:
"lineage floor 0.90; connected 2×4 cells have beta_1 = 3") therefore cannot
produce a negative rank-one holonomy on any cycle: at rank 1 it is dead by
design. Ranks 2–8 remain live (SO(r) angles can be nonzero below the budget),
so the protocol should drop the rank-1 `w1` channel, keep the graded angle
budget, and add the inequality above as a registration precondition.

There is also a structural tension worth stating: rank-one holonomy becomes
live only when lineage is already poor (`tau` small) or cycles are long, so in
the regime where identity is good it cannot add information beyond lineage.
The graded "frustration margin" is the right replacement, but its claim
boundary should say this.

## 4. Problem-by-problem notes

Format: statement issue; work done; what would move it. "Classical" means the
repo itself labels the result classical.

**ASMP-1 (identifiability modulo symmetry).** The Cut-Separation iff was
refuted internally in both directions (`asmp1_cut_separation_audit`); good.
The replacement criterion "identifiable iff `Q/G` factors through the
observation experiment" restates the definition of identifiability. The
decidable lane is Tarski–Seidenberg; the undecidable lane is §2.2; the linear
lane is linear algebra. The one informative experiment is the Qwen tomography
run: certified directions are causally live but their interactions are
context-dependent, which is a real negative about the "superstructure"
hypothesis. *Move it:* v0.2 over a decidable grammar (rational polynomial
mechanisms of bounded bit-size) asking for intervention-query complexity of
recovering `Q/G`, tied to the Sutter et al. non-linear-alignment question
(restrict the alignment map class, then ask what is identifiable).

**ASMP-2 (shift-spanning certification).** The local conjecture is close to
the classical regular-estimability characterization (van der Vaart ch. 25)
applied to the derivative of `L_s` along `T_adv`; the referee audit already
calls the local part conditional. The global continuation is the content and
has no work. Work: one forced counterexample (`asmp2_crossed_shift`), one
active-design census rejecting a myopic selector. *Move it:* drop the local
conjecture with attribution and pose the global problem concretely: for a
parametric family with compact `Theta_adv` and a known curvature bound, what
is the minimal source design certifying `sup_Theta_adv L_s <= eps`? That is
an optimal-design and covering problem with a chance of a sharp answer.

**ASMP-3 (weak-verifier frontier).** The literal iff refuted both ways
(v0.7, v2.5) shows the refutation-dimension invariant was the wrong object;
useful. The finite "frontiers" (`distance_TV(conv(H), conv(F))`, sequence
form) are game values. v2.20/v2.21 are §2.2. The named open content
(obfuscation, efficient honest refutation, correlated semantic noise) is the
doubly-efficient-debate frontier and nothing here advances it. Work: 39
packages, 486 tests. *Move it:* decidable grammar (circuits of size `T(n)`),
define the class as a complexity class, and ask the complexity question: is
there a task in P (or NP) outside the polylog-query noisy-judge debate class
under a cryptographic assumption (obfuscation)? Check the prover–estimator
debate paper first.

**ASMP-4 (two-port confinement).** The object is real and the write side is
genuinely not classical. The fork is resolved by the quantifier (§2.1). The
v0.24–v0.35 chain (support functionals, cycle polytopes, bisimulation
transfer, Kraft rounding, mean-payoff games) is competent finite-automata
theory, but the statement is about nonlinear uncertain control with a
normally hyperbolic invariant manifold, and no smooth plant was ever treated
beyond a one-dimensional rational fixture. *Move it:* take the computed-sensor
reading and do the linear case first. For `x' = Ax + Bu + w` with evaluator
`y = Cx`, full observability and controllability of the `y`-relevant unstable
modes, I expect both thresholds to equal `sum log2|lambda|` over those modes
and the region to be the quadrant (the volume argument applies at either
interface). If that is right, ASMP-4's content is entirely in the quotient,
partial-information, and finite-authority cases, and the first theorem to
write is "rectangularity for LTI, and a smallest non-rectangular witness".
The repo's v0.7 wedge (non-unique safe actions, finite alphabet) is a
candidate witness; it should be stated as a theorem about the linear-with-
constraints class rather than as an ASMP-4 "boundary result".

**ASMP-5 (reflective safety).** The dichotomy's negative half is Rice. The
positive half is proof-carrying code with an assumed-sound kernel, which is
known. The open content is the shape of the frontier for verifier
replacement (Löb, Critch's bounded Löb). The 4-bit checker-grammar census
(`asmp5_verifier_drift/v0_3_inductive_root`) does not touch it. *Move it:*
promote ASMP-5A to the main statement: fix one reflective hierarchy (e.g.
iterated consistency extensions of PA as the verifier ladder), fix a budget
`k`, and ask for the degradation functions `g_lower(k), g_upper(k)`.

**ASMP-6 (collusion capacity).** Well posed relative to covert communication;
the "tensorizing resolving modulus" and learned cover/monitor are where
novelty lives, and also where the problem may fail to have a fixed channel
(a learned monitor makes the game non-stationary). Work: one-shot
balanced-cover parity (`m` even/odd) and a v0.3 multiletter grid; toy.
*Move it:* one concrete theorem: for a monitor restricted to a finite-VC or
`k`-th-order-statistics class and cover `P_0`, show positive-rate collusion
by resolvability over the set of `P_1` matching the monitor's statistics, and
the matching converse; then the active-auditor zero-capacity result.

**ASMP-7 (attestability).** Well posed; Blackwell composite testing with a
transformation semigroup is the right frame. Prior-art gap on
compute-governance verification (§2.4). Work: finite registries, selective
suppression grids; instruments. *Move it:* the "efficiency envelope" clause is
the content; state and prove which resource predicates become attestable
given a frozen efficiency bound plus proof-carrying commitments. That is a
theorem with cryptographic ingredients and a real audience.

**ASMP-8 (Goodhart frontier).** As defined, the regret bound follows from a
triangle inequality once `D_eps` is uniform over `Pi_lambda` (the statement's
own positive example), and is unbounded once `D_eps` is a reference-measure
condition (its own negative example). The frontier is therefore the
relationship between `D_eps` and `Pi_lambda`, which the hostile-referee
question in the v0.2 draft already asks and no package answers. The KL
pressure slice is the interesting one, and it is largely settled: light-tailed
proxy error under `p_0` gives regret `O(sigma sqrt(KL))` by change of measure
(derivation in the repairs draft, sharp for Gaussian error), and heavy-tailed
error gives unbounded regret at any KL budget (Kwa et al. 2024). Work: the
movement-weighted deterministic audit certificate (`v0_6_adaptive_reuse`) is a
sound elementary bound; both Qwen control gates negative. *Move it:* restate
ASMP-8 as the tail-class classification over KL-ball reachable sets, credit
the known halves, and ask the open part: the exact frontier for sub-exponential
and polynomial tails, and the finite-sample proxy-training version.

**ASMP-9 (value identifiability under access).** The problem is reasonable as
an access-threshold question after Skalse et al. The seed (exact cardinal loop
returns, graph cohomology) answers a question no interface asks. The chain
then wandered for 87 packages. *Move it:* fix one interface that exists
(pairwise comparisons with a known link, as in RLHF), fix the gauge
(potential shaping plus positive affine), and ask for the minimal comparison
design identifying the quotient as a function of the MDP. The repo's v0.7,
v0.9, v0.13 pieces are ingredients. Prove it, then stop.

**ASMP-10 (capability transitions).** Vacuous without a model class, as the
repo's own `prefix_obstruction/RESULT_v0_1.md` says ("the claimed training
family needs a stated regularity assumption"). The negative half is trivially
true for any non-identifying observation class; the positive half is the
developmental-interpretability research program, which is empirical. *Move
it:* either demote to a preregistered empirical benchmark, or restate as a
Bayes-error question for a specific family (e.g. two-layer networks on
modular addition: is time-to-grok a function of the LLC-trajectory prefix?).

**ASMP-11 (interpretability-access detectability).** Simulation closure: any
access class whose oracles (activations, gradients, Jacobians, ablations,
edits, adaptive inputs) are polynomial-time computable from the weights and
data is simulable by the white-box distinguisher of Goldwasser et al., so
white-box undetectability for a model class implies undetectability under
every such access class. The lattice is nontrivial only below white-box
(bounded black-box budgets, sub-polynomial computation) or relative to model
distributions in which the cryptographic constructions are atypical. The
second is an empirical premise about training, not a theorem frontier. Work:
a planted-parity rank–nullity ladder (`r + s = k`); the real-model ladder
never ran (preflight stop). *Move it:* restate as undetectability relative to
the distribution of naturally trained models, and look for existing results
on that question before any new census.

**ASMP-12 (program equilibrium under resource bounds).** Well posed after the
Tennenholtz correction; the selection-dynamic question is the good one;
safety relevance is indirect. Work: finite survival correspondences over a
three-program universe, an inertial selector. *Move it:* do the modal-agent
proof-budget census the v0.2 draft proposes (Barasz et al. agents, GL
provability logic is decidable) for all 2×2 games; that is finite, exact,
and would be the first ASMP artifact with a direct line to the literature's
open questions.

## 5. Process and engineering

- `main` should either receive PR #1 or be retired; a branch named
  `spectral-bundle-v0.3-bifiltration` holding the entire ASMP program is
  misleading to any visitor.
- Add CI that runs `tests/` and one `pytest` process per ASMP package
  directory (the duplicate `run.py`/`verify_independent.py` names make a
  single collection impossible; a `conftest.py`-free per-directory loop is
  the fix). Declare `torch`, `sympy`, `networkx`, `scikit-learn`.
- Move the 17 root zips to GitHub releases; stop tracking `artifacts/`
  (38 files tracked against the ignore rule) and consider whether 76 MB of
  JSON receipts belong in git at all; a receipt is reproducible by
  construction.
- Receipts reference `D:\Download\asmp_candidate_extensions_v0_1.md`,
  `D:\Research_Engine\runs\...`; the hashed inputs should be in the repo or
  the receipts should say they are unavailable.
- Twenty-three protocols are `registered_not_run`. Each is a liability for a
  reader who takes "registered" as "done"; list them in one place.
- Replace obligation matrices with a one-line rule: a successor is admissible
  only if it is on the critical path to the problem's resolution obligations
  or closes a named prior-art gap. ASMP-9 v0.21–v0.53 would not have passed
  that rule.
- Seal hashes on canonical bytes. `.gitattributes` mandates LF, but at least
  one sealed anchor (ASMP-11 `prior_anchor_v0_2.json`) was computed on a CRLF
  working copy and fails on every compliant checkout (§7). A sealing script
  should normalize or refuse CR bytes.

## 6. Recommendations, in order

1. **Fix the statements before producing more results.** Amend rule 10 and
   freeze decidable instance grammars (§2.2); resolve the ASMP-4 quantifier
   (§2.1); restate ASMP-8 as a tail-class problem; give ASMP-10 a model
   class; restate ASMP-11 relative to natural model distributions; move
   ASMP-5A to the front of ASMP-5. Draft:
   `ultra-experiments/millennium/ASMP_V0_2_STATEMENT_REPAIRS_DRAFT_20261012.md`.
2. **Write the one-page novelty ledger** (every `candidate_new` claim, with
   package and the strongest nearby prior result).
3. **Close the prior-art gaps in §2.4** before any external review request.
4. **Add the holonomy liveness precondition** (§3.3) to the dense-local
   protocol and drop its rank-1 `w1` channel.
5. **Pick one problem and do mathematics on it.** My recommendation is
   ASMP-4's linear two-port case (rectangularity or a smallest
   non-rectangular witness), because it is the only entry where the repo's
   tools meet the statement's actual object and where I do not already know
   the answer. Second choice: the ASMP-12 modal-agent census.
6. **Repo hygiene** (§5), in one PR.

I am starting on items 1 and 4 now; see the repairs draft.

## 7. Test baseline, 2026-10-12

Environment: Windows 11, Python 3.12.10 venv with numpy 2.5.4, scipy 1.18.1,
scikit-learn 1.9.1, sympy, networkx, pytest 9.1.1, matplotlib, hypothesis;
no torch. `PYTHONPATH` set to the repo root. `core.longpaths=true` set in the
clone because ASMP-11's tests shell out to `git show` with long paths.

**Top-level `tests/`** (51 files): first run 245 passed, 5 failed, 1
collection error (85 s). After installing `matplotlib` and `hypothesis`: 251
passed. The remaining failures are all portability defects, not logic:

| Test | Cause |
|---|---|
| `test_godel_capture_hardening::test_float32_conversion_cache_excludes_head_and_hashes_tensor` | needs `torch` (not installed here; environment) |
| `test_qwen_controller_task_capture` (2 tests) | reads `C:\projects\HybridTRMLDT\ldt_trm_research_gym_v0_0_2\...\qwen08_controller_task_prompt_manifest_v0_1.json`, a file in another repository by absolute path |
| `test_holonomy_from_spec::test_independent_prose_specification_reproduces_headline_control` | imports `artifacts/external_fable_files7/holonomy_from_spec_repro.py`, which is untracked (`artifacts/` is gitignored) |

**`validate_problem_set.py`**: fails with `receipt hash mismatch: README.md`.
The sealed `VALIDATION_RECEIPT_v0_1.json` (commit `9f9505e`, 2026-07-18)
matches the README of that commit; the README was edited in `933a4b6`
(2026-07-20, "Attribute ASMP-10 obstruction and freeze prior-art gate") and
the receipt was never re-sealed. The other four sealed files match. The
candidate set's own structural validation has therefore been red on this
branch for almost three months.

**One package per ASMP, each in its own process:**

| Package | Result |
|---|---|
| ASMP-1 `asmp1_resolution_boundary_v0_2` | 9 passed |
| ASMP-2 `asmp2_crossed_shift` | 7 passed |
| ASMP-3 `asmp3_uniform_membership_undecidability_v2_20` | 12 passed |
| ASMP-4 `asmp4_registration_fork_v0_6` | 19 passed (54 s) |
| ASMP-5 `asmp5_verifier_drift/v0_3_inductive_root` | 12 passed |
| ASMP-6 `asmp6_semantic_collusion_frontier/v0_2_balanced_cover` | 24 passed |
| ASMP-7 `asmp7_attestability_frontier` | collection error when pointed at the directory (sibling subpackages share module names); 10 passed when pointed at `coverage_robustness_v0_3/test_coverage_robustness.py` |
| ASMP-8 `asmp8_goodhart_frontier_census/v0_5_audit_efficiency` | 3 passed |
| ASMP-9 `asmp9_reward_gauge_census/capped_simplex_modulus_v0_63` | 8 passed |
| ASMP-10 `asmp10_capability_transition/prefix_obstruction` | 12 passed |
| ASMP-11 `asmp11_access_ladder/covering_frontier_v0_2_1` | 25 passed, 2 failed; one failure was the long-path issue (fixed by `core.longpaths`), the other is real: `prior_anchor_v0_2.json` records `source_frontier_sha256 = 2551f33e…`, which is the SHA-256 of `covering_frontier_v0_2/artifacts_v0_2/frontier.csv` *with CRLF line endings*; the LF file mandated by `.gitattributes` hashes to `9fd87492…`. The anchor was sealed (`a24d869`, 2026-08-03) on a CRLF working copy. |
| ASMP-12 `asmp12_program_equilibrium/v0_3_constructible_survival` | 10 passed (77 s) |

The exact censuses replay; what is wrong is the binding layer around them,
which is the layer the repository advertises most.
