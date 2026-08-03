# Result v0.26

Exact costed alternating bisimulation preserves the entire achievable
worst-path read/write budget region of an additive public-history safety game.
The proof transfers strategies in both directions while retaining unrestricted
causal memory. A deterministic finite quotient can therefore inherit v0.25's
component-indexed cycle-polytope formula.

Central and independent decorated-cover harnesses check quotients of up to 64
and 96 raw states, vector Pareto frontiers or five scalarizations, and horizons
through eight or ten, with zero transfer failures. Nondeterministic successor
sets, cost changes, state-safety changes, and missing back transitions are
tested separately.

The Thue-Morse unary chain gives a sharp infinite boundary. It has exact rate
`(1/2,1/2)` but no finite exact stationary quotient, because every finite unary
quotient is eventually periodic and Thue-Morse is not. A parity chain has the
same rate and an exact two-state quotient. Finite bisimulation is thus
sufficient, not necessary.

The theorem assumes additive edge costs. At v0.26 it transferred but did not
compute nondeterministic multidimensional adversarial regions; v0.31 now closes
that finite-quotient computation. Neither theorem proves finite abstraction for
general nonlinear or continuous-belief ASMP-4 systems.

The complete 27-package chain passes all 304 tests in 281.10 seconds with
Python bytecode and pytest caching disabled.

The v0.27 successor proves a sharp `epsilon` region bound when only matched
edge costs are approximate and safety remains exact. It also refutes
metric-only zero-error safety transfer and supplies a strict Lipschitz-margin
repair.

The v0.31 successor uses classical conjunctive mean-payoff game theory to
compute every additive finite alternating quotient supplied by this theorem,
including possible infinite controller memory and finite-memory closure.

The v0.33 successor bypasses finite exact quotients entirely under a sublinear
safe-closing property. Its Thue-Morse reset witness realizes the nonfinite
alternative anticipated by this package's aperiodic boundary.

The v0.35 successor derives safe closing from a compact robust fixed-reset
atlas, providing a plant-level sufficient route that also bypasses finite exact
bisimulation.
