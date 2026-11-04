# ASMP-7 causal adaptive suppression protocol v0.4

## Status and evidence boundary

This directory is a source candidate, not a scientific result. Exactly the
eight files named in `manifest_v0_4.json#source_freeze.files` must be reviewed
and committed together before either scientific entrypoint may run. No
registered row, oracle grid, 11,520-comparison generic-terminal proof census,
result artifact, or verification artifact may be executed before that source
commit exists. Source-only checks may enumerate terminal tables but may not
run their registered action grid.

The primary benefit is a finite robustness/theory test. The claim is
`model_only`. It extends the fixed execution-dependent mask in ASMP-7 v0.3 to
a precisely causal history-dependent mask class. It does not claim a new
Bellman, stochastic-dominance, Neyman-Pearson, or randomized-response theorem.

V0.4 binds the exact historical Git bytes for the v0.1 source, registration,
result, and receipt, and for the complete v0.3 source/result/verification
bundle. The v0.3 result is an input baseline, not a newly generated outcome.

## Frozen filtration and observations

The domain is `Z={0,...,15}`. A fixed Boolean execution is known completely to
the suppressor. Its agreement set with the trusted target is `A`, with
`|A|=k`. At step `t`, before the current challenge is drawn, the suppressor
chooses an exact-`c` subset `S_t` using:

- the fixed execution and `A`;
- the entire past `(X_1,Y_1,S_1),...,(X_{t-1},Y_{t-1},S_{t-1})`; and
- suppressor-private randomization.

It cannot use current `X_t`, the fresh randomized-response or fallback coins,
or the auditor's randomization. This is a product-stream assumption, not merely
a chronological statement: suppressor-private coins, challenge draws,
randomized-response coins, uncovered fallback coins, and auditor coins are
mutually independent streams. Conditional on the complete frozen filtration,
including `S_t` and every suppressor-private coin used through time `t`, `X_t`
remains uniform on `Z` and both possible current report coins remain fresh.
After `S_t` is frozen, `X_t` is sampled from that conditional law. A covered
event uses a fresh theta-randomized report of execution correctness; an
uncovered event emits a fresh fair bit. Only the
report history `Y_1,...,Y_m` is released to the monitor. No challenge identity,
mask identity, private coin, execution state, or policy bit is released. The
registered upper-tail audits use only `K=sum_t Y_t`. Auditor randomization is
independent, hidden from the suppressor, and drawn after the full report
transcript.

Randomized suppressor policies are allowed. Conditional on their private
coins, they are deterministic policies; their values are convex mixtures of
deterministic conditional actions.

## Concrete masks and the action quotient

For a concrete mask, let `a=|S_t intersect A|`. Exact set counting gives

```text
L(k,c)=max(0,k+c-16) <= a <= U(k,c)=min(k,c),
```

and every integer in this interval is attainable. Conditional on the frozen
past, all policy coins used so far, and the selected mask, the registered
product law leaves the current challenge uniform and the report coin
independent. Averaging over those fresh variables gives

```text
q_theta(a) = 1/2 + (2*theta-1)*(a-c/2)/16
           = 1/2 + (2*theta-1)*(2*a-c)/32.
```

The denominator is 16 in the first form, equivalently 32 after clearing the
half. No denominator-8 law is admissible. Because the next-report law and the
future action set depend on a mask only through `a`, mask identity, past `X`,
past masks, and private policy coins reduce to this finite action interval for
the declared monitor.

The primary path enumerates concrete 16-point masks for the 72 registered
`(k,c)` pairs and the frozen nontrivial relabeling
`p(i)=(5*i+3) mod 16`. The independent path uses the separate count

```text
C(k,a) * C(16-k,c-a)
```

to certify exactly which intersection counts occur and that their
multiplicities sum to `C(16,c)`.

## Full-history endpoint theorem

Let `phi:{0,1}^m -> Q intersect [0,1]` be coordinatewise nondecreasing; it need
not be count-symmetric. For a report prefix `y`, let `W_t(y)` be the optimal
continuation value. At any node and action `a`,

```text
(1-q_theta(a))*W_{t+1}(y,0) + q_theta(a)*W_{t+1}(y,1).
```

Backward induction preserves
`W_{t+1}(y,1)>=W_{t+1}(y,0)`. Since theta is at least one half, the displayed
quantity is affine and nondecreasing in `a`. Therefore a maximizing suppressor
always has an optimal action `U(k,c)` and a minimizing suppressor always has an
optimal action `L(k,c)`. Concrete masks attaining those endpoints exist and
may be held constant at every step. Randomized policies cannot improve on the
endpoint because they produce convex mixtures of the same affine values.

Thus, for every deterministic finite `0<=m<=8192`,

```text
sup_pi E[phi(Y)] = E_{iid Bernoulli(q_plus(k,c))}[phi(Y)],
inf_pi E[phi(Y)] = E_{iid Bernoulli(q_minus(k,c))}[phi(Y)],
```

where `q_plus=q_theta(U)` and `q_minus=q_theta(L)`. This is a finite induction.
It does not cover an unbounded horizon, optional stopping, a random stopping
time, or an infinite-horizon limit.

For a count-symmetric nondecreasing terminal function, the full-history value
collapses to the count-state Bellman recurrence

```text
V_t(s)=ext_a [(1-q_theta(a))*V_{t+1}(s)
                         + q_theta(a)*V_{t+1}(s+1)].
```

The h=3 upper-tail oracle is an implementation check of this corollary, not
evidence from which the universal finite theorem is extrapolated. A second
registered h=3 census brute-forces all 20 monotone Boolean terminal tables,
including all 15 that are not count-symmetric, across 12 policy-class agreement
counts, six coverage counts, four privacy values, and both objectives. Its
`20*12*6*4*2=11520` exact comparisons are analytic proof checks, not additional
experimental units. The independent implementation generates the same 20
terminals from antichains and uses a bottom-up recurrence. General rational
monotone terminals decompose into nonnegative layers of Boolean upper sets;
the horizon-free backward induction above, rather than the finite census,
supports the stated `m<=8192` claim.

## Composite classes and exact minimum transfer

The compliant class is `k<=8`; forbidden boundaries are `k1 in {14,16}`.
Both `U(k,c)` and `L(k,c)` are nondecreasing in `k`, so both endpoint report
probabilities are nondecreasing in `k`. The uniform worst false-positive case
is therefore `k=8`; the minimum forbidden detection probability is attained at
`k=k1`. The quotient census covers every registered policy-class count
`k in {0,...,8,14,15,16}`.

For separated endpoints, the v0.3 exact randomized upper-tail test controls
the entire causal adaptive class by the theorem. Conversely, constant endpoint
masks are admissible causal policies, so any adaptive-robust test must solve
the corresponding simple iid binomial pair. The bound v0.3 exact
Neyman-Pearson size certificate and infeasible predecessor therefore transfer
the exact `m_star`, not merely feasibility of the selected test. When the
attainable intervals overlap, constant masks realize the same report law in
both classes and preserve the common-law impossibility. The exact bound
selective registry contains 21 `feasible_exact` and 27
`common_law_impossible` rows and no cap-infeasible row. Those two statuses are
the complete frozen v0.4 transfer universe; an upstream registry containing a
cap-infeasible selective row would require a new registration and handler.

## Frozen row universes

The primary scientific registry contains exactly 48 parameter triples:

```text
k1 in {14,16}
theta in {1/2,3/4,4/5,1}
c in {0,8,10,12,14,16}.
```

These are parameter triples, not the separate 48 representation states from
v0.1. Every selective v0.3 row, including its common-law or exact
feasible/predecessor certificate, is reproduced once.

The action-quotient universe has exactly 72 `(k,c)` pairs. The branch-complete
oracle has horizon three and exactly six manifest-bound monotone witnesses,
four thresholds, three boundary-randomization values, and two objectives:
`6*4*3*2=144` comparisons. The full-history, count-state, and constant-endpoint
values must agree in every row. Horizon three is the first report-only depth
where different prefixes such as `01` and `10` share the same count state.
The separate generic-terminal proof census has exactly 11,520 registered
comparisons and no result-row or experimental-unit interpretation.

For threshold `r` and boundary randomization `gamma`, the oracle terminal is
exactly `phi=1{K>r}+gamma*1{K=r}`. Objective `max` uses the compliant boundary
`k=8` and action `U`; objective `min` uses the witness's forbidden boundary
`k=k1` and action `L`.

The direct oracle grid `gamma in {0,1/2,1}` checks implementation branches. The
analytic theorem covers every rational coordinatewise-monotone `phi`, and the
bound v0.3 tests contain arbitrary exact rational boundary randomization.

## Scope-breaking controls

1. **Current-X timing mutation.** At `(k0,k1,theta,c)=(8,14,1,12)`, a
   current-X-aware compliant suppressor covers an agreement and omits a
   disagreement, giving `q0=3/4`. A forbidden suppressor omits an agreement and
   covers a disagreement, giving `q1=7/16`. This reverses the causal pair
   `5/8<3/4`. The mutation has a separate implementation and may never be
   passed through the causal quotient.
2. **Nonmonotone terminal mutation.** At `k=8,theta=1,c=12,m=2`, let
   `phi=1{K=1}`. After report zero choose `q=5/8`; after report one choose
   `q=3/8`. The adaptive value is `5/8`, while the best fixed mask obtains
   `1/2`. This intended divergence is separate from the 144 monotone oracle
   rows and demonstrates why terminal monotonicity is necessary.

Additional controls are concrete-mask/quotient agreement, input relabeling,
all-row v0.3 reproduction, theta-one-half privacy null, zero coverage, and full
coverage.

## Resources, artifacts, and conclusion layers

Only Python's standard library and `fractions.Fraction` are allowed. Scientific
execution is sequential, with no RNG or worker subprocesses. Ceilings are 30
wall seconds, 64 MiB peak traced Python allocation, and one MiB per canonical
JSON artifact. `tracemalloc` does not measure process RSS or native allocator
memory; the package makes no unmeasured hard-RSS claim. A resource stop retains
only a completed prefix, marks the run incomplete, and downgrades every
conclusion layer. An oversized final artifact fails before path creation.

Both scientific entrypoints require `python -I`, audit the exact eight-file
regular non-reparse live source directory before local import, bind byte-for-byte
source blobs to a full source commit, and refuse to overwrite their sibling
artifact path. The independent verifier imports no primary module and
reconstructs source/upstream bindings, the combinatorial quotient, 48 registry
rows, 144 upper-tail oracle rows, the 11,520 generic-terminal proof
comparisons, controls, and expected key universe. It records its own wall time
and peak traced-Python allocation; its final resource gate requires both the
primary and verification receipts to remain within 30 seconds and 64 MiB.

The result field `manifest_sha256` means SHA-256 of the canonical manifest
object serialized as sorted, two-space-indented JSON with one trailing newline.
Raw-file SHA-256 is recorded separately by verification.

Results keep five separate layers:

1. `metric_robustness` - invariance, timing sensitivity, monotonicity,
   anti-gaming, and clean-control probes.
2. `task_result` - the frozen causal adaptive versus static endpoint result.
3. `measurement_reliability` - exact bindings, certificates, resources, and
   independent reconstruction.
4. `claim_support` - only the finite registered model claim.
5. `operational_decision` - always no deployment authorization.

The primary artifact remains pending independent verification. Only the
write-once import-independent verification artifact may advance reliability
and claim support.

## Claim boundary

The supported positive language is only
`finite_registered_causal_adaptation_equivalence_supported`: on this fixed
16-point Boolean registry, iid-uniform fixed-length challenges, hidden causal
mask policy, report-only monitor, and monotone finite audit class,
nonanticipating exact-c mask reselection does not worsen the v0.3 frontier
beyond constant extremal masks. It establishes no current-X-aware,
nonmonotone, sequential-stopping, infinite-horizon, stateful, nonuniform,
mask-leaking, real-meter, deployment, transformation-universal, or ASMP-7
claim.
