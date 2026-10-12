# Result: common-history adaptation restores the ASMP-4 corner

**Successor scope note.** The v0.6 same-plant registration fork leaves this
expected-read/worst-write theorem unchanged while downgrading the broader
canonical status: normal-form closure must be registered, not presumed.

## Verdict

The v0.4 nonrectangular line is exact for fixed public codebook schedules, but
it is not the architecture-complete repeated-block frontier. Once the current
code pair may be chosen deterministically from common decoded history, the
exact finite frontier obeys a Bellman recurrence and strictly improves after
only two blocks. With logarithmic worst-write slack, adaptation restores the
coordinatewise lower corner asymptotically.

For `n` three-tick blocks, let `V_n(b)` be minimum expected read length at worst
write budget `b`. The exact recurrence is

~~~text
V_n(b)=min_a[r(a)+sum_i p_i V_{n-1}(b-w_i(a))].
~~~

A complete deadline census finds 207 unlabelled codes, 4,968 labelled codes,
250 feasible action signatures, and 13 coordinatewise adaptive minima. The
Bellman optimizer has an exact closed policy: use canonical Huffman whenever
residual write slack is positive and balanced at zero slack. Its finite value
is `(7/4)n+(1/4)E[(n-tau_k)_+]`, where `tau_k` is the first time the Huffman
length surplus hits initial slack `k`. The
smallest strict fixed-schedule counterexample is

~~~text
(expected read, worst write) = (57/16,5),
~~~

which improves the best fixed-schedule read total `15/4` by `3/16`.

The exact finite lower corner remains excluded: `V_n(2n)=2n`. But a guarded
Huffman relay with slack `k` has write total at most `2n+k`. Its surplus
increments are `-1,0,+1` with probabilities `1/2,1/4,1/4`, so `2^S` is a
martingale and the probability of ever hitting the guard is at most `2^{-k}`.
The expected read bound is

~~~text
(7/4)n + n/(4*2^k).
~~~

Taking `k=ceil(log2 n)` makes write slack sublinear and total read excess at
most `1/4`. The closed asymptotic region per physical tick is therefore

~~~text
[7/12,infinity) x [2/3,infinity).
~~~

The same argument covers every positive sorted four-plan law. In the strict
skew phase `2p_1+p_2>1`, let `q=p_3+p_4` and
`lambda=p_1/q>1`; then `lambda^S` is the exponential martingale and the lower
corner per block is `(3-2p_1-p_2,2)`. On the boundary and balanced side,
balanced already attains `(2,2)`. Thus every law in the v0.4 probability phase
has a rectangular common-history adaptive asymptotic region.

More generally, for any finite i.i.d. plan alphabet of size `m`, let `mu` be
the optimal expected binary prefix length and `q=ceil(log2 m)`. A fixed-length
fallback and an exponential-supermartingale guard attain `(mu,q)` with only
`O(log n)` pathwise write slack. Hence the closed per-block region is

~~~text
[mu,infinity) x [q,infinity).
~~~

An exact rational grid checks all 57 ordered laws of total mass 12 from two
through six plans: ten fixed-equality cases, 21 direct cases, and 26 guarded
cases, with no failure.

Independence is sufficient but not necessary. A general guard lemma applies
whenever a public causal fast-code policy satisfies the uniform conditional
bound `E[lambda^(length-q)|history]<=1`. The harness verifies a genuinely
correlated four-state Markov source whose Huffman labelling rotates with the
decoded state; all four conditional MGF factors equal one and its exact
32-block guard distribution matches the registered length process.

The uniform one-step MGF is not necessary. If bounded fast-code surplus obeys
`S_t/t->h-q<0` almost surely, any diverging sublinear threshold makes the
probability of ever reaching the guard vanish while adding only `o(n)` worst
write slack. An exact independent time-varying fixture alternates the canonical
law with Huffman laws approaching the balanced boundary. Its surplus rate is
`-1/8`, its read threshold is `15/8`, and every fixed one-step multiplier
eventually fails; the guarded closed region is nevertheless
`[15/8,infinity) x [2,infinity)` per block.

This separation persists under stationarity and ergodicity. In the observable
renewal-age Markov source, plan zero publicly resets the predictive state and
all other plans increment it. Reset probability is uniformly at least `3/8`,
so the chain is positive recurrent and aperiodic. Conditional Huffman coding
is optimal at every state, the stationary threshold satisfies
`1.8161864422<h_*<1.8161864463`, and the weak-state MGF factors still defeat
every fixed multiplier. The closed region is `[h_*,infinity) x [2,infinity)`.

More generally, let `Z_t` be a common sufficient predictive state for any
stationary ergodic full-support source on `m` plans. If `h_H` is the stationary
mean of the conditionally optimal Huffman length and
`q=ceil(log2 m)`, the full closed region is
`[h_H,infinity) x [q,infinity)`. Ergodicity supplies the negative-drift guard
when `h_H<q`; the fixed code attains equality when `h_H=q`.

When enabled plan support varies across a finite strongly connected public
predictor, the write threshold becomes the positional value `rho` of a
prefix-code mean-payoff game. Conditional Huffman read has stationary mean
`h`, and guarding it against a worst-optimal positional write code gives the
full region `[h,infinity) x [rho,infinity)`. In the exact alternating
four-plan/two-plan fixture, all 13 write policies are enumerated: one balanced
policy has value `3/2`, the other 12 have value `2`, and the exact region is
`[11/8,infinity) x [3/2,infinity)`.

The three-state competing-cycle fixture makes policy choice nontrivial. Its 13
write policies split into three with value `5/3`, four with value `2`, and six
with value `3`. Expected-optimal Huffman uses `(2,1,3,3)`, while the selected
worst-optimal baseline uses `(1,2,3,3)`. Their difference drift is `-1/10`,
and exact correlated state/surplus propagation gives region
`[13/10,infinity) x [5/3,infinity)`. The two-sided potential
`v=(0,-4/3,-2/3)` satisfies the Shapley equations at value `5/3`, proves the
write converse against arbitrary history-dependent policies by telescoping,
and gives the exact finite worst-path excess bound `4/3`.

The fixed-schedule segment remains exact under v0.4's explicit restriction;
the one-block Pareto obstruction also remains exact. What fails is treating
that restricted segment as the full history-adaptive asymptotic answer.

## Interpretation

Common-history adaptation performs causal budget banking. High-probability
short Huffman outputs accumulate slack, rare long outputs spend it, and a
public balanced fallback enforces the worst-case path budget. No private
schedule, timing channel, or extra communication edge is used.

This successor does not amend the canonical v0.1 metric or weaken the v0.3
same-cost collapse theorem. It strengthens the negative-resolution case:
even the heterogeneous expected-read/worst-write fixture becomes rectangular
in the natural adaptive asymptotic interpretation.

## Evidence

- Central exact verifier: `adaptive_frontier.py`
- Independent reimplementation: `verify_adaptive_theorem.py`
- Unit tests: `test_adaptive_frontier.py`
- Full proof and scope: `THEOREM.md`
- Requirement audit: `COMPLETION_AUDIT_v0_5.md`
- Canonical quantifier audit: `CANONICAL_SCOPE_AUDIT_v0_5.md`
- Harness stopping boundary: `STOPPING_ARGUMENT_v0_5.md`
- Prior-art/novelty firewall: `PRIOR_ART_AUDIT_v0_5.md`

The integrated run passes 62 tests across all six ASMP-4 generations, every
current central and independent verifier, and a fresh byte-identical replay of
the frozen v0.1 receipt-bound verification artifact.

The adaptive buffer-banking mechanism is classical in spirit. The prior-art
audit therefore limits the contribution to this exact ASMP-4 instantiation and
makes no general source-coding novelty claim.
