# ASMP-9 strategic outcome-menu theorem draft v0.65

Status: **unregistered theorem development; not claim eligible**.

## 1. Frozen grammar

Let `Theta` be a finite set of latent types.  Each type `theta` is a strict
total order over a finite outcome set `X`.

An elicitation mechanism may be arbitrarily interactive, but:

1. there is one strategic demonstrator;
2. the complete strategy set is common to all types;
3. every complete strategy produces one deterministic final outcome in `X`;
4. utility depends only on that final outcome; and
5. there are no payments, audits, verification events, or type-dependent side
   consequences.

To **strictly incentive-identify** `theta`, the mechanism must designate a
strategy `s_theta` that is its unique utility-maximizing complete strategy.
Weak optimality is insufficient: if another strategy is equally good, the
observed strategy does not identify the type under adversarial tie breaking.

## 2. Complete-strategy reduction

Every interactive mechanism in this grammar induces a deterministic map

```text
g:S -> X
```

from complete strategies to outcomes.  Internal query order and transcript
length do not change the agent's preference comparison between two complete
strategies, because only `g(s)` affects utility.

If two complete strategies produce the same outcome, no type strictly prefers
one to the other.  Therefore a strictly identifying strategy must have an
outcome distinct from every competing designated strategy.

## 3. Strict incentive-identification theorem

### Theorem 1

A subset `T subseteq Theta` is strictly incentive-identifiable in the frozen
grammar if and only if there exists an injective assignment

```text
a:T -> X
```

such that, for every `theta in T`,

```text
a(theta) strictly preferred_theta a(theta')
for every theta' != theta.
```

### Necessity

Let `s_theta` be the unique best complete strategy for `theta`, and set
`a(theta)=g(s_theta)`.

If `a(theta)=a(theta')` for distinct types, then `theta` is indifferent between
the two designated strategies, contradicting uniqueness.  Thus `a` is
injective.  Unique optimality also gives

```text
a(theta) strictly preferred_theta a(theta')
```

for every other designated strategy.

### Sufficiency

Use one report for each `theta in T` and return outcome `a(theta)`.  The stated
inequalities make truthful reporting the unique best response for every type.

## 4. Exact capacity formula

For a nonempty outcome subset `A subseteq X`, let

```text
top_A(theta)
```

be `theta`'s favorite member of `A`.

### Theorem 2

The maximum strictly incentive-identifiable subset size is

```text
C_strict(Theta,X)
  = max over nonempty A subseteq X
      |{top_A(theta): theta in Theta}|.
```

### Proof

For the lower bound, fix `A`.  For every distinct outcome appearing as a top,
choose one type having that top and assign the outcome to it.  Removing unused
members of `A` cannot change any chosen type's favorite among the assigned
outcomes.

For the upper bound, take any strictly identifying assignment and let `A` be
its image.  Each assigned type must receive its top outcome in `A`, and
injectivity permits at most one chosen type per distinct top.

## 5. Full strict-ranking domain

Let `Theta` contain all `n!` strict rankings of `n` outcomes.

### Corollary 1

```text
C_strict(Theta,X)=n.
```

Every outcome occurs as the top of some ranking, so choosing `A=X` attains
`n`.  No strictly identifying assignment can contain more types than outcomes.

Thus:

- `n=2`: both rankings can be strictly identified by giving each report its
  reported top;
- `n>=3`: at most `n` of `n!` rankings can be strictly identified, so the full
  ranking is not strategically identifiable in this grammar.

## 6. Why weak truthfulness is not identification

The report-top mechanism maps every reported ranking to its top outcome.  It
is weakly strategyproof: truthful reporting produces a best outcome.

For a true ranking on `n` outcomes, however, every report with the same top is
also optimal.  There are

```text
(n-1)!
```

such reports.  For `n>=3`, observed reporting behavior therefore does not
identify the remainder of the ranking under adversarial tie breaking.

## 7. Random problem selection escapes the deterministic bound

The deterministic capacity result is not an impossibility theorem for every
outcome-valued elicitation scheme.  Add one declared randomization primitive:

1. the agent commits a complete ranking report `r`;
2. after commitment, an unordered outcome pair `e={i,j}` is sampled with
   registered probability `w_e`; and
3. the mechanism awards the outcome ranked higher by `r` within `e`.

Assume the agent evaluates the resulting objective lottery by expected utility
for a utility representation `u_theta` that strictly respects its ranking.
For true ranking `theta` and report `r`, the expected-utility regret is

```text
Delta(theta,r)
  = sum_e w_e [
      u_theta(top_theta(e)) - u_theta(top_r(e))
    ].
```

Every summand is nonnegative.  A false report is strictly worse whenever it
reverses a pair having positive sampling probability.

This random-problem-selection construction is classical.  In particular,
Azrieli, Chambers, and Healy (2021), footnote 12, explicitly describe the
full-ranking/random-pair mechanism.  Nothing in this section is claimed as a
new elicitation mechanism or characterization.

### Theorem 3: exact support boundary

On the full domain of strict rankings over `n` outcomes, the random-pair
mechanism strictly elicits every ranking if and only if

```text
w_e > 0 for every one of the C(n,2) outcome pairs.
```

Hence its minimum support size is exactly `C(n,2)`.

Sufficiency follows from the regret decomposition: every distinct pair of
rankings reverses at least one pair.  For necessity, if pair `{i,j}` is never
sampled, choose a ranking in which `i` and `j` are adjacent and a false report
that swaps only those two outcomes.  All sampled pair choices remain
identical, so the false report has zero regret.

## 8. Normalized incentive margin

Strict ordinal identification alone has no positive uniform numerical margin:
cardinal utility gaps representing one strict order can be arbitrarily small.
For a quantitative statement, normalize utilities to a range of at most one
and require every adjacent utility gap to be at least

```text
0 < delta <= 1/(n-1).
```

Then every false report has expected regret at least

```text
delta * min_e w_e.
```

The bound is sharp over the full ranking domain and normalized utility class:
place a least-weight pair adjacently in the true ranking, give it utility gap
`delta`, and swap only that pair.

Among all pair distributions, uniform weights maximize the worst-case bound,
giving the sharp maximin margin

```text
delta / C(n,2).
```

This is a conditional robustness ledger, not a claim that human or model
utilities have the declared normalization or gap.

## 9. Commitment timing is access

The positive result requires the full ranking report to be fixed before the
random pair is selected.  If the pair is revealed first and the agent then
reports, only one binary comparison is behaviorally priced.  For any revealed
pair, each orientation is consistent with

```text
n!/2
```

complete rankings.  For `n>=3`, even a best response therefore fails to
identify the full ranking.

Randomness itself is not the relevant free resource.  The access primitive is
commitment to a reusable report before an outcome-relevant problem is sampled.

## 10. What changes the theorem

The capacity bound prices the consequence alphabet, not the number of
questions.  The random-pair result shows that objective random problem
selection plus pre-draw commitment enlarges that alphabet in expectation.
The following remain different access models:

- monetary or otherwise calibrated transfers;
- other outcome lotteries or subjective randomization;
- proxy-contingent scoring rules;
- audits or verification penalties;
- repeated consequences;
- multiple strategic agents; and
- a target that changes during elicitation.

These can enlarge the effective outcome menu or change the incentive
constraints.  They must be declared as access, not treated as free
instrumentation.

## ASMP-9 consequence

An arbitrarily rich transcript does not imply an identified value object when
the demonstrator chooses the transcript strategically.  Without verification
or calibrated consequences, the finite decision menu itself bounds strict
type identification in the deterministic grammar.  Classical random problem
selection restores full-ranking elicitation only by adding expected-utility
and commitment assumptions that must be tested or enforced in any physical
bridge.

## Proof debt before any registration

1. Exhaustively compare the capacity formula against every deterministic
   direct mechanism for every type domain through `n=3`.
2. Verify the full-domain capacity through at least `n=7`.
3. Verify the `(n-1)!` best-response multiplicity of the report-top mechanism.
4. Verify strict random-pair elicitation for all true/report pairs through
   `n=5`.
5. Construct a zero-regret adjacent-swap witness for every omitted pair
   through `n=7`.
6. Verify the sharp uniform normalized margin through `n=7`.
7. Fail closed on malformed rankings, utilities, outcome maps, and pair
   distributions.
8. Keep transfers, verification, Bayesian claims, dynamic targets, and
   physical compliance outside the theorem.

## Claim boundary

This is a finite outcome-menu specialization of classical mechanism-design
principles.  The positive random-pair construction is explicitly prior art
from Azrieli, Chambers, and Healy (2021).  Version v0.65 is not a new
revelation, taxation, random-problem-selection, strategyproofness, or
verification theorem; it is not evidence about human or model behavior; and
it does not resolve ASMP-9.
