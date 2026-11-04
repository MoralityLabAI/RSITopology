# ASMP-5: bounded verifier-drift reachability

This experiment enumerates a finite reflective-update game. Adaptive and frozen-root arms receive identical candidate edge IDs and payloads; the successor checker is stored in both arms, but only the adaptive arm activates it.

The semantic safety table is analyst-only. Candidate generation and certified reachability do not accept it as an argument. The result can establish a finite counterexample or bounded positive classification only.

Run order:

1. Commit this directory without `artifacts/`.
2. Run `python run.py --protocol protocol_v0_1.json --output-dir artifacts`.
3. Run `python verify_result.py --result artifacts/result_v0_1.json --receipt artifacts/receipt_v0_1.json --output artifacts/verification_v0_1.json`.

