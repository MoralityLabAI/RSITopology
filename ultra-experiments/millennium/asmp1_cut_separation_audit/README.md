# ASMP-1 cut-separation well-posedness audit

This directory contains an exact rational harness for the two directions of
the ASMP-1 v0.1 Cut-Separation Conjecture.

Run:

```powershell
$env:PYTHONPATH = "ultra-experiments\millennium\asmp1_cut_separation_audit"
python -m pytest ultra-experiments/millennium/asmp1_cut_separation_audit/test_cut_separation_audit.py -q
python ultra-experiments/millennium/asmp1_cut_separation_audit/cut_separation_audit.py `
  --output ultra-experiments/millennium/asmp1_cut_separation_audit/artifacts/result.json
```

The harness uses analytic Bernoulli response kernels on the three-parent
Boolean cube. The response probability is a multilinear polynomial in Walsh
coordinates, so its scientific checks reduce to exact rational linear
algebra.

It tests three independent pressure points in the proposed iff:

1. A nonconstant one-dimensional abstraction `Q(theta)=p_theta(-1,-1,-1)` is
   observed exactly from that one environment, although this environment has
   rank one on an eight-dimensional local mechanism class. Thus excitation
   sufficient to identify the whole registered mechanism class is not
   necessary for identifying a separately frozen coarse `Q`.
2. Even full replacement access to a typed hidden cut does not identify an
   upstream map through a dimension-reducing analytic downstream mechanism.
   The harness uses `X={0,1} -> H=R^2 -> Y=R`, observes every labelled input,
   and registers `do(H=(a,b))` for the entire cut. With `g(a,b)=a+2b`, each
   input retains a continuous blind direction `span{(-2,1)}`. This is a
   generic dimension obstruction for maps from two dimensions to one, not an
   isolated finite collision.
3. A full-support three-parent environment plus every singleton activation
   replacement has full site coverage, pair-separates all sites, and has a
   full-rank structural incidence matrix. Nevertheless, the passive and
   singleton-do laws have rank four on an eight-dimensional analytic response
   class. A continuous three-way interaction direction is invisible. Two
   interior mechanisms on that fiber are not related by parent permutations
   or sign flips.

These are well-posedness and conjecture audits, not a claim to have solved the
broader ASMP-1 classification program. See [RESULT_v0_1.md](RESULT_v0_1.md) for
the exact stopping argument and repair obligations.
