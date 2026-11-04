# Simulated expert review A: decision-theoretic audit of ASMP-2

## Status and adjudication

**Requested outcome:** `unresolved_refreeze_required`
**Plain-language verdict:** **INCONCLUSIVE — REFREEZE REQUIRED**

This is a simulated independent review, not a receipt from an independent
human expert team. It must not be entered into
`external_review_checklist_v0_9.json`, and it does not satisfy the two-team
gate in the v0.1 prize-style protocol.

The strong internal result is that the finite source-fiber theorem and the
finite noisy-experiment primal/dual LP are correct. The exact safety-deficiency
reduction is also correct when the decision grammar is fixed and the minimax
infimum is attained. Those findings do **not** establish that the five-part
canonical ASMP-2 target has been resolved. The proposed universal formulation
is partly a relabeling of the original minimax event, and the v0.1 statement
does not freeze enough structure to decide whether such an operational value
counts as the requested characterization.

There is also a concrete boundary defect in the claimed arbitrary-space
equivalence: without attainment, `D_G(E) <= delta` need not imply that a
certificate at confidence `1-delta` exists. This defect is repairable, but it
reinforces the need to refreeze the statement.

## Scope and independent method

I reviewed the canonical `ASMP-CANDIDATE-SET-v0.1` statement and registry, then
the candidate resolution, source-fiber theorem, decision-deficiency reduction,
finite LP, approximate extension, local counterexample, Lipschitz continuation
theorem, prior-art note, evidence ledger, and external-review packet.

I did not import or call `fiber_lp.py` or `finite_deficiency_lp.py` for the
independent numerical check. I translated the two programs directly into
SciPy's HiGHS interface and solved:

- all `438` nonempty source-fiber good-set hypergraphs with one to three worlds
  and two to three actions; and
- all `81` two-world, two-observation finite experiments formed from Bernoulli
  probabilities in `{1/4,1/2,3/4}` and nonempty two-action good sets.

Primal and dual values agreed in every case. The maximum absolute gaps were
`5.56e-17` and `1.12e-16`, respectively. The independently formulated solver
returned `1/2` for identical laws with opposite singleton good sets and `3/4`
for the symmetric `1/4` versus `3/4` one-sample experiment. Environment:
Python `3.11.4`, SciPy `1.16.2`, `scipy.optimize.linprog(method="highs")`.
This is floating-point corroboration, not a substitute for the packet's exact
rational proof.

## Answers to the four requested questions

### 1. Is the safety-deficiency reduction exactly equivalent to certification?

**Yes for finite registrations, and more generally under an explicit decision
grammar plus attainment. Not literally in the full arbitrary-space form now
claimed.**

For a Markov kernel `K` from source observations to registered policies, put

```text
s_m(K) = integral K(G_m | x) Q_m(dx).
```

Then the canonical uniform success requirement, with the kernel's randomness
included in the probability space, is

```text
inf_m s_m(K) >= 1-delta.
```

Also,

```text
sup_m [1-s_m(K)] = 1-inf_m s_m(K),
```

so minimizing the left side over `K` gives exactly the minimax failure value.
The finite LP in `FINITE_DEFICIENCY_LP_v0_7.md` is the correct epigraph form.
Its dual follows by assigning a probability vector `lambda` to the model
constraints and a free normalization multiplier `z[x]` to each observation:

```text
minimize  sum_x z[x]
subject to sum_m lambda[m] = 1,
           z[x] >= sum_m lambda[m] q[m,x] g[m,a].
```

Thus the finite theorem includes policy-selection randomization, global safety,
and utility exactly through the incidence relation `a in G_m`.

Two qualifications are load-bearing.

First, v0.1 must distinguish (i) randomness used by the learner to select a
policy and (ii) randomness internal to a deployment policy. The reduction
treats the first as probability of selecting an already-good policy. If
`L_s` and `U` instead evaluate a randomized mixture policy, that mixture must
itself be an element of `A`, and its good-set membership must be recomputed.
These are generally different semantics.

Second, an infimum is not necessarily achieved. The claimed equivalence

```text
certificate exists at confidence 1-delta  iff  D_G(E) <= delta
```

is false at equality without an optimizer. A countable discrete counterexample
uses no observations, actions `A={b,1,2,...}`, models `M={0,1,2,...}`, and

```text
G_0 = {b},
G_n = {1,2,...} minus {n}  for n >= 1.
```

For an action distribution `pi`, write `p=pi(b)`, `q=1-p`, and
`r=sup_n pi(n)`. Its worst-model success is

```text
min(p, q-r).
```

Every countable distribution with `q>0` has `r>0`, so success `1/2` is never
attained. Taking `p=1/2` and spreading the remaining mass uniformly over the
first `N` integer actions gives success `1/2-1/(2N)`. Hence `D_G(E)=1/2`, but
there is no certificate with failure at most `1/2`. All spaces are standard
Borel and every `G_m` is nonempty and measurable.

The repair is to assume compactness/closedness/continuity and prove attainment,
to use the strict implication `D_G(E)<delta`, or to formulate an explicitly
closure-valued certificate notion. The finite theorems are unaffected.

### 2. Is the source-fiber and approximate boundary sharp?

**The finite exact boundary is sharp. The total-variation statement is a valid
lower bound, but it is not by itself a complete sharp boundary for all
registered experiments.**

At a known population source law, all models in one fiber induce the same
action distribution. Maximizing its minimum good-set mass gives

```text
alpha(C) = max_pi min_(m in C) pi(G_m).
```

Selecting an optimizer separately on each finite fiber proves the stated
formula, and finite zero-sum duality gives the least-favorable mixture. The
opposite-singleton value `1/2` follows immediately. This proof is independent
of the repository enumerator.

For two worlds with disjoint singleton good actions, any successful decision
also distinguishes the worlds, so uniform-prior average success is bounded by
the Bayes testing value `(1+TV(Q_0,Q_1))/2`; worst-world success is no larger.
The deficiency lower bound `(1-TV)/2` is therefore correct and exact at the
identical-law endpoint. For asymmetric laws, uniform-prior TV need not equal
the minimax testing value, so the bound should not be advertised as the entire
sharp approximate characterization. `D_G` or the corresponding
least-favorable-prior game is the exact object.

The smooth opposite-action witness supplies a strong no-free-lunch cell:
source laws remain identical at every finite sample size while the good sets
are opposite and individually nonempty. The density theorem is also correct
for the declared unrestricted continuous continuation class, subject to the
usual nonempty-class and positive smoothness/curvature allowance. It is a
sharp result for that class, not for every frozen semiparametric class allowed
by ASMP-2.

### 3. Does the QMD deterministic-policy example refute local sufficiency?

**It refutes the literal factorization-only implication under the registered
deterministic action grammar; it simultaneously exposes that v0.1 did not
freeze the action grammar well enough for a grammar-independent verdict.**

In the stated affine Bernoulli example, information is positive and both risk
derivatives are identified, but neither deterministic action satisfies the
uniform inequality. Estimability of a derivative cannot create a robustly
feasible policy. A local theorem therefore needs a feasibility premise and an
appropriate positive safety/utility margin, or a separately typed boundary
analysis.

However, if half-half randomized deployment policies are admissible and loss
and utility are evaluated linearly under mixing, the mixture has constant loss
`1/2` and is feasible. Therefore the example should be described as a valid
counterexample to the deterministic registered version, and as evidence that
v0.1 is under-specified, rather than as an action-grammar-independent
refutation.

### 4. Does decision-specific deficiency resolve ASMP-2?

**No under the frozen v0.1 resolution protocol; a successor statement must say
what structural output is required.**

For the `0/1` loss `ell(m,a)=1{a notin G_m}`, `D_G` is simply the minimax risk
of the registered decision problem (or a decision-specific comparison with a
model-revealing oracle when every `G_m` is nonempty). This is a useful and
coordinate-invariant normalization, but the identity

```text
certificate exists iff its optimal failure probability is small
```

does not provide the requested structural coverage theorem. Likewise,
`n*(delta)=inf{n:D_G(E^n)<=delta}` is an exact definition, not a general rate
theorem, and choosing an experiment by minimizing terminal deficiency is an
optimality principle, not yet an implementable active-design characterization.

The abstract reduction lies within classical statistical decision theory and
experiment comparison; the finite fiber program is an elementary finite
zero-sum game. The packet's assembly may still be valuable, but I found no
basis for treating the abstract reduction itself as a new theorem that exceeds
the stated Blackwell/Le Cam novelty boundary. I did not conduct an exhaustive
post-2026 literature search, so this is a subsumption finding, not a novelty
priority claim.

## Five-obligation audit

| Canonical obligation | Review finding |
| --- | --- |
| Local semiparametric characterization | Adjoint-score regularity is correctly identified as prior art. The packet exposes missing feasibility and margin assumptions, but does not state and prove the full necessary-and-sufficient local policy-certificate theorem for the canonical registered class. |
| Separate local-to-global theorem | The finite source-fiber game is exact and the Lipschitz envelope theorem is a correct restricted positive result. `D_G` itself repackages global goodness; it does not characterize which topology, curvature, support, and overlap assumptions yield continuation in the general frozen QMD setting. |
| Minimax sample complexity and confidence bounds | Exact for the binary cell and variationally defined in general. The packet does not derive general rates, simultaneous bounds, or the multi-source allocation dependence required by v0.1. |
| Active environment design | `argmin_e D_G(E tensor E_e)` is correct for a fixed, equal-cost, nonadaptive one-step choice. A general next-environment rule must freeze costs, admissible interventions, conditional independence, and whether `e` may depend on observed source data. The Bellman state and transition experiment are not specified. |
| Matching no-free-lunch | Satisfied for the registered smooth indistinguishable pair and for the unrestricted finite-query/no-margin continuation class. This is the strongest completed canonical obligation. |

## Required refreeze

A successor ASMP-2 should bind at least:

1. the policy space, its topology/compactness, and both layers of
   randomization;
2. whether an exact minimax-risk definition is an admissible answer or whether
   the answer must be a structural score/tangent/covering modulus with stated
   computability or rate properties;
3. robust feasibility and positive safety/utility margins;
4. the model-class topology, support/overlap, curvature/remainder constants,
   and an attainment or closure convention;
5. the source sampling/allocation experiment; and
6. the adaptive-design observation model, intervention costs, horizon, state,
   and admissible design kernels.

With those choices frozen, the finite LP, the TV/testing lower bound, the QMD
witness, and the Lipschitz envelopes are sound components of a future
resolution. They do not presently justify either a community-level resolved
claim or `resolved_negative_subsumed_or_false` for the whole v0.1
classification program.

## Reviewed snapshot

Key SHA-256 values at review time:

```text
AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md     08115CC4CB9C5333725A820AD3CA67909E15E8625AAC3F128BDE46B88ED161F5
problem_set_v0_1.json                     30FF673486B140C178D279EB100C81A46C849BA5B9955EDDEE16C83824D43EE0
CANDIDATE_RESOLUTION_v0_6.md              B93964E9D1AFF7DFCBBE8F2FCD51BA943E768B80A813EFE48F15EECE12A2C06E
THEOREM_v0_2.md                           E036D4CFD76D4A3A1C7DD6D79E7A0D23C4A9F6D1D1646C54EFC1379C5746A9A5
DECISION_DEFICIENCY_REDUCTION_v0_3.md     6C4F5B78CC50AA9BAEBAB0DE11B4812675D6E3480DB869D260C07256B246E8C4
FINITE_DEFICIENCY_LP_v0_7.md              6BF952D5A924DC0F3433F736A2D2FDA21AAA09580CD581530049930558F98359
APPROXIMATE_DEFICIENCY_v0_8.md            4D8BA9B2A712D61D70CF4C5A43867B9A3C0113F5B660F086E71A457C5D40CE78
LOCAL_SUFFICIENCY_COUNTEREXAMPLE_v0_5.md  FD3D43412E104FA528B31D56ED0053FE9286CE6E70C5C428045FDB60D88FE8AB
LIPSCHITZ_CONTINUATION_v0_4.md            8D7F9F90D966B4696E349465F5DF663EDCD3BBF6F975656114B36578F550323A
```

**Final simulated-expert outcome:** `unresolved_refreeze_required`.
