# Proposed AI Safety Millennium Problem Candidates

This directory contains the first versioned definition draft of the
**ASMP candidate set**, seven foundational mathematical problem candidates for
AI safety. The set identifier is `ASMP-CANDIDATE-SET-v0.1`; `ASMP-7` refers
only to the seventh problem.

It is not an actual prize announcement and has no affiliation with the Clay
Mathematics Institute. “Millennium” denotes the intended depth, durability, and
resolution standard—not a claim that the seven problems have already survived
the years of community scrutiny enjoyed by established prize problems.

Start with:

- [`AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md`](AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md)
  for the mathematical statements and resolution rules;
- [`problem_set_v0_1.json`](problem_set_v0_1.json) for the machine-readable
  problem registry; and
- [`REFEREE_AUDIT_v0_1.md`](REFEREE_AUDIT_v0_1.md) for the hostile candidate
  audit and unresolved definition debt; and
- [`VALIDATION_RECEIPT_v0_1.json`](VALIDATION_RECEIPT_v0_1.json) for the sealed
  file hashes and validation claim boundary.

Prospective theorem and experiment seeds also follow the
[`prior-art-before-freeze standard`](PRIOR_ART_BEFORE_FREEZE_STANDARD_v0_1.md).
The [`structured observation-kernel motif`](STRUCTURED_OBSERVATION_KERNEL_MOTIF_v0_1.md)
records a recurring instrument pattern without promoting elementary
rank-nullity into a novelty claim.

Validate the frozen structure with:

```powershell
python ultra-experiments/millennium/validate_problem_set.py
```

The validator checks the exact seven-problem universe, canonical title and
overview consistency, normative-file pointer, graduation status, positive and
negative resolution obligations, section order, formula sentinels, UTF-8, and
the primary-reference inventory. It is a structural integrity check, not a
proof that the conjectures are open or correctly posed.

The set is intentionally architecture-independent. Transformer experiments may
motivate or instantiate a problem, but no benchmark result can resolve one.
Version 0.1 is a definition-and-audit artifact, not a claim that all seven have
already satisfied the graduation standard for a funded public prize.
