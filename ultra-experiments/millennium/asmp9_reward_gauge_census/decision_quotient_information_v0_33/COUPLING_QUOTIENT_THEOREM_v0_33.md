# Decision-relevant semantic-coupling quotient

## Status

**Unregistered development theorem. Not claim-eligible.**

This note closes a mathematical shape mismatch between two already sealed
ASMP-9 objects. It does not estimate the physical coupling between them.

## Setup

Let:

- `x in F^n` be a raw behavioral cell table;
- `C in F^(s x n)` map cells to semantic residuals;
- `K in F^(o x s)` couple semantic residuals to localized observation
  coordinates;
- `L in F^(d x o)` analyze those observations into reward coordinates; and
- `Q in F^((p-1) x d)` contain the differences between `p` candidate policy
  occupancies and one registered reference policy.

The policy-margin effect of a coupling is

```text
D(K) = Q L K C.
```

Two couplings are decision-equivalent precisely when they have the same
`D(K)`.

## Theorem

Under column-major vectorization,

```text
vec(D(K)) = (transpose(C) kron (Q L)) vec(K).
```

Consequently:

```text
decision-relevant coupling dimension
  = rank(C) rank(Q L);

decision-null coupling-gauge dimension
  = o s - rank(C) rank(Q L).
```

If an experiment may query arbitrary exact scalar linear functionals of `K`,
then `rank(C) rank(Q L)` queries are necessary and sufficient to identify
`D(K)` over the unrestricted coupling space.

### Proof

The vectorization identity is the standard formula
`vec(A K B) = (transpose(B) kron A) vec(K)`, with `A = Q L` and `B = C`.
The rank formula follows from the classical Kronecker identity
`rank(A kron B) = rank(A) rank(B)`.

For sufficiency, query any row basis of
`transpose(C) kron (Q L)`. Every policy-margin effect is then a known linear
combination of those answers.

For necessity, suppose fewer than the stated number of scalar linear queries
are made. Follow the all-zero answer branch if the strategy is adaptive. The
queried row space has dimension strictly below the row space of the canonical
operator, so it cannot contain that row space. Equivalently, its kernel is
not contained in the canonical operator's kernel. There is therefore a
nonzero coupling perturbation producing the same query transcript but a
different policy-margin effect. This proves the lower bound for deterministic
adaptive as well as nonadaptive exact linear queries. Randomized or noisy
query models require a separately declared theorem.

## Actual v0.31-v0.32 specialization

The sealed matrices have:

```text
v0.31 analysis map L             3 x 8, rank 3
v0.31 policy matrix              6 x 3
policy-difference analysis Q L   5 x 8, rank 3
v0.32 cross-difference C         6 x 12, rank 6
coupling K                       8 x 6, 48 raw coordinates
```

Therefore:

```text
decision-relevant dimension      6 * 3 = 18
decision-null gauge dimension    48 - 18 = 30
```

Restricting the candidate set to the reference and first nonreference policy
reduces `rank(Q L)` to one. The same coupling space then has six
decision-relevant and 42 decision-null directions. This control demonstrates
that the quotient is answer-dependent: asking which of six policies wins is
strictly more informative than asking one fixed pairwise policy question.

The executable development result also supplies:

- a nonzero `8 x 6` coupling whose complete policy effect is exactly zero;
- a one-coordinate coupling with a nonzero policy effect; and
- eighteen independent rows of the canonical effect operator.

## What this closes

The earlier report correctly refused to invent a unique `8 x 6` coupling.
The theorem shows that uniqueness is unnecessary for the downstream decision
question: only an 18-dimensional quotient can affect the full registered
policy family, while a 30-dimensional coupling gauge is decision-null.

## What remains open

This result does **not**:

- estimate the real observation-to-semantic coupling `K`;
- show that arbitrary scalar linear functionals of `K` are physically
  queryable;
- provide a noisy or finite-sample acquisition procedure;
- validate the mixture-affine behavioral interface on a model or human;
- establish the cost model needed by the v0.33 information allocation; or
- resolve ASMP-9.

The next prospective protocol must declare an empirical coupling acquisition
grammar. It can then ask whether that grammar spans the 18-dimensional
decision quotient, rather than requiring all 48 raw coupling coordinates.
