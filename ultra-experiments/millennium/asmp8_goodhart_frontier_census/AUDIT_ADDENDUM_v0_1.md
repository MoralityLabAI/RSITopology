# Post-run audit addendum — ASMP-8 finite Goodhart census v0.1

## Integrity

- The registered run bound itself to commit
  `47540897610836280876c03867ab89bd62cdb2b2`.
- The tracked diff hash was the SHA-256 of the empty byte string.
- The independent verifier reproduced all five artifact hashes and the primary
  witness polarity.
- Runtime was 2.11 seconds and traced Python peak memory was 9.15 MB, below the
  registered ceilings.

## Result

The primary falsification gate passed. At matched scalar pressure
`KL(pi || p0) = 0.627115814` nats, with the same reference policy and proxy,
the Gibbs path produced true-reward gain `+0.055264597` while the top-spike path
produced `-0.482093509`. The exhaustive census contained 5,300 registered
reward-vector/pressure cells satisfying the sign-separation gate.

This rejects the sufficiency of scalar KL pressure on the registered finite
class. It does not show that KL is useless: it remains a valid coordinate, but
the optimizer-path or reachable-set geometry carries additional information.

## Control limitation discovered after reveal

`G2` is mathematically valid but not a tight liveness control. Its true-reward
alphabet has spacing 1 while `2*epsilon = 0.5`, so the registered proxy errors
cannot reverse the ordering of unequal reward levels. The observed maximum
regret is consequently zero. This verifies the `2*epsilon` inequality but does
not demonstrate its sharpness.

The sealed v0.1 artifact is not changed. A successor should add a near-tie
alphabet with a frozen adverse tie-breaking convention so that the positive
control attains the bound. This limitation does not affect `G4`, whose policies,
KL match, and true-reward gains are computed independently of `G2`.

## Other claim limits

- Phase labels and alignment-bin diversity are finite-class descriptive
  summaries.
- The two optimizer paths are deliberately different curves through the policy
  simplex; the result does not classify all paths.
- No statement about reinforcement-learning training dynamics, heavy-tail
  asymptotics, or real reward models follows from this census.
