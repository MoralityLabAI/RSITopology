# ASMP-9 deterministic direct-map completeness result v0.52

## Verdict

**`deterministic_direct_map_completeness_verified`**

Every valid deterministic direct upper confidence map in the registered finite
grammar is pointwise dominated by a Buehler map induced by sorting the
outcomes by that map's own reported values. The result holds for every
total-order refinement of every tie.

Consequently, minimizing any coordinatewise nondecreasing objective over all
valid deterministic direct maps is equivalent to minimizing it over all
outcome-order Buehler maps.

This is a self-ordering corollary of classical Buehler optimality, not a new
statistical theorem. Its contribution here is to close the deterministic
direct-map seam in the ASMP-9 instrument.

## Theorem

Let `X` be finite, let `d(theta)` be a scalar risk, and define

```text
B(S) = sup { d(theta) : P_theta(S) > alpha }.
```

A deterministic direct upper map `u:X->R` is valid when

```text
P_theta(u(X) < d(theta)) <= alpha
```

for every `theta`.

Sort outcomes by nondecreasing `u(x)`, breaking ties by any fixed total order
`pi`. Define

```text
U_pi(x_(j)) = B({x_(1),...,x_(j)}).
```

Then `U_pi` is valid and

```text
U_pi(x) <= u(x)
```

for every outcome.

### Proof in one contradiction

If the inequality failed at prefix `j`, some `theta` would satisfy

```text
d(theta) > u(x_(j))
and
P_theta({x_(1),...,x_(j)}) > alpha.
```

Every report in that prefix is at most `u(x_(j))`, even after arbitrary tie
refinement. The whole prefix would therefore lie inside the failure set
`{x:u(x)<d(theta)}`, contradicting validity of `u`.

The Buehler map is itself valid because every sublevel failure set is a prefix
whose subset bound is below the corresponding risk level.

## Classical attribution

The relevant minimality property is classical:

- R. J. Buehler, “Confidence Intervals for the Product of Two Binomial
  Parameters,” *JASA* 52 (1957), 482–493,
  DOI `10.1080/01621459.1957.10501404`;
- C. J. Lloyd and P. Kabaila, “On the Optimality and Limitations of Buehler
  Bounds,” *Australian & New Zealand Journal of Statistics* 45 (2003),
  167–174, DOI `10.1111/1467-842X.00272`; and
- P. Kabaila and C. J. Lloyd, “A Simple Measure of the Efficiency of a
  Buehler Confidence Limit,” *Communications in Statistics—Theory and
  Methods* 34 (2005), 767–774, DOI `10.1081/STA-200054404`.

The present statement takes a valid direct map as its own designated ordering
statistic. No novelty is claimed for the theorem, finite-sample optimality, or
its all-order completeness corollary.

## Prospective verification

Verification source was committed at:

```text
0b9b82f6629c9bd53f16d8bc594b872668e51ce8
```

The source was prospectively registered at:

```text
96190e52282bff2353119d50b5352241b22a45f8
```

Registration SHA-256:

```text
f84ac8f00cf93a59992f5ad01a3e0e3edfb3129b223bd15714ede691c7c4e0ae
```

The write-once result was committed at:

```text
9a99438a3402ee774e03724f512b3b926a84519d
```

Verification SHA-256:

```text
7fc7bcc2fe98870ab5e302887529b5a1ac1264bcd2f484143911921076b7eb4a
```

## Exact census

The independent verifier enumerated every normalized monotone three-valued
subset-bound table on three outcomes and every direct report vector in
`{0,1,2}^3`:

| Quantity | Result |
|---|---:|
| Monotone subset-bound tables | `148` |
| Candidate deterministic direct maps | `3,996` |
| Valid direct maps | `1,494` |
| Invalid direct maps | `2,502` |
| Report-consistent total-order checks | `3,342` |
| Strict-dominance checks | `2,454` |
| Dominance mismatches | `0` |
| Buehler-validity mismatches | `0` |

For every positive denominator-six reference law:

| Quantity | Result |
|---|---:|
| Reference laws | `10` |
| Global optimum comparisons | `1,480` |
| Direct-versus-Buehler optimum mismatches | `0` |

The strict control mapped `(2,2)` to `(1,2)`. The equality control preserved
`(1,2)`. An independent finite probability experiment reconstructed the
control subset table `(0,1,1,2)`.

## Gates and resources

All eight registered gates passed:

```text
H0 source integrity:             pass
T0 tests (11/11):                pass
U0 universe completeness:        pass
D0 pointwise dominance:          pass
O0 global optimum identity:      pass
C0 control separation:           pass
X0 experiment realization:       pass
RESOURCE:                         pass.
```

Resources:

```text
elapsed:             5.8549901 seconds
peak working set:   22,413,312 bytes
worker processes:               1.
```

## What this closes

Within the finite deterministic direct-confidence grammar:

```text
min_{valid deterministic direct u} L(u)
  =
min_{total orders pi} L(U_pi)
```

for every coordinatewise nondecreasing loss `L` whose minimum exists.
Therefore the v0.48–v0.51 optimization over evidence orderings did not omit a
better deterministic direct reporting rule.

## Remaining randomized seam

Version v0.52 does not characterize a randomized procedure whose individual
deterministic components may under-cover while their aggregate coverage over
external randomization is valid. Such procedures need not be mixtures of
individually valid Buehler maps.

The next resolution-directed target is an exact finite LP characterization of
aggregate randomized coverage, including:

1. whether randomization can strictly improve reference-weighted expected
   bounds beyond every deterministic valid map;
2. a smallest strict-improvement witness or a proof that none exists in the
   declared grammar; and
3. a structural description of the extreme points rather than only a census.

## Claim boundary

This is an exact finite consolidation of classical Buehler theory. It does not
establish novelty, aggregate randomized optimality, two-sided confidence-set
optimality, continuous or strategic robustness, validity of a physical
preference channel, the existence of one scalar latent value, or a resolution
of ASMP-9.
