# ASMP-3 correlated-noise frontier: prior-art boundary

## Search conclusion

The beta-binomial majority calculation in this seed is classical probability,
not a new theorem. Its use as a finite weak-verifier gate is an instrument
contribution. The candidate contribution is the combination of separately
worst-cased false-accept and false-reject errors, an exact correlation/diversity
frontier, and a constructive distinction between average semantic accuracy and
accuracy on the refuting atoms selected by a challenger.

## Closest work

1. **Doubly-efficient debate.** Brown-Cohen et al., *Scalable AI Safety via
   Doubly-Efficient Debate* ([arXiv:2311.14125](https://arxiv.org/abs/2311.14125)),
   prove efficient verification results for computations with access to
   stochastic human-judgment oracles. Their discussion explicitly leaves open
   oracle errors concentrated on arbitrary or randomly selected subsets of
   queries. This seed studies one tiny finite instance of that unresolved noise
   issue; it does not extend their complexity-theoretic theorem.
2. **Debate query complexity.** Brown-Cohen et al., *Debate is Efficient with
   Your Time* ([arXiv:2602.08630](https://arxiv.org/abs/2602.08630)), characterize
   the number of transcript bits a verifier must inspect in a deterministic
   debate model. Our `q` counts repeated noisy semantic judgments after a
   refuting atom has been located. It is not their DQC quantity.
3. **Correlated verifier cascades.** Han, *Partially Correlated Verifier
   Cascades in LLM Harnesses* ([arXiv:2607.13918](https://arxiv.org/abs/2607.13918)),
   uses beta latent error rates to derive reliability limits for serial
   all-accept gates. The present beta-binomial calculation is adjacent and
   weaker mathematically. It differs operationally by using symmetric majority
   adjudication, reporting false acceptance and false rejection separately,
   and varying the number of independent verifier families at fixed query
   count.
4. **Weak/strong deferral.** Kiyani et al., *When to Trust the Cheap Check:
   Weak and Strong Verification for Reasoning*
   ([arXiv:2602.17633](https://arxiv.org/abs/2602.17633)), separately control
   incorrect acceptance and incorrect rejection while deciding when to invoke
   strong verification. This supports the review correction that a single
   paired gap is insufficient. Their population and online-calibration setting
   is different from this exact finite noise game.

## Frozen novelty posture

No result below will be called a new amplification theorem, a debate theorem,
or a solution to ASMP-3. A successful run establishes only an exact finite
frontier for the registered symmetric flip model and a counterexample to using
an atom-averaged error bound as a uniform semantic guarantee.

