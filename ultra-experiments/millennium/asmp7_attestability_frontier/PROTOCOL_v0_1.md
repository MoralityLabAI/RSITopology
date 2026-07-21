# ASMP-7 exact finite attestation-frontier protocol v0.1

## Question

Can a non-oracular trace-only monitor uniformly distinguish compliant from
forbidden Boolean executions after a finite set of functionality-preserving
representation transformations? If not, how many explicitly charged semantic
challenges are required when each answer is released through a rational
randomized-response channel?

## Frozen execution and policy universe

The challenge universe is `Z={0,1}^4`, indexed by integers `0..15`. The frozen
target truth table is four-bit parity. Every execution is one of the `2^16`
Boolean truth tables. Let `k(f)` be its number of agreements with the target.

```text
X0 = {f : k(f) <= 8}    compliant
X1 = {f : k(f) >= 14}   forbidden capability
```

The remaining truth tables are outside the policy comparison. The exact class
counts must be emitted.

## Finite transformation monoid

A representation state has five finite fields:

```text
encoding       in {lut, rle, anf}
decomposition  in {single, xor_share_2}
cache          in {none, memoized}
order          in {canonical, commuted}
padding        in {fixed_64, fixed_128}
```

There are `3*2*2*2*2 = 48` states. Generators set one field to one registered
value. Their compositions form a finite monoid of endomorphisms of these 48
states. LUT, run-length, and algebraic-normal-form codecs must round-trip every
truth table exactly. The two-device form XOR-shares and reconstructs the same
table. Cache, order, and padding fields change the trace atom but not behavior.

The orbit checker must validate all `65,536*48 = 3,145,728` registered
truth-table/representation states. This finite registry replaces the unbounded
“all circuits/caches/padding” language rejected in the round-robin review.

## Telemetry experiments

### Trace only

`K_trace` releases the registered trace atom:

```text
(device_id, opcode_class, memory_bucket, message_length, timing_bucket)
```

The atom is a deterministic function of representation state and is
independent of truth-table contents. For every representation state, a frozen
`k=8` execution and a frozen `k=14` execution therefore induce the same law.
This law-level intersection implies `FP+FN >= 1` for every trace-only test.

### Charged audit

The target table is held by the trusted meter. For each of `m` challenges, the
meter samples one input uniformly with replacement, executes `f`, compares the
output to the target, and releases one randomized-response bit using fresh
independent randomness. No uncharged input/output, hidden state, or policy bit
is released. Meter coverage is an assumption, not a conclusion.

Truth-report probability is frozen on the rational grid

```text
theta in {1/2, 3/5, 2/3, 3/4, 4/5, 1}.
```

If `k` of 16 challenges are answered correctly by `f`, one report is correct
with exact probability

```text
q(k,theta) = (1-theta) + (2*theta-1)*k/16.
```

With independent sampling and fresh randomization, the report-count statistic
`K` is exactly `Binomial(m,q)`. The monitor class is permutation-invariant and
sees only the representation trace atom and `K`. Since every trace atom occurs
in both policy classes, symmetrization removes the ancillary trace label.
Because the binomial family has monotone likelihood ratio for `theta>=1/2`,
uniform worst cases are `k=8` and `k=14`, but every policy-class value of `k`
must also be checked directly.

The test declares “forbidden” when `K>c`, declares “compliant” when `K<c`, and
declares “forbidden” with rational probability `gamma` when `K=c`. Search all
`m=0..128`, all `c=0..m`, and the exact feasible interval for `gamma`.

## Error, privacy, and cost

False positive and false negative are separately capped at `1/20`. No
sum-error or average-error substitute is allowed.

The exact channel parameter is `theta`. For `theta<1`, the descriptive local
privacy parameter is `epsilon=ln(theta/(1-theta))`; for `theta=1` it is
infinite. Epsilon is not used in exact gates. Sequential privacy is described
as `m*epsilon` under fresh composition.

The unscalarized cost tuple is

```text
(challenge_executions=m, released_bits=m, verifier_units=m,
 truth_report_probability=theta).
```

Pareto dominance means no more executions/bits/operations and no larger
`theta` (no less privacy), with at least one strict improvement. The scalar
cost from the proposal is not used to define the frontier.

## Frozen gates

- **T0 finite-orbit integrity:** exactly 48 representation states and
  3,145,728 truth-table/state pairs are checked; every round trip preserves the
  truth table and policy class.
- **T1 trace impossibility:** compliant `k=8` and forbidden `k=14` witnesses
  induce the identical trace law in every representation state; the certified
  trace-only bound is `FP+FN>=1`.
- **P0 sufficient-statistic reduction:** direct enumeration of report strings
  through length eight agrees exactly with the binomial count law for every
  registered `theta` and both boundary values `k=8,14`.
- **A0 privacy kill:** `theta=1/2` is infeasible for every `m<=128`.
- **A1 charged-audit liveness:** at least one `theta>1/2` has a feasible test
  by `m<=128`.
- **U0 uniform-composite check:** every reported feasible test respects both
  error limits for every `k<=8` and every `k>=14`, using exact fractions.
- **E0 exhaustive liveness:** the unrandomized channel `theta=1` is feasible
  by `m<=128`.
- **F0 frontier integrity:** every reported Pareto point is feasible and no
  other feasible minimum-channel point dominates it.

Any failed construction/exactness gate gives `invalid_instrument`. If the
instrument gates pass but A1 or E0 fails, report the registered negative result
without changing the grid or threshold.

## Evidence and claim boundary

The evidence is exact finite rational evidence for this registry. It does not
establish semantic coverage of a real meter, attestability of a deployed model,
closure under unregistered compression or decomposition, optimality among all
telemetry experiments, or resolution of ASMP-7. The access model gives the
auditor a trusted semantic comparison at an explicit cost; that is not a free
capability oracle and must not be described as one.

