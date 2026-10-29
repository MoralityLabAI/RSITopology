# ASMP-5 dynamic replicated noisy anchor protocol v0.4

## Registered object

The exact anchor is `R*=0011` (integer 3). Bit positions from least to most
significant are safe/class-0, safe/class-1, hazard/class-0, and
hazard/class-1. The primary perturbation leaves the two safe bits equal to one.
For each hazard bit it draws `m` replica-error indicators; all `2m` indicators
are mutually independent Bernoulli(`epsilon`) coins in bit-major,
replica-minor order. An odd-`m` strict majority installs that hazard bit as one.

Either error is individually exploitable: checker `0111` accepts a hazardous
proposal with proof class 0, and checker `1011` accepts it with proof class 1.
At every registered opportunity the anchor is installed and made visible
before the adversary chooses its proof class. Consequently the one-bit
majority error probability is

`p_m = sum_(k=(m+1)/2)^m C(m,k) epsilon^k (1-epsilon)^(m-k)`,

and the visible adversary's per-installation failure probability is
`q_m = 1-(1-p_m)^2`. A blinded control chooses one fixed bit-specific proof
class before visibility and therefore has probability exactly `p_m`.

`fresh_iid` draws an independent `2m`-coin batch at each of exactly `H`
post-install attack opportunities, giving risk `1-(1-q_m)^H`. `persistent`
draws one batch before the first opportunity and reuses that identical batch
forever, giving risk `q_m` for every positive horizon. All arithmetic is
`fractions.Fraction`; floats and RNG sampling are forbidden.

## Registry and theorem

The ordered grid is `m={1,3,5}`, `epsilon={0,1/20,1/10}`,
`H={1,8,64}`, then `temporal={fresh_iid,persistent}`: 54 rows. For every
finite odd `m` and probability `0<epsilon<=1`, the all-errors event proves
`p_m >= epsilon^m > 0`. Hence `q_m>0`; fresh-iid risk tends to one as the
horizon tends to infinity. Persistent risk remains the positive constant
`q_m` and is not claimed to tend to one.

## Controls

- false-negative-only noise leaves both hazard bits zero, so unsafe risk is
  zero, but independently losing both safe-majority bits has per-installation
  deadlock probability `p_m^2`;
- `epsilon=0` reconstructs the exact anchor and zero failure risk;
- the inherited v0.3 `behavior 0 -> 2 -> 0`, checker-3 cycle remains an exact
  nonhazardous liveness fixture, not a noisy-model liveness theorem;
- swapping the two hazard-bit/proof-class labels leaves every primary risk
  unchanged;
- for `H>1` and `0<q_m<1`, fresh risk is strictly greater than persistent
  risk, making the temporal distinction live;
- perfectly correlating the two hazard-bit majority errors gives visible risk
  `p_m`, rather than the primary product-law value `q_m`; and
- choosing exactly one bit-specific proof class before visibility also gives
  `p_m`, making the reveal-before-choice ordering live.

## Verification and gates

The primary uses the displayed exact binomial formulas. The import-independent
verifier instead enumerates every one of at most `2^(2*5)=1024` joint replica
patterns, assigns its exact product probability, and advances a two-state
`safe/failed` recurrence. It separately handles one persistent batch. It
rebuilds all 54 rows and controls, checks strict row order, validates the exact
eight-file committed source snapshot, and reads the frozen predecessor bytes
from commit `61a2f802adb4c4b5f06272d97d9de888413d5352`.

All bindings, rows, theorem obligations, controls, and independent comparisons
are conjunctive. Before independent verification the scientific conclusion is
pending. Scientific entrypoints require `python -I` and exclusively create
files only in the sibling artifact directory.

## Claim boundary

This is an exact result, if executed and independently verified, only for the
frozen product-error transition system and registered grid. The correlated and
false-negative cases are controls. It is not a theorem about arbitrary
learners, arbitrary correlations, learned evidence, infinite distinct-state
progress, open-ended verifier replacement, general ASMP-5 systems, or a
resolution of ASMP-5.
