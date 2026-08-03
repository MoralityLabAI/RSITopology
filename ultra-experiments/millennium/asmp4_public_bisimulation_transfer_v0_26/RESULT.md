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

The theorem assumes additive edge costs. It transfers nondeterministic games
but does not solve their multidimensional adversarial mean-payoff regions, and
it does not prove finite abstraction for general nonlinear or continuous-
belief ASMP-4 systems.

The complete 27-package chain passes all 304 tests in 281.10 seconds with
Python bytecode and pytest caching disabled.

The v0.27 successor proves a sharp `epsilon` region bound when only matched
edge costs are approximate and safety remains exact. It also refutes
metric-only zero-error safety transfer and supplies a strict Lipschitz-margin
repair.
