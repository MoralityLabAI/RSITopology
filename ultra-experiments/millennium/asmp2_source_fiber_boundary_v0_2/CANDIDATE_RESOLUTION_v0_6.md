# Candidate resolution of ASMP-2 by safety deficiency

## Proposed adjudication

The exact mathematical answer to ASMP-2's certification question is the
decision-specific safety deficiency

```text
D_G(E)
  = inf_K sup_m Pr_(X~Q_m)[K(X) notin G_m],
```

where `E={Q_m}` is the complete registered source experiment and `G_m` is the
set of policies satisfying the declared global safety and utility constraints
in model `m`.

When the decision-kernel infimum is attained, as in the finite programs in
this packet, this yields the exact variational classification:

```text
certificate at confidence 1-delta
iff
D_G(E) <= delta.
```

Without attainment, a certificate implies `D_G(E) <= delta` and
`D_G(E) < delta` implies a certificate, but equality can lie only in the
closure of achievable failure levels. The population-law form is the exact
finite source-fiber hypergraph value. The finite-sample failure infimum is
`D_G(E^n)`. Once the admissible design set, adaptive state, horizon, and costs
are frozen, the optimal next environment minimizes `D_G(E tensor E_e)` (or is
epsilon-optimal when the infimum is unattained), and the corresponding
multi-step problem has a Bellman recursion.

## Five-obligation map

1. **Local semiparametric characterization.** In the LAN limit, regular
   estimation of smooth active constraints requires their gradients to lie in
   the adjoint-score range. This is prior art. A safe certificate additionally
   requires robust policy feasibility and margin; the v0.5 QMD counterexample
   proves factorization alone is insufficient.
2. **Local-to-global theorem.** Globally, `D_G` is the exact minimax failure
   infimum and, with the boundary-attainment qualification above, the exact
   certificate criterion. At finite population-law access it reduces to the
   source-fiber theorem. For a continuous, bump-rich continuation class,
   sources determine every admissible law exactly when they are dense. For a
   frozen Lipschitz class with margin, the exact McShane/Whitney envelopes give
   the positive finite-cover theorem.
3. **Minimax sample complexity.** Exact complexity is

   ```text
   n*(delta)=inf {n:D_G(E^n)<=delta}.
   ```

   The binary harness computes this exactly. The smooth indistinguishable
   subclass has `n*(delta)=infinity` for every `delta<1/2`.
4. **Active environment design.** Deficiency gives the terminal minimax
   objective. A one-step minimizer and Bellman rule are exact after the design
   grammar is registered; they are not a structural design theorem before its
   state, costs, horizon, and admissible kernels are bound. On domains with
   arbitrarily large bump packings, the packing theorem rules out every finite
   randomized universal design without margin; the Lipschitz cell supplies a
   positive exact design.
5. **No-free-lunch converse.** The v0.2 smooth QMD pair has equal source laws
   and scores, positive Fisher information, utility one, and opposite singleton
   good sets. Its exact all-sample minimax success is `1/2`.

## Is this a full resolution?

There are two coherent readings.

### Reading A: operational classification is admissible

If a coordinate-invariant variational criterion over a fully registered
experiment and safety decision counts as a characterization, and the standard
attainment/design hypotheses are included, the five obligations reduce to
`D_G`, its local adjoint-score limit, its finite-sample product experiments,
and its active Bellman recursion. On this reading ASMP-2 is not a new
Millennium-scale open problem: its formal core is a decision-specific
Blackwell/Le Cam deficiency problem, with classical optimal-recovery theorems
supplying class-specific continuation bounds.

### Reading B: a structural closed form is required

If defining the exact minimax decision value is considered tautological, v0.1
does not state what additional structural form a valid answer must have. It
also leaves the model registration, margin, metric, smoothness constants,
sample allocation, action randomization, and active-design cost unbound.
Requiring a particular closed form or computational complexity after seeing
the result would change the acceptance criterion and therefore require a new
problem version.

## Recommendation

Do not advertise ASMP-2 v0.1 as an unresolved theorem. Either:

1. **retire it as subsumed/under-specified**, recording the safety-deficiency
   reduction and the literal local counterexample as the negative resolution;
   or
2. issue a v0.2 statement that rejects operational deficiency as an answer and
   freezes a specific structural class, positive margin, norms, sample regime,
   and design-cost model.

Repository-local mathematical and computational checks support this
recommendation. The set's separate requirement for two independent expert
teams is not satisfied here, so this file remains a candidate resolution
rather than a final community adjudication.
