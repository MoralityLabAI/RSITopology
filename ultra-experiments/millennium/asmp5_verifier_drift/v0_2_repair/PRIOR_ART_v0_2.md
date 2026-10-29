# ASMP-5 verifier-drift repair prior-art boundary v0.2

This finite census sits below established trusted-kernel and reflective-agent
work.

- Necula's proof-carrying code fixes a safety policy and lets an untrusted code
  producer supply a machine-checkable proof. The frozen-root arm is a tiny
  finite analogue, not a new proof-carrying-code architecture.
- Yudkowsky and Herreshoff's *Tiling Agents for Self-Modifying AI, and the
  Lobian Obstacle* studies self-modifying agents and reflective proof barriers.
- Critch's parametric bounded Lob theorem supplies a genuine bounded-resource
  reflection result. This census does not reproduce or strengthen it.

The only contribution claimed here is experimental: an exact matched finite
transition system that isolates activation of a replaceable checker, plus a
resource-safe implementation of the v0.1 registered universe.

References:

- G. C. Necula, "Proof-Carrying Code," POPL 1997,
  DOI `10.1145/263699.263712`.
- E. Yudkowsky and M. Herreshoff, *Tiling Agents for Self-Modifying AI, and
  the Lobian Obstacle*, 2013 draft.
- A. Critch, "Parametric Bounded Lob's Theorem and Robust Cooperation of
  Bounded Agents," arXiv:`1602.04184`, 2016.
