# ASMP-7 meter-coverage robustness protocol v0.3

## Status and precedence

This is an additive CPU-exact successor. It does not alter the registered
v0.1 or v0.2/v0.2.1 sources, artifacts, receipts, or claims. A source
checkpoint must precede any result artifact used as evidence.

## Question

How does weakening trusted semantic-meter coverage change the exact charged
audit in the frozen Boolean attestability registry, and why must
policy-independent missingness be kept separate from selective suppression?

## Frozen inherited object

The challenge domain has 16 inputs. The compliant boundary is `k=8`
agreements with the parity target. The forbidden boundaries are `k1 in
{14,16}`. A covered event releases the v0.2.1 randomized-response correctness
bit with

```text
theta in {1/2, 3/4, 4/5, 1}.
```

An uncovered event releases a fresh fair bit. Challenges sample the full
16-point domain independently with replacement, and all fallback and
randomized-response coins are fresh. Separate false-positive and
false-negative limits remain `1/20`.

Coverage is registered as an exact count

```text
c in {0,8,10,12,14,16};  rho = c/16.
```

The cap is `m=8192`. A common-law impossibility is stronger than cap
infeasibility and is never converted into a finite sample count.

## Two coverage models

### Policy-independent partial coverage

For each challenge, coverage is an execution- and policy-independent event of
probability `rho`. The report probability at agreement count `k` is

```text
q_ind(k,theta,c)
  = 1/2 + (c/16) * (q_full(k,theta) - 1/2).
```

Because `q_full(8,theta)=1/2`, the compliant boundary remains exactly fair.
This model is missingness independent of the policy object. It is not a model
of strategic suppression.

### Adversarial selective suppression

For each execution, an adversary chooses exactly `c` covered domain points
after seeing the execution. If an execution has `k` target agreements, the
number `a` of agreements inside the covered set ranges over every integer in

```text
max(0,k+c-16) <= a <= min(k,c).
```

The resulting report probability is

```text
q_sel(a,theta,c)
  = 1/2 + (2*theta-1) * (a-c/2)/16.
```

The uniform false-positive endpoint maximizes `a` at `k=8`; the uniform
false-negative endpoint minimizes `a` at `k=k1`. If the two attainable
integer ranges overlap, the adversary can give a compliant and forbidden
execution the same Bernoulli report law. Then every test obeys
`FP+FN >= 1`, regardless of sample count. At `theta=1/2` every covered law is
also fair even when the attainable `a` ranges are disjoint.

The mask is fixed for one execution while challenges are sampled with
replacement. Adaptive history-dependent mask changes are outside this
protocol.

## Exact test and certificates

When the robust endpoints satisfy `q0<q1`, use the exact size-`1/20`
randomized upper-tail test on `K`, the number of one reports:

```text
forbidden when K>t;
forbidden with probability gamma when K=t;
compliant when K<t.
```

Integer binomial masses and `fractions.Fraction` determine `t`, `gamma`, FP,
and FN. Search for the minimum `m` by monotone bracketing and binary search,
then certify both the feasible `m` and the infeasible predecessor. No
floating-point quantity decides a cell, gate, claim, or operational status.

## Frozen gates

- `E0_exact_adjacency`: every feasible cell has exact `FP=1/20`, exact
  `FN<=1/20`, and predecessor `FN>1/20`; a capped cell has exact cap failure.
- `R0_full_coverage_reproduction`: at `c=16`, both coverage models reproduce
  v0.2.1 minima `73,50,15` for `k1=14` and `40,26,5` for `k1=16` at
  `theta=3/4,4/5,1`.
- `M0_coverage_monotonicity`: for each model, boundary, and channel, robust
  separation is nondecreasing and certified sample burden is nonincreasing as
  exact coverage increases.
- `Z0_common_law_zero_information`: zero coverage and `theta=1/2` emit common
  fair laws; selective `k1=14,c=10` additionally has an explicit aligned-mask
  common-law witness for every nonprivate registered channel.
- `B0_bruteforce_small_cases`: complete four-point mask enumeration reproduces
  the attainable-agreement formula for every agreement/coverage count, and
  direct report-string enumeration through length five reproduces the
  binomial law.

## Metric-robustness probes

The sample-burden/common-law metric must pass five distinct probes:

1. **Invariance:** relabeling inputs preserves attainable agreement counts.
2. **Sensitivity:** burden changes under coverage loss and distinguishes
   selective from independent coverage at the same rate.
3. **Monotonicity:** more exact coverage never worsens the registered robust
   burden.
4. **Anti-gaming:** a live policy-independent cell cannot be substituted for
   the common-law selective cell at the same nominal coverage.
5. **Clean control:** at full coverage the two models coincide and reproduce
   v0.2.1.

## Separate decision layers

The artifact reports four noninterchangeable objects:

- `task_result`: what happened on the frozen scientific contrast;
- `measurement_reliability`: whether exactness, reproduction, and independent
  small-case checks support reading the measurement;
- `claim_support`: whether the bounded finite claim is supported after all
  scientific and metric probes;
- `operational_decision`: always `no_deployment_decision_authorized` in this
  synthetic successor.

A reliable measurement does not itself authorize the claim. A supported
finite claim does not authorize a real meter threshold or deployment action.

## Claim boundary

This protocol concerns a 16-point Boolean registry, exact-size event
coverage, fresh fair fallback bits, independent challenges, and two declared
suppression models. It does not establish real meter coverage, identify a
deployment threshold, characterize adaptive history-dependent suppression,
prove transformation-universal attestability, or resolve ASMP-7.
