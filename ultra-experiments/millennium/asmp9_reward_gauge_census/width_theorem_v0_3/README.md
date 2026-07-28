# ASMP-9 sharp query-width theorem v0.3

This theorem seed upgrades the v0.2 finite frontier into a proposed
dimension-uniform access result. For primitive integer reward rays bounded by
`B`, positive scale quotiented, and adversarial comparison-threshold radius
below one return unit, the exact worst-case coefficient width is:

```text
2        at B=1;
2B-1     at B>=2.
```

`THEOREM_DRAFT_v0_3.md` contains the proof. The verification runner replays the
constructive separator over a preregistered disjoint lattice grid and
exhaustively checks the extremal lower witnesses.

This remains a cycle-coordinate theorem after potential shaping has already
been removed. It is not a full ASMP-9 resolution.

