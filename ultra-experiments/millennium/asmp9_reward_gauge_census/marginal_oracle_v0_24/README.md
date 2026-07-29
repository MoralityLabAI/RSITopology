# ASMP-9 exact marginal-oracle development (v0.24)

This development branch asks how much information an exact local allocation
gain reveals.

The candidate theorem is that exact one-edge ratios

```text
F_G(n+e_i) / F_G(n)
```

are value-complete: `m^2` such calls reconstruct the complete uniform
availability polynomial of an `m`-edge block, including the #P-hard
count-floor value.

Read:

1. `PRIOR_ART_GATE_v0_24.md`;
2. `THEORY_DRAFT_v0_24.md`;
3. `DEVELOPMENT_NOTE_v0_24.md`; and
4. `marginal_oracle.py`.

Status: development-only, unregistered, and not claim-eligible.  The global
optimizer-output problem remains open.
