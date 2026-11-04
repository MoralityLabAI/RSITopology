# ASMP-9 v0.48 ordering-modulus development result

## Verdict

**`decision_dependent_ordering_live`**

Four of ten predeclared development cells have disjoint optimal evidence
orderings for four-class identification and root-group loss, with strictly
positive cross-regret in both directions. The statistical experiment,
parameter mixture, confidence level, and coverage rule are held fixed; only
the downstream decision risk changes.

This is burned development work. It selects the shape of a disjoint
confirmation and is not claim-eligible.

## Exact search

- Three independent binary calibration cells.
- Allocation `(1,1,1)`.
- Eight complete error-count-vector outcomes.
- Ten predeclared grid/alpha cells.
- Exact four-class risk on the union grid of 125 shared channels.
- Exact root-group risk `p_root`.
- Uniform mixture of the registered parameter laws as the reference outcome
  distribution.
- Every one of the `8! = 40,320` evidence orderings exhausted for each loss
  in each cell.

Live cell indices were:

```text
1, 3, 7, 8
```

## Cleanest live witness

For

```text
levels = {0,1/5,2/5}
alpha  = 1/10,
```

the exact results are:

| Objective | Minimum reference-expected upper | Optimal orderings |
|---|---:|---:|
| four-class identification | `1984/3125 = 0.63488` | 5,040 |
| root-group loss | `246/625 = 0.3936` | 5,040 |

The two optimizer sets are disjoint. Every four-class optimizer places

```text
(1,1,1)
```

first; every root-group optimizer places

```text
(0,1,1)
```

first. The remaining seven outcomes may occur in any order, explaining the
`7! = 5,040` optimizer counts.

Using a root-optimal order for four-class loss incurs exact regret

```text
4/3125 = 0.00128.
```

Using a four-class-optimal order for root-group loss incurs exact regret

```text
2/625 = 0.0032.
```

The result is not a tie-breaking artifact: there is no common optimum and
both cross-regrets are strictly positive.

## Interpretation

The Buehler bound is smallest only relative to a designated ordering. This
finite witness makes the dependency operational:

```text
same experiment + same coverage + same reference law
  + different decision risk
  => different optimal evidence ordering.
```

For four-class loss, the most useful first atom is the all-errors vector. For
root-group loss, branch errors with no root error are the most useful first
atom. The downstream quotient determines which unlikely observation can be
assigned the lowest early confidence bound.

At the all-zero endpoint used in v0.47, placing that atom first recovers the
same mandatory-atom modulus regardless of the remainder of the ordering.
Ordering dependence begins when confidence error must be allocated across
multiple outcomes.

## Other live cells

Disjoint optimal sets and positive cross-regrets also occur at:

```text
{0,1/5,2/5}, alpha=3/10
{0,1/10,3/10}, alpha=3/10
{0,1/10,1/5,2/5}, alpha=1/10.
```

The remaining six cells are reported as exact nulls rather than discarded.

## Operational incident

The first serializer retained every tied optimizer in every cell and attempted
to materialize an unnecessarily large JSON payload while the shared drive was
nearly full. It failed with `ENOSPC` and left only a zero-byte partial file,
which was removed before rerun. No scientific output survived that attempt.

The repaired instrument retains optimizer counts and a bounded sample of
orders, then performs a streaming complete cross-audit. The rerun completed
and wrote the canonical result:

```text
SHA-256:
cd57bfc889d8bdcdc46a33dbe11b1af7faf1ff4503091d8f9a6bd83efd19efa2
```

## Confirmation implication

Use a new 12-outcome experiment with:

- allocation `(2,1,1)`;
- an unsearched rational grid;
- exact subset dynamic programming rather than permutation enumeration; and
- frozen prediction of disjoint optimizer sets and positive cross-regrets.

The dynamic program must first reproduce the exhaustive eight-outcome
development census exactly.

## Claim boundary

This is an internally searched finite witness. It does not establish a
universal impossibility, an optimal continuous statistic, a real preference
channel, or resolution of ASMP-9.
