# ASMP-10 v0.4b continuation note

The first v0.4a continuation performed no optimizer steps. The hard-cap wrapper
read the existing `events.jsonl` modification time from the previous timed-out
segment and immediately classified it as a stale checkpoint while the new
Python process was importing PyTorch.

Version 0.4b adds a thin resume shim. Before importing the byte-identical v0.4
trainer, it refreshes the event file's filesystem modification time without
changing its contents. This gives the resumed process the registered startup
grace period. The shim then delegates directly to the sealed runner.

The scientific configuration, checkpoints, optimizer state, random states,
transition definitions, cell order, and resource caps are unchanged. The
failed v0.4a wrapper receipt is retained as engineering evidence.
