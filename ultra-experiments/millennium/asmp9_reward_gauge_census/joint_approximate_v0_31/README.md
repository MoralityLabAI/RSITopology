# ASMP-9 joint approximate quotient certificate v0.31

Development status: unregistered and unrun.

This CPU-only exact-rational instrument composes:

- bounded mechanical occupancy-row drift;
- exact context-only midpoint nuisance plus bounded residual drift;
- semantic calibration residuals with shared-cell incidence; and
- threshold-localization error.

The output is a quotient-reward error zonotope and policy-specific support
margin. The certificate must abstain when context residualization loses a
reward direction or the mechanical feedback gain is at least one.

The result, if registered and passed, will not derive any uncertainty width
from human/model data and will not resolve ASMP-9.
