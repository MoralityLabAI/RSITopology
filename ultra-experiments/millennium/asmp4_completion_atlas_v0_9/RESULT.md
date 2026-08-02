# ASMP-4 completion-atlas result v0.9

## Result

All five canonical completion requirements now have exact conditional evidence
in the v0.2-v0.8 chain, but canonical completion remains `0/5` because two
domain choices are absent from the normative source:

- the registered sensor/computation class; and
- the probability/disturbance order for randomized codes.

This is certified by two independent same-plant model forks.  Three sensor
completions yield a computed rectangle, a nonrectangular adaptive wedge, and a
raw rectangle.  Three stochastic completions yield two feasibility outcomes:
the origin is achievable under per-disturbance almost-sure safety, while the
uniform and support-zero-error readings are infeasible on the diagonal plant.

The semantic underdetermination theorem therefore applies: explicit clauses
that admit models with distinct target values do not determine one target.

## Evidence integrity

The canonical source plus seven predecessor claim files are SHA-256 sealed.
The atlas parses all seven schemas and discriminator fields, extracts the five
requirements directly from the ASMP-4 section, checks the non-normative machine
index, and inventories 112 predecessor tests across nine packages.

The source's machine index declares `registry_is_normative=false` and
`graduation_standard_satisfied=false`.  Its ASMP-4 row has no sensor grammar or
randomness semantics.  The Markdown likewise contains neither selector.

## Disposition

The evidence justifies stopping further local enumeration.  Another grid can
refine one declared completion but cannot identify which missing completion is
canonical.  Productive reopening requires a normative registry, a normative
stochastic order, a genuinely new unreduced registered class, or an
attributable proof error.

This is a rigorous stopping certificate and negative well-posedness result,
not a claim that one conditional region resolves the intended ASMP-4 problem.
