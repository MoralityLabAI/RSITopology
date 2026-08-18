# ASMP-2 source-fiber boundary v0.2

This theorem packet strengthens the earlier ASMP-2 resolution-readiness
harness. It gives:

1. an exact necessary-and-sufficient source-fiber criterion for uniform safety
   and utility certification in finite registered decision problems;
2. a smooth dominated QMD counterexample in which both hidden worlds have a
   valid non-inert policy, but require opposite policies;
3. an exact minimax success value of `1/2` for every finite source sample size;
4. a sharp density boundary for unrestricted continuous continuation classes;
   and
5. a finite active-design lower bound when no positive safety margin is
   registered.

The packet is a **candidate negative resolution argument**. The accompanying
audit deliberately separates what is proved from what the current ASMP-2
wording still leaves ambiguous.

Run:

```powershell
python -m pytest test_source_fiber.py -q
python run.py --output artifacts/result_v0_2.json
python verify_result.py --result artifacts/result_v0_2.json `
  --output artifacts/verification_v0_2.json
```

Read [`THEOREM_v0_2.md`](THEOREM_v0_2.md) before the resolution audit.
