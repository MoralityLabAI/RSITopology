# ASMP-2 active-design census v0.2.2

This second performance-only amendment removes `tracemalloc`, whose instrumentation expanded the unchanged registered computation from roughly 15.75 seconds to 171.67 seconds. It uses sampled process RSS, an internal 150-second operational ceiling, and the unchanged 180-second external total-wall ceiling.

All scientific fields remain byte-bound to v0.2. Projector algorithms remain byte-bound to v0.2.1. Neither quarantined v0.2.1 outcome nor any scientific field was consulted in this amendment.

