# v0.2: same-size dormant causal gate

**Scope:** a model-free, exactly enumerable GF(2) counterexample to identifying causal pathways from ordinary passive observations. IIT Phi, consciousness and asymptotic Fidelity Recursive Complexity (FRC) are outside the experiment.

## Exact construction

Both systems have 16 binary state coordinates, binary external cue u[t], and initial state x(0)=0. All operations are in GF(2).

Plain updates x'[0]=u, x'[i]=x[i-1] for 1 <= i <= 14, and x'[15]=0.

Dormant_gate changes precisely one equation: x'[7]=x[6] XOR x[15]. Each system reads a 12-step-delayed cue from x[12].

**Proposition 1 (ordinary-input observational equivalence).** For every finite binary cue stream starting in the all-zero state, the entire sequence of 16-coordinate observable states and fixed-readout predictions coincides between the systems.

*Proof.* By induction, x[15]=0 after every ordinary transition in both systems. Thus the additional XOR input vanishes along every reachable state, so the remaining update rules coincide at every step. All deterministic passive statistics of the resulting trajectories, including Fourier spectra, covariance and recall performance, coincide as well.

**Proposition 2 (causal separation).** Toggle coordinate 15 in both systems after the same step t0. Immediately after the intervention their full states are equal; after one further step, x[7] differs. The difference shifts into x[12] at t0+6, changing the delayed-readout prediction.

**Proposition 3 (distinct structural ranks in equal-sized systems).** For the fixed partition {0,...,7}|{8,...,15}, the exact one-step matrix cross-block GF(2) rank sum is 1 (plain) versus 2 (dormant). The ordinary-input controllability rank is 15 in both, because x[15] remains unreachable from the registered initial state.

The only transition matrix entry that differs is A[7,15], adding one cross-cut direction. A[8,7] supplies the crossing common to both systems. Tests extract every basis-vector transition, perform exact GF(2) elimination and exhaustively compare all 256 length-eight cue streams.

## Registered controls and results

Frozen protocol: protocol_v0_2.json. Development uses 24 trials at seed 20261027; replication uses 24 trials at seed 44178013. The run matrix verifies determinism and receipt integrity. The propositions themselves hold for every ordinary input stream.

v0.1's failed lag-8 XOR-spread prediction remains documented independently in its original receipts.

## Scientific and FRC boundary

Every trace-based statistic computed from normally reachable states is equal for the two systems even though the matrices differ. An observer inspecting the source transitions or intervening on x[15] can distinguish them. The result therefore depends on the explicitly restricted input and observation interface.

GF(2) cross-block rank is a structural proxy, not Tononi IIT Phi. Phi can depend on state and on the selected version's definitions. No subjective-experience label is present.

The ordinary-input-only oracle cannot distinguish the models with any number of queries; this is a support restriction, not proof of growing FRC. With permission for one targeted state intervention and a one-step follow-up, the models are distinguishable. No recursive rounds, weight changes or FRC lim-inf estimates are involved.

## Reproduce

python -m unittest discover -s tests -p 'test_harmonic_*.py' -v
python scripts/run_harmonic_dormant_gate.py --seed 20261027 --trials 24 --out HarmonicConsciousness/results/dormant_gate_dev_v0_2.json
python scripts/run_harmonic_dormant_gate.py --seed 44178013 --trials 24 --out HarmonicConsciousness/results/dormant_gate_replication_v0_2.json
