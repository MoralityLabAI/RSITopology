# ASMP-9 v0.49 common-ordering development result

## Status

**Finite theorem instrument derived and tested; not prospectively registered.**

The v0.48 prospective null is now explained by an exact finite object. For
each decision risk, the Bellman-optimal outcome orderings form paths in a
tight-predecessor DAG on the Boolean subset lattice. Two decision risks admit
a common optimal ordering exactly when the two tight DAGs have a common
root-to-top path.

This is an instance-wise characterization, not yet a structural
classification that predicts compatibility without solving the two dynamic
programs.

## Exact results

### Common-chain theorem

For subset-bound table `B_d`, positive outcome weights `w`, and

```text
V_d(S)
  = min_(x in S) [
      V_d(S \ {x}) + w_x B_d(S)
    ],
```

mark `S\{x} -> S` tight when it realizes equality.

An ordering is optimal exactly when all of its prefix edges are tight.
Consequently:

```text
common optimum exists
  iff
intersection of tight DAGs has an empty-to-full path.
```

The number of common paths is the exact number of common optimal orderings.
If no path exists, the reachable-set boundary labels which objective blocks
every possible continuation and supplies a finite obstruction certificate.

### Ordering gauge

For two bound tables, set

```text
h(S) = B_2(S) - a B_1(S),  a > 0.
```

If the edge form `w_x h(S)` has zero curl on every Boolean-lattice square,
then it is an exact discrete one-form. There is a subset potential `Phi` with

```text
w_x h(S) = Phi(S) - Phi(S \ {x}),
```

and hence

```text
C_2(pi)
  = a C_1(pi) + Phi(X) - Phi(empty)
```

for every ordering. The optimizer sets are identical.

This condition is sufficient for shared optimality and characterizes affine
equality of all ordering costs. It is not necessary merely for one shared
optimum.

## Recovery of v0.48

The new independent implementation exactly recovers the confirmation counts:

```text
four-class optimizers: 1,451,520
root-group optimizers: 4,354,560
common optimizers:     1,451,520.
```

The same pair is not ordering-gauge equivalent at any positive scale. Its
Boolean-square equations demand 17 distinct scale ratios. Thus the common
optimum in v0.48 is a weaker phenomenon than affine equality of ordering
costs.

A planted two-outcome control with opposed singleton bounds has one optimizer
per objective, no common path, and a nonempty labelled obstruction boundary.

## Verification

```text
6 tests passed
```

The tests cover:

- dynamic-program optimizer counts against exhaustive permutations;
- a planted disjoint tight-DAG pair;
- common-path counts against exhaustive set intersection;
- zero-curl affine cost identity on every ordering;
- a nonzero-curl rejection; and
- exact recovery of the v0.48 confirmation plus rejection of every positive
  ordering-gauge scale.

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m pytest -q -p no:cacheprovider `
  ultra-experiments/millennium/asmp9_reward_gauge_census/common_ordering_v0_49/test_common_ordering.py
```

## Next resolution-directed step

The tight-DAG theorem completely decides a finite instance but still requires
solving both subset programs. The next useful theorem must identify a
restricted structural class where shared optimality or incompatibility
follows directly from the experiment and decision risks.

The strongest current positive condition is zero-curl ordering-gauge
equivalence. Candidate weaker classes include common nested risk level sets
with controlled magnitudes or comonotone predecessor margins. Any successor
must recover both the v0.48 disjoint development control and the common-optimum
confirmation.

## Claim boundary

Bellman tightness, path intersection in a DAG, and zero-curl path independence
are classical finite mathematics. This development packages them as the next
ASMP-9 evidence-ordering object. It does not establish novelty, a continuous
minimax theorem, a real preference channel, or a resolution of ASMP-9.
