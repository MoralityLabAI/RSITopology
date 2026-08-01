# ASMP-4 heterogeneous port-cost result v0.4

## Result

The v0.3 boundary has been sharpened in both directions.

First, positive changes of units do not break serial collapse. If the read and
write charges are `a_r J_T+o(T)` and `a_w J_T+o(T)` for one shared bilateral
tree cost, the closed region is exactly

~~~text
[a_r h_J,infinity) x [a_w h_J,infinity).
~~~

Second, genuinely different risk functionals can break rectangularity. In the
four-plan no-lag prefix game, the read port pays expected length under
`(1/2,1/4,1/8,1/8)` and the write port pays worst-case length. Over every finite
binary prefix-free read/write codebook pair, the only Pareto minima are:

~~~text
Huffman/Huffman: (7/4,3)
balanced/balanced: (2,2).
~~~

No safe code can combine expected read cost below `2` with worst write length `2`.
Worst write length `2` forces a balanced `2+2` tick-one partition, and causal
refinement forces the read partition and every read length to be at least two.
Safe write length `3` is dominated by the exact Huffman point because Kraft's
inequality gives the universal expected-read bound `H(p)=7/4`; longer write
codes miss the registered three-tick deadline.

Both matching formats have identity relays, so the fixture retains bilateral
copy closure for every admitted minimal tree. The tradeoff comes from the two
costs choosing different diagonal trees.

More generally, for any positive sorted four-plan law, the unbalanced expected
cost is `E_H(p)=3-2p_1-p_2`. The frontier has two minima exactly when
`2p_1+p_2>1`; otherwise balanced `(2,2)` is the unique minimum. Four plans are
minimal because every full three-leaf binary tree has the single length profile
`(1,2,2)`.

For repeated three-tick blocks on a fixed plant-independent public codebook
schedule, the complete registered fixed-schedule asymptotic frontier is

~~~text
upward-closure conv{(7/12,1),(2/3,2/3)}.
~~~

The coordinatewise lower corner `(7/12,2/3)` is excluded. This is an exact
nonrectangular two-port frontier with fixed control authority and no side
channel, caused by heterogeneous expected/worst cost semantics plus a frozen
synchronous deadline.

The later v0.5 adaptive-history successor shows that the scheduling qualifier
is load-bearing. A codebook schedule chosen deterministically from common
decoded history strictly improves the two-block frontier and attains the
coordinatewise corner asymptotically with `O(log n)` write slack. The v0.4
one-block and fixed-schedule claims remain exact; they are not the full
history-adaptive asymptotic region.

## Verification

The central harness checks:

- all `4 x 24 x 24 = 2,304` labelled extremal-format assignments and exact
  representative feasible counts `48,0,0,192`;
- synthesis of all 240 feasible causal prefix tables and safe replay of all
  960 plan-specific terminal controls;
- all five full binary tree shapes, 120 plan-labelled codebooks, and 14,400
  ordered pairs, with 960 feasible factors and 3,840 safe terminal replays;
- all 34 positive ordered denominator-16 probability laws, split into 27
  strict-skew, two boundary, and five balanced cells with zero phase errors;
- exact frontier sizes `1,1,1,2` from one through four plans;
- the two finite Pareto points and excluded coordinatewise corner;
- all 90 public format schedules through twelve blocks;
- the exact frontier identity `4 E[length_r] + max length_w = 10n`; and
- 400 positive rational unit-rescaling cells.

The independent verifier reimplements the causality partition test, cost
calculation, schedule identity, theorem sentinels, and frozen-canonical scope
check without importing the central harness.

The integrated post-audit run passes all 44 tests across the frozen v0.1 game,
definition audit, v0.2 theorem, v0.3 metric repair, and this v0.4 successor.
Every central and independent theorem verifier passes. The historical v0.1
verifier remains byte-identical to its SHA-256-bound run receipt rather than
being reformatted to satisfy a newer lint preference.

`COMPLETION_AUDIT_v0_4.md` reconciles this successor with every frozen ASMP-4
obligation and states why another finite grid would not strengthen the current
candidate resolution absent a concrete proof or scope objection.

`PRIOR_ART_AUDIT_v0_4.md` compares the result with primary invariance-entropy,
network-entropy, cascade-source-coding, and zero-delay-coding sources. It treats
the normal-form result as a repository-specific diagnosis and makes no
literature-level novelty claim.

## Claim boundary

This package is a boundary strengthening, not a new ASMP-4 resolution claim.
The frozen v0.1 problem charges both ports with the same worst-case complete
transcript-cardinality formula. The witness deliberately changes that premise
to expected read length versus worst-case write length and freezes no-lag
prefix deadlines, while allowing every finite binary prefix-free codebook. It
shows precisely why “different units” and “different cost orderings” must not
be conflated.
