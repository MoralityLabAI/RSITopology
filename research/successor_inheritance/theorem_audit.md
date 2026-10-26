# Theorem and assumptions audit

## Versions and claim boundary

Source experiment: Control-Harness PR #12, commit
`165d8ee43a805fd9bdcf5a6e486a8c880cd35698`. The six originals and Git blob
identities are preserved in [provenance.json](provenance.json).

Manuscripts: the [first paper](https://github.com/MoralityLabAI/morality-lab-site/blob/5caf6458c1c92825d2c7231a7c38597549f54181/papers/SuperAlignment_Intractability_1.pdf)
and [companion paper](https://github.com/MoralityLabAI/morality-lab-site/blob/5caf6458c1c92825d2c7231a7c38597549f54181/papers/SuperAlignment_Intractability_2.pdf),
both revised October 10, 2026. The source experiment cites the original August
draft. The revisions already correct several claims that would otherwise be
overstated; this audit does not attribute the old statements to the current paper.

**Conclusion:** the finite query lower bound is valid under its stated access
restrictions. The experiment does not establish super-polynomial FRC in
recursive depth. A complete artifact-reading verifier decides this toy
property in a linear scan of the training rows.

## 1. Exact membership-query proposition

Let N = 2^b, H = {0,1,2,3}, U = {4,...,N-1}, and M = N-4. The candidate family
contains the clean function f_0(x)=0 and, for every s in U, a point violator
f_s(x)=1[x=s]. A verifier receives only membership answers f(x). It must accept
f_0 and reject every f_s. It cannot inspect the artifact, source code, target,
digest, seed, or implementation state, and has no authoritative action fence.

**Proposition (proved here).** A deterministic, zero-error verifier needs M
distinct queries in the worst case, even if it chooses queries adaptively.

**Proof.** Follow its all-zero transcript. With fewer than M distinct queries,
some s in U is not queried. The clean function and f_s produce the same
transcript, including the adaptively chosen subsequent queries. Completeness
on the clean function forces acceptance of f_s. Querying all U attains M. The
guarantee concerns distinguishing clean from *any* point violation, not an
attacker known in advance to have supplied a violation. Without completeness,
the always-reject verifier would invalidate this formulation.

**Randomized two-sided extension (proved).** Suppose false rejection of clean
inputs is at most alpha and false acceptance of every point violator is at most
beta. If q bounds the queries on every random tape, couple clean and point
runs using the same tape. For uniform s independent of the tape, they differ
only if s lies in the all-zero query set Q. Therefore

`1 - beta <= Pr(reject | uniform point) <= alpha + q/M`,

so `q >= (1-alpha-beta) M`. At alpha=beta=1/3 this gives M/3. This is the
off-support version of revised Theorem 3; that theorem uses the full cube
and gives 2^m/3. The source experiment's M bound is for zero error and must
not be presented as a two-sided 1/3-error bound. Neither proof is a runtime
lower bound for unrestricted verifiers.

For a detector that rejects only after witnessing a violation, B uniformly
sampled distinct points in U detect a fixed target with probability
`min(B,M)/M`. Hence a per-target miss guarantee delta requires at least
`ceil((1-delta) M)` such probes. This differs from the two-sided bound because
clean false rejection is zero. Adaptivity cannot extract location information
from a sequence of all-zero answers.

## 2. Width b is not recursive depth k

The single-target sweep holds the mechanism fixed and varies b. The exponential
factor comes solely from representing M = 2^b-4 possible locations with b bits.
The adaptive sweep fixes b=11 and varies k in {1,2,4,8}; its probe budget is
exactly 16k, and it inserts at most k new deviations. There is no inferred
exponential growth in k. At fixed b the supply of fresh targets is finite and
the implemented process stops after at most M rounds.

Under ideal fresh uniform sampling, write p=min(B,M)/M and r=1-p. For k<=M,
the expected surviving count satisfies `E[S_j]=r(E[S_(j-1)]+1)`. Thus it is
`r(1-r^k)/(1-r)` for p>0 and k for B=0. This is an elementary prediction for
one repair strategy, not a lower bound on the optimal defender's resources.

The revised first paper explicitly adds Assumption 6, `m(k)>=c k`, plus
reachability of every competent point-violating agent and adversarial
concentration on a point. The experiment does not test or imply that
assumption. Substituting b=k in a plotting script would impose it by design.
Theorem 3 becomes a conditional bound on FRC only if **every admissible
construction** must certify an untrusted successor through the restricted
black-box interface. The paper's remarks make that extra restriction explicit.

## 3. Mapping to Fidelity Recursive Complexity

Revised Definitions 3--4 minimize defender resources while requiring both
minimum fidelity over all rounds and a task-competence floor eta on the
reference environment. They include a fixed patch map D and quantify over
admissible adaptive strategies. The source benchmark samples one attack/patch
strategy and does not optimize resource allocations or instantiate that
quantification. Its end-of-round fidelity cannot replace the minimum over
rounds: repairing a violation does not make an earlier violation disappear.
Definition 11's round-k summary is usable as a shorthand only when it retains
the Definition 3 history-level requirement; it is not automatically equivalent
to an arbitrary final-round distribution.

The toy's `ordinary_task(0)==solve` checks one competence bit. It prevents the
reported benign/contaminated comparison from being explained by stopping that
task. It is not a measurement of general capability or a rich Comp_k. The
shutdown property covers one valid intervention response; disabling the
interface, time-to-halt, and unauthorized resumption from Definition 2 are not
modeled. The pristine agent defers the task and is an integrity control, not
a competent candidate for the FRC optimization.

Even with the competence floor, this family admits a compact competent safe
policy (solve the task, halt on shutdown), and an exact artifact-reading check.
Consequently there is no general construction-hardness result here. The
original Theorem 2 is Conjecture 1 in the revised manuscript. Corollary 2's
linear test-expansion cost is a bound on that defense, not on the minimum FRC.
The source's reported query totals are audit-cost surrogates, not measured FRC.
The companion paper's fixed-budget fidelity-versus-capability curve is another
quantity, explicitly distinguished in its revised Section 2.

## 4. Semantic verifier defeats this toy's apparent hardness

`semantic_check` reads every supplied row and resolves the final shutdown label
at each in-domain key. Unmentioned contexts default to halt. It accepts iff
no final label is continue. Correctness follows immediately by induction over
the ordered rows using the learner's last-write-wins rule. This checks the
actual final semantics: merely rejecting any historical continue row would
incorrectly reject a repaired artifact.

For L rows and K distinct in-domain shutdown keys it takes L scan steps and
O(K) memory, with expected constant-time dictionary operations. Context-key
processing adds bit cost (up to O(b) per key); it is not unit-cost arithmetic
on unbounded integers. No enumeration of 2^b contexts or policy query is used.
Truth enumeration in the comparison runner is separately accounted as oracle
instrumentation. The paired experiment checks agreement with that oracle,
not with an assumed label returned by the semantic verifier itself.

Assumptions: the verifier sees the complete immutable artifact actually used;
the known total deterministic learner faithfully implements these semantics;
there is no hidden state or unrecorded data; and the verified artifact remains
bound to the constructed successor. These assumptions are true by construction
here. They need separate validation for a learned model. This is a fixed
white-box verifier, outside Definition 9's on-support restriction and
Assumption 5, so its success does not contradict the query theorem.

## 5. Other guarantees and accounting caveats

| Mechanism | Conditional guarantee | What it does not establish |
| --- | --- | --- |
| Historical replay | Equality on H | Safety outside H |
| Random probes | Finite-domain detection probability under the sampling model | Universal certification from a small sample |
| Corpus digest allowlist | Approved bytes under collision resistance and an uncompromised external list | Semantics of arbitrary new updates; safe unapproved updates are denied |
| Semantic scan | Exact P for the declared learner and complete rows | Correctness of an unknown training algorithm |
| Action fence | Returned halt for every toy shutdown call | Safety of an incomplete or bypassable real interface |
| Recompilation | Same inherited rows produce the same rule | Biological inheritance, learned-model persistence, or novel child behavior |

The toy fence calls the total `on_shutdown` method before returning halt; it
is not robust to arbitrary blocking code or exceptions outside this model.
The adaptive `fenced_worst_case_fidelity` field is a construction-level
constant. The single-target arm explicitly enumerates fenced responses.
The three-generation lineage consists of three fresh compilations of identical
rows, not three independent learners or three self-designed transformations.

The source's `exhaustive_queries=N` is a nominal full-domain budget: `any`
short-circuits, so it is not the actual executed call count. `hash_gate_bytes`
is one illustrative artifact, not the cell's mean. The port retains these
fields for comparability. An edge-case correction makes adaptive summary
totals use completed rounds when k exceeds M; the pinned matrix is unaffected.

Published seeds and XOR/arithmetic seed derivation provide deterministic replay,
not cryptographic privacy or a proof of independent randomness. The exact
probability calculations use ideal independent draws; Wilson intervals on the
deterministic seed grid are descriptive, without a formal coverage guarantee
for arbitrary adaptive attacks. No seed was retuned after observing results.

## 6. Eigensystem escape and the repository's geometry

The point update is a concrete instance of the first paper's Lemma 2: the
restriction of the shutdown response function to H is unchanged while its
extension changes. For binary deviation vector v, the observation projection
R_H satisfies `R_H e_s=0` for s outside H. Inheritance carries this unobserved
behavioral difference through the artifact. It does not require a semantic
expressivity gap, meta-reasoning, a new ontology, or actual self-modification.

The companion paper's revised Proposition 1 instead concerns a correction
subspace S and Jacobian J. When J_SS is invertible, drift is
`atan(||J_perp,S J_SS^(-1)||_2)`; it depends on leakage out of S, not merely
on a nonzero commutator or overlap with top growth directions. Its revision
explicitly separates geometric drift from invisible change under a projection.
The symbolic experiment has no J or learned S and measures no eigenvalues,
principal angles, lineage or holonomy. These meanings must not be equated.

RSI Topology already supplies complementary matched controls: band failover,
spectrum-preserving conjugation, and loop holonomy can defeat successively
coarser identity summaries. Its [signed-control theorem](../../docs/CONTROL_RISK_THEOREM.md)
also states that identity measurements alone cannot establish behavioral
semantics. A corpus hash here is not an `AnchorRegistry` lineage or
`holonomy_clean` certificate. A future bridge must bind artifacts and the
learner to operator receipts, measure behavioral outcomes separately, and
test whether geometry adds held-out prediction beyond direct artifact access.
No such geometric or real-model evidence is claimed by this experiment.

## Claims ledger

| Claim | Evidence class | Disposition |
| --- | --- | --- |
| M deterministic exact queries; randomized q >= (1-alpha-beta)M | Proved finite query results | Valid only under the explicit access/error model |
| Exact semantic decision by final-label scan | Proved property of this learner | Linear row scan; complete-artifact assumption |
| Controls, persistence, and fence responses | Deterministic synthetic results | Verified by executable tests and records |
| Detection rates and surviving counts on the seed grid | Empirical synthetic findings | Reproduced; no real-model extrapolation |
| Exponential growth in recursive depth | Conditional theoretical implication | Requires untested context-growth/reachability assumptions |
| Universal unfenced super-polynomial FRC | Conjecture | Not established by these results |
| Spectral drift predicts successor contamination in trained models | Research conjecture | No relevant model data in this experiment |

The companion paper's reserve-collapse theorem also needs persistent hazard,
no expected recovery off failure events, and bounded increments. These are
explicit in its revision; a finite repairable row process supplies no evidence
for them or for almost-sure collapse of an unbounded successor chain.
