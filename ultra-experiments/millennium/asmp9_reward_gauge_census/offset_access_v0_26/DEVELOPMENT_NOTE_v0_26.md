# ASMP-9 v0.26 development note

This successor changes axes deliberately.

Versions v0.17 through v0.25 characterize increasingly broad pieces of the
finite experimental-design problem inside one known comparison model. The
canonical ASMP-9 statement, however, also requires robustness to a declared
class of behavioral misspecification.

Version v0.8 proved that an unrestricted unknown monotone link enlarges the
finite-design value equivalence class beyond positive affine gauge. It left
the minimal link-calibrating intervention family open.

V0.26 develops one exact positive access channel:

```text
add a known scalar offset to one alternative;
locate the shared indifference midpoint;
recover the utility gap as a threshold location.
```

The result is intentionally conditional on this strong access. Its main
scientific purpose is to separate three claims that are otherwise easily
blurred:

1. ordinary comparisons do not identify a cardinal utility under an unknown
   link;
2. a known reward-unit intervention can make the cardinal coordinate
   identifiable; and
3. finite-sample recovery still needs a quantitative margin assumption.

Current status: theorem and implementation development only. No fresh
registered cells have been run.
