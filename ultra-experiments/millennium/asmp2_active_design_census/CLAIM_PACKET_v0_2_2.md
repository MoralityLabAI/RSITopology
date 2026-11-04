# ASMP-2 v0.2.2 resource-measurement amendment

No scientific estimand, threshold, seed, tie rule, feature class, candidate environment, deployment family, selector, or claim boundary changes.

The sole change is replacing intrusive Python allocation tracing with process-level RSS sampling. The operational timer begins on entry to `main` and must finish result serialization inside 150 seconds, leaving a registered 30-second margin for artifact emission and interpreter shutdown under the external 180-second ceiling.

The v0.2.1 outputs remain quarantined and are not inputs to this run.

