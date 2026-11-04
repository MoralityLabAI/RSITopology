# ASMP-3 normative-closure impossibility v2.18

This package closes the remaining normative-definition blocker as a scoped
impossibility result.  It constructs two incompatible, clause-preserving
completions of the sealed v0.1 text, binds them to the exact v0.7 material fork,
and proves that no source-only rule can select one while remaining valid in
every completion.

The operational result is:

```text
sealed v0.1 + current authority record
    -> FIX and ADM both survive
    -> unique entailment-sound closure is impossible
    -> one authorized scope axiom resolves the binary fork
```

Primary documents:

- `NORMATIVE_CLOSURE_IMPOSSIBILITY_THEOREM_v2_18.md` gives the theorem and
  proof;
- `AUTHORITY_HANDOFF_v2_18.md` gives the exact authorized repair choices;
- `COMPLETION_AUDIT_v2_18.md` records verification and regression totals.

Reproduce:

```powershell
python run_normative_closure_impossibility.py
python verify_normative_closure_impossibility.py
python -m pytest . -q
python build_release_manifest.py
```

Generated JSON receipts are ignored by default and must be deliberately added
when sealing a release.
