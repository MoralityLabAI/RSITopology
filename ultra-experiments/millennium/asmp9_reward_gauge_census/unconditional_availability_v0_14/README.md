# ASMP-9 unconditional availability and conditional power v0.14

This directory contains a burned CPU-only theorem-development census and a
prospective exact verification protocol. The fresh v0.14 registry has not
been executed at the implementation-freeze stage.

Version v0.13 showed that conditioning Bradley-Terry comparison counts on
vertex win balance removes scalar-value nuisance exactly, but it reported
fiber availability and conditional power separately. This successor asks
whether those quantities combine into a nuisance-uniform unconditional
guarantee.

The candidate result is a no-go: an unbounded scalar nuisance can concentrate
the experiment on singleton fibers. The conditional test remains exact, but
its unconditional power gain above size vanishes because the informative
fiber is almost never realized.

The development artifacts are never claim-eligible. The theorem,
implementation, tests, environment receipt, and fresh registry become
claim-eligible only if a later registration seals their exact bytes before
the fresh run, every registered gate passes, and an independent verifier
accepts the resulting artifact.

The protocol does not claim a general conditional-inference theorem or an
ASMP-9 resolution.
