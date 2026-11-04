# ASMP-9 v0.16 registered execution abort

The first prospectively registered v0.16 execution did not complete inside
its frozen resource envelope.

- registered wall cap: 120 seconds;
- outer command timeout observed: 184.04 seconds;
- output directory: not created;
- result/receipt: not emitted;
- surviving worker: explicitly terminated after the cap breach.

Therefore:

```text
G9_resource_and_scope = fail
scientific gates = not_evaluated
registered verdict = not_evaluated_resource_abort
```

No mathematical outcome from this execution is claim-eligible. The theorem
proof and burned development census remain available as development work, but
they are not promoted by this run.

The failure exposed an implementation defect in the protocol packaging:
full exact endpoint enumeration at the largest compact-value cells was too
expensive, and the runner emitted its receipt only after completing every
stage. Any successor must:

1. use a disjoint registry;
2. benchmark its verification cost only on burned cells;
3. write a start/abort ledger before the expensive stage;
4. retain the original 120-second failure in the public record; and
5. freeze a workload that completes with substantial margin rather than
   raising the cap after failure.
