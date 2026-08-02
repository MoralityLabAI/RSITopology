# ASMP-4 positive-dimensional NHIM audit v0.12

This package removes the degenerate-point escape hatch from the v0.11 repair.
It adds a neutral circle tangent to the same bounded-authority sensor fork and
checks the resulting invariant circle against a primary classical NHIM
definition.

- [THEOREM.md](THEOREM.md): positive-dimensional fork theorem
- [RESULT.md](RESULT.md): compact result
- [COMPLETION_AUDIT_v0_12.md](COMPLETION_AUDIT_v0_12.md): evidence matrix
- [PRIMARY_DEFINITION_SCOPE_v0_12.md](PRIMARY_DEFINITION_SCOPE_v0_12.md): primary definition mapping
- [primary_definition_receipt_v0_12.json](primary_definition_receipt_v0_12.json): PDF and clause receipt
- [REVIEWER_PACKET_v0_12.md](REVIEWER_PACKET_v0_12.md): reproduction, caveats, and falsification conditions
- [positive_dimensional_nhim_claim_v0_12.json](positive_dimensional_nhim_claim_v0_12.json): frozen claim

Run:

```powershell
python run_verification.py
python verify_positive_dimensional_nhim.py
python -m pytest -q test_positive_dimensional_nhim.py
```

Expected results are nine central gates, eight import-independent checks, and
nine focused tests.  The integrated ASMP-4 inventory is 164 passing tests.

Successor: [v0.13](../asmp4_positive_volume_collar_v0_13/README.md) embeds the
circle in a positive-volume safe collar and proves an exact finite-margin
correction.  The frozen v0.12 claim is unchanged.
