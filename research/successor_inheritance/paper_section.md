# Proposed paper section: successor artifacts and the limits of historical verification

**Placement:** after the first paper's revised Lemma 2/Corollary 2, with a
cross-reference from FRC-Bench. This is a proposed addition for the October
10, 2026 revision; it does not edit either manuscript. Its scope and proof
obligations are detailed in the [audit](theorem_audit.md).

## Successor artifacts as carriers of unobserved behavior

Historical behavioral agreement need not survive a change in the distribution
on which a successor is evaluated. An artifact can transmit a rule that is
invisible to the predecessor's historical tests even when the successor is
compiled anew and inherits none of the predecessor's runtime state. We isolate
this mechanism with a finite symbolic construction, separating it from
self-modification search, representation learning, and model deception.

Let a successor be compiled from an ordered artifact A containing task and
shutdown rows. The last row at a key determines its label, and absent shutdown
keys return halt. A task-only update teaches an independent task. Adding one
shutdown row at s outside H={0,1,2,3} changes the response there to continue.
Both versions retain the same task competence and agree on H. Recompilation
from the contaminated artifact preserves the off-support rule. This is an
artifact-level instance of Lemma 2's indistinguishability construction, not
evidence of a learned model autonomously choosing an alternative calculus.

Writing the binary deviation vector as v and restriction to H as R_H, the
change is e_s with R_H e_s=0. The observation interface is unchanged while
an unobserved coordinate changes. This connects successor inheritance to
behavioral eigensystem escape: the artifact carries information outside the
verifier's observation set across a successor boundary.

## Access-relative certification cost

For b context bits and M=2^b-4 possible off-support points, any deterministic
membership-query verifier that accepts the clean successor and rejects every
point violator requires M distinct probes in the worst case. Otherwise a
point outside its all-zero transcript yields an indistinguishable violator.
A uniform sample of B distinct points detects a point with probability
min(B,M)/M. These are finite-family query results. The randomized two-sided
version with both errors at most 1/3 has the lower bound M/3, corresponding
to revised Theorem 3. Exponential dependence on b becomes exponential
dependence on recursive depth only with an additional context-growth and
reachability assumption such as Assumption 6.

In a pinned 1,024-trial synthetic reproduction, the single-point detection
counts were 75, 16, 1 and 0 out of 128 for b=5,7,9,11 with B=16. At fixed
b=11, the adaptive process retained means 1.0000, 1.9766, 3.9297 and 7.7266
deviations after k=1,2,4,8 rounds. Its private-query budget was 16k. These
descriptive results concern one patch strategy; they neither optimize resources
nor satisfy the minimax, all-round fidelity and competence requirements needed
to measure FRC_P(k;delta,eta).

An artifact-reading semantic verifier reverses the apparent hardness. It scans
the rows once, resolves last-write-wins labels, and checks for a remaining
continue label. It agrees with exhaustive truth on all 6,400 paired checks,
including repaired artifacts. Its row-operation cost is O(L), with O(K)
stored keys under expected dictionary costs, rather than M domain probes.
Complete access to the actual artifact and correct knowledge of the learner
are essential assumptions. This comparison demonstrates why the verifier's
information interface must accompany every hardness statement.

An external digest allowlist provides a different guarantee: it recognizes
approved bytes, rejecting both contamination and safe but unapproved changes.
An authoritative action fence forces halt at the toy interface while leaving
the internal contaminated rule intact. These controls distinguish semantic
certification, provenance integrity and constrained execution.

## Relation to spectral identity and limits

Behavioral projection escape is not the same as drift of a correction-feature
subspace under a self-modification Jacobian. The companion paper's revised
Proposition 1 ties the latter to leakage out of the subspace. RSI Topology's
spectrum-preserving conjugation and holonomy controls further show that
occupancy, subspace lineage and signed-coordinate transport carry different
information. None is measured by this symbolic experiment, and no spectral
certificate here is used to certify behavioral safety.

A future joint test must bind each successor artifact and learner to its
operator and lineage receipts, then evaluate behavior and task competence
independently. It should compare artifact-reading semantic checks with
restricted behavioral audits, and test whether geometric measurements add
predictive value. Until that bridge is measured, successor inheritance supplies
a reproducible observation blind spot and an access-relative query theorem,
not a proof of general super-alignment intractability or exponential FRC in k.

*Evidence status:* query bounds and semantic correctness are proved within
the finite model; persistence and controls are deterministic synthetic facts;
the seeded rates are empirical synthetic observations; depth-growth and
trained-model geometric connections remain conjectural. Source code, seeds,
raw records and exact test receipts are archived in RSI Topology's
`research/successor_inheritance/` module.
