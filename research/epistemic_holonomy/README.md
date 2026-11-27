# EH-01: Provenance-marked reality-tunnel mathematics

This CPU-only RSI-Topology excursion studies Robert Anton Wilson's reality tunnels through finite evidence-provenance graphs. The formal statements and claim boundaries appear in [THEOREMS.md](THEOREMS.md). The frozen experiment specification is in [protocols/epistemic_holonomy_v0_1.json](../../protocols/epistemic_holonomy_v0_1.json).

The graph vertices represent **authenticated independent-information states**. An echo of already processed evidence is a self-loop when information states are identified by original source. An updater that counts that echo as new evidence assigns a nonzero log-odds increment to the loop. The Hodge cycle projection measures this inconsistency. A source-marking error can erase the cycle; a perfectly flat belief system can still be false.

The implementation is isolated from the existing Grassmann monitor-holonomy and signed-coordinate attestation APIs.

## Reproduce

From the repository root:

    python -m pytest -q tests/test_epistemic_holonomy.py
    python scripts/run_epistemic_holonomy.py --output artifacts/epistemic_holonomy_eh01.json

Requires NumPy and pytest; no network, model weights, or GPUs. Defaults: source reliability 0.6, apparent observation counts 1, 2, 4, 8, 10, 16, and 32, paired seed 11, and 20,000 trials. The program produces deterministic exact-population calculations and a seeded paired simulation.

## Primary finite observation

Ten apparent instances of one 60%-reliable original bit generate 98.30% confidence under naive independent-copy updating, even though predictive accuracy remains 60%. Expected log loss is 1.63905 nats. Ten truly independent 60%-reliable signals yield expected log loss 0.52213 nats. The echo graph contains nine source-duplicate loops whose each holonomy is log(1.5). The provenance-corrected policy on **the identical graph** assigns zero increment to every duplicate loop.

The repository's preexisting holonomy_clean certification continues to apply only to signed-coordinate identity, not to belief truth or behavioral control.

## Proposed extension

Freeze provenance and outcome-independent source grouping before a real experiment. Measure grouped held-out calibration and loss alongside cycle projection, with baselines for repetition count and model confidence. Neural interpretability claims remain future work.
