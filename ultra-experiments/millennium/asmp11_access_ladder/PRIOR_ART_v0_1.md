# ASMP-11 v0.1 prior-art boundary

The Boolean visibility threshold is classical Fourier analysis and reuses the
instrument family already audited under ASMP-1. It is not presented as a new
theorem.

The negative baseline is substantially stronger than the toy seed:

- Goldwasser, Kim, Vaikuntanathan, and Zamir construct backdoors undetectable
  to efficient white-box distinguishers even when model and training data are
  supplied (`arXiv:2204.06974`).
- Kalavasis et al. extend undetectable constructions to obfuscated networks
  and language-model settings (`arXiv:2406.05660`).
- Bogdanov, Rosen, and Vafa give a 2026 statistical white-box result in which
  honest and backdoored model distributions are close in total variation even
  with full model descriptions (`arXiv:2607.09532`).

Accordingly, this experiment claims only an exact access-class separator for a
transparent finite mechanism. Its successor must test a prospectively frozen,
independently motivated ladder against paired models; it may not imply that raw
white-box access defeats cryptographic constructions.
