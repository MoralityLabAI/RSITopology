# ASMP-9 hidden-consideration access theorem draft v0.64

Status: **unregistered theorem development; not claim eligible**.

## 1. Objects and quantifier order

Let `X` be a finite set with `n>=2`.  A latent value object is a strict total
order `succ` on `X`.

For each recorded menu `A`, an unobserved consideration mechanism draws a
nonempty set `C subseteq A`.  The observed choice is the `succ`-maximal member
of `C`.

The experimenter may randomize:

- the recorded menu `A`; or
- an attention instruction `z`.

Unless explicitly stated otherwise, the actual consideration law

```text
mu(C|A,z,succ)
```

is unrestricted and unobserved.  Thus the mechanism may depend on the menu,
instruction, and latent preference.

## 2. Unrestricted hidden-consideration collapse

### Theorem 1

For every family of stochastic choice kernels

```text
p_z(x|A),
```

and every strict preference `succ`, there exists a hidden-consideration
mechanism that produces exactly those kernels.

### Construction

For every `A,z`, draw the singleton consideration set

```text
C={x}
```

with probability `p_z(x|A)`.

The top-ranked member of a singleton is `x`, independently of `succ`.
Therefore the resulting observed law is exactly `p_z`.

### Corollary 1: total preference collapse

Every strict preference has the same observable range.  No nonconstant
functional of `succ` is identified from any amount of recorded-menu data.

### Corollary 2: randomization without compliance is insufficient

Randomized menu or attention-instruction assignment does not help.  The
construction is applied separately after each randomized `A,z`.

The key missing premise is not randomization.  It is a restriction or
measurement tying `z` to the actual considered set.

### Corollary 3: recorded singleton attention is also uninformative

Even if the singleton `C` is recorded perfectly, it contains no comparison.
Observed compliance is useful only when the induced consideration sets expose
joint alternatives under stable preference.

## 3. General compliance-separation criterion

For a registered intervention `z`, let `Gamma_z` be the nonempty family of
consideration sets that an unobserved compliance mechanism is allowed to
choose.  Define

```text
O_z(succ) = {max_succ(C): C in Gamma_z}.
```

The compliance mechanism may observe `succ` and randomize arbitrarily inside
`Gamma_z`.

### Theorem 2

One intervention `z` distinguishes two rankings `succ` and `succ'` uniformly
over all allowed compliance laws if and only if

```text
O_z(succ) intersect O_z(succ') = empty.
```

A finite intervention suite `Z` identifies every ranking if and only if every
pair of distinct rankings is separated by at least one `z in Z`.

### Proof

For one ranking, the attainable outcome laws form the probability simplex on
`O_z(succ)`: every admissible consideration set chooses one member of that
set, and arbitrary mixtures of consideration sets produce arbitrary mixtures
over their attainable winners.

Two such simplexes intersect exactly when their vertex supports intersect.  If
an outcome `x` lies in both supports, both latent rankings can choose
compliance laws producing the point mass at `x`.  If the supports are
disjoint, every allowed outcome law distinguishes them.  Applying this
criterion separately to each recorded intervention proves the suite result.

Thus minimum finite intervention design is an exact separation-cover problem:
each intervention covers the unordered ranking pairs it separates, and a
valid suite covers every pair.

Randomizing over a recorded intervention suite does not improve its
identifying content beyond the interventions in its support.  The conditional
law after each assigned `z` remains separately selectable by the hidden
compliance mechanism.

## 4. Exact pair-forcing endpoint

Now strengthen the interface.  For any registered unordered pair `{x,y}`,
the intervention guarantees:

```text
C={x,y}.
```

The observed choice reports whether `x succ y` or `y succ x`.  Let `E` be the
nonadaptively queried pair family.

### Theorem 3

The forced-pair interface identifies every strict total order on `X` exactly
if and only if

```text
E=binom(X,2).
```

Consequently the sharp nonadaptive query count is

```text
|E|=binom(n,2).
```

### Sufficiency

If every pair is queried, every pairwise comparison is known and hence the
strict total order is known.

### Necessity

Suppose `{x,y}` is not queried.  Construct a strict order in which `x` and
`y` are adjacent.  Swap only those adjacent alternatives.  Their relation to
every third alternative is unchanged, so every queried pair has the same
winner in both orders.  The two latent value objects are distinct but
observationally equivalent.

This is a worst-case, nonadaptive statement.  Adaptive comparison sorting has
a different classical query complexity and is not claimed here.

## 5. Stochastic-preference warning

Pair forcing identifies pairwise comparison probabilities for a distribution
over rankings.  It generally does not identify the distribution itself.
Full-consideration menu variation similarly leaves classical
choice-share-equivalence classes.  The positive theorem therefore applies
only to a deterministic, stable strict preference.

For stochastic mixtures, the correct object is the identified set or a
functional constant over that set, as in current stochastic-choice
identification theory.

## 6. ASMP-9 consequence

The hidden-menu branch has a sharp qualitative boundary:

```text
unrestricted unobserved consideration:
  all preferences observationally equivalent;

randomized instruction with unrestricted unobserved compliance:
  still all preferences observationally equivalent;

verified exact pair forcing, deterministic stable preference:
  full identification iff every pair is queried.
```

For intermediate hidden-compliance grammars, the exact finite target is the
separation-cover number induced by the attainable-choice sets `O_z(succ)`.
Thus an access theorem must name the compliance object.  Calling a randomized
prompt an "attention intervention" does not make it one.

## Proof debt before any registration

1. Exhaustively enumerate all pair-query graphs and strict rankings through
   at least `n=5`, checking injectivity iff the graph is complete.
2. Construct an adjacent-swap witness for every missing pair.
3. Verify exact reproduction of rational stochastic kernels through
   singleton attention for every latent ranking in a finite census.
4. Keep stochastic-mixture identification outside the deterministic positive
   claim.
5. Verify the general attainable-choice separation criterion independently.
6. Treat the cited limited-consideration and stochastic-choice results as
   parents, not competitors.

## Claim boundary

This is an elementary finite access theorem and two endpoint corollaries.  It
is not a new limited-consideration model, a new comparison-sorting theorem, a
point-identification result for preference mixtures, a welfare theorem, an
empirical validation of attention interventions, or a resolution of ASMP-9.
