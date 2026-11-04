# Qwen0.8B Controller-Task Stalk Capture Protocol

Protocol: `qwen08_controller_task_capture_v0_1`.

The registered capture supplies fresh, outcome-blind layer-19 and layer-23 representations to the controller-mesh
typed-sheaf study. It consumes the gym’s sealed 576-prompt manifest and the already pinned Qwen3.5-0.8B base
checkpoint. It performs no generation, logit evaluation, gradients, adapter loading, or weight mutation.

The capture is prepared but not authorized or run. Authorization requires:

- the exact committed protocol, capture implementation, gym config, and prompt-manifest hashes;
- a clean RSITopology implementation commit present on a remote ref;
- explicit confirmation of the registered 6,144 MB RAM, 3,440 MB GPU, 50% CPU, 750 MB/s I/O, 3,600-second,
  batch-four, zero-swap envelope;
- the existing Job Object hard-cap and cleanup validation receipt.

Successful capture emits 36 immutable NPZ chunks and a complete index. Any bounded abort is a valid incomplete
result and does not authorize controller analysis. The index carries `outcomes_consumed=false`,
`logits_materialized=false`, `generation=false`, `gradients=false`, and `weight_mutation=false` as enforced fields.
