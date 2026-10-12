# ASMP-8 finite Goodhart-frontier census

This CPU-only experiment asks whether `KL(pi || p0)` is sufficient to describe
optimization pressure independently of optimizer path on a frozen finite
class. Gibbs tilting and a top-state spike mixture are matched to the same KL
at seven pressures, then evaluated exhaustively on 15,620 normalized labelled
true-reward vectors with a shared proxy.

The experiment can reject scalar KL sufficiency on this class. It cannot prove
a universal Goodhart frontier. A uniform-error positive control and a rare-tail
average-error negative control prevent the result from being read as “all proxy
guarantees are impossible.”

## Before the claim-eligible run

```powershell
python -m pytest ultra-experiments/millennium/asmp8_goodhart_frontier_census/test_goodhart_frontier.py -q
```

Commit the protocol, runner, verifier, tests, and this README. The registered
runner refuses to begin with a tracked diff or uncommitted sealed input.

## Registered run

```powershell
python ultra-experiments/millennium/asmp8_goodhart_frontier_census/run.py `
  --protocol ultra-experiments/millennium/asmp8_goodhart_frontier_census/protocol_v0_1.json `
  --output-dir ultra-experiments/millennium/asmp8_goodhart_frontier_census/artifacts

python ultra-experiments/millennium/asmp8_goodhart_frontier_census/verify_result.py `
  --artifact-dir ultra-experiments/millennium/asmp8_goodhart_frontier_census/artifacts
```

Outputs are write-once and include the result, receipt, phase table, alignment-
bin table, strongest witnesses, and a generated Markdown report.
