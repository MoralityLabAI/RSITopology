# ASMP-6 round-robin review

## Verdict: `revise_before_pilot`

The bounded construction has useful liveness controls and keeps learned
codebooks out of release. Its capacity estimand is not yet tight enough for
exact enumeration to support the stated claims.

## Findings

1. **Fatal until repaired — reliability and covertness are under-specified.**
   Define whether decoding error is maximal over messages/tasks/audit histories
   or average under a frozen distribution. Define monitor advantage as a
   specific hypothesis-testing quantity (uniform composite error bounds or
   total variation between named transcript laws), and
   state whether it is evaluated per message or only after mixing over the
   hidden message. Mixture-only covertness can conceal message-specific signals.

2. **Fatal until repaired — the key regime can manufacture the headline.** A
   key rate `k` is ambiguous between `k` total bits and `kT` bits. A renewable
   one-time pad can turn ordinary task ambiguity into covert
   capacity without measuring adaptive semantic collusion. Freeze key entropy,
   monitor knowledge, reuse, and compromise model; report unkeyed capacity and
   net keyed rate after key consumption separately. Never pool them.

3. **Scope-narrowing — finite ambiguity and positive rate are not finite-grid
   conclusions.** `T<=16` cannot certify `sup_T B_T<=C`. Three positive values of
   `B_T/T` likewise do not prove positive asymptotic rate. Both must remain
   `finite_horizon_only` unless a checked subadditive upper bound or
   concatenable construction applies for every horizon.

4. **Repairable — the tensorization falsifier needs an exact budget law.** Error,
   distortion, covertness, key, and audit-history budgets do not automatically
   tensorize. Register every allocation across two blocks and compare against
   the optimum over all legal allocations, not one product-code split. Product
   challenge marginals also do not erase history dependence of adaptive
   policies.

5. **Repairable — task liveness is too aggregate.** `U_min=0.90` may permit the
   channel to spend a 10% failure budget directly on signaling. Require the
   floor per task stratum and message, report worst-cell utility, and add a
   competence-matched benign policy. The four controls otherwise provide good
   finite liveness.

6. **Nonissue with containment — safety boundary.** Aggregate-only release is
   appropriate, but a learned run still creates encoders internally. Require a
   restricted artifact lifecycle and independent approval. This can tune audit
   policy, not certify absence of unmodeled channels.

7. **Repairable — resources are not auditable.** Exact/MILP growth at `T=16`
   may exceed 24 GB or 12 hours. Record variable/constraint counts, solver and
   gap; run `T<=8` before freezing the full envelope. Qwen is premature.

## Strongest objection and concrete repair

As written, keyed mixture-covertness can yield a positive rate for classical
encryption over repeated ambiguity, making the intended phenomenon
non-identifiable. Define the full testing game, use maximal reliability and
per-message (or explicitly mixture-only) covertness, debit consumed key bits,
and make asymptotic labels conditional on a machine-checked composition lemma.
Then the pilot is worth running.
