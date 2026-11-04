# ASMP-4 round-robin review

## Verdict: `revise_before_pilot`

The rational finite-game approach is appropriate, and the proposal consistently
limits exactness to a frozen architecture. One quantifier ambiguity is
load-bearing, however, and must be repaired before code fixes it accidentally.

## Findings

### Fatal as written: the viability estimand permits a different code per cell

`V_T` is the fraction of initial cells “from which some admissible causal code”
works. Literally this is `fraction{x: exists C_x}`, whereas the ASMP capacity
region requires `exists C: for every x in K_0`. Cell-specific synthesis can
encode initial-state information in controller choice outside either charged
port and substantially overstate viability. The strongest possible result would
therefore not test the stated two-port question.

**Concrete repair:** freeze one of two distinct estimands:

```text
V_T = max_C fraction{x in registered K_0 cells: C confines x for all w},
F_T = 1{exists one C confining every registered cell for all w}.
```

Report both if desired, but use only `F_T` for a capacity claim. The solver
certificate must identify the single universal code and replay it jointly over
all cells and disturbance branches.

### Scope-narrowing: H3 is not a refutation of the canonical conjecture

The canonical statement explicitly allows architecture-dependent tradeoff
inequalities. A solver-certified compensation cell refutes rectangularity for
this grammar, not separate-port lower bounds in general. Rename H3 accordingly.
Charge read and write independently by worst-case transcript-alphabet size (or
frozen prefix-free length) over the whole horizon; never substitute total bits
or realized-path usage.

### Repairable: exact scope and resources are under-specified

Ordered partition count, action-dictionary size, controller-memory states, and
budget-allocation grammar need numeric values now. Without them, neither
completeness of backward synthesis nor the 4–120 minute estimates are auditable.
State the finite policy count/state recurrence, peak table size, and timeout
semantics. The optional QBF estimate should be labelled provisional until a
small encoding reports variables and clauses. Solver timeout must remain
`undetermined`, never infeasible.

### Repairable: liveness controls need pinned cells

Run the stable zero-rate control at `c=0`; otherwise unstable unrestricted `z`
can drive `n`. Pin the analog-side-channel positive to a read-limited cell with
sufficient write authority, and pre-verify that the full-action dictionary can
cancel the registered disturbance. These avoid mistaking authority or tangent
forcing for information scarcity.

### Nonissue, conditional on implementation

The component separation and deliberate-reference rejection are strong
no-side-channel controls. Also reject controller selection conditional on the
initial cell, state-correlated initialization/randomness, mutable shared logs,
and callbacks. Exhaustive `T<=3` agreement plus rational replay is an adequate
pilot optimality check within the enumerated grammar—not beyond it.

With the universal-code quantifier fixed and grammar sizes costed, run the
pilot; do not run the optional scale-up yet.
