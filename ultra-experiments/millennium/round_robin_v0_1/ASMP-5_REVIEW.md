# ASMP-5 round-robin review

## Verdict

**`revise_before_pilot`**. The bounded census is worthwhile and its claim
boundary is disciplined, but the adaptive-versus-root comparison is not
yet sufficiently matched to identify verifier drift.

## Findings

1. **Repairable, load-bearing — comparator mismatch.** Adaptive replacement
   traverses states with an installed successor checker; the baseline forbids
   that state change. Equal bit budgets do not ensure equal candidate paths or
   reachable-state opportunity. A separation could therefore reflect different
   update graphs rather than the accepting checker's identity. Freeze one
   candidate-edge universe of tuples `(p',T',c',proof)` for both arms, charge
   identical payloads, and retain `T'` as an inert field in the root arm. The
   only arm-dependent operations should be which checker evaluates the edge and
   whether the already-present `T'` becomes active. Report paired reachability
   on identical candidate edge IDs.

2. **Repairable — semantic-label leakage.** Saying that `Safe` is not callable
   is necessary but insufficient: the universe generator, state encoding,
   pruning logic, proof tokens, or library selection could contain `Safe` or an
   isomorphic bit. Seal the analyst-only label table after generating the
   candidate graph; hash the observable tuple supplied to `p` and `T`;
   assert that generation and reachability never read labels; and add a
   label-permutation replay that changes only analysis labels. A checker deriving
   safety from permitted behavioral semantics is not leakage and should remain
   possible.

3. **Scope-narrowing — liveness/non-Zeno.** Integer progress plus a changed
   behavior vector correctly excludes identity and finite-horizon Zeno tricks,
   but an eight-step chain is only bounded liveness, not the canonical unbounded
   progress condition. State the required count of distinct behavior vectors,
   ensure every `N` cell can support nine states, and do not condition universe
   generation on planting the required chain. Missing capacity should make that
   cell unavailable, not failed.

4. **Nonissue with explicit boundary — finite state.** Exhaustive search can
   certify a minimum counterexample or positive classification only for this
   finite universe. The proposal already prohibits inference to open-ended
   reflective safety; preserve that wording in every result headline.

5. **Nonissue/scope-narrowing — optional model run.** The frozen scorer cleanly
   estimates recursion through proposal quality only. It cannot bound evaluator,
   objective, or certificate self-improvement. Keep proposal tokens, masked
   padding, selection calls, accepted-edit count, and outer-holdout exposure
   paired by round, not merely total FLOPs.

6. **Repairable — resources.** `N` and the cardinalities of `p`, `T`, `c`, and
   the transition graph are not related explicitly. Exhaustive Boolean-table
   products can exceed the stated 45 minutes. Add a closed-form state/
   edge count, a pre-outcome benchmark, hard RAM/time ceilings, checkpointing,
   and `unavailable_resource_cap` rather than silently sampling the census.

## Strongest objection and repair

Without the shared candidate-edge construction, the primary contrast is not
causally attributable to verifier replacement. Apply the paired inert-checker
repair above before registration; then the pilot is justified.
