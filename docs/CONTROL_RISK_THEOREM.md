# Identity measurements as a signed-control risk bound

## Theorem

Let the registered overlap on edge `e` have polar decomposition

`M_e = Q_e S_e`,

where `Q_e` is orthogonal and `S_e` is a positive contraction. Let `W_e` be the squared minimum singular value recorded as worst-direction retention. For a path of `m` edges, define the realized coordinate map `M = M_m ... M_1` and its polar transport product `H = Q_m ... Q_1`.

Then

`||M - I||_2 <= sum_e (1 - sqrt(W_e)) + ||H - I||_2`.

The proof is a telescoping product bound: every factor has norm at most one, so replacing `M_e` by `Q_e` costs at most `||S_e-I||_2 = 1-sqrt(W_e)`. The triangle inequality then separates accumulated contraction from loop displacement.

For orientation-preserving `H`, canonical rotation blocks give

`||H-I||_2 = 2 sin(alpha_max/2)`,

where `alpha_max` is the largest canonical angle. If `det(H)<0`, an eigenvalue is `-1` and `||H-I||_2=2`. These bounds are sharp.

Consequently, if simultaneous one-sided measurement bounds cover every `W_e` and `alpha_max` with probability at least `1-delta`, authorizing only when the conservative sum is at most control budget `epsilon` gives

`P(authorize and ||M-I||_2 > epsilon) <= delta`.

This is a false-authorization guarantee, not a promise of high unconditional classification accuracy. Long paths can make the bound conservative; systems close to a noisy threshold must deny or abstain.

## Average-coordinate identities

For a uniformly random unit coordinate `v`, the ordinary lineage and holonomy statistics also have exact interpretations:

`E[1-||M_e v||^2] = 1 - mean_i(sigma_i^2)`

and

`E[1-v^T H v] = 1 - trace(H)/r`.

Worst-direction losses are attained by the minimum singular vector and the maximum-angle rotation plane. Thus the measurements are exact identity-distortion statistics under the registered linear model, rather than merely correlates.

## Impossibility boundary

No identity vector alone can prove general self-improvement risk. Two downstream systems can share the same bases, overlaps, hashes, and holonomy while assigning opposite behavioral meanings to the transported coordinate. The measurement therefore bounds loss of signed control identity. Any connection to behavioral control or self-improvement remains a grouped held-out empirical claim with downstream covariates.

## Receipt assumption

The theorem assumes receipts are bound to their geometry. The implementation now rejects out-of-range lineage, angle, determinant, and loss scalars; requires directed closed loop receipts; and recomputes sectioning plaquette loss and determinant from ordered boundary transports. Attestation loop scalars still require a hash-bound upstream holonomy artifact because `AnchorRecord` does not contain the matrix itself.

