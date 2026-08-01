# ASMP-4 serial-collapse result v0.2

## Result

The canonical deterministic no-side-channel architecture does not have two
independent achieved-information entropies.

For every safe code, the write transcript is a deterministic causal image of
the read transcript. More strongly, the sensor can simulate that controller
map and the controller can relay it, producing identical plant behavior with
bijective read and write transcript languages, or equal cardinalities after a
fixed plant-independent delay prefix.

If `nu_T` is the minimum number of realized causal control/write words needed
for `T`-step confinement, then the exact finite region is

```text
R_T = {(B_r,B_w): B_r>=log2(nu_T), B_w>=log2(nu_T)}.
```

For arbitrary nonempty `K_0` contained in `K`, let `h_perp(K_0,K)` be the
infimum control-language growth rate over infinite safe observation policies.
Then

```text
closure(R_K) =
    [h_perp(K_0,K),infinity) x [h_perp(K_0,K),infinity).
```

For a registered repeatable-block specification, the corresponding
regenerative entropy additionally obeys
`h_perp^reg(K)=inf_T log2(nu_T^reg(K))/T`. Thus, for the general capacity
region,

```text
h_read_perp(K_0,K) = h_write_perp(K_0,K) = h_perp(K_0,K).
```

Unequal or nonrectangular frontiers require an extra restriction or information
source, such as actuator-local state, private random channel state,
deadline-incompatible timing, unequal symbol costs, port-specific peak
alphabets, computational limits, or changing actuator authority.

## Exact finite correction

For

```text
x_(t+1)=a*x_t+u_t,
x_0 in [-delta,delta],
|x_t|<=L,
a>1,
```

with unrestricted controls,

```text
nu_T=ceil(a^T*delta/L).
```

This gives exact zero-rate coasting while `a^T delta<=L` and converges to the
classical `log2(a)` threshold. The diagonal-box formula is the product of the
coordinate covering counts and recovers the sum of positive log-eigenvalues.

## Verification

The independent finite harness passes all eleven gates:

- 162 finite plant/observation pairs;
- 648 exact read/write budget cells;
- zero discrepancies from the diagonal-quadrant theorem;
- exact binary mode growth `2^T`;
- partial-observation and unseen-disturbance kill cases;
- actuator-side-information collapse;
- a full-versus-restricted actuator-authority control;
- exact fixed-FIFO-delay relay replay through three ticks of delay; and
- stable, unstable-margin, nonhyperbolic, and diagonal-box formulas.

The proof and boundaries are in `THEOREM.md`; the requirement-by-requirement
assessment is in `RESOLUTION_AUDIT.md`.

The predecessor definition audit independently replayed all 77 feasible
v0.1 witnesses: none violated `|M_w(T)|<=|M_r(T)|`, and 34 had a strict
write-language collapse. Those are precisely the codes that relay normal form
can improve on the read side.

## Claim status

This is a self-contained candidate mathematical resolution, not an empirical
resolution and not a claim of external peer-review consensus. It resolves the
deterministic noiseless achieved-transcript object stated in ASMP-4 v0.1. A
noisy, private-channel-state, or deadline-incompatible successor would be a
different problem.
