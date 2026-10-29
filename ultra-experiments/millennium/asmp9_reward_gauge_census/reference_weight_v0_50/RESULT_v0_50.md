# ASMP-9 reference-law robustness theorem v0.50

## Verdict

**`finite_reference_weight_theorem_verified`**

For finite direct-Buehler evidence ordering, the choice of reference law is
part of the decision certificate. A declared ordering is jointly optimal
over a rational polytope of reference laws exactly when it is optimal at
every registered polytope vertex. Equivalently, its prefix path must lie in
the intersection of the tight-predecessor DAGs for every
`(decision objective, reference vertex)` scenario.

The result supplies:

1. an exact rational weight region for each evidence ordering;
2. a necessary-and-sufficient robust common-chain certificate;
3. a labelled finite obstruction when no robust ordering exists;
4. an exact minimax-regret measure of non-robustness; and
5. a smallest statistical witness showing that one-mixture compatibility
   need not survive a reference-law family.

This is classical finite parametric and robust shortest-path mathematics
specialized to one ASMP-9 confidence object. It is not a novelty claim or an
ASMP-9 resolution.

## Reference-weight regions

For decision objective `d`, ordering `pi`, and outcome `x`, let

```text
b_d^pi(x) = B_d(S_pi(x))
```

be the bound reported at the prefix where `x` appears. Under reference law
`w`,

```text
C_d(pi;w) = <w,b_d^pi>.
```

The exact region where `pi` is optimal for every declared objective is

```text
R_pi(D)
  = {
      w in simplex :
      <w,b_d^pi-b_d^sigma> <= 0
      for every d and every ordering sigma
    }.
```

This is a rational polytope. It records the reference-law dependence rather
than hiding it behind one chosen mixture.

## Vertex and robust-chain theorem

Let

```text
W = conv{v_1,...,v_k}
```

be a registered polytope of strictly positive reference laws. Because every
ordering-cost difference is linear in `w`,

```text
pi jointly optimal for every d and w in W
  iff
pi jointly optimal for every (d,v_i).
```

For every objective/vertex scenario, construct the v0.49 tight-predecessor
DAG. A robust common ordering exists exactly when their intersection has an
`empty`-to-full path. Path count equals the exact number of robust orderings.
If no path exists, the reachable-set boundary identifies which
objective/vertex scenarios block every continuation.

## Exact robust regret

For an ordering `pi`, define

```text
Reg(pi;D,W)
  = max_(d,w in W) [
      C_d(pi;w) - min_sigma C_d(sigma;w)
    ].
```

Then

```text
Reg(pi;D,W)
  = max_(d,i,sigma)
      <v_i,b_d^pi-b_d^sigma>.
```

Thus:

```text
robust common ordering exists
  iff
min_pi Reg(pi;D,W) = 0.
```

The positive value grades failure but does not convert a non-robust ordering
into an exact certificate.

## Minimal reference-sensitivity witness

Use one objective, two outcomes, and the Buehler subset table

```text
B(empty,x,y,X) = (0,0,0,1).
```

At reference vertices

```text
v_L = (3/4,1/4)
v_R = (1/4,3/4),
```

the ordering costs are

| Ordering | `v_L` | `v_R` |
|---|---:|---:|
| `(x,y)` | `1/4` | `3/4` |
| `(y,x)` | `3/4` | `1/4` |

The endpoint optima are unique and opposite. No ordering is optimal
throughout the line segment, and the exact minimum worst-case regret is
`1/2`.

The table is statistically realizable by one risk-one parameter with outcome
law `(1/2,1/2)` and `alpha=3/5`: neither singleton probability exceeds
`alpha`, while the full-set probability does. One outcome has no ordering
choice, one objective already suffices, and one reference law always has an
optimum. This is therefore cardinality-minimal for reference-law sensitivity
inside the unrestricted finite grammar.

The witness is a candidate-new elementary control, not established novelty.

## Prospective exhaustive verification

The source was committed at

```text
78c5cf47245ff82980cf8cca0befd88a0283fb39
```

and prospectively registered at

```text
c753a80e4fdcd524851271b6fdc3577cac6f0a0d.
```

Registration SHA-256:

```text
262b271bd87e393c6ff939e7d8a012fb9c7d7d642a0f39741fa2936a98fd2962
```

The frozen universe comprised all monotone binary tables on three outcomes
satisfying `B(empty)=0`:

```text
Dedekind M3:              20
excluded constant-one:     1
admissible tables:        19
ordered objective pairs: 361.
```

The reference family was the convex hull of

```text
(1/2,1/3,1/6)
(1/6,1/3,1/2).
```

All registered gates passed:

| Check | Result |
|---|---:|
| Robust table pairs | `79` |
| Non-robust table pairs | `282` |
| Robust-chain count mismatches | `0` |
| Regret-equivalence mismatches | `0` |
| Weight-region checks | `1,140` |
| Weight-region mismatches | `0` |
| Held-out interpolation checks | `790` |
| Interpolation mismatches | `0` |
| v0.48 common optimizers recovered | `1,451,520` |
| Tests | `11/11` |

The robust/non-robust split was an output, not a registered gate.

Resources:

```text
elapsed: 8.5378651 seconds
peak working set: 27,660,288 bytes
workers: 1
```

Verification result commit:

```text
a312a4b88166e790ba1d4a9910b39ba88752f4d5
```

Verification SHA-256:

```text
c47e0dbd193b4e1b0a58a86dfadb2b33e0cb9699f93736d207fdd5c8adf4772a
```

## Relation to v0.48-v0.49

With the v0.48 uniform reference law as a singleton family, the new
implementation exactly recovers all `1,451,520` common optimal orderings.
Version v0.50 strengthens the question from:

```text
Does one reference law admit a common optimum?
```

to:

```text
Over which reference-law region does that optimum remain valid?
```

This closes the finite reference-law-family obligation. It does not show
that any particular reference mixture is scientifically correct.

## Next resolution-directed target

The next finite gap is randomized evidence ordering. Randomization cannot
create zero regret unless its support lies in the common optimizer
intersection, but it can reduce positive worst-case regret by mixing chains.
A v0.51 theorem should formulate the exact primal/dual finite game over
orderings and objective/reference scenarios, give a smallest strict
randomization-gain witness, and distinguish exact certification from
approximate minimax compromise.

## Claim boundary

Polyhedral optimizer regions, vertex checking, scenario-wise robust paths,
and minimax regret are classical. The contribution is their auditable
specialization to decision-relative Buehler evidence ordering. The result
does not establish efficient large-width enumeration, randomized-procedure
optimality, continuous or strategic robustness, a calibrated physical
preference channel, or an ASMP-9 resolution.
