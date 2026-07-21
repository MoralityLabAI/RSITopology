# ASMP-10 v0.4c continuation note

Version 0.4b refreshed the event-file heartbeat successfully but performed no
optimizer steps. Checkpoint restoration then failed because the sealed base
trainer loads the checkpoint with `map_location` equal to the CUDA device.
That operation also moves the saved CPU RNG byte tensor to CUDA, whereas
`torch.set_rng_state` requires a CPU byte tensor.

Version 0.4c retains the heartbeat repair and adds an exact device correction:
immediately before the unchanged trainer restores RNG state, the shim moves the
saved PyTorch CPU and CUDA RNG byte tensors to CPU. Their byte contents are not
changed and no RNG is reseeded. The shim restores the original setter functions
when the trainer returns.

All scientific configuration, model and optimizer checkpoints, metric history,
cell ordering, decision rules, and resource caps remain byte-identical. The
v0.4b abort is retained as engineering evidence.
