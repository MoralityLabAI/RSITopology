# ASMP-9 randomized evidence-ordering result v0.51

## Verdict

**`randomization_improves_regret_not_certification`**

Randomizing over direct-Buehler evidence orderings reduced worst-case
certificate regret for `234` of the `361` registered table pairs. It did not
create a single new zero-regret certificate. Randomized value was zero for
exactly the same `79` pairs that already possessed a deterministic ordering
optimal in every decision/reference scenario.

This is the registered boundary:

> Mixing can improve approximate minimax performance, but it cannot repair a
> missing common decision-relative evidence identity.

The zero-sum-game and randomized-minmax construction is directly subsumed by
prior work. This result is an exact finite Buehler specialization and audit
instrument, not a novelty claim or an ASMP-9 resolution.

## Exact game

For ordering `pi` and scenario `s=(decision objective, reference vertex)`,
define

```text
A(pi,s)
  = C_s(pi) - min_sigma C_s(sigma).
```

The optimizer's exact mixed-ordering problem is

```text
minimize    t
subject to  sum_pi p(pi) A(pi,s) <= t  for every s
            sum_pi p(pi) = 1
            p(pi) >= 0.
```

Its adversarial dual is

```text
maximize    z
subject to  sum_s q(s) A(pi,s) >= z  for every pi
            sum_s q(s) = 1
            q(s) >= 0.
```

Both programs were solved in exact rational arithmetic by complete LP-vertex
enumeration. Every pair passed primal/dual equality, feasibility, and
complementary slackness.

## Why randomization cannot restore exact certification

All entries of `A` are nonnegative. A mixed strategy has value zero only if
every scenario expectation is zero. Therefore every positive-probability
ordering in its support must have zero regret in every scenario:

```text
randomized value = 0
  iff
support(p) is contained in
intersection_s argmin_pi C_s(pi).
```

This is the same deterministic common-chain intersection certified by
v0.49-v0.50. Randomization cannot cancel positive regret with negative regret,
because negative regret does not exist.

## Smallest strict-gain control

The v0.50 two-outcome reference-switch witness has regret matrix

```text
          left   right
(x,y)       0     1/2
(y,x)      1/2     0.
```

Its exact game is:

```text
deterministic minimax regret: 1/2
randomized minimax regret:    1/4
randomization gain:           1/4
optimizer mixture:           (1/2,1/2)
adversary mixture:           (1/2,1/2).
```

The equal adversarial mixture supplies the matching lower bound. Two
orderings and two scenarios are minimal for strict gain: one ordering cannot
be mixed, and one scenario always has a deterministic zero-regret optimum.

## Prospective census

The verification source was committed at

```text
b5c6b9b2303e208b2d2056b2a617a43d31f86f85
```

and prospectively registered at

```text
d66df77ac156c536c60547b038c5cc4d84f3279d.
```

Registration SHA-256:

```text
e9c7ef6ff7b649bb816d589801fa9caeb9bf20e20e053716dd7ffd5dfeb6a539
```

The frozen universe reused v0.50:

```text
admissible monotone tables: 19
ordered objective pairs:   361
orderings per pair:          6
reference vertices:          2
scenarios per pair:          4.
```

The strict-gain count and distribution were unthresholded outcomes.

## Exact result

| Quantity | Result |
|---|---:|
| Pairs with deterministic common zero-regret order | `79` |
| Pairs without a common zero-regret order | `282` |
| Pairs with strict randomization gain | `234` |
| Pairs without strict gain | `127` |
| Maximum gain | `1/4` |
| Pairs attaining maximum gain | `16` |
| Mean gain over all pairs | `35489/454860` |

Among the `127` no-gain pairs, `79` already had exact zero regret and `48`
were non-robust games for which mixing did not improve the best deterministic
compromise. Randomization therefore helped most, but not all, incompatible
pairs.

Exact gain histogram:

| Gain | Pair count |
|---:|---:|
| `0` | `127` |
| `1/36` | `4` |
| `1/30` | `8` |
| `1/24` | `12` |
| `1/18` | `24` |
| `1/12` | `52` |
| `2/21` | `4` |
| `1/9` | `6` |
| `7/60` | `4` |
| `1/8` | `4` |
| `2/15` | `40` |
| `1/6` | `52` |
| `3/16` | `4` |
| `3/14` | `4` |
| `1/4` | `16` |

Optimizer support sizes:

```text
size 1:  91 pairs
size 2: 216 pairs
size 3:  50 pairs
size 4:   4 pairs.
```

Least-favorable scenario support sizes:

```text
size 1:  79 pairs
size 2: 255 pairs
size 3:  23 pairs
size 4:   4 pairs.
```

## Verification

All ten registered gates passed:

```text
source mismatches:                  0
primal/dual mismatches:             0
certificate slackness failures:     0
independent simplex failures:       0
independent feasibility failures:   0
independent slackness failures:     0
zero-support mismatches:            0
deterministic-value mismatches:     0
randomized-dominance failures:      0
tests:                          10/10.
```

Resources:

```text
elapsed: 105.2706745 seconds
peak working set: 25,767,936 bytes
workers: 1.
```

Verification result commit:

```text
c3e1e660349bda230b6a113af33ead75e6c9b926
```

Verification SHA-256:

```text
03c1e42a3b452200b3955f34a15626f8f9d09da75d045e1ac1d1c454a30aecfa
```

The sealed receipt contains every one of the 361 exact pair rows, including
primal and dual strategies.

## Prior-art boundary

Mastin, Jaillet, and Chin directly formulate randomized minmax regret for
combinatorial optimization and prove stronger algorithmic results. Version
v0.51 contributes no new minimax framework, polynomial-time result, or
integrality-gap theorem.

The durable ASMP-9 specialization is the distinction between:

- exact decision-relative certification, which still requires a
  deterministic common-optimum intersection; and
- approximate minimax compromise, which mixing can improve.

## Remaining deterministic-direct seam

Version v0.51 randomizes only among individually valid direct-Buehler
procedures. It does not yet prove that the union over all Buehler orderings is
complete among every deterministic direct confidence map, nor does it permit
mixtures of individually under-covering maps whose aggregate randomized
coverage is valid.

The next theorem target is therefore:

1. prove or refute that every valid deterministic direct bound is weakly
   dominated by the Buehlerization induced by sorting its reported values;
2. verify that statement over a complete multilevel finite universe; and
3. keep aggregate-coverage randomization as a separate later problem.

## Claim boundary

This is established randomized-minmax mathematics specialized to finite
Buehler evidence ordering. It does not justify randomized confidence
reporting operationally, solve aggregate randomized coverage, provide an
efficient large-width implementation, handle continuous or strategic
uncertainty, validate a physical preference channel, or resolve ASMP-9.
