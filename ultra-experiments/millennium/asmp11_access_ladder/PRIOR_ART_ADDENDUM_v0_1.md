# ASMP-11 v0.1 prior-art and access-model addendum

## Why this addendum exists

`PRIOR_ART_v0_1.md` was committed with the prospective registration, but the
result commit did not link it. This additive document makes the literature
boundary visible from the circulation surface without modifying any registered
source.

## Direct mathematical ancestors

- The parity threshold is a standard consequence of Boolean Fourier
  orthogonality. Kearns's statistical-query model supplies the relevant noisy,
  finite-tolerance negative baseline: parity is the canonical separation
  between exact correlation access and efficient SQ learning.
- Blum, Kalai, and Wasserman, *Noise-Tolerant Learning, the Parity Problem, and
  the Statistical Query Model* (JACM 2003; `arXiv:cs/0010022`), show that noisy
  parity/LPN has structure beyond the SQ model while remaining computationally
  nontrivial. The current noiseless exact census makes no LPN or sampling
  hardness claim.
- Angluin, Aspnes, Chen, and Wu, *Learning a Circuit by Injecting Values*
  (JCSS 2009), formalize value-injection queries that set internal wires and
  observe circuit output. That is the closest direct ancestor of the present
  causal-fixing coordinate. Their algorithms and lower bounds depend on
  circuit topology; the current parity seed is not a new circuit-learning
  result.

## White-box negative baseline

- Goldwasser, Kim, Vaikuntanathan, and Zamir (`arXiv:2204.06974`) give planted
  backdoors undetectable to efficient white-box distinguishers supplied with
  the model and training data.
- Kalavasis et al. (`arXiv:2406.05660`) extend undetectable constructions to
  obfuscated networks and language-model settings.
- Bogdanov, Rosen, and Vafa (`arXiv:2607.09532`) give a statistical white-box
  construction whose honest and backdoored model distributions are close in
  total variation even with full model descriptions.

The finite access ladder is therefore an instrument calibration strictly below
these negative results. It cannot be cited as evidence that interpretability
or causal interventions defeat an obfuscated or cryptographic backdoor.

## Cost qualification

Every v0.1 query count is a **nonadaptive exhaustive upper bound**: all
registered restrictions and all registered Walsh coordinates are queried.
The census proves neither an adaptive lower bound nor optimality of that query
schedule. In particular, the result that causal fixings do not reduce cost is
restricted to this nonadaptive exhaustive accounting; an adaptive
value-injection strategy may change the ordering.
