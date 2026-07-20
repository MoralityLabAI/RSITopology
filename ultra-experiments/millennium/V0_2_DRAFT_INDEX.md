# ASMP v0.2 Draft Index

Additive work toward a possible v0.2 is kept separate from the frozen seven in
`ASMP-CANDIDATE-SET-v0.1`.

- [`V0_2_SCOPE_EXPANSION_DRAFT.md`](V0_2_SCOPE_EXPANSION_DRAFT.md) audits six
  specification, dynamics, reflection, adversarial-internal, and multi-agent
  proposals against primary prior art.
- [`problem_set_v0_2_expansion_draft.json`](problem_set_v0_2_expansion_draft.json)
  records their provisional dispositions. Five remain possible top-level
  additions; bounded tiling is currently a quantitative `ASMP-5A` subproblem.
- [`validate_v0_2_expansion.py`](validate_v0_2_expansion.py) checks the draft's
  structure while confirming that it points to the frozen v0.1 parent.
- [`V0_2_INPUT_RECEIPT.json`](V0_2_INPUT_RECEIPT.json) records the filename,
  byte count, and SHA-256 of the supplied brainstorm source used during
  reconciliation.

Run:

```powershell
python ultra-experiments/millennium/validate_v0_2_expansion.py
```

This directory is a non-normative drafting surface. It neither supersedes v0.1
nor establishes that the candidate statements are open.
