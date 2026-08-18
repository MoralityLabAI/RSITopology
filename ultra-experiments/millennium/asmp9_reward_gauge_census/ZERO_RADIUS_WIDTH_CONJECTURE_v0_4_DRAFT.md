# ASMP-9 zero-radius coefficient-width conjecture v0.4 draft

## Motivation

The corrected v0.3.1 theorem covers strictly positive comparison-threshold
ambiguity:

```text
0 < delta < 1.
```

At `delta=0`, exact ties carry information and the sharp width changes. This
document records the next theorem target rather than folding the endpoint back
into v0.3.1.

## Candidate formula

For primitive integer reward rays bounded by `B`, positive scale quotiented,
dimension `d>=2`, and exact ternary responses `sign(q dot z)`, the conjectured
worst-case coefficient width is:

```text
Q0*(B) = 1      for B in {1,2},
         B-1    for B>=3.
```

The conjecture is dimension-independent.

## Current exact evidence

Full query-family enumeration gives:

| dimension | reward bounds checked | observed exact thresholds |
|---:|---:|---|
| 2 | `B=1..8` | `1,1,2,3,4,5,6,7` |
| 3 | `B=1..3` | `1,1,2` |

These cells are exploratory and burned. A future verification protocol must use
disjoint bounds.

## Sharp lower witness

For `B>=3`, use:

```text
z =(B,   B-1),
z'=(B-1, B-2).
```

Let the two query scores be `A` and `C`. If their exact signs differ, orient
the query so that:

```text
A>=1 and C<=0.
```

Then `x+y=A-C>=1`. Since:

```text
C=(B-1)(x+y)-y<=0,
```

we have:

```text
y >= (B-1)(x+y) >= B-1.
```

The reverse orientation gives `y<=-(B-1)`. Thus width below `B-1` cannot
identify this pair.

The query:

```text
q=(B-2,-(B-1))
```

attains the bound on the witness, producing scores `-1` and `0`.

## Open proof obligation

The missing step is a dimension-uniform upper bound:

> For every pair of distinct primitive rays in the infinity-norm `B` box,
> construct an integer query of width at most `B-1` whose exact ternary signs
> differ.

A perpendicular query immediately gives width at most `B`; the proof must save
one unit in the boundary cases. The likely structure is:

1. use a nonzero two-coordinate minor;
2. take a primitive perpendicular to one projected ray when its width is at
   most `B-1`;
3. classify the remaining boundary-face cases where both candidate rays touch
   `+/-B`; and
4. build a Farey-neighbor or one-step perturbed perpendicular separator on
   those faces.

Until that upper bound is proved, the formula is a conjecture and must not be
reported as a theorem.

## Why this matters for ASMP-9

The discontinuity quantifies the value of exact indifference information:

```text
positive ambiguity: 2B-1
exact ties:          conjecturally B-1.
```

That is nearly a factor-of-two change in charged query expressivity, caused by
an arbitrarily small positive response-model misspecification. If proved, it
would give a clean instability theorem connecting access complexity to
demonstrator-model precision.

## Claim boundary

This remains a finite cycle-coordinate problem after potential shaping has
been removed. It is not yet a theorem and does not address finite samples,
human preferences, discounted shaping, or policy observations.

