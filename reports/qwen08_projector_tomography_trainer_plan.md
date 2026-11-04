# Qwen-0.8B projector tomography trainer plan

This is an inference-only causal measurement run. It applies no optimizer and writes no model weights.

## Scientific object

Four rank-one between-class-scatter projectors are reconstructed from the frozen construction half at layers 11, 15, 19, and 23. Each source node is required to have a `lineage_certified` receipt. The experiment attenuates every binary subset of those four projectors and measures teacher-forced answer log probability on disjoint geometry-validation prompts.

The complete Boolean cube identifies the exact multilinear interaction spectrum. Leave-one-subcondition-out prediction tests whether degree-two terms learned on eight graph families improve prediction on the ninth beyond an additive model. A seeded orthogonal random-projector arm is the matched control.

## Safety and claim boundary

The intervention uses the gauge-invariant projector `v v^T`, never a transported signed coordinate. It is therefore engineering evidence, not authorization for signed VPD rewards or disparate weight edits. The run cannot establish recursive improvement or a global high-rank fiber.

## Resource envelope

- Windows Job Object: 6,144 MB aggregate/process memory hard cap.
- CPU hard cap: 50%.
- Sustained I/O ceiling: 750 MB/s.
- CUDA allocation allowance: 3,440 MB on the 4 GB device.
- Wall-clock timeout: 3,600 seconds.
- Batch size: 8; checkpoint after every arm/subset work unit and at least every 60 seconds.
- No swap allocation by the experiment.

The runner is resumable by work unit. In `finally`, it removes hooks, releases model/tokenizer/tensors, runs Python garbage collection, synchronizes CUDA, empties its cache, and calls IPC cleanup. The wrapper terminates only the owned process tree and writes a post-run cleanup receipt.
