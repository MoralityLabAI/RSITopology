# Exact conditional inference can have vanishing unconditional power

## Result

Version v0.13.2 showed that conditioning finite Bradley-Terry comparison
counts on vertex win balance removes a scalar-value nuisance exactly. Version
v0.14 closes the next access-ledger seam: it combines the conditional test
with the probability that the realized count fiber is informative.

On a consistently oriented `k`-cycle with `n` independent Bernoulli
comparisons per edge, two outcome vectors belong to the same balance fiber
exactly when they differ by an integer multiple of the all-ones vector.
Consequently, a realized outcome `Y` has an informative fiber exactly when:

```text
max(Y)-min(Y) < n.
```

If `P0_e=(1-p_e)^n` and `Pn_e=p_e^n`, its exact probability is:

```text
A(p)
  = product_e (1-P0_e)
  + product_e (1-Pn_e)
  - product_e (1-P0_e-Pn_e).
```

On every informative fiber, conditioning cancels the scalar nuisance and the
one-sided cycle-alternative likelihood ratio is proportional to `R^z`.
Therefore a randomized upper-tail rule has exact conditional size `alpha`.

## The no-go statement

Randomize at size `alpha` on singleton fibers. Unconditional excess power
then factors exactly as:

```text
Power_s(R)-alpha
  = sum over informative fibers t
      P_(s,R)(T=t) [Power_t(R)-alpha],
```

and hence:

```text
0 <= Power_s(R)-alpha
   <= (1-alpha) A(p_(s,R)).
```

The scalar-gradient nuisance family:

```text
s(q)=(q^(k-1),q^(-1),...,q^(-1))
```

has product one for every `q`. As `q` grows, one edge saturates at `n` wins
while the others saturate at zero, so `A(p)` and unconditional excess power
converge to zero even though the conditional law and exact conditional test
remain valid.

Thus exact nuisance cancellation does not imply a nontrivial
nuisance-uniform unconditional detection guarantee.

## Matched positive statement

If every alternative edge probability lies in the declared interior:

```text
epsilon <= p_e <= 1-epsilon,
```

then:

```text
A(p) >= [1-(1-epsilon)^n]^k.
```

For fixed finite `(k,n,R,alpha)` with `R>1`, the minimum conditional gain over
informative fibers is strictly positive. Multiplying these two terms gives a
strictly positive uniform lower bound on unconditional excess power.

The fresh positive-control arm fixed `epsilon=1/4` before execution. All 18
registered balanced-nuisance cells satisfied the interior and the exact
lower bound.

## Registered verification

The implementation was frozen at commit `e59072f`. Registration commit
`581226c` sealed 17 inputs before the 120 fresh cells were evaluated.

All ten gates passed:

- 120/120 cells had exact normalized null and alternative mass;
- the closed availability formula matched exhaustive enumeration;
- every fiber test had exact conditional size `1/20`;
- unconditional excess power matched the informative-fiber decomposition;
- all 90 positive-alternative cells obeyed the availability upper bound;
- all 18 fixed-interior positive controls obeyed the registered lower bound;
- all 30 `R=1` controls had power exactly `1/20` and zero gain; and
- all 18 `q=1024` endpoints had lower availability and excess power than
  their matched `q=1` controls.

The largest registered extreme-to-balanced excess-power ratio was:

```text
5.0910006966308135e-14.
```

For example:

| `k` | `n` | `R` | balanced availability | extreme availability | balanced excess | extreme excess |
|---:|---:|---:|---:|---:|---:|---:|
| 6 | 1 | `5/4` | `3.125e-2` | `1.591e-15` | `1.736e-4` | `8.839e-18` |
| 6 | 3 | `7/4` | `7.042e-1` | `2.153e-13` | `1.130e-2` | `5.710e-17` |
| 7 | 3 | `5/2` | `6.146e-1` | `6.260e-16` | `1.517e-2` | `7.806e-20` |

These decimals summarize exact rational records in
[`artifacts_v0_14`](artifacts_v0_14).

The CPU-only registered run completed in `91.75` seconds at `41,639,936`
peak resident bytes. The independent verifier reran all 120 exact cells and
matched the registry, summary, scientific gates, rendered report, hashes, and
claim boundary. A clean second run reproduced every scientific field. The 9
dedicated tests passed, and all 1,159 tests across the repository's 120 test
files passed in isolated fresh processes.

## Prior-art and novelty boundary

Conditioning away nuisance parameters, exact conditional inference,
Bradley-Terry toric models, and loss of information near extreme sufficient
statistics are classical. Novelty in those foundations is not claimed.

The contribution is an ASMP-9 access-ledger specialization that distinguishes:

1. exactness after an informative fiber has been realized;
2. the probability that such a fiber is realized;
3. an explicit scalar nuisance that destroys unconditional power; and
4. a declared design condition that restores a positive finite guarantee.

## ASMP-9 contribution and remaining gap

Version v0.14 proves that a positive finite-sample preference-access theorem
cannot rely on conditional exactness alone. It must expose a bounded
item-strength or probability interior, a balancing intervention, a nuisance
distribution, or an availability floor.

This does **not** resolve ASMP-9. The result assumes one oriented cycle,
equal fixed edge counts, independent Bernoulli responses, a known logistic
link, observed item identities, and one one-sided circulation alternative.
It does not validate Bradley-Terry behavior, certify scalarity from
non-rejection, handle unknown links, dependence, strategic response, latent
context, adaptive design, or sequential finite-MDP behavior.
