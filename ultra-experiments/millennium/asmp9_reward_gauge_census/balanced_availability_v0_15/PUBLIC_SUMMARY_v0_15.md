# ASMP-9 v0.15: sharp availability and trial threshold

## Result in one sentence

For the conditional cycle experiment introduced in v0.13, a declared
probability interior permits an exact—not merely conservative—worst-case
informative-fiber probability and therefore an exact minimum number of trials
per edge needed to guarantee a target availability.

## The mathematical result

Consider a consistently oriented cycle of length `k`. Each edge receives `n`
independent Bernoulli comparisons with probability

```text
epsilon <= p_e <= 1-epsilon.
```

The conditional experiment is informative exactly when the observed edge
counts do not contain both a zero edge and a full edge. Its availability is

```text
A(p)
  = product_e [1-(1-p_e)^n]
  + product_e [1-p_e^n]
  - product_e [1-p_e^n-(1-p_e)^n].
```

This function is separately concave in the edge probabilities, so a global
minimum over the probability box occurs at an endpoint assignment. Among
those assignments, the minimum occurs when `epsilon` and `1-epsilon` are
distributed across the cycle as evenly as possible.

Let

```text
m=floor(k/2),  h=ceil(k/2),
a=(1-epsilon)^n,  b=epsilon^n,
x=1-a,  y=1-b,  z=1-a-b.
```

Then the exact minimax availability is

```text
A_min(k,n,epsilon)
  = x^m y^h + y^m x^h - z^k.
```

The endpoint split attains the bound, so this is a sharp identity rather than
a union bound.

For target availability `1-delta`, the exact equal-count requirement is

```text
n_star(k,epsilon,delta)
  = min {n>=1 : A_min(k,n,epsilon) >= 1-delta}.
```

For fixed `k` and positive interior, the small-`delta` scaling is

```text
n_star
  = log(floor(k/2) ceil(k/2) / delta)
    / [2 log(1/(1-epsilon))]
    + O(1).
```

The doubled exponent is the operational fact hidden by v0.14's conservative
one-sided lower bound: an uninformative fiber requires both a zero edge and a
full edge.

## Prospective verification

The implementation, theorem, protocol, environment, prior-art boundary, and
tests were frozen at commit
`018d95a675e7a9bb32505d656ebd4d3ced489afd`. The prospective registration was
then committed at
`9d6ee8799695f6dda4395aee039a9eb977866f18`.

The registration bound 17 files under SHA-256 and used parameter values
disjoint from the burned development registry.

The fresh exact run covered:

- 36 theorem cells;
- 48 exact trial-threshold cells;
- 6 zero-interior negative controls; and
- 32 unequal-allocation falsification cells.

All nine registered gates passed.

Selected exact thresholds:

| cycle length | interior `epsilon` | target | trials per edge |
| ---: | ---: | ---: | ---: |
| 11 | 1/16 | 0.875 | 40 |
| 11 | 1/16 | 0.995 | 67 |
| 11 | 3/10 | 0.95 | 10 |
| 13 | 3/20 | 0.95 | 23 |
| 16 | 1/16 | 0.95 | 60 |
| 16 | 3/10 | 0.995 | 14 |
| 16 | 7/20 | 0.995 | 11 |

At `epsilon=0`, all six controls had zero worst-case availability for finite
trial counts, confirming that some probability-interior assumption is
necessary.

The exact run took 2.780 seconds and peaked at 20,938,752 resident bytes. The
GPU was prohibited and unused.

## Independent replay

An independent verifier:

- recomputed all 17 sealed hashes;
- checked the result and report against the run receipt;
- independently evaluated the closed form and every endpoint assignment;
- independently reconstructed every threshold predecessor/current pair;
- independently enumerated every unequal allocation and nuisance endpoint;
  and
- checked the resource and claim-boundary fields.

All 29 checks passed. A clean detached-worktree replay reproduced every
scientific field exactly; only wall-time and peak-memory telemetry differed.

## The unequal-allocation result is deliberately weaker

With a fixed total trial budget, counts differing by at most one were optimal
in all 32 fresh finite cells. This failed to falsify the balancing conjecture.
It did not prove the general conjecture.

That distinction is substantive. A proposed general averaging certificate
failed during development, so the protocol registers the finite allocation
grid only as a falsification target. The exact equal-count theorem does not
depend on that conjecture.

## Prior-art and claim boundary

Conditional likelihood, conditional versus unconditional exact inference,
paired-comparison minimax estimation, and Bradley-Terry optimal design are
established literatures. The contribution here is a narrow ASMP-9
access-ledger specialization: it identifies the exact bounded-interior
nuisance for this conditional quotient and turns it into a sharp finite trial
threshold.

This result does not validate Bradley-Terry as a model of people or language
models, establish a general optimal-design theorem, solve general inverse
reinforcement learning, or resolve ASMP-9.

## Canonical artifacts

- [`THEOREM_v0_15.md`](THEOREM_v0_15.md)
- [`PROTOCOL_v0_15.md`](PROTOCOL_v0_15.md)
- [`registration_v0_15.json`](registration_v0_15.json)
- [`RESULT_v0_15.md`](RESULT_v0_15.md)
- [`result_v0_15.json`](result_v0_15.json)
- [`receipt_v0_15.json`](receipt_v0_15.json)
- [`verification_v0_15.json`](verification_v0_15.json)
- [`release_manifest_v0_15.json`](release_manifest_v0_15.json)
- [`RESOLUTION_AUDIT_v0_15.md`](../RESOLUTION_AUDIT_v0_15.md)
