# ASMP-8 adaptive deterministic-audit protocol v0.6

## Frozen object

- six enumerable outcome atoms with uniform baseline probability;
- proxy values `i/5` for atom `i`;
- every directed policy that moves mass `1/6` from one atom to another;
- hidden pointwise errors in the complete ternary cube `{-1,0,1}^6`;
- every revealed-atom subset; and
- pointwise error cap one.

For policy displacement `d`, proxy gain `g`, revealed set `S`, and hidden
error vector `e`, define

```text
L(d,S,e_S) = g + sum_(i in S) d_i e_i
               - sum_(i not in S) |d_i|.
```

The exact true gain is `g+sum_i d_i e_i`.  Each unseen contribution is at
least `-|d_i|`, so `L<=true_gain` for every policy, transcript, and error
population.  The inequality remains true after any adaptive selector chooses
`d` and `S` from the revealed transcript because it is simultaneous and
pointwise, not an average over a fixed selection rule.

## Frozen adaptive control

At each step choose the policy with largest plug-in score

```text
g + sum_(i in S) d_i e_i,
```

breaking ties by policy ID.  Audit an unrevealed atom with largest movement
weight for that selected policy, breaking ties by atom index.  Repeat through
full census.  The plug-in score is a selection metric only.  Positive exact
gain and the robust lower bound are evidence metrics.  False plug-in
declarations are a hazard metric.

## Gates

- all policy distributions are valid;
- the robust lower bound is sound on every
  `729 x 64 x 30 = 1,399,680` pointwise cell;
- replacing one unseen worst case by its revealed contribution never lowers a
  fixed-policy certificate;
- full census equals exact true gain;
- the adaptive robust selector has zero false declarations; and
- the matched plug-in selector has at least one false declaration.

## Robustness probes

1. invariance under joint atom relabeling;
2. sensitivity to the registered error cap;
3. monotonicity under additional reveals for a fixed policy;
4. anti-gaming separation from the plug-in selector; and
5. full-census clean-control equality.

## Conclusion layers

- **Task result:** deterministic adaptive-selection soundness in the frozen
  finite class.
- **Measurement reliability:** complete exact census plus an import-independent
  replay.
- **Claim support:** reusable pointwise partial-census certificates for bounded
  deterministic atom errors.
- **Operational decision:** retain this certificate for adaptive finite audits,
  but require a new protocol for noisy labels or nonenumerable outputs.

## Claim boundary

This package does not validate stochastic optional stopping, noisy or drifting
human labels, reuse of a confidence sequence after data-dependent model
training, a learned reward model, an open-ended output space, or ASMP-8 as a
whole.  It proves soundness, not favorable audit efficiency for every adaptive
search.
