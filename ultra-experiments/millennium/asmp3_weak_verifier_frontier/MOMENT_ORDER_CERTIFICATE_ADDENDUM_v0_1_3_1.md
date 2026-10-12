# v0.1.3.1 order-three certificate clarification

Cold review found that v0.1.3 emitted the sharp order-three primal law and
verified the upper envelope by exact vertex enumeration, but documented an
explicit dual certificate only at order four.

This additive clarification supplies the missing symmetric certificate:

```text
1{S>=5} <= S/15 - (S)_2/15 + (S)_3/30
```

for every `S in {0,...,9}`. Taking expectations under the frozen independent
reference moments gives

```text
9/(5*15) - 72/(25*15) + 504/(125*30) = 39/625.
```

The existing law supported on `{0,2,3,5}` has tail `39/625`, so primal and
dual values agree exactly. This changes no result or minimum-order conclusion;
it makes the order-three rung independently checkable in the same form as the
order-four rung.

The reference qualifier was already present in `MOMENT_ORDER_RESULT_v0_1_3.md`:
the claim concerns moments of the independent `Binomial(9,1/5)` reference and
does not generalize `m*=4` to other tuples or real judge panels.

