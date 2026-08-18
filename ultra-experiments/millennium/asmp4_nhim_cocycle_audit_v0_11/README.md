# ASMP-4 NHIM/cocycle audit v0.11

This package repairs the most contestable remaining premise in the ASMP-4
stopping certificate.  It replaces the v0.6 binary-input derivative shortcut
with bounded interval authority and maps the closed loop to an explicit
full-shift random cocycle NHIM, while preserving both exact sensor-registry
regions.

**Successor note.** The
[v0.12 circle extension](../asmp4_positive_dimensional_nhim_v0_12/RESULT.md)
removes the zero-dimensional-fiber objection by adding a neutral tangent
rotation and checking a compact connected invariant circle against a classical
NHIM definition.  The exact regions remain unchanged.

- [THEOREM.md](THEOREM.md): repair theorem
- [RESULT.md](RESULT.md): compact disposition
- [COMPLETION_AUDIT_v0_11.md](COMPLETION_AUDIT_v0_11.md): evidence matrix
- [PRIMARY_DEFINITION_SCOPE_v0_11.md](PRIMARY_DEFINITION_SCOPE_v0_11.md): checked primary definition and nonclaims
- [primary_definition_receipt_v0_11.json](primary_definition_receipt_v0_11.json): URL, PDF hash, pages, and clause mapping
- [REVIEWER_PACKET_v0_11.md](REVIEWER_PACKET_v0_11.md): reproduction, caveats, and falsification conditions
- [nhim_cocycle_claim_v0_11.json](nhim_cocycle_claim_v0_11.json): frozen claim

Run:

```powershell
python run_verification.py
python verify_nhim_cocycle_audit.py
python -m pytest -q test_nhim_cocycle_audit.py
```

Expected results are twelve central gates, eleven import-independent checks,
and ten focused tests.  The integrated ASMP-4 chain contains 155 tests.
