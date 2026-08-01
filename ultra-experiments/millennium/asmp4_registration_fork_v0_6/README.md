# ASMP-4 canonical registration fork v0.6

This package tests the strongest unresolved scope seam after the v0.5
adaptive-history result. It keeps the plant, safety predicate, control
authority, channels, and canonical terminal-language metric fixed while
changing only whether the registered sensor may compute a sufficient statistic
or must emit its raw observation.

The exact asymptotic regions are `(1,1)`-cornered for the computed-sensor class
and `(2,1)`-cornered for the forced-raw class. This preserves the v0.3 theorem
inside its normal-form-closed scope and prevents its unconditional promotion
across sensor grammars that are not closed under upstream computation.

The complete four-mode registry lattice is also exhausted: all 32,767
nonempty subsets of the 15 partitions and all 245,760 inclusion-cover edges.
The exact corner is governed by the minimum safe block count, monotonicity has
no failures, and 26,624 cover edges improve strictly.

For arbitrary finite full-reset action-fiber sizes, a Stirling/Bell formula
counts every registry corner and strict lattice edge without registry
enumeration. It is independently checked on all 18 action shapes and 75 action
partitions through five modes, including lattices with `2^52` registries.

A machine-checked canonical quantifier audit reads the source problem itself:
all eight relevant architecture clauses are present, while neither sensor-
closure completion is selected. Independent code reproduces that result and
binds the two completions to their distinct exact regions. A 13-case mutation
audit rejects deletion of any required clause, insertion of any recognized
closure selector, and collapse of the two region witnesses.

A separate registry-model audit removes the remaining semantic shortcut. It
extracts 13 source obligations and checks them against executable computed and
raw code registries rather than prefilled compliance booleans. Independent
code reconstructs both registries, replays their complete mode languages, and
derives their distinct exact regions.

The global-scope audit covers the complete normative Markdown and its machine
index. It finds 31 uses of `registered`, zero definitions of the causal-code
domain, and confirms that `problem_set_v0_1.json` is explicitly non-normative
and does not add a sensor-grammar field for ASMP-4.

The general theorem parameterizes every finite full-reset mode plant by its
registered sensor-partition grammar. If `m` is the number of required-action
classes and `kappa` is the smallest admitted safe partition, the exact corner
is `(log2 kappa,log2 m)`, even for history-adaptive partition selection.

For constrained finite transition graphs with a fixed transducer, the subset-
observer theorem gives the exact corner `(h_f,h_g)`, where both label-language
entropies are finite spectral-radius computations. The golden-mean fixture has
forced-raw corner `(log2 phi,0)` and computed-sensor corner `(0,0)`.

The fixed-transducer census also classifies first failure exactly: among all
60,134 cases through three modes, 37,430 are safe forever and the rest fail by
horizon five. A constant-sensor three-mode witness is safe through horizon four
and fails at five, isolating the finite/infinite seam analytically.

For a history-adaptive sensor grammar on a constrained graph, Theorem 6 gives
the exact finite Bellman recurrence and reduces the infinite-horizon problem to
a prescribed-initial-state entropy game. An optimal stationary belief policy
exists, with exact corner `(log2 rho_I,h_g)`. A strongly connected, aperiodic
three-mode fixture has adaptive corner `(log2 phi,log2 phi)` but best fixed-
grammar corner `(1,log2 phi)`, with exact Fibonacci versus binary read-language
growth.
Central and import-independent censuses agree on all 120,050 three-mode,
two-partition grammar cases at horizon four.

They also exhaust the complete 31-member nonempty grammar lattice for every
three-mode graph/initial/action case: 372,155 grammar cases and 960,400 cover
edges. Monotonicity has no failures, 104,556 edges improve finite value
strictly, and 12 singleton grammars are safe through horizon four but first
fail at horizon five.

Run the central harness:

~~~powershell
python run_verification.py
~~~

Run the independent verifier:

~~~powershell
python verify_registration_fork.py
~~~

Run the focused tests:

~~~powershell
python -m pytest -q test_registration_fork.py
~~~

The integrated ASMP-4 run now contains 81 tests across seven generations and
11 central/independent audit programs, plus the frozen v0.1 receipt replay.
