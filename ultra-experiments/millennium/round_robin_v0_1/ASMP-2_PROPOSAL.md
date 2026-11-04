# ASMP-2 proposal: crossed-shift continuation test

## Narrow subproblem

Test, in the smallest exact model, the distinction ASMP-2 makes between
**local shift spanning** and **global continuation**. The repository's Qwen
results motivate this distinction: prompt identity explains over 95% of
retention variance while average response energy remains nonzero, so many
evaluations need not supply one uniform context certificate. Those results are
not ASMP-2 evidence and are not pooled here.

## Mathematical object and frozen hypotheses

Let the deployment coordinate be `theta=(theta_1,theta_2)` in `[-1,1]^2` and
the non-inert policy always act, with utility `U=1` and required floor
`u_0=0.8`; abstention has `U=0` and is inadmissible. Observations are
`(Z_1,Z_2,Y)`, where

```text
Z_i ~ Bernoulli(1/2 + theta_i/8),
Y   ~ Bernoulli(1/2 + (theta_1+theta_2)/16
                         + s*theta_1*theta_2/8),  s in {-1,+1}.
```

All probabilities remain in `[1/4,3/4]`. Safety loss is `L_s=E[Y]`. The source
cross is `E_axis={(0,0),(+/-1/2,0),(0,+/-1/2)}`. The two worlds have identical
source laws and identical risk derivatives at the origin. After Fisher
whitening, the source score experiment spans both coordinate directions with
positive minimum singular value `kappa`.

Freeze two ambiguity radii over an `l_infinity` ball of radius `t`:

```text
Delta_local(t) = sup over source-indistinguishable worlds and ||theta||_inf<=t
                 of |L_+(theta)-L_-(theta)|,
Delta_global    = Delta_local(1).
```

**H1 (local):** in the full-span crossed model,
`Delta_local(t)=t^2/4`, so first-order ambiguity vanishes; in a matched
unspanned model whose hidden term is `s*theta_2/8`, ambiguity is `t/4`.

**H2 (global):** full local spanning does not imply a global certificate:
`Delta_global=1/4`, and at `(1,1)` one world exceeds the frozen safety threshold
`epsilon=0.60` while its source-indistinguishable partner does not. Adding one
diagonal source `(1/2,1/2)` distinguishes this registered two-world family.

## Smallest decisive experiment

Implement an exact-rational enumerator for the two world pairs, source
restriction matrices, risk-relevant quotient, `kappa`, and ambiguity maxima on
box vertices. Emit a certificate for each equality above and a nullspace
witness when certification fails. This is a sharp local-versus-global test,
not a domain-generalization leaderboard.

Controls:

1. **Affine control:** set the crossed coefficient to zero; full span then has
   no continuation ambiguity in the registered affine class.
2. **Risk-null control:** leave an unspanned nuisance direction that changes a
   fourth observed variable but neither `L_s` nor `U`; quotienting it must not
   block certification.
3. **Inert-policy control:** abstention must fail the utility floor.
4. **Coordinate control:** rational signed permutations of `theta` must leave
   rank, ambiguity, and decisions unchanged.
5. **Count-matched design control:** replace, rather than append, one redundant
   axial source by the diagonal source, showing that geometry—not evaluation
   count—breaks the crossed ambiguity.

Kill the instrument if any registered equality fails under exact arithmetic,
if the full-span arm has a first-order ambiguity term, if the unspanned
risk-relevant arm lacks one, if the risk-null direction blocks, or if the
count-matched diagonal design fails to distinguish the worlds. A pass validates
only this finite construction.

**Evidence class:** exact/certified finite-model computation, with an
independently checkable rational witness table.

## Optional scale-up

For dimensions `d=2..12` and degree-2/3 bounded polynomial Bernoulli risk
families, enumerate or interval-bound the kernel of each source restriction
operator. Compare an active selector that chooses the next environment
maximizing worst-case kernel evaluation on `Theta_adv` with count-matched
random and space-filling designs. Primary estimand: reduction in exact minimax
global ambiguity per added environment; secondary: conditioning on the
risk-relevant quotient. This tests whether a local span plus targeted nonlocal
support closes ambiguity more efficiently, without claiming a universal
active-design theorem.

## Resources and consumer

| Run | Wall time | CPU | RAM | Disk | GPU |
|---|---:|---:|---:|---:|---:|
| Exact pilot | `<1 min` | 1 core | `<256 MB` | `<10 MB` | none, 0 GPU-hours |
| Full polynomial sweep | `2-6 h` | 8 cores | `<=4 GB` | `<=1 GB` | none, 0 GPU-hours |

Named consumer: the HRMmmm evaluation-suite planner. Reusable artifact:
`shift_span_certificate` plus a source-selection receipt identifying the
largest remaining risk-relevant null direction.

## Claim boundary and reason not to run

This experiment can establish an exact counterexample to the implication
"local tangent span implies global safety" in one bounded class and validate a
candidate audit instrument. Empirical or finite computational work cannot
resolve ASMP-2's semiparametric necessity/sufficiency, minimax sample bounds,
or global continuation frontier.

Reason not to run: the core is polynomial interpolation and nullspace linear
algebra, so its mathematical novelty may be too low unless the active-design
receipt is immediately useful to the harness.
