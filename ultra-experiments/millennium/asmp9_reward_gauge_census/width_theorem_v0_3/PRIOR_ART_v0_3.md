# ASMP-9 sharp query-width theorem: prior-art boundary

## Classical setting

The qualitative ingredients are classical:

- distinct rays can be separated by a homogeneous hyperplane;
- signs of linear measurements identify directions through a hyperplane
  tessellation;
- rational separating hyperplanes can be rescaled to integer normals; and
- separation of integer point sets by hyperplanes is part of discrete convex
  geometry.

Relevant anchors include:

- Plan and Vershynin, *One-Bit Compressed Sensing by Linear Programming*,
  <https://arxiv.org/abs/1109.4299>;
- Plan and Vershynin, *Dimension Reduction by Random Hyperplane
  Tessellations*, <https://www.math.uci.edu/~rvershyn/papers/pv-tessellations.pdf>;
- Kashimura, Numata, and Takemura, *Separation of Integer Points by a
  Hyperplane under Some Weak Notions of Discrete Convexity*,
  <https://arxiv.org/abs/1002.2839>; and
- the reward-invariance sources listed in
  `../ordinal_frontier_v0_2/PRIOR_ART_v0_2.md`.

## Narrow residual claim

The candidate lemma here is not a new separating-hyperplane theorem. It is the
sharp coefficient-width specialization for this exact finite access grammar:

```text
primitive reward rays z in Z^d with ||z||_infinity <= B;
primitive integer sign queries q;
adversarial additive threshold radius 0 <= delta < 1;
positive reward scale quotiented, negative scale not quotiented.
```

For `d >= 2`, the proposed exact universal width is:

```text
Q*(B) = 2                  if B = 1
        2B - 1             if B >= 2.
```

The upper bound is a constructive two-coordinate integer separator. The lower
bound is an explicit adjacent-ray pair. This exact formula was not located in
the bounded search above. Absence from this search is not evidence of novelty;
the result should be described as a candidate-new elementary access lemma
until checked by a discrete-geometry specialist.

## Distinction from one-bit compressed sensing

One-bit compressed sensing usually asks for approximate recovery of sparse or
structured vectors from random measurements, often asymptotically and with
probabilistic guarantees. This theorem asks for worst-case exact separation of
every primitive lattice ray in a bounded box, using deterministic integer
normals whose coefficient width is the charged resource.

Neither result subsumes the other without additional reductions.

