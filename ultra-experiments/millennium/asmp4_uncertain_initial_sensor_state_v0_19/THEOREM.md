# Uncertain initial sensor-state theorem v0.19

## Registered initial uncertainty

Retain the v0.18 finite sensor transducer and the v0.13 positive-volume
collar. Replace the known initial sensor state by a registered nonempty set
`I subseteq S`. Nature chooses the actual `s_0 in I` adversarially. The
controller knows `I`, but does not learn `s_0` through an uncharged reset,
random seed, normal symbol, or calibration phase. Universal safety starts at
the first plant step.

Raw sensor words and normal cells remain separately injective in the read
transcript. The normal symbol depends only on the normal coordinate and cannot
encode the actual initial sensor state, mode, or transducer event.

## Theorem

Initialize the v0.18 subset observer at

`B_0=I`.

The uncertain-initial experiment is feasible if and only if every reachable
transition from `B_0` has a singleton current `q`-class set. This is the same
local transition rule as v0.18 but a genuinely different registered start
belief.

Sufficiency follows by decoding the singleton class at every raw observation
and applying the normal-cell controller. For necessity, choose the earliest
mixed transition on a common raw history. Earlier homogeneous transitions fix
one common earlier `q` history. The two supported executions can therefore use
the same normal cell and have the same pre-step normal value `n`. Their current
safe-control intervals are `[-1-2n,1-2n]` and `[7-2n,9-2n]`, which are
disjoint. Unknown initial state cannot be replaced by an arbitrary
representative.

Let `A_I` be the output-multiplicity adjacency matrix of the reachable observer
from `I`, and let

`L_T(I)=e_I^T A_I^T 1`

be its exact length-`T` raw language. For `0<rho<=1`, exact counts are

- reads: `L_T(I) ceil(rho*2^T)`;
- writes: `2^T ceil(rho*2^T)`.

Every feasible experiment has exact asymptotic region

`[1+log2(rho(A_I)),infinity) x [2,infinity)`.

An infeasible experiment has an empty universal-support safety region.

## Initial-set monotonicity

If `I subseteq J`, every word possible from `I` is possible from `J`, so
`L_T(I)<=L_T(J)`. Feasibility is downward monotone: feasibility from `J`
implies feasibility from `I`. The converse fails because cross-state witnesses
that are absent from either singleton belief can coexist in the union belief.
Thus larger initial uncertainty can destroy feasibility or raise the read
threshold, but it cannot improve either quantity under this raw-charging
contract.

## Separating fixtures

1. The v0.18 history-toggle transducer is feasible from either known singleton
   state but infeasible from `I={0,1}` at the first symbol.
2. A synchronizing transducer emits `2q+s` and resets to state zero. From full
   uncertainty it has `L_T(I)=2^(T+1)`: uncertainty costs one finite bit but
   leaves spectral radius 2 and read corner 2.
3. A union-dominant transducer has a low-rate state with two raw symbols per
   step and a high-rate state with four. From the low state its read corner is
   2; from `I={0,1}`, `L_T(I)=4^T`, spectral radius is 4, and the read corner is
   3. Initial uncertainty can therefore change the asymptotic rate, not just a
   transient constant.

## Complete two-state census

Take every deterministic binary-output, binary-next-state transducer with two
hidden states and two `q` classes. There are 256 transition tables. Pair each
with the three nonempty initial sets `{0}`, `{1}`, and `{0,1}`, giving 768
registered experiments.

Two independent enumerators give:

- singleton feasibility counts 80 and 80;
- full-uncertainty feasibility count 32;
- 192 feasible and 576 infeasible registered pairs;
- signature histogram `000:160`, `111:32`, `110:32`, `100:16`, `010:16`,
  where bits record feasibility from `{0}`, `{1}`, `{0,1}`;
- 32 transducers feasible from both known singleton states but infeasible from
  their unknown union; and
- among the 32 full-uncertainty feasible tables, reachable-belief-count
  histogram `{1:8,2:12,3:12}` and `L_T=2^T` for every table.

For this two-state full-uncertainty census, feasibility is equivalent to global
current-output separation of the two `q` classes. This equivalence is special
to starting from the full two-state set; the general theorem still requires
reachable beliefs.

## Scope

This closes finite registered initial-state sets under universal support safety
and no pre-safety calibration. It does not classify a probabilistic prior on
the initial state, an active calibration phase before safety begins,
controller-side raw compression, continuous sensor state, expected length, or
average and block error. It remains a local registered-family theorem, not the
full nonlinear coordinate-invariant ASMP-4 variational characterization.
