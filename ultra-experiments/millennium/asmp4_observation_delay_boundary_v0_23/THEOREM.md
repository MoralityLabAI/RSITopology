# Observation-delay boundary theorem

Fix the registered collar dynamics

`n_(t+1) = 2 n_t + u_t - q_t`,

with `n_t in [-1,1]`, `u_t in [-2,10]`, and arbitrary
`q_t in {0,8}`. Safety is required for every initial collar point from the
first write. Plant-independent shared randomness is universally quantified.

## The sharp boundary

- At delay zero, the exact two-port region is
  `[2,infinity) x [2,infinity)`.
- With no current-mode preview, every integer `d >= 1` has empty region,
  regardless of message capacity, controller memory, or causal processing.
- A charged current-mode preview before the write restores
  `[2,infinity) x [2,infinity)`.
- If the mode is constant and a charged one-bit seed is available before
  safety begins, the exact region is `[1,infinity) x [1,infinity)`.

## Proof of positive-delay impossibility

At a common pre-write normal coordinate `n`, the safe controls are

- `I_0(n) = [-1-2n, 1-2n]` when `q_t=0`;
- `I_8(n) = [7-2n, 9-2n]` when `q_t=8`.

The lower endpoint of `I_8(n)` minus the upper endpoint of `I_0(n)` is
`(7-2n)-(1-2n)=6`; the gap is exactly 6 for every `n`. Thus the two safe-control
sets are disjoint.

For any positive delay, choose two disturbance histories identical before the
current step and split their current modes between 0 and 8. The delayed
information, controller state, normal state, and fixed randomness seed are the
same at the write. The controller must therefore choose the same action in
both branches, but no such action lies in both safe intervals. Failure occurs
already on the first write, so added capacity or memory cannot repair it.

## Restoration and finite counts

Knowing current `q_t` permits `u_t=q_t-2n_t`, which is in `[-2,10]` throughout
the collar and sends `n_(t+1)` to zero. The v0.22 causal coding theorem then
gives `2^T ceil(rho 2^T)` read and write words over horizon `T`, hence corner
`(2,2)`. Charged preview supplies precisely the missing current bit and has the
same count.

For constant `q`, the initial charged seed has two values and is reused. The
exact count becomes `2 ceil(rho 2^T)` on each port, whose asymptotic rate is
one. The normal expanding direction supplies the matching lower bound.
