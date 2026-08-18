# ASMP-5 bounded verifier-drift result

## Decision

**UNAVAILABLE — resource cap reached; stop the sequence.**

The exact registered census did not finish within its 180-second wall ceiling. The command wrapper returned timeout after 184.1 seconds, and the still-running matching Python process was terminated. No `result_v0_1.json` or registered receipt was emitted, and no partial scientific outcome was read.

Per protocol v0.1, the deterministic status is:

```text
unavailable_resource_cap_stop_sequence
```

This is neither a pass nor a scientific failure of the verifier-drift hypothesis. It says the frozen implementation/resource pairing was inadequate for the registered exact census. Sampling, threshold relaxation, code optimization, and an immediate retry are prohibited in this run.

## Binding

- Preregistered commit: `ba4ba496af2c98b3e95c133abf2c07c2e506cbe2`
- Protocol SHA-256: `2d284469dd886dde49b8e4682920c93bd3931f36c4fa8f099a03e9339664178f`
- Claim packet SHA-256: `894e97919b31a59a166d71fcd8dbe289d03aa761775e322e28e3a91336578753`
- Runner SHA-256: `5b2232c89fdff81cd11bff711379d122427aadac8d6329b9ca58073da01ddb9b`
- Termination receipt SHA-256: `3e3f74dec18027e1c0471f1144be641b45cd713e8b487551af562c81ca9f6324`

## Consequence

The ordered sequence stops here. ASMP-3 and ASMP-1 were not run. ASMP-6 and ASMP-7 remain deferred as registered. A successor ASMP-5 protocol would require a separately committed version with a justified optimization or larger explicit ceiling; it cannot inherit a claim from this unavailable run.

## Claim boundary

No verifier-drift result was obtained. The only result is that this exact implementation did not complete inside its frozen local resource cap.
