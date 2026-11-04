# ASMP-2 active-design regret census

This successor to `asmp2_crossed_shift` tests a non-forced finite question: how much multi-step regret does a one-step minimax environment selector incur relative to source subsets that are globally minimal under a frozen numerical score contract?

The registered universe contains all 16 corners of `{-1,+1}^4`, the complete square-free polynomial feature class through degree two, all 65,536 source subsets, and three frozen deployment sets. It is CPU-only and exhaustive over subsets. Scores are ordered after rounding to ten decimals; deterministic selected designs receive exact-rational witness checks. The run therefore does not claim exact ordering inside a numerical tie bin.

Run only after committing all sealed inputs:

```powershell
python run.py --protocol protocol_v0_2.json --output-dir artifacts
python verify_result.py --result artifacts/result_v0_2.json --receipt artifacts/receipt_v0_2.json --output artifacts/verification_v0_2.json
```
