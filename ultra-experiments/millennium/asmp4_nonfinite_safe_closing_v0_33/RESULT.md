# Result v0.33

The sublinear safe-closing property promotes v0.24's reset-block formula to the
complete infinite-code two-port region without assuming a finite quotient.
Inside each registered recurrent component,

`R_q = closure(upward(conv(P_q)))`

and the weighted support family `h_q(lambda)` reconstructs that region exactly.
The full region is the closure of the union of the component regions, preserving
nonconvex irreversible choices.

Cost-preserving causal state conjugacies and transcript relabelings transport
the component decomposition, block sets, support functions, and complete
region, giving a coordinate-invariant registered construction.

The exact finite-horizon correction is the vector closing charge divided by
the prefix horizon.  A state-space shadowing construction is safe whenever its
error is below the registered evaluator margin.  These statements turn the
previously informal request for a nonfinite replacement into checkable
hypotheses.

The sharp witness is an infinite Thue-Morse scheduler with a one-step reset.
It has no finite exact stationary cost quotient, yet constant closing overhead
recovers the exact corner `(1/2,1/2)`.  Two irreversible aperiodic components
retain a nonconvex union and reject the false midpoint `(1,1)`.

Central and import-independent implementations check 4,096 prefix horizons,
8,320 bounded eventual-period candidates, 26,112 exact finite-correction rows,
component support geometry, the limsup boundary, and eight hostile mutations.
The explicit 34-package chain passes all 374 tests in 360.75 seconds with
Python bytecode and pytest caching disabled.

This is a nonfinite variational replacement under an explicit safe-closing
property, not a full resolution of ASMP-4.  The unresolved global obligation is
to prove safe closing—or a different exhaustive replacement—for a formally
registered normally hyperbolic nonlinear class.

V0.34 subsequently proves safe closing for compact connected public-information
components with safe local finite-cost connector certificates. It does not
derive those certificates from the still-underspecified plant-level wording.

V0.35 supplies a quantitative alternative sufficient condition: a compact
fixed-reset atlas built from strict Lipschitz safety margins, charged source
labels, and charged actuator words gives constant safe closing directly.  It
constructs such an atlas for an exact nonlinear uncertain fixture, while
leaving robust pointwise connector existence for the full canonical class
open.
