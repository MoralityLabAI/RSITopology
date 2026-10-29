# ASMP-9 v0.21 post-run note

## What changed

The v0.20 audit asked for either an exact parameterized algorithm or a
hardness reduction for the local finite-design problem inside one general
biconnected block.  Version v0.21 supplies a hardness classification at the
count-floor boundary:

```text
ASMP local availability numerator = T_G(0,2).
```

Thus even the value of the forced design is #P-hard to compute.

## What did not change

The above-floor design problem remains open.  When `N>|E|` or
`epsilon != 1/2`, edges can have `INTERIOR` status with nonzero probability
and allocations are no longer forced.  The objective becomes a weighted sum
over partial orientations followed by a maximin integer design problem.  The
classical total-orientation result does not classify that object.

The 2019 branchwidth/pathwidth algorithms are relevant positive prior art for
the count-floor numerator.  They must not be described as algorithms for the
full weighted ternary ASMP objective without a new derivation.

## Next load-bearing question

The next local-block step should target one of:

1. a reduction showing #P-hardness of exact weighted availability for a fixed
   rational `epsilon < 1/2` and declared counts;
2. an exact fixed-parameter algorithm for weighted ternary availability in
   branchwidth/treewidth and maximum count; or
3. the complexity of the above-floor maximin allocation itself.

Only after the nonadaptive local object is classified should the program
spend on adaptive allocation or response dependence.

