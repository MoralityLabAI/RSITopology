# Simulated expert review B: QMD and continuation audit of ASMP-2

## Status and provenance

**Plain-language verdict:** **INCONCLUSIVE — REFREEZE REQUIRED**

This is a simulated independent review produced with an Ultra-reasoning agent,
not a receipt from an independent human expert team. It must not be entered in
`external_review_checklist_v0_9.json`, and it does not satisfy the frozen
two-team acceptance gate.

The coordinating agent persisted this report from the simulated reviewer's
completed derivations after interrupting a long-running final-emission step.
The mathematical findings below are the simulated reviewer's; the coordinator
has not promoted them to external evidence.

## Independent reconstruction

The review reconstructed the smooth opposite-action example directly from

```text
g(theta) = (16/9) theta^2 (theta^2-1/4)^2,
P(Z=1) = 1/2 + theta/8,
P_s(Y_a=1) = 1/2 + theta/16 + a s g(theta)/8.
```

The supplied result JSON and verifier outputs were not used as premises. The
review separately checked the source jets, score experiment, Fisher
information, probability bounds, risk curvature, globally good action sets,
all-sample decision value, density/packing argument, Lipschitz envelopes, and
the deterministic local counterexample.

## Findings on the smooth QMD witness

The core construction checks out.

1. `g` and `g'` vanish at each source point `{-1/2,0,1/2}`. Consequently the
   two hidden worlds induce exactly the same complete source law and source
   score for every finite sample allocation.
2. The independent Bernoulli-channel Fisher contributions at `theta=0` add to

   ```text
   4[(1/8)^2 + 2(1/16)^2] = 3/32.
   ```

3. The probability channels stay uniformly away from zero and one. The direct
   bounds are tighter than the qualitative compact-subset claim, so dominated
   finite-alphabet QMD and common full support are valid.
4. Direct differentiation gives `max |g''| = 386/9`; division by eight gives
   the stated action-risk curvature bound `193/36`.
5. For world `s`, action `a=-s` is uniformly safe at threshold `9/16`, while
   `a=s` has loss `11/16` at `theta=1`. Thus

   ```text
   G_- = {+1},  G_+ = {-1}.
   ```

6. Since every finite source experiment has identical laws in the two worlds,
   every decision rule induces the same distribution on actions in both.
   Maximizing the smaller mass of the two opposite singleton actions gives
   exactly `1/2`. This proves the all-`n` minimax value and infinite sample
   complexity for every requested failure probability below `1/2`.

This is a valid, unusually clean no-free-lunch witness. It establishes that
source score identification, positive Fisher information, smoothness, full
support, bounded curvature, and individual feasibility do not jointly imply a
uniform source-only certificate.

## Continuation and active-design audit

The negative continuation idea is sound, but two theorem statements need
repair before publication.

First, Theorem 3 says that the registered class *contains* all continuous
families and then uses continuity to prove the dense-source sufficiency
direction for every member of the class. Containment is not enough: the class
could also contain discontinuous families that agree on a dense source set.
The correct hypothesis must require every admissible family to be continuous,
while also requiring enough richness to contain the bump perturbations used
for necessity. For example:

```text
the class is a subset of the continuous full-support families and contains
the stated local bump pairs.
```

Under that repair, equality on a dense source set extends by continuity, and a
non-dense source set admits an opposite-sign bump in an unsampled open region.

Second, the randomized `T`-query packing argument requires a deployment domain
with arbitrarily large finite packings of disjoint candidate bump regions.
That is true for a positive-dimensional Euclidean domain with interior, but it
does not follow merely from the broad phrase “compact Euclidean domain.” A
finite domain, for example, can be exhausted. The corollary should state the
needed infinite packing/non-isolated-region hypothesis. With it, the bound

```text
average success <= 1/2 + T/(2N)
```

is correct, and choosing `N` large proves the claimed finite-query obstruction
when no positive margin is frozen.

The McShane/Whitney Lipschitz result is correct for the explicitly registered
product class of compatible loss and utility continuations. Its fill-distance
criterion gives a genuine positive theorem and identifies the missing
smoothness/margin scale. It is classical optimal-recovery machinery and does
not by itself resolve the general semiparametric program.

## Local-factorization audit

The affine Bernoulli example in
`LOCAL_SUFFICIENCY_COUNTEREXAMPLE_v0_5.md` correctly shows that estimability of
pathwise derivatives cannot manufacture a robustly feasible action. Positive
information and continuous derivative factorization hold, but both registered
deterministic actions violate the uniform threshold.

The conclusion is grammar-dependent. If randomized deployment policies are
admissible and risks mix linearly, the half-half mixture has constant risk
`1/2` and repairs this particular example. The counterexample therefore
refutes the literal deterministic-policy/factorization-only clause, while also
showing that the policy-randomization and local-certificate semantics must be
frozen in a successor statement.

## Resolution-scope assessment

The QMD witness and repaired continuation arguments are strong negative
components, but several claimed obligation closures are definitions or
restricted-class results rather than the requested general characterization:

- decision-specific deficiency is the exact minimax failure value, but does
  not itself give a structural coverage criterion for the full QMD class;
- defining sample complexity as the first `n` at which deficiency crosses a
  threshold is exact but is not a general minimax rate theorem;
- minimizing terminal deficiency describes an objective, but without a frozen
  adaptive observation model, costs, horizon, and admissible design kernels it
  is not a general active-design theorem; and
- the local counterexample depends on a deterministic action grammar that the
  canonical statement does not unambiguously bind.

The packet therefore supports a convincing stop/refreeze conclusion, not a
claim that the entire frozen five-part ASMP-2 program has been negatively
resolved.

## Required repairs

1. Replace “contains all continuous families” with hypotheses that make every
   admissible continuation continuous and separately guarantee bump richness.
2. Add the infinite-packing or positive-dimensional-interior assumption to the
   randomized finite-query corollary.
3. Freeze policy randomization and the meaning of a local certificate.
4. State whether variational deficiency definitions count as the requested
   characterization, or require structural rate and active-design theorems.

**Final simulated-expert outcome:** `unresolved_refreeze_required`.
