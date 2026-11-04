# ASMP-4 registration-fork result v0.6

## Result

The canonical achieved-transcript problem has no registration-independent
answer until sensor computation closure is fixed.

For one four-mode uncertain safety plant, with identical evaluator, control
authority, deterministic noiseless serial channels, and terminal-language
cardinality cost, the exact regions are:

~~~text
computed sensor:   [1,infinity) x [1,infinity),
forced raw sensor: [2,infinity) x [1,infinity).
~~~

The computed sensor emits the action-sufficient statistic `{0,1}|{2,3}`. The
forced raw sensor must distinguish all four modes. In both cases every binary
required-action word occurs, so the write threshold is one bit per step.

The result is analytic for every horizon. The harness exhausts all 15
partitions of four modes, finds exactly four safe partitions with block counts
`2,3,3,4`, and directly replays every disturbance path through horizon eight.
An independent implementation reconstructs the partition census and language
counts without importing the central code.

The two branches sit inside a complete registry-lattice theorem. Across all
32,767 nonempty subsets of the 15 sensor partitions, exactly 2,047 are
infeasible, while 16,384, 12,288, and 2,048 have minimum safe block count two,
three, and four. All 245,760 single-partition inclusion edges obey registry
monotonicity, with 26,624 strict improvements. Thus the raw/full strict fork is
one certified edge-to-chain witness inside the complete registry universe,
not a cherry-picked pair.

More generally, if the required-action fibers have sizes `n_i`, the safe
`k`-cell partition count is the Stirling convolution
`s_k=sum product_i S(n_i,k_i)`. This gives closed formulas
`2^u-1` for infeasible registries,
`(2^s_k-1)2^(u+sum_(j>k)s_j)` for every exact corner, and a corresponding
strict-edge count. Two implementations verify all 18 action-block shapes and
75 action partitions through five modes. The five-mode `(2,3)` shape alone
classifies all `2^52` registries analytically.

The same fork has an exact rational evaluator-transversal realization:
`n'=(3/2)n+u-q(z)`, `z'=w`, with
`q(z)=(12+13z-z^3)/24` on `z=-3,-1,1,3`. Its values are `0,0,1,1`; the normal
multiplier is `3/2`, the tangent reset derivative is zero, and the normal input
derivative is one. Exact replay confirms every correct-control path remains on
`n=0` and either wrong binary control leaves it immediately.

## Consequence

The v0.2/v0.3 bilateral normal-form theorem remains correct for code classes
closed under moving controller computation upstream and downstream. The raw
registration deliberately fails upstream closure. Therefore this is not a
counterexample to that theorem; it is a counterexample to treating its closure
premise as automatic for every architecture permitted by the canonical phrase
“registered causal code.”

The repository’s ASMP-4 status should therefore be “partial structural
classification with an exact registration fork,” not an unconditional
canonical negative resolution. Selecting which branch is intended requires a
specification decision, not a larger finite census.

The conclusion is now checked directly against the canonical problem file.
Central and import-independent source parsers find all eight relevant
architecture clauses and zero clauses selecting either upstream-computation
closure or forced-raw transduction. They then bind those two textual
completions to the exact unequal regions above. The resulting disposition is
`registration_class_underdetermined`.

This is no longer a metadata assertion. A central model-completion harness and
an import-independent reconstruction extract 13 canonical obligations, build
both finite code registries explicitly, replay every mode word through horizon
six, and verify all 13 obligations for each registry. The source selects
neither registry predicate, while the independently derived regions remain
distinct. Thus the existential definition of `R_K` is genuinely relative to
an unspecified registration domain.

The audit also searches beyond the ASMP-4 subsection. The word `registered`
occurs 31 times in the complete normative Markdown, with zero code-domain
definitions. The companion `problem_set_v0_1.json` expressly identifies
itself as a non-normative index, points back to the Markdown, marks the
candidate set as an ungraduated definition draft, and adds no ASMP-4 sensor-
grammar field. No global source silently closes the missing quantifier.

The fork also extends to a parameterized theorem. For any finite full-reset
mode plant with `m` required-action classes and registered sensor-partition
grammar `Gamma`, let `kappa` be the minimum number of cells in an admitted
partition refining the action classes. The exact region is

~~~text
[log2 kappa,infinity) x [log2 m,infinity),
~~~

and the plant is infeasible if no admitted partition refines the action
classes. The converse covers arbitrary history-dependent selection from
`Gamma`. Central and independent censuses reproduce all refinement pairs
through five modes: `1,3,12,60,358`.

For constrained finite mode dynamics and a fixed registered transducer `f`,
Theorem 5 gives a second exact formula. Confinement is feasible precisely when
every reachable subset-observer belief fixes the required action `g`; then

~~~text
finite region:     [log2 |L_f(T)|,infinity) x
                   [log2 |L_g(T)|,infinity),
asymptotic region: [h_f,infinity) x [h_g,infinity).
~~~

The entropies are logarithms of spectral radii of finite deterministic subset
observers. The exhaustive audit covers 60,134 graph/initial-set/transducer/
action cases through three modes, including 37,430 feasible cases, and matches
12,060 subset counts to direct path expansion.

The same 60,134-case universe has a complete first-failure classification.
There are 37,430 infinitely safe cases; all others first fail with histogram
`10642,8406,3110,534,12` at horizons one through five. The maximal witness
`0->{1},1->{2},2->{0,1}` with a constant sensor is safe through horizon four
and fails exactly at five. This proves a finite/infinite separation rather than
inferring one from a truncated run.

On the golden-mean graph `0->{0,1}, 1->{0}`, a forced raw sensor and constant
safe action give region `[log2(phi),infinity) x [0,infinity)`, whereas a
computed constant sensor gives `(0,0)`. The exact read counts are Fibonacci
numbers `F_(T+2)`.

Theorem 6 treats history-adaptive sensor grammars on constrained graphs. Its
exact finite Bellman recurrence minimizes the sum of continuation-language
sizes over safe registered partitions at each public belief. On the strongly
connected, aperiodic graph

~~~text
0->{0,1}, 1->{0,2}, 2->{0,1}, initial belief {0,2},
~~~

the stationary adaptive grammar has read and write counts `F_(T+1)` and corner
`(log2 phi,log2 phi)`. Every feasible fixed member of the same two-partition
grammar has read count `2^T`, so its best corner is `(1,log2 phi)`. This proves
a strict asymptotic benefit from public-history sensor adaptation without a
transient or periodic loophole. More generally, the viable belief recursion is
a prescribed-initial-state extended entropy game. The positional-policy
theorem gives

~~~text
rho_I = lim_T V_T(I)^(1/T)
      = min over stationary viable policies pi of rho_I(A_pi),
region = [log2 rho_I,infinity) x [h_g,infinity).
~~~

Thus one stationary belief policy attains the optimal read rate for every
finite registered graph, not only for the fixture. The positional theorem is
credited to the entropy-game literature in `PRIOR_ART_AUDIT_v0_6.md`; the
ASMP-4 contribution is the exact belief/partition reduction and two-port
consequence.

The v0.7 relational-action successor removes unique safe actions as a scope
loophole. On one four-mode full-reset plant it proves an exact nonrectangular
adaptive region between `(log2 3,log2 3)` and `(2,1)`, while the computed and
raw registrations on that same plant remain distinct rectangles. This
successor also proves that zero-error randomized observation supports contain
a deterministic safe subtree with no larger port languages. These results
strengthen the registration stopping conclusion without changing any v0.6
claim.

Two independent implementations exhaust all 120,050 three-mode two-partition
grammar cases at horizon four. They find 99,524 adaptively feasible cases,
including 1,572 with no feasible fixed member, and 4,863 strict improvements
over the best fixed member. All 99,524 are also infinitely viable, with no
horizon-four-only false positive, and every case obeys the required-action
lower bound.

The full three-mode grammar lattice sharpens that bounded finding. Across all
372,155 nonempty grammars and 960,400 inclusion-cover edges, finite Bellman
values and infinite viability are monotone under adding registered partitions.
There are 104,556 strict finite-value edges and a maximum one-edge ratio of 81.
Exactly 12 horizon-four-feasible cases are not infinitely viable; all use a
singleton grammar and first fail at horizon five. This transient boundary is
invisible in the earlier two-partition slice and is now isolated rather than
silently generalized away.

## Evidence

- Exact theorem: `THEOREM.md`
- Central harness: `registration_fork.py`
- Independent verifier: `verify_registration_fork.py`
- Tests: `test_registration_fork.py`
- Completion/scope audit: `COMPLETION_AUDIT_v0_6.md`
- Harness stopping argument: `STOPPING_ARGUMENT_v0_6.md`
- Prior-art boundary: `PRIOR_ART_AUDIT_v0_6.md`
- Adaptive proof ledger: `PROOF_AUDIT_v0_6.md`
