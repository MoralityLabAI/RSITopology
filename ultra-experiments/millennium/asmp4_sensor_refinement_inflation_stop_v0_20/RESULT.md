# Result v0.20

Every raw symbol of a feasible finite sensor transducer can be cloned into `m`
irrelevant registered colors. The construction preserves feasibility, hidden-
state beliefs, plant dynamics, and exact writes, but gives

`A_m=mA` and `L_T(m)=m^T L_T`.

Forced-raw read capacity therefore increases by `log2(m)`. For the computed
sensor family, the exact region is
`[2+log2(m),infinity) x [2,infinity)`, while the color-forgetting quotient has
the fixed region `[2,infinity) x [2,infinity)`. The forced-raw read threshold is
unbounded even though the plant and control-relevant statistic never change.

Two implementations check the general computed and golden fixtures and all
768 clones of the 256 small deterministic transducers for `m=1,2,3`. Each
clone factor preserves the `80/176` feasible/infeasible split.

This supplies a convincing scoped stop against seeking a plant-only read
entropy from forced-raw local fixtures. Progress requires an explicit sensor
selector, an optimization over encoders, or an allowed sufficient-statistic
quotient. The result does not refute a parameterized sensor theorem and does
not resolve the full global ASMP-4 variational program.

The final current-state 21-package regression passes all 244 tests in 327.11
seconds. `REQUIREMENT_AUDIT_v0_20.md` maps that evidence to every frozen
resolution obligation and records why the disposition is an operational stop,
not a complete negative resolution.

The v0.21 successor formalizes the exact-support quotient-first route. It
eliminates duplicate-label inflation while leaving the v0.20 stop intact for
unspecified plant-only forced-raw semantics.
