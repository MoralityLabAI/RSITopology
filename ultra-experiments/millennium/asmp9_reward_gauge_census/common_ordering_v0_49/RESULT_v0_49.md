# ASMP-9 common evidence-ordering theorem v0.49

## Verdict

**`finite_common_ordering_theorem_verified`**

For a fixed finite experiment, positive reference weights, and two declared
decision risks, the existence of a common optimal direct-Buehler evidence
ordering is exactly a path-intersection problem on the Boolean subset lattice.
The theorem supplies:

1. a necessary-and-sufficient finite common-chain certificate;
2. a labelled cut certificate when the two optimizer sets are disjoint;
3. a cardinality-minimal statistical obstruction to a decision-independent
   ordering over unrestricted finite risks; and
4. a zero-curl ordering-gauge condition sufficient for two objectives to have
   identical optimizer sets.

This closes the finite instance-characterization target left by v0.48. It is
classical finite dynamic programming and discrete path independence,
specialized to the ASMP-9 evidence-ordering grammar. It is not a novelty claim
or a resolution of ASMP-9.

## Common-chain characterization

For outcome set `X`, positive reference weights `w_x`, subset-bound table
`B_d`, and subset `S`, define

```text
V_d(empty) = 0,

V_d(S) = min_(x in S) [
  V_d(S \ {x}) + w_x B_d(S)
].
```

Mark the predecessor edge `S\{x} -> S` tight when it realizes equality.
An outcome ordering is optimal for `d` exactly when all its prefix edges are
tight. Therefore:

```text
two risks have a common optimal ordering
  iff
the intersection of their tight-predecessor DAGs
contains an empty-to-X path.
```

The number of such paths is the exact number of common optimal orderings. If
no path reaches `X`, the reachable subsets together with the objective labels
on the blocked boundary edges form a finite disjointness certificate.

Because the ordering universe is finite, disjoint optimizer sets imply
strictly positive cross-regret in both directions.

## Minimal universal obstruction

Two outcomes and two parameters suffice to rule out a universal
decision-independent ordering, and neither cardinality can be reduced.

Let

```text
X = {x,y}
Theta = {a,b}
alpha = 1/5

P_a = (9/10,1/10)
P_b = (1/10,9/10).
```

Take opposite binary decision risks. Their subset tables are

```text
B_1(empty,x,y,X) = (0,0,1,1)
B_2(empty,x,y,X) = (0,1,0,1).
```

With equal outcome weights, the two ordering-cost pairs are

```text
(x,y): (1/2,1)
(y,x): (1,1/2).
```

Each risk has a unique optimizer, the optimizer sets are disjoint, and both
cross-regrets equal `1/2`. One outcome has only one ordering. With one
parameter, every nonzero nonnegative scalar risk is a positive rescaling of
the same eligibility table, while zero risk ties all orderings.

The minimality statement is recorded as a candidate-new elementary lemma,
not established novelty.

## Ordering gauge

For two bound tables and `a>0`, put

```text
h(S) = B_2(S) - a B_1(S)
```

and assign edge value

```text
omega_h(S\{x},S) = w_x h(S).
```

The following are equivalent:

1. `omega_h` has zero curl on every Boolean-lattice square;
2. there is a subset potential `Phi` with
   `w_x h(S)=Phi(S)-Phi(S\{x})`; and
3. the path sum of `omega_h` is independent of the ordering.

Consequently,

```text
C_2(pi)
  = a C_1(pi) + Phi(X) - Phi(empty)
```

for every ordering `pi`, so the optimizer sets are identical. This condition
is sufficient for a common optimum and necessary for affine equality of all
ordering costs. It is not necessary merely for one shared optimum.

## Exhaustive verification

The frozen executor enumerated every monotone binary subset table on four
outcomes satisfying the Buehler normalization

```text
B(empty)=0.
```

The full Dedekind count is `168`; the constant-one table violates this
normalization, leaving:

```text
admissible tables: 167
ordered table pairs: 167^2 = 27,889.
```

Across all pairs:

```text
tight-DAG optimizer mismatches:   0
common-chain count mismatches:    0
positive-gauge pairs:           169
gauge theorem failures:           0
```

The verifier also checked:

- the exact minimal witness and both `1/2` cross-regrets;
- one-outcome and one-parameter minimality controls;
- exact recovery of the v0.48 confirmation counts;
- rejection of ordering-gauge equivalence on that common-optimum fixture; and
- the registered time, memory, and single-worker ceilings.

The original theorem sweep ran in `57.3521` seconds with peak working set
`30,326,784` bytes. The combined scientific and repair suites pass:

```text
scientific theorem tests: 7/7
repair-integrity tests:   3/3
combined:                10/10
```

## Verification-universe correction

The original verification protocol incorrectly registered the full Dedekind
count `168` and `168^2=28,224` pairs while the executor correctly enforced
`B(empty)=0`. Every theorem comparison passed, but count gate `D0` failed.

The original registration, executor, and failed receipt remain immutable:

```text
verification source commit:
1bd553ebf65feb5671d0e4ca16853c14b7abf91d

verification registration commit:
a3fafffa2abb7fff3cc7c408bd85ac4f414af44d

failed verification receipt commit:
15627556f38b781dc3a7521a69494e630d174c07

failed receipt SHA-256:
c31af79810f3cb29e85a19335a47cf4277b5de87ad2d25a87ffd210c8893803e
```

An additive, post-outcome verifier-only repair was committed and separately
registered:

```text
repair source commit:
2399cd04da172a326334c9691c391638746a3b6c

repair registration commit:
e5c92f927161d06017b540411e921d9f8e56987e

repair registration SHA-256:
aea8a36bc9761cd16dfef64674ca7914c0052b416ab70b4d1742a63ea0ae0447
```

The repaired verifier can pass only when the original failure is exactly the
count mismatch, every other original gate passed, both theorem-mismatch
counts are zero, all original and repair hashes match, and the observed
universe is exactly `167` tables and `27,889` pairs. It passed. No theorem
value, witness, enumeration row, source file, or scientific gate changed.

Canonical repaired-verification SHA-256:

```text
e8fb791cdbbfb7e1a2b992a11535147c4242d1f696bf97abe62a296156cd3b08
```

## Recovery of v0.48

The independent implementation exactly recovers:

```text
four-class optimizers: 1,451,520
root-group optimizers: 4,354,560
common optimizers:     1,451,520.
```

That pair is not ordering-gauge equivalent at any positive scale: its square
equations require 17 distinct scale ratios. The result distinguishes shared
optimality from full affine equivalence of ordering costs.

## Resolution relevance

Version v0.49 closes the finite common-ordering question in the following
precise sense:

- common optimality is decidable by an exact necessary-and-sufficient
  certificate;
- incompatibility has a finite labelled obstruction;
- unrestricted decision-independent ordering has a sharp smallest witness;
  and
- zero-curl gauge equivalence gives a structural positive class.

It does **not** yet characterize one ordering that is robust over a family of
reference laws, randomized confidence procedures, continuous experiments, or
strategic and misspecified response channels. The next load-bearing target is
a reference-law-family theorem: characterize the weight polytope on which a
declared chain remains jointly optimal, and determine when no chain is robust
over the registered family.

## Claim boundary

Bellman tightness, path intersection in a DAG, Buehler ordering dependence,
and zero-curl path independence are classical mathematics. The contribution
is a transparent finite consolidation for one ASMP-9 obligation plus an
explicit minimal statistical control. Nothing here identifies a real model's
value function, validates a physical preference channel, handles arbitrary
behavioral misspecification, or resolves ASMP-9.
